"""Market trend analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.market_insight import MarketTrend

logger = logging.getLogger(__name__)

class TrendAnalyzerAgent:
    """Agent for analyzing market trends."""
    
    def analyze_trends(self, market_data: Dict[str, Any]) -> List[MarketTrend]:
        """Analyze market trends from provided data."""
        try:
            if not market_data:
                return []

            trends = []
            
            # Analyze industry trends
            industry_trends = self._analyze_industry_trends(market_data)
            trends.extend(industry_trends)
            
            # Analyze technology trends
            tech_trends = self._analyze_technology_trends(market_data)
            trends.extend(tech_trends)
            
            # Analyze consumer trends
            consumer_trends = self._analyze_consumer_trends(market_data)
            trends.extend(consumer_trends)
            
            return trends

        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return []

    def _analyze_industry_trends(self, data: Dict[str, Any]) -> List[MarketTrend]:
        """Analyze industry-specific trends."""
        try:
            trends = []
            industry_data = data.get('industry', {})
            
            # Growth trends
            growth_data = industry_data.get('growth', {})
            if growth_data:
                trends.append(MarketTrend(
                    trend_type='industry_growth',
                    description=self._generate_growth_description(growth_data),
                    impact_score=growth_data.get('impact', 0.0),
                    growth_rate=growth_data.get('rate', 0.0),
                    confidence=growth_data.get('confidence', 0.0),
                    supporting_data=growth_data
                ))
            
            # Innovation trends
            innovation_data = industry_data.get('innovation', {})
            if innovation_data:
                trends.append(MarketTrend(
                    trend_type='industry_innovation',
                    description=self._generate_innovation_description(innovation_data),
                    impact_score=innovation_data.get('impact', 0.0),
                    growth_rate=innovation_data.get('adoption_rate', 0.0),
                    confidence=innovation_data.get('confidence', 0.0),
                    supporting_data=innovation_data
                ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing industry trends: {str(e)}")
            return []

    def _analyze_technology_trends(self, data: Dict[str, Any]) -> List[MarketTrend]:
        """Analyze technology trends."""
        try:
            trends = []
            tech_data = data.get('technology', {})
            
            # Emerging technologies
            emerging_tech = tech_data.get('emerging', {})
            for tech_name, tech_info in emerging_tech.items():
                trends.append(MarketTrend(
                    trend_type='emerging_technology',
                    description=f"Emerging technology: {tech_name}",
                    impact_score=tech_info.get('impact', 0.0),
                    growth_rate=tech_info.get('adoption_rate', 0.0),
                    confidence=tech_info.get('confidence', 0.0),
                    supporting_data=tech_info
                ))
            
            # Technology adoption trends
            adoption_data = tech_data.get('adoption', {})
            if adoption_data:
                trends.append(MarketTrend(
                    trend_type='technology_adoption',
                    description=self._generate_adoption_description(adoption_data),
                    impact_score=adoption_data.get('impact', 0.0),
                    growth_rate=adoption_data.get('rate', 0.0),
                    confidence=adoption_data.get('confidence', 0.0),
                    supporting_data=adoption_data
                ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing technology trends: {str(e)}")
            return []

    def _analyze_consumer_trends(self, data: Dict[str, Any]) -> List[MarketTrend]:
        """Analyze consumer behavior trends."""
        try:
            trends = []
            consumer_data = data.get('consumer', {})
            
            # Preference trends
            preferences = consumer_data.get('preferences', {})
            for pref_name, pref_info in preferences.items():
                trends.append(MarketTrend(
                    trend_type='consumer_preference',
                    description=f"Consumer preference: {pref_name}",
                    impact_score=pref_info.get('impact', 0.0),
                    growth_rate=pref_info.get('growth_rate', 0.0),
                    confidence=pref_info.get('confidence', 0.0),
                    supporting_data=pref_info
                ))
            
            # Behavior trends
            behavior_data = consumer_data.get('behavior', {})
            if behavior_data:
                trends.append(MarketTrend(
                    trend_type='consumer_behavior',
                    description=self._generate_behavior_description(behavior_data),
                    impact_score=behavior_data.get('impact', 0.0),
                    growth_rate=behavior_data.get('rate', 0.0),
                    confidence=behavior_data.get('confidence', 0.0),
                    supporting_data=behavior_data
                ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing consumer trends: {str(e)}")
            return []

    def _generate_growth_description(self, data: Dict[str, Any]) -> str:
        """Generate description for growth trends."""
        try:
            rate = data.get('rate', 0) * 100
            direction = 'growth' if rate > 0 else 'decline'
            return f"Industry showing {abs(rate):.1f}% annual {direction}"
        except Exception:
            return "Industry growth trend"

    def _generate_innovation_description(self, data: Dict[str, Any]) -> str:
        """Generate description for innovation trends."""
        try:
            focus_areas = data.get('focus_areas', [])
            if focus_areas:
                areas = ', '.join(focus_areas[:3])
                return f"Innovation focused on: {areas}"
            return "Industry innovation trend"
        except Exception:
            return "Industry innovation trend"

    def _generate_adoption_description(self, data: Dict[str, Any]) -> str:
        """Generate description for technology adoption trends."""
        try:
            rate = data.get('rate', 0) * 100
            tech_type = data.get('technology_type', 'new technology')
            return f"{tech_type} adoption rate: {rate:.1f}%"
        except Exception:
            return "Technology adoption trend"

    def _generate_behavior_description(self, data: Dict[str, Any]) -> str:
        """Generate description for consumer behavior trends."""
        try:
            key_changes = data.get('key_changes', [])
            if key_changes:
                changes = ', '.join(key_changes[:2])
                return f"Consumer behavior shifts: {changes}"
            return "Consumer behavior trend"
        except Exception:
            return "Consumer behavior trend" 