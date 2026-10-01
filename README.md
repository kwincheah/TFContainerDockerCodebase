# RunPod CV Environment

[![build](https://img.shields.io/github/actions/workflow/status/kwincheah/TFContainerDockerCodebase/build.yml?branch=main&style=flat-square&label=build)](https://github.com/kwincheah/TFContainerDockerCodebase/actions/workflows/build.yml)
![PyTorch](https://img.shields.io/badge/PyTorch-2.14_·_CUDA_12.6-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLO-111F68?style=flat-square)
![RunPod](https://img.shields.io/badge/RunPod-ready-673AB7?style=flat-square)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

A **GPU-ready Docker image for computer vision and vision-language work on [RunPod](https://www.runpod.io)**: PyTorch + CUDA, Ultralytics YOLO, Hugging Face Transformers, OpenCV, JupyterLab and SSH, preinstalled and version-pinned.

**Why:** every new pod used to start by reinstalling the same packages and downloading the same weights. With this image, the libraries are baked in, and model and dataset downloads go to the **`/workspace` network volume**, so the next pod starts ready to train.

## What's inside

| Component | Version |
|---|---|
| Base image | `pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime` (Ubuntu 24.04, Python 3.12) |
| PyTorch / torchvision | 2.14.1 / 0.29.1 (CUDA 12.6, cuDNN 9) |
| Ultralytics (YOLO) | 8.4.170 |
| Transformers · Accelerate · huggingface_hub | 5.17.0 · 1.15.0 · 1.16.1 |
| timm · OpenCV | 1.0.30 · 5.0.0 |
| pandas · scikit-learn · Matplotlib · TensorBoard | 3.0.6 · 1.9.1 · 3.11.2 · 2.21.0 |
| JupyterLab | 4.6.4 |
| Tools | OpenSSH server, git, wget, curl, tmux, nano |

The model caches point at the network volume:

| Variable | Path |
|---|---|
| `HF_HOME` | `/workspace/.cache/huggingface` |
| `TORCH_HOME` | `/workspace/.cache/torch` |
| `YOLO_CONFIG_DIR` | `/workspace/.config/Ultralytics` |

## Use it on RunPod

1. **Make the image pullable:** after the first publish, open GitHub → **Packages → runpod-cv-env → Package settings** and set **visibility to Public**. Or keep it private and add GHCR credentials in RunPod.
2. **Create a template:** RunPod → **Templates → New Template**:

   | Field | Value |
   |---|---|
   | Container image | `ghcr.io/kwincheah/runpod-cv-env:latest` |
   | Container disk | 30 GB |
   | Volume mount path | `/workspace` |
   | Expose HTTP ports | `8888` (JupyterLab) |
   | Expose TCP ports | `22` (SSH) |
   | Environment variables | `JUPYTER_PASSWORD` = your password |

3. **Create a Network Volume** (Storage → Network Volumes) in the same region as your GPUs, and attach it when deploying the pod.
4. **Deploy** the pod with the template and volume:
   - **JupyterLab:** **Connect → HTTP 8888**, then log in with your `JUPYTER_PASSWORD`.
   - **SSH:** add your public key in RunPod **Settings → SSH Public Keys**; RunPod passes it to the container as `PUBLIC_KEY`. Then `ssh root@<ip> -p <port>`.

> Keep datasets, checkpoints and `runs/` under `/workspace` too. Everything else in the container is reset when the pod is recreated.

### Startup options

| Variable | Default | Effect |
|---|---|---|
| `PUBLIC_KEY` | set by RunPod | Starts the SSH server and authorises this key |
| `JUPYTER_PASSWORD` | *(random)* | JupyterLab token. If unset, a random token is generated and printed in the pod logs. Jupyter never runs without authentication |
| `START_JUPYTER` | `1` | Set to `0` to skip JupyterLab |

SSH sessions inherit the container's environment (CUDA paths, cache locations, RunPod variables).

## Use it anywhere else

On any machine with an NVIDIA GPU and the NVIDIA Container Toolkit:

```sh
docker run --gpus all -p 8888:8888 -e JUPYTER_PASSWORD=secret \
  -v "$PWD:/workspace" ghcr.io/kwincheah/runpod-cv-env:latest
# then open http://localhost:8888 and log in with the password
```

To check the environment:

```sh
docker run --rm --gpus all -v "$PWD/examples:/examples" \
  ghcr.io/kwincheah/runpod-cv-env:latest python /examples/smoke_test.py
# PyTorch 2.14.1+cu126 | CUDA 12.6 | device=cuda (NVIDIA ...)
# CNN test accuracy: 1.000
# YOLO11n forward pass OK (2.6M params)
# OK
```

The smoke test trains a tiny CNN on synthetic OpenCV images and runs a YOLO11n forward pass. It uses the GPU when one is available and falls back to CPU.

## Build & CI

```sh
docker build -t runpod-cv-env .
```

To add packages, edit `requirements.txt` and rebuild. Don't add `torch` to it; PyTorch comes from the base image.

The [`build`](.github/workflows/build.yml) workflow runs the smoke test on CPU (GitHub runners have no GPU):

| Trigger | Build + smoke test | Push to GHCR |
|---|:---:|:---:|
| Push to `main`, pull request | ✅ | — |
| **Run workflow** (manual, `publish` ticked) | ✅ | ✅ `latest`, `sha-<commit>` |
| GitHub release `vX.Y.Z` | ✅ | ✅ `latest`, `X.Y.Z`, `sha-<commit>` |

Publishing uses the built-in `GITHUB_TOKEN`; no extra secrets are needed.

## Project structure

```text
.
├── Dockerfile              # PyTorch CUDA base + CV/VLM libraries, JupyterLab, SSH
├── start.sh                # Entrypoint: SSH (PUBLIC_KEY), JupyterLab (with auth), GPU check
├── requirements.txt        # Pinned additions on top of the base image
├── examples/
│   └── smoke_test.py       # CNN training + YOLO11n forward pass (GPU or CPU)
└── .github/workflows/
    └── build.yml           # Build → smoke test → (optionally) push to GHCR
```

## License

[MIT](LICENSE) © Cheah Ken Win
