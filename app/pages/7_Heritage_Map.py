import pandas as pd
import streamlit as st

st.set_page_config(page_title="Heritage map", page_icon="🗺️", layout="centered")
st.title("Heritage map")
st.write("Six places where Ashoka's edicts are carved on rock.")

SITES = [
    {"name": "Girnar", "place": "Near Junagadh, Gujarat",
     "lat": 21.525075, "lon": 70.479543,
     "note": "All 14 Major Rock Edicts are carved here in Brahmi. Edict 2 names the Greek king Antiochos."},
    {"name": "Dhauli", "place": "Near Bhubaneswar, Odisha",
     "lat": 20.189157, "lon": 85.842594,
     "note": "The front of the rock is shaped like an elephant. It carries the separate Kalinga edicts."},
    {"name": "Jaugada", "place": "Ganjam district, Odisha",
     "lat": 19.522602, "lon": 84.830885,
     "note": "Like Dhauli, it carries the separate Kalinga edicts instead of Edicts 11 to 13."},
    {"name": "Sopara", "place": "Thane district, Maharashtra",
     "lat": 19.414153, "lon": 72.795063,
     "note": "An old port town. Only fragments of Rock Edicts 8 and 9 survive."},
    {"name": "Kalsi", "place": "Near Chakrata, Uttarakhand",
     "lat": 30.5180, "lon": 77.8482,
     "note": "One of the rock edicts that survives in its original state."},
    {"name": "Erragudi", "place": "Andhra Pradesh",
     "lat": 15.209722, "lon": 77.576944,
     "note": "All 14 Major Rock Edicts are here, along with Minor Rock Edicts 1 and 2."},
]

df = pd.DataFrame(SITES)
try:
    st.map(df, latitude="lat", longitude="lon", size=30000, color="#E0A95A")
except TypeError:
    st.map(df, latitude="lat", longitude="lon")

st.markdown("#### Pick a site")
choice = st.selectbox("Site", [s["name"] for s in SITES], label_visibility="collapsed")
s = next(x for x in SITES if x["name"] == choice)

st.markdown(f"## {s['name']}")
st.caption(f"{s['place']}  ·  {s['lat']:.4f}, {s['lon']:.4f}")
st.write(s["note"])
st.markdown(f"[Open in Google Maps](https://www.google.com/maps?q={s['lat']},{s['lon']})")

st.caption("Coordinates come from India's tentative World Heritage list for the Ashokan "
           "edict sites and are approximate. The map needs an internet connection.")