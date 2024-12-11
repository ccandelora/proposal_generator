from typing import Dict, List, Any
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from PIL import Image
import io
import hashlib
from .base_agent import BaseAgent

class WebsiteScreenshotter(BaseAgent):
    """Captures and analyzes screenshots of websites."""
    
    def __init__(self):
        super().__init__()
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = 'screenshots'
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process websites and capture screenshots."""
        results = {
            'client_website': {},
            'competitor_websites': [],
            'design_insights': [],
            'improvement_opportunities': []
        }
        
        # Analyze client website
        client_website = client_brief.get('website', '')
        if client_website:
            results['client_website'] = self._analyze_website(client_website, is_client=True)
        
        # Analyze competitor websites
        if context and context.get('competitive_analysis'):
            competitors = context['competitive_analysis'].get('competitors', [])
            for comp in competitors:
                competitor_analysis = self._analyze_website(comp['website'], is_client=False)
                if competitor_analysis:
                    competitor_analysis['competitor_name'] = comp['name']
                    results['competitor_websites'].append(competitor_analysis)
        
        # Generate insights
        results['design_insights'] = self._generate_design_insights(results)
        results['improvement_opportunities'] = self._identify_improvements(results)
        
        return results

    def _analyze_website(self, url: str, is_client: bool) -> Dict[str, Any]:
        """Analyze a website and capture screenshots of its pages."""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            pages = self._discover_pages(driver, url)
            
            analysis = {
                'website': url,
                'pages': [],
                'layout_patterns': [],
                'color_scheme': [],
                'ui_elements': [],
                'responsive_issues': []
            }
            
            for page in pages:
                page_analysis = self._analyze_page(driver, page, is_client)
                if page_analysis:
                    analysis['pages'].append(page_analysis)
            
            # Aggregate patterns across pages
            analysis['layout_patterns'] = self._identify_layout_patterns(analysis['pages'])
            analysis['color_scheme'] = self._extract_color_scheme(analysis['pages'])
            analysis['ui_elements'] = self._identify_common_elements(analysis['pages'])
            analysis['responsive_issues'] = self._check_responsive_design(driver, url)
            
            driver.quit()
            return analysis
            
        except Exception as e:
            print(f"Error analyzing website {url}: {str(e)}")
            return None

    def _discover_pages(self, driver: webdriver.Chrome, url: str) -> List[str]:
        """Discover pages on the website."""
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            base_domain = urlparse(url).netloc
            
            pages = set([url])
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                
                # Only include pages from the same domain
                if urlparse(absolute_url).netloc == base_domain:
                    pages.add(absolute_url)
            
            return list(pages)[:10]  # Limit to 10 pages for efficiency
            
        except Exception as e:
            print(f"Error discovering pages: {str(e)}")
            return [url]

    def _analyze_page(self, driver: webdriver.Chrome, url: str, is_client: bool) -> Dict[str, Any]:
        """Analyze a single page and capture screenshots."""
        try:
            driver.get(url)
            time.sleep(2)  # Wait for dynamic content to load
            
            # Take full page screenshot
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Generate unique filename based on URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            screenshot_path = os.path.join(self.screenshots_dir, f"{url_hash}.png")
            
            # Save screenshot
            driver.save_screenshot(screenshot_path)
            
            # Analyze page structure
            analysis = {
                'url': url,
                'screenshot_path': screenshot_path,
                'title': soup.title.string if soup.title else '',
                'type': self._determine_page_type(url, soup),
                'layout_elements': self._analyze_layout(soup),
                'ui_components': self._analyze_ui_components(soup),
                'color_palette': self._extract_colors(driver),
                'text_content': self._analyze_text_content(soup),
                'responsive_elements': self._analyze_responsive_elements(soup)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing page {url}: {str(e)}")
            return None

    def _determine_page_type(self, url: str, soup: BeautifulSoup) -> str:
        """Determine the type of page based on URL and content."""
        url_lower = url.lower()
        content_text = soup.get_text().lower()
        
        if 'contact' in url_lower or 'contact' in content_text:
            return 'Contact Page'
        elif 'about' in url_lower or 'about' in content_text:
            return 'About Page'
        elif 'service' in url_lower or 'service' in content_text:
            return 'Services Page'
        elif 'product' in url_lower or 'product' in content_text:
            return 'Product Page'
        elif 'blog' in url_lower or 'news' in url_lower:
            return 'Blog/News Page'
        elif url_lower.endswith('/') or url_lower.endswith('index.html'):
            return 'Home Page'
        else:
            return 'Other'

    def _analyze_layout(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the layout structure of the page."""
        layout = {
            'header_present': bool(soup.find('header')),
            'footer_present': bool(soup.find('footer')),
            'navigation_type': self._determine_navigation_type(soup),
            'content_structure': self._analyze_content_structure(soup),
            'grid_system': self._detect_grid_system(soup)
        }
        return layout

    def _analyze_ui_components(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze UI components on the page."""
        components = []
        
        # Forms
        forms = soup.find_all('form')
        for form in forms:
            components.append({
                'type': 'form',
                'fields': len(form.find_all('input')),
                'has_submit': bool(form.find('button', type='submit'))
            })
        
        # Buttons
        buttons = soup.find_all(['button', 'a'], class_=lambda x: x and 'btn' in x.lower())
        if buttons:
            components.append({
                'type': 'buttons',
                'count': len(buttons),
                'styles': self._analyze_button_styles(buttons)
            })
        
        # Images
        images = soup.find_all('img')
        if images:
            components.append({
                'type': 'images',
                'count': len(images),
                'responsive': sum(1 for img in images if 'img-fluid' in img.get('class', []))
            })
        
        return components

    def _extract_colors(self, driver: webdriver.Chrome) -> List[str]:
        """Extract color palette from the page."""
        # Execute JavaScript to get computed styles
        colors = driver.execute_script("""
            var colors = new Set();
            var elements = document.getElementsByTagName('*');
            for (var i = 0; i < elements.length; i++) {
                var style = window.getComputedStyle(elements[i]);
                colors.add(style.color);
                colors.add(style.backgroundColor);
            }
            return Array.from(colors);
        """)
        
        # Filter out transparent and none values
        return [color for color in colors if color and color != 'transparent' and color != 'rgba(0, 0, 0, 0)']

    def _analyze_text_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze text content and typography."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = soup.find_all('p')
        
        return {
            'heading_count': len(headings),
            'paragraph_count': len(paragraphs),
            'text_hierarchy': self._analyze_text_hierarchy(headings)
        }

    def _analyze_responsive_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze responsive design elements."""
        responsive_elements = {
            'responsive_images': len(soup.find_all('img', class_=lambda x: x and 'responsive' in x.lower())),
            'responsive_containers': len(soup.find_all(class_=lambda x: x and 'container' in x.lower())),
            'media_queries': self._detect_media_queries(soup)
        }
        return responsive_elements

    def _identify_layout_patterns(self, pages: List[Dict[str, Any]]) -> List[str]:
        """Identify common layout patterns across pages."""
        patterns = []
        
        # Check for consistent header/footer
        header_consistent = all(page['layout_elements']['header_present'] for page in pages)
        footer_consistent = all(page['layout_elements']['footer_present'] for page in pages)
        
        if header_consistent:
            patterns.append("Consistent Header Layout")
        if footer_consistent:
            patterns.append("Consistent Footer Layout")
        
        # Check navigation patterns
        nav_types = [page['layout_elements']['navigation_type'] for page in pages]
        if len(set(nav_types)) == 1:
            patterns.append(f"Consistent {nav_types[0]} Navigation")
        
        return patterns

    def _extract_color_scheme(self, pages: List[Dict[str, Any]]) -> List[str]:
        """Extract common color scheme across pages."""
        all_colors = []
        for page in pages:
            all_colors.extend(page['color_palette'])
        
        # Get unique colors
        unique_colors = list(set(all_colors))
        return unique_colors[:5]  # Return top 5 most common colors

    def _identify_common_elements(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify common UI elements across pages."""
        common_elements = []
        
        # Analyze forms
        forms = [page['ui_components'] for page in pages]
        if any('form' in str(comp) for comps in forms for comp in comps):
            common_elements.append({
                'type': 'form',
                'frequency': 'common'
            })
        
        # Analyze buttons
        button_styles = []
        for page in pages:
            for comp in page['ui_components']:
                if comp['type'] == 'buttons':
                    button_styles.extend(comp['styles'])
        
        if button_styles:
            common_elements.append({
                'type': 'button_styles',
                'styles': list(set(button_styles))
            })
        
        return common_elements

    def _check_responsive_design(self, driver: webdriver.Chrome, url: str) -> List[str]:
        """Check responsive design issues."""
        issues = []
        viewports = [
            (375, 667),  # iPhone
            (768, 1024),  # Tablet
            (1920, 1080)  # Desktop
        ]
        
        for width, height in viewports:
            driver.set_window_size(width, height)
            driver.get(url)
            time.sleep(2)
            
            # Check for horizontal scrolling
            scroll_width = driver.execute_script('return document.documentElement.scrollWidth')
            if scroll_width > width:
                issues.append(f"Horizontal scrolling at {width}x{height}")
            
            # Check for overlapping elements
            overlapping = driver.execute_script("""
                var elements = document.getElementsByTagName('*');
                for (var i = 0; i < elements.length; i++) {
                    var rect1 = elements[i].getBoundingClientRect();
                    for (var j = i + 1; j < elements.length; j++) {
                        var rect2 = elements[j].getBoundingClientRect();
                        if (!(rect1.right < rect2.left || 
                            rect1.left > rect2.right || 
                            rect1.bottom < rect2.top || 
                            rect1.top > rect2.bottom)) {
                            return true;
                        }
                    }
                }
                return false;
            """)
            
            if overlapping:
                issues.append(f"Overlapping elements at {width}x{height}")
        
        return issues

    def _generate_design_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights from website analysis."""
        insights = []
        
        # Analyze client website
        client_site = results['client_website']
        if client_site:
            insights.append("Current Website Analysis:")
            insights.extend(self._analyze_site_patterns(client_site))
        
        # Compare with competitors
        if results['competitor_websites']:
            insights.append("\nCompetitor Website Patterns:")
            competitor_patterns = []
            for comp in results['competitor_websites']:
                competitor_patterns.extend(self._analyze_site_patterns(comp))
            insights.extend(list(set(competitor_patterns)))
        
        return insights

    def _identify_improvements(self, results: Dict[str, Any]) -> List[str]:
        """Identify potential improvements based on analysis."""
        improvements = []
        
        client_site = results['client_website']
        competitor_sites = results['competitor_websites']
        
        if client_site:
            # Check responsive design
            if client_site.get('responsive_issues'):
                improvements.append("Improve responsive design implementation")
            
            # Check UI consistency
            if len(client_site.get('layout_patterns', [])) < 3:
                improvements.append("Enhance UI consistency across pages")
            
            # Compare with competitor features
            competitor_features = set()
            for comp in competitor_sites:
                for ui_comp in comp.get('ui_elements', []):
                    competitor_features.add(ui_comp['type'])
            
            client_features = set(ui_comp['type'] for ui_comp in client_site.get('ui_elements', []))
            missing_features = competitor_features - client_features
            
            if missing_features:
                improvements.append(f"Consider adding: {', '.join(missing_features)}")
        
        return improvements

    def _determine_navigation_type(self, soup: BeautifulSoup) -> str:
        """Determine the type of navigation used."""
        nav = soup.find('nav')
        if not nav:
            return 'No Navigation'
        
        if 'navbar-expand' in str(nav.get('class', [])):
            return 'Bootstrap Navbar'
        elif nav.find('div', class_='hamburger'):
            return 'Hamburger Menu'
        else:
            return 'Standard Navigation'

    def _analyze_content_structure(self, soup: BeautifulSoup) -> List[str]:
        """Analyze the content structure of the page."""
        structure = []
        
        if soup.find('main'):
            structure.append('Main Content Area')
        if soup.find('aside'):
            structure.append('Sidebar')
        if soup.find('article'):
            structure.append('Article Structure')
        if soup.find('section'):
            structure.append('Section Divisions')
        
        return structure

    def _detect_grid_system(self, soup: BeautifulSoup) -> str:
        """Detect the grid system being used."""
        if soup.find(class_=lambda x: x and 'container' in x):
            if soup.find(class_=lambda x: x and 'row' in x):
                return 'Bootstrap Grid'
            return 'Custom Container System'
        return 'No Grid System'

    def _analyze_button_styles(self, buttons) -> List[str]:
        """Analyze button styles."""
        styles = []
        for button in buttons:
            classes = button.get('class', [])
            if 'primary' in str(classes):
                styles.append('Primary')
            elif 'secondary' in str(classes):
                styles.append('Secondary')
            elif 'outline' in str(classes):
                styles.append('Outline')
        return list(set(styles))

    def _analyze_text_hierarchy(self, headings) -> Dict[str, int]:
        """Analyze text hierarchy."""
        hierarchy = {}
        for heading in headings:
            level = heading.name  # h1, h2, etc.
            hierarchy[level] = hierarchy.get(level, 0) + 1
        return hierarchy

    def _detect_media_queries(self, soup: BeautifulSoup) -> List[str]:
        """Detect media queries in stylesheets."""
        media_queries = []
        style_tags = soup.find_all('style')
        for style in style_tags:
            content = style.string
            if content and '@media' in content:
                media_queries.append('Custom Media Queries')
        
        # Check for responsive framework classes
        if soup.find(class_=lambda x: x and any(size in str(x) for size in ['sm-', 'md-', 'lg-', 'xl-'])):
            media_queries.append('Framework Responsive Classes')
        
        return media_queries

    def _analyze_site_patterns(self, site_data: Dict[str, Any]) -> List[str]:
        """Analyze patterns in a website's design and structure."""
        patterns = []
        
        # Analyze layout patterns
        if site_data.get('layout_patterns'):
            patterns.extend(site_data['layout_patterns'])
        
        # Analyze UI elements
        if site_data.get('ui_elements'):
            for element in site_data['ui_elements']:
                if element.get('frequency') == 'common':
                    patterns.append(f"Consistent {element['type']} implementation")
                if element.get('type') == 'button_styles' and element.get('styles'):
                    patterns.append(f"Standardized button styles: {', '.join(element['styles'])}")
        
        # Analyze responsive design
        if site_data.get('responsive_issues'):
            patterns.append("Responsive design needs improvement")
        else:
            patterns.append("Good responsive design implementation")
        
        # Analyze color scheme
        if site_data.get('color_scheme'):
            patterns.append(f"Consistent color palette with {len(site_data['color_scheme'])} primary colors")
        
        # Analyze page types
        page_types = set()
        for page in site_data.get('pages', []):
            if page.get('type'):
                page_types.add(page['type'])
        if page_types:
            patterns.append(f"Includes {', '.join(page_types)} pages")
        
        # Analyze navigation
        nav_types = set()
        for page in site_data.get('pages', []):
            if page.get('layout_elements', {}).get('navigation_type'):
                nav_types.add(page['layout_elements']['navigation_type'])
        if len(nav_types) == 1:
            patterns.append(f"Consistent {next(iter(nav_types))} navigation")
        elif len(nav_types) > 1:
            patterns.append("Inconsistent navigation types")
        
        return patterns