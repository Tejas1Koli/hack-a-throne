import json
import logging
import os
import time
import traceback
from typing import Dict, Any, Optional

import httpx

from ..analyzers.base_analyzer import BaseClauseAnalyzer
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterAnalyzer(BaseClauseAnalyzer):
    """Clause analyzer using OpenRouter API."""
    
    def __init__(self):
        logger.info("Initializing OpenRouterAnalyzer")
        
        try:
            self.api_key = settings.OPENROUTER_API_KEY
            self.api_url = settings.OPENROUTER_URL
            self.model = settings.OPENROUTER_MODEL
            
            if not self.api_key:
                error_msg = "OpenRouter API key is not configured"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"OpenRouterAnalyzer initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouterAnalyzer: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def analyze_clause(self, clause: str) -> Dict[str, Any]:
        """
        Analyze a clause using OpenRouter API.
        
        Args:
            clause: The text of the clause to analyze
            
        Returns:
            Dict containing analysis with keys: clause, risk_score, explanation, 
            clause_type, safer_version
        """
        logger.debug(f"Analyzing clause: {clause[:100]}...")
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(clause)
            logger.debug("Built prompt for OpenRouter API")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            logger.debug(f"Sending request to OpenRouter API (model: {self.model})")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    response_time = time.time() - start_time
                    
                    logger.debug(f"OpenRouter API response status: {response.status_code}")
                    logger.debug(f"API response time: {response_time:.2f}s")
                    
                    response.raise_for_status()
                    
                    result = response.json()
                    logger.debug("Received response from OpenRouter API")
                    
                    # Log API usage if available
                    if 'usage' in result:
                        usage = result['usage']
                        logger.debug(
                            f"API usage - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}, "
                            f"Completion tokens: {usage.get('completion_tokens', 'N/A')}, "
                            f"Total tokens: {usage.get('total_tokens', 'N/A')}"
                        )
                    
                    content = result['choices'][0]['message']['content']
                    logger.debug(f"Raw API response content: {content[:200]}...")
                    
                    try:
                        analysis = json.loads(content)
                        logger.debug("Successfully parsed API response as JSON")
                        
                        result = {
                            "clause": clause,
                            "risk_score": float(analysis.get("risk_score", 0)),
                            "explanation": analysis.get("explanation", ""),
                            "clause_type": analysis.get("clause_type", "Other"),
                            "safer_version": analysis.get("safer_version", clause)
                        }
                        
                        logger.debug(f"Analysis complete. Risk score: {result['risk_score']}, Type: {result['clause_type']}")
                        return result
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"Failed to parse API response as JSON: {str(e)}"
                        logger.error(error_msg)
                        logger.error(f"Response content: {content}")
                        raise ValueError(error_msg) from e
                        
                except httpx.HTTPStatusError as e:
                    error_msg = f"OpenRouter API request failed with status {e.response.status_code}"
                    logger.error(error_msg)
                    logger.error(f"Response: {e.response.text}")
                    raise
                    
                except httpx.TimeoutException:
                    error_msg = "OpenRouter API request timed out"
                    logger.error(error_msg)
                    raise TimeoutError(error_msg) from None
                    
                except Exception as e:
                    error_msg = f"Unexpected error calling OpenRouter API: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    raise
                    
        except Exception as e:
            logger.error(f"Error in analyze_clause: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return error response
            return {
                "clause": clause,
                "risk_score": 0.0,
                "explanation": f"Error analyzing clause: {str(e)}",
                "clause_type": "Error",
                "safer_version": clause,
                "error": str(e)
            }
    
    def _build_prompt(self, clause: str) -> str:
        """
        Build the prompt for the OpenRouter API.
        
        Args:
            clause: The legal clause to analyze
            
        Returns:
            Formatted prompt string
        """
        logger.debug("Building prompt for OpenRouter API")
        
        prompt = f"""You are a legal document analysis assistant. Analyze the following legal clause and provide:

1. Risk score (0-5, where 0 is no risk and 5 is high risk)
2. Brief explanation of the risk
3. Clause type (e.g., 'Liability', 'Confidentiality', 'Termination', 'Governing Law', 'Indemnification')
4. A safer rewritten version of the clause

IMPORTANT: Return ONLY a valid JSON object with these exact keys: risk_score, explanation, clause_type, safer_version

Clause to analyze:
{clause}

JSON Response:"""

        logger.debug(f"Built prompt with {len(clause)} characters of clause text")
        return prompt
