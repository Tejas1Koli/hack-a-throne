import logging
import os
import tempfile
import traceback
from typing import List, Dict, Any, Optional

import spacy

from .text_extractor import TextExtractorFactory
from .analyzers.base_analyzer import BaseClauseAnalyzer

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents and analyze their clauses."""
    
    def __init__(self, clause_analyzer: BaseClauseAnalyzer):
        """Initialize with a clause analyzer."""
        logger.info("Initializing DocumentProcessor")
        self.clause_analyzer = clause_analyzer
        
        try:
            logger.debug("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return the analysis."""
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Extract text
            logger.debug("Extracting text from document...")
            text = self._extract_text(file_path)
            if not text:
                error_msg = "Failed to extract text from the document"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Extracted text length: {len(text)} characters")
            
            # Preprocess and split into clauses
            logger.debug("Preprocessing text and splitting into clauses...")
            text = self._preprocess_text(text)
            clauses = self._split_into_clauses(text)
            logger.info(f"Document split into {len(clauses)} clauses")
            
            # Analyze each clause
            analyses = []
            logger.debug("Starting clause analysis...")
            
            for i, clause in enumerate(clauses, 1):
                try:
                    if len(clause) > 20:  # Only analyze meaningful clauses
                        logger.debug(f"Analyzing clause {i}/{len(clauses)} (length: {len(clause)})")
                        analysis = await self.clause_analyzer.analyze_clause(clause)
                        analyses.append(analysis)
                        logger.debug(f"Clause {i} analysis complete")
                    else:
                        logger.debug(f"Skipping short clause: {clause[:50]}...")
                except Exception as e:
                    logger.error(f"Error analyzing clause {i}: {str(e)}")
                    logger.error(f"Clause content: {clause}")
                    logger.error(traceback.format_exc())
                    # Continue with other clauses even if one fails
            
            logger.info(f"Completed analysis of {len(analyses)} clauses")
            
            # Calculate overall risk (simple average for now)
            overall_risk = 0.0
            if analyses:
                overall_risk = sum(a['risk_score'] for a in analyses) / len(analyses)
                logger.debug(f"Calculated overall risk: {overall_risk}")
            
            result = {
                "clauses": analyses,
                "overall_risk": overall_risk
            }
            
            logger.info("Document processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from a file."""
        logger.debug(f"Extracting text from file: {file_path}")
        try:
            extractor = TextExtractorFactory.get_extractor(file_path)
            if not extractor:
                error_msg = f"Unsupported file type: {file_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            text = extractor.extract_text(file_path)
            logger.debug(f"Successfully extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess the extracted text."""
        logger.debug("Preprocessing text...")
        try:
            processed = " ".join(text.split())
            logger.debug(f"Text preprocessed. Original length: {len(text)}, Processed length: {len(processed)}")
            return processed
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            logger.error(traceback.format_exc())
            # Return original text if preprocessing fails
            return text
    
    def _split_into_clauses(self, text: str) -> List[str]:
        """Split text into clauses using spaCy sentence segmentation."""
        logger.debug("Splitting text into clauses...")
        try:
            doc = self.nlp(text)
            clauses = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            logger.debug(f"Text split into {len(clauses)} clauses")
            return clauses
        except Exception as e:
            logger.error(f"Error splitting text into clauses: {str(e)}")
            logger.error(traceback.format_exc())
            # Fallback to simple split on periods if spaCy fails
            return [s.strip() for s in text.split('.') if s.strip()]
