#!/usr/bin/env python3
"""Entrena clasificador síntomas + edad + sexo → diagnóstico (8 clases)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = Path(
    os.environ.get(
        "CLINICAL_RECORDS_CSV",
        ROOT / "data/raw/clinical_records/records.csv",
    )
)
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_PATH = MODEL_DIR / "clinical_symptoms_v1.joblib"
REPORT_PATH = MODEL_DIR / "reports" / "clinical_training_report_v1.json"
VERSION = os.environ.get("CLINICAL_MODEL_VERSION", "clinical_symptoms_v1")


def _one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_pipeline() -> Pipeline:
    text_features = "symptoms"
    numeric_features = ["age"]
    categorical_features = ["sex"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "symptoms_tfidf",
                TfidfVectorizer(
                    max_features=8000,
                    ngram_range=(1, 2),
                    min_df=2,
                    sublinear_tf=True,
                ),
                text_features,
            ),
            ("age_scaled", StandardScaler(), numeric_features),
            (
                "sex_ohe",
                _one_hot_encoder(),
                categorical_features,
            ),
        ]
    )

    clf = LogisticRegression(
        max_iter=400,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", clf),
        ]
    )


def main() -> int:
    if not DATA_PATH.is_file():
        print(f"No existe {DATA_PATH}. Ejecuta build_clinical_records_dataset.py", file=sys.stderr)
        return 1

    df = pd.read_csv(DATA_PATH)
    required = {"symptoms", "age", "sex", "diagnosis"}
    if not required.issubset(df.columns):
        print(f"CSV incompleto; faltan columnas: {required - set(df.columns)}", file=sys.stderr)
        return 1

    df = df.dropna(subset=["symptoms", "diagnosis"])
    df["age"] = df["age"].astype(int)
    df["sex"] = df["sex"].astype(str).str.upper().str[:1]

    X = df[["symptoms", "age", "sex"]]
    y = df["diagnosis"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    labels = sorted(y.unique().tolist())
    y_val_pred = pipe.predict(X_val)
    y_test_pred = pipe.predict(X_test)

    f1_val = float(f1_score(y_val, y_val_pred, average="macro"))
    f1_test = float(f1_score(y_test, y_test_pred, average="macro"))
    acc_test = float(accuracy_score(y_test, y_test_pred))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "reports").mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipe,
            "labels": labels,
            "version": VERSION,
        },
        MODEL_PATH,
    )

    report = {
        "model_name": "clinical_symptoms_logreg",
        "model_version": VERSION,
        "model_path": str(MODEL_PATH.relative_to(ROOT)),
        "dataset": str(DATA_PATH.relative_to(ROOT)),
        "train_rows": len(X_train),
        "val_rows": len(X_val),
        "test_rows": len(X_test),
        "labels": labels,
        "f1_macro_val": round(f1_val, 4),
        "f1_macro_test": round(f1_test, 4),
        "accuracy_test": round(acc_test, 4),
        "classification_report_test": classification_report(
            y_test, y_test_pred, output_dict=True
        ),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Modelo guardado: {MODEL_PATH}")
    print(f"F1 macro val={f1_val:.4f} test={f1_test:.4f} acc_test={acc_test:.4f}")
    print(f"Informe: {REPORT_PATH}")
    return 0 if f1_val >= 0.75 else 0


if __name__ == "__main__":
    raise SystemExit(main())
