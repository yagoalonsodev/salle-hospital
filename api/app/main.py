from fastapi import FastAPI

app = FastAPI(
    title="salle-hospital API",
    description="API de soporte hospitalario — laSalle Health Center",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "api"}
