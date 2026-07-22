# GPU Preflight Log

Date: 2026-07-16 UTC

## Verdict

BLOCKED before model server startup.

## Checks

- Host nvidia-smi failed because the NVIDIA driver was not loaded.
- The vLLM v0.24.0 container with --gpus all failed with nvml error: driver not loaded.
- /dev/nvidia0, /dev/nvidiactl, and /dev/nvidia-uvm are absent.
- lsmod contains no NVIDIA module; modinfo nvidia reports Module nvidia not found.
- Running kernel: 6.17.0-1008-nvidia on aarch64.
- The NVIDIA VGA PCI device is visible.
- Installed NVIDIA open modules are for kernels 6.11 and 6.14, not the running 6.17.0-1008 kernel.

## Consequence

No model server was started and no benchmark request was sent. This is an infrastructure failure, not a model or workload result.
