#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="weather-forecast-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
CLOUD_SQL_INSTANCE="weather-forecasts"

echo "Deploying pre-built image to Cloud Run..."
echo "Image: $IMAGE_NAME"

gcloud run deploy $SERVICE_NAME \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars "GOOGLE_CLOUD_LOCATION=${REGION}" \
    --set-env-vars "CLOUD_SQL_INSTANCE=${CLOUD_SQL_INSTANCE}" \
    --set-secrets "CLOUD_SQL_PASSWORD=forecast_db_password:latest" \
    --add-cloudsql-instances "${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}"

echo ""
echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.url)'
