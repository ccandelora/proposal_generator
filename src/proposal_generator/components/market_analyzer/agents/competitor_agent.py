"""Competitor analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.market_insight import CompetitorInsight

logger = logging.getLogger(__name__)

class CompetitorAnalyzerAgent:
    """Agent for analyzing competitors."""
    
    def analyze_competitor(self, url: str, competitor_data: Dict[str, Any]) -> CompetitorInsight:
        """Analyze a competitor's market position and features."""
        try:
            if not competitor_data:
                return self._create_empty_insight(url)

            # Extract basic information
            name = competitor_data.get('name', 'Unknown Competitor')
            market_share = competitor_data.get('market_share', 0.0)
            
            # Analyze strengths and weaknesses
            strengths = self._analyze_strengths(competitor_data)
            weaknesses = self._analyze_weaknesses(competitor_data)
            
            # Analyze features
            key_features = self._analyze_features(competitor_data)
            
            # Calculate metrics
            metrics = self._calculate_metrics(competitor_data)

            return CompetitorInsight(
                name=name,
                url=url,
                strengths=strengths,
                weaknesses=weaknesses,
                market_share=market_share,
                key_features=key_features,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Error analyzing competitor {url}: {str(e)}")
            return self._create_empty_insight(url)

    def _create_empty_insight(self, url: str) -> CompetitorInsight:
        """Create empty competitor insight."""
        return CompetitorInsight(
            name='Unknown Competitor',
            url=url,
            strengths=[],
            weaknesses=[],
            market_share=0.0,
            key_features=[],
            metrics={}
        )

    def _analyze_strengths(self, data: Dict[str, Any]) -> List[str]:
        """Analyze competitor strengths."""
        try:
            strengths = []
            metrics = data.get('metrics', {})
            
            # Check market presence
            if metrics.get('market_share', 0) > 0.2:
                strengths.append('Strong market presence')
                
            # Check brand recognition
            if metrics.get('brand_recognition', 0) > 0.7:
                strengths.append('High brand recognition')
                
            # Check customer satisfaction
            if metrics.get('customer_satisfaction', 0) > 0.8:
                strengths.append('High customer satisfaction')
                
            # Check feature set
            if len(data.get('features', [])) > 10:
                strengths.append('Comprehensive feature set')
                
            return strengths
            
        except Exception as e:
            logger.error(f"Error analyzing strengths: {str(e)}")
            return []

    def _analyze_weaknesses(self, data: Dict[str, Any]) -> List[str]:
        """Analyze competitor weaknesses."""
        try:
            weaknesses = []
            metrics = data.get('metrics', {})
            
            # Check pricing
            if metrics.get('price_competitiveness', 0) < 0.5:
                weaknesses.append('High pricing')
                
            # Check customer support
            if metrics.get('support_rating', 0) < 0.6:
                weaknesses.append('Poor customer support')
                
            # Check technical issues
            if metrics.get('technical_issues', 0) > 0.3:
                weaknesses.append('Frequent technical issues')
                
            # Check feature gaps
            missing_features = data.get('missing_features', [])
            if missing_features:
                weaknesses.append(f"Missing key features: {', '.join(missing_features[:3])}")
                
            return weaknesses
            
        except Exception as e:
            logger.error(f"Error analyzing weaknesses: {str(e)}")
            return []

    def _analyze_features(self, data: Dict[str, Any]) -> List[str]:
        """Analyze competitor features."""
        try:
            features = []
            
            # Get core features
            core_features = data.get('features', {}).get('core', [])
            if core_features:
                features.extend(core_features)
                
            # Get unique features
            unique_features = data.get('features', {}).get('unique', [])
            if unique_features:
                features.extend(unique_features)
                
            # Get premium features
            premium_features = data.get('features', {}).get('premium', [])
            if premium_features:
                features.extend(premium_features)
                
            return list(set(features))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error analyzing features: {str(e)}")
            return []

    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate competitor metrics."""
        try:
            metrics = {}
            raw_metrics = data.get('metrics', {})
            
            # Market metrics
            metrics['market_position'] = {
                'share': raw_metrics.get('market_share', 0),
                'growth': raw_metrics.get('growth_rate', 0),
                'trend': raw_metrics.get('trend', 'stable')
            }
            
            # Performance metrics
            metrics['performance'] = {
                'revenue': raw_metrics.get('revenue', 0),
                'customer_base': raw_metrics.get('customer_base', 0),
                'satisfaction': raw_metrics.get('customer_satisfaction', 0)
            }
            
            # Feature metrics
            metrics['features'] = {
                'count': len(data.get('features', [])),
                'unique_count': len(data.get('features', {}).get('unique', [])),
                'coverage': raw_metrics.get('feature_coverage', 0)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {} 