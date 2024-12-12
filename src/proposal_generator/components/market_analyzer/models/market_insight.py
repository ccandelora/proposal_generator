"""Market insight model."""
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class MarketInsight:
    """Data class for market analysis insights."""
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

@dataclass
class CompetitorInsight:
    """Data class for competitor analysis insights."""
    name: str
    url: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: float
    key_features: List[str]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'url': self.url,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'market_share': self.market_share,
            'key_features': self.key_features,
            'metrics': self.metrics
        }

@dataclass
class MarketTrend:
    """Data class for market trend analysis."""
    trend_type: str
    description: str
    impact_score: float
    growth_rate: float
    confidence: float
    supporting_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'trend_type': self.trend_type,
            'description': self.description,
            'impact_score': self.impact_score,
            'growth_rate': self.growth_rate,
            'confidence': self.confidence,
            'supporting_data': self.supporting_data
        }

@dataclass
class MarketAnalysis:
    """Data class for complete market analysis."""
    market_size: float
    growth_potential: float
    competitors: List[CompetitorInsight]
    trends: List[MarketTrend]
    opportunities: List[Dict[str, Any]]
    threats: List[Dict[str, Any]]
    target_segments: List[Dict[str, Any]]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'market_size': self.market_size,
            'growth_potential': self.growth_potential,
            'competitors': [competitor.to_dict() for competitor in self.competitors],
            'trends': [trend.to_dict() for trend in self.trends],
            'opportunities': self.opportunities,
            'threats': self.threats,
            'target_segments': self.target_segments,
            'recommendations': self.recommendations
        } 