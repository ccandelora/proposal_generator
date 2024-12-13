from typing import Dict, List, Any
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import time
import re
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from pydantic import BaseModel, ConfigDict
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ContentAnalyzerConfig(BaseModel):
    """Configuration for content analyzer."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ContentAnalyzerAgent(Agent):
    """Agent specialized in analyzing website content."""
    
    def __init__(self):
        super().__init__(
            name="Content Analyzer",
            role="Content Analysis Expert",
            goal="Analyze website content structure and quality",
            backstory="""You are an expert at analyzing website content, 
            understanding its structure, and evaluating its quality.""",
            tools=[
                Tool(
                    name="analyze_text_content",
                    func=self._analyze_text_content,
                    description="Analyze text content",
                    args_schema=ContentAnalyzerConfig
                ),
                Tool(
                    name="analyze_media_content",
                    func=self._analyze_media_content,
                    description="Analyze media content",
                    args_schema=ContentAnalyzerConfig
                ),
                Tool(
                    name="analyze_structure",
                    func=self._analyze_structure,
                    description="Analyze content structure",
                    args_schema=ContentAnalyzerConfig
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the content analysis task."""
        html_content = task.context.get('html_content')
        url = task.context.get('url')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze text content
            text_analysis = await self.tools['analyze_text_content'](soup)
            
            # Analyze media content
            media_analysis = await self.tools['analyze_media_content'](soup)
            
            # Analyze structure
            structure_analysis = await self.tools['analyze_structure'](soup)
            
            return {
                'text_analysis': text_analysis,
                'media_analysis': media_analysis,
                'structure_analysis': structure_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {}

    def _analyze_text_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze text content of the website."""
        try:
            # Get all text content
            text_content = soup.get_text()
            words = text_content.split()
            
            # Calculate basic metrics
            word_count = len(words)
            avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
            
            # Analyze headings
            headings = {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4'))
            }
            
            # Analyze paragraphs
            paragraphs = soup.find_all('p')
            avg_paragraph_length = sum(len(p.get_text().split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
            
            return {
                'word_count': word_count,
                'avg_word_length': round(avg_word_length, 2),
                'heading_structure': headings,
                'paragraph_count': len(paragraphs),
                'avg_paragraph_length': round(avg_paragraph_length, 2)
            }
        except Exception as e:
            logger.error(f"Error analyzing text content: {str(e)}")
            return {}

    def _analyze_media_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze media content of the website."""
        try:
            # Analyze images
            images = soup.find_all('img')
            image_analysis = {
                'count': len(images),
                'with_alt': sum(1 for img in images if img.get('alt')),
                'responsive': sum(1 for img in images if 'img-fluid' in img.get('class', []))
            }
            
            # Analyze videos
            videos = soup.find_all(['video', 'iframe'])
            video_analysis = {
                'count': len(videos),
                'embedded': sum(1 for v in videos if v.name == 'iframe')
            }
            
            return {
                'images': image_analysis,
                'videos': video_analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing media content: {str(e)}")
            return {}

    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content structure of the website."""
        try:
            # Analyze main structural elements
            structure = {
                'has_header': bool(soup.find('header')),
                'has_footer': bool(soup.find('footer')),
                'has_nav': bool(soup.find('nav')),
                'has_main': bool(soup.find('main')),
                'has_sidebar': bool(soup.find(['aside', 'div'], class_=lambda x: x and 'sidebar' in x.lower()))
            }
            
            # Analyze sections
            sections = soup.find_all('section')
            section_analysis = {
                'count': len(sections),
                'with_headings': sum(1 for s in sections if s.find(['h1', 'h2', 'h3', 'h4']))
            }
            
            return {
                'structure': structure,
                'sections': section_analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            return {}

class TechnicalAnalyzerConfig(BaseModel):
    """Configuration for technical analyzer."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

class TechnicalAnalyzerAgent(Agent):
    """Agent specialized in analyzing technical aspects."""
    
    def __init__(self):
        super().__init__(
            name="Technical Analyzer",
            role="Technical Analysis Expert",
            goal="Analyze website technical implementation and performance",
            backstory="""You are an expert at analyzing website technical aspects,
            including performance, security, and technologies used.""",
            tools=[
                Tool(
                    name="analyze_performance",
                    func=self._analyze_performance,
                    description="Analyze website performance",
                    args_schema=TechnicalAnalyzerConfig
                ),
                Tool(
                    name="analyze_security",
                    func=self._analyze_security,
                    description="Analyze security features",
                    args_schema=TechnicalAnalyzerConfig
                ),
                Tool(
                    name="detect_technologies",
                    func=self._detect_technologies,
                    description="Detect technologies used",
                    args_schema=TechnicalAnalyzerConfig
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the technical analysis task."""
        response = task.context.get('response')
        html_content = task.context.get('html_content')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze performance
            performance = await self.tools['analyze_performance'](response)
            
            # Analyze security
            security = await self.tools['analyze_security'](response)
            
            # Detect technologies
            technologies = await self.tools['detect_technologies'](soup, response)
            
            return {
                'performance': performance,
                'security': security,
                'technologies': technologies
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return {}

    def _analyze_performance(self, response: requests.Response) -> Dict[str, Any]:
        """Analyze website performance metrics."""
        try:
            return {
                'load_time': response.elapsed.total_seconds(),
                'content_size': len(response.content),
                'response_code': response.status_code
            }
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            return {}

    def _analyze_security(self, response: requests.Response) -> Dict[str, Any]:
        """Analyze website security features."""
        try:
            headers = response.headers
            return {
                'https': response.url.startswith('https'),
                'hsts': bool(headers.get('Strict-Transport-Security')),
                'xss_protection': bool(headers.get('X-XSS-Protection')),
                'content_security': bool(headers.get('Content-Security-Policy')),
                'x_frame_options': bool(headers.get('X-Frame-Options'))
            }
        except Exception as e:
            logger.error(f"Error analyzing security: {str(e)}")
            return {}

    def _detect_technologies(self, soup: BeautifulSoup, response: requests.Response) -> List[str]:
        """Detect technologies used on the website."""
        technologies = []
        try:
            # Check for common frontend frameworks
            if soup.find(string=lambda text: 'react' in str(text).lower()):
                technologies.append('React')
            if soup.find(string=lambda text: 'angular' in str(text).lower()):
                technologies.append('Angular')
            if soup.find(string=lambda text: 'vue' in str(text).lower()):
                technologies.append('Vue.js')
            
            # Check for common libraries
            if soup.find('script', {'src': lambda x: x and 'jquery' in x.lower()}):
                technologies.append('jQuery')
            if soup.find('link', {'href': lambda x: x and 'bootstrap' in x.lower()}):
                technologies.append('Bootstrap')
            
            # Check for web servers from headers
            server = response.headers.get('Server')
            if server:
                technologies.append(f"Server: {server}")
            
            return technologies
        except Exception as e:
            logger.error(f"Error detecting technologies: {str(e)}")
            return []

class UserExperienceConfig(BaseModel):
    """Configuration for user experience analyzer."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Path: str
        }
    )

class UserExperienceAgent(Agent):
    """Agent specialized in analyzing user experience."""
    
    def __init__(self):
        super().__init__(
            name="User Experience Analyzer",
            role="UX Analysis Expert",
            goal="Analyze website user experience and usability",
            backstory="""You are an expert at analyzing website user experience,
            including navigation, accessibility, and mobile responsiveness.""",
            tools=[
                Tool(
                    name="analyze_navigation",
                    func=self._analyze_navigation,
                    description="Analyze website navigation",
                    args_schema=UserExperienceConfig
                ),
                Tool(
                    name="analyze_accessibility",
                    func=self._analyze_accessibility,
                    description="Analyze accessibility features",
                    args_schema=UserExperienceConfig
                ),
                Tool(
                    name="analyze_responsiveness",
                    func=self._analyze_responsiveness,
                    description="Analyze mobile responsiveness",
                    args_schema=UserExperienceConfig
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the UX analysis task."""
        html_content = task.context.get('html_content')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze navigation
            navigation = await self.tools['analyze_navigation'](soup)
            
            # Check accessibility
            accessibility = await self.tools['analyze_accessibility'](soup)
            
            # Check mobile friendliness
            mobile_friendly = await self.tools['analyze_responsiveness'](soup)
            
            return {
                'navigation': navigation,
                'accessibility': accessibility,
                'mobile_friendly': mobile_friendly
            }
            
        except Exception as e:
            logger.error(f"Error in UX analysis: {str(e)}")
            return {}

    def _analyze_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze website navigation structure."""
        try:
            # Find main navigation
            nav = soup.find('nav')
            if not nav:
                nav = soup.find(['div', 'ul'], class_=lambda x: x and 'nav' in str(x).lower())
            
            nav_items = []
            if nav:
                nav_items = nav.find_all('a')
            
            return {
                'has_main_nav': bool(nav),
                'nav_items_count': len(nav_items),
                'has_search': bool(soup.find('form', class_=lambda x: x and 'search' in str(x).lower())),
                'has_breadcrumbs': bool(soup.find(class_=lambda x: x and 'breadcrumb' in str(x).lower()))
            }
        except Exception as e:
            logger.error(f"Error analyzing navigation: {str(e)}")
            return {}

    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check website accessibility features."""
        try:
            images = soup.find_all('img')
            forms = soup.find_all('form')
            
            return {
                'images_with_alt': sum(1 for img in images if img.get('alt')),
                'forms_with_labels': sum(1 for form in forms if form.find('label')),
                'has_skip_link': bool(soup.find('a', {'href': '#main'})),
                'has_aria_labels': bool(soup.find(attrs={'aria-label': True}))
            }
        except Exception as e:
            logger.error(f"Error checking accessibility: {str(e)}")
            return {}

    def _analyze_responsiveness(self, soup: BeautifulSoup) -> bool:
        """Check if website is mobile friendly."""
        try:
            # Check for viewport meta tag
            viewport = soup.find('meta', {'name': 'viewport'})
            has_viewport = bool(viewport and 'width=device-width' in viewport.get('content', ''))
            
            # Check for responsive classes
            responsive_elements = soup.find_all(class_=lambda x: x and any(
                term in str(x).lower() for term in ['responsive', 'mobile', 'sm-', 'md-', 'lg-']
            ))
            
            return has_viewport and bool(responsive_elements)
        except Exception as e:
            logger.error(f"Error checking mobile friendliness: {str(e)}")
            return False

class LawFirmAnalyzerConfig(BaseModel):
    """Configuration for law firm analyzer."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

class LawFirmAnalyzerAgent(Agent):
    """Agent specialized in analyzing law firm websites."""
    
    def __init__(self):
        super().__init__(
            name="Law Firm Analyzer",
            role="Law Firm Website Expert",
            goal="Analyze law firm specific website features",
            backstory="""You are an expert at analyzing law firm websites,
            understanding their unique requirements and best practices.""",
            tools=[
                Tool(
                    name="analyze_practice_areas",
                    func=self._analyze_practice_areas,
                    description="Analyze practice areas coverage",
                    args_schema=LawFirmAnalyzerConfig
                ),
                Tool(
                    name="analyze_attorney_profiles",
                    func=self._analyze_attorney_profiles,
                    description="Analyze attorney profile presentation",
                    args_schema=LawFirmAnalyzerConfig
                ),
                Tool(
                    name="analyze_case_studies",
                    func=self._analyze_case_studies,
                    description="Analyze case studies and results",
                    args_schema=LawFirmAnalyzerConfig
                )
            ]
        )

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the law firm analysis task."""
        html_content = task.context.get('html_content')
        url = task.context.get('url')
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze practice areas
            practice_areas = await self.tools['analyze_practice_areas'](soup)
            
            # Analyze attorney profiles
            attorneys = await self.tools['analyze_attorney_profiles'](soup)
            
            # Analyze legal resources
            resources = await self.tools['analyze_case_studies'](soup)
            
            return {
                'practice_areas': practice_areas,
                'attorneys': attorneys,
                'legal_resources': resources
            }
            
        except Exception as e:
            logger.error(f"Error in law firm analysis: {str(e)}")
            return {}

    def _analyze_practice_areas(self, soup: BeautifulSoup) -> List[str]:
        """Analyze law firm practice areas."""
        practice_areas = []
        try:
            # Common practice area keywords
            practice_keywords = [
                'corporate law', 'business law', 'litigation', 'real estate',
                'employment law', 'intellectual property', 'patent', 'trademark',
                'family law', 'divorce', 'criminal defense', 'personal injury',
                'estate planning', 'probate', 'tax law', 'immigration'
            ]
            
            # Look for practice area sections
            practice_section = soup.find(
                ['div', 'section'],
                class_=lambda x: x and 'practice' in str(x).lower()
            )
            
            if practice_section:
                # Extract practice areas from lists
                for item in practice_section.find_all('li'):
                    text = item.get_text().strip().lower()
                    if any(keyword in text for keyword in practice_keywords):
                        practice_areas.append(text.title())
            
            return list(set(practice_areas))
        except Exception as e:
            logger.error(f"Error analyzing practice areas: {str(e)}")
            return []

    def _analyze_attorney_profiles(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze attorney profiles."""
        attorneys = []
        try:
            # Look for attorney sections
            attorney_sections = soup.find_all(
                ['div', 'section'],
                class_=lambda x: x and any(term in str(x).lower() for term in ['attorney', 'lawyer', 'team'])
            )
            
            for section in attorney_sections:
                attorney = {}
                
                # Get name
                name_tag = section.find(['h1', 'h2', 'h3', 'h4'])
                if name_tag:
                    attorney['name'] = name_tag.get_text().strip()
                
                # Get title/position
                title_tag = name_tag.find_next(['p', 'div']) if name_tag else None
                if title_tag:
                    attorney['title'] = title_tag.get_text().strip()
                
                # Get practice areas
                practice_tag = section.find(text=re.compile(r'Practice Areas?|Expertise|Focus', re.I))
                if practice_tag and practice_tag.parent:
                    practice_list = practice_tag.parent.find_next(['ul', 'p'])
                    if practice_list:
                        attorney['practice_areas'] = [
                            area.strip() 
                            for area in practice_list.get_text().split(',')
                        ]
                
                if attorney:
                    attorneys.append(attorney)
            
            return attorneys
        except Exception as e:
            logger.error(f"Error analyzing attorney profiles: {str(e)}")
            return []

    def _analyze_case_studies(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze legal resources section."""
        try:
            resources = {
                'blog_posts': [],
                'publications': [],
                'newsletters': [],
                'case_studies': []
            }
            
            # Look for resource sections
            resource_section = soup.find(
                ['div', 'section'],
                class_=lambda x: x and any(term in str(x).lower() for term in ['resource', 'publication', 'blog'])
            )
            
            if resource_section:
                # Extract blog posts
                blog_posts = resource_section.find_all(
                    ['article', 'div'],
                    class_=lambda x: x and 'blog' in str(x).lower()
                )
                resources['blog_posts'] = [
                    {'title': post.find(['h2', 'h3', 'h4']).get_text().strip()}
                    for post in blog_posts if post.find(['h2', 'h3', 'h4'])
                ]
                
                # Extract publications
                publications = resource_section.find_all(
                    ['article', 'div'],
                    class_=lambda x: x and 'publication' in str(x).lower()
                )
                resources['publications'] = [
                    {'title': pub.find(['h2', 'h3', 'h4']).get_text().strip()}
                    for pub in publications if pub.find(['h2', 'h3', 'h4'])
                ]
            
            return resources
        except Exception as e:
            logger.error(f"Error analyzing legal resources: {str(e)}")
            return {}

class WebsiteAnalyzer(BaseAgent):
    """Orchestrates website analysis using a crew of specialized agents."""
    
    def __init__(self):
        super().__init__()
        self.content_analyzer = ContentAnalyzerAgent()
        self.technical_analyzer = TechnicalAnalyzerAgent()
        self.ux_analyzer = UserExperienceAgent()
        self.law_firm_analyzer = LawFirmAnalyzerAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebsiteAnalyzer/1.0;)'
        })

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process client brief using a crew of specialized agents."""
        try:
            url = client_brief.get('website')
            if not url:
                logger.error("No website URL provided")
                return {}

            # Get website content
            response = self.session.get(url, timeout=30)
            html_content = response.text

            # Create the crew
            crew = Crew(
                agents=[
                    self.content_analyzer,
                    self.technical_analyzer,
                    self.ux_analyzer,
                    self.law_firm_analyzer
                ],
                tasks=[
                    Task(
                        description="Analyze website content",
                        agent=self.content_analyzer,
                        context={
                            'html_content': html_content,
                            'url': url
                        }
                    ),
                    Task(
                        description="Analyze technical aspects",
                        agent=self.technical_analyzer,
                        context={
                            'response': response,
                            'html_content': html_content
                        }
                    ),
                    Task(
                        description="Analyze user experience",
                        agent=self.ux_analyzer,
                        context={
                            'html_content': html_content
                        }
                    ),
                    Task(
                        description="Analyze law firm specific features",
                        agent=self.law_firm_analyzer,
                        context={
                            'html_content': html_content,
                            'url': url
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
            logger.error(f"Error in website analysis process: {str(e)}")
            return {}

    def _format_results(self, crew_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format crew results into expected output structure."""
        return {
            'content_analysis': crew_result.get('text_analysis', {}),
            'technical_analysis': {
                'performance': crew_result.get('performance', {}),
                'security': crew_result.get('security', {}),
                'technologies': crew_result.get('technologies', [])
            },
            'user_experience': {
                'navigation': crew_result.get('navigation', {}),
                'accessibility': crew_result.get('accessibility', {}),
                'mobile_friendly': crew_result.get('mobile_friendly', False)
            },
            'law_firm_analysis': {
                'practice_areas': crew_result.get('practice_areas', []),
                'attorneys': crew_result.get('attorneys', []),
                'legal_resources': crew_result.get('legal_resources', [])
            }
        }