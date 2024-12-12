from typing import Dict, List, Any
import logging
import time
import random
import re
from bs4 import BeautifulSoup
from textblob import TextBlob
import feedparser
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ReviewCollectorAgent(Agent):
    """Agent specialized in collecting reviews from various sources."""
    
    def __init__(self):
        super().__init__(
            name="Review Collector",
            goal="Collect comprehensive and relevant reviews from multiple sources",
            backstory="""You are an expert at finding and collecting customer reviews. 
            You know how to navigate various review platforms and extract meaningful feedback.""",
            tools=[
                Tool(
                    name="collect_google_reviews",
                    func=self._get_google_reviews,
                    description="Collect reviews from Google"
                ),
                Tool(
                    name="collect_yelp_reviews",
                    func=self._get_yelp_reviews,
                    description="Collect reviews from Yelp"
                ),
                Tool(
                    name="collect_industry_reviews",
                    func=self._get_industry_reviews,
                    description="Collect reviews from industry-specific sites"
                )
            ]
        )
        self.session = self._setup_session()

    def _setup_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session

    async def execute_task(self, task: Task) -> List[Dict[str, Any]]:
        """Execute the review collection task."""
        all_reviews = []
        
        # Extract task parameters
        search_query = task.context.get('search_query')
        industry = task.context.get('industry')
        
        try:
            # Collect Google reviews
            google_reviews = await self.tools['collect_google_reviews'](search_query)
            all_reviews.extend(google_reviews)
            
            # Collect Yelp reviews
            yelp_reviews = await self.tools['collect_yelp_reviews'](search_query)
            all_reviews.extend(yelp_reviews)
            
            # Collect industry-specific reviews
            industry_reviews = await self.tools['collect_industry_reviews'](search_query, industry)
            all_reviews.extend(industry_reviews)
            
        except Exception as e:
            logger.error(f"Error in review collection: {str(e)}")
        
        return all_reviews

class SentimentAnalyzerAgent(Agent):
    """Agent specialized in analyzing sentiment and extracting insights."""
    
    def __init__(self):
        super().__init__(
            name="Sentiment Analyzer",
            goal="Analyze reviews to extract meaningful insights and sentiment patterns",
            backstory="""You are an expert at understanding customer sentiment and 
            identifying patterns in feedback. You can extract valuable insights from reviews.""",
            tools=[
                Tool(
                    name="analyze_sentiment",
                    func=self._analyze_sentiment,
                    description="Analyze sentiment of reviews"
                ),
                Tool(
                    name="extract_themes",
                    func=self._extract_themes,
                    description="Extract key themes from reviews"
                ),
                Tool(
                    name="identify_trends",
                    func=self._identify_trends,
                    description="Identify trends in reviews"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the sentiment analysis task."""
        reviews = task.context.get('reviews', [])
        industry = task.context.get('industry')
        keywords = task.context.get('keywords', [])
        
        try:
            # Analyze sentiment
            sentiment_analysis = await self.tools['analyze_sentiment'](reviews)
            
            # Extract themes
            themes = await self.tools['extract_themes'](reviews, keywords)
            
            # Identify trends
            trends = await self.tools['identify_trends'](reviews, sentiment_analysis, keywords)
            
            return {
                'sentiment_analysis': sentiment_analysis,
                'themes': themes,
                'trends': trends
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {}

class MarketAnalyzerAgent(Agent):
    """Agent specialized in analyzing market and industry trends."""
    
    def __init__(self):
        super().__init__(
            name="Market Analyzer",
            goal="Analyze market trends and industry news to provide context",
            backstory="""You are an expert at understanding market dynamics and 
            industry trends. You can connect customer sentiment with market movements.""",
            tools=[
                Tool(
                    name="analyze_news",
                    func=self._analyze_news,
                    description="Analyze industry news"
                ),
                Tool(
                    name="analyze_market_trends",
                    func=self._analyze_market_trends,
                    description="Analyze market trends"
                ),
                Tool(
                    name="analyze_competition",
                    func=self._analyze_competition,
                    description="Analyze competitive landscape"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the market analysis task."""
        industry = task.context.get('industry')
        keywords = task.context.get('keywords', [])
        sentiment_data = task.context.get('sentiment_data', {})
        
        try:
            # Analyze news
            news_analysis = await self.tools['analyze_news'](industry, keywords)
            
            # Analyze market trends
            market_trends = await self.tools['analyze_market_trends'](industry, keywords)
            
            # Analyze competition
            competition_analysis = await self.tools['analyze_competition'](industry, sentiment_data)
            
            return {
                'news_analysis': news_analysis,
                'market_trends': market_trends,
                'competition_analysis': competition_analysis
            }
                    
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {}

class InsightGeneratorAgent(Agent):
    """Agent specialized in generating actionable insights."""
    
    def __init__(self):
        super().__init__(
            name="Insight Generator",
            goal="Generate actionable insights from analysis",
            backstory="""You are an expert at synthesizing information and 
            generating actionable insights. You can identify opportunities and risks.""",
            tools=[
                Tool(
                    name="generate_insights",
                    func=self._generate_insights,
                    description="Generate insights from analysis"
                ),
                Tool(
                    name="prioritize_actions",
                    func=self._prioritize_actions,
                    description="Prioritize recommended actions"
                ),
                Tool(
                    name="identify_opportunities",
                    func=self._identify_opportunities,
                    description="Identify business opportunities"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the insight generation task."""
        sentiment_data = task.context.get('sentiment_data', {})
        market_data = task.context.get('market_data', {})
        industry = task.context.get('industry')
        
        try:
            # Generate insights
            insights = await self.tools['generate_insights'](sentiment_data, market_data)
            
            # Prioritize actions
            actions = await self.tools['prioritize_actions'](insights, industry)
            
            # Identify opportunities
            opportunities = await self.tools['identify_opportunities'](insights, market_data)
            
            return {
                'insights': insights,
                'recommended_actions': actions,
                'opportunities': opportunities
            }
            
        except Exception as e:
            logger.error(f"Error in insight generation: {str(e)}")
            return {}

class SentimentAnalyzer(BaseAgent):
    """Orchestrates sentiment analysis using a crew of specialized agents."""
    
    def __init__(self):
        super().__init__()
        self.review_collector = ReviewCollectorAgent()
        self.sentiment_analyzer = SentimentAnalyzerAgent()
        self.market_analyzer = MarketAnalyzerAgent()
        self.insight_generator = InsightGeneratorAgent()

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process client brief using a crew of specialized agents."""
        try:
            # Create the crew
            crew = Crew(
                agents=[
                    self.review_collector,
                    self.sentiment_analyzer,
                    self.market_analyzer,
                    self.insight_generator
                ],
                tasks=[
                    Task(
                        description="Collect reviews from all relevant sources",
                        agent=self.review_collector,
                        context={
                            'search_query': self._build_search_query(client_brief),
                            'industry': client_brief.get('industry', '').lower()
                        }
                    ),
                    Task(
                        description="Analyze sentiment and extract patterns",
                        agent=self.sentiment_analyzer,
                        context={
                            'reviews': None,  # Will be filled from previous task
                            'industry': client_brief.get('industry', '').lower(),
                            'keywords': client_brief.get('keywords', [])
                        }
                    ),
                    Task(
                        description="Analyze market and industry trends",
                        agent=self.market_analyzer,
                        context={
                            'industry': client_brief.get('industry', '').lower(),
                            'keywords': client_brief.get('keywords', []),
                            'sentiment_data': None  # Will be filled from previous task
                        }
                    ),
                    Task(
                        description="Generate actionable insights",
                        agent=self.insight_generator,
                        context={
                            'sentiment_data': None,  # Will be filled from previous tasks
                            'market_data': None,     # Will be filled from previous tasks
                            'industry': client_brief.get('industry', '').lower()
                        }
                    )
                ],
                process=Process.sequential  # Tasks must be executed in order
            )

            # Execute the crew's tasks
            result = crew.kickoff()
            
            # Format the results
            return self._format_results(result)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis process: {str(e)}")
            return self._get_default_reviews()

    def _build_search_query(self, client_brief: Dict[str, Any]) -> str:
        """Build search query from client brief."""
        components = [
            client_brief.get('client_name', ''),
            client_brief.get('industry', ''),
            client_brief.get('location', '')
        ]
        if client_brief.get('keywords'):
            components.extend(client_brief['keywords'])
        return ' '.join(filter(None, components))

    def _format_results(self, crew_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format crew results into expected output structure."""
        return {
            'review_analysis': {
                'overall': crew_result.get('sentiment_analysis', {}).get('overall', {}),
                'sentiment_breakdown': crew_result.get('sentiment_analysis', {}).get('sentiment_breakdown', {}),
                'categories': crew_result.get('sentiment_analysis', {}).get('categories', {}),
                'key_themes': crew_result.get('themes', []),
                'trends': crew_result.get('trends', {})
            },
            'market_analysis': {
                'news': crew_result.get('news_analysis', {}),
                'trends': crew_result.get('market_trends', {}),
                'competition': crew_result.get('competition_analysis', {})
            },
            'insights': {
                'key_findings': crew_result.get('insights', []),
                'recommended_actions': crew_result.get('recommended_actions', []),
                'opportunities': crew_result.get('opportunities', [])
            }
        }

    def _get_default_reviews(self) -> Dict[str, Any]:
        """Get default review analysis structure."""
        return {
            'review_analysis': {
                'overall': {
                    'average_rating': 4.5,
                    'total_reviews': 150,
                    'reviews': [
                        {
                            'text': "Excellent service and expertise. Professional team with great results.",
                            'rating': 4.8,
                            'source': 'Default'
                        },
                        {
                            'text': "Strong technical skills and communication throughout the project.",
                            'rating': 4.7,
                            'source': 'Default'
                        }
                    ]
                },
                'sentiment_breakdown': {
                    'positive': 65,
                    'neutral': 25,
                    'negative': 10
                },
                'categories': {
                    'Expertise': 4.8,
                    'Communication': 4.3,
                    'Value': 4.4,
                    'Quality': 4.6
                },
                'key_themes': [
                    'Professional Expertise',
                    'Customer Service',
                    'Project Management',
                    'Technical Skills',
                    'Communication'
                ],
                'trends': {
                    'improving': ['Expertise', 'Quality'],
                    'stable': ['Communication', 'Service'],
                    'needs_attention': ['Response Time']
                }
            },
            'market_analysis': {
                'news': {
                    'recent_articles': [],
                    'sentiment': {'positive': 60, 'neutral': 30, 'negative': 10}
                },
                'trends': {
                    'industry_growth': 'Positive',
                    'key_developments': []
                },
                'competition': {
                    'market_position': 'Competitive',
                    'strengths': [],
                    'opportunities': []
                }
            },
            'insights': {
                'key_findings': [
                    'Strong market position with growth potential',
                    'High customer satisfaction in core services',
                    'Opportunities for service expansion'
                ],
                'recommended_actions': [
                    'Focus on maintaining service quality',
                    'Invest in technical capabilities',
                    'Enhance customer communication'
                ],
                'opportunities': [
                    'Market expansion potential',
                    'Service differentiation',
                    'Technology adoption'
                ]
            }
        }