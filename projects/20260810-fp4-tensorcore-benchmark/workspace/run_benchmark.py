import argparse
import json
import subprocess
import time
from pathlib import Path


IMAGE = "vllm/vllm-openai:latest"
HF_CACHE = Path("/home/hiroki/.cache/huggingface")
WORKLOADS = [
    {"name": "latency_short", "input": 128, "output": 128, "concurrency": 1},
    {"name": "decode_heavy", "input": 128, "output": 512, "concurrency": 1},
    {"name": "mixed_throughput", "input": 1024, "output": 256, "concurrency": 8},
    {"name": "prefill_heavy", "input": 4096, "output": 128, "concurrency": 4},
]


def run_command(command: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def docker_logs(container: str) -> str:
    result = run_command(["docker", "logs", container], timeout=60)
    return result.stdout + result.stderr


def stop_container(container: str) -> None:
    run_command(["docker", "stop", container], timeout=60)


def wait_ready(port: int, container: str, timeout_s: int = 900) -> tuple[bool, str]:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        status = run_command(["docker", "inspect", "-f", "{{.State.Status}}", container], timeout=30)
        if status.returncode != 0 or status.stdout.strip() == "exited":
            return False, docker_logs(container)
        health = run_command(["curl", "-fsS", f"http://127.0.0.1:{port}/health"], timeout=30)
        if health.returncode == 0:
            return True, docker_logs(container)
        time.sleep(5)
    return False, docker_logs(container)


def start_server(model_path: Path, model_id: str, dtype: str, port: int, container: str) -> tuple[bool, str]:
    if model_path.is_relative_to(HF_CACHE):
        volume = f"{HF_CACHE}:/hf-cache:ro"
        container_model_path = Path("/hf-cache") / model_path.relative_to(HF_CACHE)
    else:
        volume = f"{model_path}:/model:ro"
        container_model_path = Path("/model")
    command = [
        "docker",
        "run",
        "-d",
        "--rm",
        "--gpus",
        "all",
        "--network",
        "host",
        "--ipc=host",
        "--name",
        container,
        "-v",
        volume,
        IMAGE,
        str(container_model_path),
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--served-model-name",
        model_id,
        "--max-model-len",
        "8192",
        "--gpu-memory-utilization",
        "0.90",
        "--generation-config",
        "vllm",
    ]
    if dtype:
        command.extend(["--dtype", dtype])
    started = run_command(command, timeout=120)
    if started.returncode != 0:
        return False, started.stdout + started.stderr
    return wait_ready(port, container)


def run_workload(
    root: Path,
    model_id: str,
    model_path: Path,
    port: int,
    workload: dict,
    label: str,
    workload_filter: set[str],
) -> tuple[bool, str]:
    result_path = root / "logs" / f"{label}.json"
    container_result_path = Path("/results") / "logs" / f"{label}.json"
    if model_path.is_relative_to(HF_CACHE):
        volume = f"{HF_CACHE}:/hf-cache:ro"
        container_model_path = Path("/hf-cache") / model_path.relative_to(HF_CACHE)
    else:
        volume = f"{model_path}:/model:ro"
        container_model_path = Path("/model")

    command = [
        "docker",
        "run",
        "--rm",
        "--gpus",
        "all",
        "--entrypoint",
        "vllm",
        "--network",
        "host",
        "-v",
        f"{root}:/results",
        "-v",
        volume,
        IMAGE,
        "bench",
        "serve",
        "--backend",
        "openai-chat",
        "--base-url",
        f"http://127.0.0.1:{port}",
        "--endpoint",
        "/v1/chat/completions",
        "--model",
        str(container_model_path),
        "--served-model-name",
        model_id,
        "--tokenizer",
        str(container_model_path),
        "--dataset-name",
        "random",
        "--random-input-len",
        str(workload["input"]),
        "--random-output-len",
        str(workload["output"]),
        "--num-prompts",
        "2",
        "--num-warmups",
        "1",
        "--max-concurrency",
        str(workload["concurrency"]),
        "--request-rate",
        "inf",
        "--save-result",
        "--result-filename",
        str(container_result_path),
    ]
    if workload["name"] not in workload_filter:
        return True, "skipped"
    result = run_command(command, timeout=1800)
    log_path = root / "logs" / f"{label}.bench.log"
    write_text(log_path, result.stdout + result.stderr)
    return result.returncode == 0 and result_path.exists(), result.stdout + result.stderr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--only", nargs="*", help="実行するmodel idを限定する")
    parser.add_argument("--workloads", nargs="*", help="実行するworkload名を限定する")
    args = parser.parse_args()
    root = args.root.resolve()
    workload_filter = set(args.workloads or [workload["name"] for workload in WORKLOADS])
    models = json.loads((root / "inputs" / "models.json").read_text(encoding="utf-8"))
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    selected = set(args.only or [model["id"] for model in models])
    port = 18110
    run_manifest = {"image": IMAGE, "workloads": WORKLOADS, "models": [], "started_at": time.time()}

    for model in models:
        if model["id"] not in selected:
            continue
        model_path = Path(model["path"])
        if not model_path.is_absolute():
            model_path = root / model_path
        entry = {"model": model, "workloads": []}
        if not model_path.exists():
            entry["status"] = "blocked_missing_model"
            run_manifest["models"].append(entry)
            continue

        container = f"fp4-bench-{model['id'].replace('_', '-') }"
        stop_container(container)
        ok, server_log = start_server(model_path, "benchmark-model", model["dtype"], port, container)
        write_text(logs_dir / f"{model['id']}.server.log", server_log)
        if not ok:
            entry["status"] = "server_failed"
            run_manifest["models"].append(entry)
            stop_container(container)
            port += 1
            continue

        entry["status"] = "server_ready"
        for workload in WORKLOADS:
            label = f"{model['id']}__{workload['name']}"
            ok, output = run_workload(root, "benchmark-model", model_path, port, workload, label, workload_filter)
            entry["workloads"].append({"name": workload["name"], "label": label, "status": "completed" if ok else "failed"})
            if not ok:
                write_text(logs_dir / f"{label}.failure.log", output)
        entry["server_log_after"] = str(logs_dir / f"{model['id']}.server.after.log")
        write_text(logs_dir / f"{model['id']}.server.after.log", docker_logs(container))
        stop_container(container)
        run_manifest["models"].append(entry)
        port += 1

    run_manifest["finished_at"] = time.time()
    write_text(logs_dir / "run-manifest.json", json.dumps(run_manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
