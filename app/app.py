import glob
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import streamlit as st
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import transforms

from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="LipiLens", page_icon="🪨", layout="centered")

st.markdown("""
<style>
.hero {text-align:center; padding: 1.2rem 0 0.4rem 0;}
.hero h1 {font-size: 3rem; margin-bottom: 0;}
.hero p {color:#BFB29C; font-size:1.05rem;}
.card {background:#221C17; border:1px solid #3A2F26; border-radius:16px;
       padding:1.2rem; text-align:center;}
.big {font-size:5rem; line-height:1.1; color:#E0A95A;}
.latin {font-size:1.4rem; letter-spacing:0.05em;}
.small {color:#BFB29C; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>LipiLens</h1>'
    '<p>Read ancient Brahmi letters from photos of stone inscriptions</p></div>',
    unsafe_allow_html=True)


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
tab1, tab2, tab3 = st.tabs(["Read a letter", "How it works", "About"])

with tab1:
    file = st.file_uploader("Upload a photo of ONE letter", type=["jpg", "jpeg", "png"])
    if st.button("Try a random example"):
        crops = glob.glob("data/real/crops/*/*.png")
        if crops:
            st.session_state["example"] = random.choice(crops)

    img = None
    if file:
        img = Image.open(file)
    elif "example" in st.session_state:
        img = Image.open(st.session_state["example"])

    if img is None:
        st.info("Upload a letter photo, or press the example button.")
    else:
        x = tf(prepare(img)).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(x)[0], dim=0)
        top = probs.topk(3)
        guesses = list(zip(top.values.tolist(), top.indices.tolist()))
        p1, i1 = guesses[0]
        name1 = letter_name(classes[i1])

        left, right = st.columns([1, 1.4])
        with left:
            st.image(img, caption="Your letter", width=190)
            ref = f"data/synthetic/clean/{classes[i1]}.png"
            if os.path.exists(ref):
                st.image(ref, caption="Font version of the guess", width=110)
        with right:
            st.markdown(
                f'<div class="card"><div class="big">{to_devanagari(name1)}</div>'
                f'<div class="latin">{to_latin(name1)}</div>'
                f'<div class="small">{p1 * 100:.0f}% confident</div></div>',
                unsafe_allow_html=True)
            st.progress(min(1.0, max(0.0, p1)))

        if p1 < 0.5:
            st.warning("Not very sure. Try a tighter, straighter crop with the letter in the centre.")

        st.markdown("#### Other possibilities")
        for p, i in guesses[1:]:
            n = letter_name(classes[i])
            st.write(f"**{to_devanagari(n)}**  {to_latin(n)}  ({p * 100:.0f}%)")
            st.progress(min(1.0, max(0.0, p)))

with tab2:
    st.markdown("""
1. Letters are drawn from a Brahmi font and given stone-style effects.
2. A small CNN learns the 48 letters from these images.
3. It is fine-tuned on hand-labelled crops from real inscription photos.
4. LipiLens shows its top 3 guesses, in Devanagari and Latin.
""")
    st.markdown("**Accuracy on photos the model never saw**")
    st.table({
        "Model": ["Font-only", "Fine-tuned (used here)"],
        "Top-1": ["0.25", "about 0.67"],
        "Top-3": ["0.37", "about 0.89"],
    })

with tab3:
    st.markdown("""
LipiLens is a student project for reading Brahmi inscriptions.

**Tips for best results**
- Crop tightly around one letter.
- Use a straight-on photo with the letter in the centre.
- Check the other possibilities if the first guess looks wrong.

**Limitations:** it reads single letters only, and similar-looking letters
can be confused. Photos come from Wikimedia Commons (credits in the GitHub repo).
""")