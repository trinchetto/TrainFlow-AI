# Python Project Template

A comprehensive Python project template with Poetry, CI/CD, Docker, and Google Cloud Run deployment.

## Template Overview

This template provides a complete project structure with:

- **Dependency Management**: Poetry for package and dependency management
- **Code Quality**: Ruff (linting & formatting) + MyPy (type checking)
- **Testing**: Pytest with coverage reporting and parallel execution
- **Pre-commit Hooks**: Automated code quality checks
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
- **Containerization**: Docker configuration optimized for Cloud Run
- **Cloud Deployment**: Automated deployment to Google Cloud Run

## Setup Instructions

### 1. Replace Placeholders

Search and replace the following placeholders throughout the template:

- `{{PROJECT_NAME}}`: Your project name (e.g., `my-awesome-project`)
- `{{PACKAGE_NAME}}`: Your Python package name (e.g., `my_awesome_project`)
- `{{PROJECT_DESCRIPTION}}`: Brief project description
- `{{AUTHOR_NAME}}`: Your name
- `{{AUTHOR_EMAIL}}`: Your email address

**Files to update:**
- `pyproject.toml`
- `Dockerfile`
- `.github/workflows/ci.yml`
- `scripts/test_docker.sh`
- `scripts/deploy_cloud_run.sh`
- `src/{{PACKAGE_NAME}}/__init__.py`
- `src/{{PACKAGE_NAME}}/main.py`

**Important**: Rename the directory `src/{{PACKAGE_NAME}}` to `src/your_package_name`

### 2. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### 3. Configure GitHub Secrets

For CI/CD and Cloud Run deployment, add these secrets to your GitHub repository:

**Required for Cloud Run deployment:**
- `WIF_PROVIDER`: Workload Identity Federation provider
- `WIF_SERVICE_ACCOUNT`: Service account email for WIF
- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `CLOUD_RUN_REGION`: Cloud Run region (e.g., `us-central1`)
- `CLOUD_RUN_SERVICE`: Cloud Run service name

**Optional secrets:**
Add any environment variables your application needs (e.g., API keys)

### 4. Project Structure

```
.
├── .github/
│   ├── workflows/
│   │   └── ci.yml                 # CI/CD pipeline
│   └── dependabot.yml             # Dependency updates
├── scripts/
│   ├── test_docker.sh             # Docker smoke test
│   └── deploy_cloud_run.sh        # Cloud Run deployment
├── src/
│   └── {{PACKAGE_NAME}}/          # Your package source code
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_example.py            # Example tests
├── .gitignore                     # Git ignore rules
├── .gcloudignore                  # GCloud ignore rules
├── .pre-commit-config.yaml        # Pre-commit hooks config
├── cloudbuild.yaml                # Google Cloud Build config
├── Dockerfile                     # Container definition
├── pyproject.toml                 # Poetry & tool configuration
└── README.md                      # This file
```

## Development Workflow

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov={{PACKAGE_NAME}} --cov-report=term

# Run tests in parallel
poetry run pytest -n auto

# Generate coverage badge
poetry run coverage-badge -o coverage.svg -f
```

### Code Quality

```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run linter only
poetry run ruff check .

# Run formatter
poetry run ruff format .

# Run type checker
poetry run mypy src
```

### Docker

```bash
# Build Docker image
docker build -t {{PROJECT_NAME}} .

# Run container locally
docker run -p 8080:8080 {{PROJECT_NAME}}

# Run smoke test
bash scripts/test_docker.sh
```

### Cloud Run Deployment

```bash
# Deploy to Cloud Run
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export SERVICE_NAME={{PROJECT_NAME}}
bash scripts/deploy_cloud_run.sh
```

## CI/CD Pipeline

The GitHub Actions workflow consists of three jobs:

1. **lint-and-test**: Runs pre-commit hooks and pytest with coverage
2. **docker-test**: Builds and smoke tests the Docker container
3. **deploy-cloud-run**: Deploys to Cloud Run (only on main branch pushes)

## Customization Tips

### Adding Dependencies

```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name
```

### Modifying Dockerfile

Update the `CMD` instruction to match your application's entry point:

```dockerfile
CMD ["sh", "-c", "python src/{{PACKAGE_NAME}}/main.py"]
```

Common alternatives:
- Web app: `CMD ["uvicorn", "{{PACKAGE_NAME}}.main:app", "--host", "0.0.0.0", "--port", "8080"]`
- Chainlit: `CMD ["chainlit", "run", "src/{{PACKAGE_NAME}}/app.py", "--host", "0.0.0.0", "--port", "8080"]`

### Adjusting Cloud Run Resources

Edit `scripts/deploy_cloud_run.sh`:

```bash
--memory=512Mi          # Adjust memory allocation
--cpu=1                 # Adjust CPU allocation
--max-instances=10      # Adjust max instances
--timeout=900           # Adjust request timeout
```

## Additional Suggestions

Consider adding these enhancements to your project:

### 1. Documentation
- **Sphinx or MkDocs**: For comprehensive documentation
- **Docstrings**: Google-style or NumPy-style docstrings
- **API Documentation**: Auto-generated from code

### 2. Monitoring & Observability
- **Logging**: Structured logging with `structlog` or `python-json-logger`
- **Metrics**: Prometheus metrics integration
- **Tracing**: OpenTelemetry for distributed tracing
- **Error Tracking**: Sentry integration

### 3. Security
- **Dependency Scanning**: Snyk or GitHub Advanced Security
- **Secret Scanning**: git-secrets or TruffleHog
- **SAST**: Bandit for security linting
- **Container Scanning**: Trivy or Grype

### 4. Additional Development Tools
- **Task Runner**: `invoke` or `make` for common tasks
- **Environment Management**: `python-dotenv` for local development
- **Database Migrations**: Alembic (if using SQLAlchemy)
- **API Documentation**: OpenAPI/Swagger spec generation

### 5. Testing Enhancements
- **Integration Tests**: Separate test directory
- **E2E Tests**: Playwright or Selenium for web apps
- **Load Testing**: Locust or k6
- **Mutation Testing**: `mutmut` for test quality

### 6. Code Quality Enhancements
- **Complexity Checking**: radon or mccabe
- **Import Sorting**: isort (or use ruff's import sorting)
- **Docstring Coverage**: interrogate
- **Dead Code Detection**: vulture

### 7. CI/CD Enhancements
- **Release Automation**: semantic-release or release-drafter
- **Changelog Generation**: git-changelog or towncrier
- **Performance Benchmarks**: pytest-benchmark
- **Test Sharding**: Split tests across multiple runners

### 8. Cloud Infrastructure
- **Infrastructure as Code**: Terraform or Pulumi
- **Service Mesh**: Istio or Linkerd (for complex microservices)
- **CDN**: Cloud CDN for static assets
- **Secrets Management**: Google Secret Manager integration

### 9. Additional GitHub Features
- **Issue Templates**: `.github/ISSUE_TEMPLATE/`
- **PR Templates**: `.github/pull_request_template.md`
- **Code Owners**: `.github/CODEOWNERS`
- **Security Policy**: `SECURITY.md`

### 10. Development Experience
- **Dev Containers**: `.devcontainer/` for VS Code
- **Docker Compose**: For local multi-service development
- **Makefile**: Common development commands
- **EditorConfig**: Consistent coding styles across editors

## License

This template is provided as-is. Add your own LICENSE file for your project.

## Support

For issues with the template structure, refer to the source repository.
