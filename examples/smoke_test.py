"""Smoke test: train a tiny CNN on synthetic images (square vs. circle) and check it learns.

Exercises TensorFlow, NumPy, OpenCV and scikit-learn in one run (~10 s on CPU).
Usage: docker run --rm -v "$PWD/examples:/workspace" ghcr.io/kwincheah/tfcontainer python smoke_test.py
"""

import cv2
import numpy as np
import sklearn
import tensorflow as tf
from sklearn.model_selection import train_test_split

SIZE, N = 32, 800
rng = np.random.default_rng(0)


def make_image(label: int) -> np.ndarray:
    img = np.zeros((SIZE, SIZE), np.uint8)
    c = rng.integers(10, SIZE - 10, 2)
    r = int(rng.integers(5, 9))
    if label == 0:
        cv2.rectangle(img, (int(c[0] - r), int(c[1] - r)), (int(c[0] + r), int(c[1] + r)), 255, -1)
    else:
        cv2.circle(img, (int(c[0]), int(c[1])), r, 255, -1)
    noise = rng.normal(0, 20, img.shape)
    return np.clip(img + noise, 0, 255).astype(np.float32) / 255.0


y = rng.integers(0, 2, N)
X = np.stack([make_image(int(label)) for label in y])[..., None]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

tf.random.set_seed(0)
model = tf.keras.Sequential([
    tf.keras.layers.Input((SIZE, SIZE, 1)),
    tf.keras.layers.Conv2D(16, 3, activation="relu"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(32, 3, activation="relu"),
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X_train, y_train, epochs=15, batch_size=32, verbose=0)
_, acc = model.evaluate(X_test, y_test, verbose=0)

print(f"TensorFlow {tf.__version__} | NumPy {np.__version__} | OpenCV {cv2.__version__} | scikit-learn {sklearn.__version__}")
print(f"Test accuracy: {acc:.3f}")
assert acc > 0.85, "model failed to learn"
print("OK")
