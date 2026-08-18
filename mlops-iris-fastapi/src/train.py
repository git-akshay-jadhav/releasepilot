from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "iris_model.joblib"


def train_model() -> dict[str, float]:
    iris = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        iris.data,
        iris.target,
        test_size=0.2,
        random_state=42,
        stratify=iris.target,
    )

    params = {
        "n_estimators": 100,
        "max_depth": 3,
        "random_state": 42,
    }
    model = RandomForestClassifier(**params)

    mlflow.set_tracking_uri(f"file:{ROOT / 'mlruns'}")
    mlflow.set_experiment("iris-classifier")

    with mlflow.start_run():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)

        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "f1_macro": f1_score(y_test, predictions, average="macro"),
        }

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name="model", input_example=x_test[:3])

        MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(
            {
                "model": model,
                "target_names": iris.target_names.tolist(),
                "feature_names": iris.feature_names,
                "metrics": metrics,
            },
            MODEL_PATH,
        )

    return metrics


if __name__ == "__main__":
    results = train_model()
    print(f"Model saved to {MODEL_PATH}")
    print(f"Accuracy: {results['accuracy']:.3f}")
    print(f"F1 macro: {results['f1_macro']:.3f}")
