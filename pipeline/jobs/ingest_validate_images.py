#!/usr/bin/env python3
"""
Ingesta automática de radiografías: validación, deduplicación (MD5) y carga a MinIO.

Escanea el manifest o el árbol raw; valida por particiones (sin cargar todo en RAM).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    LongType,
    StringType,
    StructField,
    StructType,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/opt/scripts")
from db_log import finish_run, log_event, log_quality_issues, start_run  # noqa: E402

try:
    from env_utils import minio_config  # noqa: E402
except ImportError:
    minio_config = None  # type: ignore[misc, assignment]

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
MANIFEST_CSV = os.environ.get(
    "MANIFEST_CSV",
    str(DATA_ROOT / "raw/covid19_vs_pneumonia/manifest.csv"),
)
RAW_ROOT = Path(os.environ.get("RAW_ROOT", str(DATA_ROOT / "raw/covid19_vs_pneumonia")))
PROCESSED_DIR = Path(
    os.environ.get("PROCESSED_MANIFEST_DIR", str(DATA_ROOT / "processed/manifest"))
)
MIN_SIZE_BYTES = int(os.environ.get("MIN_IMAGE_BYTES", "500"))
UPLOAD_MINIO = os.environ.get("UPLOAD_MINIO", "true").lower() in ("1", "true", "yes")
MAX_UPLOAD = int(os.environ.get("MAX_UPLOAD", "0"))  # 0 = sin límite

ROW_SCHEMA = StructType(
    [
        StructField("file_path", StringType(), False),
        StructField("fs_path", StringType(), False),
        StructField("filename", StringType(), False),
        StructField("split", StringType(), True),
        StructField("folder", StringType(), True),
        StructField("label", StringType(), True),
        StructField("content_hash", StringType(), True),
        StructField("file_size", LongType(), True),
        StructField("is_valid_jpg", BooleanType(), False),
        StructField("path_ok", BooleanType(), False),
    ]
)


def _spark() -> SparkSession:
    master = os.environ.get("SPARK_MASTER_URL", "local[*]")
    return (
        SparkSession.builder.appName("salle-ingest-validate-images")
        .master(master)
        .config("spark.sql.shuffle.partitions", "16")
        .getOrCreate()
    )


def _load_manifest(spark: SparkSession):
    manifest_path = Path(MANIFEST_CSV)
    data_root = str(DATA_ROOT)
    if manifest_path.is_file():
        return (
            spark.read.option("header", True)
            .csv(str(manifest_path))
            .withColumn(
                "fs_path",
                F.concat(
                    F.lit(data_root + "/"),
                    F.regexp_replace(F.col("file_path"), r"^data/", ""),
                ),
            )
        )

    # Escaneo automático si no hay manifest
    paths = []
    for split in ("train", "test"):
        for folder in ("NORMAL", "PNEUMONIA", "COVID19"):
            d = RAW_ROOT / split / folder
            if not d.is_dir():
                continue
            for jpg in d.glob("*.jpg"):
                rel = f"data/raw/covid19_vs_pneumonia/{split}/{folder}/{jpg.name}"
                paths.append((rel, str(jpg), jpg.name, split, folder, ""))

    return spark.createDataFrame(
        paths,
        ["file_path", "fs_path", "filename", "split", "folder", "label"],
    )


def main() -> None:
    run_id = os.environ.get(
        "PIPELINE_RUN_ID",
        f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}-IMG",
    )
    job_name = "ingest_validate_images"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    start_run(run_id, job_name)

    spark = _spark()
    spark.sparkContext.setLogLevel("WARN")

    manifest = _load_manifest(spark)
    total_in = manifest.count()
    log_event(run_id, "EVT-SCAN01", "scan", "running", total_in, f"Filas manifest: {total_in}")

    inspect = spark.sparkContext.broadcast(
        {
            "data_root": str(DATA_ROOT),
            "min_size": MIN_SIZE_BYTES,
        }
    )

    def _partition(rows):
        root = Path(inspect.value["data_root"])
        min_sz = inspect.value["min_size"]
        label_map = {"NORMAL": "sana", "PNEUMONIA": "neumonia", "COVID19": "covid"}
        for row in rows:
            r = row.asDict() if hasattr(row, "asDict") else dict(row)
            fs = r.get("fs_path") or ""
            local = Path(fs) if fs else root / str(r.get("file_path", "")).replace("data/", "", 1)
            split = r.get("split") or ""
            folder = r.get("folder") or ""
            lbl = r.get("label") or label_map.get(folder, "")
            if not local.is_file():
                yield (
                    str(r.get("file_path", local)),
                    str(local),
                    local.name,
                    split,
                    folder,
                    lbl,
                    None,
                    0,
                    False,
                    False,
                )
                continue
            content = local.read_bytes()
            size = len(content)
            ok = size >= min_sz and content[:3] == b"\xff\xd8\xff"
            ch = hashlib.md5(content).hexdigest() if ok else None
            rel = f"data/raw/covid19_vs_pneumonia/{split}/{folder}/{local.name}"
            yield (
                rel,
                str(local),
                local.name,
                split,
                folder,
                lbl,
                ch,
                size,
                ok,
                split in ("train", "test") and lbl in ("sana", "neumonia", "covid"),
            )

    rdd = manifest.rdd.mapPartitions(_partition)
    df = spark.createDataFrame(rdd, ROW_SCHEMA)

    invalid = df.filter(~F.col("is_valid_jpg") | ~F.col("path_ok"))
    valid = df.filter(F.col("is_valid_jpg") & F.col("path_ok"))

    w_dup = Window.partitionBy("content_hash").orderBy(F.col("file_path"))
    ranked = valid.withColumn("dup_rank", F.row_number().over(w_dup))

    duplicates = ranked.filter(F.col("dup_rank") > 1)
    unique_valid = ranked.filter(F.col("dup_rank") == 1).withColumn(
        "minio_object_key",
        F.concat(F.lit("raw/"), F.col("content_hash"), F.lit(".jpg")),
    )

    out_cols = [
        "file_path",
        "fs_path",
        "filename",
        "split",
        "folder",
        "label",
        "content_hash",
        "file_size",
        "minio_object_key",
    ]

    unique_valid.select(out_cols).write.mode("overwrite").parquet(
        str(PROCESSED_DIR / "validated.parquet")
    )
    unique_valid.select(out_cols).coalesce(1).write.mode("overwrite").option(
        "header", True
    ).csv(str(PROCESSED_DIR / "validated_csv"))

    inv_rej = invalid.withColumn(
        "reject_reason",
        F.when(~F.col("is_valid_jpg"), F.lit("corrupt")).otherwise(F.lit("incomplete")),
    )
    dup_rej = duplicates.withColumn("reject_reason", F.lit("duplicate"))
    inv_rej.select(
        "file_path", "content_hash", "reject_reason", "file_size", "label", "split"
    ).unionByName(
        dup_rej.select(
            "file_path", "content_hash", "reject_reason", "file_size", "label", "split"
        )
    ).write.mode("overwrite").parquet(str(PROCESSED_DIR / "rejected.parquet"))

    records_out = unique_valid.count()
    n_invalid = invalid.count()
    n_dup = duplicates.count()

    report = {
        "run_id": run_id,
        "total_scanned": total_in,
        "valid_unique": records_out,
        "rejected": n_invalid + n_dup,
        "invalid_corrupt": n_invalid,
        "duplicates_removed": n_dup,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    (PROCESSED_DIR / "ingest_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if UPLOAD_MINIO and records_out > 0:
        _upload_to_minio(unique_valid)

    sample_invalid = [
        {
            "issue_type": "corrupt" if not r["is_valid_jpg"] else "incomplete",
            "details": r["file_path"],
        }
        for r in invalid.select("file_path", "is_valid_jpg").limit(200).collect()
    ]
    sample_dup = [
        {"issue_type": "duplicate", "details": r["file_path"]}
        for r in duplicates.select("file_path").limit(200).collect()
    ]
    log_quality_issues(run_id, sample_invalid + sample_dup)

    finish_run(
        run_id,
        status="ok",
        records_in=total_in,
        records_out=records_out,
        records_failed=n_invalid + n_dup,
    )
    log_event(run_id, "EVT-ING01", "ingesta_imagenes", "ok", records_out, json.dumps(report)[:500])

    print(json.dumps(report, indent=2))
    spark.stop()


def _upload_to_minio(unique_valid) -> None:
    try:
        from minio import Minio
    except ImportError:
        print("minio no instalado; omitiendo subida")
        return

    if minio_config is None:
        raise RuntimeError("env_utils no disponible; monta /opt/scripts en el contenedor")
    endpoint, access, secret, bucket = minio_config()
    secure = os.environ.get("MINIO_SECURE", "false").lower() == "true"

    client = Minio(endpoint, access_key=access, secret_key=secret, secure=secure)
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    rows = unique_valid.select("fs_path", "minio_object_key").collect()
    if MAX_UPLOAD > 0:
        rows = rows[:MAX_UPLOAD]
    uploaded = 0
    for row in rows:
        local = Path(row["fs_path"])
        if not local.is_file():
            continue
        client.fput_object(
            bucket,
            row["minio_object_key"],
            str(local),
            content_type="image/jpeg",
        )
        uploaded += 1
        if uploaded % 500 == 0:
            print(f"MinIO: {uploaded}/{len(rows)}...")

    print(f"MinIO: {uploaded} objetos en bucket '{bucket}'")


if __name__ == "__main__":
    main()
