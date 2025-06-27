import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import json

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")

def analyze_document(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Send a document to the API for analysis.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Analysis results as a dictionary with 'overall_risk' and 'clauses' keys
    """
    url = f"{API_BASE_URL}/analyze"
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
            response = requests.post(url, files=files, timeout=60)
            
        response.raise_for_status()
        
        # Get the raw response
        data = response.json()
        
        # Transform the response to match frontend expectations
        if isinstance(data, list):
            # If response is a list of clauses
            clauses = data
        elif isinstance(data, dict) and 'clauses' in data:
            # If response already has a 'clauses' key
            clauses = data['clauses']
        else:
            # If single clause response, wrap in a list
            clauses = [data]
            
        # Calculate overall risk (average of all clause risks)
        if clauses:
            overall_risk = sum(float(clause.get('risk_score', 0)) for clause in clauses) / len(clauses)
        else:
            overall_risk = 0.0
            
        return {
            'overall_risk': overall_risk,
            'clauses': clauses
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error analyzing document: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

def get_health() -> bool:
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get("status") == "ok"
        return False
    except (requests.RequestException, json.JSONDecodeError):
        return False

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """
    Save an uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Path to the saved file or None if failed
    """
    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = temp_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return str(file_path)
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return None