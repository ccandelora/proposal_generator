"""Content generation models."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    """Types of content that can be generated."""
    PROPOSAL = "proposal"
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_SPEC = "technical_spec"
    MARKET_ANALYSIS = "market_analysis"
    RECOMMENDATIONS = "recommendations"

class ContentTone(Enum):
    """Tone options for generated content."""
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"
    FORMAL = "formal"

@dataclass
class ContentTemplate:
    """Template for content generation."""
    template_type: ContentType
    sections: List[str]
    required_data: List[str]
    optional_data: List[str]
    tone: ContentTone
    max_length: Optional[int] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'template_type': self.template_type.value,
            'sections': self.sections,
            'required_data': self.required_data,
            'optional_data': self.optional_data,
            'tone': self.tone.value,
            'max_length': self.max_length,
            'metadata': self.metadata
        }

@dataclass
class ContentSection:
    """Generated content section."""
    title: str
    content: str
    keywords: List[str]
    metrics: Dict[str, Any]
    references: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'content': self.content,
            'keywords': self.keywords,
            'metrics': self.metrics,
            'references': self.references
        }

@dataclass
class GeneratedContent:
    """Complete generated content."""
    content_type: ContentType
    title: str
    sections: List[ContentSection]
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    summary: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content_type': self.content_type.value,
            'title': self.title,
            'sections': [section.to_dict() for section in self.sections],
            'metadata': self.metadata,
            'metrics': self.metrics,
            'summary': self.summary,
            'recommendations': self.recommendations
        }

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'word_count': self.word_count,
            'readability_score': self.readability_score,
            'keyword_density': self.keyword_density,
            'sentiment_score': self.sentiment_score,
            'technical_complexity': self.technical_complexity,
            'uniqueness_score': self.uniqueness_score,
            'quality_score': self.quality_score
        }

@dataclass
class ContentRequest:
    """Request for content generation."""
    content_type: ContentType
    target_audience: str
    tone: ContentTone
    key_points: List[str]
    keywords: List[str]
    max_length: Optional[int] = None
    required_sections: Optional[List[str]] = None
    reference_data: Optional[Dict[str, Any]] = None
    style_guide: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content_type': self.content_type.value,
            'target_audience': self.target_audience,
            'tone': self.tone.value,
            'key_points': self.key_points,
            'keywords': self.keywords,
            'max_length': self.max_length,
            'required_sections': self.required_sections,
            'reference_data': self.reference_data,
            'style_guide': self.style_guide
        } 