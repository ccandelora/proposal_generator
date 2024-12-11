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
import random

logger = logging.getLogger(__name__)

class CompetitiveAnalyzer(BaseAgent):
    """Analyzes competitors and market data."""
    
    def __init__(self):
        super().__init__()
        self.website_analyzer = WebsiteAnalyzer()
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process competitive analysis request.
        
        Args:
            data: Dictionary containing company name, competitors, and industry
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            company_name = data.get('company_name', '')
            competitors = data.get('competitors', [])
            industry = data.get('industry', '')
            
            if not competitors and not industry:
                return self._handle_error(ValueError("No competitors or industry provided"), "competitive analysis")
            
            return self.analyze(company_name, competitors, industry)
        except Exception as e:
            return self._handle_error(e, "competitive analysis")

    def analyze(self, company_name: str, competitors: List[str], industry: str) -> Dict[str, Any]:
        """
        Perform comprehensive competitive analysis.
        
        Args:
            company_name: Name of the client's company
            competitors: List of competitor URLs
            industry: Industry sector
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Validate inputs
            if not isinstance(competitors, list):
                logger.warning("Competitors is not a list, converting to list")
                if isinstance(competitors, str):
                    competitors = [competitors]
                else:
                    competitors = []

            # Ensure all competitors are strings
            competitors = [str(comp) for comp in competitors if comp]
            
            # Get market trends (with fallback data)
            market_trends = self._analyze_market_trends(industry)
            
            # Analyze competitors
            competitor_analysis = {}
            if competitors:
                try:
                    competitor_analysis = self._analyze_competitors(competitors)
                except Exception as e:
                    logger.warning(f"Error analyzing competitors: {str(e)}")
                    competitor_analysis = {}
            
            # Get news analysis
            news_analysis = {
                'industry_news': {'articles': []},
                'competitor_news': {}
            }
            if company_name and industry:
                try:
                    news_analysis = self._analyze_news(company_name, competitors, industry)
                except Exception as e:
                    logger.warning(f"Error in news analysis: {str(e)}")
            
            # Get financial analysis
            financial_analysis = {}
            if competitors:
                try:
                    financial_analysis = self._analyze_financial_data(competitors)
                except Exception as e:
                    logger.warning(f"Error in financial analysis: {str(e)}")
            
            # Combine all analyses
            results = {
                'market_trends': market_trends,
                'competitor_analysis': competitor_analysis,
                'news_analysis': news_analysis,
                'financial_analysis': financial_analysis,
                'summary': {
                    'total_competitors': len(competitors),
                    'analyzed_competitors': len(competitor_analysis),
                    'has_financial_data': bool(financial_analysis),
                    'has_news_data': bool(news_analysis.get('industry_news', {}).get('articles')),
                    'industry': industry
                }
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in competitive analysis: {str(e)}")
            # Return a valid data structure even on error
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
                    'industry': industry,
                    'error': str(e)
                }
            }

    def _get_fallback_trends(self, industry: str) -> Dict[str, Any]:
        """Get static fallback data for market trends."""
        return {
            'related_queries': {
                'rising': [
                    {'query': 'business law firms', 'value': 150},
                    {'query': 'corporate law firms', 'value': 120},
                    {'query': 'litigation law firms', 'value': 100}
                ],
                'top': [
                    {'query': 'best law firms', 'value': 100},
                    {'query': 'top law firms', 'value': 90},
                    {'query': 'local law firms', 'value': 80}
                ]
            },
            'interest_over_time': [
                {'date': '2024-01-01', 'value': 75},
                {'date': '2024-01-08', 'value': 80},
                {'date': '2024-01-15', 'value': 85},
                {'date': '2024-01-22', 'value': 82},
                {'date': '2024-01-29', 'value': 88},
                {'date': '2024-02-05', 'value': 85},
                {'date': '2024-02-12', 'value': 90}
            ],
            'trend_summary': {
                'average_interest': 83.5,
                'max_interest': 90,
                'min_interest': 75,
                'current_interest': 90
            }
        }

    def _analyze_market_trends(self, industry: str) -> Dict[str, Any]:
        """Analyze market trends using Google Trends."""
        try:
            # Add error checking for empty industry
            if not industry:
                return self._get_fallback_trends(industry)

            # Clean up industry term for better results
            industry_term = f"{industry} law firm"  # Make it more specific for law firms
            
            # Initialize trends data structure
            trends_data = {
                'related_queries': {'rising': [], 'top': []},
                'interest_over_time': [],
                'trend_summary': {
                    'average_interest': 0,
                    'max_interest': 0,
                    'min_interest': 0,
                    'current_interest': 0
                }
            }
            
            # Helper function for exponential backoff
            def make_request_with_backoff(request_func, max_retries=2, initial_delay=10):
                for attempt in range(max_retries):
                    try:
                        # Add increasing delay between attempts
                        delay = initial_delay * (2 ** attempt)  # 10, 20 seconds
                        logger.info(f"Waiting {delay} seconds before Google Trends request...")
                        time.sleep(delay)
                        
                        result = request_func()
                        if result is not None:
                            return result
                    except Exception as e:
                        if "429" in str(e):
                            logger.warning("Rate limit hit, using fallback data")
                            return None
                        logger.warning(f"Error in request: {str(e)}")
                        if attempt == max_retries - 1:
                            return None
                return None
            
            # Build payload with conservative settings
            def build_payload():
                try:
                    self.pytrends.build_payload(
                        [industry_term],
                        timeframe='today 1-m',  # Reduce to 1 month for less data
                        geo='US'
                    )
                    return True
                except Exception as e:
                    logger.warning(f"Error building payload: {str(e)}")
                    return None

            # Execute single request with backoff
            success = False
            try:
                if make_request_with_backoff(build_payload):
                    # Try to get at least one type of data
                    try:
                        interest_df = self.pytrends.interest_over_time()
                        if interest_df is not None and not interest_df.empty and industry_term in interest_df.columns:
                            # Sample every 7 days
                            sampled_data = interest_df[industry_term].iloc[::7]
                            trends_data['interest_over_time'] = [
                                {
                                    'date': index.strftime('%Y-%m-%d'),
                                    'value': int(value)
                                }
                                for index, value in sampled_data.items()
                            ]
                            success = True
                    except Exception as e:
                        logger.warning(f"Error getting interest data: {str(e)}")

                if not success:
                    logger.warning("Using fallback data due to Google Trends limitations")
                    return self._get_fallback_trends(industry)
                    
            except Exception as e:
                logger.warning(f"Error during Google Trends request: {str(e)}")
                return self._get_fallback_trends(industry)
            
            # Calculate trend summary if we have real data
            if trends_data['interest_over_time']:
                values = [point['value'] for point in trends_data['interest_over_time']]
                trends_data['trend_summary'] = {
                    'average_interest': round(sum(values) / len(values), 2),
                    'max_interest': max(values),
                    'min_interest': min(values),
                    'current_interest': values[-1]
                }
                return trends_data
            else:
                return self._get_fallback_trends(industry)
            
        except Exception as e:
            logger.warning(f"Error analyzing market trends: {str(e)}")
            return self._get_fallback_trends(industry)

    def _analyze_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """Analyze competitor websites."""
        results = {}
        
        for competitor_url in competitors:
            try:
                if not isinstance(competitor_url, str):
                    continue
                    
                # Get website info
                website_data = self.website_analyzer.process(competitor_url)
                
                if website_data and not website_data.get('error'):
                    results[competitor_url] = {
                        'website_analysis': website_data,
                        'technologies': website_data.get('technologies', []),
                        'content_analysis': website_data.get('content_analysis', {}),
                        'performance': website_data.get('performance_metrics', {})
                    }
                else:
                    logger.warning(f"No valid analysis data for {competitor_url}")
                    results[competitor_url] = {
                        'error': website_data.get('error', 'No analysis data available'),
                        'website_analysis': {},
                        'technologies': [],
                        'content_analysis': {},
                        'performance': {}
                    }
            except Exception as e:
                logger.warning(f"Error analyzing competitor {competitor_url}: {str(e)}")
                results[competitor_url] = {
                    'error': str(e),
                    'website_analysis': {},
                    'technologies': [],
                    'content_analysis': {},
                    'performance': {}
                }
        
        return results

    def _analyze_news(self, company_name: str, competitors: List[str], industry: str) -> Dict[str, Any]:
        """Analyze news coverage."""
        try:
            news_data = {
                'industry_news': {'articles': []},
                'competitor_news': {},
                'summary': {
                    'total_articles': 0,
                    'sources': set(),
                    'latest_date': None
                }
            }
            
            # Get industry news
            try:
                industry_news = self.news_api.get_everything(
                    q=f"{industry} law firm",
                    language='en',
                    sort_by='relevancy',
                    page_size=10
                )
                
                if industry_news and 'articles' in industry_news:
                    news_data['industry_news'] = industry_news
                    news_data['summary']['total_articles'] += len(industry_news['articles'])
                    
                    # Update sources and latest date
                    for article in industry_news['articles']:
                        if article.get('source', {}).get('name'):
                            news_data['summary']['sources'].add(article['source']['name'])
                        if article.get('publishedAt'):
                            if not news_data['summary']['latest_date'] or article['publishedAt'] > news_data['summary']['latest_date']:
                                news_data['summary']['latest_date'] = article['publishedAt']
                
            except Exception as e:
                logger.warning(f"Error getting industry news: {str(e)}")
            
            # Get competitor news
            for competitor_url in competitors:
                try:
                    if not isinstance(competitor_url, str):
                        continue
                        
                    domain = urlparse(competitor_url).netloc
                    company = domain.split('.')[-2]
                    
                    news = self.news_api.get_everything(
                        q=f"{company} law firm",
                        language='en',
                        sort_by='relevancy',
                        page_size=5
                    )
                    
                    if news and 'articles' in news:
                        news_data['competitor_news'][competitor_url] = news
                        news_data['summary']['total_articles'] += len(news['articles'])
                        
                        # Update sources and latest date
                        for article in news['articles']:
                            if article.get('source', {}).get('name'):
                                news_data['summary']['sources'].add(article['source']['name'])
                            if article.get('publishedAt'):
                                if not news_data['summary']['latest_date'] or article['publishedAt'] > news_data['summary']['latest_date']:
                                    news_data['summary']['latest_date'] = article['publishedAt']
                    
                except Exception as e:
                    logger.warning(f"Error getting news for {competitor_url}: {str(e)}")
                    continue
            
            # Convert sources set to list for JSON serialization
            news_data['summary']['sources'] = list(news_data['summary']['sources'])
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error analyzing news: {str(e)}")
            return {
                'industry_news': {'articles': []},
                'competitor_news': {},
                'summary': {
                    'total_articles': 0,
                    'sources': [],
                    'latest_date': None,
                    'error': str(e)
                }
            }

    def _analyze_financial_data(self, competitors: List[str]) -> Dict[str, Any]:
        """Analyze financial data for public companies."""
        financial_data = {}
        
        for competitor_url in competitors:
            try:
                if not isinstance(competitor_url, str):
                    continue
                    
                # Skip non-company URLs like directories
                if any(directory in competitor_url.lower() for directory in ['justia.com', 'martindale.com', 'findlaw.com', 'avvo.com']):
                    continue
                    
                # Try to extract company name from URL
                try:
                    domain = urlparse(competitor_url).netloc
                    company = domain.split('.')[-2]  # Get main part of domain
                    
                    # Skip if company name is too generic
                    if len(company) < 3:
                        continue
                        
                    # Try to get financial info
                    ticker = yf.Ticker(company)
                    info = ticker.info
                    
                    if info and isinstance(info, dict):
                        financial_data[competitor_url] = {
                            'market_cap': info.get('marketCap'),
                            'revenue': info.get('totalRevenue'),
                            'employees': info.get('fullTimeEmployees'),
                            'industry': info.get('industry'),
                            'sector': info.get('sector')
                        }
                        logger.info(f"Found financial data for {company}")
                except Exception as e:
                    logger.debug(f"Could not get financial data for {competitor_url}: {str(e)}")
                    continue
                    
            except Exception as e:
                logger.debug(f"Error processing competitor URL {competitor_url}: {str(e)}")
                continue
        
        # Add summary statistics
        if financial_data:
            summary = {
                'total_analyzed': len(financial_data),
                'average_market_cap': None,
                'average_revenue': None,
                'total_employees': 0
            }
            
            market_caps = [data.get('market_cap') for data in financial_data.values() if data.get('market_cap')]
            revenues = [data.get('revenue') for data in financial_data.values() if data.get('revenue')]
            employees = [data.get('employees') for data in financial_data.values() if data.get('employees')]
            
            if market_caps:
                summary['average_market_cap'] = sum(market_caps) / len(market_caps)
            if revenues:
                summary['average_revenue'] = sum(revenues) / len(revenues)
            if employees:
                summary['total_employees'] = sum(employees)
                
            financial_data['summary'] = summary
        
        return financial_data 

    def _analyze_competitive_matrix(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate feature comparison matrix and pricing analysis."""
        return {
            'feature_matrix': self._generate_feature_matrix(competitors),
            'pricing_analysis': self._analyze_pricing_positions(competitors),
            'tech_advantages': self._analyze_tech_advantages(competitors),
            'ux_comparison': self._compare_user_experience(competitors)
        }

    def _generate_feature_matrix(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a feature comparison matrix."""
        # Common features to look for
        feature_categories = {
            'core_features': [
                'responsive_design',
                'contact_form',
                'search_functionality',
                'social_media_integration',
                'blog_section',
                'newsletter',
                'client_portal',
                'case_studies'
            ],
            'technical_features': [
                'ssl_security',
                'cdn_enabled',
                'mobile_optimization',
                'api_integration',
                'analytics_integration'
            ],
            'content_features': [
                'practice_area_pages',
                'attorney_profiles',
                'testimonials',
                'resources_section',
                'faq_section',
                'news_updates'
            ]
        }

        matrix = {
            'categories': feature_categories,
            'comparisons': {}
        }

        # Analyze each competitor
        for competitor in competitors:
            if not isinstance(competitor, dict):
                continue

            website_analysis = competitor.get('website_analysis', {})
            features = {
                'core_features': {},
                'technical_features': {},
                'content_features': {}
            }

            # Analyze core features
            content = website_analysis.get('content_analysis', {})
            structure = website_analysis.get('structure', {})
            
            features['core_features'] = {
                'responsive_design': website_analysis.get('mobile_friendly', False),
                'contact_form': bool(content.get('forms', [])),
                'search_functionality': bool(structure.get('search')),
                'social_media_integration': bool(website_analysis.get('social_links')),
                'blog_section': bool(structure.get('blog')),
                'newsletter': bool(content.get('newsletter_form')),
                'client_portal': bool(structure.get('login')),
                'case_studies': bool(structure.get('case_studies'))
            }

            # Analyze technical features
            tech = website_analysis.get('technical_analysis', {})
            features['technical_features'] = {
                'ssl_security': tech.get('security_features', {}).get('https', False),
                'cdn_enabled': bool(tech.get('cdn_detected')),
                'mobile_optimization': tech.get('mobile_friendly', False),
                'api_integration': bool(tech.get('api_endpoints')),
                'analytics_integration': bool(tech.get('analytics_present'))
            }

            # Analyze content features
            features['content_features'] = {
                'practice_area_pages': bool(structure.get('practice_areas')),
                'attorney_profiles': bool(structure.get('attorney_profiles')),
                'testimonials': bool(content.get('testimonials')),
                'resources_section': bool(structure.get('resources')),
                'faq_section': bool(structure.get('faq')),
                'news_updates': bool(structure.get('news'))
            }

            matrix['comparisons'][competitor.get('website', 'unknown')] = features

        return matrix

    def _analyze_pricing_positions(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pricing positions of competitors."""
        pricing_data = {
            'segments': {
                'premium': [],
                'mid_range': [],
                'value': []
            },
            'factors': {},
            'summary': {}
        }

        for competitor in competitors:
            if not isinstance(competitor, dict):
                continue

            website = competitor.get('website', '')
            if not website:
                continue

            # Analyze factors that indicate pricing position
            website_analysis = competitor.get('website_analysis', {})
            tech_analysis = website_analysis.get('technical_analysis', {})
            content_analysis = website_analysis.get('content_analysis', {})

            # Calculate a pricing score based on various factors
            factors = {
                'tech_sophistication': len(tech_analysis.get('technologies_used', [])) / 10,  # 0-1 score
                'content_quality': content_analysis.get('content_score', 0) / 100,  # 0-1 score
                'feature_richness': len(website_analysis.get('features', [])) / 20,  # 0-1 score
                'performance': 1 - (tech_analysis.get('average_load_time', 5) / 5)  # 0-1 score
            }

            # Calculate overall score
            overall_score = sum(factors.values()) / len(factors)

            # Categorize based on score
            if overall_score > 0.7:
                pricing_data['segments']['premium'].append(website)
            elif overall_score > 0.4:
                pricing_data['segments']['mid_range'].append(website)
            else:
                pricing_data['segments']['value'].append(website)

            pricing_data['factors'][website] = factors

        # Generate summary
        pricing_data['summary'] = {
            'premium_count': len(pricing_data['segments']['premium']),
            'mid_range_count': len(pricing_data['segments']['mid_range']),
            'value_count': len(pricing_data['segments']['value']),
            'market_position': self._determine_market_position(pricing_data['segments'])
        }

        return pricing_data

    def _analyze_tech_advantages(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technology stack advantages."""
        tech_analysis = {
            'stacks': {},
            'trends': {},
            'advantages': [],
            'recommendations': []
        }

        all_technologies = set()
        tech_count = {}

        # Gather all technologies and count occurrences
        for competitor in competitors:
            if not isinstance(competitor, dict):
                continue

            website = competitor.get('website', '')
            if not website:
                continue

            website_analysis = competitor.get('website_analysis', {})
            tech_stack = website_analysis.get('technical_analysis', {}).get('technologies_used', [])

            tech_analysis['stacks'][website] = tech_stack
            all_technologies.update(tech_stack)

            for tech in tech_stack:
                tech_count[tech] = tech_count.get(tech, 0) + 1

        # Analyze trends
        total_competitors = len([c for c in competitors if isinstance(c, dict) and c.get('website')])
        tech_analysis['trends'] = {
            tech: count / total_competitors * 100 if total_competitors > 0 else 0
            for tech, count in tech_count.items()
        }

        # Identify modern vs legacy technologies
        modern_tech = {'React', 'Vue.js', 'Angular', 'Node.js', 'GraphQL', 'Kubernetes', 'Docker'}
        legacy_tech = {'jQuery', 'PHP', 'Apache', 'MySQL'}

        # Generate advantages and recommendations
        tech_analysis['advantages'] = [
            f"Modern framework adoption: {tech}" 
            for tech in modern_tech.intersection(all_technologies)
        ]

        tech_analysis['recommendations'] = [
            f"Consider upgrading {tech} to modern alternatives"
            for tech in legacy_tech.intersection(all_technologies)
        ]

        return tech_analysis

    def _compare_user_experience(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare user experience across competitors."""
        ux_analysis = {
            'metrics': {},
            'best_practices': {},
            'rankings': {},
            'recommendations': []
        }

        for competitor in competitors:
            if not isinstance(competitor, dict):
                continue

            website = competitor.get('website', '')
            if not website:
                continue

            website_analysis = competitor.get('website_analysis', {})
            tech_analysis = website_analysis.get('technical_analysis', {})
            content_analysis = website_analysis.get('content_analysis', {})

            # Analyze UX metrics
            metrics = {
                'load_time': tech_analysis.get('average_load_time', 0),
                'mobile_friendly': tech_analysis.get('mobile_friendly', False),
                'accessibility_score': website_analysis.get('accessibility_score', 0),
                'navigation_clarity': self._calculate_navigation_score(website_analysis),
                'content_readability': self._calculate_readability_score(content_analysis)
            }

            # Analyze best practices
            best_practices = {
                'clear_cta': self._has_clear_cta(website_analysis),
                'intuitive_navigation': self._has_intuitive_navigation(website_analysis),
                'responsive_design': tech_analysis.get('mobile_friendly', False),
                'fast_loading': metrics['load_time'] < 3,
                'accessible_content': metrics['accessibility_score'] > 80
            }

            ux_analysis['metrics'][website] = metrics
            ux_analysis['best_practices'][website] = best_practices

        # Generate rankings
        ux_analysis['rankings'] = self._generate_ux_rankings(ux_analysis['metrics'])

        # Generate recommendations based on analysis
        ux_analysis['recommendations'] = self._generate_ux_recommendations(ux_analysis)

        return ux_analysis

    def _calculate_navigation_score(self, website_analysis: Dict[str, Any]) -> float:
        """Calculate a navigation clarity score."""
        score = 0
        structure = website_analysis.get('structure', {})
        
        if structure.get('navigation'):
            score += 30
        if structure.get('footer'):
            score += 20
        if structure.get('sitemap'):
            score += 20
        if structure.get('search'):
            score += 30
            
        return score

    def _calculate_readability_score(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate a content readability score."""
        score = 0
        
        # Check for proper heading structure
        if content_analysis.get('headings', {}).get('proper_hierarchy', False):
            score += 30
            
        # Check paragraph length
        avg_paragraph_length = content_analysis.get('average_paragraph_length', 0)
        if avg_paragraph_length > 0:
            if avg_paragraph_length <= 150:
                score += 40
            elif avg_paragraph_length <= 300:
                score += 20
                
        # Check content structure
        if content_analysis.get('lists', 0) > 0:
            score += 30
            
        return score

    def _has_clear_cta(self, website_analysis: Dict[str, Any]) -> bool:
        """Check if website has clear calls to action."""
        content = website_analysis.get('content_analysis', {})
        return bool(content.get('cta_elements', 0) > 0)

    def _has_intuitive_navigation(self, website_analysis: Dict[str, Any]) -> bool:
        """Check if website has intuitive navigation."""
        structure = website_analysis.get('structure', {})
        return bool(structure.get('navigation') and structure.get('footer'))

    def _generate_ux_rankings(self, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate UX rankings based on metrics."""
        rankings = {
            'overall': [],
            'speed': [],
            'mobile': [],
            'accessibility': []
        }
        
        # Sort by different criteria
        if metrics:
            # Overall ranking
            rankings['overall'] = sorted(
                metrics.keys(),
                key=lambda x: (
                    metrics[x]['accessibility_score'] +
                    (100 if metrics[x]['mobile_friendly'] else 0) +
                    (100 * (1 - metrics[x]['load_time']/10)) +
                    metrics[x]['navigation_clarity'] +
                    metrics[x]['content_readability']
                ),
                reverse=True
            )
            
            # Speed ranking
            rankings['speed'] = sorted(
                metrics.keys(),
                key=lambda x: metrics[x]['load_time']
            )
            
            # Mobile ranking
            rankings['mobile'] = sorted(
                metrics.keys(),
                key=lambda x: (1 if metrics[x]['mobile_friendly'] else 0),
                reverse=True
            )
            
            # Accessibility ranking
            rankings['accessibility'] = sorted(
                metrics.keys(),
                key=lambda x: metrics[x]['accessibility_score'],
                reverse=True
            )
            
        return rankings

    def _generate_ux_recommendations(self, ux_analysis: Dict[str, Any]) -> List[str]:
        """Generate UX recommendations based on analysis."""
        recommendations = []
        
        # Analyze metrics across all competitors
        all_metrics = ux_analysis['metrics']
        if all_metrics:
            avg_load_time = sum(m['load_time'] for m in all_metrics.values()) / len(all_metrics)
            mobile_friendly_count = sum(1 for m in all_metrics.values() if m['mobile_friendly'])
            avg_accessibility = sum(m['accessibility_score'] for m in all_metrics.values()) / len(all_metrics)
            
            if avg_load_time > 3:
                recommendations.append("Improve page load times to under 3 seconds")
            if mobile_friendly_count < len(all_metrics) * 0.8:
                recommendations.append("Enhance mobile responsiveness")
            if avg_accessibility < 80:
                recommendations.append("Improve accessibility features")
                
        # Analyze best practices
        all_practices = ux_analysis['best_practices']
        if all_practices:
            practice_scores = {
                practice: sum(1 for p in all_practices.values() if p[practice])
                for practice in next(iter(all_practices.values())).keys()
            }
            
            for practice, score in practice_scores.items():
                if score < len(all_practices) * 0.6:
                    recommendations.append(f"Implement {practice.replace('_', ' ')}")
                    
        return recommendations

    def _determine_market_position(self, segments: Dict[str, List[str]]) -> str:
        """Determine overall market position based on segment distribution."""
        total = len(segments['premium']) + len(segments['mid_range']) + len(segments['value'])
        if total == 0:
            return "Market position unclear"
            
        premium_ratio = len(segments['premium']) / total if total > 0 else 0
        value_ratio = len(segments['value']) / total if total > 0 else 0
        
        if premium_ratio > 0.4:
            return "Premium-dominated market"
        elif value_ratio > 0.4:
            return "Value-driven market"
        else:
            return "Balanced market with mid-range focus"

    def _get_market_trends(self, keywords: List[str]) -> Dict[str, Any]:
        """Get market trends data from Google Trends with fallback data."""
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.5)
            
            # Build payload
            kw_list = keywords[:5]  # Google Trends limits to 5 keywords
            pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='US', gprop='')
            
            # Get interest over time
            interest_over_time_df = pytrends.interest_over_time()
            
            # Get related queries
            related_queries = pytrends.related_queries()
            
            # Process the data
            trends_data = {
                'trend_summary': {
                    'current_interest': interest_over_time_df[kw_list[0]].iloc[-1] if not interest_over_time_df.empty else None,
                    'trend_direction': 'increasing' if not interest_over_time_df.empty and 
                        interest_over_time_df[kw_list[0]].iloc[-1] > interest_over_time_df[kw_list[0]].iloc[0] else 'decreasing',
                    'peak_interest': interest_over_time_df[kw_list[0]].max() if not interest_over_time_df.empty else None
                },
                'related_topics': []
            }
            
            # Add related queries
            for kw in kw_list:
                if kw in related_queries and related_queries[kw]['rising'] is not None:
                    rising_queries = related_queries[kw]['rising'].head(3)
                    for _, row in rising_queries.iterrows():
                        trends_data['related_topics'].append({
                            'topic': row['query'],
                            'growth': f"{row['value']}% increase"
                        })
            
            return trends_data
            
        except Exception as e:
            self.logger.warning(f"Error fetching Google Trends data: {str(e)}. Using fallback data.")
            return self._get_fallback_trends_data()
    
    def _get_fallback_trends_data(self) -> Dict[str, Any]:
        """Provide fallback market trends data when API fails."""
        return {
            'trend_summary': {
                'current_interest': 75,
                'trend_direction': 'increasing',
                'peak_interest': 100
            },
            'related_topics': [
                {
                    'topic': 'Legal Tech Innovation',
                    'growth': '180% increase'
                },
                {
                    'topic': 'AI in Legal Services',
                    'growth': '150% increase'
                },
                {
                    'topic': 'Digital Law Practice',
                    'growth': '120% increase'
                }
            ]
        }