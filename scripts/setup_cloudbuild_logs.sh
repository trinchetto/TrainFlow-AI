#!/bin/bash

# Configure Cloud Build logging bucket for VPC-SC environments
# Run this script to set up proper logging for Cloud Build within VPC-SC perimeter

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 trainflow-ai"
    exit 1
fi

PROJECT_ID=$1
LOGS_BUCKET="${PROJECT_ID}-cloudbuild-logs"

echo "Configuring Cloud Build logging for project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Get project number for Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Create the logs bucket
echo "Creating logs bucket: gs://${LOGS_BUCKET}"
if gsutil ls gs://"${LOGS_BUCKET}" >/dev/null 2>&1; then
    echo "Logs bucket already exists"
else
    gsutil mb gs://"${LOGS_BUCKET}"
    
    # Set bucket location and storage class for better performance
    gsutil lifecycle set /dev/stdin gs://"${LOGS_BUCKET}" <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF
    
    echo "Created logs bucket with 30-day lifecycle policy"
fi

# Grant Cloud Build service account access
echo "Granting Cloud Build service account access to logs bucket..."
gsutil iam ch serviceAccount:${CLOUDBUILD_SA}:objectAdmin gs://"${LOGS_BUCKET}"

# Grant GitHub Actions service account access (if it exists)
GITHUB_SA="github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe $GITHUB_SA >/dev/null 2>&1; then
    echo "Granting GitHub Actions service account access to logs bucket..."
    gsutil iam ch serviceAccount:${GITHUB_SA}:objectAdmin gs://"${LOGS_BUCKET}"
fi

echo ""
echo "✅ Cloud Build logging configuration complete!"
echo ""
echo "Logs bucket: gs://${LOGS_BUCKET}"
echo "This bucket is now configured for Cloud Build logs within your VPC-SC perimeter."
echo ""
echo "To use this bucket in your builds, your cloudbuild.yaml should include:"
echo "options:"
echo "  logging: GCS_ONLY"
echo "  logStreamingOption: STREAM_OFF"