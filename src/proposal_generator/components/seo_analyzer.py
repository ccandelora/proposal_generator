"""SEO Analyzer module."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SEOInsight:
    """Data class for SEO analysis insights."""
    category: str
    score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    priority: str
    metadata: Dict[str, Any]

class TechnicalSEOAgent:
    """Agent for analyzing technical SEO aspects."""
    
    def __init__(self, progress_callback=None):
        """Initialize SEO analyzer with specialized agents."""
        self.progress_callback = progress_callback
    
    def analyze_technical_seo(self, url: str, page_data: Dict[str, Any]) -> SEOInsight:
        """Analyze technical SEO aspects."""
        try:
            if not page_data:
                return SEOInsight(
                    category='technical_seo',
                    score=0.0,
                    findings=[],
                    recommendations=[],
                    priority='unknown',
                    metadata={}
                )

            # Analyze different aspects
            speed_analysis = self._analyze_page_speed(page_data)
            mobile_analysis = self._analyze_mobile_friendliness(page_data)
            technical_elements = self._analyze_technical_elements(page_data)

            # Calculate overall score
            score = self._calculate_technical_score(
                speed_analysis,
                mobile_analysis,
                technical_elements
            )

            # Determine priority
            priority = self._determine_priority(
                speed_analysis['score'],
                mobile_analysis['score'],
                technical_elements['score']
            )

            # Generate recommendations
            recommendations = self._generate_technical_recommendations(
                speed_analysis,
                mobile_analysis,
                technical_elements
            )

            return SEOInsight(
                category='technical_seo',
                score=score,
                findings=[
                    *speed_analysis['findings'],
                    *mobile_analysis['findings'],
                    *technical_elements['findings']
                ],
                recommendations=recommendations,
                priority=priority,
                metadata={
                    'speed_metrics': speed_analysis['metrics'],
                    'mobile_metrics': mobile_analysis['metrics'],
                    'technical_elements': technical_elements['elements']
                }
            )

        except Exception as e:
            logger.error(f"Error in technical SEO analysis: {str(e)}")
            return SEOInsight(
                category='technical_seo',
                score=0.0,
                findings=[],
                recommendations=[],
                priority='unknown',
                metadata={}
            )

    def _analyze_page_speed(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page speed metrics."""
        try:
            performance = page_data.get('performance', {})
            metrics = {
                'fcp': performance.get('first_contentful_paint', 0),
                'lcp': performance.get('largest_contentful_paint', 0),
                'ttfb': performance.get('time_to_first_byte', 0),
                'tti': performance.get('time_to_interactive', 0)
            }
            
            score = self._calculate_speed_score(metrics)
            findings = []
            
            if metrics['fcp'] > 1800:
                findings.append({
                    'issue': 'Slow First Contentful Paint',
                    'impact': 'high',
                    'recommendation': 'Optimize critical rendering path'
                })
                
            return {
                'findings': findings,
                'metrics': metrics,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing page speed: {str(e)}")
            return {'findings': [], 'metrics': {}, 'score': 0.0}

    def _analyze_mobile_friendliness(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mobile friendliness."""
        try:
            mobile = page_data.get('mobile', {})
            metrics = {
                'has_viewport': mobile.get('has_viewport_meta', False),
                'text_size': mobile.get('text_size', {}),
                'tap_targets': mobile.get('tap_targets', {})
            }
            
            score = self._calculate_mobile_score(metrics)
            findings = []
            
            if not metrics['has_viewport']:
                findings.append({
                    'issue': 'Missing viewport meta tag',
                    'impact': 'critical',
                    'recommendation': 'Add viewport meta tag'
                })
                
            return {
                'findings': findings,
                'metrics': metrics,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing mobile friendliness: {str(e)}")
            return {'findings': [], 'metrics': {}, 'score': 0.0}

    def _analyze_technical_elements(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical elements."""
        try:
            meta = page_data.get('meta', {})
            elements = {
                'title': meta.get('title', {}),
                'description': meta.get('description', {}),
                'robots': meta.get('robots', {}),
                'canonical': meta.get('canonical', {})
            }
            
            findings = []
            score = 1.0
            
            if not elements['title'].get('present'):
                findings.append({
                    'issue': 'Missing title tag',
                    'impact': 'high',
                    'recommendation': 'Add title tag'
                })
                score *= 0.8
                
            return {
                'findings': findings,
                'elements': elements,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical elements: {str(e)}")
            return {'findings': [], 'elements': {}, 'score': 0.0}

    def _calculate_technical_score(self, speed: Dict[str, Any], mobile: Dict[str, Any], 
                                 technical: Dict[str, Any]) -> float:
        """Calculate overall technical score."""
        try:
            weights = {'speed': 0.4, 'mobile': 0.4, 'technical': 0.2}
            return (
                speed['score'] * weights['speed'] +
                mobile['score'] * weights['mobile'] +
                technical['score'] * weights['technical']
            )
        except Exception:
            return 0.0

    def _calculate_speed_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate speed score."""
        try:
            fcp_score = 1.0 if metrics['fcp'] < 1800 else 0.5
            lcp_score = 1.0 if metrics['lcp'] < 2500 else 0.5
            return (fcp_score + lcp_score) / 2
        except Exception:
            return 0.0

    def _calculate_mobile_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate mobile friendliness score."""
        try:
            base_score = 1.0
            if not metrics['has_viewport']:
                base_score *= 0.5
            if metrics['text_size'].get('too_small', False):
                base_score *= 0.8
            if metrics['tap_targets'].get('too_close', False):
                base_score *= 0.8
            return base_score
        except Exception:
            return 0.0

    def _determine_priority(self, speed_score: float, mobile_score: float, 
                          technical_score: float) -> str:
        """Determine priority based on scores."""
        try:
            avg_score = (speed_score + mobile_score + technical_score) / 3
            if avg_score < 0.5:
                return 'critical'
            elif avg_score < 0.7:
                return 'high'
            elif avg_score < 0.9:
                return 'medium'
            else:
                return 'low'
        except Exception:
            return 'unknown'

    def _generate_technical_recommendations(self, speed: Dict[str, Any], 
                                         mobile: Dict[str, Any],
                                         technical: Dict[str, Any]) -> List[str]:
        """Generate technical recommendations."""
        try:
            recommendations = []
            for analysis in [speed, mobile, technical]:
                for finding in analysis.get('findings', []):
                    if finding.get('impact') in ['critical', 'high']:
                        recommendations.append(finding.get('recommendation'))
            return recommendations
        except Exception:
            return []

class ContentSEOAgent:
    """Agent for analyzing content SEO aspects."""
    
    def __init__(self, progress_callback=None):
        """Initialize SEO analyzer with specialized agents."""
        self.progress_callback = progress_callback
    
    def analyze_content_seo(self, url: str, page_data: Dict[str, Any]) -> SEOInsight:
        """Analyze content SEO aspects."""
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

class BacklinkAnalyzerAgent:
    """Agent for analyzing backlink profiles."""
    
    def __init__(self, progress_callback=None):
        """Initialize SEO analyzer with specialized agents."""
        self.progress_callback = progress_callback
    
    def analyze_backlinks(self, url: str, backlink_data: Dict[str, Any]) -> SEOInsight:
        """Analyze backlink profile."""
        try:
            if not backlink_data:
                return SEOInsight(
                    category='backlinks',
                    score=0.0,
                    findings=[],
                    recommendations=[],
                    priority='unknown',
                    metadata={}
                )

            profile = backlink_data.get('profile', {})
            quality = backlink_data.get('quality', {})
            competitors = backlink_data.get('competitors', {})

            # Calculate metrics
            metrics = {
                'total_backlinks': profile.get('total', 0),
                'referring_domains': profile.get('referring_domains', 0),
                'authority_score': quality.get('authority', {}).get('high_authority', 0),
                'spam_score': quality.get('spam_score', {}).get('average', 0),
                'competitor_gap': competitors.get('link_gap', {}).get('total', 0)
            }

            # Generate findings
            findings = []
            if metrics['spam_score'] > 20:
                findings.append({
                    'issue': 'High spam score in backlink profile',
                    'severity': 'high'
                })

            # Calculate score
            score = self._calculate_backlink_score(metrics)

            # Generate recommendations
            recommendations = self._generate_backlink_recommendations(metrics, findings)

            # Determine priority
            priority = 'high' if score < 0.6 else 'medium' if score < 0.8 else 'low'

            return SEOInsight(
                category='backlinks',
                score=score,
                findings=findings,
                recommendations=recommendations,
                priority=priority,
                metadata=metrics
            )

        except Exception as e:
            logger.error(f"Error analyzing backlinks: {str(e)}")
            return SEOInsight(
                category='backlinks',
                score=0.0,
                findings=[],
                recommendations=[],
                priority='unknown',
                metadata={}
            )

    def _calculate_backlink_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate backlink profile score."""
        try:
            # Weight different factors
            authority_weight = 0.4
            spam_weight = 0.3
            diversity_weight = 0.3
            
            authority_score = metrics['authority_score']
            spam_score = max(0, 1 - (metrics['spam_score'] / 100))
            diversity_score = min(1, metrics['referring_domains'] / max(metrics['total_backlinks'], 1))
            
            return (
                authority_score * authority_weight +
                spam_score * spam_weight +
                diversity_score * diversity_weight
            )
        except Exception:
            return 0.0

    def _generate_backlink_recommendations(self, metrics: Dict[str, Any], 
                                        findings: List[Dict[str, Any]]) -> List[str]:
        """Generate backlink recommendations."""
        try:
            recommendations = []
            
            if metrics['spam_score'] > 20:
                recommendations.append('Audit and disavow spammy backlinks')
                
            if metrics['authority_score'] < 0.3:
                recommendations.append('Focus on acquiring high-authority backlinks')
                
            if metrics['competitor_gap'] > 1000:
                recommendations.append('Analyze and target competitor backlink sources')
                
            return recommendations
        except Exception:
            return []

class SEOAnalyzer:
    """Main class for SEO analysis."""

    def __init__(self, progress_callback=None):
        """Initialize SEO analyzer with specialized agents."""
        self.progress_callback = progress_callback
        self.technical_agent = TechnicalSEOAgent(progress_callback)
        self.content_agent = ContentSEOAgent(progress_callback)
        self.backlink_agent = BacklinkAnalyzerAgent(progress_callback)

    def analyze_seo(self, url: str, page_data: Dict[str, Any], 
                   backlink_data: Dict[str, Any]) -> Dict[str, SEOInsight]:
        """Perform comprehensive SEO analysis."""
        try:
            if not url:
                raise ValueError("Invalid URL")
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL format")

            if self.progress_callback:
                self.progress_callback("Starting SEO Analysis", 0, completed_steps=[])
            
            # Technical analysis
            if self.progress_callback:
                self.progress_callback("Analyzing Technical SEO...", 20, 
                                     completed_steps=["✓ Initialized analysis"])
            technical = self.technical_agent.analyze_technical_seo(url, page_data)
            
            # Content analysis
            if self.progress_callback:
                self.progress_callback("Analyzing Content SEO...", 40, 
                                     completed_steps=["✓ Initialized analysis",
                                                    "✓ Technical SEO analysis"])
            content = self.content_agent.analyze_content_seo(url, page_data)
            
            # Backlink analysis
            if self.progress_callback:
                self.progress_callback("Analyzing Backlinks...", 60,
                                     completed_steps=["✓ Initialized analysis",
                                                    "✓ Technical SEO analysis",
                                                    "✓ Content SEO analysis"])
            backlinks = self.backlink_agent.analyze_backlinks(url, backlink_data)

            if self.progress_callback:
                self.progress_callback("Compiling SEO Analysis Results...", 80,
                                     completed_steps=["✓ Initialized analysis",
                                                    "✓ Technical SEO analysis",
                                                    "✓ Content SEO analysis",
                                                    "✓ Backlink analysis"])

            results = {
                'technical': technical,
                'content': content,
                'backlinks': backlinks
            }

            if self.progress_callback:
                self.progress_callback("SEO Analysis Complete", 100,
                                     completed_steps=["✓ Initialized analysis",
                                                    "✓ Technical SEO analysis",
                                                    "✓ Content SEO analysis",
                                                    "✓ Backlink analysis",
                                                    "✓ Results compiled"])
            return results

        except Exception as e:
            logger.error(f"Error in SEO analysis: {str(e)}")
            if self.progress_callback:
                self.progress_callback(f"Analysis failed: {str(e)}", 0, 
                                     completed_steps=["⚠ Analysis error"])
            # ... rest of error handling