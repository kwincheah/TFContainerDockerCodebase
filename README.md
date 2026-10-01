# TensorFlow ML Container

[![build](https://img.shields.io/github/actions/workflow/status/kwincheah/TFContainerDockerCodebase/build.yml?branch=main&style=flat-square&label=build)](https://github.com/kwincheah/TFContainerDockerCodebase/actions/workflows/build.yml)
![Python](https://img.shields.io/badge/python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21_(CPU)-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![Docker](https://img.shields.io/badge/docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

A reproducible **Docker environment for machine learning and computer vision** on CPU: TensorFlow, OpenCV and the usual data-science stack, with pinned versions.
Every change is built and **smoke-tested in CI** (a small CNN is trained inside the image) before the image is published to GitHub Container Registry.

## What's inside

| Component | Version |
|---|---|
| Base OS | Ubuntu 22.04 |
| Python | 3.10 (virtual environment at `/opt/venv`) |
| TensorFlow (CPU) / Keras | 2.21.0 / 3.12 |
| OpenCV (headless) | 5.0.0 |
| NumPy · Pandas | 2.2.6 · 2.3.3 |
| scikit-learn | 1.7.2 |
| Matplotlib · Pillow | 3.10.9 · 12.3.0 |

Also included:
- **A non-root user** (`ml`, UID 1000), with `/workspace` as the working directory
- **Headless defaults**: `MPLBACKEND=Agg` and quiet TensorFlow logging

## Quick start

```sh
# Pull the image
docker pull ghcr.io/kwincheah/tfcontainer:latest

# Interactive Python
docker run -it --rm ghcr.io/kwincheah/tfcontainer:latest

# Run a script from your project folder
docker run --rm -v "$PWD:/workspace" ghcr.io/kwincheah/tfcontainer:latest python train.py
```

Check the environment with the included smoke test:

```sh
docker run --rm -v "$PWD/examples:/workspace" ghcr.io/kwincheah/tfcontainer:latest python smoke_test.py
# TensorFlow 2.21.0 | NumPy 2.2.6 | OpenCV 5.0.0 | scikit-learn 1.7.2
# Test accuracy: 1.000
# OK
```

The smoke test draws synthetic **square vs. circle** images with OpenCV and trains a small CNN on them. It finishes in about 10 seconds on a CPU.

## Build locally

```sh
git clone https://github.com/kwincheah/TFContainerDockerCodebase.git
cd TFContainerDockerCodebase
docker build -t tfcontainer .
```

To add packages, edit `requirements.txt` and rebuild.

## CI / publishing

The [`build`](.github/workflows/build.yml) workflow:

| Trigger | Build + smoke test | Push to GHCR |
|---|:---:|:---:|
| Push to `main`, pull request | ✅ | — |
| **Run workflow** (manual, `publish` ticked) | ✅ | ✅ `latest`, `sha-<commit>` |
| GitHub release `vX.Y.Z` | ✅ | ✅ `latest`, `X.Y.Z`, `sha-<commit>` |

Publishing uses the built-in `GITHUB_TOKEN`, so no personal access token or extra secrets are needed. Docker layers are cached between runs.

## Project structure

```text
.
├── Dockerfile              # Ubuntu 22.04 + Python 3.10 venv + pinned ML stack, non-root user
├── requirements.txt        # Pinned package versions
├── examples/
│   └── smoke_test.py       # Synthetic-image CNN training check
└── .github/workflows/
    └── build.yml           # Build → smoke test → (optionally) push to GHCR
```

## License

[MIT](LICENSE) © Cheah Ken Win
