# Workload Identity Federation Quick Setup

## 🚀 Quick Setup Commands

### 1. Run the Setup Script

```bash
# Replace YOUR_PROJECT_ID with your actual GCP project ID
./scripts/setup_workload_identity.sh YOUR_PROJECT_ID
```

### 2. Add GitHub Secrets

The script will output values for these secrets. Add them to your repository:

#### GitHub Repository → Settings → Secrets and variables → Actions → Repository secrets

- `WIF_PROVIDER` - (provided by script output)
- `WIF_SERVICE_ACCOUNT` - (provided by script output)  
- `GCP_PROJECT_ID` - Your Google Cloud project ID
- `CLOUD_RUN_REGION` - e.g., `us-central1`
- `CLOUD_RUN_SERVICE` - e.g., `trainflow-ai`
- `OPENAI_API_KEY` - Your OpenAI API key

### 3. Deploy

```bash
git add .
git commit -m "Setup Workload Identity Federation"
git push origin main
```

## 📋 What This Sets Up

✅ **Secure authentication** - No service account keys in GitHub  
✅ **Automatic deployment** - Push to main → Deploy to Cloud Run  
✅ **Proper permissions** - Least privilege access  
✅ **Audit logging** - All actions tracked in Google Cloud  

## 📖 Full Documentation

See [`docs/workload-identity-setup.md`](workload-identity-setup.md) for detailed instructions and troubleshooting.

## ✅ Verification

After setup, check:

1. GitHub Actions workflow runs successfully on push to main
2. New Cloud Run revision is deployed
3. Service is accessible at the Cloud Run URL
