# ------------------------------------------------------------
# Simple Legal Risk Analyzer – Streamlit (Lite Version)
# ------------------------------------------------------------
# Purpose: Keep the code minimal and readable so you can grasp it quickly.
# Libraries needed: streamlit, PyPDF2, docx2txt
# Install with:
#   pip install streamlit PyPDF2 docx2txt
# ------------------------------------------------------------

import streamlit as st
import re
import PyPDF2
import docx2txt
from pathlib import Path

# ------------------ PAGE CONFIG ---------------------------------------------
st.set_page_config(page_title="Legal Risk Analyzer (Lite)", page_icon="📄")

# ------------------ CONSTANTS -----------------------------------------------
RISK_KEYWORDS = {
    "indemnify": 3,
    "liability": 2,
    "penalty": 2,
    "terminate": 1,
    "exclusive": 1,
}

COLOR = {
    "Low": "#d1fae5",      # Green tint
    "Medium": "#fef9c3",   # Yellow tint
    "High": "#fee2e2",     # Red tint
}

# ------------------ UTILITY FUNCTIONS ---------------------------------------

def extract_text(upload):
    """Return plain text from a PDF or DOCX file."""
    ext = Path(upload.name).suffix.lower()
    if ext == ".pdf":
        reader = PyPDF2.PdfReader(upload)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == ".docx":
        return docx2txt.process(upload)
    st.error("Only PDF or DOCX files are supported.")
    return ""


def split_into_clauses(text: str):
    """Very simple clause splitter: break on double newlines."""
    return [c.strip() for c in re.split(r"\n{2,}", text) if len(c.strip()) > 40]


def risk_of_clause(clause: str):
    """Count risky keywords and map to a risk level."""
    score = sum(weight for k, weight in RISK_KEYWORDS.items() if k in clause.lower())
    if score >= 4:
        return score, "High"
    if score >= 2:
        return score, "Medium"
    return score, "Low"

# ------------------ UI -------------------------------------------------------

st.title("📄 Simple Legal Risk Analyzer")
st.write(
    "Upload a PDF or DOCX contract. The app splits it into clauses and flags risky ones based on keywords."
)

upload = st.file_uploader("Upload contract", type=["pdf", "docx"])

if upload:
    text = extract_text(upload)
    if not text:
        st.stop()

    st.subheader("Preview")
    st.text_area("First 1500 characters", text[:1500], height=150)

    st.subheader("Clause Analysis")

    for num, clause in enumerate(split_into_clauses(text), start=1):
        score, level = risk_of_clause(clause)
        bg = COLOR[level]
        with st.expander(f"Clause {num} – {level} risk (score {score})"):
            st.markdown(
                f"<div style='background:{bg};padding:10px;border-radius:6px'>{clause}</div>",
                unsafe_allow_html=True,
            )
else:
    st.info("➡️ Upload a document to begin.")
