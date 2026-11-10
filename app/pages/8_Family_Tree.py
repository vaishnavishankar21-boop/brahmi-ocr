import streamlit as st

st.set_page_config(page_title="Family tree", page_icon="🌳", layout="centered")
st.title("Brahmi family tree")
st.write("Brahmi is the ancestor of most scripts used across South and Southeast Asia.")

EDGES = [
    ("Brahmi", "Gupta"),
    ("Gupta", "Nagari"),
    ("Nagari", "Devanagari"),
    ("Gupta", "Sharada"),
    ("Sharada", "Gurmukhi"),
    ("Gupta", "Bengali-Assamese"),
    ("Brahmi", "Tamil-Brahmi"),
    ("Tamil-Brahmi", "Pallava"),
    ("Pallava", "Tamil"),
    ("Pallava", "Grantha"),
    ("Grantha", "Malayalam"),
    ("Pallava", "Khmer"),
    ("Khmer", "Thai"),
    ("Brahmi", "Kadamba"),
    ("Kadamba", "Kannada"),
    ("Kadamba", "Telugu"),
]
LABELS = {
    "Brahmi": "Brahmi\\n(3rd century BCE)",
    "Gupta": "Gupta\\n(5th century CE)",
}

parents = {child: parent for parent, child in EDGES}
nodes = sorted({n for edge in EDGES for n in edge})
choices = sorted(c for _, c in EDGES)


def make_dot(highlight):
    hl = set(highlight)
    lines = [
        "digraph G {",
        'bgcolor="transparent"; rankdir=TB; nodesep=0.3;',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=13, '
        'fillcolor="#221C17", color="#E0A95A", fontcolor="#F3EBDD"];',
        'edge [color="#BFB29C"];',
    ]
    for n in nodes:
        attrs = f'label="{LABELS.get(n, n)}"'
        if n in hl:
            attrs += ', fillcolor="#E0A95A", fontcolor="#14110F"'
        lines.append(f'"{n}" [{attrs}];')
    for p, c in EDGES:
        if p in hl and c in hl:
            lines.append(f'"{p}" -> "{c}" [color="#E0A95A", penwidth=3];')
        else:
            lines.append(f'"{p}" -> "{c}";')
    lines.append("}")
    return "\n".join(lines)


choice = st.selectbox("Trace a script back to Brahmi", ["(none)"] + choices)
path = []
if choice != "(none)":
    path = [choice]
    while path[-1] in parents:
        path.append(parents[path[-1]])
    path.reverse()
    st.success("  →  ".join(path))

st.graphviz_chart(make_dot(path), use_container_width=True)

st.markdown("#### Did you know?")
st.markdown("""
- Brahmi appeared fully developed in the 3rd century BCE, and the 5th-century Gupta script is sometimes called "Late Brahmi".
- Devanagari, Tamil and Kannada look very different, but they share the same logic: a consonant with a built-in "a" sound, plus vowel signs.
- Tamil-Brahmi inscriptions from the 3rd century BCE are among the earliest evidence of the Brahmic family.
""")

with st.expander("Text version of the tree"):
    st.code("""Brahmi
├── Gupta
│   ├── Nagari → Devanagari
│   ├── Sharada → Gurmukhi
│   └── Bengali-Assamese
├── Tamil-Brahmi
│   └── Pallava
│       ├── Tamil
│       ├── Grantha → Malayalam
│       └── Khmer → Thai
└── Kadamba
    ├── Kannada
    └── Telugu""", language=None)

st.caption("This tree is simplified. Scholars disagree on some details (for example, how Tamil "
           "developed), and many scripts are left out.")