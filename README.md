# TFContainerDockerCodebase

This workflow pulls a TensorFlow-based Docker image (wincheahken/tfcontainer) from Docker Hub—designed for machine learning model training with Python and essential libraries—and pushes it to GitHub Container Registry (GHCR) for centralized, GitHub-native access and reuse.

## Features

- **Ubuntu Base OS**  
  Robust and widely-used operating system for development and deployment.

- **Python 3.10**  
  Modern Python environment for ML and data science projects.

- **TensorFlow (CPU-only)**  
  Optimized for general-purpose CPUs, suitable for experimentation and development.

- **Popular ML Libraries**  
  - NumPy
  - Pandas
  - Matplotlib
  - Scikit-learn
  
- **Additional Dependencies**  
  Includes essential packages for training and experimentation.

## Getting the Image

The container image is published on **GitHub Container Registry (GHCR)** for easy access.

**Pull the latest image:**
```sh
docker pull ghcr.io/kwincheah/tfcontainer:latest
```

**Example usage:**
```sh
docker run -it --rm ghcr.io/<namespace>/tfcontainer:latest python
```

## Publishing Workflow

A GitHub Actions workflow is included to automate pushing the Docker image from Docker Hub to GHCR. The process:

1. **Authenticate to GHCR** using a GitHub Personal Access Token (PAT).
2. **Pull the image** from Docker Hub (`wincheahken/tfcontainer:latest`).
3. **Tag the image** for GHCR (`ghcr.io/<namespace>/tfcontainer:latest`).
4. **Push the image** to GHCR.

> **Note:** To use this workflow, set up a `GHCR_PAT` secret with appropriate permissions in your repository settings.

## License

[MIT](LICENSE) (or specify another license if different)

---

**Author:** [kwincheah](https://github.com/kwincheah)
