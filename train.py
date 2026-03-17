"""
train.py -- Train a classifier and log results to MLflow.

Reads MLFLOW_TRACKING_URI from the environment (set as a GitHub Actions secret).
Reads FORCE_ACCURACY from the environment to override the logged accuracy
(used only for demonstrating a pipeline failure when accuracy < 0.85).
Writes the MLflow Run ID to model_info.txt for handover to the deploy job.
"""
import os
import sys

import mlflow
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# ── MLflow setup ──────────────────────────────────────────────────────────────
TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI") or "mlruns"
mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment("iris-classifier")

# ── Load dataset ──────────────────────────────────────────────────────────────
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Train model ───────────────────────────────────────────────────────────────
N_ESTIMATORS = 100
clf = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=42)
clf.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
real_accuracy = accuracy_score(y_test, clf.predict(X_test))

# FORCE_ACCURACY overrides the logged value (used to demo a failure run)
force_acc = os.environ.get("FORCE_ACCURACY", "").strip()
accuracy = float(force_acc) if force_acc else real_accuracy

if force_acc:
    print(f"[OVERRIDE] FORCE_ACCURACY={accuracy} (real accuracy was {real_accuracy:.4f})")

# ── Log to MLflow ─────────────────────────────────────────────────────────────
with mlflow.start_run() as run:
    run_id = run.info.run_id
    mlflow.log_param("n_estimators", N_ESTIMATORS)
    mlflow.log_param("test_size", 0.2)
    mlflow.log_metric("accuracy", accuracy)

print(f"Run ID  : {run_id}")
print(f"Accuracy: {accuracy:.4f}")
print(f"Tracking: {TRACKING_URI}")

# ── Write Run ID to model_info.txt ────────────────────────────────────────────
with open("model_info.txt", "w") as f:
    f.write(run_id)

print("model_info.txt written successfully.")
sys.exit(0)
