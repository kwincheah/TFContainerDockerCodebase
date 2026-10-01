# GPU-ready computer vision environment for RunPod (works on any NVIDIA Docker host).
# PyTorch + CUDA come from the official image; we add CV/VLM libraries, JupyterLab and SSH.
FROM pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    MPLBACKEND=Agg \
    # Keep model downloads on the /workspace network volume so new pods don't re-download them
    HF_HOME=/workspace/.cache/huggingface \
    TORCH_HOME=/workspace/.cache/torch \
    YOLO_CONFIG_DIR=/workspace/.config/Ultralytics

# libgl/glib for OpenCV, openssh for RunPod's SSH, git/wget/tmux for day-to-day work
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 openssh-server git wget curl tmux nano ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd /workspace

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

WORKDIR /workspace
EXPOSE 8888 22
CMD ["/start.sh"]
