from typing import Dict, Any, List, Optional
import logging
import os
import tempfile
import html2text
import platform
import time
import json
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from .components.website_analyzer import WebsiteAnalyzer
from .components.competitor_finder import CompetitorFinder
from .components.competitor_analyzer import CompetitorAnalyzer
from .components.competitive_analyzer import CompetitiveAnalyzer
from .components.sentiment_analyzer import SentimentAnalyzer
from .components.seo_analyzer import SEOAnalyzer
from .components.website_screenshotter import WebsiteScreenshotter
from .components.mockup_generator import MockupGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProposalGenerator:
    """Generates business proposals based on client briefs."""
    
    def __init__(self):
        """Initialize the proposal generator with its components."""
        self.website_analyzer = WebsiteAnalyzer()
        self.competitor_finder = CompetitorFinder()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.competitive_analyzer = CompetitiveAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.website_screenshotter = WebsiteScreenshotter()
        self.mockup_generator = MockupGenerator()

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
                sentiment_analysis = self.sentiment_analyzer.process(client_brief)
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

    def generate_pdf(self, content: Dict[str, Any], output_path: str) -> str:
        """Generate a PDF from the proposal content."""
        try:
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
            
            # Add title
            story.append(Paragraph(content['title'], styles['CustomHeading1']))
            story.append(Spacer(1, 30))
            
            # Add sections
            for section in content['sections']:
                # Add section title
                story.append(Paragraph(section['title'], styles['CustomHeading2']))
                story.append(Spacer(1, 12))
                
                # Process section content
                content_lines = section['content'].split('\n')
                current_list = []
                
                for line in content_lines:
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
                        if line.startswith('### '):
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
                        logger.warning(f"Error processing line '{line}': {str(e)}")
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
                
                story.append(Spacer(1, 20))
            
            # Build the PDF
            doc.build(story)
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _generate_title(self, client_brief: Dict[str, Any]) -> str:
        """Generate proposal title."""
        return f"Proposal for {client_brief.get('client_name', 'Client')}"

    def _generate_executive_summary(self, client_brief: Dict[str, Any], 
                                  competitive_analysis: Optional[Dict[str, Any]], 
                                  sentiment_analysis: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Generate executive summary section."""
        content = ["## Executive Summary\n\n"]
        
        # Add client overview
        client_name = client_brief.get('client_name', 'our client')
        industry = client_brief.get('industry', 'legal services')
        content.append(f"We are pleased to present this proposal to {client_name} ")
        content.append(f"for enhancing their presence in the {industry} market. ")
        
        # Add market context
        if competitive_analysis and competitive_analysis.get('market_analysis'):
            market_position = competitive_analysis['market_analysis'].get('market_position', {})
            if market_position.get('position'):
                content.append(f"Our analysis indicates a {market_position['position'].lower()} market ")
                if market_position.get('factors'):
                    content.append("characterized by " + ", ".join(market_position['factors'][:2]) + ". ")
        
        # Add sentiment context
        if sentiment_analysis and sentiment_analysis.get('review_analysis'):
            review_analysis = sentiment_analysis['review_analysis']
            if review_analysis.get('sentiment_breakdown'):
                sentiment = review_analysis['sentiment_breakdown']
                content.append(f"\nMarket sentiment analysis reveals {sentiment.get('positive', 0)}% positive ")
                content.append(f"and {sentiment.get('negative', 0)}% negative sentiment in current market offerings. ")
        
        # Add value proposition
        content.append("\n### Our Value Proposition\n\n")
        content.append("We propose a comprehensive solution that will:\n\n")
        content.append("* Enhance market presence and competitive positioning\n")
        content.append("* Optimize service delivery and client engagement\n")
        content.append("* Leverage technology for operational efficiency\n")
        content.append("* Drive sustainable growth and market leadership\n")
        
        return {
            'title': 'Executive Summary',
            'content': ''.join(content)
        }

    def _generate_market_analysis(self, competitive_analysis: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Generate market analysis section."""
        content = ["## Market Analysis\n\n"]
        
        if not competitive_analysis:
            content.append("Based on our preliminary market research:\n\n")
            content.append("* Market shows potential for growth and innovation\n")
            content.append("* Opportunities exist for service differentiation\n")
            content.append("* Technology adoption can provide competitive advantage\n")
            return {
                'title': 'Market Analysis',
                'content': ''.join(content)
            }
        
        # Market Overview
        content.append("### Market Overview\n\n")
        if competitive_analysis.get('market_trends'):
            trends = competitive_analysis['market_trends']
            if isinstance(trends, dict):
                trend_summary = trends.get('trend_summary', {})
                if trend_summary:
                    content.append(f"Current market interest: {trend_summary.get('current_interest', 'N/A')}\n")
                    content.append(f"Average market interest: {trend_summary.get('average_interest', 'N/A')}\n")
                    content.append(f"Peak market interest: {trend_summary.get('max_interest', 'N/A')}\n\n")
        
        # Competitor Analysis
        if competitive_analysis.get('competitors'):
            content.append("### Competitor Analysis\n\n")
            competitors = competitive_analysis['competitors']
            if isinstance(competitors, list):
                for comp in competitors[:3]:  # Show top 3 competitors
                    if isinstance(comp, dict):
                        content.append(f"#### {comp.get('name', 'Competitor')}\n")
                        if comp.get('description'):
                            content.append(f"{comp['description']}\n")
                        if comp.get('strengths'):
                            content.append("\nStrengths:\n")
                            for strength in comp['strengths']:
                                content.append(f"* {strength}\n")
        
        # Market Trends
        if competitive_analysis.get('market_trends'):
            content.append("\n### Market Trends\n\n")
            trends = competitive_analysis['market_trends']
            if isinstance(trends, list):
                for trend in trends[:5]:  # Show top 5 trends
                    content.append(f"* {trend}\n")
        
        return {
            'title': 'Market Analysis',
            'content': ''.join(content)
        }

    def _generate_competitive_positioning(self, competitive_analysis: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Generate competitive positioning section."""
        content = ["## Competitive Positioning\n\n"]
        
        if not competitive_analysis:
            content.append("Our competitive positioning strategy focuses on:\n\n")
            content.append("* Service excellence and innovation\n")
            content.append("* Technology-driven efficiency\n")
            content.append("* Client-centric approach\n")
            content.append("* Market specialization\n")
            return {
                'title': 'Competitive Positioning',
                'content': ''.join(content)
            }
        
        # Strengths and Opportunities
        content.append("### Strengths and Opportunities\n\n")
        if competitive_analysis.get('strengths'):
            for strength in competitive_analysis['strengths']:
                content.append(f"* {strength}\n")
        
        # Market Position
        if competitive_analysis.get('market_position'):
            content.append("\n### Market Position\n\n")
            position = competitive_analysis['market_position']
            if isinstance(position, dict):
                if position.get('summary'):
                    content.append(f"{position['summary']}\n\n")
                if position.get('advantages'):
                    content.append("Key advantages:\n")
                    for advantage in position['advantages']:
                        content.append(f"* {advantage}\n")
        
        # Differentiation Strategy
        content.append("\n### Differentiation Strategy\n\n")
        content.append("Our approach emphasizes:\n\n")
        content.append("* Technology-driven service delivery\n")
        content.append("* Specialized expertise and experience\n")
        content.append("* Client-focused communication\n")
        content.append("* Innovative solutions\n")
        
        return {
            'title': 'Competitive Positioning',
            'content': ''.join(content)
        }

    def _generate_technical_architecture(self, client_brief: Dict[str, Any]) -> Dict[str, str]:
        """Generate technical architecture section."""
        content = ["## Technical Architecture\n\n"]
        
        # Core Architecture
        content.append("### Core Architecture\n\n")
        content.append("Our solution is built on a modern, scalable architecture:\n\n")
        content.append("* Cloud-native infrastructure\n")
        content.append("* Microservices architecture\n")
        content.append("* Containerized deployment\n")
        content.append("* API-first design\n")
        
        # Security
        content.append("\n### Security\n\n")
        content.append("Enterprise-grade security measures include:\n\n")
        content.append("* End-to-end encryption\n")
        content.append("* Multi-factor authentication\n")
        content.append("* Regular security audits\n")
        content.append("* Automated threat detection\n")
        
        # Scalability
        content.append("\n### Scalability\n\n")
        content.append("The system is designed for growth:\n\n")
        content.append("* Horizontal scaling capability\n")
        content.append("* Load balancing\n")
        content.append("* Caching layers\n")
        content.append("* Database optimization\n")
        
        return {
            'title': 'Technical Architecture',
            'content': ''.join(content)
        }

    def _generate_team_structure(self, client_brief: Dict[str, Any]) -> Dict[str, str]:
        """Generate team structure section."""
        content = ["## Team Structure\n\n"]
        
        # Project Leadership
        content.append("### Project Leadership\n\n")
        content.append("* Project Director: Strategic oversight\n")
        content.append("* Technical Lead: Architecture and implementation\n")
        content.append("* Product Manager: Requirements and delivery\n")
        
        # Development Team
        content.append("\n### Development Team\n\n")
        content.append("* Senior Developers (3)\n")
        content.append("* UI/UX Specialists (2)\n")
        content.append("* QA Engineers (2)\n")
        content.append("* DevOps Engineer\n")
        
        # Support Team
        content.append("\n### Support Team\n\n")
        content.append("* Technical Support Engineers\n")
        content.append("* Documentation Specialists\n")
        content.append("* Training Coordinators\n")
        
        return {
            'title': 'Team Structure',
            'content': ''.join(content)
        }

    def _generate_project_timeline(self, client_brief: Dict[str, Any]) -> Dict[str, str]:
        """Generate project timeline section."""
        content = ["## Project Timeline\n\n"]
        
        # Discovery Phase
        content.append("### Phase 1: Discovery (2-3 weeks)\n\n")
        content.append("* Requirements gathering\n")
        content.append("* Technical assessment\n")
        content.append("* Architecture planning\n")
        
        # Development Phase
        content.append("\n### Phase 2: Development (8-10 weeks)\n\n")
        content.append("* Core functionality development\n")
        content.append("* Integration implementation\n")
        content.append("* Regular progress reviews\n")
        
        # Testing Phase
        content.append("\n### Phase 3: Testing (3-4 weeks)\n\n")
        content.append("* Comprehensive testing\n")
        content.append("* Performance optimization\n")
        content.append("* Security auditing\n")
        
        # Deployment Phase
        content.append("\n### Phase 4: Deployment (2-3 weeks)\n\n")
        content.append("* Final deployment preparations\n")
        content.append("* Staff training\n")
        content.append("* Go-live support\n")
        
        return {
            'title': 'Project Timeline',
            'content': ''.join(content)
        }

    def _generate_investment_section(self, client_brief: Dict[str, Any]) -> Dict[str, str]:
        """Generate investment section."""
        content = ["## Investment\n\n"]
        
        # Development Costs
        content.append("### Development Investment\n\n")
        content.append("* Core Development: $75,000\n")
        content.append("* Design & UX: $25,000\n")
        content.append("* Testing & QA: $15,000\n")
        content.append("* Deployment: $10,000\n")
        
        # Ongoing Costs
        content.append("\n### Ongoing Support\n\n")
        content.append("* Monthly Maintenance: $2,500\n")
        content.append("* Support Hours: Included\n")
        content.append("* Updates: Included\n")
        content.append("* Security Patches: Included\n")
        
        # Payment Schedule
        content.append("\n### Payment Schedule\n\n")
        content.append("* 30% upon project initiation\n")
        content.append("* 30% at development milestone\n")
        content.append("* 30% at testing completion\n")
        content.append("* 10% at project completion\n")
        
        return {
            'title': 'Investment',
            'content': ''.join(content)
        }

    def _generate_next_steps(self) -> Dict[str, str]:
        """Generate next steps section."""
        content = ["## Next Steps\n\n"]
        
        # Review and Discussion
        content.append("### 1. Review and Discussion\n\n")
        content.append("* Schedule detailed review meeting\n")
        content.append("* Discuss requirements and approach\n")
        content.append("* Address any questions\n")
        
        # Agreement
        content.append("\n### 2. Agreement and Setup\n\n")
        content.append("* Finalize project scope\n")
        content.append("* Sign agreement\n")
        content.append("* Initial payment\n")
        
        # Project Start
        content.append("\n### 3. Project Initiation\n\n")
        content.append("* Team onboarding\n")
        content.append("* Project setup\n")
        content.append("* Kick-off meeting\n")
        
        return {
            'title': 'Next Steps',
            'content': ''.join(content)
        }