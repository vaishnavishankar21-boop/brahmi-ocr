import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

random.seed(1)
np.random.seed(1)

FONT_PATH = "data/fonts/NotoSansBrahmi-Regular.ttf"
OUT = "data/synthetic/drawn"
N = 60
SIZE = 256

#font = ImageFont.truetype(FONT_PATH, 180)
codes = list(range(0x11005, 0x11035))


def glyph(code):
       img = Image.open(f"data/synthetic/clean/{code:X}.png").convert("L")
       return cv2.resize(np.array(img), (SIZE, SIZE), interpolation=cv2.INTER_CUBIC)


def wobble(a, strength):
    h, w = a.shape
    dx = cv2.GaussianBlur(np.random.randn(h, w).astype(np.float32), (0, 0), 25)
    dy = cv2.GaussianBlur(np.random.randn(h, w).astype(np.float32), (0, 0), 25)
    dx = dx / (dx.std() + 1e-6) * strength
    dy = dy / (dy.std() + 1e-6) * strength
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    return cv2.remap(a, (xs + dx).astype(np.float32), (ys + dy).astype(np.float32),
                     cv2.INTER_LINEAR, borderValue=255)


def draw_like(base):
    a = wobble(base, random.uniform(3, 9))
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), random.uniform(-12, 12), random.uniform(0.85, 1.1))
    a = cv2.warpAffine(a, M, (w, h), borderValue=255)
    ink = 255 - a
    k = np.ones((3, 3), np.uint8)
    n = random.randint(-2, 3)
    if n > 0:
        ink = cv2.dilate(ink, k, iterations=n)
    elif n < 0:
        ink = cv2.erode(ink, k, iterations=-n)
    ink = cv2.GaussianBlur(ink, (0, 0), random.uniform(1.0, 2.5))
    a = 255 - ((ink > 90).astype(np.uint8) * 255)
    ys, xs = np.where(a < 128)
    if len(xs) < 30:
        return None
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    pad = int(0.15 * max(x1 - x0, y1 - y0)) + 4
    crop = a[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
    ch, cw = crop.shape
    s = max(ch, cw)
    out = np.full((s, s), 255, np.uint8)
    out[(s - ch) // 2:(s - ch) // 2 + ch, (s - cw) // 2:(s - cw) // 2 + cw] = crop
    return out


total = 0
for code in codes:
    base = glyph(code)
    folder = f"{OUT}/{code:X}"
    os.makedirs(folder, exist_ok=True)
    saved = 0
    tries = 0
    while saved < N and tries < N * 5:
        tries += 1
        img = draw_like(base)
        if img is None:
            continue
        cv2.imwrite(f"{folder}/{saved}.png", img)
        saved += 1
        total += 1
print("saved", total, "images")

rows = []
for code in codes[::8]:
    row = []
    for i in range(8):
        im = cv2.imread(f"{OUT}/{code:X}/{i}.png", 0)
        row.append(cv2.resize(im, (64, 64)))
    rows.append(np.hstack(row))
cv2.imwrite("data/synthetic/drawn_preview.png", np.vstack(rows))
print("saved preview")