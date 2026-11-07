import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import streamlit as st
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import transforms

from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="LipiLens", page_icon="🪨")
st.title("LipiLens")
st.write("Upload a photo of one Brahmi letter carved in stone. LipiLens shows its best guesses.")


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
file = st.file_uploader("Letter image", type=["jpg", "jpeg", "png"])

if file:
    img = Image.open(file)
    st.image(img, caption="Your image", width=200)
    x = tf(prepare(img)).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(x)[0], dim=0)
    top = probs.topk(3)
    st.subheader("Best guesses")
    for p, i in zip(top.values.tolist(), top.indices.tolist()):
        name = letter_name(classes[i])
        st.write(f"**{to_devanagari(name)}**  ({to_latin(name)}) - {p * 100:.0f}%")