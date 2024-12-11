from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from duckduckgo_search import DDGS
import whois
from datetime import datetime, timedelta
from .base_agent import BaseAgent
import logging
import time
import random
from urllib.parse import quote_plus, urljoin

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_hour: int = 20):
        self.requests_per_hour = requests_per_hour
        self.request_timestamps = []
        
    def wait_if_needed(self):
        """Implement aggressive rate limiting."""
        now = datetime.now()
        # Remove timestamps older than 1 hour
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if now - ts < timedelta(hours=1)]
        
        # If we've made too many requests in the last hour, wait
        if len(self.request_timestamps) >= self.requests_per_hour:
            oldest_timestamp = min(self.request_timestamps)
            wait_seconds = (oldest_timestamp + timedelta(hours=1) - now).total_seconds()
            if wait_seconds > 0:
                logger.info(f"Rate limit approaching, waiting {wait_seconds:.1f} seconds...")
                time.sleep(wait_seconds)
        
        # Add random delay between 20-40 seconds
        delay = random.uniform(20, 40)
        logger.info(f"Adding delay of {delay:.1f} seconds between requests...")
        time.sleep(delay)
        
        # Record this request
        self.request_timestamps.append(now)

class CompetitorFinder(BaseAgent):
    """Discovers and analyzes competitors in the market."""
    
    def __init__(self):
        """Initialize the competitor finder."""
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

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process the client brief to find competitors."""
        business_name = client_brief.get('client_name', '')
        industry = client_brief.get('industry', '')
        location = client_brief.get('location', '')

        if not all([business_name, industry, location]):
            logger.error("Missing required information in client brief")
            return {'competitors': []}

        try:
            competitors = self._discover_competitors(business_name, industry, location)
            return {'competitors': competitors}
        except Exception as e:
            logger.error(f"Error finding competitors: {str(e)}")
            return {'competitors': []}

    def _discover_competitors(self, business_name: str, industry: str, location: str) -> List[Dict[str, Any]]:
        """Discover competitors using various methods."""
        logger.info(f"Starting competitor search for {business_name} in {location}")
        competitors = []

        # Try direct directory scraping first
        try:
            directory_competitors = self._scrape_legal_directories(location)
            competitors.extend(directory_competitors)
        except Exception as e:
            logger.error(f"Error during directory scraping: {str(e)}")

        # Deduplicate and limit results
        unique_competitors = self._deduplicate_competitors(competitors)
        logger.info(f"Found {len(unique_competitors)} unique competitors")
        return unique_competitors[:5]

    def _scrape_legal_directories(self, location: str) -> List[Dict[str, Any]]:
        """Scrape legal directories directly."""
        competitors = []
        
        # Try Martindale
        try:
            logger.info("Searching Martindale directory...")
            self._wait_between_requests()  # Add delay before request
            martindale_results = self._scrape_martindale(location)
            if martindale_results:
                competitors.extend(martindale_results)
                logger.info(f"Found {len(martindale_results)} results from Martindale")
        except Exception as e:
            logger.error(f"Error scraping Martindale: {str(e)}")

        if len(competitors) < 5:
            try:
                logger.info("Searching Justia directory...")
                self._wait_between_requests()  # Add delay before request
                justia_results = self._scrape_justia(location)
                if justia_results:
                    competitors.extend(justia_results)
                    logger.info(f"Found {len(justia_results)} results from Justia")
            except Exception as e:
                logger.error(f"Error scraping Justia: {str(e)}")

        if len(competitors) < 5:
            try:
                logger.info("Searching FindLaw directory...")
                self._wait_between_requests()  # Add delay before request
                findlaw_results = self._scrape_findlaw(location)
                if findlaw_results:
                    competitors.extend(findlaw_results)
                    logger.info(f"Found {len(findlaw_results)} results from FindLaw")
            except Exception as e:
                logger.error(f"Error scraping FindLaw: {str(e)}")

        return competitors

    def _scrape_martindale(self, location: str) -> List[Dict[str, Any]]:
        """Scrape Martindale directory."""
        results = []
        try:
            location_parts = location.lower().split(',')
            city = location_parts[0].strip()
            state = location_parts[1].strip() if len(location_parts) > 1 else ''
            
            url = f"https://www.martindale.com/search/attorneys/{state}/{city}/"
            
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find law firm listings
                for firm in soup.select('.attorney-search-card'):
                    try:
                        name_elem = firm.select_one('.attorney-name')
                        if not name_elem:
                            continue
                            
                        name = name_elem.get_text(strip=True)
                        website = urljoin(url, name_elem.get('href', ''))
                        description = firm.select_one('.attorney-search-practice-areas')
                        description = description.get_text(strip=True) if description else ''
                        
                        if website and name:
                            results.append({
                                'name': name,
                                'website': website,
                                'description': description,
                                'source': 'Martindale'
                            })
                            logger.info(f"Found competitor from Martindale: {name}")
                        
                    except Exception as e:
                        logger.error(f"Error parsing Martindale result: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error accessing Martindale: {str(e)}")
            
        return results[:5]

    def _scrape_justia(self, location: str) -> List[Dict[str, Any]]:
        """Scrape Justia directory."""
        results = []
        location_parts = location.lower().split(',')
        city = location_parts[0].strip()
        state = location_parts[1].strip() if len(location_parts) > 1 else ''
        
        url = f"https://www.justia.com/lawyers/{state}/{city}"
        
        try:
            self._wait_between_requests()
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find law firm listings
                for firm in soup.select('.lawyer-card'):
                    try:
                        name_elem = firm.select_one('.lawyer-name')
                        if not name_elem:
                            continue
                            
                        name = name_elem.get_text(strip=True)
                        website = urljoin(url, name_elem.get('href', ''))
                        description = firm.select_one('.practice-areas')
                        description = description.get_text(strip=True) if description else ''
                        
                        if website and name:
                            results.append({
                                'name': name,
                                'website': website,
                                'description': description,
                                'source': 'Justia'
                            })
                            logger.info(f"Found competitor from Justia: {name}")
                        
                    except Exception as e:
                        logger.error(f"Error parsing Justia result: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error accessing Justia: {str(e)}")
            
        return results[:5]

    def _scrape_findlaw(self, location: str) -> List[Dict[str, Any]]:
        """Scrape FindLaw directory."""
        results = []
        location_parts = location.lower().split(',')
        city = location_parts[0].strip()
        state = location_parts[1].strip() if len(location_parts) > 1 else ''
        
        url = f"https://lawyers.findlaw.com/{state}/{city}/law-firms-all"
        
        try:
            self._wait_between_requests()
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find law firm listings
                for firm in soup.select('.listing-card'):
                    try:
                        name_elem = firm.select_one('.listing-title')
                        if not name_elem:
                            continue
                            
                        profile_url = urljoin(url, name_elem.get('href', ''))
                        if not profile_url:
                            continue
                        
                        # Follow profile link to get actual website
                        website_info = self._follow_profile_link(profile_url)
                        if website_info:
                            results.append({
                                'name': website_info['name'],
                                'website': website_info['website'],
                                'description': website_info['description'],
                                'source': 'FindLaw'
                            })
                            logger.info(f"Found competitor from FindLaw: {website_info['name']}")
                        
                    except Exception as e:
                        logger.error(f"Error parsing FindLaw result: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error accessing FindLaw: {str(e)}")
            
        return results[:5]

    def _deduplicate_competitors(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate competitors based on name similarity."""
        seen_names = set()
        unique_competitors = []
        
        for comp in competitors:
            name = comp['name'].lower()
            # Remove common suffixes
            name = name.replace('llc', '').replace('llp', '').replace('pc', '').strip()
            
            if name not in seen_names:
                seen_names.add(name)
                unique_competitors.append(comp)
        
        return unique_competitors

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.lower()
        except Exception:
            return None

    def _analyze_competitor(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a competitor's website and market presence."""
        try:
            website = competitor['website']
            domain = self._extract_domain(website)
            print(f"\nAnalyzing competitor: {competitor['name']} ({domain})")
            
            # Get website info
            domain_info = self._get_domain_info(domain)
            
            # Get website rank (Alexa rank or similar)
            website_rank = self._get_website_rank(domain)
            
            # Create basic analysis even if website content analysis fails
            analysis = {
                'name': competitor['name'],
                'website': website,
                'domain_age': domain_info.get('age', 'Unknown'),
                'website_rank': website_rank,
                'keywords': [],
                'technologies': [],
                'unique_features': [],
                'market_position': self._determine_market_position(website_rank, domain_info.get('age', 0)),
                'strengths': [],
                'weaknesses': []
            }
            
            try:
                # Analyze website content
                website_data = self._analyze_website_content(website)
                
                # Update analysis with website data if available
                analysis.update({
                    'keywords': website_data.get('keywords', []),
                    'technologies': website_data.get('technologies', []),
                    'unique_features': website_data.get('features', []),
                    'strengths': self._analyze_strengths(
                        website_data.get('technologies', []),
                        website_data.get('features', [])
                    ),
                    'weaknesses': self._analyze_weaknesses(
                        website_data.get('technologies', []),
                        website_data.get('features', [])
                    )
                })
            except Exception as e:
                print(f"Error analyzing website content for {competitor['name']}: {str(e)}")
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing competitor {competitor['name']}: {str(e)}")
            return None

    def _get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get domain registration information."""
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            age = 0
            if creation_date:
                if isinstance(creation_date, str):
                    creation_date = datetime.strptime(creation_date, '%Y-%m-%d')
                age = (datetime.now() - creation_date).days / 365.25
                
            return {
                'registrar': w.registrar,
                'creation_date': creation_date,
                'age': round(age, 1)
            }
        except:
            return {}

    def _analyze_website_content(self, url: str) -> Dict[str, Any]:
        """Analyze website content using Selenium."""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract meta keywords
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            keywords = []
            if meta_keywords:
                keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
            
            # Extract visible text keywords
            text_content = soup.get_text()
            words = text_content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords from content
            content_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            keywords.extend([word for word, _ in content_keywords])
            
            # Detect technologies
            technologies = self._detect_technologies(soup)
            
            # Analyze features
            features = self._detect_features(soup)
            
            driver.quit()
            
            return {
                'keywords': list(set(keywords)),
                'technologies': technologies,
                'features': features,
                'strengths': self._analyze_strengths(technologies, features),
                'weaknesses': self._analyze_weaknesses(technologies, features)
            }
        except Exception as e:
            print(f"Error analyzing website content: {str(e)}")
            return {}

    def _detect_technologies(self, soup: BeautifulSoup) -> List[str]:
        """Detect technologies used on the website."""
        technologies = []
        
        # Check for common technologies
        if soup.find(string=lambda text: 'react' in str(text).lower()):
            technologies.append('React')
        if soup.find(string=lambda text: 'angular' in str(text).lower()):
            technologies.append('Angular')
        if soup.find(string=lambda text: 'vue' in str(text).lower()):
            technologies.append('Vue.js')
        if soup.find('script', {'src': lambda x: x and 'jquery' in x.lower()}):
            technologies.append('jQuery')
        if soup.find('link', {'href': lambda x: x and 'bootstrap' in x.lower()}):
            technologies.append('Bootstrap')
        
        return technologies

    def _detect_features(self, soup: BeautifulSoup) -> List[str]:
        """Detect key features of the website."""
        features = []
        
        # Check for common features
        if soup.find('form'):
            features.append('Contact Form')
        if soup.find(string=lambda text: 'chat' in str(text).lower()):
            features.append('Live Chat')
        if soup.find('a', {'href': lambda x: x and ('blog' in x.lower() or 'news' in x.lower())}):
            features.append('Blog/News Section')
        if soup.find(string=lambda text: 'newsletter' in str(text).lower()):
            features.append('Newsletter')
        if soup.find(string=lambda text: 'testimonial' in str(text).lower()):
            features.append('Testimonials')
        
        return features

    def _get_website_rank(self, domain: str) -> int:
        """Get website rank (simplified version)."""
        try:
            # This is a simplified version. In a real implementation,
            # you would use a service like Alexa API or similar
            response = requests.get(f"http://{domain}")
            return response.status_code
        except:
            return 999999

    def _determine_market_position(self, rank: int, age: float) -> str:
        """Determine market position based on rank and age."""
        if rank < 100000:
            return "Market Leader"
        elif rank < 500000:
            return "Strong Competitor"
        elif rank < 1000000:
            return "Established Player"
        elif age > 5:
            return "Established but Limited Presence"
        else:
            return "Emerging Player"

    def _analyze_strengths(self, technologies: List[str], features: List[str]) -> List[str]:
        """Analyze competitor strengths."""
        strengths = []
        
        if len(technologies) > 3:
            strengths.append("Modern Technology Stack")
        if len(features) > 4:
            strengths.append("Feature-Rich Website")
        if 'Live Chat' in features:
            strengths.append("Strong Customer Engagement")
        if 'Blog/News Section' in features:
            strengths.append("Content Marketing Focus")
        
        return strengths

    def _analyze_weaknesses(self, technologies: List[str], features: List[str]) -> List[str]:
        """Analyze competitor weaknesses."""
        weaknesses = []
        
        if not technologies:
            weaknesses.append("Limited Technical Implementation")
        if 'jQuery' in technologies:
            weaknesses.append("Older Technology Stack")
        if 'Contact Form' not in features:
            weaknesses.append("Limited Contact Options")
        if 'Blog/News Section' not in features:
            weaknesses.append("Limited Content Marketing")
        
        return weaknesses

    def _generate_market_insights(self, competitors: List[Dict[str, Any]]) -> List[str]:
        """Generate market insights from competitor analysis."""
        insights = []
        
        # Analyze market maturity
        avg_age = sum(c.get('domain_age', 0) for c in competitors) / len(competitors) if competitors else 0
        if avg_age > 10:
            insights.append("Mature market with established players")
        elif avg_age > 5:
            insights.append("Developing market with growing competition")
        else:
            insights.append("Emerging market with opportunities for innovation")
        
        # Analyze technology trends
        all_technologies = []
        for comp in competitors:
            all_technologies.extend(comp.get('technologies', []))
        
        if all_technologies:
            tech_count = {}
            for tech in all_technologies:
                tech_count[tech] = tech_count.get(tech, 0) + 1
            
            popular_tech = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[0]
            insights.append(f"Popular technology: {popular_tech[0]}")
        
        # Analyze feature trends
        all_features = []
        for comp in competitors:
            all_features.extend(comp.get('unique_features', []))
        
        if all_features:
            feature_count = {}
            for feature in all_features:
                feature_count[feature] = feature_count.get(feature, 0) + 1
            
            common_features = [f for f, c in feature_count.items() if c >= len(competitors)/2]
            if common_features:
                insights.append(f"Common features: {', '.join(common_features)}")
        
        return insights

    def _analyze_keyword_trends(self, competitors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze keyword trends across competitors."""
        keyword_count = {}
        
        for comp in competitors:
            for keyword in comp.get('keywords', []):
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_keywords[:10])  # Return top 10 keywords

    def _analyze_market_positioning(self, competitors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze market positioning of competitors."""
        positioning = {
            'Market Leaders': [],
            'Strong Competitors': [],
            'Established Players': [],
            'Emerging Players': []
        }
        
        for comp in competitors:
            position = comp.get('market_position', '')
            if 'Leader' in position:
                positioning['Market Leaders'].append(comp['name'])
            elif 'Strong' in position:
                positioning['Strong Competitors'].append(comp['name'])
            elif 'Established' in position:
                positioning['Established Players'].append(comp['name'])
            else:
                positioning['Emerging Players'].append(comp['name'])
        
        return positioning