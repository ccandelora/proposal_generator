"""Backlink analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.seo_insight import SEOInsight

logger = logging.getLogger(__name__)

class BacklinkAnalyzerAgent:
    """Agent for analyzing backlink profiles."""
    
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
 