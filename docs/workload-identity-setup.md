# Workload Identity Federation Setup

Set up secure authentication between GitHub Actions and Google Cloud using Workload Identity Federation. No service account keys needed.

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- Admin access to your GitHub repository

## Setup Steps

### 1. Run the Setup Script

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Run the setup script
./scripts/setup_workload_identity.sh YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

### 2. Add GitHub Secrets

The script will output the required values. Add these secrets to your GitHub repository:

**Go to:** Settings → Secrets and variables → Actions → Repository secrets

| Secret Name | Example Value |
|-------------|---------------|
| `WIF_PROVIDER` | `projects/123456789/locations/global/workloadIdentityPools/github-wif-pool/providers/github-wif-provider` |
| `WIF_SERVICE_ACCOUNT` | `github-actions-sa@your-project.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | `your-project-id` |
| `CLOUD_RUN_REGION` | `us-central1` |
| `CLOUD_RUN_SERVICE` | `trainflow-ai` |
| `OPENAI_API_KEY` | `sk-...` |

### 3. Deploy

Push to the main branch to trigger deployment:

```bash
git push origin main
```

## What This Does

- Creates a service account with minimal required permissions
- Sets up Workload Identity Federation pool and provider
- Configures repository-specific access restrictions
- Enables secure, keyless authentication from GitHub Actions to Google Cloud

## Troubleshooting

If you get authentication errors, verify:

1. All GitHub secrets are added correctly
2. The `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT` values match the script output exactly
3. Your repository name matches `trinchetto/TrainFlow-AI` (update the script if different)

