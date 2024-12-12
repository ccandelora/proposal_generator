"""Technical SEO analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.seo_insight import SEOInsight

logger = logging.getLogger(__name__)

class TechnicalSEOAgent:
    """Agent for analyzing technical SEO aspects."""
    
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