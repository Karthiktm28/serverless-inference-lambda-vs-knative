from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.pipeline import run_pipeline

app = FastAPI(title="Serverless inference pipeline")


class PredictRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        return run_pipeline(req.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))