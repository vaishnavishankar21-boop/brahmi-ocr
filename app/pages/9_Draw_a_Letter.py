import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import streamlit as st
import torch
import torch.nn as nn
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from torchvision import transforms

from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="Draw a letter", page_icon="✏️", layout="centered")
st.title("Draw a letter")
st.write("Draw one Brahmi letter with your mouse or finger. LipiLens tries to read it.")


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


def from_canvas(arr):
    rgba = Image.fromarray(arr.astype("uint8"), "RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(white, rgba).convert("L")
    a = np.array(gray)
    ys, xs = np.where(a < 128)
    if len(xs) < 30:
        return None
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    pad = int(0.15 * max(x1 - x0, y1 - y0)) + 4
    crop = gray.crop((max(0, x0 - pad), max(0, y0 - pad),
                      min(gray.width, x1 + pad), min(gray.height, y1 + pad)))
    w, h = crop.size
    s = max(w, h)
    out = Image.new("L", (s, s), 255)
    out.paste(crop, ((s - w) // 2, (s - h) // 2))
    return out


model, classes = load_model()
st.session_state.setdefault("canvas_n", 0)

left, right = st.columns([1, 1])
with left:
    canvas = st_canvas(
        stroke_width=6,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=300,
        drawing_mode="freedraw",
        update_streamlit=True,
        key=f"canvas_{st.session_state.canvas_n}",
        return_image_data=True,
    )
    if st.button("Clear"):
        st.session_state.canvas_n += 1
        st.rerun()

with right:
    img = None
    if canvas is not None and canvas.image_data is not None:
        img = from_canvas(canvas.image_data)
    if img is None:
        st.info("Draw a letter on the canvas.")
    else:
        st.image(img, caption="What the model sees", width=110)
        x = tf(img).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(x)[0], dim=0)
        top = probs.topk(3)
        st.markdown("#### Best guesses")
        for p, i in zip(top.values.tolist(), top.indices.tolist()):
            n = letter_name(classes[i])
            st.write(f"**{to_devanagari(n)}**  {to_latin(n)}  ({p * 100:.0f}%)")

st.caption("LipiLens learned from stone photos, so drawings may be misread. Draw big, "
           "clear, simple strokes in the middle of the box.")
