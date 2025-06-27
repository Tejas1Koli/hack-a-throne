# ------------------------------------------------------------
# Legal Risk Lens – Streamlit App (Hackathon Edition)
# ------------------------------------------------------------
# ☑ Installation (run once):
#   pip install streamlit python-docx docx2txt PyPDF2 plotly
# ------------------------------------------------------------
"""
Legal Risk Lens
===============
A compact Streamlit application that ingests PDF/DOCX contracts, extracts clauses,
estimates a lightweight risk score, offers safer language, and allows the user
to export an edited DOCX.

Designed for rapid prototyping in hackathons – no external services required.
Feel free to swap the toy `estimate_risk` logic with your own model or API.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import List, Tuple

import streamlit as st
from docx import Document
from docx.shared import Pt
import docx2txt
import PyPDF2
import plotly.express as px


st.set_page_config(
    page_title="Legal Risk Lens",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)



RISK_KEYWORDS = {
    "indemnify": 2,
    "liability": 2,
    "penalty": 2,
    "breach": 1,
    "terminate": 1,
    "exclusive": 1,
    "unlimited": 1,
    "warranty": 1,
    "confidential": 1,
}

COLOR_MAP = {
    "Low": "#d1fae5",      # green‑50
    "Medium": "#fef9c3",   # yellow‑100
    "High": "#fee2e2",     # red‑100
}

def extract_text(file) -> str:
    """Return raw text from a PDF or DOCX file-like object."""
    suffix = Path(file.name).suffix.lower()
    if suffix == ".pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix in {".docx", ".doc"}:
        # docx2txt returns a path if file-like; so dump to BytesIO first
        temp_path = "/tmp/uploaded_doc.docx"
        with open(temp_path, "wb") as fh:
            fh.write(file.read())
        return docx2txt.process(temp_path)
    st.warning("Unsupported file type – please upload PDF or DOCX.")
    return ""

def split_into_clauses(text: str) -> List[str]:
    """Naive clause splitter using double line‑breaks or semi‑colons."""
    blocks = re.split(r"\n{2,}|;\s*\n", text)
    return [b.strip() for b in blocks if len(b.strip()) > 30]

def estimate_risk(clause: str, tolerance: str) -> Tuple[int, str]:
    """Return a 0‑5 score and level label based on keywords.
    Tolerance scales the raw score.
    """
    raw = sum(weight for k, weight in RISK_KEYWORDS.items() if k in clause.lower())
    # Scale according to user tolerance
    scale = {"Strict": 1.2, "Moderate": 1.0, "Lenient": 0.8}[tolerance]
    score = min(int(round(raw * scale)), 5)
    if score >= 4:
        level = "High"
    elif score >= 2:
        level = "Medium"
    else:
        level = "Low"
    return score, level

def suggest_safer(clause: str) -> str:
    """Very naive safer alternative generator – replace risky words."""
    replacements = {
        "indemnify": "mutually indemnify",
        "unlimited": "reasonable",
        "penalty": "remedy",
    }
    safer = clause
    for k, v in replacements.items():
        safer = re.sub(rf"\b{k}\b", v, safer, flags=re.IGNORECASE)
    return safer

def get_risk_color(level: str) -> str:
    return COLOR_MAP[level]

# ------------------ SIDEBAR --------------------------------------------------
with st.sidebar:
    st.header("⚙ Settings")
    show_alternatives = st.checkbox("Show Safer Suggestions", True)
    tolerance = st.selectbox("Risk Tolerance", ["Strict", "Moderate", "Lenient"], index=1)

# ------------------ MAIN PAGE ------------------------------------------------

st.title("📜 Legal Document Risk Analyzer")
st.markdown(
    "Upload a contract or agreement and instantly see which clauses could expose you to risk."
)

uploaded_file = st.file_uploader("📂 Upload Legal Document", type=["pdf", "docx"])

if uploaded_file:
    raw_text = extract_text(uploaded_file)
    if not raw_text:
        st.stop()

    st.success("Document uploaded successfully ✅")
    st.subheader("🔍 Extracted Preview")
    st.text_area("First 2,000 characters", raw_text[:2000], height=200)

    clauses = split_into_clauses(raw_text)
    if not clauses:
        st.warning("Could not detect clauses. Try another document.")
        st.stop()

    # Analyse clauses
    st.divider()
    st.header("🧩 Clause‑by‑Clause Analysis")

    session_key = f"choices_{uploaded_file.name}"
    if session_key not in st.session_state:
        st.session_state[session_key] = ["Original"] * len(clauses)

    risk_levels = []

    for idx, clause in enumerate(clauses):
        score, level = estimate_risk(clause, tolerance)
        risk_levels.append(level)
        color = get_risk_color(level)
        safer_clause = suggest_safer(clause)

        with st.expander(f"Clause {idx + 1} – {level} Risk ({score}/5)"):
            st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:6px'>"
                        f"{clause}</div>", unsafe_allow_html=True)

            st.caption("ℹ️ Detected keywords boost the risk score. Replace or negotiate them if possible.")

            if show_alternatives and clause.lower() != safer_clause.lower():
                st.markdown("**🔐 Suggested Alternative:**")
                st.code(safer_clause)
                st.session_state[session_key][idx] = st.radio(
                    "Choose version to keep:",
                    ["Original", "Suggested"],
                    key=f"choice_{idx}",
                    horizontal=True,
                )

    # ------------------ SUMMARY VISUAL --------------------------------------
    st.divider()
    st.header("📊 Risk Summary")
    risk_df = (
        px.data.tips()  # dummy frame to satisfy px in offline env
        .head(0)
        .assign(risk_level=risk_levels[:0])  # empty init
    )
    risk_df = st.DataFrame({"risk_level": risk_levels})
    fig = px.pie(risk_df, names="risk_level", title="Clause Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

    # ------------------ EXPORT ----------------------------------------------
    st.divider()
    st.header("⬇️ Export Revised Contract")

    def build_docx(selections: List[str]):
        doc = Document()
        doc.styles["Normal"].font.name = "Times New Roman"
        doc.styles["Normal"].font.size = Pt(11)

        for choice, original, idx in zip(selections, clauses, range(len(clauses))):
            if choice == "Suggested":
                para = suggest_safer(original)
            else:
                para = original
            doc.add_paragraph(para)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    if st.button("Generate & Download"):
        buf = build_docx(st.session_state[session_key])
        st.download_button(
            "📥 Download DOCX",
            data=buf,
            file_name="revised_contract.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

else:
    st.info("⬆️ Upload a PDF or DOCX to begin.")
