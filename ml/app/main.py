"""Servicio de inferencia TensorFlow — FastAPI."""

from __future__ import annotations

import io
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from PIL import Image, UnidentifiedImageError

from app.clinical_inference import (
    clinical_model_status,
    load_clinical_model,
    predict_clinical,
)
from app.inference import load_model, model_status, predict_pil
from app.logging_config import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    load_model()
  except FileNotFoundError:
    pass
  load_clinical_model()
  yield


app = FastAPI(
  title="salle-hospital ML",
  description="Inferencia ResNet50 — clasificación RX",
  version="1.0.0",
  lifespan=lifespan,
)


@app.get("/health")
def health(response: Response):
  rx = model_status()
  clinical = clinical_model_status()
  rx_ok = rx["model_loaded"]
  clinical_ok = clinical["clinical_model_loaded"]
  if rx_ok and clinical_ok:
    overall = "ok"
    response.status_code = 200
  elif rx_ok or clinical_ok:
    overall = "degraded"
    response.status_code = 200
  else:
    overall = "degraded"
    response.status_code = 503
  return {
    "status": overall,
    "service": "ml",
    **rx,
    **clinical,
  }


class ClinicalPredictBody(BaseModel):
  symptoms: str = Field(..., min_length=3, max_length=4000)
  age: int = Field(..., ge=0, le=120)
  sex: str = Field(default="X", max_length=1)


@app.post("/predict-clinical")
def predict_clinical_endpoint(body: ClinicalPredictBody):
  try:
    return predict_clinical(
      symptoms=body.symptoms,
      age=body.age,
      sex=body.sex,
    )
  except ValueError as exc:
    raise HTTPException(400, str(exc)) from exc
  except FileNotFoundError as exc:
    raise HTTPException(503, str(exc)) from exc


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
