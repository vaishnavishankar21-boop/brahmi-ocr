import base64
import html
import os
import unicodedata

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Share card", page_icon="📤", layout="centered")
st.title("Share card")
st.write("Make a picture you can post or send.")

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
def font_b64():
    if not os.path.exists(FONT_PATH):
        return ""
    with open(FONT_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


PAGE = """
<style>
@font-face{font-family:'BrahmiNoto';src:url(data:font/ttf;base64,__FONT__) format('truetype');}
body{margin:0;font-family:Georgia,serif;color:#F3EBDD;}
#card{width:600px;height:340px;box-sizing:border-box;padding:28px;border-radius:20px;
 background:linear-gradient(135deg,#2b221b,#14110F);border:2px solid #E0A95A;
 display:flex;flex-direction:column;justify-content:space-between;text-align:center;}
#brahmi{font-family:'BrahmiNoto',Georgia,serif;font-size:76px;color:#E0A95A;line-height:1.3;}
.small{color:#BFB29C;font-size:16px;}
.title{font-size:20px;letter-spacing:.08em;}
button{margin-top:16px;padding:10px 18px;font-size:16px;border-radius:8px;border:0;
 background:#E0A95A;color:#14110F;cursor:pointer;}
#out img{margin-top:14px;max-width:100%;border-radius:12px;}
#note{margin-top:8px;font-size:14px;color:#BFB29C;}
</style>
<div id="card">
  <div class="title">__TITLE__</div>
  <div id="brahmi">__MAIN__</div>
  <div class="small">__SUB__</div>
  <div class="small">LipiLens &middot; read ancient Brahmi</div>
</div>
<button id="go">Make picture</button>
<div id="note"></div>
<div id="out"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
document.getElementById('go').onclick = async function () {
  const note = document.getElementById('note');
  try {
    await document.fonts.load("76px BrahmiNoto");
    await document.fonts.ready;
    const canvas = await html2canvas(document.getElementById('card'), {scale: 2, backgroundColor: null});
    const img = new Image();
    img.src = canvas.toDataURL('image/png');
    const out = document.getElementById('out');
    out.innerHTML = '';
    out.appendChild(img);
    note.textContent = 'Right-click the picture and choose Save image as. On a phone, press and hold it.';
  } catch (e) {
    note.textContent = 'Could not make the picture. Take a screenshot of the card instead.';
  }
};
</script>
"""

mode = st.radio("Card type", ["My name in Brahmi", "My quiz score"], horizontal=True)

if mode == "My name in Brahmi":
    name = st.text_input("Your name", value="Amulya")
    words = name.strip().split()
    if not words:
        st.stop()
    title = "My name in Brahmi"
    main = " ".join(convert_word(w.lower()) for w in words)
    sub = name.strip()
else:
    total = st.session_state.get("total", 0)
    score = st.session_state.get("score", 0)
    best = st.session_state.get("best", 0)
    if total == 0:
        st.info("Play the Quiz page first, then come back here.")
        st.stop()
    title = "Brahmi quiz"
    main = f"{score}/{total}"
    sub = f"Best streak: {best}"

page = (PAGE.replace("__FONT__", font_b64())
        .replace("__TITLE__", html.escape(title))
        .replace("__MAIN__", html.escape(main))
        .replace("__SUB__", html.escape(sub)))
components.html(page, height=820, scrolling=True)