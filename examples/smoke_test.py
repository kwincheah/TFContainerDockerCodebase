"""Smoke test for the image: runs on GPU if one is available, otherwise CPU.

1. Trains a tiny PyTorch CNN on synthetic OpenCV images (square vs. circle).
2. Builds a YOLO11n model from its config (no download) and runs a forward pass.

Usage: docker run --rm --gpus all -v "$PWD/examples:/examples" ghcr.io/kwincheah/runpod-cv-env python /examples/smoke_test.py
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import transformers
import ultralytics
from ultralytics import YOLO

device = "cuda" if torch.cuda.is_available() else "cpu"
gpu = torch.cuda.get_device_name(0) if device == "cuda" else "none"
print(f"PyTorch {torch.__version__} | CUDA {torch.version.cuda} | device={device} ({gpu})")
print(f"OpenCV {cv2.__version__} | Ultralytics {ultralytics.__version__} | Transformers {transformers.__version__}")

# 1) Tiny CNN on synthetic images
SIZE, N = 32, 800
rng = np.random.default_rng(0)


def make_image(label: int) -> np.ndarray:
    img = np.zeros((SIZE, SIZE), np.uint8)
    cx, cy = (int(v) for v in rng.integers(10, SIZE - 10, 2))
    r = int(rng.integers(5, 9))
    if label == 0:
        cv2.rectangle(img, (cx - r, cy - r), (cx + r, cy + r), 255, -1)
    else:
        cv2.circle(img, (cx, cy), r, 255, -1)
    return np.clip(img + rng.normal(0, 20, img.shape), 0, 255).astype(np.float32) / 255.0


y = rng.integers(0, 2, N)
X = torch.tensor(np.stack([make_image(int(v)) for v in y]))[:, None].to(device)
Y = torch.tensor(y, dtype=torch.float32).to(device)
split = int(N * 0.75)

torch.manual_seed(0)
model = nn.Sequential(
    nn.Conv2d(1, 16, 3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(16, 32, 3), nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten(),
    nn.Linear(32, 1),
).to(device)
opt = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCEWithLogitsLoss()
for _ in range(40):
    for i in range(0, split, 32):
        opt.zero_grad()
        loss_fn(model(X[i:i + 32]).squeeze(1), Y[i:i + 32]).backward()
        opt.step()
with torch.no_grad():
    acc = ((model(X[split:]).squeeze(1) > 0).float() == Y[split:]).float().mean().item()
print(f"CNN test accuracy: {acc:.3f}")
assert acc > 0.85, "CNN failed to learn"

# 2) YOLO11n forward pass (architecture from yaml, random weights, no network needed)
yolo = YOLO("yolo11n.yaml")
results = yolo.predict(np.zeros((640, 640, 3), np.uint8), device=device, verbose=False)
print(f"YOLO11n forward pass OK ({sum(p.numel() for p in yolo.model.parameters()) / 1e6:.1f}M params)")
print("OK")
