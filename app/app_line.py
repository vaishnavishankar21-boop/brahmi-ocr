import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import cv2
import numpy as np
import streamlit as st
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import transforms

from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="LipiLens", page_icon="🪨", layout="wide")
st.title("LipiLens: read a line")
st.write("Upload a photo of ONE line of Brahmi letters. LipiLens finds each letter and reads it.")


@st.cache_resource
def load_model():
    ck = torch.load("models/finetuned.pt", map_location="cpu")
    classes = ck["classes"]
    model = nn.Sequential(
        nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(64 * 8 * 8, 128), nn.ReLU(),
        nn.Linear(128, len(classes)),
    )
    model.load_state_dict(ck["model"])
    model.eval()
    return model, classes


tf = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])


def prepare(img):
    img = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    w, h = img.size
    s = int(max(w, h) * 1.2)
    bg = int(np.median(np.array(img)))
    out = Image.new("L", (s, s), bg)
    out.paste(img, ((s - w) // 2, (s - h) // 2))
    return out


model, classes = load_model()

st.sidebar.header("Settings")
c = st.sidebar.slider("Sensitivity (higher finds fewer marks)", 2, 25, 8)
k = st.sidebar.slider("Join strokes (bigger joins more)", 1, 9, 3)
hmin = st.sidebar.slider("Smallest letter height (% of photo)", 5, 60, 20)
hmax = st.sidebar.slider("Biggest letter height (% of photo)", 40, 100, 95)
show_bw = st.sidebar.checkbox("Show the black-and-white view")

file = st.file_uploader("Photo of one line", type=["jpg", "jpeg", "png"])

if file:
    img = Image.open(file).convert("RGB")
    gray = np.array(img.convert("L"))
    H, W = gray.shape

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    bw = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, c)
    if k > 1:
        bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if hmin * H / 100 <= h <= hmax * H / 100 and 0.2 * h <= w <= 1.6 * h:
            boxes.append((x, y, w, h))
    boxes.sort(key=lambda b: b[0])

    shown = np.array(img).copy()
    results = []
    for n, (x, y, w, h) in enumerate(boxes, 1):
        pad = int(0.1 * max(w, h))
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(W, x + w + pad), min(H, y + h + pad)
        crop = Image.fromarray(gray[y0:y1, x0:x1])
        with torch.no_grad():
            probs = torch.softmax(model(tf(prepare(crop)).unsqueeze(0))[0], dim=0)
        p, i = probs.max(0)
        name = letter_name(classes[i.item()])
        results.append((n, name, p.item()))
        cv2.rectangle(shown, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(shown, str(n), (x, max(20, y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

    st.image(shown, caption=f"{len(boxes)} letters found", use_container_width=True)
    if show_bw:
        st.image(bw, caption="Black-and-white view", use_container_width=True)

    if results:
        st.subheader("Reading (left to right)")
        st.markdown("## " + " ".join(to_devanagari(r[1]) for r in results))
        st.write(" ".join(to_latin(r[1]) for r in results))
        st.write("Letter by letter:")
        for n, name, p in results:
            st.write(f"{n}. **{to_devanagari(name)}** ({to_latin(name)}) - {p * 100:.0f}% sure")
    else:
        st.write("No letters found. Try changing the settings on the left.")