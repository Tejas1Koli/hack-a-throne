from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseClauseAnalyzer(ABC):
    """Abstract base class for clause analyzers."""
    
    @abstractmethod
    async def analyze_clause(self, clause: str) -> Dict[str, Any]:
        """Analyze a single clause and return the analysis results.
        
        Args:
            clause: The text of the clause to analyze.
            
        Returns:
            Dict containing analysis results with keys: 
            clause, risk_score, explanation, clause_type, safer_version
        """
        pass
