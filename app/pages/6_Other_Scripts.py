import html
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import streamlit as st
from scripts_map import TAMIL_MERGE, letter_in, parse_word, render
from translit import letter_name, to_latin

st.set_page_config(page_title="Other scripts", page_icon="🌏", layout="centered")
st.markdown(
    "<style>.big{font-size:2.6rem;color:#E0A95A;line-height:1.5;}"
    ".lab{color:#BFB29C;font-size:0.9rem;}</style>",
    unsafe_allow_html=True)
st.title("Other scripts")
st.write("See Brahmi sounds in Devanagari, Kannada and Tamil.")

SCRIPTS = [("Devanagari", "DEVANAGARI"), ("Kannada", "KANNADA"), ("Tamil", "TAMIL")]
tab1, tab2 = st.tabs(["Write a name", "Letter table"])

with tab1:
    name = st.text_input("Name in English letters", value="Amulya")
    eo = st.radio("Treat e and o as", ["long", "short"], horizontal=True,
                  help="Kannada and Tamil have both short and long e and o.")
    final = st.checkbox("Write a final consonant without the 'a' sound", value=True)
    words = name.strip().split()
    if words:
        tokens = [parse_word(w.lower(), final) for w in words]
        for label, script in SCRIPTS:
            text = " ".join(render(t, script, eo) for t in tokens)
            st.markdown(
                f'<div class="lab">{label}</div><div class="big">{html.escape(text)}</div>',
                unsafe_allow_html=True)
        st.caption("Tamil does not have separate letters for voiced and aspirated sounds, "
                   "so some letters are merged there.")

with tab2:
    codes = [f"{c:X}" for c in range(0x11005, 0x11035)]
    code = st.selectbox("Brahmi letter", codes,
                        format_func=lambda c: to_latin(letter_name(c)))
    lname = letter_name(code)
    cols = st.columns(4)
    ref = f"data/synthetic/clean/{code}.png"
    if os.path.exists(ref):
        cols[0].image(ref, caption="Brahmi (font)", width=90)
    for col, (label, script) in zip(cols[1:], SCRIPTS):
        ch = letter_in(script, lname) or "—"
        col.markdown(f'<div class="lab">{label}</div><div class="big">{ch}</div>',
                     unsafe_allow_html=True)
    merged = TAMIL_MERGE.get(lname)
    if merged:
        st.info(f"Tamil has no separate letter for {to_latin(lname)}. "
                f"It uses the {merged.lower()} letter instead.")
    if letter_in("TAMIL", lname) is None:
        st.info("Tamil has no letter for this sound.")

    with st.expander("See all 48 letters"):
        rows = []
        for c in codes:
            n = letter_name(c)
            rows.append({
                "Brahmi sound": to_latin(n),
                "Devanagari": letter_in("DEVANAGARI", n) or "—",
                "Kannada": letter_in("KANNADA", n) or "—",
                "Tamil": letter_in("TAMIL", n) or "—",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)