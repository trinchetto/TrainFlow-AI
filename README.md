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

## Docker & Cloud Run

1. Populate the `.env` file with the required OpenAI and Google Cloud values (placeholders are provided).
2. Build the container:

   ```bash
   docker build -t trainflow-ai .
   ```

3. Test locally by running the container and passing the `.env` variables:

   ```bash
   docker run --rm --env-file .env -p 8000:8080 trainflow-ai
   ```

   Visit `http://localhost:8000` and chat with the assistant to confirm the deployment works. When no valid `OPENAI_API_KEY` is supplied the fallback responses are used, which still validates the Chainlit wiring.

4. Deploy to Cloud Run (example):

   ```bash
   source .env
   gcloud auth activate-service-account --key-file "$GOOGLE_APPLICATION_CREDENTIALS"
   gcloud config set project "$GCP_PROJECT_ID"
   gcloud run deploy "${CLOUD_RUN_SERVICE}" \
     --image gcr.io/${GCP_PROJECT_ID}/${CLOUD_RUN_SERVICE}:latest \
     --region "${CLOUD_RUN_REGION}" \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=${OPENAI_API_KEY},OPENAI_MODEL=${OPENAI_MODEL}
   ```

   You can substitute the image reference if you push a different tag. After deployment, open the Cloud Run URL to verify the UI is reachable.

## License

This project is released under the terms of the [MIT License](LICENSE).
