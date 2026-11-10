import base64
import os
import unicodedata

import streamlit as st

st.set_page_config(page_title="Your name in Brahmi", page_icon="✍️", layout="centered")
st.title("Write your name in Brahmi")
st.write("Type a name in English letters and see it in Brahmi.")

FONT_PATH = "data/fonts/NotoSansBrahmi-Regular.ttf"
VIRAMA = unicodedata.lookup("BRAHMI VIRAMA")

CONS = {
    "k": "KA", "kh": "KHA", "g": "GA", "gh": "GHA",
    "ch": "CA", "chh": "CHA", "j": "JA", "jh": "JHA",
    "t": "TA", "th": "THA", "d": "DA", "dh": "DHA", "n": "NA",
    "p": "PA", "ph": "PHA", "b": "BA", "bh": "BHA", "m": "MA",
    "y": "YA", "r": "RA", "l": "LA", "v": "VA", "w": "VA",
    "s": "SA", "sh": "SHA", "h": "HA",
    "f": "PHA", "z": "JA", "q": "KA", "c": "KA",
}
CONS_KEYS = sorted(CONS, key=len, reverse=True)
VOWEL_KEYS = ["aa", "ai", "au", "ee", "ii", "oo", "uu", "a", "e", "i", "o", "u"]
ALIAS = {"ee": "ii", "oo": "uu"}


def take(word, i, keys):
    for k in keys:
        if word.startswith(k, i):
            return k
    return None


def convert_word(word, final_virama=True):
    out = []
    after_consonant = False
    i = 0
    while i < len(word):
        orig = take(word, i, VOWEL_KEYS)
        if orig:
            i += len(orig)
            v = ALIAS.get(orig, orig)
            if after_consonant:
                if v != "a":
                    out.append(unicodedata.lookup("BRAHMI VOWEL SIGN " + v.upper()))
                after_consonant = False
            else:
                out.append(unicodedata.lookup("BRAHMI LETTER " + v.upper()))
            continue
        c = take(word, i, CONS_KEYS)
        if c:
            i += len(c)
            if after_consonant:
                out.append(VIRAMA)
            out.append(unicodedata.lookup("BRAHMI LETTER " + CONS[c]))
            after_consonant = True
            continue
        if after_consonant and final_virama:
            out.append(VIRAMA)
        after_consonant = False
        out.append(word[i])
        i += 1
    if after_consonant and final_virama:
        out.append(VIRAMA)
    return "".join(out)


@st.cache_data
def font_css():
    if not os.path.exists(FONT_PATH):
        return ""
    with open(FONT_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return (
        "<style>@font-face{font-family:'BrahmiNoto';"
        f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}"
        ".brahmi{font-family:'BrahmiNoto',serif;font-size:3.2rem;"
        "line-height:1.5;color:#E0A95A;text-align:center;}</style>"
    )


css = font_css()
if css:
    st.markdown(css, unsafe_allow_html=True)
else:
    st.warning("Font file not found at data/fonts/NotoSansBrahmi-Regular.ttf. "
               "The letters may still show if your computer has a Brahmi font.")

name = st.text_input("Your name", value="Amulya")
final_virama = st.checkbox(
    "Write a final consonant without the 'a' sound (adds a virama)", value=True)

words = name.strip().split()
if words:
    results = [convert_word(w.lower(), final_virama) for w in words]
    brahmi = " ".join(results)
    st.markdown(f'<div class="brahmi">{brahmi}</div>', unsafe_allow_html=True)
    st.markdown("#### Word by word")
    for w, r in zip(words, results):
        st.markdown(
            f'**{w}** &nbsp;→&nbsp; <span class="brahmi" style="font-size:2rem">{r}</span>',
            unsafe_allow_html=True)
    st.write("Copy it from here:")
    st.code(brahmi, language=None)

with st.expander("How the spelling works"):
    st.markdown("""
- Consonants carry an "a" sound unless a vowel sign or a virama changes it.
- `kh gh ch chh jh th dh ph bh sh` are single letters.
- `ee` is written like `ii`, and `oo` is written like `uu`.
- Two consonants in a row are joined with a virama.
- `t d n` use the dental letters, and `c` is written as KA.
- This follows the modern Unicode rules, not the exact spelling used on Ashoka's stones.
""")