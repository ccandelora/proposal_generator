from typing import Dict, List, Any
import logging
import time
import random
import re
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DirectorySearchAgent(Agent):
    """Agent specialized in searching legal directories."""
    
    def __init__(self):
        super().__init__(
            name="Directory Searcher",
            goal="Find competitors through legal directories",
            backstory="""You are an expert at navigating legal directories and 
            finding relevant competitor information.""",
            tools=[
                Tool(
                    name="search_martindale",
                    func=self._search_martindale,
                    description="Search Martindale directory"
                ),
                Tool(
                    name="search_justia",
                    func=self._search_justia,
                    description="Search Justia directory"
                ),
                Tool(
                    name="search_findlaw",
                    func=self._search_findlaw,
                    description="Search FindLaw directory"
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
        """Execute the directory search task."""
        competitors = []
        search_query = task.context.get('search_query')
        location = task.context.get('location')
        
        try:
            # Search Martindale
            martindale_results = await self.tools['search_martindale'](search_query, location)
            competitors.extend(martindale_results)
            
            # Search Justia
            justia_results = await self.tools['search_justia'](search_query, location)
            competitors.extend(justia_results)
            
            # Search FindLaw
            findlaw_results = await self.tools['search_findlaw'](search_query, location)
            competitors.extend(findlaw_results)
            
        except Exception as e:
            logger.error(f"Error in directory search: {str(e)}")
        
        return competitors

class WebsiteAnalyzerAgent(Agent):
    """Agent specialized in analyzing competitor websites."""
    
    def __init__(self):
        super().__init__(
            name="Website Analyzer",
            goal="Analyze competitor websites for technologies and features",
            backstory="""You are an expert at analyzing websites to identify 
            technologies, features, and competitive advantages.""",
            tools=[
                Tool(
                    name="analyze_technologies",
                    func=self._detect_technologies,
                    description="Detect technologies used on website"
                ),
                Tool(
                    name="analyze_features",
                    func=self._detect_features,
                    description="Detect website features"
                ),
                Tool(
                    name="analyze_content",
                    func=self._analyze_content,
                    description="Analyze website content"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the website analysis task."""
        website_url = task.context.get('website_url')
        html_content = task.context.get('html_content')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze technologies
            technologies = await self.tools['analyze_technologies'](soup)
            
            # Analyze features
            features = await self.tools['analyze_features'](soup)
            
            # Analyze content
            content_analysis = await self.tools['analyze_content'](soup)
            
            return {
                'technologies': technologies,
                'features': features,
                'content_analysis': content_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in website analysis: {str(e)}")
            return {}

class MarketAnalyzerAgent(Agent):
    """Agent specialized in analyzing market positioning."""
    
    def __init__(self):
        super().__init__(
            name="Market Analyzer",
            goal="Analyze market positioning and trends",
            backstory="""You are an expert at analyzing market positions, trends, 
            and competitive landscapes.""",
            tools=[
                Tool(
                    name="analyze_market_position",
                    func=self._analyze_market_positioning,
                    description="Analyze market positioning"
                ),
                Tool(
                    name="analyze_trends",
                    func=self._analyze_keyword_trends,
                    description="Analyze market trends"
                ),
                Tool(
                    name="generate_insights",
                    func=self._generate_market_insights,
                    description="Generate market insights"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the market analysis task."""
        competitors = task.context.get('competitors', [])
        
        try:
            # Analyze market positioning
            positioning = await self.tools['analyze_market_position'](competitors)
            
            # Analyze trends
            trends = await self.tools['analyze_trends'](competitors)
            
            # Generate insights
            insights = await self.tools['generate_insights'](competitors)
            
            return {
                'market_positioning': positioning,
                'trends': trends,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {}

class CompetitorFinder(BaseAgent):
    """Orchestrates competitor finding using a crew of specialized agents."""
    
    def __init__(self):
        super().__init__()
        self.directory_searcher = DirectorySearchAgent()
        self.website_analyzer = WebsiteAnalyzerAgent()
        self.market_analyzer = MarketAnalyzerAgent()

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process client brief using a crew of specialized agents."""
        try:
            # Create the crew
            crew = Crew(
                agents=[
                    self.directory_searcher,
                    self.website_analyzer,
                    self.market_analyzer
                ],
                tasks=[
                    Task(
                        description="Find competitors in legal directories",
                        agent=self.directory_searcher,
                        context={
                            'search_query': self._build_search_query(client_brief),
                            'location': client_brief.get('location', '')
                        }
                    ),
                    Task(
                        description="Analyze competitor websites",
                        agent=self.website_analyzer,
                        context={
                            'competitors': None  # Will be filled from previous task
                        }
                    ),
                    Task(
                        description="Analyze market positioning",
                        agent=self.market_analyzer,
                        context={
                            'competitors': None  # Will be filled from previous tasks
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
            logger.error(f"Error in competitor finding process: {str(e)}")
            return self._get_default_competitors()

    def _build_search_query(self, client_brief: Dict[str, Any]) -> str:
        """Build search query from client brief."""
        components = [
            client_brief.get('industry', ''),
            client_brief.get('location', ''),
            'top firms'
        ]
        return ' '.join(filter(None, components))

    def _format_results(self, crew_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format crew results into expected output structure."""
        return {
            'competitors': crew_result.get('competitors', []),
            'market_analysis': {
                'positioning': crew_result.get('market_positioning', {}),
                'trends': crew_result.get('trends', {}),
                'insights': crew_result.get('insights', [])
            }
        }

    def _get_default_competitors(self) -> Dict[str, Any]:
        """Get default competitor analysis structure."""
        return {
            'competitors': [
                {
                    'name': 'Example Competitor 1',
                    'description': 'A leading firm in the industry',
                    'strengths': ['Strong market presence', 'Innovative solutions'],
                    'technologies': ['Modern stack', 'Cloud infrastructure'],
                    'features': ['Client portal', 'Online scheduling']
                }
            ],
            'market_analysis': {
                'positioning': {
                    'Market Leaders': ['Example Competitor 1'],
                    'Strong Competitors': [],
                    'Established Players': [],
                    'Emerging Players': []
                },
                'trends': {
                    'technology': ['Cloud adoption', 'AI integration'],
                    'features': ['Digital transformation', 'Client self-service']
                },
                'insights': [
                    'Growing market with digital transformation opportunities',
                    'Increasing focus on client self-service capabilities'
                ]
            }
        }