# Dockerfile
# Accepts the MLflow Run ID as a build argument so the correct model
# version can be fetched at image-build time.

FROM python:3.10-slim

# Accept the MLflow Run ID at build time
ARG RUN_ID
ENV RUN_ID=${RUN_ID}

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir mlflow scikit-learn

# Simulate downloading the model for the given Run ID
RUN echo "Downloading model for MLflow Run ID: ${RUN_ID}"

# Copy application code
COPY train.py .
COPY check_threshold.py .

CMD ["python", "-c", "import os; print('Model container ready. Run ID:', os.environ.get('RUN_ID', 'not set'))"]
