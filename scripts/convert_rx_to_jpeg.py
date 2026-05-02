#!/usr/bin/env python3
"""Convierte imágenes .jpg no-JPEG (p. ej. PNG) a JPEG válido in-place."""

from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = Path(
    sys.argv[1] if len(sys.argv) > 1 else ROOT / "data/raw/covid19_vs_pneumonia"
)
REPORT_PATH = RAW_ROOT.parent.parent / "processed/manifest/conversion_report.json"


def is_jpeg(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(3) == b"\xff\xd8\xff"


def convert_file(path: Path) -> str:
    """Devuelve: skipped_jpeg | converted | failed."""
    if is_jpeg(path):
        return "skipped_jpeg"

    try:
        with Image.open(path) as img:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            elif img.mode == "L":
                img = img.convert("RGB")
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=95, optimize=True)
            path.write_bytes(buf.getvalue())
        return "converted"
    except Exception as exc:
        print(f"FAIL {path}: {exc}")
        return "failed"


def main() -> None:
    if not RAW_ROOT.is_dir():
        raise SystemExit(f"No existe {RAW_ROOT}")

    stats = {"skipped_jpeg": 0, "converted": 0, "failed": 0}
    for jpg in sorted(RAW_ROOT.rglob("*.jpg")):
        result = convert_file(jpg)
        stats[result] = stats.get(result, 0) + 1

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(json.dumps(stats, indent=2))
    print(f"Informe: {REPORT_PATH}")

    if stats["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
