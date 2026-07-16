#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${EXP_DIR}/results"
LOGS_DIR="${EXP_DIR}/logs"
IMAGE="${IMAGE:-vllm/vllm-openai:v0.24.0}"
HF_HOME_HOST="${HF_HOME_HOST:-/home/hiroki/.cache/huggingface}"
NUM_PROMPTS="${NUM_PROMPTS:-10}"
NUM_WARMUPS="${NUM_WARMUPS:-3}"
INPUT_LEN="${INPUT_LEN:-128}"
OUTPUT_LEN="${OUTPUT_LEN:-128}"
MAX_CONCURRENCY="${MAX_CONCURRENCY:-1}"
REQUEST_RATE="${REQUEST_RATE:-inf}"
NUM_SPEC_TOKENS="${NUM_SPEC_TOKENS:-4}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
STARTUP_TIMEOUT_SEC="${STARTUP_TIMEOUT_SEC:-1800}"

mkdir -p "${RESULTS_DIR}" "${LOGS_DIR}"

run_variant() {
  local variant="$1"
  local target_model="$2"
  local port="$3"
  local container="gemma4-mtp-${variant}"
  local server_log="${LOGS_DIR}/${variant}.server.log"
  local bench_log="${LOGS_DIR}/${variant}.bench.log"
  local metrics_file="${RESULTS_DIR}/${variant}.metrics.txt"
  local result_file="${variant}.benchmark.json"
  local spec_config

  spec_config=$(printf '{"method":"mtp","model":"google/gemma-4-26B-A4B-it-assistant","num_speculative_tokens":%s}' "${NUM_SPEC_TOKENS}")

  docker rm -f "${container}" >/dev/null 2>&1 || true

  docker run -d --gpus all \
    --name "${container}" \
    --ipc=host \
    --network host \
    -v "${HF_HOME_HOST}:/root/.cache/huggingface" \
    "${IMAGE}" \
    "${target_model}" \
    --host 0.0.0.0 \
    --port "${port}" \
    --served-model-name "${variant}" \
    --trust-remote-code \
    --language-model-only \
    --dtype auto \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    --safetensors-load-strategy prefetch \
    --speculative-config "${spec_config}" \
    >"${server_log}.container-id"

  cleanup() {
    docker logs "${container}" >"${server_log}" 2>&1 || true
    docker rm -f "${container}" >/dev/null 2>&1 || true
  }
  trap cleanup RETURN

  local deadline=$((SECONDS + STARTUP_TIMEOUT_SEC))
  until curl -fsS "http://127.0.0.1:${port}/v1/models" >/dev/null 2>&1; do
    if (( SECONDS >= deadline )); then
      echo "ERROR: server startup timed out for ${variant}" | tee -a "${bench_log}"
      return 1
    fi
    if ! docker ps --filter "name=${container}" --format '{{.Names}}' | grep -q "^${container}$"; then
      echo "ERROR: server container exited for ${variant}" | tee -a "${bench_log}"
      docker logs "${container}" >"${server_log}" 2>&1 || true
      return 1
    fi
    sleep 10
  done

  curl -fsS "http://127.0.0.1:${port}/metrics" >"${metrics_file}.before" || true

  docker run --rm --gpus all --network host \
    -v "${RESULTS_DIR}:/results" \
    --entrypoint vllm \
    "${IMAGE}" bench serve \
    --backend openai \
    --base-url "http://127.0.0.1:${port}" \
    --endpoint /v1/completions \
    --model "${variant}" \
    --tokenizer "${target_model}" \
    --dataset-name random \
    --input-len "${INPUT_LEN}" \
    --output-len "${OUTPUT_LEN}" \
    --num-prompts "${NUM_PROMPTS}" \
    --num-warmups "${NUM_WARMUPS}" \
    --max-concurrency "${MAX_CONCURRENCY}" \
    --request-rate "${REQUEST_RATE}" \
    --ignore-eos \
    --temperature 0 \
    --save-result \
    --result-dir /results \
    --result-filename "${result_file}" \
    --label "${variant}_in${INPUT_LEN}_out${OUTPUT_LEN}" \
    >"${bench_log}" 2>&1

  curl -fsS "http://127.0.0.1:${port}/metrics" >"${metrics_file}.after" || true
}

run_variant "bf16_target_mtp" "google/gemma-4-26B-A4B-it" 18001
run_variant "fp8_dynamic_target_mtp" "RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic" 18002

echo "Baseline runs completed. Raw results are under ${RESULTS_DIR}."
