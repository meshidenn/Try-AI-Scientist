#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-${PROJECT_DIR}/workspace}"
HF_HOME_HOST="${HF_HOME_HOST:-/home/hiroki/.cache/huggingface}"
IMAGE="${IMAGE:-vllm/vllm-openai:gemma4-cu130}"
MODEL="${MODEL:-google/gemma-4-26B-A4B-it}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-gemma4-26b-moe}"
PORT="${PORT:-18021}"
CONTAINER="${CONTAINER:-toyota-pdf-gemma4-vllm}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
STARTUP_TIMEOUT_SEC="${STARTUP_TIMEOUT_SEC:-1800}"
LOG_DIR="${LOG_DIR:-${PROJECT_DIR}/logs}"

mkdir -p "${LOG_DIR}"
docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true

docker run -d --gpus all \
  --name "${CONTAINER}" \
  --ipc=host \
  --shm-size=16g \
  --network bridge \
  -p "127.0.0.1:${PORT}:${PORT}" \
  -v "${HF_HOME_HOST}:/root/.cache/huggingface" \
  -v "${WORKSPACE_DIR}:/workspace:ro" \
  "${IMAGE}" \
  "${MODEL}" \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --limit-mm-per-prompt.image 1 \
  --allowed-local-media-path /workspace \
  --trust-remote-code \
  >"${LOG_DIR}/vllm.container-id"

deadline=$((SECONDS + STARTUP_TIMEOUT_SEC))
until curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; do
  if (( SECONDS >= deadline )); then
    docker logs "${CONTAINER}" >"${LOG_DIR}/vllm.server.log" 2>&1 || true
    echo "ERROR: vLLM startup timed out" >&2
    exit 1
  fi
  if ! docker ps --filter "name=${CONTAINER}" --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker logs "${CONTAINER}" >"${LOG_DIR}/vllm.server.log" 2>&1 || true
    echo "ERROR: vLLM container exited" >&2
    exit 1
  fi
  sleep 10
done

docker logs "${CONTAINER}" >"${LOG_DIR}/vllm.server.ready.log" 2>&1 || true
echo "vLLM server is ready: http://127.0.0.1:${PORT}/v1"
