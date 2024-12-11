from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SEOAnalyzer(BaseAgent):
    """Analyzes websites for SEO optimization."""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze website SEO.
        
        Args:
            data: Dictionary containing website URL and analysis options
            
        Returns:
            Dictionary containing SEO analysis results
        """
        try:
            url = data.get('website')
            if not url:
                return {'error': 'No website URL provided'}
            
            return self.analyze_seo(url)
        except Exception as e:
            return self._handle_error(e, "SEO analysis")

    def analyze_seo(self, url: str) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis of a website."""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic SEO elements
            title = soup.title.string if soup.title else None
            meta_description = soup.find('meta', {'name': 'description'})
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            
            # Heading structure
            headings = {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4')),
                'h5': len(soup.find_all('h5')),
                'h6': len(soup.find_all('h6'))
            }
            
            # Image optimization
            images = soup.find_all('img')
            image_analysis = {
                'total': len(images),
                'missing_alt': len([img for img in images if not img.get('alt')])
            }
            
            # Link analysis
            links = soup.find_all('a')
            internal_links = [link for link in links if link.get('href', '').startswith(('/')) or url in link.get('href', '')]
            external_links = [link for link in links if link.get('href', '').startswith(('http', 'https')) and url not in link.get('href', '')]
            
            # Mobile optimization
            viewport_meta = soup.find('meta', {'name': 'viewport'})
            responsive_meta = bool(viewport_meta and 'width=device-width' in viewport_meta.get('content', ''))
            
            # Social media meta tags
            og_tags = {tag.get('property'): tag.get('content') for tag in soup.find_all('meta', property=lambda x: x and x.startswith('og:'))}
            twitter_tags = {tag.get('name'): tag.get('content') for tag in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})}
            
            # Schema markup
            schema_tags = soup.find_all('script', type='application/ld+json')
            
            return {
                'basic_seo': {
                    'title': title,
                    'title_length': len(title) if title else 0,
                    'meta_description': meta_description.get('content') if meta_description else None,
                    'meta_description_length': len(meta_description.get('content', '')) if meta_description else 0,
                    'meta_keywords': meta_keywords.get('content') if meta_keywords else None
                },
                'heading_structure': headings,
                'images': image_analysis,
                'links': {
                    'total': len(links),
                    'internal': len(internal_links),
                    'external': len(external_links)
                },
                'mobile_optimization': {
                    'viewport_meta_tag': bool(viewport_meta),
                    'responsive_meta_tag': responsive_meta
                },
                'social_media': {
                    'open_graph': og_tags,
                    'twitter_cards': twitter_tags
                },
                'structured_data': {
                    'schema_markup_present': bool(schema_tags),
                    'schema_types': len(schema_tags)
                },
                'recommendations': self._generate_recommendations({
                    'title_length': len(title) if title else 0,
                    'meta_description_length': len(meta_description.get('content', '')) if meta_description else 0,
                    'has_keywords': bool(meta_keywords),
                    'missing_alt_images': image_analysis['missing_alt'],
                    'has_h1': headings['h1'] > 0,
                    'has_schema': bool(schema_tags),
                    'has_social_tags': bool(og_tags or twitter_tags)
                })
            }
        except Exception as e:
            logger.warning(f"Error analyzing SEO for {url}: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate SEO recommendations based on analysis."""
        recommendations = []
        
        if metrics['title_length'] < 30 or metrics['title_length'] > 60:
            recommendations.append("Optimize title length (recommended: 30-60 characters)")
            
        if metrics['meta_description_length'] < 120 or metrics['meta_description_length'] > 160:
            recommendations.append("Optimize meta description length (recommended: 120-160 characters)")
            
        if not metrics['has_keywords']:
            recommendations.append("Add meta keywords to improve search engine understanding")
            
        if metrics['missing_alt_images'] > 0:
            recommendations.append(f"Add alt text to {metrics['missing_alt_images']} images")
            
        if not metrics['has_h1']:
            recommendations.append("Add H1 heading for main page title")
            
        if not metrics['has_schema']:
            recommendations.append("Implement schema markup for better search engine understanding")
            
        if not metrics['has_social_tags']:
            recommendations.append("Add Open Graph and Twitter Card meta tags for better social sharing")
        
        return recommendations 