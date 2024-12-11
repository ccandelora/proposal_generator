import logging
import os
import tempfile
import html2text
import platform
import time
import json
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from .components.website_analyzer import WebsiteAnalyzer
from .components.competitor_analyzer import CompetitorAnalyzer
from .components.competitor_finder import CompetitorFinder
from .components.competitive_analyzer import CompetitiveAnalyzer
from .components.sentiment_analyzer import SentimentAnalyzer
from .components.seo_analyzer import SEOAnalyzer
from .components.website_screenshotter import WebsiteScreenshotter
from .components.mockup_generator import MockupGenerator

class ProposalGenerator:
    """Generates comprehensive proposals based on client briefs."""
    
    def __init__(self):
        """Initialize the proposal generator with all necessary components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.website_analyzer = WebsiteAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.competitor_finder = CompetitorFinder()
        self.competitive_analyzer = CompetitiveAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.website_screenshotter = WebsiteScreenshotter()
        self.mockup_generator = MockupGenerator()
        
        # Set up logging if not already configured
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

    def create_proposal(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Create a proposal based on client brief."""
        try:
            logger.info("Starting proposal generation")
            sections = []

            # Find and analyze competitors
            logger.info("Finding and analyzing competitors...")
            competitive_analysis = self.competitor_finder.process(client_brief)
            
            if not competitive_analysis or not competitive_analysis.get('competitors'):
                logger.warning("No competitors found by competitor finder")
            
            # Analyze market sentiment
            logger.info("Analyzing market sentiment...")
            sentiment_analysis = None
            try:
                sentiment_analysis = self.sentiment_analyzer.analyze(client_brief)
            except Exception as e:
                logger.warning(f"Error in sentiment analysis: {str(e)}")
                logger.warning("Missing competitor analysis data")
            
            # Generate proposal sections
            try:
                # Executive Summary
                sections.append(self._generate_executive_summary(
                    client_brief,
                    competitive_analysis,
                    sentiment_analysis
                ))
                
                # Market Analysis
                sections.append(self._generate_market_analysis(competitive_analysis))
                
                # Competitive Positioning
                sections.append(self._generate_competitive_positioning(competitive_analysis))
                
                # Technical Architecture
                sections.append(self._generate_technical_architecture(client_brief))
                
                # Team Structure
                sections.append(self._generate_team_structure(client_brief))
                
                # Project Timeline
                sections.append(self._generate_project_timeline(client_brief))
                
                # Investment
                sections.append(self._generate_investment_section(client_brief))
                
                # Next Steps
                sections.append(self._generate_next_steps())
                
            except Exception as e:
                logger.error(f"Error generating proposal sections: {str(e)}")
                logger.warning("Missing critical data for proposal generation")
                raise
            
            # Combine all sections
            proposal_content = {
                'title': self._generate_title(client_brief),
                'sections': sections
            }
            
            return proposal_content
            
        except Exception as e:
            logger.error(f"Error generating proposal: {str(e)}")
            raise

    def _validate_client_brief(self, client_brief: Dict[str, Any]) -> bool:
        """Validate that the client brief contains all required fields."""
        required_fields = [
            'project_type',
            'description',
            'timeline',
            'budget_range'
        ]
        
        return all(field in client_brief for field in required_fields)
        
    def _verify_required_data(self, **kwargs) -> bool:
        """Verify that we have the minimum required data for a complete proposal."""
        client_brief = kwargs.get('client_brief', {})
        competitor_analysis = kwargs.get('competitor_analysis', {})
        competitive_analysis = kwargs.get('competitive_analysis', {})
        sentiment_analysis = kwargs.get('sentiment_analysis', {})
        
        # Check client brief data
        if not client_brief.get('project_type') or not client_brief.get('description'):
            self.logger.warning("Missing critical client brief information")
            return False
            
        # Check competitor data if competitor analysis was requested
        if client_brief.get('analysis_options', {}).get('competitor_analysis'):
            if not competitor_analysis or not competitor_analysis.get('competitors'):
                self.logger.warning("Missing competitor analysis data")
                return False
                
            if not competitive_analysis or not competitive_analysis.get('market_trends'):
                self.logger.warning("Missing market trends data")
                return False
                
        # Check sentiment data if sentiment analysis was requested
        if client_brief.get('analysis_options', {}).get('sentiment_analysis'):
            if not sentiment_analysis or not sentiment_analysis.get('review_analysis'):
                self.logger.warning("Missing sentiment analysis data")
                return False
                
        return True
        
    def _get_fallback_market_trends(self) -> Dict[str, Any]:
        """Get fallback market trends data."""
        return {
            'trend_summary': {
                'current_interest': 75,
                'average_interest': 70,
                'max_interest': 85
            },
            'related_topics': [
                {'topic': 'Digital Transformation', 'growth': '150%'},
                {'topic': 'Cloud Computing', 'growth': '120%'},
                {'topic': 'Mobile Development', 'growth': '100%'}
            ]
        }
        
    def _get_fallback_financial_data(self) -> Dict[str, Any]:
        """Get fallback financial analysis data."""
        return {
            'summary': {
                'average_revenue': 1000000,
                'total_employees': 500,
                'market_growth': '15%'
            }
        }
        
    def _get_fallback_sentiment_data(self) -> Dict[str, Any]:
        """Get fallback sentiment analysis data."""
        return {
            'review_analysis': {
                'overall': {
                    'average_rating': 4.5,
                    'total_reviews': 100,
                    'reviews': [
                        {
                            'text': "Great service and technical expertise",
                            'rating': 5.0
                        }
                    ]
                },
                'sentiment_breakdown': {
                    'positive': 75,
                    'neutral': 20,
                    'negative': 5
                }
            }
        }

    def _generate_executive_summary(self, client_brief: Dict[str, Any], **kwargs) -> str:
        """Generate the executive summary section."""
        summary = []
        
        # Introduction
        client_name = client_brief.get('client_name', 'Client')
        project_type = client_brief.get('project_type', 'web development')
        summary.append("## Executive Summary\n")
        summary.append(f"This proposal outlines a comprehensive {project_type} solution for {client_name}.")
        
        # Current Website Summary
        website_analysis = kwargs.get('website_analysis', {})
        if website_analysis and not website_analysis.get('error'):
            tech_analysis = website_analysis.get('technical_analysis', {})
            content_analysis = website_analysis.get('content_analysis', {})
            
            if tech_analysis or content_analysis:
                summary.append("\nCurrent Website Analysis:")
                if tech_analysis:
                    perf = tech_analysis.get('performance_metrics', {})
                    if perf:
                        summary.append(f"- Load Time: {perf.get('load_time', 'N/A'):.2f}s")
                if content_analysis:
                    summary.append(f"- Content Volume: {content_analysis.get('total_words', 0):,} words")
        
        # SEO Summary
        seo_analysis = kwargs.get('seo_analysis', {})
        if seo_analysis and not seo_analysis.get('error'):
            if seo_analysis.get('overview', {}).get('score'):
                summary.append(f"- SEO Score: {seo_analysis['overview']['score']}/100")
        
        # Market Analysis Summary
        competitor_analysis = kwargs.get('competitor_analysis', {})
        competitive_analysis = kwargs.get('competitive_analysis', {})
        
        if competitor_analysis:
            summary.append("\nMarket Analysis Highlights:")
            market_insights = competitor_analysis.get('market_insights', [])
            # Get up to 2 insights safely
            insights_to_show = market_insights if isinstance(market_insights, list) else []
            for insight in insights_to_show[:2]:
                if insight:
                    summary.append(f"- {insight}")
            
            # Add competitive insights
            if competitive_analysis:
                market_trends = competitive_analysis.get('market_trends', [])
                if market_trends:
                    if isinstance(market_trends, list) and market_trends:
                        summary.append(f"- Market Trend: {market_trends[0]}")
                    elif isinstance(market_trends, dict):
                        trend_summary = market_trends.get('trend_summary', {})
                        if trend_summary:
                            summary.append(f"- Market Interest: {trend_summary.get('current_interest', 'N/A')}")
                
                news_analysis = competitive_analysis.get('news_analysis', {})
                industry_news = news_analysis.get('industry_news', {})
                articles = industry_news.get('articles', [])
                if articles and isinstance(articles, list) and len(articles) > 0:
                    first_article = articles[0]
                    if isinstance(first_article, dict) and first_article.get('title'):
                        summary.append(f"- Recent Industry Development: {first_article['title']}")
        
        # Business Goals
        business_goals = client_brief.get('business_goals', [])
        if business_goals and isinstance(business_goals, list):
            summary.append("\nThis project aims to achieve the following business objectives:")
            for goal in business_goals:
                if goal:
                    summary.append(f"- {goal}")
        
        # Target Audience
        target_audience = client_brief.get('target_audience')
        if target_audience:
            summary.append(f"\nThis solution is specifically designed for {target_audience}.")
        
        return "\n".join(summary)

    def _generate_website_overview(self, **kwargs) -> str:
        """Generate the website overview section based on all analyses."""
        sections = []
        
        sections.append("## Current Website Analysis\n")
        
        # Technical Analysis
        website_analysis = kwargs.get('website_analysis')
        if website_analysis and not website_analysis.get('error'):
            sections.append("### Technical Overview\n")
            
            tech_analysis = website_analysis.get('technical_analysis', {})
            if tech_analysis:
                # Performance metrics
                sections.append("#### Performance Metrics")
                if tech_analysis.get('performance_metrics'):
                    perf = tech_analysis['performance_metrics']
                    sections.append("| Metric | Value |")
                    sections.append("|--------|-------|")
                    sections.append(f"| Load Time | {perf.get('load_time', 'N/A'):.2f}s |")
                    sections.append(f"| Response Time | {perf.get('response_time', 'N/A'):.2f}s |")
                    sections.append(f"| Content Size | {perf.get('content_size', 0) / 1024:.1f} KB |")
                
                # Technologies used
                if tech_analysis.get('technologies_used'):
                    sections.append("\n#### Technology Stack")
                    for tech in tech_analysis['technologies_used']:
                        sections.append(f"- {tech}")
                
                # Mobile friendliness
                sections.append("\n#### Mobile Optimization")
                sections.append("✓ Mobile-Friendly" if tech_analysis.get('mobile_friendly') else "⚠ Mobile Optimization Required")
        
        # SEO Analysis
        seo_analysis = kwargs.get('seo_analysis')
        if seo_analysis and not seo_analysis.get('error'):
            sections.append("\n### SEO Analysis\n")
            
            # Overall SEO score
            if seo_analysis.get('overview', {}).get('score'):
                sections.append(f"Overall SEO Score: {seo_analysis['overview']['score']}/100\n")
            
            # Key SEO metrics
            if seo_analysis.get('metrics'):
                sections.append("#### Key SEO Metrics")
                sections.append("| Metric | Status |")
                sections.append("|--------|--------|")
                for metric, status in seo_analysis['metrics'].items():
                    sections.append(f"| {metric} | {status} |")
            
            # SEO recommendations
            if seo_analysis.get('recommendations'):
                sections.append("\n#### Recommendations")
                for rec in seo_analysis['recommendations']:
                    sections.append(f"- {rec}")
        
        # Visual Analysis
        visual_analysis = kwargs.get('visual_analysis')
        if visual_analysis and not visual_analysis.get('error'):
            sections.append("\n### Visual Analysis\n")
            
            # Layout patterns
            if visual_analysis.get('layout_patterns'):
                sections.append("#### Layout Patterns")
                for pattern in visual_analysis['layout_patterns']:
                    sections.append(f"- {pattern}")
            
            # UI elements
            if visual_analysis.get('ui_elements'):
                sections.append("\n#### UI Elements")
                for element in visual_analysis['ui_elements']:
                    sections.append(f"- {element}")
            
            # Color scheme
            if visual_analysis.get('color_scheme'):
                sections.append("\n#### Color Scheme")
                sections.append("| Color | Usage |")
                sections.append("|-------|--------|")
                for color in visual_analysis['color_scheme']:
                    sections.append(f"| {color['hex']} | {color['usage']} |")
            
            # Responsive issues
            if visual_analysis.get('responsive_issues'):
                sections.append("\n#### Responsive Design Issues")
                for issue in visual_analysis['responsive_issues']:
                    sections.append(f"- {issue}")
        
        return "\n".join(sections)

    def _generate_market_analysis(self, **kwargs) -> str:
        """Generate the market analysis section based on competitor and sentiment analysis."""
        sections = []
        sections.append("## Market Analysis\n")
        
        competitor_analysis = kwargs.get('competitor_analysis', {})
        competitive_analysis = kwargs.get('competitive_analysis', {})
        sentiment_analysis = kwargs.get('sentiment_analysis', {})
        
        # Market Overview
        sections.append("### Market Overview")
        
        # Add market trends if available
        market_trends = competitive_analysis.get('market_trends', [])
        if market_trends:
            sections.append("\nMarket Trends:")
            if isinstance(market_trends, list):
                # Safely get up to 3 trends
                for trend in market_trends[:3] if market_trends else []:
                    sections.append(f"- {trend}")
            elif isinstance(market_trends, dict):
                # Handle structured trends data
                trend_summary = market_trends.get('trend_summary', {})
                if trend_summary:
                    sections.append(f"- Average Interest: {trend_summary.get('average_interest', 'N/A')}")
                    sections.append(f"- Current Interest: {trend_summary.get('current_interest', 'N/A')}")
                    sections.append(f"- Peak Interest: {trend_summary.get('max_interest', 'N/A')}")
                
                related_queries = market_trends.get('related_queries', {}).get('rising', [])
                if related_queries:
                    sections.append("\nRising Trends:")
                    # Safely get up to 3 queries
                    for query in related_queries[:3] if related_queries else []:
                        if isinstance(query, dict):
                            sections.append(f"- {query.get('query', 'N/A')}: {query.get('value', 'N/A')}% increase")
                        else:
                            sections.append(f"- {query}")
        
        # Competitor Analysis
        if competitor_analysis:
            sections.append("\n### Competitor Analysis")
            
            # Add summary if available
            summary = competitor_analysis.get('summary', {})
            if summary:
                sections.append(f"\nAnalyzed {summary.get('total_competitors', 0)} competitors in the market.")
                if summary.get('has_financial_data'):
                    sections.append("Financial insights available for public companies.")
            
            # Add competitor details
            competitors = competitor_analysis.get('competitors', [])
            if competitors:
                if isinstance(competitors, list):
                    # Safely get up to 5 competitors
                    for comp in competitors[:5] if competitors else []:
                        if isinstance(comp, dict):
                            name = comp.get('name', 'Unknown Competitor')
                            sections.append(f"\n#### {name}")
                            if comp.get('description'):
                                sections.append(comp['description'])
                            if comp.get('strengths'):
                                sections.append("\nStrengths:")
                                for strength in comp['strengths']:
                                    sections.append(f"- {strength}")
                elif isinstance(competitors, dict):
                    # Handle structured competitor data
                    # Safely get up to 5 competitors
                    for url, data in list(competitors.items())[:5] if competitors else []:
                        name = data.get('name', url)
                        sections.append(f"\n#### {name}")
                        if data.get('website_analysis', {}).get('overview'):
                            sections.append(data['website_analysis']['overview'])
                        if data.get('technologies'):
                            sections.append("\nKey Technologies:")
                            # Safely get up to 3 technologies
                            techs = data.get('technologies', [])
                            for tech in techs[:3] if techs else []:
                                sections.append(f"- {tech}")
        
        # Financial Analysis
        financial_analysis = competitive_analysis.get('financial_analysis', {})
        if financial_analysis:
            sections.append("\n### Financial Overview")
            summary = financial_analysis.get('summary', {})
            if summary:
                if summary.get('average_revenue'):
                    sections.append(f"\nAverage Revenue: ${summary['average_revenue']:,.2f}")
                if summary.get('total_employees'):
                    sections.append(f"Total Industry Employees: {summary['total_employees']:,}")
        
        # News Analysis
        news_analysis = competitive_analysis.get('news_analysis', {})
        if news_analysis:
            sections.append("\n### Industry News")
            industry_news = news_analysis.get('industry_news', {})
            articles = industry_news.get('articles', [])
            if articles:
                sections.append("\nRecent Developments:")
                # Safely get up to 3 articles
                for article in articles[:3] if articles else []:
                    title = article.get('title', '')
                    source = article.get('source', {}).get('name', '')
                    if title and source:
                        sections.append(f"- {title} ({source})")
        
        # Market Sentiment
        if sentiment_analysis:
            sections.append("\n### Market Sentiment")
            review_analysis = sentiment_analysis.get('review_analysis', {})
            
            # Overall sentiment metrics
            overall = review_analysis.get('overall', {})
            if overall:
                sections.append("\n#### Overall Metrics")
                sections.append(f"- Average Rating: {overall.get('average_rating', 'N/A')}/5.0")
                sections.append(f"- Total Reviews Analyzed: {overall.get('total_reviews', 'N/A')}")
            
            # Sentiment breakdown
            sentiment_breakdown = review_analysis.get('sentiment_breakdown', {})
            if sentiment_breakdown:
                sections.append("\n#### Sentiment Distribution")
                sections.append(f"- Positive: {sentiment_breakdown.get('positive', 0)}%")
                sections.append(f"- Neutral: {sentiment_breakdown.get('neutral', 0)}%")
                sections.append(f"- Negative: {sentiment_breakdown.get('negative', 0)}%")
            
            # Category ratings
            categories = review_analysis.get('categories', {})
            if categories:
                sections.append("\n#### Category Ratings")
                for category, rating in categories.items():
                    sections.append(f"- {category}: {rating}/5.0")
            
            # Key themes
            key_themes = review_analysis.get('key_themes', [])
            if key_themes:
                sections.append("\n#### Key Themes")
                for theme in key_themes:
                    sections.append(f"- {theme}")
            
            # Trends
            trends = review_analysis.get('trends', {})
            if trends:
                sections.append("\n#### Sentiment Trends")
                
                if trends.get('improving'):
                    sections.append("\nImproving Areas:")
                    for area in trends['improving']:
                        sections.append(f"- {area}")
                
                if trends.get('stable'):
                    sections.append("\nStable Areas:")
                    for area in trends['stable']:
                        sections.append(f"- {area}")
                
                if trends.get('needs_attention'):
                    sections.append("\nAreas Needing Attention:")
                    for area in trends['needs_attention']:
                        sections.append(f"- {area}")
            
            # Sample reviews
            reviews = overall.get('reviews', [])
            if reviews:
                sections.append("\n#### Sample Reviews")
                for review in reviews[:2]:  # Show only top 2 reviews
                    if isinstance(review, dict):
                        text = review.get('text', '')
                        rating = review.get('rating', '')
                        if text and rating:
                            sections.append(f"- \"{text}\" (Rating: {rating}/5.0)")
        
        return "\n".join(sections)

    def _generate_project_scope(self, client_brief: Dict[str, Any], **kwargs) -> str:
        """Generate the project scope section."""
        scope = []
        
        scope.append("## Project Scope\n")
        
        # Project Overview
        if client_brief.get('project_type'):
            scope.append("### Project Overview\n")
            scope.append(f"This {client_brief['project_type']} project will deliver a comprehensive solution that meets your business objectives and technical requirements.")
        
        # Current Website Issues
        website_analysis = kwargs.get('website_analysis')
        seo_analysis = kwargs.get('seo_analysis')
        visual_analysis = kwargs.get('visual_analysis')
        
        if any([website_analysis, seo_analysis, visual_analysis]):
            scope.append("\n### Current Website Analysis\n")
            
            # Technical Issues
            if website_analysis and not website_analysis.get('error'):
                tech_analysis = website_analysis.get('technical_analysis', {})
                if tech_analysis:
                    scope.append("#### Technical Considerations")
                    if tech_analysis.get('mobile_friendly') is not None:
                        scope.append(f"- Mobile Optimization Required: {'No' if tech_analysis['mobile_friendly'] else 'Yes'}")
                    if tech_analysis.get('performance_metrics'):
                        perf = tech_analysis['performance_metrics']
                        if perf.get('load_time', 0) > 3:
                            scope.append("- Performance Optimization Required")
                            scope.append(f"  - Current Load Time: {perf['load_time']:.2f}s")
                            scope.append("  - Target Load Time: < 3s")
                
                content_analysis = website_analysis.get('content_analysis', {})
                if content_analysis:
                    scope.append("\n#### Content Migration")
                    if content_analysis.get('total_words'):
                        scope.append(f"- Content Volume: {content_analysis['total_words']:,} words")
                    if content_analysis.get('total_images'):
                        scope.append(f"- Images: {content_analysis['total_images']} files")
                    if content_analysis.get('total_forms'):
                        scope.append(f"- Forms: {content_analysis['total_forms']} forms")
            
            # SEO Issues
            if seo_analysis and not seo_analysis.get('error'):
                scope.append("\n#### SEO Improvements")
                if seo_analysis.get('recommendations'):
                    for rec in seo_analysis['recommendations']:
                        scope.append(f"- {rec}")
            
            # Visual/UX Issues
            if visual_analysis and not visual_analysis.get('error'):
                scope.append("\n#### Visual and UX Improvements")
                if visual_analysis.get('responsive_issues'):
                    scope.append("Responsive Design Issues to Address:")
                    for issue in visual_analysis['responsive_issues']:
                        scope.append(f"- {issue}")
                
                if visual_analysis.get('ui_elements'):
                    scope.append("\nUI Elements to Optimize:")
                    for element in visual_analysis['ui_elements']:
                        if isinstance(element, dict) and element.get('needs_improvement'):
                            scope.append(f"- {element['type']}: {element['issue']}")
        
        # Key Features
        if client_brief.get('features'):
            scope.append("\n### Key Features\n")
            for feature in client_brief['features']:
                scope.append(f"- {feature}")
        
        # Deliverables
        scope.append("\n### Core Deliverables\n")
        
        # Project Management
        scope.append("#### Project Management")
        scope.append("- Detailed project planning and requirements documentation")
        scope.append("- Regular progress updates and stakeholder communication")
        scope.append("- Risk management and mitigation planning")
        
        # Design and Development
        scope.append("\n#### Design and Development")
        scope.append("- Comprehensive UI/UX design")
        scope.append("- Responsive implementation for all devices")
        scope.append("- Development of all specified features")
        scope.append("- Integration with required systems")
        
        # Quality Assurance
        scope.append("\n#### Quality Assurance")
        scope.append("- Comprehensive testing strategy")
        scope.append("- Performance optimization")
        scope.append("- Security testing and hardening")
        scope.append("- Cross-browser compatibility testing")
        
        # Deployment and Support
        scope.append("\n#### Deployment and Support")
        scope.append("- Controlled deployment process")
        scope.append("- Staff training and documentation")
        scope.append("- Post-launch support and maintenance")
        scope.append("- Performance monitoring and optimization")
        
        return "\n".join(scope)

    def _generate_implementation_strategy(self, client_brief: Dict[str, Any], **kwargs) -> str:
        """Generate the implementation strategy section."""
        strategy = []
        
        strategy.append("## Implementation Strategy\n")
        
        # Technical Strategy
        website_analysis = kwargs.get('website_analysis', {})
        seo_analysis = kwargs.get('seo_analysis', {})
        
        if website_analysis and not website_analysis.get('error'):
            strategy.append("### Technical Approach\n")
            
            tech_analysis = website_analysis.get('technical_analysis', {})
            if tech_analysis:
                priorities = []
                
                # Mobile optimization
                if not tech_analysis.get('mobile_friendly', True):
                    priorities.append({
                        'priority': 'Mobile Optimization',
                        'description': 'Implement responsive design for all devices',
                        'impact': 'High'
                    })
                
                # Performance optimization
                perf_metrics = tech_analysis.get('performance_metrics', {})
                if perf_metrics.get('load_time', 0) > 3:
                    priorities.append({
                        'priority': 'Performance Optimization',
                        'description': 'Improve page load times and overall performance',
                        'impact': 'High'
                    })
                
                # SEO improvements
                if seo_analysis and seo_analysis.get('recommendations'):
                    priorities.append({
                        'priority': 'SEO Optimization',
                        'description': 'Implement SEO best practices and improvements',
                        'impact': 'Medium'
                    })
                
                if priorities:
                    strategy.append("| Priority | Description | Impact |")
                    strategy.append("|----------|-------------|---------|")
                    for p in priorities:
                        strategy.append(f"| {p['priority']} | {p['description']} | {p['impact']} |")
        
        # Market Strategy
        competitor_analysis = kwargs.get('competitor_analysis', {})
        competitive_analysis = kwargs.get('competitive_analysis', {})
        
        if competitor_analysis or competitive_analysis:
            strategy.append("\n### Market Strategy\n")
            
            # Competitive positioning
            market_insights = competitor_analysis.get('market_insights', [])
            if market_insights and isinstance(market_insights, list):
                strategy.append("#### Competitive Positioning")
                # Safely get up to 3 insights
                insights_to_show = market_insights[:3] if len(market_insights) > 0 else []
                for insight in insights_to_show:
                    if insight:
                        strategy.append(f"- {insight}")
            
            # Market trends response
            market_trends = competitive_analysis.get('market_trends', [])
            if market_trends:
                strategy.append("\n#### Market Trends Response")
                if isinstance(market_trends, list):
                    # Safely get up to 3 trends
                    trends_to_show = market_trends[:3] if len(market_trends) > 0 else []
                    for trend in trends_to_show:
                        if trend:
                            strategy.append(f"- {trend}")
                elif isinstance(market_trends, dict):
                    trend_summary = market_trends.get('trend_summary', {})
                    if trend_summary:
                        strategy.append(f"- Focus on {trend_summary.get('current_interest', 'emerging trends')}")
        
        # Implementation Phases
        strategy.append("\n### Implementation Phases\n")
        
        # Phase 1: Discovery and Planning
        strategy.append("#### Phase 1: Discovery and Planning")
        strategy.append("- Detailed requirements gathering and analysis")
        strategy.append("- Stakeholder interviews and workshops")
        strategy.append("- Technical architecture planning")
        
        # Phase 2: Design and Development
        strategy.append("\n#### Phase 2: Design and Development")
        strategy.append("- UI/UX design and prototyping")
        strategy.append("- Iterative development with regular reviews")
        strategy.append("- Quality assurance and testing")
        
        # Phase 3: Launch and Optimization
        strategy.append("\n#### Phase 3: Launch and Optimization")
        strategy.append("- Deployment and launch")
        strategy.append("- Performance monitoring and optimization")
        strategy.append("- Training and documentation")
        
        # Timeline
        if client_brief.get('timeline'):
            strategy.append(f"\nEstimated Timeline: {client_brief['timeline']}")
        
        return "\n".join(strategy)

    def _generate_timeline(self, client_brief: Dict[str, Any]) -> str:
        """Generate the project timeline section."""
        timeline = []
        
        timeline.append("## Project Timeline\n")
        
        # Parse timeline
        total_weeks = self._parse_timeline(client_brief.get('timeline', ''))
        
        # Calculate phase durations
        planning_weeks = max(1, total_weeks * 0.15)
        design_weeks = max(1, total_weeks * 0.25)
        development_weeks = max(2, total_weeks * 0.40)
        testing_weeks = max(1, total_weeks * 0.20)
        
        timeline.append("| Phase | Duration | Key Deliverables |")
        timeline.append("|-------|-----------|-----------------|")
        timeline.append(f"| Planning & Analysis | {self._format_duration(planning_weeks)} | Project plan, requirements document, technical specifications |")
        timeline.append(f"| Design | {self._format_duration(design_weeks)} | Wireframes, mockups, design system |")
        timeline.append(f"| Development | {self._format_duration(development_weeks)} | Core functionality, integrations, content migration |")
        timeline.append(f"| Testing & Deployment | {self._format_duration(testing_weeks)} | Testing, bug fixes, deployment |")
        
        return "\n".join(timeline)

    def _generate_investment(self, client_brief: Dict[str, Any]) -> str:
        """Generate the investment section of the proposal."""
        sections = []
        
        sections.append("## Investment\n")
        
        # Project Investment
        budget_range = client_brief.get('budget_range')
        if budget_range:
            sections.append("### Project Investment\n")
            sections.append(f"The investment for this project falls within {budget_range}.")
        
        # Payment Schedule
        payment_terms = client_brief.get('payment_terms', {})
        if payment_terms:
            sections.append("\n### Payment Schedule\n")
            
            # Milestone Payments
            milestones = payment_terms.get('milestones', [])
            if milestones:
                sections.append("| Milestone | Percentage | Description |")
                sections.append("|-----------|------------|-------------|")
                for milestone in milestones:
                    if isinstance(milestone, dict):
                        name = milestone.get('name', '')
                        percentage = milestone.get('percentage', '')
                        description = milestone.get('description', '')
                        sections.append(f"| {name} | {percentage}% | {description} |")
        
        # Value Proposition
        value_props = client_brief.get('value_proposition', [])
        if value_props:
            sections.append("\n### Value Proposition\n")
            sections.append("Your investment includes:")
            for prop in value_props:
                sections.append(f"- {prop}")
        
        # Additional Services
        additional_services = client_brief.get('additional_services', [])
        if additional_services:
            sections.append("\n### Additional Services\n")
            sections.append("Optional services available:")
            for service in additional_services:
                if isinstance(service, dict):
                    name = service.get('name', '')
                    cost = service.get('cost', '')
                    description = service.get('description', '')
                    sections.append(f"- {name}: {cost}")
                    if description:
                        sections.append(f"  {description}")
        
        # Terms and Conditions
        terms = client_brief.get('terms_and_conditions', [])
        if terms:
            sections.append("\n### Terms and Conditions\n")
            for term in terms:
                sections.append(f"- {term}")
        
        return "\n".join(sections)

    def _generate_next_steps(self, client_brief: Dict[str, Any]) -> str:
        """Generate the next steps section."""
        steps = []
        
        steps.append("## Next Steps\n")
        steps.append("To proceed with this project, we recommend the following next steps:\n")
        
        steps.append("1. Review Proposal")
        steps.append("   - Review all sections of this proposal")
        steps.append("   - Note any questions or concerns")
        steps.append("   - Identify areas needing clarification")
        
        steps.append("\n2. Project Discussion")
        steps.append("   - Schedule a detailed project discussion")
        steps.append("   - Review technical requirements")
        steps.append("   - Discuss timeline and milestones")
        
        steps.append("\n3. Agreement and Initiation")
        steps.append("   - Finalize project scope and terms")
        steps.append("   - Sign project agreement")
        steps.append("   - Process initial payment")
        
        steps.append("\n4. Project Kickoff")
        steps.append("   - Schedule kickoff meeting")
        steps.append("   - Introduce project team")
        steps.append("   - Begin project planning phase")
        
        return "\n".join(steps)

    def _parse_timeline(self, timeline_str: str) -> float:
        """Parse timeline string to number of weeks."""
        try:
            if 'month' in timeline_str.lower():
                months = float(timeline_str.lower().split('month')[0].strip())
                return months * 4
            elif 'week' in timeline_str.lower():
                return float(timeline_str.lower().split('week')[0].strip())
            return 8  # Default to 8 weeks if parsing fails
        except:
            return 8

    def _format_duration(self, weeks: float) -> str:
        """Format duration in weeks to a readable string."""
        if weeks < 1:
            return f"{int(weeks * 7)} days"
        elif weeks == 1:
            return "1 week"
        else:
            return f"{int(weeks)} weeks"

    def _generate_mockups_section(self, mockups: Dict[str, Any]) -> str:
        """Generate the mockups section of the proposal."""
        sections = []
        
        sections.append("## Design Mockups\n")
        
        if mockups.get('error'):
            sections.append("*Design mockups could not be generated at this time.*")
            return "\n".join(sections)
        
        # Overview
        if mockups.get('overview'):
            sections.append("### Design Overview\n")
            sections.append(mockups['overview'])
        
        # Design System
        design_system = mockups.get('design_system', {})
        if design_system:
            sections.append("\n### Design System\n")
            
            # Colors
            colors = design_system.get('colors', {})
            if colors:
                sections.append("#### Color Palette")
                primary_colors = colors.get('primary', [])
                if primary_colors:
                    sections.append("\nPrimary Colors:")
                    for color in primary_colors:
                        sections.append(f"- {color.get('name', 'Color')}: {color.get('hex', '#000000')}")
                
                secondary_colors = colors.get('secondary', [])
                if secondary_colors:
                    sections.append("\nSecondary Colors:")
                    for color in secondary_colors:
                        sections.append(f"- {color.get('name', 'Color')}: {color.get('hex', '#000000')}")
            
            # Typography
            typography = design_system.get('typography', {})
            if typography:
                sections.append("\n#### Typography")
                if typography.get('primary_font'):
                    sections.append(f"Primary Font: {typography['primary_font']}")
                if typography.get('secondary_font'):
                    sections.append(f"Secondary Font: {typography['secondary_font']}")
            
            # Components
            components = design_system.get('components', [])
            if components:
                sections.append("\n#### Key Components")
                for component in components:
                    if isinstance(component, dict):
                        name = component.get('name', 'Component')
                        description = component.get('description', '')
                        sections.append(f"- {name}: {description}")
        
        # Page Mockups
        page_mockups = mockups.get('pages', [])
        if page_mockups:
            sections.append("\n### Page Mockups\n")
            for page in page_mockups:
                if isinstance(page, dict):
                    name = page.get('name', 'Page')
                    sections.append(f"#### {name}")
                    
                    if page.get('description'):
                        sections.append(page['description'])
                    
                    features = page.get('features', [])
                    if features:
                        sections.append("\nKey Features:")
                        for feature in features:
                            sections.append(f"- {feature}")
                    
                    if page.get('mockup_path'):
                        sections.append(f"\n![{name} Mockup]({page['mockup_path']})")
        
        # Responsive Design
        responsive = mockups.get('responsive_design', {})
        if responsive:
            sections.append("\n### Responsive Design\n")
            
            breakpoints = responsive.get('breakpoints', {})
            if breakpoints:
                sections.append("#### Breakpoints")
                for device, width in breakpoints.items():
                    sections.append(f"- {device.title()}: {width}px")
            
            adaptations = responsive.get('adaptations', [])
            if adaptations:
                sections.append("\n#### Design Adaptations")
                for adaptation in adaptations:
                    if isinstance(adaptation, dict):
                        sections.append(f"- {adaptation.get('description', '')}")
        
        return "\n".join(sections)

    def generate_pdf(self, content: str, output_path: str) -> str:
        """Generate a PDF from the proposal content."""
        try:
            # Ensure content is a string
            if not isinstance(content, str):
                content = str(content)

            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            styles = getSampleStyleSheet()
            
            # Create custom styles
            styles.add(ParagraphStyle(
                name='CustomHeading1',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            ))
            styles.add(ParagraphStyle(
                name='CustomHeading2',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=20
            ))
            styles.add(ParagraphStyle(
                name='CustomHeading3',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=15
            ))
            styles.add(ParagraphStyle(
                name='CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                spaceBefore=6,
                spaceAfter=6
            ))
            
            # Create the PDF content
            story = []
            
            # Process content line by line
            current_list = []
            for line in content.split('\n'):
                if not line.strip():
                    # Add any pending list items
                    if current_list:
                        bullet_list = ListFlowable(
                            [Paragraph(item, styles['CustomNormal']) for item in current_list],
                            bulletType='bullet',
                            leftIndent=20
                        )
                        story.append(bullet_list)
                        current_list = []
                    story.append(Spacer(1, 12))
                    continue
                
                try:
                    if line.startswith('# '):
                        # Main heading
                        text = line[2:].strip()
                        story.append(Paragraph(text, styles['CustomHeading1']))
                    elif line.startswith('## '):
                        # Subheading
                        text = line[3:].strip()
                        story.append(Paragraph(text, styles['CustomHeading2']))
                    elif line.startswith('### '):
                        # Sub-subheading
                        text = line[4:].strip()
                        story.append(Paragraph(text, styles['CustomHeading3']))
                    elif line.startswith('- '):
                        # Bullet point - collect for list
                        current_list.append(line[2:].strip())
                    else:
                        # Normal text
                        if current_list:
                            # Add pending list items before continuing
                            bullet_list = ListFlowable(
                                [Paragraph(item, styles['CustomNormal']) for item in current_list],
                                bulletType='bullet',
                                leftIndent=20
                            )
                            story.append(bullet_list)
                            current_list = []
                        story.append(Paragraph(line.strip(), styles['CustomNormal']))
                except Exception as e:
                    self.logger.warning(f"Error processing line '{line}': {str(e)}")
                    continue
                
                story.append(Spacer(1, 6))
            
            # Add any remaining list items
            if current_list:
                bullet_list = ListFlowable(
                    [Paragraph(item, styles['CustomNormal']) for item in current_list],
                    bulletType='bullet',
                    leftIndent=20
                )
                story.append(bullet_list)
            
            # Build the PDF
            doc.build(story)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _generate_competitive_positioning(self, competitor_analysis: Dict[str, Any], competitive_analysis: Dict[str, Any]) -> str:
        """Generate the competitive positioning section."""
        sections = []
        sections.append("## Competitive Positioning\n")
        
        # SWOT Analysis
        sections.append("### SWOT Analysis\n")
        
        # Strengths
        sections.append("#### Strengths")
        strengths = []
        if competitor_analysis and competitor_analysis.get('strengths'):
            strengths.extend(competitor_analysis['strengths'])
        if competitive_analysis and competitive_analysis.get('tech_advantages', {}).get('advantages'):
            strengths.extend(competitive_analysis['tech_advantages']['advantages'])
        for strength in strengths:
            sections.append(f"- {strength}")
            
        # Weaknesses
        sections.append("\n#### Weaknesses")
        weaknesses = []
        if competitor_analysis and competitor_analysis.get('weaknesses'):
            weaknesses.extend(competitor_analysis['weaknesses'])
        if competitive_analysis and competitive_analysis.get('tech_advantages', {}).get('recommendations'):
            weaknesses.extend(competitive_analysis['tech_advantages']['recommendations'])
        for weakness in weaknesses:
            sections.append(f"- {weakness}")
            
        # Opportunities
        sections.append("\n#### Opportunities")
        if competitive_analysis and competitive_analysis.get('market_trends'):
            trends = competitive_analysis['market_trends']
            if isinstance(trends, list):
                for trend in trends[:3]:
                    sections.append(f"- {trend}")
            elif isinstance(trends, dict) and trends.get('trend_summary'):
                summary = trends['trend_summary']
                sections.append(f"- Growing market interest: {summary.get('current_interest', 'N/A')}")
                
        # Threats
        sections.append("\n#### Threats")
        if competitive_analysis and competitive_analysis.get('market_position'):
            sections.append(f"- {competitive_analysis['market_position']}")
        if competitive_analysis and competitive_analysis.get('news_analysis', {}).get('industry_news', {}).get('articles'):
            articles = competitive_analysis['news_analysis']['industry_news']['articles']
            for article in articles[:2]:
                if isinstance(article, dict) and article.get('title'):
                    sections.append(f"- {article['title']}")
        
        # Feature Comparison Matrix
        if competitive_analysis and competitive_analysis.get('feature_matrix'):
            sections.append("\n### Feature Comparison Matrix\n")
            matrix = competitive_analysis['feature_matrix']
            
            # Headers
            sections.append("| Feature | Our Solution | Competition |")
            sections.append("|---------|--------------|-------------|")
            
            # Core Features
            sections.append("\n**Core Features**")
            for feature in matrix['categories']['core_features']:
                competitor_support = sum(1 for comp in matrix['comparisons'].values() 
                                      if comp['core_features'].get(feature, False))
                total_competitors = len(matrix['comparisons'])
                support_ratio = competitor_support / total_competitors if total_competitors > 0 else 0
                sections.append(f"| {feature.replace('_', ' ').title()} | Planned | {support_ratio*100:.0f}% of competitors |")
            
            # Technical Features
            sections.append("\n**Technical Features**")
            for feature in matrix['categories']['technical_features']:
                competitor_support = sum(1 for comp in matrix['comparisons'].values() 
                                      if comp['technical_features'].get(feature, False))
                total_competitors = len(matrix['comparisons'])
                support_ratio = competitor_support / total_competitors if total_competitors > 0 else 0
                sections.append(f"| {feature.replace('_', ' ').title()} | Planned | {support_ratio*100:.0f}% of competitors |")
            
            # Content Features
            sections.append("\n**Content Features**")
            for feature in matrix['categories']['content_features']:
                competitor_support = sum(1 for comp in matrix['comparisons'].values() 
                                      if comp['content_features'].get(feature, False))
                total_competitors = len(matrix['comparisons'])
                support_ratio = competitor_support / total_competitors if total_competitors > 0 else 0
                sections.append(f"| {feature.replace('_', ' ').title()} | Planned | {support_ratio*100:.0f}% of competitors |")
        
        # Market Differentiation Strategy
        sections.append("\n### Market Differentiation Strategy\n")
        
        # Technology Stack Advantages
        if competitive_analysis and competitive_analysis.get('tech_advantages'):
            tech_advantages = competitive_analysis['tech_advantages']
            sections.append("#### Technology Stack Advantages")
            for advantage in tech_advantages.get('advantages', []):
                sections.append(f"- {advantage}")
            
            sections.append("\n#### Technology Trends")
            trends = tech_advantages.get('trends', {})
            for tech, adoption in list(trends.items())[:5]:
                sections.append(f"- {tech}: {adoption:.1f}% adoption rate")
        
        # Pricing Position Analysis
        if competitive_analysis and competitive_analysis.get('pricing_analysis'):
            sections.append("\n### Pricing Position Analysis\n")
            pricing = competitive_analysis['pricing_analysis']
            
            # Market Segments
            sections.append("#### Market Segments")
            segments = pricing.get('segments', {})
            sections.append(f"- Premium Segment: {len(segments.get('premium', []))} competitors")
            sections.append(f"- Mid-Range Segment: {len(segments.get('mid_range', []))} competitors")
            sections.append(f"- Value Segment: {len(segments.get('value', []))} competitors")
            
            # Market Position
            if pricing.get('summary', {}).get('market_position'):
                sections.append(f"\nMarket Position: {pricing['summary']['market_position']}")
        
        # User Experience Benefits
        if competitive_analysis and competitive_analysis.get('ux_comparison'):
            sections.append("\n### User Experience Benefits\n")
            ux = competitive_analysis['ux_comparison']
            
            # UX Metrics
            sections.append("#### UX Advantages")
            if ux.get('best_practices'):
                best_practices = next(iter(ux['best_practices'].values()))
                for practice, implemented in best_practices.items():
                    if implemented:
                        sections.append(f"- {practice.replace('_', ' ').title()}")
            
            # UX Recommendations
            if ux.get('recommendations'):
                sections.append("\n#### UX Improvements")
                for rec in ux['recommendations']:
                    sections.append(f"- {rec}")
        
        return "\n".join(sections)

    def _generate_technical_architecture(self) -> str:
        """Generate the technical architecture section."""
        sections = []
        sections.append("## Technical Architecture\n")
        
        # System Overview
        sections.append("### System Overview\n")
        sections.append("Our solution is built on a modern, scalable architecture that emphasizes:")
        sections.append("- Security and data protection")
        sections.append("- High availability and performance")
        sections.append("- Scalability and maintainability")
        sections.append("- Integration capabilities\n")
        
        # Technology Stack
        sections.append("### Technology Stack\n")
        sections.append("#### Frontend")
        sections.append("- React.js for dynamic user interfaces")
        sections.append("- TypeScript for type-safe development")
        sections.append("- Material-UI for consistent design")
        sections.append("- Redux for state management")
        sections.append("- Jest and React Testing Library for testing\n")
        
        sections.append("#### Backend")
        sections.append("- Python FastAPI for high-performance API")
        sections.append("- PostgreSQL for reliable data storage")
        sections.append("- Redis for caching and session management")
        sections.append("- Celery for background task processing")
        sections.append("- Docker for containerization\n")
        
        # Security Architecture
        sections.append("### Security Architecture\n")
        sections.append("Our security architecture implements multiple layers of protection:")
        sections.append("- SSL/TLS encryption for all data in transit")
        sections.append("- Role-based access control (RBAC)")
        sections.append("- Regular security audits and penetration testing")
        sections.append("- Automated vulnerability scanning")
        sections.append("- Secure data backup and disaster recovery\n")
        
        # Deployment Architecture
        sections.append("### Deployment Architecture\n")
        sections.append("The system utilizes a cloud-native architecture:")
        sections.append("- Kubernetes for container orchestration")
        sections.append("- Automated CI/CD pipeline")
        sections.append("- Blue-green deployment strategy")
        sections.append("- Auto-scaling based on demand")
        sections.append("- Multi-region availability\n")
        
        # Integration Architecture
        sections.append("### Integration Architecture\n")
        sections.append("Our system supports various integration methods:")
        sections.append("- RESTful APIs with OpenAPI specification")
        sections.append("- GraphQL for flexible data queries")
        sections.append("- Webhook support for real-time notifications")
        sections.append("- OAuth2 for secure authentication")
        sections.append("- Standard data formats (JSON, XML)\n")
        
        # Performance Optimization
        sections.append("### Performance Optimization\n")
        sections.append("Performance is optimized through:")
        sections.append("- Content Delivery Network (CDN)")
        sections.append("- Database query optimization")
        sections.append("- Caching at multiple levels")
        sections.append("- Asynchronous processing")
        sections.append("- Load balancing\n")
        
        # Monitoring and Maintenance
        sections.append("### Monitoring and Maintenance\n")
        sections.append("Comprehensive monitoring includes:")
        sections.append("- Real-time performance monitoring")
        sections.append("- Automated error tracking")
        sections.append("- System health dashboards")
        sections.append("- Predictive maintenance alerts")
        sections.append("- Regular system updates and patches\n")
        
        return "\n".join(sections)

    def _generate_team_structure(self) -> str:
        """Generate the team structure section."""
        sections = []
        sections.append("## Team Structure\n")
        
        # Project Leadership
        sections.append("### Project Leadership\n")
        sections.append("Our dedicated project team is structured to ensure efficient delivery and clear communication:")
        sections.append("- **Project Director**: Strategic oversight and client relationship management")
        sections.append("- **Technical Lead**: Architecture design and technical decision-making")
        sections.append("- **Product Manager**: Requirements gathering and feature prioritization")
        sections.append("- **Delivery Manager**: Timeline management and resource coordination\n")
        
        # Development Team
        sections.append("### Development Team\n")
        sections.append("Our development team consists of specialized professionals:")
        sections.append("#### Frontend Development")
        sections.append("- Senior Frontend Engineers (React.js, TypeScript)")
        sections.append("- UI/UX Designers")
        sections.append("- Frontend Testing Specialists\n")
        
        sections.append("#### Backend Development")
        sections.append("- Senior Backend Engineers (Python, FastAPI)")
        sections.append("- Database Architects")
        sections.append("- API Integration Specialists\n")
        
        sections.append("#### DevOps & Infrastructure")
        sections.append("- Cloud Infrastructure Engineers")
        sections.append("- DevOps Engineers")
        sections.append("- Security Specialists\n")
        
        # Quality Assurance
        sections.append("### Quality Assurance\n")
        sections.append("Our QA team ensures high-quality deliverables:")
        sections.append("- QA Lead")
        sections.append("- Automated Testing Engineers")
        sections.append("- Performance Testing Specialists")
        sections.append("- Security Testing Engineers\n")
        
        # Support Team
        sections.append("### Support Team\n")
        sections.append("Dedicated support personnel ensure smooth operations:")
        sections.append("- Technical Support Engineers")
        sections.append("- Documentation Specialists")
        sections.append("- Training Coordinators\n")
        
        # Team Communication
        sections.append("### Team Communication\n")
        sections.append("We maintain clear communication channels:")
        sections.append("- Daily standup meetings")
        sections.append("- Weekly progress reviews")
        sections.append("- Bi-weekly client updates")
        sections.append("- Monthly strategic planning sessions")
        sections.append("- Continuous feedback loops\n")
        
        # Scaling & Flexibility
        sections.append("### Scaling & Flexibility\n")
        sections.append("Our team structure is designed to scale based on project needs:")
        sections.append("- Flexible resource allocation")
        sections.append("- Cross-functional team capabilities")
        sections.append("- Knowledge sharing protocols")
        sections.append("- Backup resource availability")
        sections.append("- Training and skill development programs\n")
        
        return "\n".join(sections)