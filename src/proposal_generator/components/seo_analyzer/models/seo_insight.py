"""SEO Insight model."""
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SEOInsight:
    """Data class for SEO analysis insights."""
    category: str
    score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    priority: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'category': self.category,
            'score': self.score,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'priority': self.priority,
            'metadata': self.metadata
        } 