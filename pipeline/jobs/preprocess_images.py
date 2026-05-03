#!/usr/bin/env python3
"""
Preprocesado RX para ML: resize, normalización, augmentation (train) y splits train/val/test.

Orquestado con PySpark (mapPartitions); transformaciones PIL en workers.
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from image_transforms import (  # noqa: E402
    LABEL_FROM_FOLDER,
    eval_augment_types,
    process_and_save,
    train_augment_types,
)

DATA_ROOT = Path(os.environ.get("DATA_ROOT", "/opt/data"))
MANIFEST_DIR = Path(
    os.environ.get("PROCESSED_MANIFEST_DIR", str(DATA_ROOT / "processed/manifest"))
)
FEATURES_VERSION = os.environ.get("FEATURES_VERSION", "v1")
FEATURES_ROOT = Path(
    os.environ.get("FEATURES_ROOT", str(DATA_ROOT / "processed/features"))
) / FEATURES_VERSION

IMAGE_SIZE = int(os.environ.get("IMAGE_SIZE", "224"))
VAL_RATIO = float(os.environ.get("VAL_RATIO", "0.15"))
RANDOM_SEED = int(os.environ.get("RANDOM_SEED", "42"))
PARTITIONS = int(os.environ.get("PREPROCESS_PARTITIONS", "8"))
PREPROCESS_LIMIT = int(os.environ.get("PREPROCESS_LIMIT", "0"))  # 0 = todas

INDEX_SCHEMA = StructType(
    [
        StructField("sample_id", StringType(), False),
        StructField("source_path", StringType(), False),
        StructField("output_path", StringType(), False),
        StructField("split", StringType(), False),
        StructField("label", StringType(), False),
        StructField("augment_type", StringType(), False),
        StructField("image_size", IntegerType(), False),
    ]
)


def _spark() -> SparkSession:
    master = os.environ.get("SPARK_MASTER_URL", "local[*]")
    return (
        SparkSession.builder.appName("salle-preprocess-images")
        .master(master)
        .config("spark.sql.shuffle.partitions", str(PARTITIONS))
        .getOrCreate()
    )


def _load_validated(spark: SparkSession):
    validated = MANIFEST_DIR / "validated.parquet"
    validated_csv = MANIFEST_DIR / "validated_csv"
    manifest = DATA_ROOT / "raw/covid19_vs_pneumonia/manifest.csv"

    if validated.is_dir():
        df = spark.read.parquet(str(validated))
    elif validated_csv.is_dir():
        df = spark.read.option("header", True).csv(str(validated_csv))
    elif manifest.is_file():
        data_root = str(DATA_ROOT)
        df = (
            spark.read.option("header", True)
            .csv(str(manifest))
            .withColumn(
                "fs_path",
                F.concat(
                    F.lit(data_root + "/"),
                    F.regexp_replace(F.col("file_path"), r"^data/", ""),
                ),
            )
        )
    else:
        raise FileNotFoundError("No hay validated.parquet ni manifest.csv")

    if "label" not in df.columns and "folder" in df.columns:
        pairs = []
        for k, v in LABEL_FROM_FOLDER.items():
            pairs.extend([F.lit(k), F.lit(v)])
        mapping = F.create_map(*pairs)
        df = df.withColumn("label", mapping[F.col("folder")])

    if "fs_path" not in df.columns:
        data_root = str(DATA_ROOT)
        df = df.withColumn(
            "fs_path",
            F.concat(
                F.lit(data_root + "/"),
                F.regexp_replace(F.col("file_path"), r"^data/", ""),
            ),
        )

    return df.select("fs_path", "file_path", "label", "split", "content_hash").distinct()


def _assign_splits(rows: list[dict]) -> list[dict]:
    """test original → test; train original → train + validation (estratificado por label)."""
    rng = random.Random(RANDOM_SEED)
    by_label: dict[str, list[dict]] = defaultdict(list)
    test_rows: list[dict] = []

    for row in rows:
        if row.get("split") == "test":
            row = {**row, "ml_split": "test"}
            test_rows.append(row)
        else:
            by_label[row["label"]].append(row)

    out = list(test_rows)
    for label, items in by_label.items():
        rng.shuffle(items)
        n_val = max(1, int(len(items) * VAL_RATIO))
        for i, row in enumerate(items):
            row = {**row, "ml_split": "validation" if i < n_val else "train"}
            out.append(row)
    return out


def _process_partition(rows_iter):
    import hashlib
    import sys
    from pathlib import Path as _Path

    # Workers Spark no heredan sys.path del driver
    jobs_dir = _Path(__file__).resolve().parent
    if str(jobs_dir) not in sys.path:
        sys.path.insert(0, str(jobs_dir))
    from image_transforms import (  # noqa: WPS433
        eval_augment_types,
        process_and_save,
        train_augment_types,
    )

    records = list(rows_iter)
    if not records:
        return iter([])

    rng = random.Random(RANDOM_SEED)
    results = []

    for row in records:
        rec = row.asDict() if hasattr(row, "asDict") else dict(row)
        fs_path = rec["fs_path"]
        if not Path(fs_path).is_file():
            continue

        ml_split = rec["ml_split"]
        label = rec["label"]
        content_hash = rec.get("content_hash") or hashlib.md5(
            Path(fs_path).read_bytes()
        ).hexdigest()

        aug_types = (
            train_augment_types()
            if ml_split == "train"
            else eval_augment_types()
        )

        for aug in aug_types:
            sample_id = hashlib.sha256(
                f"{content_hash}:{ml_split}:{aug}".encode()
            ).hexdigest()[:16]
            out_rel = f"{ml_split}/{label}/{sample_id}_{aug}.jpg"
            out_abs = str(FEATURES_ROOT / out_rel)

            process_and_save(
                fs_path,
                out_abs,
                IMAGE_SIZE,
                aug,
                rng,
            )

            results.append(
                {
                    "sample_id": sample_id,
                    "source_path": rec.get("file_path", fs_path),
                    "output_path": f"data/processed/features/{FEATURES_VERSION}/{out_rel}",
                    "split": ml_split,
                    "label": label,
                    "augment_type": aug,
                    "image_size": IMAGE_SIZE,
                }
            )

    return iter(results)


def main() -> None:
    FEATURES_ROOT.mkdir(parents=True, exist_ok=True)
    spark = _spark()
    spark.sparkContext.setLogLevel("WARN")
    jobs_dir = Path(__file__).resolve().parent
    spark.sparkContext.addPyFile(str(jobs_dir / "image_transforms.py"))

    base = _load_validated(spark)
    collected = [r.asDict() for r in base.collect()]
    assigned = _assign_splits(collected)
    if PREPROCESS_LIMIT > 0:
        assigned = assigned[:PREPROCESS_LIMIT]
        print(f"PREPROCESS_LIMIT={PREPROCESS_LIMIT} (modo prueba)")

    print(f"Filas a procesar (imágenes fuente): {len(assigned)}")
    for split in ("train", "validation", "test"):
        n = sum(1 for r in assigned if r["ml_split"] == split)
        print(f"  {split}: {n}")

    work = spark.createDataFrame(assigned).repartition(PARTITIONS, "label")

    index_rdd = work.rdd.mapPartitions(_process_partition)
    index_df = spark.createDataFrame(index_rdd, schema=INDEX_SCHEMA)

    index_df.write.mode("overwrite").parquet(str(FEATURES_ROOT / "dataset_index.parquet"))
    index_df.coalesce(1).write.mode("overwrite").option("header", True).csv(
        str(FEATURES_ROOT / "dataset_index_csv")
    )

    stats = (
        index_df.groupBy("split", "label", "augment_type")
        .count()
        .orderBy("split", "label", "augment_type")
        .collect()
    )
    counts = [r.asDict() for r in stats]
    total_samples = index_df.count()

    report = {
        "features_version": FEATURES_VERSION,
        "image_size": IMAGE_SIZE,
        "val_ratio": VAL_RATIO,
        "random_seed": RANDOM_SEED,
        "source_images": len(assigned),
        "output_samples": total_samples,
        "counts": counts,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "justification_doc": "docs/preprocess-distributed-justification.md",
    }
    report_path = FEATURES_ROOT / "preprocess_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    spark.stop()


if __name__ == "__main__":
    main()
