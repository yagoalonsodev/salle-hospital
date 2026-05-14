#!/usr/bin/env python3
"""Ingesta masiva CSV clínico → PostgreSQL (PySpark + upsert por lotes)."""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/opt/scripts")
from db_log import finish_run, log_event, log_quality_issues, start_run  # noqa: E402
from salle_logging import setup_logging  # noqa: E402

log = setup_logging("ingest_csv_to_postgres")

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
STUDIES_CSV = Path(
    os.environ.get("STUDIES_CSV", str(DATA_ROOT / "raw/clinical/studies.csv"))
)
EVENTS_CSV = Path(
    os.environ.get("EVENTS_CSV", str(DATA_ROOT / "raw/clinical/pipeline_events.csv"))
)
DEFAULT_SITE = os.environ.get("DEFAULT_SITE_CODE", "LSHC-01")
BATCH_SIZE = int(os.environ.get("CSV_INGEST_BATCH", "500"))

VALID_LABELS = {"sana", "neumonia", "covid"}
VALID_SPLITS = {"train", "test", "val", "clinical"}
AGE_RANGES = ("18-30", "31-45", "46-60", "61-75", "76+")


def _spark() -> SparkSession:
    master = os.environ.get("SPARK_MASTER_URL", "local[*]")
    return (
        SparkSession.builder.appName("salle-ingest-csv-postgres")
        .master(master)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def _patient_row(patient_id: str) -> tuple:
    h = int(hashlib.md5(patient_id.encode()).hexdigest()[:8], 16)
    sex = ("M", "F", "X")[h % 3]
    age_range = AGE_RANGES[h % len(AGE_RANGES)]
    suffix = patient_id.replace("PAT-", "")[-6:]
    display_name = f"Paciente {suffix}"
    return (patient_id, display_name, sex, age_range, DEFAULT_SITE)


def _write_patients(conn, rows: list[tuple]) -> int:
    from psycopg2.extras import execute_batch

    sql = """
        INSERT INTO patients (patient_id, display_name, sex, age_range, site_code)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (patient_id) DO UPDATE SET
            display_name = EXCLUDED.display_name,
            sex = EXCLUDED.sex,
            age_range = EXCLUDED.age_range,
            site_code = EXCLUDED.site_code
    """
    with conn.cursor() as cur:
        execute_batch(cur, sql, rows, page_size=BATCH_SIZE)
    return len(rows)


def _write_studies(conn, rows: list[tuple]) -> int:
    from psycopg2.extras import execute_batch

    sql = """
        INSERT INTO studies (
            study_id, patient_id, file_path, minio_object_key, split, label,
            source_dataset, modality, body_part, captured_at
        )
        VALUES (%s, %s, %s, %s, %s::data_split, %s::study_label, %s, %s, %s, %s)
        ON CONFLICT (study_id) DO UPDATE SET
            patient_id = EXCLUDED.patient_id,
            file_path = EXCLUDED.file_path,
            split = EXCLUDED.split,
            label = EXCLUDED.label,
            source_dataset = EXCLUDED.source_dataset,
            captured_at = EXCLUDED.captured_at
    """
    with conn.cursor() as cur:
        execute_batch(cur, sql, rows, page_size=BATCH_SIZE)
    return len(rows)


def _ensure_pipeline_runs(conn, run_ids: set[str]) -> None:
    """Crea filas mínimas en pipeline_runs para eventos históricos del CSV."""
    if not run_ids:
        return
    from psycopg2.extras import execute_batch

    now = datetime.now(timezone.utc)
    stubs = [(rid, "historical_csv", "ingesta_csv", now, now) for rid in run_ids]
    sql = """
        INSERT INTO pipeline_runs (run_id, job_name, stage, status, started_at, finished_at)
        VALUES (%s, %s, %s, 'ok', %s, %s)
        ON CONFLICT (run_id) DO NOTHING
    """
    with conn.cursor() as cur:
        execute_batch(cur, sql, stubs, page_size=BATCH_SIZE)


def _write_events(conn, rows: list[tuple]) -> int:
    from psycopg2.extras import execute_batch

    sql = """
        INSERT INTO pipeline_events (event_id, run_id, stage, status, records, message, logged_at)
        VALUES (%s, %s, %s, %s::pipeline_status, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING
    """
    with conn.cursor() as cur:
        execute_batch(cur, sql, rows, page_size=BATCH_SIZE)
    return len(rows)


def _get_conn():
    import psycopg2

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL no configurada")
    return psycopg2.connect(url)


def main() -> None:
    run_id = os.environ.get(
        "PIPELINE_RUN_ID",
        f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}-CSV",
    )
    job_name = "ingest_csv_to_postgres"

    if not STUDIES_CSV.is_file():
        raise FileNotFoundError(f"No existe {STUDIES_CSV}; ejecuta build_clinical_data.py antes.")

    start_run(run_id, job_name, stage="ingesta_csv")

    spark = _spark()
    spark.sparkContext.setLogLevel("WARN")

    try:
        raw = spark.read.option("header", True).csv(str(STUDIES_CSV))
        total_in = raw.count()
        log_event(run_id, "EVT-CSV01", "ingesta_csv", "running", total_in, f"Filas CSV: {total_in}")

        required = [
            "study_id",
            "patient_id",
            "file_path",
            "split",
            "label",
            "source_dataset",
            "modality",
            "body_part",
            "captured_at",
        ]
        for col in required:
            if col not in raw.columns:
                raise ValueError(f"Columna obligatoria ausente en studies.csv: {col}")

        studies = (
            raw.dropDuplicates(["study_id"])
            .withColumn("label", F.lower(F.trim(F.col("label"))))
            .withColumn("split", F.lower(F.trim(F.col("split"))))
            .withColumn(
                "captured_at",
                F.to_timestamp(F.col("captured_at")).cast(TimestampType()),
            )
        )

        invalid = studies.filter(
            F.col("study_id").isNull()
            | F.col("patient_id").isNull()
            | F.col("file_path").isNull()
            | ~F.col("label").isin(list(VALID_LABELS))
            | ~F.col("split").isin(list(VALID_SPLITS))
            | F.col("captured_at").isNull()
        )
        n_invalid = invalid.count()
        valid = studies.join(invalid.select("study_id"), "study_id", "left_anti")

        quality_rows = [
            {
                "issue_type": "incomplete",
                "details": r["study_id"] or r["file_path"] or "unknown",
            }
            for r in invalid.select("study_id", "file_path").limit(200).collect()
        ]
        log_quality_issues(run_id, quality_rows)

        patient_ids = valid.select("patient_id").distinct()
        patients_out = [
            _patient_row(r["patient_id"])
            for r in patient_ids.collect()
        ]

        studies_out = [
            (
                r["study_id"],
                r["patient_id"],
                r["file_path"],
                None,
                r["split"],
                r["label"],
                r["source_dataset"],
                r["modality"],
                r["body_part"],
                r["captured_at"],
            )
            for r in valid.collect()
        ]

        conn = _get_conn()
        try:
            n_patients = _write_patients(conn, patients_out)
            n_studies = _write_studies(conn, studies_out)
            n_events = 0
            if EVENTS_CSV.is_file():
                ev_df = spark.read.option("header", True).csv(str(EVENTS_CSV))
                events_out = []
                for r in ev_df.collect():
                    logged = r["logged_at"]
                    if logged:
                        try:
                            ts = datetime.fromisoformat(str(logged).replace("Z", "+00:00"))
                        except ValueError:
                            ts = datetime.now(timezone.utc)
                    else:
                        ts = datetime.now(timezone.utc)
                    events_out.append(
                        (
                            r["event_id"],
                            r["run_id"],
                            r["stage"],
                            r["status"],
                            int(r["records"] or 0),
                            (r["message"] or "")[:2000],
                            ts,
                        )
                    )
                run_ids = {r[1] for r in events_out if r[1]}
                _ensure_pipeline_runs(conn, run_ids)
                n_events = _write_events(conn, events_out)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        log_event(
            run_id,
            "EVT-CSV02",
            "ingesta_csv",
            "ok",
            n_studies,
            f"patients={n_patients} studies={n_studies} events={n_events}",
        )
        finish_run(
            run_id,
            status="ok",
            records_in=total_in,
            records_out=n_studies,
            records_failed=n_invalid,
        )
        log.info(
            "Ingesta CSV OK: in=%d out=%d failed=%d patients=%d",
            total_in,
            n_studies,
            n_invalid,
            n_patients,
        )
    except Exception as exc:
        log.exception("Ingesta CSV fallida: %s", exc)
        finish_run(
            run_id,
            status="failed",
            records_in=0,
            records_out=0,
            records_failed=0,
            error_message=str(exc)[:2000],
        )
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
