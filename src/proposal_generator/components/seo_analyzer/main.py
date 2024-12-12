"""Main SEO analyzer module."""
from typing import Dict, Any
import logging
from .models.seo_insight import SEOInsight
from .agents.technical_agent import TechnicalSEOAgent
from .agents.content_agent import ContentSEOAgent
from .agents.backlink_agent import BacklinkAnalyzerAgent

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    """Main class for SEO analysis."""

    def __init__(self):
        """Initialize SEO analyzer with specialized agents."""
        self.technical_agent = TechnicalSEOAgent()
        self.content_agent = ContentSEOAgent()
        self.backlink_agent = BacklinkAnalyzerAgent()

    def analyze_seo(self, url: str, page_data: Dict[str, Any], 
                   backlink_data: Dict[str, Any]) -> Dict[str, SEOInsight]:
        """
        Perform comprehensive SEO analysis.
        
        Args:
            url: Website URL to analyze
            page_data: Technical and content data
            backlink_data: Backlink profile data
            
        Returns:
            Dict containing analysis results from all agents
        """
        try:
            if not url:
                raise ValueError("Invalid URL")
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL format")

            return {
                'technical': self.technical_agent.analyze_technical_seo(url, page_data),
                'content': self.content_agent.analyze_content_seo(url, page_data),
                'backlinks': self.backlink_agent.analyze_backlinks(url, backlink_data)
            }

        except Exception as e:
            logger.error(f"Error in SEO analysis: {str(e)}")
            empty_insight = SEOInsight(
                category='error',
                score=0.0,
                findings=[],
                recommendations=[],
                priority='unknown',
                metadata={'error': str(e)}
            )
            return {
                'technical': empty_insight,
                'content': empty_insight,
                'backlinks': empty_insight
            } 