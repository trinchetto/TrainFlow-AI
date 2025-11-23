#!/bin/bash

# Setup Workload Identity Federation for GitHub Actions - Fixed Version
# This version uses the latest Google Cloud recommendations

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 trainflow-ai"
    exit 1
fi

PROJECT_ID=$1
REPO_OWNER="trinchetto"
REPO_NAME="TrainFlow-AI"
POOL_ID="github-wif-pool"
PROVIDER_ID="github-wif-provider"
SERVICE_ACCOUNT="github-actions-sa"

echo "Setting up Workload Identity Federation for project: $PROJECT_ID"
echo "Repository: $REPO_OWNER/$REPO_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create service account if it doesn't exist
echo "Creating service account..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then
    echo "Service account $SERVICE_ACCOUNT already exists, skipping creation"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT \
        --display-name="GitHub Actions Service Account" \
        --description="Service account for GitHub Actions deployments"
fi

# Grant necessary roles
echo "Granting roles to service account..."
ROLES=(
    "roles/run.admin"
    "roles/cloudbuild.builds.builder"
    "roles/storage.admin"
    "roles/iam.serviceAccountUser"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role" >/dev/null
done

# Create Cloud Build logs bucket
LOGS_BUCKET="${PROJECT_ID}-cloudbuild-logs"
echo "Creating Cloud Build logs bucket..."
if gsutil ls gs://"${LOGS_BUCKET}" >/dev/null 2>&1; then
    echo "Logs bucket already exists"
else
    gsutil mb gs://"${LOGS_BUCKET}"
    echo "Created logs bucket: gs://${LOGS_BUCKET}"
fi

# Grant the service account access to the logs bucket
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://"${LOGS_BUCKET}"

# Also grant Cloud Build service account access
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
gsutil iam ch serviceAccount:${CLOUDBUILD_SA}:objectAdmin gs://"${LOGS_BUCKET}"

# Create workload identity pool
echo "Creating workload identity pool..."
gcloud iam workload-identity-pools create $POOL_ID \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --description="Identity pool for GitHub Actions"

# Get the full pool ID
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe $POOL_ID \
    --location="global" \
    --format="value(name)")

# Create OIDC provider with proper attribute mapping for GitHub
echo "Creating workload identity provider..."
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
    --location="global" \
    --workload-identity-pool=$POOL_ID \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository=='$REPO_OWNER/$REPO_NAME'"

# Allow the GitHub repo to impersonate the service account
echo "Setting up impersonation..."
gcloud iam service-accounts add-iam-policy-binding \
    $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/$WORKLOAD_IDENTITY_POOL_ID/attribute.repository/$REPO_OWNER/$REPO_NAME"

# Get the workload identity provider
WORKLOAD_IDENTITY_PROVIDER=$(gcloud iam workload-identity-pools providers describe $PROVIDER_ID \
    --location="global" \
    --workload-identity-pool=$POOL_ID \
    --format="value(name)")

echo ""
echo "🎉 Workload Identity Federation setup complete!"
echo ""
echo "Add these secrets to your GitHub repository ($REPO_OWNER/$REPO_NAME):"
echo "Settings > Secrets and variables > Actions > Repository secrets"
echo ""
echo "WIF_PROVIDER: $WORKLOAD_IDENTITY_PROVIDER"
echo "WIF_SERVICE_ACCOUNT: $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"
echo "GCP_PROJECT_ID: $PROJECT_ID"
echo ""
echo "Other secrets you need to add:"
echo "CLOUD_RUN_REGION: us-central1"
echo "CLOUD_RUN_SERVICE: trainflow-ai"
echo "OPENAI_API_KEY: <your-openai-api-key>"