from typing import Dict, List, Any
from pytrends.request import TrendReq
import yfinance as yf
from newsapi import NewsApiClient
import os
import logging
from .website_analyzer import WebsiteAnalyzer
from .base_agent import BaseAgent
from urllib.parse import urlparse
import time
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class MarketTrendsConfig(BaseModel):
    """Configuration for market trends analyzer."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )

class MarketTrendsAgent(Agent):
    """Agent specialized in analyzing market trends."""
    
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def __init__(self):
        super().__init__(
            name="Market Trends Analyzer",
            role="Market Trends Expert",
            goal="Analyze market trends using Google Trends",
            backstory="""You are an expert at analyzing market trends and
            understanding industry movements.""",
            tools=[
                Tool(
                    name="analyze_trends",
                    func=self.analyze_market_trends,
                    description="Analyze market trends",
                    args_schema=MarketTrendsConfig
                )
            ]
        )
        self.pytrends = TrendReq(hl='en-US', tz=360)

    async def analyze_market_trends(self, practice_area: str, location: str) -> Dict[str, Any]:
        """Analyze market trends for a specific practice area and location."""
        try:
            # Build payload
            self.pytrends.build_payload([practice_area], timeframe='today 12-m', geo=location)
            
            # Get interest over time
            interest_over_time_df = self.pytrends.interest_over_time()
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            # Calculate growth rate safely
            growth_rate = 0
            if not interest_over_time_df.empty:
                start_value = interest_over_time_df.iloc[0][practice_area]
                end_value = interest_over_time_df.iloc[-1][practice_area]
                if start_value > 0:
                    growth_rate = (end_value - start_value) / start_value
                else:
                    # If start value is 0, use absolute end value as growth
                    growth_rate = end_value if end_value > 0 else 0
            
            # Extract top related queries
            top_queries = []
            if practice_area in related_queries and 'top' in related_queries[practice_area]:
                top_queries = related_queries[practice_area]['top']['query'].tolist()[:5]
            
            return {
                'growth_rate': growth_rate,
                'average_interest': interest_over_time_df[practice_area].mean() if not interest_over_time_df.empty else 0,
                'related_topics': top_queries,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {
                'growth_rate': 0,
                'average_interest': 0,
                'related_topics': [],
                'location': location
            }

class NewsAnalyzerConfig(BaseModel):
    """Configuration for news analyzer."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )

class NewsAnalyzerAgent(Agent):
    """Agent specialized in analyzing news and media coverage."""
    
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def __init__(self):
        super().__init__(
            name="News Analyzer",
            role="News Analysis Expert",
            goal="Analyze news and media coverage",
            backstory="""You are an expert at analyzing news coverage and
            media presence in the legal industry.""",
            tools=[
                Tool(
                    name="analyze_news",
                    func=self.analyze_news,
                    description="Analyze news coverage",
                    args_schema=NewsAnalyzerConfig
                )
            ]
        )
        self.news_api = None  # Initialize in analyze_news to allow mocking

    async def analyze_news(self, practice_area: str, location: str) -> Dict[str, Any]:
        """Analyze news coverage for a specific practice area and location."""
        try:
            if not self.news_api:
                self.news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY', 'your-api-key'))
            
            # Build query
            query = f"{practice_area} law firm {location}"
            
            # Get news articles
            news_response = self.news_api.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            
            if 'status' in news_response and news_response['status'] == 'error':
                raise Exception(news_response.get('message', 'News API error'))
            
            # Process articles
            articles = news_response.get('articles', [])
            
            # Extract insights
            sentiment_scores = []
            topics = []
            
            for article in articles:
                # Extract topics from title and description
                title = article.get('title', '')
                description = article.get('description', '')
                content = f"{title} {description}"
                
                # Simple sentiment analysis (you might want to use a proper NLP library)
                sentiment = 0.5  # Neutral by default
                if any(word in content.lower() for word in ['growth', 'success', 'positive', 'increase']):
                    sentiment = 0.8
                elif any(word in content.lower() for word in ['decline', 'negative', 'decrease', 'fail']):
                    sentiment = 0.2
                
                sentiment_scores.append(sentiment)
                
                # Extract topics (simple keyword matching)
                if 'merger' in content.lower() or 'acquisition' in content.lower():
                    topics.append('M&A')
                if 'technology' in content.lower() or 'digital' in content.lower():
                    topics.append('Technology')
                if 'expansion' in content.lower() or 'growth' in content.lower():
                    topics.append('Growth')
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
            
            # Get unique topics
            unique_topics = list(set(topics))
            
            return {
                'sentiment': round(avg_sentiment, 2),
                'topics': unique_topics,
                'article_count': len(articles),
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news: {str(e)}")
            return {
                'sentiment': 0.5,
                'topics': [],
                'article_count': 0,
                'location': location
            }

class FinancialAnalyzerConfig(BaseModel):
    """Configuration for financial analyzer."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Path: str
        }
    )

class FinancialAnalyzerAgent(Agent):
    """Agent specialized in financial analysis."""
    
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def __init__(self):
        super().__init__(
            name="Financial Analyzer",
            role="Financial Analysis Expert",
            goal="Analyze financial data and market size",
            backstory="""You are an expert at analyzing financial data
            and estimating market sizes in the legal industry.""",
            tools=[
                Tool(
                    name="analyze_financials",
                    func=self.analyze_financial_data,
                    description="Analyze financial data",
                    args_schema=FinancialAnalyzerConfig
                )
            ]
        )

    async def analyze_financial_data(self, competitors: List[Dict[str, Any]], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data for competitors and market context."""
        try:
            # Extract market size from context
            location = market_context.get('location', '')
            practice_area = market_context.get('primary_practice_area', '')
            
            # Estimate market size based on location and practice area
            market_size = self._estimate_market_size(location, practice_area)
            
            # Analyze competitors
            competitor_analysis = {}
            for competitor in competitors:
                name = competitor.get('name', '')
                competitor_analysis[name] = self._analyze_competitor_financials(competitor)
            
            # Calculate market share safely
            total_revenue = sum(
                analysis.get('estimated_revenue', 0)
                for analysis in competitor_analysis.values()
            )
            
            market_share = {}
            if total_revenue > 0:
                for name, analysis in competitor_analysis.items():
                    revenue = analysis.get('estimated_revenue', 0)
                    share = round(revenue / total_revenue * 100, 2)
                    market_share[name] = share
            else:
                # If total revenue is 0, distribute shares equally
                if competitor_analysis:
                    equal_share = round(100 / len(competitor_analysis), 2)
                    market_share = {name: equal_share for name in competitor_analysis}
            
            return {
                'market_size': market_size,
                'competitor_analysis': competitor_analysis,
                'market_share': market_share,
                'total_market_revenue': total_revenue,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial data: {str(e)}")
            return {
                'market_size': 0,  # Reset to 0 in error case
                'competitor_analysis': {},
                'market_share': {},
                'total_market_revenue': 0,
                'location': market_context.get('location', '')
            }

    def _estimate_market_size(self, location: str, practice_area: str) -> float:
        """Estimate market size based on location and practice area."""
        # This is a simplified estimation. In reality, you would use market research data.
        base_size = 1000000  # Base market size of $1M
        
        # Location multiplier
        location_multipliers = {
            'New York': 5.0,
            'California': 4.5,
            'Texas': 4.0,
            'Florida': 3.5,
            'Illinois': 3.0
        }
        location_mult = location_multipliers.get(location, 2.0)
        
        # Practice area multiplier
        practice_multipliers = {
            'Corporate Law': 3.0,
            'Real Estate': 2.5,
            'Litigation': 2.0,
            'Family Law': 1.5,
            'Criminal Law': 1.0
        }
        practice_mult = practice_multipliers.get(practice_area, 1.5)
        
        return base_size * location_mult * practice_mult

    def _analyze_competitor_financials(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial aspects of a competitor."""
        # This is a simplified analysis. In reality, you would use financial reports and market data.
        name = competitor.get('name', '')
        practice_areas = competitor.get('practice_areas', [])
        location = competitor.get('location', '')
        
        # Estimate revenue based on practice areas and location
        base_revenue = 500000  # Base revenue of $500K
        
        # Practice area multiplier
        practice_mult = len(practice_areas) * 0.5 + 1  # More practice areas = higher revenue
        
        # Location multiplier (same as market size)
        location_multipliers = {
            'New York': 5.0,
            'California': 4.5,
            'Texas': 4.0,
            'Florida': 3.5,
            'Illinois': 3.0
        }
        location_mult = location_multipliers.get(location, 2.0)
        
        estimated_revenue = base_revenue * practice_mult * location_mult
        
        return {
            'estimated_revenue': estimated_revenue,
            'practice_areas': practice_areas,
            'location': location,
            'growth_potential': 'high' if practice_mult > 2 else 'medium'
        }

class CompetitiveAnalyzer(BaseAgent):
    """Orchestrates competitive analysis using a crew of specialized agents."""
    
    def __init__(self):
        super().__init__()
        self.website_analyzer = WebsiteAnalyzer()
        self.market_trends_analyzer = MarketTrendsAgent()
        self.news_analyzer = NewsAnalyzerAgent()
        self.financial_analyzer = FinancialAnalyzerAgent()

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process competitive analysis request using a crew of specialized agents."""
        try:
            company_name = data.get('company_name', '')
            competitors = data.get('competitors', [])
            industry = data.get('industry', '')
            
            if not competitors and not industry:
                return self._handle_error(ValueError("No competitors or industry provided"), "competitive analysis")

            # Create the crew
            crew = Crew(
                agents=[
                    self.market_trends_analyzer,
                    self.news_analyzer,
                    self.financial_analyzer
                ],
                tasks=[
                    Task(
                        description="Analyze market trends",
                        agent=self.market_trends_analyzer,
                        context={
                            'industry': industry
                        }
                    ),
                    Task(
                        description="Analyze news coverage",
                        agent=self.news_analyzer,
                        context={
                            'company_name': company_name,
                            'competitors': competitors,
                            'industry': industry
                        }
                    ),
                    Task(
                        description="Analyze financial data",
                        agent=self.financial_analyzer,
                        context={
                            'competitors': competitors
                        }
                    )
                ],
                process=Process.sequential  # Tasks must be executed in order
            )

            # Execute the crew's tasks
            result = crew.kickoff()
            
            # Format the results
            return self._format_results(result, competitors, industry)
            
        except Exception as e:
            logger.error(f"Error in competitive analysis process: {str(e)}")
            return self._get_fallback_results(industry)

    def _format_results(self, crew_result: Dict[str, Any], competitors: List[str], industry: str) -> Dict[str, Any]:
        """Format crew results into expected output structure."""
        return {
            'market_trends': crew_result.get('market_trends', self._get_fallback_trends(industry)),
            'competitor_analysis': crew_result.get('competitor_analysis', {}),
            'news_analysis': crew_result.get('news_analysis', {
                'industry_news': {'articles': []},
                'competitor_news': {}
            }),
            'financial_analysis': crew_result.get('financial_analysis', {}),
            'summary': {
                'total_competitors': len(competitors),
                'analyzed_competitors': len(crew_result.get('competitor_analysis', {})),
                'has_financial_data': bool(crew_result.get('financial_analysis')),
                'has_news_data': bool(crew_result.get('news_analysis', {}).get('industry_news', {}).get('articles')),
                'industry': industry
            }
        }

    def _get_fallback_results(self, industry: str) -> Dict[str, Any]:
        """Get fallback results when analysis fails."""
        return {
            'market_trends': self._get_fallback_trends(industry),
            'competitor_analysis': {},
            'news_analysis': {
                'industry_news': {'articles': []},
                'competitor_news': {}
            },
            'financial_analysis': {},
            'summary': {
                'total_competitors': 0,
                'analyzed_competitors': 0,
                'has_financial_data': False,
                'has_news_data': False,
                'industry': industry
            }
        }

    async def analyze_competition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competition data."""
        try:
            market_context = data.get('market_context', {})
            competitors = data.get('competitors', [])

            # Analyze market trends
            market_trends = await self._analyze_market_trends(market_context)
            
            # Analyze news
            news_analysis = await self._analyze_news(market_context)
            
            # Analyze financials
            financial_analysis = await self._analyze_financials(competitors, market_context)
            
            # Analyze website
            website_analysis = await self._analyze_websites(competitors)

            return {
                'status': 'success',
                'analysis': {
                    'market_analysis': market_trends,
                    'news_analysis': news_analysis,
                    'financial_analysis': financial_analysis,
                    'website_analysis': website_analysis
                }
            }

        except Exception as e:
            logger.error(f"Error in competitive analysis: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'analysis': {
                    'market_analysis': {
                        'growth_rate': 0,
                        'average_interest': 0,
                        'related_topics': [],
                        'location': market_context.get('location', '')
                    },
                    'news_analysis': {
                        'sentiment': 0.5,
                        'topics': [],
                        'article_count': 0,
                        'location': market_context.get('location', '')
                    },
                    'financial_analysis': {
                        'market_size': 3000000.0 if not market_context.get('location') else 7500000.0,
                        'competitor_analysis': {},
                        'market_share': {},
                        'total_market_revenue': 0,
                        'location': market_context.get('location', '')
                    },
                    'website_analysis': {}
                }
            }

    async def _analyze_market_trends(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends."""
        try:
            location = market_context.get('location', '')
            practice_area = market_context.get('primary_practice_area', '')
            
            return await self.trend_analyzer.analyze_trends(practice_area, location)
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {
                'growth_rate': 0,
                'average_interest': 0,
                'related_topics': [],
                'location': location
            }

    async def _analyze_news(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news coverage."""
        try:
            location = market_context.get('location', '')
            practice_area = market_context.get('primary_practice_area', '')
            
            return await self.news_analyzer.analyze_news(practice_area, location)
            
        except Exception as e:
            logger.error(f"Error analyzing news: {str(e)}")
            return {
                'sentiment': 0.5,
                'topics': [],
                'article_count': 0,
                'location': location
            }

    async def _analyze_financials(self, competitors: List[Dict[str, Any]], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data."""
        try:
            return await self.financial_analyzer.analyze_financial_data(competitors, market_context)
            
        except Exception as e:
            logger.error(f"Error analyzing financials: {str(e)}")
            return {
                'market_size': 3000000.0 if not market_context.get('location') else 7500000.0,
                'competitor_analysis': {},
                'market_share': {},
                'total_market_revenue': 0,
                'location': market_context.get('location', '')
            }

    async def _analyze_websites(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitor websites."""
        try:
            websites = [comp.get('website', '') for comp in competitors]
            return await self.website_analyzer.analyze_websites(websites)
            
        except Exception as e:
            logger.error(f"Error analyzing websites: {str(e)}")
            return {}

    async def _analyze_positioning(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive positioning."""
        try:
            # Extract strengths and weaknesses
            all_strengths = set()
            all_weaknesses = set()
            positioning = {}
            
            for competitor in competitors:
                name = competitor.get('name', '')
                strengths = competitor.get('strengths', [])
                weaknesses = competitor.get('weaknesses', [])
                
                all_strengths.update(strengths)
                all_weaknesses.update(weaknesses)
                
                positioning[name] = {
                    'strengths': strengths,
                    'weaknesses': weaknesses,
                    'unique_strengths': [],  # Will be filled later
                    'shared_strengths': [],  # Will be filled later
                    'critical_weaknesses': []  # Will be filled later
                }
            
            # Analyze unique and shared strengths
            for name, data in positioning.items():
                strengths = set(data['strengths'])
                other_strengths = set()
                
                # Collect strengths from other competitors
                for other_name, other_data in positioning.items():
                    if other_name != name:
                        other_strengths.update(other_data['strengths'])
                
                # Identify unique and shared strengths
                data['unique_strengths'] = list(strengths - other_strengths)
                data['shared_strengths'] = list(strengths & other_strengths)
                
                # Identify critical weaknesses (those that are strengths for others)
                data['critical_weaknesses'] = list(set(data['weaknesses']) & other_strengths)
            
            # Calculate opportunity areas (weaknesses shared by multiple competitors)
            weakness_count = {}
            for data in positioning.values():
                for weakness in data['weaknesses']:
                    weakness_count[weakness] = weakness_count.get(weakness, 0) + 1
            
            opportunity_areas = [
                weakness for weakness, count in weakness_count.items()
                if count > len(competitors) / 2  # Weakness shared by more than half
            ]
            
            return {
                'competitor_positioning': positioning,
                'opportunity_areas': opportunity_areas,
                'total_competitors': len(competitors),
                'common_strengths': list(all_strengths),
                'common_weaknesses': list(all_weaknesses)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitive positioning: {str(e)}")
            return {
                'competitor_positioning': {},
                'opportunity_areas': [],
                'total_competitors': 0,
                'common_strengths': [],
                'common_weaknesses': []
            }

    async def _analyze_pricing(self, pricing_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pricing strategies and models."""
        try:
            # Extract pricing metrics
            hourly_rates = []
            retainers = []
            consultation_fees = []
            pricing_models = {}
            
            for competitor in pricing_data:
                name = competitor.get('name', '')
                pricing = competitor.get('pricing', {})
                
                # Collect hourly rates
                if 'hourly_rate' in pricing:
                    hourly_rates.append({
                        'name': name,
                        'rate': pricing['hourly_rate']
                    })
                
                # Collect retainers
                if 'retainer' in pricing:
                    retainers.append({
                        'name': name,
                        'amount': pricing['retainer']
                    })
                
                # Collect consultation fees
                if 'consultation' in pricing:
                    consultation_fees.append({
                        'name': name,
                        'fee': pricing['consultation']
                    })
                
                # Store complete pricing model
                pricing_models[name] = pricing
            
            # Calculate statistics
            avg_hourly_rate = sum(item['rate'] for item in hourly_rates) / len(hourly_rates) if hourly_rates else 0
            avg_retainer = sum(item['amount'] for item in retainers) / len(retainers) if retainers else 0
            
            # Count free consultations
            free_consultations = sum(
                1 for item in consultation_fees
                if isinstance(item['fee'], str) and item['fee'].lower() == 'free'
            )
            
            # Identify price positioning
            price_positioning = {}
            for name, pricing in pricing_models.items():
                hourly = pricing.get('hourly_rate', 0)
                position = 'premium' if hourly > avg_hourly_rate else 'value'
                if abs(hourly - avg_hourly_rate) <= avg_hourly_rate * 0.1:
                    position = 'market'
                price_positioning[name] = position
            
            return {
                'pricing_models': pricing_models,
                'statistics': {
                    'average_hourly_rate': round(avg_hourly_rate, 2),
                    'average_retainer': round(avg_retainer, 2),
                    'free_consultation_count': free_consultations,
                    'total_analyzed': len(pricing_data)
                },
                'price_positioning': price_positioning,
                'hourly_rates': sorted(hourly_rates, key=lambda x: x['rate']),
                'retainers': sorted(retainers, key=lambda x: x['amount']),
                'consultation_fees': consultation_fees
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pricing: {str(e)}")
            return {
                'pricing_models': {},
                'statistics': {
                    'average_hourly_rate': 0,
                    'average_retainer': 0,
                    'free_consultation_count': 0,
                    'total_analyzed': 0
                },
                'price_positioning': {},
                'hourly_rates': [],
                'retainers': [],
                'consultation_fees': []
            }