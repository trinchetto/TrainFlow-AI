# Template Quick Start Guide

## Quick Setup (5 minutes)

### Step 1: Copy Template Files

Copy all files from this `repo-template` directory to your new project.

### Step 2: Find and Replace Placeholders

Use your editor's find-and-replace feature (case-sensitive):

| Placeholder | Example | Description |
|------------|---------|-------------|
| `{{PROJECT_NAME}}` | `my-awesome-app` | Kebab-case project name |
| `{{PACKAGE_NAME}}` | `my_awesome_app` | Snake_case Python package name |
| `{{PROJECT_DESCRIPTION}}` | `An awesome Python application` | Short description |
| `{{AUTHOR_NAME}}` | `John Doe` | Your name |
| `{{AUTHOR_EMAIL}}` | `john@example.com` | Your email |

### Step 3: Rename Package Directory

```bash
mv src/{{PACKAGE_NAME}} src/your_package_name
```

### Step 4: Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

### Step 5: Initialize Git and Install

```bash
git init
poetry install
poetry run pre-commit install
```

### Step 6: Run Tests

```bash
poetry run pytest
```

## Placeholder Location Reference

### Files Containing Placeholders

- ✓ `pyproject.toml` - All placeholders
- ✓ `Dockerfile` - `{{PACKAGE_NAME}}`
- ✓ `.github/workflows/ci.yml` - `{{PACKAGE_NAME}}`
- ✓ `scripts/test_docker.sh` - `{{PROJECT_NAME}}`
- ✓ `scripts/deploy_cloud_run.sh` - `{{PROJECT_NAME}}`
- ✓ `src/{{PACKAGE_NAME}}/__init__.py` - `{{PROJECT_DESCRIPTION}}`
- ✓ `src/{{PACKAGE_NAME}}/main.py` - `{{PROJECT_NAME}}`

### Directory to Rename

- `src/{{PACKAGE_NAME}}/` → `src/your_package_name/`

## What's Included

### Development Tools
- **Poetry**: Modern dependency management
- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage
- **Pre-commit**: Automated code quality checks

### CI/CD
- **GitHub Actions**: Automated testing and deployment
- **Dependabot**: Automated dependency updates
- **Coverage Badge**: Visual test coverage indicator

### Docker & Cloud
- **Dockerfile**: Optimized multi-stage build
- **Cloud Build**: Google Cloud Build configuration
- **Cloud Run**: Automated deployment scripts
- **.gcloudignore**: Optimized deployment size

## Testing the Template

After setup, verify everything works:

```bash
# 1. Verify dependencies install
poetry install

# 2. Run tests
poetry run pytest

# 3. Run pre-commit hooks
poetry run pre-commit run --all-files

# 4. Test Docker build
docker build -t test-image .

# 5. Run smoke test (if applicable)
bash scripts/test_docker.sh
```

## Common Customizations

### Change Python Version

Edit `pyproject.toml`:
```toml
[tool.poetry.dependencies]
python = "^3.11"  # Change to your version
```

Also update:
- `Dockerfile`: `FROM python:3.11-slim`
- `.github/workflows/ci.yml`: `python-version: "3.11"`

### Add Dependencies

```bash
poetry add requests httpx pydantic
poetry add --group dev pytest-asyncio black
```

### Modify Entry Point

Edit `Dockerfile` CMD line based on your app type:

**CLI Tool:**
```dockerfile
CMD ["python", "-m", "{{PACKAGE_NAME}}"]
```

**Web API (FastAPI/Uvicorn):**
```dockerfile
CMD ["uvicorn", "{{PACKAGE_NAME}}.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Streamlit:**
```dockerfile
CMD ["streamlit", "run", "src/{{PACKAGE_NAME}}/app.py", "--server.port", "8080"]
```

**Chainlit:**
```dockerfile
CMD ["chainlit", "run", "src/{{PACKAGE_NAME}}/app.py", "--host", "0.0.0.0", "--port", "8080"]
```

### Disable Cloud Run Deployment

Comment out or remove the `deploy-cloud-run` job in `.github/workflows/ci.yml`:

```yaml
# deploy-cloud-run:
#   runs-on: ubuntu-latest
#   ...
```

## GitHub Secrets Setup

Navigate to your repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `WIF_PROVIDER` | Workload Identity Federation provider | `projects/123/locations/global/...` |
| `WIF_SERVICE_ACCOUNT` | Service account email | `github-actions@project.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | Google Cloud project ID | `my-gcp-project` |
| `CLOUD_RUN_REGION` | Cloud Run region | `us-central1` |
| `CLOUD_RUN_SERVICE` | Cloud Run service name | `my-service` |

## Troubleshooting

### Pre-commit hooks fail

```bash
# Update hooks
poetry run pre-commit autoupdate

# Skip if needed (not recommended)
git commit --no-verify
```

### Poetry lock issues

```bash
# Update lock file
poetry lock --no-update

# Or regenerate
rm poetry.lock && poetry install
```

### Docker build fails

Check:
1. Poetry version in Dockerfile matches installed version
2. All dependencies are in pyproject.toml
3. PYTHONPATH is correctly set

### Type checking fails

Add module overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["untyped_library.*"]
ignore_missing_imports = true
```

## Next Steps

1. ✓ Set up GitHub repository
2. ✓ Configure GitHub secrets (if using Cloud Run)
3. ✓ Add your application code to `src/{{PACKAGE_NAME}}/`
4. ✓ Write tests in `tests/`
5. ✓ Update README.md with project-specific info
6. ✓ Create your first commit
7. ✓ Push to GitHub and verify CI passes

Happy coding! 🚀
