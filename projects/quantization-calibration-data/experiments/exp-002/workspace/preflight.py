import importlib.util
import json
import platform
import subprocess
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = EXP_DIR / "logs"
RESULTS_DIR = EXP_DIR / "results"
LOG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODULES = [
    "torch",
    "transformers",
    "datasets",
    "llmcompressor",
    "compressed_tensors",
    "vllm",
]


def run(cmd):
    try:
        proc = subprocess.run(cmd, check=False, text=True, capture_output=True)
        return {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    except Exception as exc:
        return {"returncode": None, "stdout": "", "stderr": f"ERROR: {exc}"}


def main():
    modules = {name: importlib.util.find_spec(name) is not None for name in MODULES}
    nvidia_smi = run(["nvidia-smi"])
    local_qwen4b = Path("/home/hiroki/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507").exists()
    snapshot_files = []
    snap_root = Path("/home/hiroki/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots")
    if snap_root.exists():
        snapshot_files = sorted(str(p) for p in snap_root.rglob("*") if p.is_file())[:200]
    report = {
        "experiment_id": "exp-002",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "modules": modules,
        "nvidia_smi": nvidia_smi,
        "local_qwen4b_cache_exists": local_qwen4b,
        "qwen4b_snapshot_file_count_sampled": len(snapshot_files),
        "qwen4b_snapshot_files_sample": snapshot_files,
    }
    (LOG_DIR / "preflight.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
