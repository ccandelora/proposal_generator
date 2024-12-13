"""Content models for proposal generation."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

class ContentType(Enum):
    """Types of content that can be generated."""
    PROPOSAL = "proposal"
    TECHNICAL_SPEC = "technical_spec"
    MARKET_ANALYSIS = "market_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"

class ContentTone(Enum):
    """Tones that can be applied to content."""
    FORMAL = "formal"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"

@dataclass
class ContentRequest:
    """Request for content generation."""
    content_type: ContentType
    topic: str
    target_audience: str
    tone: ContentTone
    key_points: List[str]
    keywords: List[str]
    max_length: Optional[int] = None
    required_sections: Optional[List[str]] = None
    reference_data: Optional[Dict[str, Any]] = None

@dataclass
class ContentSection:
    """Section of generated content."""
    title: str
    content: str
    keywords: List[str]
    metrics: Dict[str, Any]
    references: List[Dict[str, Any]]

@dataclass
class ContentMetrics:
    """Metrics for generated content."""
    word_count: int
    readability_score: float
    keyword_density: Dict[str, float]
    sentiment_score: float
    technical_complexity: float
    uniqueness_score: float
    quality_score: float

@dataclass
class GeneratedContent:
    """Generated content with metadata."""
    content_type: ContentType
    title: str
    sections: List[ContentSection]
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    summary: str
    recommendations: List[str] 