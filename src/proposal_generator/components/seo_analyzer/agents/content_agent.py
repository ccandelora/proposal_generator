"""Content SEO analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.seo_insight import SEOInsight

logger = logging.getLogger(__name__)

class ContentSEOAgent:
    """Agent for analyzing content SEO aspects."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def analyze_content_seo(self, url: str, page_data: Dict[str, Any]) -> SEOInsight:
        """Analyze content SEO aspects."""
        if self.progress_callback:
            self.progress_callback("Analyzing SEO content...", 0)
            
        try:
            if not page_data:
                return SEOInsight(
                    category='content_seo',
                    score=0.0,
                    findings=[],
                    recommendations=[],
                    priority='unknown',
                    metadata={}
                )

            # Analyze keyword usage
            keyword_analysis = self._analyze_keyword_usage(page_data)
            
            # Analyze content structure
            structure_analysis = self._analyze_content_structure(page_data)
            
            # Analyze content quality
            quality_analysis = self._analyze_content_quality(page_data)
            
            # Calculate overall score
            score = (keyword_analysis['score'] + structure_analysis['score'] + quality_analysis['score']) / 3
            
            # Determine priority
            priority = 'high' if score < 0.7 else 'medium' if score < 0.9 else 'low'
            
            return SEOInsight(
                category='content_seo',
                score=score,
                findings=[
                    *keyword_analysis['findings'],
                    *structure_analysis['findings'],
                    *quality_analysis['findings']
                ],
                recommendations=[
                    *keyword_analysis['recommendations'],
                    *structure_analysis['recommendations'],
                    *quality_analysis['recommendations']
                ],
                priority=priority,
                metadata={
                    'keyword_metrics': keyword_analysis['metrics'],
                    'structure_metrics': structure_analysis['metrics'],
                    'quality_metrics': quality_analysis['metrics']
                }
            )
            
        except Exception as e:
            logger.error(f"Error in content SEO analysis: {str(e)}")
            return SEOInsight(
                category='content_seo',
                score=0.0,
                findings=[],
                recommendations=[],
                priority='unknown',
                metadata={}
            )
        
        if self.progress_callback:
            self.progress_callback("SEO analysis complete", 100)

    def _analyze_keyword_usage(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze keyword usage in content."""
        try:
            keywords = page_data.get('keywords', {})
            metrics = {
                'primary_keyword': keywords.get('primary', {}),
                'secondary_keywords': keywords.get('secondary', []),
                'density': keywords.get('density', {}),
                'placement': keywords.get('placement', {})
            }
            
            findings = []
            recommendations = []
            score = 1.0
            
            # Check primary keyword
            if not metrics['primary_keyword'].get('present'):
                findings.append({
                    'issue': 'Missing primary keyword',
                    'severity': 'high'
                })
                recommendations.append('Add primary keyword to content')
                score *= 0.7
                
            return {
                'findings': findings,
                'recommendations': recommendations,
                'metrics': metrics,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing keyword usage: {str(e)}")
            return {
                'findings': [],
                'recommendations': [],
                'metrics': {},
                'score': 0.0
            }

    def _analyze_content_structure(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content structure."""
        try:
            structure = page_data.get('structure', {})
            metrics = {
                'headings': structure.get('headings', {}),
                'paragraphs': structure.get('paragraphs', {}),
                'lists': structure.get('lists', {}),
                'images': structure.get('images', {})
            }
            
            findings = []
            recommendations = []
            score = 1.0
            
            if metrics['headings'].get('multiple_h1', False):
                findings.append({
                    'issue': 'Multiple H1 tags',
                    'severity': 'medium'
                })
                recommendations.append('Use only one H1 tag per page')
                score *= 0.8
                
            return {
                'findings': findings,
                'recommendations': recommendations,
                'metrics': metrics,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content structure: {str(e)}")
            return {
                'findings': [],
                'recommendations': [],
                'metrics': {},
                'score': 0.0
            }

    def _analyze_content_quality(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality."""
        try:
            quality = page_data.get('quality', {})
            metrics = {
                'readability': quality.get('readability', {}),
                'engagement': quality.get('engagement', {}),
                'uniqueness': quality.get('uniqueness', {}),
                'freshness': quality.get('freshness', {})
            }
            
            findings = []
            recommendations = []
            score = 1.0
            
            if metrics['readability'].get('score', 100) < 60:
                findings.append({
                    'issue': 'Low readability score',
                    'severity': 'medium'
                })
                recommendations.append('Improve content readability')
                score *= 0.8
                
            return {
                'findings': findings,
                'recommendations': recommendations,
                'metrics': metrics,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content quality: {str(e)}")
            return {
                'findings': [],
                'recommendations': [],
                'metrics': {},
                'score': 0.0
            }
