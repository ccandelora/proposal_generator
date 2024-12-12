from typing import Dict, List, Any, Optional
import logging
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import whois
import re
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class WebsiteAnalyzerAgent(Agent):
    """Agent specialized in analyzing competitor websites."""
    
    def __init__(self):
        super().__init__(
            name="Website Analyzer",
            goal="Analyze competitor websites for information and features",
            backstory="""You are an expert at analyzing websites to extract 
            valuable competitive information and insights.""",
            tools=[
                Tool(
                    name="analyze_website",
                    func=self._analyze_website,
                    description="Analyze website content and features"
                ),
                Tool(
                    name="extract_services",
                    func=self._extract_services,
                    description="Extract services offered"
                ),
                Tool(
                    name="get_domain_info",
                    func=self._get_domain_info,
                    description="Get domain registration information"
                )
            ]
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the website analysis task."""
        competitor = task.context.get('competitor')
        
        try:
            website = competitor.get('website', '')
            if not website:
                return None

            # Add delay between requests
            delay = random.uniform(3, 5)
            time.sleep(delay)
            
            # Analyze website
            website_data = await self.tools['analyze_website'](website)
            
            # Extract services
            services = await self.tools['extract_services'](website_data.get('soup'))
            
            # Get domain info
            domain_info = await self.tools['get_domain_info'](website)
            
            return {
                'name': competitor.get('name'),
                'website': website,
                'description': website_data.get('description', competitor.get('description', '')),
                'services': services,
                'domain_info': domain_info,
                'source': competitor.get('source', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error in website analysis: {str(e)}")
            return None

    def _analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze website content."""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else ''
            
            return {
                'soup': soup,
                'description': description
            }
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {str(e)}")
            return {}

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract services from website content."""
        services = set()
        
        # Common service-related keywords
        service_keywords = ['practice areas', 'services', 'what we do', 'expertise']
        
        # Look for service-related sections
        for keyword in service_keywords:
            elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
            for element in elements:
                parent = element.parent
                if parent:
                    # Look for nearby lists
                    service_lists = parent.find_all(['ul', 'ol'])
                    for service_list in service_lists:
                        for item in service_list.find_all('li'):
                            service = item.get_text(strip=True)
                            if service and len(service.split()) <= 5:  # Avoid long phrases
                                services.add(service)
        
        return list(services)

    def _get_domain_info(self, url: str) -> Dict[str, Any]:
        """Get domain registration information."""
        try:
            domain = url.split('/')[2]
            w = whois.whois(domain)
            return {
                'creation_date': str(w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date),
                'registrar': w.registrar,
                'country': w.country
            }
        except Exception as e:
            logger.error(f"Error getting domain info for {url}: {str(e)}")
            return {}

class MarketAnalyzerAgent(Agent):
    """Agent specialized in analyzing market insights."""
    
    def __init__(self):
        super().__init__(
            name="Market Analyzer",
            goal="Analyze market insights from competitor data",
            backstory="""You are an expert at analyzing market trends and 
            generating insights from competitor data.""",
            tools=[
                Tool(
                    name="generate_insights",
                    func=self._generate_market_insights,
                    description="Generate market insights"
                ),
                Tool(
                    name="analyze_keywords",
                    func=self._analyze_keyword_trends,
                    description="Analyze keyword trends"
                ),
                Tool(
                    name="analyze_positioning",
                    func=self._analyze_market_positioning,
                    description="Analyze market positioning"
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the market analysis task."""
        competitors = task.context.get('competitors', [])
        
        try:
            # Generate market insights
            insights = await self.tools['generate_insights'](competitors)
            
            # Analyze keyword trends
            trends = await self.tools['analyze_keywords'](competitors)
            
            # Analyze market positioning
            positioning = await self.tools['analyze_positioning'](competitors)
            
            return {
                'market_insights': insights,
                'keyword_trends': trends,
                'market_positioning': positioning
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {}

    def _generate_market_insights(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market insights from competitor analysis."""
        try:
            # Collect all services
            all_services = []
            for comp in competitors:
                all_services.extend(comp.get('services', []))
            
            # Count service frequency
            service_counts = {}
            for service in all_services:
                service_counts[service] = service_counts.get(service, 0) + 1
            
            # Find most common services
            common_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate average company age
            ages = []
            current_year = datetime.now().year
            for comp in competitors:
                try:
                    creation_date = comp.get('domain_info', {}).get('creation_date')
                    if creation_date:
                        creation_year = datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S').year
                        ages.append(current_year - creation_year)
                except Exception:
                    continue
            
            avg_age = sum(ages) / len(ages) if ages else None
            
            return {
                'common_services': common_services,
                'average_company_age': avg_age,
                'total_competitors': len(competitors)
            }
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return {}

    def _analyze_keyword_trends(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze keyword trends from competitor descriptions."""
        try:
            # Collect all descriptions
            descriptions = []
            for comp in competitors:
                if comp.get('description'):
                    descriptions.append(comp['description'])
            
            # Simple keyword frequency analysis
            words = ' '.join(descriptions).lower().split()
            word_freq = {}
            
            # Skip common words
            skip_words = {'the', 'and', 'or', 'in', 'at', 'of', 'to', 'for', 'a', 'an', 'with', 'by'}
            
            for word in words:
                if word not in skip_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'top_keywords': top_keywords,
                'total_words_analyzed': len(words)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing keyword trends: {str(e)}")
            return {}

    def _analyze_market_positioning(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market positioning of competitors."""
        try:
            positions = {
                'established': 0,
                'growing': 0,
                'new': 0
            }
            
            current_year = datetime.now().year
            
            for comp in competitors:
                try:
                    creation_date = comp.get('domain_info', {}).get('creation_date')
                    if creation_date:
                        creation_year = datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S').year
                        age = current_year - creation_year
                        
                        if age > 10:
                            positions['established'] += 1
                        elif age > 5:
                            positions['growing'] += 1
                        else:
                            positions['new'] += 1
                except Exception:
                    continue
            
            return {
                'market_positions': positions,
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market positioning: {str(e)}")
            return {}

class CompetitorAnalyzer(BaseAgent):
    """Orchestrates competitor analysis using a crew of specialized agents."""
    
    def __init__(self):
        super().__init__()
        self.website_analyzer = WebsiteAnalyzerAgent()
        self.market_analyzer = MarketAnalyzerAgent()

    def process(self, competitors: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process competitors using a crew of specialized agents."""
        if not competitors:
            logger.warning("No competitors provided for analysis")
            return self._empty_analysis_result()

        try:
            # Create the crew
            crew = Crew(
                agents=[
                    self.website_analyzer,
                    self.market_analyzer
                ],
                tasks=[
                    Task(
                        description="Analyze competitor websites",
                        agent=self.website_analyzer,
                        context={
                            'competitors': competitors
                        }
                    ),
                    Task(
                        description="Analyze market insights",
                        agent=self.market_analyzer,
                        context={
                            'competitors': None  # Will be filled from previous task
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
            logger.error(f"Error in competitor analysis process: {str(e)}")
            return self._empty_analysis_result()

    def _format_results(self, crew_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format crew results into expected output structure."""
        return {
            'competitors': crew_result.get('competitors', []),
            'market_insights': crew_result.get('market_insights', {}),
            'keyword_trends': crew_result.get('keyword_trends', {}),
            'market_positioning': crew_result.get('market_positioning', {})
        }

    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result structure."""
        return {
            'competitors': [],
            'market_insights': {},
            'keyword_trends': {},
            'market_positioning': {}
        }