#!/usr/bin/env python3
"""Smoke test mínimo de conectividad Spark (usado por verify_stack.sh)."""

from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder.appName("salle-verify-smoke").getOrCreate()
    print("SPARK_OK", spark.version)
    spark.stop()
