#!/bin/bash
# Container entrypoint: SSH (if RunPod passes PUBLIC_KEY) + JupyterLab, then stay alive.
set -e

# SSH sessions start with a clean environment; save the container's env (CUDA paths, HF_HOME,
# RunPod variables, ...) so every login shell and `ssh pod <command>` sees the same settings.
export -p | grep -vE '^declare -x (HOME|PWD|OLDPWD|SHLVL|HOSTNAME|TERM|_)=' > /etc/profile.d/container_env.sh
grep -qs container_env.sh ~/.bashrc || sed -i '1i source /etc/profile.d/container_env.sh' ~/.bashrc

if [ -n "$PUBLIC_KEY" ]; then
    mkdir -p ~/.ssh && chmod 700 ~/.ssh
    echo "$PUBLIC_KEY" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
    ssh-keygen -A >/dev/null
    /usr/sbin/sshd
    echo "[start] SSH server started"
fi

if [ "${START_JUPYTER:-1}" = "1" ]; then
    # Never run Jupyter without auth: use JUPYTER_PASSWORD, or generate a token and print it.
    TOKEN="${JUPYTER_PASSWORD:-$(python -c 'import secrets; print(secrets.token_hex(16))')}"
    [ -z "$JUPYTER_PASSWORD" ] && echo "[start] Jupyter token: $TOKEN"
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
        --ServerApp.token="$TOKEN" --ServerApp.root_dir=/workspace \
        --ServerApp.allow_origin='*' > /var/log/jupyter.log 2>&1 &
    echo "[start] JupyterLab on port 8888 (log: /var/log/jupyter.log)"
fi

python -c "import torch; print('[start] PyTorch', torch.__version__, '| CUDA available:', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"

exec sleep infinity
