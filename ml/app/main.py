from fastapi import FastAPI

app = FastAPI(
    title="salle-hospital ML",
    description="Servicio de inferencia — clasificación de radiografías",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ml", "model_loaded": False}
