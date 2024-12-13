"""Financial analysis agent."""
from typing import Dict, Any, List
import logging
from ..models.market_insight import MarketInsight

logger = logging.getLogger(__name__)

class FinancialAnalyzerAgent:
    """Agent for analyzing financial aspects of the market."""
    
    def analyze_financials(self, market_data: Dict[str, Any]) -> MarketInsight:
        """Analyze financial aspects of the market."""
        try:
            if not market_data:
                return self._create_empty_insight()

            # Analyze market size and growth
            size_analysis = self._analyze_market_size(market_data)
            
            # Analyze investment trends
            investment_analysis = self._analyze_investments(market_data)
            
            # Analyze revenue potential
            revenue_analysis = self._analyze_revenue_potential(market_data)
            
            # Calculate overall score
            score = self._calculate_financial_score(
                size_analysis,
                investment_analysis,
                revenue_analysis
            )

            # Generate findings
            findings = [
                *size_analysis['findings'],
                *investment_analysis['findings'],
                *revenue_analysis['findings']
            ]

            # Generate recommendations
            recommendations = self._generate_recommendations(
                size_analysis,
                investment_analysis,
                revenue_analysis
            )

            # Determine priority
            priority = self._determine_priority(score)

            return MarketInsight(
                category='financial',
                score=score,
                findings=findings,
                recommendations=recommendations,
                priority=priority,
                metadata={
                    'market_size': size_analysis['metrics'],
                    'investments': investment_analysis['metrics'],
                    'revenue': revenue_analysis['metrics']
                }
            )

        except Exception as e:
            logger.error(f"Error analyzing financials: {str(e)}")
            return self._create_empty_insight()

    def _create_empty_insight(self) -> MarketInsight:
        """Create empty financial insight."""
        return MarketInsight(
            category='financial',
            score=0.0,
            findings=[],
            recommendations=[],
            priority='unknown',
            metadata={}
        )

    def _analyze_market_size(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market size and growth."""
        try:
            findings = []
            metrics = {}
            
            # Get market size data with defaults
            market = data.get('market_size', {})
            current_size = market.get('current', 0)
            projected_size = market.get('projected', 0)
            growth_rate = market.get('growth_rate', 0)
            
            # Calculate metrics safely
            metrics['current_size'] = current_size
            metrics['projected_size'] = projected_size
            metrics['growth_rate'] = growth_rate
            
            # Calculate growth potential safely
            if current_size > 0:
                metrics['growth_potential'] = (projected_size - current_size) / current_size
            else:
                # If current size is 0, use absolute projected size as potential
                metrics['growth_potential'] = projected_size if projected_size > 0 else 0
            
            # Generate findings
            if growth_rate > 0.2:
                findings.append({
                    'aspect': 'market_growth',
                    'finding': f"High market growth rate of {growth_rate*100:.1f}%",
                    'impact': 'positive'
                })
            elif growth_rate < 0:
                findings.append({
                    'aspect': 'market_growth',
                    'finding': f"Market contraction of {abs(growth_rate)*100:.1f}%",
                    'impact': 'negative'
                })
                
            return {
                'findings': findings,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market size: {str(e)}")
            return {'findings': [], 'metrics': {}}

    def _analyze_investments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze investment trends."""
        try:
            findings = []
            metrics = {}
            
            # Get investment data
            investments = data.get('investments', {})
            total_funding = investments.get('total_funding', 0)
            funding_rounds = investments.get('funding_rounds', [])
            major_investors = investments.get('major_investors', [])
            
            # Calculate metrics
            metrics['total_funding'] = total_funding
            metrics['num_rounds'] = len(funding_rounds)
            metrics['avg_round_size'] = total_funding / len(funding_rounds) if funding_rounds else 0
            metrics['num_major_investors'] = len(major_investors)
            
            # Generate findings
            if total_funding > 100000000:  # $100M
                findings.append({
                    'aspect': 'funding',
                    'finding': f"Strong investment interest with ${total_funding/1000000:.1f}M total funding",
                    'impact': 'positive'
                })
                
            if len(major_investors) > 5:
                findings.append({
                    'aspect': 'investors',
                    'finding': f"Strong investor backing with {len(major_investors)} major investors",
                    'impact': 'positive'
                })
                
            return {
                'findings': findings,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing investments: {str(e)}")
            return {'findings': [], 'metrics': {}}

    def _analyze_revenue_potential(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue potential."""
        try:
            findings = []
            metrics = {}
            
            # Get revenue data
            revenue = data.get('revenue', {})
            avg_revenue = revenue.get('average', 0)
            revenue_growth = revenue.get('growth_rate', 0)
            profit_margin = revenue.get('profit_margin', 0)
            
            # Calculate metrics
            metrics['avg_revenue'] = avg_revenue
            metrics['revenue_growth'] = revenue_growth
            metrics['profit_margin'] = profit_margin
            metrics['profitability_score'] = min(1.0, profit_margin / 0.3)  # Normalize to max 30% margin
            
            # Generate findings
            if revenue_growth > 0.3:
                findings.append({
                    'aspect': 'revenue_growth',
                    'finding': f"High revenue growth potential of {revenue_growth*100:.1f}%",
                    'impact': 'positive'
                })
                
            if profit_margin > 0.2:
                findings.append({
                    'aspect': 'profitability',
                    'finding': f"Strong profit margin of {profit_margin*100:.1f}%",
                    'impact': 'positive'
                })
                
            return {
                'findings': findings,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing revenue potential: {str(e)}")
            return {'findings': [], 'metrics': {}}

    def _calculate_financial_score(self, size_analysis: Dict[str, Any],
                                investment_analysis: Dict[str, Any],
                                revenue_analysis: Dict[str, Any]) -> float:
        """Calculate overall financial score."""
        try:
            scores = []
            
            # Market size score
            size_metrics = size_analysis['metrics']
            if size_metrics:
                growth_score = min(1.0, size_metrics.get('growth_rate', 0) / 0.3)
                scores.append(growth_score)
            
            # Investment score
            inv_metrics = investment_analysis['metrics']
            if inv_metrics:
                funding_score = min(1.0, inv_metrics.get('total_funding', 0) / 100000000)
                scores.append(funding_score)
            
            # Revenue score
            rev_metrics = revenue_analysis['metrics']
            if rev_metrics:
                revenue_score = rev_metrics.get('profitability_score', 0)
                scores.append(revenue_score)
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating financial score: {str(e)}")
            return 0.0

    def _generate_recommendations(self, size_analysis: Dict[str, Any],
                               investment_analysis: Dict[str, Any],
                               revenue_analysis: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations."""
        try:
            recommendations = []
            
            # Market size recommendations
            size_metrics = size_analysis['metrics']
            if size_metrics.get('growth_rate', 0) > 0.2:
                recommendations.append("Capitalize on high market growth with aggressive expansion")
            
            # Investment recommendations
            inv_metrics = investment_analysis['metrics']
            if inv_metrics.get('total_funding', 0) > 50000000:
                recommendations.append("Leverage strong investment climate for funding opportunities")
            
            # Revenue recommendations
            rev_metrics = revenue_analysis['metrics']
            if rev_metrics.get('profit_margin', 0) < 0.15:
                recommendations.append("Focus on improving profit margins through operational efficiency")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _determine_priority(self, score: float) -> str:
        """Determine priority based on financial score."""
        try:
            if score < 0.3:
                return 'low'
            elif score < 0.6:
                return 'medium'
            else:
                return 'high'
        except Exception:
            return 'unknown' 