# TrainFlow-AI

![Test Coverage](./coverage.svg)

TrainFlow-AI is a Python package that will power an AI-based endurance coach assistant. The repository currently ships with a tiny placeholder implementation so that tooling, tests, and automation can run end-to-end.

## Getting started

1. [Install Poetry](https://python-poetry.org/docs/#installation)
2. Install dependencies:

   ```bash
   poetry install
   ```

3. Run the quality gates locally:

   ```bash
   poetry run pre-commit run --all-files
   poetry run pytest
   ```

## License

This project is released under the terms of the [MIT License](LICENSE).
