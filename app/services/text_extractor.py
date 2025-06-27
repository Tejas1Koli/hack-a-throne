from abc import ABC, abstractmethod
from typing import Optional
import pdfplumber
from docx import Document
import tempfile
import os

class TextExtractor(ABC):
    """Abstract base class for text extractors."""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text from the given file."""
        pass

class PDFTextExtractor(TextExtractor):
    """Extract text from PDF files."""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

class DOCXTextExtractor(TextExtractor):
    """Extract text from DOCX files."""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text])

class TextExtractorFactory:
    """Factory class to create appropriate text extractor based on file extension."""
    
    @staticmethod
    def get_extractor(file_path: str) -> Optional[TextExtractor]:
        """Get the appropriate text extractor for the given file."""
        _, ext = os.path.splitext(file_path.lower())
        
        extractors = {
            '.pdf': PDFTextExtractor(),
            '.docx': DOCXTextExtractor(),
        }
        
        return extractors.get(ext)
