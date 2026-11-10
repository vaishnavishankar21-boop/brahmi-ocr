import glob
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import streamlit as st
from translit import letter_name, to_devanagari, to_latin

st.set_page_config(page_title="Brahmi quiz", page_icon="🎯", layout="centered")
st.title("Brahmi quiz")
st.write("Look at the letter and pick the right answer.")

codes = [f"{c:X}" for c in range(0x11005, 0x11035)]


def label(c):
    n = letter_name(c)
    return f"{to_devanagari(n)}   {to_latin(n)}"


mode = st.radio("Practise with", ["Real stone crops", "Font letters"], horizontal=True)

real = [p for p in glob.glob("data/real/crops/*/*.png")
        if os.path.basename(os.path.dirname(p)) in codes]
font = glob.glob("data/synthetic/clean/*.png")
use_real = mode == "Real stone crops" and len(real) > 0
pool = real if use_real else font

defaults = {"score": 0, "total": 0, "streak": 0, "best": 0, "q": None,
            "answered": False, "last_ok": False, "qid": 0, "mode": mode}
for key, val in defaults.items():
    st.session_state.setdefault(key, val)

if st.session_state.mode != mode:
    st.session_state.mode = mode
    st.session_state.q = None
    st.session_state.answered = False


def new_question():
    path = random.choice(pool)
    if use_real:
        correct = os.path.basename(os.path.dirname(path))
    else:
        correct = os.path.splitext(os.path.basename(path))[0]
    wrong = random.sample([c for c in codes if c != correct], 3)
    options = wrong + [correct]
    random.shuffle(options)
    st.session_state.qid += 1
    st.session_state.q = {"path": path, "correct": correct, "options": options}
    st.session_state.answered = False


if st.sidebar.button("Reset score"):
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.streak = 0
    st.session_state.best = 0
    st.session_state.q = None
    st.session_state.answered = False

if not pool:
    st.warning("No images found for the quiz.")
    st.stop()

if st.session_state.q is None:
    new_question()
q = st.session_state.q

c1, c2, c3 = st.columns(3)
c1.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
c2.metric("Streak", st.session_state.streak)
c3.metric("Best streak", st.session_state.best)

st.image(q["path"], width=180)
choice = st.radio(
    "Which letter is this?", q["options"], format_func=label, index=None,
    key=f"opt_{st.session_state.qid}", disabled=st.session_state.answered)

if not st.session_state.answered:
    if st.button("Check answer"):
        if choice is None:
            st.warning("Pick an answer first.")
        else:
            st.session_state.total += 1
            if choice == q["correct"]:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.session_state.best = max(st.session_state.best, st.session_state.streak)
                st.session_state.last_ok = True
            else:
                st.session_state.streak = 0
                st.session_state.last_ok = False
            st.session_state.answered = True
            st.rerun()
else:
    if st.session_state.last_ok:
        st.success("Correct!")
    else:
        st.error(f"Not quite. It was {label(q['correct'])}.")
    ref = f"data/synthetic/clean/{q['correct']}.png"
    if os.path.exists(ref):
        st.image(ref, caption="Font version of the right answer", width=100)
    if st.button("Next question"):
        new_question()
        st.rerun()