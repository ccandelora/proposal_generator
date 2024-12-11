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

    def create_proposal(self, client_brief: Dict[str, Any]) -> str:
        """Create a complete proposal based on client brief."""
        try:
            self.logger.info("Starting proposal generation")
            
            # Initialize analyses
            website_analysis = None
            competitor_analysis = None
            competitive_analysis = None
            sentiment_analysis = None
            seo_analysis = None
            visual_analysis = None
            
            # Get analysis options
            analysis_options = client_brief.get('analysis_options', {})
            
            # Website Analysis
            website_url = client_brief.get('website_url')
            if website_url and analysis_options.get('website_analysis'):
                self.logger.info(f"Analyzing website: {website_url}")
                website_analysis = self.website_analyzer.process(website_url)
                if website_analysis.get('error'):
                    self.logger.error(f"Website analysis failed: {website_analysis['error']}")
                    website_analysis = None
                else:
                    # Additional analyses for the website
                    seo_analysis = self.seo_analyzer.process({'website': website_url})
                    visual_analysis = self.website_screenshotter.process({'url': website_url, 'is_client': True})
            
            # Competitor Analysis
            if analysis_options.get('competitor_analysis'):
                self.logger.info("Finding and analyzing competitors...")
                # First find competitors
                finder_results = self.competitor_finder.process(client_brief)
                
                if finder_results and finder_results.get('competitors'):
                    self.logger.info(f"Found {len(finder_results['competitors'])} competitors")
                    # Then analyze them in detail
                    competitor_analysis = self.competitor_analyzer.process(finder_results['competitors'])
                    
                    if competitor_analysis and competitor_analysis.get('competitors'):
                        self.logger.info("Analyzing market and financial data...")
                        # Get market and financial data
                        competitors = [comp.get('website', '') for comp in competitor_analysis.get('competitors', [])]
                        competitive_analysis = self.competitive_analyzer.process({
                            'company_name': client_brief.get('client_name', ''),
                            'competitors': competitors,
                            'industry': client_brief.get('industry', '')
                        })
                else:
                    self.logger.warning("No competitors found by competitor finder")
            
            # Sentiment Analysis
            if analysis_options.get('sentiment_analysis'):
                self.logger.info("Analyzing market sentiment...")
                sentiment_analysis = self.sentiment_analyzer.process(client_brief)
            
            # Generate mockups if requested
            mockups = None
            if analysis_options.get('mockups'):
                self.logger.info("Generating mockups...")
                mockups = self.mockup_generator.process(client_brief)
            
            # Generate each section
            sections = []
            
            # Title
            project_name = f"Proposal for {client_brief.get('client_name', 'Client')}"
            sections.append(f"# {project_name}\n")
            
            # Executive Summary
            sections.append(self._generate_executive_summary(
                client_brief,
                website_analysis=website_analysis,
                competitor_analysis=competitor_analysis,
                competitive_analysis=competitive_analysis,
                sentiment_analysis=sentiment_analysis,
                seo_analysis=seo_analysis
            ))
            sections.append("")
            
            # Current Website Analysis
            if website_analysis or seo_analysis or visual_analysis:
                sections.append(self._generate_website_overview(
                    website_analysis=website_analysis,
                    seo_analysis=seo_analysis,
                    visual_analysis=visual_analysis
                ))
                sections.append("")
            
            # Market Analysis
            if competitor_analysis or competitive_analysis or sentiment_analysis:
                sections.append(self._generate_market_analysis(
                    competitor_analysis=competitor_analysis,
                    competitive_analysis=competitive_analysis,
                    sentiment_analysis=sentiment_analysis
                ))
                sections.append("")
            
            # Project Scope
            sections.append(self._generate_project_scope(
                client_brief,
                website_analysis=website_analysis,
                seo_analysis=seo_analysis,
                visual_analysis=visual_analysis
            ))
            sections.append("")
            
            # Implementation Strategy
            sections.append(self._generate_implementation_strategy(
                client_brief,
                website_analysis=website_analysis,
                competitor_analysis=competitor_analysis,
                competitive_analysis=competitive_analysis,
                seo_analysis=seo_analysis
            ))
            sections.append("")
            
            # Mockups and Visuals
            if mockups:
                sections.append(self._generate_mockups_section(mockups))
                sections.append("")
            
            # Investment
            sections.append(self._generate_investment(client_brief))
            
            return "\n".join(sections)
            
        except Exception as e:
            self.logger.error(f"Error generating proposal: {str(e)}")
            raise

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
            if sentiment_analysis.get('overall_sentiment'):
                sections.append(f"\nOverall Market Sentiment: {sentiment_analysis['overall_sentiment']}")
            
            key_topics = sentiment_analysis.get('key_topics', [])
            if key_topics:
                sections.append("\nKey Topics:")
                # Safely get up to 3 topics
                for topic in key_topics[:3] if key_topics else []:
                    sections.append(f"- {topic}")
        
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