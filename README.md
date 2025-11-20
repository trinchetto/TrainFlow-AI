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

## Chainlit UI

An interactive [Chainlit](https://docs.chainlit.io/) workspace is included to chat with the LangGraph coach graph.

1. Export `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, default `gpt-4o-mini`). Without a key, the UI falls back to deterministic placeholder plans.
2. Start the UI:

   ```bash
   poetry run chainlit run src/trainflow_ai/chainlit_app.py --port 8000 --watch
   ```

3. Open the printed URL to ask questions; each prompt is passed through the graph defined in `src/trainflow_ai/coach_graph.py`.

## License

This project is released under the terms of the [MIT License](LICENSE).
