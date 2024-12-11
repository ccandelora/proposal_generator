import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse
import concurrent.futures
import time
import re

class WebsiteAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebsiteAnalyzer/1.0;)'
        })

    def process(self, website_url: str) -> Dict[str, Any]:
        """Analyze a website comprehensively."""
        try:
            self.logger.info(f"Starting comprehensive analysis of {website_url}")
            
            # Initialize results
            results = {
                'url': website_url,
                'pages': [],
                'overview': {},
                'content_analysis': {},
                'technical_analysis': {},
                'seo_analysis': {},
                'error': None
            }
            
            # Basic validation
            if not website_url:
                self.logger.error("No website URL provided")
                return {'error': 'No website URL provided'}
                
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
                results['url'] = website_url
            
            try:
                # Test connection first
                self.logger.info(f"Testing connection to {website_url}")
                response = self.session.get(website_url, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                self.logger.error(f"Failed to connect to website: {str(e)}")
                return {'error': f'Failed to connect to website: {str(e)}'}

            # Analyze homepage first
            self.logger.info("Analyzing homepage...")
            homepage_analysis = self._analyze_page(website_url)
            if homepage_analysis.get('error'):
                self.logger.error(f"Failed to analyze homepage: {homepage_analysis['error']}")
                return {'error': homepage_analysis['error']}
            
            results['pages'].append(homepage_analysis)
            
            # Get important pages to analyze
            self.logger.info("Discovering important pages...")
            important_urls = self._discover_important_pages(website_url, homepage_analysis.get('links', []))
            
            # Analyze important pages in parallel
            self.logger.info(f"Analyzing {len(important_urls)} additional pages...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {
                    executor.submit(self._analyze_page, url): url 
                    for url in important_urls
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        page_analysis = future.result()
                        if not page_analysis.get('error'):
                            results['pages'].append(page_analysis)
                            self.logger.info(f"Successfully analyzed {url}")
                        else:
                            self.logger.warning(f"Failed to analyze {url}: {page_analysis['error']}")
                    except Exception as e:
                        self.logger.error(f"Error analyzing {url}: {str(e)}")
            
            # Aggregate and analyze all collected data
            self.logger.info("Aggregating analysis results...")
            aggregated = self._aggregate_analysis(results['pages'])
            results.update(aggregated)
            
            # Validate completeness
            self._validate_analysis(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            return {'error': str(e)}

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize links from the page."""
        links = []
        seen = set()
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            # Normalize URL
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # Only include links from the same domain
            parsed = urlparse(href)
            if parsed.netloc != base_domain:
                continue
                
            # Remove fragments and normalize
            href = href.split('#')[0]
            if href and href not in seen:
                links.append(href)
                seen.add(href)
        
        return links

    def _discover_important_pages(self, base_url: str, links: List[str]) -> List[str]:
        """Identify important pages to analyze."""
        important_pages = set()
        base_domain = urlparse(base_url).netloc
        
        # Important page patterns
        important_patterns = [
            r'/about',
            r'/services',
            r'/contact',
            r'/team',
            r'/portfolio',
            r'/products',
            r'/features',
            r'/pricing',
            r'/faq',
            r'/support',
            r'/blog'
        ]
        
        for link in links:
            try:
                parsed = urlparse(link)
                if parsed.netloc != base_domain:
                    continue
                    
                path = parsed.path.lower()
                
                # Check if it's an important page
                if any(re.search(pattern, path) for pattern in important_patterns):
                    important_pages.add(link)
                    
            except Exception as e:
                self.logger.warning(f"Error processing link {link}: {str(e)}")
                continue
        
        # Limit the number of pages to analyze
        return list(important_pages)[:5]  # Analyze up to 5 important pages

    def _analyze_law_firm_specific(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze law firm specific features."""
        analysis = {
            'practice_areas': [],
            'attorneys': [],
            'firm_features': [],
            'client_resources': [],
            'contact_info': {}
        }
        
        # Practice area keywords
        practice_keywords = [
            'corporate law', 'business law', 'litigation', 'real estate',
            'employment law', 'intellectual property', 'patent', 'trademark',
            'family law', 'divorce', 'criminal defense', 'personal injury',
            'estate planning', 'probate', 'tax law', 'immigration',
            'civil rights', 'environmental law', 'healthcare law',
            'securities', 'mergers', 'acquisitions', 'bankruptcy'
        ]
        
        for page in pages:
            content = page.get('content', {}).get('text_content', '').lower()
            headers = page.get('headers', {})
            
            # Extract practice areas
            for keyword in practice_keywords:
                if keyword in content:
                    analysis['practice_areas'].append(keyword.title())
            
            # Extract attorney information
            if 'team' in page.get('type', '') or 'attorney' in page.get('type', ''):
                attorney_info = self._extract_attorney_info(page)
                analysis['attorneys'].extend(attorney_info)
            
            # Extract firm features
            features = self._extract_firm_features(page)
            analysis['firm_features'].extend(features)
            
            # Extract client resources
            resources = self._extract_client_resources(page)
            analysis['client_resources'].extend(resources)
            
            # Extract contact information
            contact = self._extract_contact_info(page)
            if contact:
                analysis['contact_info'].update(contact)
        
        # Remove duplicates
        analysis['practice_areas'] = list(set(analysis['practice_areas']))
        analysis['firm_features'] = list(set(analysis['firm_features']))
        analysis['client_resources'] = list(set(analysis['client_resources']))
        
        return {'law_firm_analysis': analysis}

    def _extract_attorney_info(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract attorney information from a page."""
        attorneys = []
        
        # Look for attorney sections
        attorney_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            term in str(x).lower() for term in ['attorney', 'lawyer', 'team', 'staff', 'professional']
        ))
        
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
            
            # Get education
            education_tag = section.find(text=re.compile(r'Education|Degrees?', re.I))
            if education_tag and education_tag.parent:
                education_list = education_tag.parent.find_next(['ul', 'p'])
                if education_list:
                    attorney['education'] = [
                        degree.strip() 
                        for degree in education_list.get_text().split('\n')
                        if degree.strip()
                    ]
            
            # Get contact info
            email = section.find('a', href=re.compile(r'mailto:'))
            if email:
                attorney['email'] = email['href'].replace('mailto:', '')
            
            phone = section.find('a', href=re.compile(r'tel:'))
            if phone:
                attorney['phone'] = phone['href'].replace('tel:', '')
            
            if attorney.get('name'):  # Only add if we found a name
                attorneys.append(attorney)
        
        return attorneys

    def _extract_firm_features(self, page: Dict[str, Any]) -> List[str]:
        """Extract law firm features from a page."""
        features = []
        content = page.get('content', {}).get('text_content', '').lower()
        
        feature_patterns = [
            (r'free consultation', 'Offers Free Consultation'),
            (r'24/7|around the clock', '24/7 Availability'),
            (r'contingency fee', 'Contingency Fee Available'),
            (r'virtual meeting|video conference', 'Virtual Consultations Available'),
            (r'multilingual|spanish|chinese', 'Multilingual Services'),
            (r'award[- ]winning', 'Award-Winning Firm'),
            (r'years of experience', 'Experienced Attorneys'),
            (r'client portal', 'Client Portal Available')
        ]
        
        for pattern, feature in feature_patterns:
            if re.search(pattern, content):
                features.append(feature)
        
        return features

    def _analyze_page(self, url: str) -> Dict[str, Any]:
        """Analyze a single page comprehensively."""
        try:
            self.logger.info(f"Analyzing page: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic page info
            page_info = {
                'url': url,
                'type': self._determine_page_type(url, soup),
                'title': soup.title.string if soup.title else None,
                'meta_description': self._get_meta_description(soup),
                'status_code': response.status_code,
                'load_time': response.elapsed.total_seconds()
            }
            
            # Content analysis
            page_info['content'] = self._analyze_content(soup)
            
            # Structure analysis
            page_info['structure'] = {
                'headers': self._analyze_headers(soup),
                'navigation': bool(soup.find('nav')),
                'footer': bool(soup.find('footer')),
                'sidebar': bool(soup.find(['aside', 'div'], class_=['sidebar', 'side-bar'])),
                'main_content': bool(soup.find('main'))
            }
            
            # Links and resources
            page_info['links'] = self._extract_links(soup, url)
            page_info['images'] = self._analyze_images(soup, url)
            page_info['forms'] = self._analyze_forms(soup)
            
            # Technical aspects
            page_info['technologies'] = self._detect_technologies(soup, response)
            page_info['performance_metrics'] = self._measure_performance(response)
            page_info['mobile_friendly'] = self._check_mobile_friendly(soup)
            page_info['accessibility'] = self._check_accessibility(soup)
            page_info['security_features'] = self._check_security_features(response)
            
            # Law firm specific analysis
            if 'attorney' in url.lower() or 'lawyer' in url.lower() or 'practice' in url.lower():
                page_info['attorney_info'] = self._extract_attorney_info(soup)
                page_info['practice_areas'] = self._extract_practice_areas_from_page(soup)
            
            return page_info
            
        except Exception as e:
            return {'error': str(e), 'url': url}

    def _extract_practice_areas_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Extract practice areas from a page."""
        practice_areas = set()
        
        # Common practice area keywords
        practice_keywords = [
            'corporate law', 'business law', 'litigation', 'real estate',
            'employment law', 'intellectual property', 'patent', 'trademark',
            'family law', 'divorce', 'criminal defense', 'personal injury',
            'estate planning', 'probate', 'tax law', 'immigration',
            'civil rights', 'environmental law', 'healthcare law',
            'securities', 'mergers', 'acquisitions', 'bankruptcy'
        ]
        
        # Look for practice areas in headers
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for header in headers:
            text = header.get_text().lower()
            for keyword in practice_keywords:
                if keyword in text:
                    practice_areas.add(keyword.title())
            
            # Check if this is a practice areas section
            if 'practice' in text or 'areas' in text:
                # Look for lists under this header
                next_element = header.find_next(['ul', 'ol'])
                if next_element:
                    for item in next_element.find_all('li'):
                        item_text = item.get_text().lower()
                        for keyword in practice_keywords:
                            if keyword in item_text:
                                practice_areas.add(keyword.title())
        
        # Look for practice areas in navigation
        nav = soup.find('nav')
        if nav:
            nav_items = nav.find_all('a')
            for item in nav_items:
                text = item.get_text().lower()
                for keyword in practice_keywords:
                    if keyword in text:
                        practice_areas.add(keyword.title())
        
        return list(practice_areas)

    def _aggregate_analysis(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate analysis from all pages."""
        if not pages:
            return {}
            
        # Calculate overview metrics
        overview = {
            'total_pages': len(pages),
            'average_load_time': sum(p.get('load_time', 0) for p in pages) / len(pages),
            'pages_analyzed': [p.get('url') for p in pages]
        }
        
        # Aggregate content metrics
        total_words = sum(p.get('content', {}).get('word_count', 0) for p in pages)
        total_images = sum(len(p.get('images', [])) for p in pages)
        total_forms = sum(len(p.get('forms', [])) for p in pages)
        
        content_analysis = {
            'total_words': total_words,
            'average_words_per_page': total_words / len(pages) if pages else 0,
            'total_images': total_images,
            'total_forms': total_forms
        }
        
        # Aggregate technical metrics
        technical_analysis = {
            'mobile_friendly': all(p.get('mobile_friendly', False) for p in pages),
            'average_load_time': sum(p.get('load_time', 0) for p in pages) / len(pages),
            'technologies_used': self._aggregate_technologies(pages)
        }
        
        # Aggregate SEO metrics
        seo_analysis = {
            'pages_with_meta_description': sum(1 for p in pages if p.get('meta_description')),
            'pages_with_title': sum(1 for p in pages if p.get('title')),
            'average_title_length': sum(len(p.get('title', '')) for p in pages) / len(pages) if pages else 0
        }

        # Add features analysis
        features = {
            'navigation': {
                'menu_present': any(p.get('structure', {}).get('navigation', False) for p in pages),
                'footer_present': any(p.get('structure', {}).get('footer', False) for p in pages),
                'sidebar_present': any(p.get('structure', {}).get('sidebar', False) for p in pages)
            },
            'functionality': {
                'forms_present': total_forms > 0,
                'search_functionality': any('search' in str(p.get('forms', [])).lower() for p in pages),
                'social_links': any('social' in str(p.get('links', [])).lower() for p in pages)
            },
            'content_features': {
                'multimedia_content': total_images > 0,
                'interactive_elements': any(p.get('forms', []) for p in pages),
                'structured_content': any(p.get('structure', {}).get('main_content', False) for p in pages)
            }
        }

        # Add user experience analysis
        user_experience = {
            'accessibility': {
                'alt_texts': sum(img.get('has_alt', False) for p in pages for img in p.get('images', [])),
                'form_labels': sum(len(form.get('fields', [])) for p in pages for form in p.get('forms', [])),
                'semantic_structure': any(p.get('structure', {}).get('main_content', False) for p in pages)
            },
            'performance': {
                'load_time_score': self._calculate_performance_score(pages),
                'mobile_friendly': technical_analysis['mobile_friendly'],
                'responsive_design': all(p.get('mobile_friendly', False) for p in pages)
            },
            'usability': {
                'clear_navigation': features['navigation']['menu_present'],
                'consistent_layout': len(set(p.get('type', '') for p in pages)) > 1,
                'readable_content': content_analysis['average_words_per_page'] > 0
            }
        }
        
        return {
            'overview': overview,
            'content_analysis': content_analysis,
            'technical_analysis': technical_analysis,
            'seo_analysis': seo_analysis,
            'features': features,
            'user_experience': user_experience
        }
        
    def _aggregate_technologies(self, pages: List[Dict[str, Any]]) -> List[str]:
        """Aggregate technologies used across all pages."""
        technologies = set()
        for page in pages:
            technologies.update(page.get('technologies', []))
        return list(technologies)

    def _validate_analysis(self, results: Dict[str, Any]) -> None:
        """Validate that all necessary analysis components are present and complete."""
        required_sections = [
            'pages', 'features', 'technical_analysis', 
            'content_analysis', 'user_experience'
        ]
        
        missing_sections = [
            section for section in required_sections 
            if not results.get(section)
        ]
        
        if missing_sections:
            self.logger.warning(f"Incomplete analysis. Missing sections: {missing_sections}")
            results['warnings'] = f"Incomplete analysis in sections: {', '.join(missing_sections)}"

    # Helper methods for specific analyses
    def _determine_page_type(self, url: str, soup: BeautifulSoup) -> str:
        """Determine the type of page based on URL and content."""
        url_lower = url.lower()
        if '/about' in url_lower:
            return 'about'
        elif '/contact' in url_lower:
            return 'contact'
        elif '/practice' in url_lower or '/services' in url_lower:
            return 'practice_areas'
        elif '/attorney' in url_lower or '/team' in url_lower:
            return 'team'
        elif '/case' in url_lower or '/result' in url_lower:
            return 'case_studies'
        else:
            return 'general'

    def _extract_practice_areas(self, pages: List[Dict[str, Any]]) -> List[str]:
        """Extract practice areas from pages."""
        practice_areas = set()
        for page in pages:
            if page.get('type') == 'practice_areas':
                # Extract from headers and content
                headers = page.get('headers', {})
                for header in headers.values():
                    if any(keyword in header.lower() for keyword in ['law', 'legal', 'litigation']):
                        practice_areas.add(header)
        return list(practice_areas)

    def _extract_team_info(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract information about the legal team."""
        team_info = {
            'attorneys': [],
            'support_staff': [],
            'expertise_areas': set()
        }
        
        for page in pages:
            if page.get('type') in ['team', 'about']:
                # Process team member information
                content = page.get('content', {})
                # Implementation details for extracting team information
                pass
                
        return team_info

    def _analyze_content_quality(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the quality of content across pages."""
        return {
            'readability_score': self._calculate_readability_score(pages),
            'content_depth': self._analyze_content_depth(pages),
            'expertise_signals': self._analyze_expertise_signals(pages)
        }

    def _calculate_security_score(self, pages: List[Dict[str, Any]]) -> float:
        """Calculate overall security score."""
        security_features = [
            page.get('security_features', {})
            for page in pages
        ]
        
        # Scoring logic for security features
        return sum(1 for features in security_features if features.get('https', False)) / len(pages)

    def _calculate_performance_score(self, pages: List[Dict[str, Any]]) -> float:
        """Calculate a performance score based on load times and other metrics."""
        if not pages:
            return 0.0
            
        # Calculate average load time
        load_times = [p.get('load_time', float('inf')) for p in pages]
        avg_load_time = sum(load_times) / len(load_times)
        
        # Score based on load time (0-40 points)
        # Under 2 seconds is excellent (40 points)
        # Over 8 seconds is poor (0 points)
        load_time_score = max(0, min(40, 40 * (1 - avg_load_time / 8)))
        
        # Score based on mobile friendliness (0-30 points)
        mobile_score = 30 if all(p.get('mobile_friendly', False) for p in pages) else 0
        
        # Score based on content optimization (0-30 points)
        content_scores = []
        for page in pages:
            page_score = 0
            # Check images
            if page.get('images'):
                images_with_alt = sum(1 for img in page['images'] if img.get('has_alt'))
                total_images = len(page['images'])
                if total_images > 0:
                    page_score += 10 * (images_with_alt / total_images)
            
            # Check structure
            if page.get('structure', {}).get('main_content'):
                page_score += 10
            
            # Check load time
            if page.get('load_time', float('inf')) < 3:
                page_score += 10
                
            content_scores.append(page_score)
        
        avg_content_score = sum(content_scores) / len(content_scores) if content_scores else 0
        
        # Calculate final score (0-100)
        total_score = load_time_score + mobile_score + avg_content_score
        
        return round(total_score, 2)

    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from the page."""
        meta = soup.find('meta', {'name': 'description'})
        return meta.get('content') if meta else ''

    def _analyze_headers(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Analyze headers with focus on law firm content."""
        headers = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            if h_tags:
                headers[f'h{i}'] = []
                for tag in h_tags:
                    text = tag.get_text().strip()
                    if text:
                        headers[f'h{i}'].append(text)
                        # Look for practice areas in headers
                        if any(term in text.lower() for term in ['practice', 'expertise', 'services']):
                            parent = tag.find_parent(['div', 'section'])
                            if parent:
                                areas = parent.find_all(['li', 'p'])
                                headers[f'{h_tags}_practice_areas'] = [
                                    area.get_text().strip() 
                                    for area in areas
                                ]
        return headers

    def _analyze_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page content."""
        text_content = soup.get_text(' ', strip=True)
        words = text_content.split()
        
        return {
            'text_content': text_content,
            'word_count': len(words),
            'paragraphs': len(soup.find_all('p')),
            'lists': len(soup.find_all(['ul', 'ol'])),
            'headings': self._analyze_headers(soup)
        }
        
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Analyze images on the page."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                    
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                    'has_alt': bool(img.get('alt'))
                })
        return images
        
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze forms on the page."""
        forms = []
        for form in soup.find_all('form'):
            form_info = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'fields': [],
                'has_submit': False
            }
            
            # Analyze form fields
            for field in form.find_all(['input', 'textarea', 'select']):
                if field.get('type') == 'submit':
                    form_info['has_submit'] = True
                else:
                    form_info['fields'].append({
                        'type': field.get('type', 'text'),
                        'name': field.get('name', ''),
                        'required': field.get('required') is not None
                    })
                    
            forms.append(form_info)
        return forms
        
    def _detect_technologies(self, soup: BeautifulSoup, response: requests.Response) -> List[str]:
        """Detect technologies used on the website."""
        technologies = set()
        
        # Check headers
        headers = response.headers
        if headers.get('Server'):
            technologies.add(f"Server: {headers['Server']}")
        if headers.get('X-Powered-By'):
            technologies.add(f"Powered by: {headers['X-Powered-By']}")
            
        # Check for common frameworks and libraries
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src', '')
            if 'jquery' in src.lower():
                technologies.add('jQuery')
            elif 'bootstrap' in src.lower():
                technologies.add('Bootstrap')
            elif 'react' in src.lower():
                technologies.add('React')
            elif 'vue' in src.lower():
                technologies.add('Vue.js')
            elif 'angular' in src.lower():
                technologies.add('Angular')
                
        # Check for CMS indicators
        if soup.find(class_=lambda x: x and 'wordpress' in x.lower()):
            technologies.add('WordPress')
        elif soup.find(class_=lambda x: x and 'drupal' in x.lower()):
            technologies.add('Drupal')
        elif soup.find(class_=lambda x: x and 'joomla' in x.lower()):
            technologies.add('Joomla')
            
        return list(technologies)
        
    def _measure_performance(self, response: requests.Response) -> Dict[str, float]:
        """Measure basic performance metrics."""
        return {
            'load_time': response.elapsed.total_seconds(),
            'content_size': len(response.content),
            'response_time': response.elapsed.total_seconds()
        }
        
    def _check_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        """Check if the page appears to be mobile-friendly."""
        viewport = soup.find('meta', {'name': 'viewport'})
        responsive_meta = viewport and 'width=device-width' in viewport.get('content', '').lower()
        
        # Check for responsive classes
        responsive_classes = soup.find_all(class_=lambda x: x and any(
            term in str(x).lower() 
            for term in ['mobile', 'responsive', 'sm-', 'md-', 'lg-', 'xl-']
        ))
        
        # Check for media queries in style tags
        media_queries = any(
            'media' in style.string.lower() 
            for style in soup.find_all('style') 
            if style.string
        )
        
        return bool(responsive_meta or responsive_classes or media_queries)
        
    def _check_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Check basic accessibility features."""
        return {
            'images_with_alt': sum(1 for img in soup.find_all('img') if img.get('alt')),
            'form_labels': sum(1 for label in soup.find_all('label')),
            'aria_attributes': sum(1 for tag in soup.find_all() if any(attr.startswith('aria-') for attr in tag.attrs)),
            'skip_links': bool(soup.find('a', href='#main-content'))
        }
        
    def _check_security_features(self, response: requests.Response) -> Dict[str, bool]:
        """Check security features from response headers."""
        headers = response.headers
        return {
            'https': response.url.startswith('https'),
            'hsts': bool(headers.get('Strict-Transport-Security')),
            'xss_protection': bool(headers.get('X-XSS-Protection')),
            'content_security': bool(headers.get('Content-Security-Policy')),
            'x_frame_options': bool(headers.get('X-Frame-Options'))
        }