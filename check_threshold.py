"""
check_threshold.py -- Gate the deploy job based on MLflow accuracy metric.

Reads the MLflow Run ID from model_info.txt (downloaded from the validate job
artifact), queries the local MLflow tracking store for the logged accuracy,
and exits with code 1 if the accuracy is below the threshold -- halting the
pipeline before any deployment happens.
"""
import os
import sys

import mlflow

THRESHOLD = 0.85

# ── MLflow setup ──────────────────────────────────────────────────────────────
TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "mlruns")
mlflow.set_tracking_uri(TRACKING_URI)

# ── Read Run ID ───────────────────────────────────────────────────────────────
try:
    with open("model_info.txt") as f:
        run_id = f.read().strip()
except FileNotFoundError:
    print("ERROR: model_info.txt not found. Was the model-info artifact downloaded?")
    sys.exit(1)

if not run_id:
    print("ERROR: model_info.txt is empty.")
    sys.exit(1)

print(f"Run ID   : {run_id}")
print(f"Tracking : {TRACKING_URI}")

# ── Query MLflow for the accuracy metric ──────────────────────────────────────
client = mlflow.tracking.MlflowClient()

try:
    run = client.get_run(run_id)
except Exception as exc:
    print(f"ERROR: Could not retrieve run {run_id} from MLflow: {exc}")
    sys.exit(1)

accuracy = run.data.metrics.get("accuracy")

if accuracy is None:
    print("ERROR: 'accuracy' metric not found in MLflow run.")
    sys.exit(1)

print(f"Accuracy : {accuracy:.4f}")
print(f"Threshold: {THRESHOLD}")
print("-" * 40)

# ── Threshold check ───────────────────────────────────────────────────────────
if accuracy < THRESHOLD:
    print(f"THRESHOLD CHECK FAILED -- {accuracy:.4f} < {THRESHOLD}")
    print("Pipeline halted: model does not meet the minimum accuracy requirement.")
    sys.exit(1)

print(f"THRESHOLD CHECK PASSED -- {accuracy:.4f} >= {THRESHOLD}")
print("Model approved for deployment.")
sys.exit(0)
