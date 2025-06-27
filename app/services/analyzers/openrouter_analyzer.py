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
            # Debug: API key presence, prefix, and length
            logger.info(f"[DEBUG] API Key loaded: {'set' if self.api_key else 'NOT set'}")
            if self.api_key:
                logger.info(f"[DEBUG] API Key prefix: {self.api_key[:8]}")
                logger.info(f"[DEBUG] API Key length: {len(self.api_key)}")
            # Get SSL verification setting, default to True if not set
            self.verify_ssl = getattr(settings, 'OPENROUTER_VERIFY_SSL', True)
            logger.info(f"[DEBUG] SSL verification: {'enabled' if self.verify_ssl else 'disabled'}")
            if not self.api_key:
                error_msg = "OpenRouter API key is not configured"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.info(f"OpenRouterAnalyzer initialized with model: {self.model}")
            # Create a persistent client with connection pooling
            self.client = httpx.AsyncClient(
                timeout=60.0,
                verify=self.verify_ssl,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                )
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouterAnalyzer: {str(e)}")
            logger.error(traceback.format_exc())
            raise
            
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
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
        
        # Ensure the client is still connected
        if self.client.is_closed:
            logger.warning("HTTP client was closed, recreating...")
            self.client = httpx.AsyncClient(verify=self.verify_ssl)
        
        try:
            prompt = self._build_prompt(clause)
            logger.debug("Built prompt for OpenRouter API")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Referer": "http://localhost:8001",  # Correct header name for OpenRouter
                "X-Title": "Legal Document Analyzer"  # Optional: Identify your app
            }
            # Debug: Log headers with redacted API key
            redacted_headers = {k: (v[:8] + '...' if k == 'Authorization' else v) for k, v in headers.items()}
            logger.info(f"[DEBUG] Request headers: {redacted_headers}")
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            logger.info(f"[DEBUG] Request payload: {json.dumps(payload)}")
            logger.debug(f"Sending request to OpenRouter API (model: {self.model})")
            try:
                response = await self.client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response_time = time.time() - start_time
                logger.debug(f"OpenRouter API response status: {response.status_code}")
                logger.info(f"[DEBUG] Response status: {response.status_code}")
                logger.info(f"[DEBUG] Response headers: {dict(response.headers)}")
                logger.info(f"[DEBUG] Response text: {response.text}")
                response.raise_for_status()
                
                # Get the raw response text first for debugging
                response_text = response.text
                logger.info(f"[DEBUG] Raw API response: {response_text}")
                logger.info(f"[DEBUG] Response headers: {dict(response.headers)}")
                
                try:
                    result = response.json()
                    logger.debug("Successfully parsed JSON response")
                    
                    # Log API usage if available
                    if 'usage' in result:
                        usage = result['usage']
                        logger.debug(
                            f"API usage - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}, "
                            f"Completion tokens: {usage.get('completion_tokens', 'N/A')}, "
                            f"Total tokens: {usage.get('total_tokens', 'N/A')}"
                        )
                    
                    # Extract content from the response
                    content = result.get('choices', [{}])[0].get('message', {}).get('content')
                    if not content:
                        error_msg = "No content in API response"
                        logger.error(f"{error_msg}. Full response: {result}")
                        raise ValueError(error_msg)
                    
                    logger.debug(f"Raw API response content: {content}")
                    
                    try:
                        analysis = json.loads(content)
                        logger.debug("Successfully parsed content as JSON")
                        
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
                        logger.error(f"{error_msg}. Raw response: {response_text}")
                        logger.error(f"Response headers: {dict(response.headers)}")
                        raise ValueError(f"{error_msg}. Raw response: {response_text}") from e
                        
                except Exception as e:
                    error_msg = f"Failed to extract analysis from API response: {str(e)}"
                    logger.error(f"{error_msg}. Raw response: {response_text}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    if 'content' in locals():
                        logger.error(f"Response content: {content}")
                    raise ValueError(f"{error_msg}. Raw response: {response_text}") from e
                    
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
