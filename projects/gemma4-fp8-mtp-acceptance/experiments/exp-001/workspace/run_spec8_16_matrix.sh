#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${EXP_DIR}/results"
LOGS_DIR="${EXP_DIR}/logs"
IMAGE="${IMAGE:-vllm/vllm-openai:v0.24.0}"
HF_HOME_HOST="${HF_HOME_HOST:-/home/hiroki/.cache/huggingface}"
NUM_PROMPTS="${NUM_PROMPTS:-16}"
NUM_WARMUPS="${NUM_WARMUPS:-2}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.78}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
STARTUP_TIMEOUT_SEC="${STARTUP_TIMEOUT_SEC:-1800}"
PORT="${PORT:-18061}"
CONTAINER="gemma4-random-spec-high"
VARIANTS="${VARIANTS:-bf16_s8,bf16_s16,fp8_s8,fp8_s16}"

# exp-001 で既に実測した全ユニークな workload 条件を再利用する。
WORKLOADS=(
  "128:128:1"
  "128:512:1"
  "128:512:4"
  "1024:1024:1"
  "1024:1024:2"
  "1024:1024:4"
  "1024:1024:8"
  "1024:2048:1"
  "2048:1024:1"
  "2048:1536:1"
)

mkdir -p "${RESULTS_DIR}" "${LOGS_DIR}"

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
  local spec_tokens="${variant##*_s}"
  local served_model="random_${variant}"
  local spec_config

  if [[ "${variant}" == bf16_* ]]; then
    target_model="google/gemma-4-26B-A4B-it"
  else
    target_model="RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic"
  fi

  spec_config=$(printf '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":%s}' "${spec_tokens}")
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
    --speculative-config "${spec_config}" \
    >"${LOGS_DIR}/${variant}.container-id"

  wait_for_server

  for workload in "${WORKLOADS[@]}"; do
    IFS=':' read -r input_len output_len concurrency <<<"${workload}"
    local label="${variant}_in${input_len}_out${output_len}_c${concurrency}"
    echo "benchmark ${label}" | tee -a "${LOGS_DIR}/${variant}.run.log"
    docker run --rm --gpus all --network host \
      -v "${RESULTS_DIR}:/results" \
      --entrypoint vllm \
      "${IMAGE}" bench serve \
      --backend openai \
      --base-url "http://127.0.0.1:${PORT}" \
      --endpoint /v1/completions \
      --model "${served_model}" \
      --tokenizer "${target_model}" \
      --dataset-name random \
      --input-len "${input_len}" \
      --output-len "${output_len}" \
      --num-prompts "${NUM_PROMPTS}" \
      --num-warmups "${NUM_WARMUPS}" \
      --max-concurrency "${concurrency}" \
      --request-rate inf \
      --ignore-eos \
      --temperature 0 \
      --save-result \
      --result-dir /results \
      --result-filename "${label}.benchmark.json" \
      --label "${label}" \
      >"${LOGS_DIR}/${label}.bench.log" 2>&1
  done

  docker logs "${CONTAINER}" >"${LOGS_DIR}/${variant}.server.log" 2>&1 || true
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
}

IFS=',' read -ra variant_values <<<"${VARIANTS}"
for variant in "${variant_values[@]}"; do
  run_variant "${variant}"
done

CURRENT_VARIANT="completed"
echo "High speculative-token random matrix completed."
