import os, glob, random
import cv2
import numpy as np

SRC = "data/synthetic/clean"
OUT = "data/synthetic/augmented"
N = 100  # variations per letter
random.seed(42)
np.random.seed(42)

def augment(img):
    h, w = img.shape
    # tilt, zoom, shift
    M = cv2.getRotationMatrix2D((w / 2, h / 2), random.uniform(-10, 10), random.uniform(0.8, 1.1))
    M[:, 2] += (random.uniform(-6, 6), random.uniform(-6, 6))
    img = cv2.warpAffine(img, M, (w, h), borderValue=255)
    # thicker or thinner strokes
    k = np.ones((2, 2), np.uint8)
    r = random.random()
    if r < 0.3:
        img = cv2.erode(img, k)   # thicker ink
    elif r < 0.6:
        img = cv2.dilate(img, k)  # thinner ink
    # gray stone colors
    ink = (255 - img).astype(np.float32) / 255
    bg = random.uniform(130, 220)
    fg = random.uniform(30, 110)
    out = bg * (1 - ink) + fg * ink
    # stone texture: bumpy + grainy
    low = cv2.GaussianBlur(np.random.randn(h, w).astype(np.float32), (0, 0), 6)
    low = low / (low.std() + 1e-6) * random.uniform(5, 15)
    fine = np.random.randn(h, w).astype(np.float32) * random.uniform(5, 20)
    out = out + low + fine
    # small chips
    for _ in range(random.randint(0, 6)):
        cv2.circle(out, (random.randint(0, w - 1), random.randint(0, h - 1)),
                   random.randint(1, 3), bg, -1)
    # blur
    b = random.choice([1, 3, 3, 5])
    if b > 1:
        out = cv2.GaussianBlur(out, (b, b), 0)
    return np.clip(out, 0, 255).astype(np.uint8)

total = 0
files = sorted(glob.glob(f"{SRC}/*.png"))
for f in files:
    code = os.path.splitext(os.path.basename(f))[0]
    img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    os.makedirs(f"{OUT}/{code}", exist_ok=True)
    for i in range(N):
        cv2.imwrite(f"{OUT}/{code}/{i}.png", augment(img))
        total += 1
print("saved", total, "images")

# preview: 6 letters x 8 samples
rows = []
for f in files[:6]:
    code = os.path.splitext(os.path.basename(f))[0]
    row = [cv2.imread(f"{OUT}/{code}/{i}.png", 0) for i in range(8)]
    rows.append(np.hstack(row))
cv2.imwrite("data/synthetic/augmented_preview.png", np.vstack(rows))
print("saved preview")