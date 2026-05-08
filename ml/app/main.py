"""Servicio de inferencia TensorFlow — FastAPI."""

from __future__ import annotations

import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.inference import load_model, model_status, predict_pil
from app.logging_config import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    load_model()
  except FileNotFoundError:
    pass
  yield


app = FastAPI(
  title="salle-hospital ML",
  description="Inferencia ResNet50 — clasificación RX",
  version="1.0.0",
  lifespan=lifespan,
)


@app.get("/health")
def health():
  status = model_status()
  code = 200 if status["model_loaded"] else 503
  return {
    "status": "ok" if status["model_loaded"] else "degraded",
    "service": "ml",
    **status,
  }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
  if not file.content_type or not file.content_type.startswith("image/"):
    raise HTTPException(400, "Se requiere un archivo de imagen")
  raw = await file.read()
  if len(raw) > 10 * 1024 * 1024:
    raise HTTPException(413, "Imagen demasiado grande (máx. 10 MB)")
  try:
    image = Image.open(io.BytesIO(raw))
    image.verify()
    image = Image.open(io.BytesIO(raw))
  except (UnidentifiedImageError, OSError) as exc:
    raise HTTPException(400, f"Imagen no válida: {exc}") from exc

  try:
    result = predict_pil(image)
  except FileNotFoundError as exc:
    raise HTTPException(503, str(exc)) from exc

  return result
