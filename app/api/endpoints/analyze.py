from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import tempfile
import os
from app.models.schemas import DocumentAnalysis, HTTPError
from app.services.analyzers.openrouter_analyzer import OpenRouterAnalyzer
from app.services.document_processor import DocumentProcessor

router = APIRouter()

def get_document_processor():
    """Dependency for document processor with OpenRouter analyzer."""
    analyzer = OpenRouterAnalyzer()
    return DocumentProcessor(analyzer)

@router.post(
    "",
    response_model=DocumentAnalysis,
    responses={
        400: {"model": HTTPError, "description": "Invalid file format or content"},
        500: {"model": HTTPError, "description": "Internal server error"}
    }
)
async def analyze_document(
    file: UploadFile = File(..., description="Legal document to analyze (PDF or DOCX)"),
    processor: DocumentProcessor = Depends(get_document_processor)
) -> DocumentAnalysis:
    """
    Analyze a legal document and return clause-by-clause analysis.
    
    - **file**: Legal document in PDF or DOCX format
    - **returns**: Analysis of the document including risk scores and suggestions
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = os.path.splitext(file.filename)[-1].lower()
    if file_ext not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload a PDF or DOCX file."
        )
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name
    
    try:
        # Process the document
        result = await processor.process_document(temp_path)
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
