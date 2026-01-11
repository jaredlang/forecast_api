#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="weather-forecast-api"
TAG="${TAG:-latest}"

PORT="${PORT:-8200}"
MEMORY="${MEMORY:-512Mi}"
CPU="${CPU:-1}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
TIMEOUT="${TIMEOUT:-300}"

CLOUD_SQL_INSTANCE="weather-forecasts"
CLOUD_SQL_PASSWORD_SECRET="forecast_db_password:latest"

# Construct full image path
IMAGE_PATH="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${TAG}"

# Required environment variables
if [ -z "${WEATHER_AGENT_URL}" ]; then
  echo "Error: WEATHER_AGENT_URL environment variable is required"
  exit 1
fi

echo "Deploying pre-built image to Cloud Run..."
echo "Image: $IMAGE_PATH"

echo "================================================"
echo "Deploying to Cloud Run"
echo "================================================"
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Name: ${SERVICE_NAME}"
echo "Image: ${IMAGE_PATH}"
echo "Port: ${PORT}"
echo "Memory: ${MEMORY}"
echo "CPU: ${CPU}"
echo "Max Instances: ${MAX_INSTANCES}"
echo "Min Instances: ${MIN_INSTANCES}"
echo "Timeout: ${TIMEOUT}s"
echo "Weather Agent URL: ${WEATHER_AGENT_URL}"
echo "================================================"

gcloud run deploy $SERVICE_NAME \
    --image "$IMAGE_PATH" \
    --platform=managed \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --port="${PORT}" \
    --memory="${MEMORY}" \
    --cpu="${CPU}" \
    --max-instances="${MAX_INSTANCES}" \
    --min-instances="${MIN_INSTANCES}" \
    --timeout="${TIMEOUT}" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars "GOOGLE_CLOUD_LOCATION=${REGION}" \
    --set-env-vars "CLOUD_SQL_INSTANCE=${CLOUD_SQL_INSTANCE}" \
    --set-secrets "CLOUD_SQL_PASSWORD=${CLOUD_SQL_PASSWORD_SECRET}" \
    --add-cloudsql-instances "${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}" \
    --set-env-vars "WEATHER_AGENT_URL=${WEATHER_AGENT_URL}"

echo "================================================"
echo "Deployment completed successfully!"
echo "================================================"

echo "Service URL:"
gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)'

echo "================================================"
