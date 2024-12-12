"""Main market analyzer module."""
from typing import Dict, Any, List
import logging
from .models.market_insight import MarketAnalysis
from .agents.competitor_agent import CompetitorAnalyzerAgent
from .agents.trend_agent import TrendAnalyzerAgent
from .agents.financial_agent import FinancialAnalyzerAgent

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Main class for market analysis."""

    def __init__(self):
        """Initialize market analyzer with specialized agents."""
        self.competitor_agent = CompetitorAnalyzerAgent()
        self.trend_agent = TrendAnalyzerAgent()
        self.financial_agent = FinancialAnalyzerAgent()

    def analyze_market(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """
        Perform comprehensive market analysis.
        
        Args:
            market_data: Dictionary containing market data including competitors,
                        trends, and financial information
            
        Returns:
            MarketAnalysis object containing complete analysis
        """
        try:
            if not market_data:
                return self._create_empty_analysis()

            # Analyze competitors
            competitors = []
            for comp_url, comp_data in market_data.get('competitors', {}).items():
                competitor = self.competitor_agent.analyze_competitor(comp_url, comp_data)
                competitors.append(competitor)

            # Analyze market trends
            trends = self.trend_agent.analyze_trends(market_data)

            # Analyze financials
            financials = self.financial_agent.analyze_financials(market_data)

            # Extract market size and growth
            market_size = market_data.get('market_size', {}).get('current', 0)
            growth_potential = market_data.get('market_size', {}).get('growth_rate', 0)

            # Identify opportunities and threats
            opportunities = self._identify_opportunities(competitors, trends, financials)
            threats = self._identify_threats(competitors, trends, financials)

            # Identify target segments
            target_segments = self._identify_target_segments(market_data)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                competitors,
                trends,
                financials,
                opportunities,
                threats
            )

            return MarketAnalysis(
                market_size=market_size,
                growth_potential=growth_potential,
                competitors=competitors,
                trends=trends,
                opportunities=opportunities,
                threats=threats,
                target_segments=target_segments,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return self._create_empty_analysis()

    def _create_empty_analysis(self) -> MarketAnalysis:
        """Create empty market analysis."""
        return MarketAnalysis(
            market_size=0.0,
            growth_potential=0.0,
            competitors=[],
            trends=[],
            opportunities=[],
            threats=[],
            target_segments=[],
            recommendations=[]
        )

    def _identify_opportunities(self, competitors: List[Any], trends: List[Any], 
                              financials: Any) -> List[Dict[str, Any]]:
        """Identify market opportunities."""
        try:
            opportunities = []

            # Check competitor gaps
            competitor_features = set()
            for comp in competitors:
                competitor_features.update(comp.key_features)

            if competitor_features:
                opportunities.append({
                    'type': 'feature_gap',
                    'description': 'Potential for feature differentiation',
                    'details': list(competitor_features)
                })

            # Check market trends
            for trend in trends:
                if trend.impact_score > 0.7 and trend.confidence > 0.6:
                    opportunities.append({
                        'type': 'trend_opportunity',
                        'description': trend.description,
                        'impact_score': trend.impact_score
                    })

            # Check financial opportunities
            if financials.score > 0.7:
                opportunities.append({
                    'type': 'financial_opportunity',
                    'description': 'Strong financial growth potential',
                    'score': financials.score
                })

            return opportunities

        except Exception as e:
            logger.error(f"Error identifying opportunities: {str(e)}")
            return []

    def _identify_threats(self, competitors: List[Any], trends: List[Any], 
                         financials: Any) -> List[Dict[str, Any]]:
        """Identify market threats."""
        try:
            threats = []

            # Check competitor threats
            for comp in competitors:
                if comp.market_share > 0.3:
                    threats.append({
                        'type': 'competitor_threat',
                        'description': f"Strong competitor: {comp.name}",
                        'market_share': comp.market_share
                    })

            # Check trend threats
            for trend in trends:
                if trend.impact_score < 0.3 and trend.confidence > 0.6:
                    threats.append({
                        'type': 'trend_threat',
                        'description': trend.description,
                        'impact_score': trend.impact_score
                    })

            # Check financial threats
            if financials.score < 0.3:
                threats.append({
                    'type': 'financial_threat',
                    'description': 'Poor financial outlook',
                    'score': financials.score
                })

            return threats

        except Exception as e:
            logger.error(f"Error identifying threats: {str(e)}")
            return []

    def _identify_target_segments(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify target market segments."""
        try:
            segments = []
            segment_data = market_data.get('segments', {})

            for segment_name, segment_info in segment_data.items():
                size = segment_info.get('size', 0)
                growth = segment_info.get('growth', 0)
                needs = segment_info.get('needs', [])

                if size > 0 and growth > 0:
                    segments.append({
                        'name': segment_name,
                        'size': size,
                        'growth': growth,
                        'needs': needs,
                        'attractiveness': self._calculate_segment_attractiveness(
                            size,
                            growth,
                            len(needs)
                        )
                    })

            # Sort segments by attractiveness
            return sorted(segments, key=lambda x: x['attractiveness'], reverse=True)

        except Exception as e:
            logger.error(f"Error identifying target segments: {str(e)}")
            return []

    def _calculate_segment_attractiveness(self, size: float, growth: float, 
                                       num_needs: int) -> float:
        """Calculate segment attractiveness score."""
        try:
            # Normalize factors
            size_score = min(1.0, size / 1000000)  # Normalize to $1M
            growth_score = min(1.0, growth / 0.5)  # Normalize to 50% growth
            needs_score = min(1.0, num_needs / 10)  # Normalize to 10 needs

            # Weight factors
            weights = {
                'size': 0.4,
                'growth': 0.4,
                'needs': 0.2
            }

            return (
                size_score * weights['size'] +
                growth_score * weights['growth'] +
                needs_score * weights['needs']
            )

        except Exception as e:
            logger.error(f"Error calculating segment attractiveness: {str(e)}")
            return 0.0

    def _generate_recommendations(self, competitors: List[Any], trends: List[Any],
                               financials: Any, opportunities: List[Dict[str, Any]],
                               threats: List[Dict[str, Any]]) -> List[str]:
        """Generate market recommendations."""
        try:
            recommendations = []

            # Add competitor-based recommendations
            if competitors:
                strong_competitors = [c for c in competitors if c.market_share > 0.2]
                if strong_competitors:
                    recommendations.append(
                        f"Focus on differentiation from {len(strong_competitors)} strong competitors"
                    )

            # Add trend-based recommendations
            positive_trends = [t for t in trends if t.impact_score > 0.6]
            if positive_trends:
                recommendations.append(
                    f"Capitalize on {len(positive_trends)} positive market trends"
                )

            # Add financial recommendations
            if financials.score > 0.7:
                recommendations.append(
                    "Leverage strong financial position for market expansion"
                )
            elif financials.score < 0.3:
                recommendations.append(
                    "Focus on improving financial metrics before expansion"
                )

            # Add opportunity-based recommendations
            if opportunities:
                recommendations.append(
                    f"Pursue {len(opportunities)} identified market opportunities"
                )

            # Add threat mitigation recommendations
            if threats:
                recommendations.append(
                    f"Address {len(threats)} identified market threats"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return [] 