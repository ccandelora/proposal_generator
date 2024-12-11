import time
from typing import List, Dict, Any, Optional
import logging
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import whois
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CompetitorAnalyzer(BaseAgent):
    """Analyzes competitors and their market positioning."""

    def __init__(self):
        """Initialize the competitor analyzer."""
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _wait_between_requests(self):
        """Add delay between requests."""
        delay = random.uniform(3, 5)
        logger.info(f"Waiting {delay:.1f} seconds between requests...")
        time.sleep(delay)

    def process(self, competitors: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze the competitors and generate insights."""
        if not competitors:
            logger.warning("No competitors provided for analysis")
            return self._empty_analysis_result()

        try:
            analyzed_competitors = []
            for competitor in competitors:
                analysis = self._analyze_competitor(competitor)
                if analysis:
                    analyzed_competitors.append(analysis)

            if not analyzed_competitors:
                logger.warning("No competitor analysis results generated")
                return self._empty_analysis_result()

            return {
                'competitors': analyzed_competitors,
                'market_insights': self._generate_market_insights(analyzed_competitors),
                'keyword_trends': self._analyze_keyword_trends(analyzed_competitors),
                'market_positioning': self._analyze_market_positioning(analyzed_competitors)
            }
        except Exception as e:
            logger.error(f"Error during competitor analysis: {str(e)}")
            return self._empty_analysis_result()

    def _analyze_competitor(self, competitor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single competitor."""
        try:
            website = competitor.get('website', '')
            if not website:
                return None

            self._wait_between_requests()
            
            # Get website info
            try:
                response = self.session.get(website, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc['content'] if meta_desc else competitor.get('description', '')
                
                # Extract services
                services = self._extract_services(soup)
                
                # Get domain info
                domain_info = self._get_domain_info(website)
                
                return {
                    'name': competitor['name'],
                    'website': website,
                    'description': description,
                    'services': services,
                    'domain_info': domain_info,
                    'source': competitor.get('source', 'Unknown')
                }
                
            except Exception as e:
                logger.error(f"Error analyzing competitor website {website}: {str(e)}")
                return {
                    'name': competitor['name'],
                    'website': website,
                    'description': competitor.get('description', ''),
                    'services': [],
                    'domain_info': {},
                    'source': competitor.get('source', 'Unknown')
                }
                
        except Exception as e:
            logger.error(f"Error analyzing competitor: {str(e)}")
            return None

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

    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result structure."""
        return {
            'competitors': [],
            'market_insights': {},
            'keyword_trends': {},
            'market_positioning': {}
        }