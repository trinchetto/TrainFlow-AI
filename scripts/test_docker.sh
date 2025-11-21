#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-trainflow-ai-ci}
CONTAINER_NAME=chainlit-ci-test

trap 'docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true' EXIT

docker build -t "${IMAGE}" .

docker run -d --name "${CONTAINER_NAME}" \
  --env OPENAI_API_KEY=dummy \
  --env OPENAI_MODEL=gpt-4o-mini \
  -p 127.0.0.1:8001:8080 \
  "${IMAGE}" >/dev/null

for _ in {1..30}; do
  if curl -fsS http://127.0.0.1:8001 >/dev/null; then
    echo "Chainlit UI reachable"
    exit 0
  fi
  sleep 2
done

echo "Chainlit UI did not respond in time" >&2
exit 1
