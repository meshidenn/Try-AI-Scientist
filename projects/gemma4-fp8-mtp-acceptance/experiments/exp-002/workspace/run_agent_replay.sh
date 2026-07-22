#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="${EXP_DIR}/workspace"
RESULTS_DIR="${EXP_DIR}/results"
LOGS_DIR="${EXP_DIR}/logs"
IMAGE="${IMAGE:-vllm/vllm-openai:v0.24.0}"
HF_HOME_HOST="${HF_HOME_HOST:-/home/hiroki/.cache/huggingface}"
NUM_PROMPTS="${NUM_PROMPTS:-16}"
NUM_WARMUPS="${NUM_WARMUPS:-2}"
CONCURRENCIES="${CONCURRENCIES:-1,2,4}"
VARIANTS="${VARIANTS:-bf16_off,bf16_s1,bf16_s2,bf16_s4,bf16_s8,bf16_s16,fp8_off,fp8_s1,fp8_s2,fp8_s4,fp8_s8,fp8_s16}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.78}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"
STARTUP_TIMEOUT_SEC="${STARTUP_TIMEOUT_SEC:-1800}"
PORT="${PORT:-18051}"
CONTAINER="gemma4-agent-replay"

mkdir -p "${RESULTS_DIR}" "${LOGS_DIR}"
python3 "${WORKSPACE_DIR}/generate_agent_trace.py"
python3 "${WORKSPACE_DIR}/convert_to_sharegpt.py"

cleanup() {
  docker logs "${CONTAINER}" >"${LOGS_DIR}/${CURRENT_VARIANT:-unknown}.server.log" 2>&1 || true
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

wait_for_server() {
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SEC))
  until curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; do
    if (( SECONDS >= deadline )); then
      echo "ERROR: server startup timed out for ${CURRENT_VARIANT}" | tee -a "${LOGS_DIR}/${CURRENT_VARIANT}.run.log"
      return 1
    fi
    if ! docker ps --filter "name=${CONTAINER}" --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
      echo "ERROR: server exited for ${CURRENT_VARIANT}" | tee -a "${LOGS_DIR}/${CURRENT_VARIANT}.run.log"
      docker logs "${CONTAINER}" >"${LOGS_DIR}/${CURRENT_VARIANT}.server.log" 2>&1 || true
      return 1
    fi
    sleep 10
  done
}

run_variant() {
  local variant="$1"
  local target_model
  local spec_tokens
  local served_model="agent_${variant}"
  local spec_config
  local -a speculative_args=()

  if [[ "${variant}" == bf16_* ]]; then
    target_model="google/gemma-4-26B-A4B-it"
  else
    target_model="RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic"
  fi

  if [[ "${variant}" == *_off ]]; then
    spec_tokens=0
  else
    spec_tokens="${variant##*_s}"
    spec_config=$(printf '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":%s}' "${spec_tokens}")
    speculative_args=(--speculative-config "${spec_config}")
  fi

  CURRENT_VARIANT="${variant}"
  export CURRENT_VARIANT
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true

  echo "starting ${variant}: model=${target_model}, speculative_tokens=${spec_tokens}" | tee "${LOGS_DIR}/${variant}.run.log"
  docker run -d --gpus all \
    --name "${CONTAINER}" \
    --ipc=host \
    --network host \
    -v "${HF_HOME_HOST}:/root/.cache/huggingface" \
    "${IMAGE}" \
    "${target_model}" \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --served-model-name "${served_model}" \
    --trust-remote-code \
    --language-model-only \
    --dtype auto \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    --safetensors-load-strategy prefetch \
    "${speculative_args[@]}" \
    >"${LOGS_DIR}/${variant}.container-id"

  wait_for_server

  IFS=',' read -ra concurrency_values <<<"${CONCURRENCIES}"
  for concurrency in "${concurrency_values[@]}"; do
    local label="${variant}_agent_c${concurrency}"
    local result_file="${label}.benchmark.json"
    echo "benchmark ${label}" | tee -a "${LOGS_DIR}/${variant}.run.log"

    docker run --rm --gpus all --network host \
      -v "${WORKSPACE_DIR}:/workspace:ro" \
      -v "${RESULTS_DIR}:/results" \
      --entrypoint vllm \
      "${IMAGE}" bench serve \
      --backend openai \
      --base-url "http://127.0.0.1:${PORT}" \
      --endpoint /v1/completions \
      --model "${served_model}" \
      --tokenizer "${target_model}" \
      --dataset-name sharegpt \
      --dataset-path /workspace/agent_trace_sharegpt.json \
      --sharegpt-output-len 512 \
      --num-prompts "${NUM_PROMPTS}" \
      --num-warmups "${NUM_WARMUPS}" \
      --max-concurrency "${concurrency}" \
      --request-rate inf \
      --temperature 0 \
      --disable-shuffle \
      --save-detailed \
      --save-result \
      --result-dir /results \
      --result-filename "${result_file}" \
      --label "${label}" \
      >"${LOGS_DIR}/${label}.bench.log" 2>&1

    curl -fsS "http://127.0.0.1:${PORT}/metrics" >"${RESULTS_DIR}/${label}.metrics.txt" || true
  done

  docker logs "${CONTAINER}" >"${LOGS_DIR}/${variant}.server.log" 2>&1 || true
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
}

IFS=',' read -ra variant_values <<<"${VARIANTS}"
for variant in "${variant_values[@]}"; do
  run_variant "${variant}"
done

CURRENT_VARIANT="completed"
echo "Agent trace replay completed."
