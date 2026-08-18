from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "iris_model.joblib"

REQUEST_COUNT = Counter("iris_api_requests_total", "Total API requests", ["endpoint"])
PREDICTION_LATENCY = Histogram(
    "iris_prediction_latency_seconds",
    "Prediction latency in seconds",
)


class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., gt=0, examples=[5.1])
    sepal_width: float = Field(..., gt=0, examples=[3.5])
    petal_length: float = Field(..., gt=0, examples=[1.4])
    petal_width: float = Field(..., gt=0, examples=[0.2])


class PredictionResponse(BaseModel):
    predicted_class: int
    species: str
    model_accuracy: float


def load_model_artifact() -> dict:
    if not MODEL_PATH.exists():
        raise RuntimeError(
            "Model artifact is missing. Run `python src/train.py` before starting the API."
        )
    return joblib.load(MODEL_PATH)


artifact = load_model_artifact()
app = FastAPI(
    title="Iris MLOps API",
    description="A small MLOps project with training, tracking, testing, API serving, and monitoring.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="/health").inc()
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: IrisFeatures) -> PredictionResponse:
    REQUEST_COUNT.labels(endpoint="/predict").inc()
    values = [[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width,
    ]]

    with PREDICTION_LATENCY.time():
        try:
            predicted_class = int(artifact["model"].predict(values)[0])
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Prediction failed") from exc

    return PredictionResponse(
        predicted_class=predicted_class,
        species=artifact["target_names"][predicted_class],
        model_accuracy=artifact["metrics"]["accuracy"],
    )


@app.get("/metrics")
def metrics() -> Response:
    REQUEST_COUNT.labels(endpoint="/metrics").inc()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
