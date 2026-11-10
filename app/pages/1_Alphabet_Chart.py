import glob
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import streamlit as st
from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="Alphabet chart", page_icon="🔤", layout="centered")
st.title("Brahmi alphabet chart")
st.write("Pick a letter to see its modern forms and real examples from stone.")

codes = [f"{c:X}" for c in range(0x11005, 0x11035)]


def label(c):
    n = letter_name(c)
    return f"{to_devanagari(n)}   {to_latin(n)}"


choice = st.selectbox("Choose a letter", codes, format_func=label)
name = letter_name(choice)

left, right = st.columns([1, 1.4])
with left:
    ref = f"data/synthetic/clean/{choice}.png"
    if os.path.exists(ref):
        st.image(ref, caption="Font version", width=150)
with right:
    st.markdown(f"## {to_devanagari(name)}  ·  {to_latin(name)}")
    st.write(f"Unicode: U+{choice}")

crops = sorted(glob.glob(f"data/real/crops/{choice}/*.png"))[:4]
if crops:
    st.markdown("#### Real examples from stone")
    cols = st.columns(len(crops))
    for col, f in zip(cols, crops):
        col.image(f, use_container_width=True)
else:
    st.info("No real examples saved for this letter yet.")

with st.expander("See all 48 letters"):
    for start in range(0, len(codes), 8):
        cols = st.columns(8)
        for col, c in zip(cols, codes[start:start + 8]):
            path = f"data/synthetic/clean/{c}.png"
            if os.path.exists(path):
                col.image(path, caption=to_latin(letter_name(c)), use_container_width=True)