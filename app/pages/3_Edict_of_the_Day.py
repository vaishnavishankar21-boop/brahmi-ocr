import datetime
import os

import streamlit as st

st.set_page_config(page_title="Edict of the day", page_icon="📜", layout="centered")
st.title("Edict of the day")
st.write("A new story from the stone every day.")

# To show a photo, put its file name from data/real/raw in "photo".
EDICTS = [
    {"title": "Girnar", "place": "Near Junagadh, Gujarat",
     "story": "All 14 Major Rock Edicts are carved here in Brahmi. Edict 2 names the Greek king Antiochos. "
              "The site also records the story of Sudarshan Lake.",
     "photo": ""},
    {"title": "Dhauli", "place": "Near Bhubaneswar, Odisha",
     "story": "The front of the rock is shaped like an elephant. It was found in 1837 by Markham Kittoe. "
              "Two separate Kalinga edicts are carved here, and Edicts 11 to 13 are left out.",
     "photo": ""},
    {"title": "Kalsi", "place": "Near Chakrata, Dehradun district, Uttarakhand",
     "story": "One of the rock edicts that survives in its original state, written in Brahmi.",
     "photo": ""},
    {"title": "Jaugada", "place": "Ganjam district, Odisha",
     "story": "Like Dhauli, it carries the separate Kalinga edicts instead of Edicts 11 to 13.",
     "photo": ""},
    {"title": "Erragudi", "place": "Andhra Pradesh",
     "story": "All 14 Major Rock Edicts are here, along with Minor Rock Edicts 1 and 2.",
     "photo": ""},
    {"title": "Sopara", "place": "Thane district, Maharashtra",
     "story": "Only fragments of Rock Edicts 8 and 9 survive at this site.",
     "photo": ""},
    {"title": "Mansehra and Shahbazgarhi", "place": "Pakistan",
     "story": "These edicts are written in Kharosthi, not Brahmi. Brahmi was not the only script of "
              "the time, and LipiLens cannot read these yet.",
     "photo": ""},
    {"title": "Rock Edict XII", "place": "Several sites",
     "story": "A strong appeal for religious tolerance and respect between different sects.",
     "photo": ""},
    {"title": "Rock Edict XIII", "place": "Several sites",
     "story": "The most famous edict. It talks about regret over the suffering caused by the Kalinga war.",
     "photo": ""},
]

today = datetime.date.today()
default = today.toordinal() % len(EDICTS)
st.caption(f"Today is {today.strftime('%d %B %Y')}")

i = st.selectbox("Browse edict sites", range(len(EDICTS)), index=default,
                 format_func=lambda n: EDICTS[n]["title"])
e = EDICTS[i]

st.markdown(f"## {e['title']}")
st.caption(e["place"])
st.write(e["story"])

path = os.path.join("data", "real", "raw", e["photo"]) if e["photo"] else ""
if path and os.path.exists(path):
    st.image(path, caption="Photo from Wikimedia Commons (see credits in the repo)",
             use_container_width=True)
else:
    st.info("No photo attached to this site yet.")

st.caption("Facts checked against Wikipedia's pages on the edicts of Ashoka. "
           "Always double-check before using them in your report.")