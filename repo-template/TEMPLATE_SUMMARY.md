# Repository Template - Extraction Summary

This template was extracted from the **TrainFlow-AI** repository to create a reusable foundation for Python projects with modern tooling and Cloud Run deployment.

## What's Included in This Template

### 📦 Dependency Management
- **Poetry** configuration with modern Python package management
- Lock file excluded from git (for library development)
- Separate dev dependencies group
- Build system configuration

### 🧪 Testing Infrastructure
- **Pytest** with parallel execution via pytest-xdist
- Test coverage reporting with pytest-cov
- Coverage badge generation
- Example test structure in `tests/`
- Pytest configuration in pyproject.toml

### 🔍 Code Quality Tools
- **Ruff**: Fast linting and formatting (replaces Black, isort, flake8)
- **MyPy**: Strict static type checking
- **Pre-commit hooks**: Automated quality checks before commits
- Configuration in pyproject.toml and .pre-commit-config.yaml

### 🚀 CI/CD Pipeline
- **GitHub Actions workflow** with three stages:
  1. Lint and test (runs pre-commit + pytest)
  2. Docker test (builds and smoke tests container)
  3. Cloud Run deployment (on main branch only)
- **Dependabot** configuration for weekly dependency updates
- Coverage badge generation in CI

### 🐳 Docker Configuration
- **Multi-stage Dockerfile** optimized for production
- Python 3.12-slim base image
- Poetry installation and dependency management
- Configurable entry point
- Cloud Run optimized settings

### ☁️ Google Cloud Run Deployment
- **Cloud Build** configuration (cloudbuild.yaml)
- **Deployment script** with configurable resources
- **Smoke test script** for Docker validation
- **.gcloudignore** for optimized deployment size
- Workload Identity Federation support

### 📝 Configuration Files
- **.gitignore**: Comprehensive Python exclusions
- **.gcloudignore**: Cloud deployment exclusions
- **.pre-commit-config.yaml**: Hook configuration
- **.github/dependabot.yml**: Dependency update automation

### 📚 Documentation
- **README.md**: Complete setup and usage guide
- **TEMPLATE_GUIDE.md**: Quick start reference
- **TEMPLATE_SUMMARY.md**: This file

## Template Structure

```
repo-template/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                    # CI/CD pipeline
│   └── dependabot.yml                # Dependency updates
├── scripts/
│   ├── test_docker.sh                # Docker smoke testing
│   └── deploy_cloud_run.sh           # Cloud Run deployment
├── src/
│   └── {{PACKAGE_NAME}}/             # Package source (rename this!)
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_example.py               # Example test file
├── .gitignore                        # Git exclusions
├── .gcloudignore                     # GCloud exclusions
├── .pre-commit-config.yaml           # Pre-commit hooks
├── cloudbuild.yaml                   # Cloud Build config
├── Dockerfile                        # Container definition
├── pyproject.toml                    # Poetry & tool config
├── README.md                         # Full documentation
├── TEMPLATE_GUIDE.md                 # Quick start guide
└── TEMPLATE_SUMMARY.md               # This file
```

## Placeholders to Replace

Use find-and-replace (case-sensitive) across all files:

| Placeholder | Description | Location |
|------------|-------------|----------|
| `{{PROJECT_NAME}}` | Kebab-case project name | Multiple files |
| `{{PACKAGE_NAME}}` | Snake_case package name | Multiple files |
| `{{PROJECT_DESCRIPTION}}` | Project description | pyproject.toml, __init__.py |
| `{{AUTHOR_NAME}}` | Author name | pyproject.toml |
| `{{AUTHOR_EMAIL}}` | Author email | pyproject.toml |

**Don't forget to rename:** `src/{{PACKAGE_NAME}}/` → `src/your_package_name/`

## Technology Stack

| Category | Tool | Version |
|----------|------|---------|
| Language | Python | 3.12+ |
| Package Manager | Poetry | 1.8.4 |
| Linter/Formatter | Ruff | 0.14.8 |
| Type Checker | MyPy | 1.11.1 |
| Test Framework | Pytest | 9.0.2 |
| Test Runner | pytest-xdist | 3.6.1 |
| Coverage | pytest-cov | 5.0+ |
| Pre-commit | pre-commit | 4.4.0 |
| Container | Docker | N/A |
| Cloud Platform | Google Cloud Run | N/A |
| CI/CD | GitHub Actions | N/A |

## Features Not Included (But Recommended)

Consider adding based on your project needs:

### Documentation
- Sphinx or MkDocs for comprehensive docs
- API documentation generation
- Contribution guidelines

### Monitoring & Observability
- Structured logging (structlog)
- Error tracking (Sentry)
- Performance monitoring (APM)
- OpenTelemetry integration

### Security
- Dependency vulnerability scanning (Snyk, Safety)
- Secret scanning (git-secrets, TruffleHog)
- SAST tools (Bandit)
- Container scanning (Trivy, Grype)

### Development Experience
- Dev containers (.devcontainer/)
- Docker Compose for local development
- Makefile for common tasks
- Task runner (invoke, just)

### Advanced Testing
- Integration test suite
- E2E tests (Playwright, Selenium)
- Load testing (Locust, k6)
- Mutation testing (mutmut)

### Infrastructure
- Terraform/Pulumi for IaC
- Kubernetes manifests (if not using Cloud Run)
- Service mesh configuration
- CDN setup

### CI/CD Enhancements
- Release automation (semantic-release)
- Changelog generation
- Performance benchmarking
- Test result reporting

## Source Repository

Extracted from: **TrainFlow-AI**
- Original purpose: AI-based endurance coach assistant
- Technologies: LangGraph, Chainlit, LangChain, OpenAI
- Deployment: Google Cloud Run

## Usage Tips

### For New Projects
1. Copy entire `repo-template/` directory
2. Replace all placeholders
3. Rename package directory
4. Run `poetry install`
5. Start coding!

### For Existing Projects
1. Cherry-pick files you need
2. Merge with existing configuration
3. Adopt incrementally
4. Test thoroughly

### Customization
- Modify Ruff rules in `pyproject.toml` → `[tool.ruff.lint]`
- Adjust MyPy strictness in `pyproject.toml` → `[tool.mypy]`
- Add pre-commit hooks in `.pre-commit-config.yaml`
- Configure Cloud Run resources in `scripts/deploy_cloud_run.sh`

## License

This template follows the MIT license. Add your own LICENSE file for your project.

## Support

For questions about this template, refer to:
- **README.md** for comprehensive documentation
- **TEMPLATE_GUIDE.md** for quick start instructions
- Original TrainFlow-AI repository for examples

---

**Version**: 1.0
**Last Updated**: 2025-12-17
**Extracted From**: TrainFlow-AI v0.1.0
