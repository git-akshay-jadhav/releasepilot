# Iris MLOps FastAPI Project

This is a beginner-friendly MLOps project. It trains a machine learning model, tracks the experiment with MLflow, saves the model artifact, serves predictions through FastAPI, exposes Prometheus metrics, and runs tests in CI.

## What You Learn

| MLOps area | Project evidence |
| --- | --- |
| Model training | `src/train.py` trains a Random Forest classifier |
| Experiment tracking | MLflow logs parameters, metrics, and the model |
| Model artifact | `models/iris_model.joblib` stores the trained model |
| Model serving | `src/app.py` exposes `/predict` with FastAPI |
| Monitoring | `/metrics` exposes Prometheus metrics |
| Testing | `tests/test_api.py` validates health, prediction, and bad input |
| Containerization | `Dockerfile` and `docker-compose.yml` run the API in Docker |
| CI/CD foundation | GitHub Actions runs lint, train, and tests |

## Run Locally

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

Train the model:

```bash
python src/train.py
```

Start the API:

```bash
uvicorn src.app:app --reload
```

Open:

- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>
- Metrics: <http://localhost:8000/metrics>

Example prediction:

```bash
curl -X POST http://localhost:8000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"sepal_length\":5.1,\"sepal_width\":3.5,\"petal_length\":1.4,\"petal_width\":0.2}"
```

## View MLflow Runs

After training, run:

```bash
mlflow ui --backend-store-uri mlruns
```

Then open <http://localhost:5000>.

## Run Tests

```bash
pytest
ruff check src tests
```

## Run With Docker

Train the model first so the artifact exists:

```bash
python src/train.py
docker compose up --build
```

Then test:

```bash
curl http://localhost:8000/health
```

## Suggested Demo Script

1. Explain the ML problem: predict Iris flower species from four measurements.
2. Run `python src/train.py` and show MLflow metrics.
3. Start the FastAPI app and show `/docs`.
4. Send a `/predict` request.
5. Show `/metrics` as the monitoring entry point.
6. Run `pytest` to prove the service is tested.
7. Show the GitHub Actions workflow as the CI/CD foundation.
