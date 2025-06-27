import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px
from pathlib import Path
from typing import Dict, Any, Optional

# Import utilities
from utils import analyze_document, get_health, save_uploaded_file

# Page configuration
st.set_page_config(
    page_title="Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #2c3e50; margin-bottom: 1rem; }
    .sub-header { color: #3498db; margin-top: 1.5rem; margin-bottom: 1rem; }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    .analysis-card { 
        background-color: #f8f9fa; 
        border-radius: 0.5rem; 
        padding: 1.5rem; 
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

def display_sidebar():
    """Display the sidebar with app information and controls."""
    st.sidebar.title("⚖️ LegalDoc Analyzer")
    st.sidebar.markdown("---")
    
    # API status
    st.sidebar.subheader("API Status")
    api_status = get_health()
    status_text = "🟢 Running" if api_status else "🔴 Not Available"
    st.sidebar.markdown(f"**Backend API:** {status_text}")
    
    if not api_status:
        st.sidebar.warning("Please ensure the backend API is running on http://localhost:8001")
    
    # File upload
    st.sidebar.markdown("---")
    st.sidebar.subheader("Upload Document")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application analyzes legal documents to identify potential risks "
        "and suggests safer alternatives for problematic clauses."
    )

def display_main_content():
    """Display the main content area."""
    st.markdown("<h1 class='main-header'>Legal Document Analyzer</h1>", unsafe_allow_html=True)
    
    if st.session_state.uploaded_file is None:
        display_upload_instruction()
    else:
        process_uploaded_file()

def display_upload_instruction():
    """Display upload instructions."""
    st.markdown("### 📄 Upload a legal document to get started")
    st.markdown("Use the sidebar to upload a PDF or DOCX file for analysis.")
    
    # Placeholder for demo purposes
    st.image(
        "https://cdn-icons-png.flaticon.com/512/2991/2991111.png",
        width=200,
        use_column_width=False
    )

def process_uploaded_file():
    """Process the uploaded file and display results."""
    uploaded_file = st.session_state.uploaded_file
    
    # Display file info
    st.markdown(f"### 📑 Analyzing: **{uploaded_file.name}**")
    st.markdown(f"**File type:** {uploaded_file.type}")
    st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
    
    # Analyze button
    if st.button("🔍 Analyze Document", use_container_width=True):
        with st.spinner("Analyzing document..."):
            # Save the uploaded file
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                # Show progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress
                for percent in range(0, 101, 10):
                    time.sleep(0.1)
                    progress_bar.progress(percent)
                    status_text.text(f"Progress: {percent}%")
                
                # Get analysis results
                analysis_results = analyze_document(file_path)
                
                if analysis_results:
                    st.session_state.analysis_results = analysis_results
                    st.session_state.show_results = True
                    st.rerun()
                else:
                    st.error("Failed to analyze the document. Please try again.")
                    st.session_state.analysis_results = None
                    st.session_state.show_results = False
                
                # Clean up the temporary file
                try:
                    os.remove(file_path)
                except:
                    pass
            else:
                st.error("Failed to save the uploaded file.")
    
    # Display results if available
    if st.session_state.get('show_results', False) and st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results)

def display_analysis_results(results: Dict[str, Any]):
    """Display the analysis results."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Overall risk score
    overall_risk = results.get('overall_risk', 0)
    risk_category = get_risk_category(overall_risk)
    
    # Display risk score with color
    st.markdown(f"### Overall Risk Score: <span class='{risk_category}'>{overall_risk:.1f}/5.0</span>", 
               unsafe_allow_html=True)
    
    # Risk meter with better visualization
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric("Risk Level", risk_category.capitalize())
    with col2:
        st.progress(overall_risk / 5.0, text=f"{overall_risk:.1f}/5.0")
    
    # Risk interpretation with more detailed explanation
    st.markdown("### Risk Assessment")
    st.markdown(get_risk_interpretation(overall_risk))
    
    # Display clauses in an expandable section
    with st.expander("📋 View Detailed Analysis", expanded=True):
        clauses = results.get('clauses', [])
        
        if not clauses:
            st.info("No clauses were analyzed or no issues were found.")
            return
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📄 Clause-by-Clause Analysis", "📊 Risk Summary"])
        
        with tab1:
            display_detailed_view(clauses)
        
        with tab2:
            display_summary_view(clauses)

def display_detailed_view(clauses: list):
    """Display detailed view of each clause analysis."""
    for i, clause in enumerate(clauses, 1):
        with st.container():
            st.markdown("---")
            st.markdown(f"### 📝 Clause {i}")
            
            # Main content in columns
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Risk score with visual indicator
                risk_score = clause.get('risk_score', 0)
                risk_category = get_risk_category(risk_score)
                st.markdown("#### Risk Assessment")
                st.markdown(
                    f"<div style='font-size: 1.5rem;'><span class='{risk_category}'>"
                    f"{risk_score:.1f}/5.0 - {risk_category.capitalize()}</span></div>", 
                    unsafe_allow_html=True
                )
                
                # Risk meter
                st.progress(risk_score / 5.0, text=f"{risk_score:.1f}/5.0")
                
                # Clause metadata
                st.markdown("#### Details")
                clause_type = clause.get('clause_type', 'Uncategorized')
                st.markdown(f"**Type:** {clause_type}")
                
            with col2:
                # Original clause
                st.markdown("#### Original Clause")
                st.markdown(f"```\n{clause.get('clause', 'No content')}\n```")
                
                # Explanation and suggestions
                explanation = clause.get('explanation', '')
                if explanation:
                    st.markdown("#### Analysis")
                    st.markdown(explanation)
                
                # Safer version if available
                safer_version = clause.get('safer_version')
                if safer_version:
                    with st.expander("✨ Suggested Improvement", expanded=False):
                        st.markdown(safer_version)
        st.markdown("---")


def display_summary_view(clauses: list):
    """Display summary statistics and visualizations."""
    if not clauses:
        return
    
    # Create DataFrame for visualization
    df = pd.DataFrame([{
        'Clause': f"Clause {i+1}",
        'Risk Score': clause.get('risk_score', 0),
        'Type': clause.get('clause_type', 'Unknown'),
        'Has Suggestion': clause.get('safer_version', '') != clause.get('clause', '')
    } for i, clause in enumerate(clauses)])
    
    # Risk distribution
    st.markdown("### Risk Distribution")
    fig = px.pie(
        df, 
        names='Risk Score', 
        title='Risk Score Distribution',
        color_discrete_sequence=px.colors.sequential.RdBu_r
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk by clause type
    st.markdown("### Risk by Clause Type")
    if len(df['Type'].unique()) > 1:  # Only show if we have multiple types
        fig = px.box(
            df, 
            x='Type', 
            y='Risk Score',
            color='Type',
            title='Risk Score by Clause Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Suggestions summary
    suggestions_count = df['Has Suggestion'].sum()
    st.metric("Suggested Improvements", f"{suggestions_count} of {len(df)}")

def get_risk_category(score: float) -> str:
    """Get the risk category based on the score."""
    if score >= 4.0:
        return "risk-high"
    elif score >= 2.0:
        return "risk-medium"
    return "risk-low"

def get_risk_interpretation(score: float) -> str:
    """Get a human-readable interpretation of the risk score."""
    if score >= 4.0:
        return "🚨 **High Risk**: This document contains several high-risk clauses that require immediate attention. " \
               "We strongly recommend reviewing and modifying the highlighted sections."
    elif score >= 2.5:
        return "⚠️ **Moderate Risk**: This document contains some potentially problematic clauses. " \
               "Consider reviewing the suggestions to improve these sections."
    elif score >= 1.0:
        return "ℹ️ **Low Risk**: This document appears to be relatively safe, but there are a few areas that could be improved. " \
               "Review the suggestions for potential enhancements."
    return "✅ **Minimal Risk**: This document appears to be well-drafted with minimal risks. " \
           "No immediate action is required, but you may still want to review the detailed analysis."

# Main app flow
try:
    display_sidebar()
    display_main_content()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)