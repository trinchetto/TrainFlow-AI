#!/usr/bin/env bash
set -euo pipefail

IMAGE=${IMAGE:-{{PROJECT_NAME}}-ci}
CONTAINER_NAME={{PROJECT_NAME}}-ci-test

trap 'docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true' EXIT

docker build -t "${IMAGE}" .

docker run -d --name "${CONTAINER_NAME}" \
  -p 127.0.0.1:8001:8080 \
  "${IMAGE}" >/dev/null

# Wait for the service to be ready
for _ in {1..30}; do
  if curl -fsS http://127.0.0.1:8001 >/dev/null; then
    echo "Service is reachable"
    exit 0
  fi
  sleep 2
done

echo "Service did not respond in time" >&2
exit 1
