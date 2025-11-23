#!/usr/bin/env bash
set -euo pipefail

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required" >&2
  exit 1
fi

PROJECT_ID=${PROJECT_ID:-}
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-trainflow-ai}
IMAGE_TAG=${IMAGE_TAG:-$(git rev-parse --short HEAD)}

if [[ -z "$PROJECT_ID" ]]; then
  echo "PROJECT_ID environment variable must be set" >&2
  exit 1
fi

IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"

OPENAI_FLAG=()
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  OPENAI_FLAG=("--set-env-vars" "OPENAI_API_KEY=${OPENAI_API_KEY}")
fi

LOGS_BUCKET="${PROJECT_ID}-cloudbuild-logs"

echo "Creating logs bucket if it doesn't exist..."
gsutil mb gs://"${LOGS_BUCKET}" 2>/dev/null || echo "Bucket already exists or creation skipped"

echo "Building image ${IMAGE}"
# Use Cloud Build config with custom logs bucket
BUILD_ID=$(gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions="_IMAGE_NAME=${IMAGE}" \
  --format="value(id)" \
  --timeout=10m \
  --gcs-log-dir="gs://${LOGS_BUCKET}/logs" \
  --gcs-source-staging-dir="gs://${LOGS_BUCKET}/staging" \
  .)
echo "Build completed with ID: ${BUILD_ID}"

echo "Deploying to Cloud Run service ${SERVICE_NAME} in ${REGION}"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --timeout=900 \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  "${OPENAI_FLAG[@]}"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format 'value(status.url)')
echo "Deployment complete. Service URL: ${SERVICE_URL}"
