"""Comprehensive Proposal Generator module."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .components.seo_screenshotter import SEOScreenshotter
from .components.market_analyzer import MarketAnalyzer
from .components.seo_analyzer import SEOAnalyzer
from .components.content_generator import ContentGenerator
from .components.mockup_generator import MockupGenerator
from .config import get_gemini_llm

async def generate_comprehensive_proposal(
    client_name: str,
    business_name: str,
    industry: str,
    target_market: str,
    website: str,
    project_description: str,
    special_features: Optional[str] = None,
    pain_points: Optional[str] = None,
    business_goals: Optional[str] = None,
    competitors: Optional[List[str]] = None,
    budget: Optional[str] = None,
    timeline: Optional[str] = None,
    technical_requirements: Optional[str] = None
) -> str:
    """
    Generate a comprehensive proposal based on form input.
    
    Args:
        client_name: Name of the client
        business_name: Name of the business
        industry: Industry type
        target_market: Target market description
        website: Client's website URL
        project_description: Description of the project
        special_features: Special features requested
        pain_points: Current pain points
        business_goals: Business objectives
        competitors: List of competitor URLs
        budget: Project budget range
        timeline: Project timeline
        technical_requirements: Technical requirements
        
    Returns:
        str: Generated proposal in markdown format
    """
    # Initialize the generator
    generator = ComprehensiveProposalGenerator()
    
    # Convert form inputs to required format
    project_goals = []
    if project_description:
        project_goals.append(f"Primary Goal: {project_description}")
    if special_features:
        project_goals.append(f"Special Features: {special_features}")
    if business_goals:
        for goal in business_goals.split('\n'):
            if goal.strip():
                project_goals.append(goal.strip())
                
    # Process target audience
    target_audience = [segment.strip() for segment in target_market.split(',') if segment.strip()]
    
    # Process key services/features
    key_services = []
    if special_features:
        key_services.extend([feature.strip() for feature in special_features.split('\n') if feature.strip()])
    
    # Ensure competitors is a list
    competitor_urls = competitors if competitors else []
    
    # Generate the proposal
    proposal_data = await generator.generate_proposal(
        client_url=website,
        competitor_urls=competitor_urls,
        client_name=client_name,
        project_goals=project_goals,
        industry=industry,
        target_audience=target_audience,
        key_services=key_services
    )
    
    # Add budget and timeline information to the proposal
    proposal_sections = proposal_data['proposal_document'].split('\n')
    
    if budget:
        proposal_sections.append("\n## Investment Details")
        proposal_sections.append(f"\nProject Budget Range: {budget}")
        
    if timeline:
        proposal_sections.append("\n## Project Timeline")
        proposal_sections.append(f"\nEstimated Duration: {timeline}")
        
    if technical_requirements:
        proposal_sections.append("\n## Technical Specifications")
        proposal_sections.append("\nSpecific technical requirements:")
        for req in technical_requirements.split('\n'):
            if req.strip():
                proposal_sections.append(f"- {req.strip()}")
                
    if pain_points:
        proposal_sections.append("\n## Current Challenges")
        proposal_sections.append("\nIdentified pain points to address:")
        for point in pain_points.split('\n'):
            if point.strip():
                proposal_sections.append(f"- {point.strip()}")
    
    return '\n'.join(proposal_sections)

class ComprehensiveProposalGenerator:
    """Class for generating comprehensive project proposals using all available agents."""
    
    def __init__(self):
        """Initialize all components."""
        self.llm = get_gemini_llm()
        self.screenshotter = SEOScreenshotter()
        self.market_analyzer = MarketAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.content_generator = ContentGenerator()
        self.mockup_generator = MockupGenerator()

        # Set LLM for all components
        for component in [self.screenshotter, self.market_analyzer, self.seo_analyzer, 
                        self.content_generator, self.mockup_generator]:
            if hasattr(component, 'llm'):
                component.llm = self.llm

    async def generate_proposal(self,
                              client_url: str,
                              competitor_urls: List[str],
                              client_name: str,
                              project_goals: List[str],
                              industry: str,
                              target_audience: List[str],
                              key_services: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive proposal using all available agents and components.
        
        Args:
            client_url: Client's website URL
            competitor_urls: List of competitor URLs
            client_name: Client's business name
            project_goals: List of project objectives
            industry: Client's industry
            target_audience: List of target audience segments
            key_services: List of client's key services/products
            
        Returns:
            Dictionary containing all proposal sections and assets
        """
        # Collect all analyses in parallel
        visual_analysis = self.screenshotter.analyze_website(client_url, competitor_urls)
        market_analysis = await self.market_analyzer.analyze_market({
            'industry': industry,
            'target_audience': target_audience,
            'competitors': competitor_urls,
            'key_services': key_services
        })
        seo_analysis = self.seo_analyzer.analyze_seo(
            client_url,
            {'technical': True, 'content': True, 'backlinks': True},
            {'competitors': competitor_urls}
        )
        
        # Generate content strategy
        content_strategy = self.content_generator.generate_strategy({
            'market_analysis': market_analysis,
            'seo_analysis': seo_analysis,
            'target_audience': target_audience,
            'key_services': key_services
        })
        
        # Generate mockups based on analyses
        mockups = self.mockup_generator.generate_mockup({
            'project': client_name,
            'requirements': self._extract_mockup_requirements(
                visual_analysis,
                market_analysis,
                seo_analysis
            ),
            'page_type': 'homepage'
        })
        
        # Compile all recommendations
        recommendations = self._compile_recommendations(
            visual_analysis,
            market_analysis,
            seo_analysis,
            content_strategy
        )
        
        # Generate proposal document
        proposal = self._generate_proposal_document(
            client_name=client_name,
            project_goals=project_goals,
            visual_analysis=visual_analysis,
            market_analysis=market_analysis,
            seo_analysis=seo_analysis,
            content_strategy=content_strategy,
            mockups=mockups,
            recommendations=recommendations
        )
        
        return {
            'proposal_document': proposal,
            'mockups': mockups,
            'analyses': {
                'visual': visual_analysis,
                'market': market_analysis,
                'seo': seo_analysis
            },
            'content_strategy': content_strategy,
            'recommendations': recommendations
        }

    def _extract_mockup_requirements(self,
                                   visual_analysis: Dict[str, Any],
                                   market_analysis: Dict[str, Any],
                                   seo_analysis: Dict[str, Any]) -> List[str]:
        """Extract mockup requirements from various analyses."""
        requirements = []
        
        # Visual requirements
        if 'design_analysis' in visual_analysis:
            design = visual_analysis['design_analysis']
            if design.get('colors', {}).get('harmony_score', 1.0) < 0.7:
                requirements.append('improve_color_harmony')
            if design.get('layout', {}).get('effectiveness', '') == 'limited':
                requirements.append('enhance_layout_structure')
                
        # Market-driven requirements
        if 'trends' in market_analysis:
            for trend in market_analysis['trends']:
                if trend.get('adoption_rate', 0) > 0.7:
                    requirements.append(f'incorporate_{trend["name"]}')
                    
        # SEO-driven requirements
        if 'technical' in seo_analysis:
            tech_seo = seo_analysis['technical']
            if tech_seo.get('mobile_friendly', False) == False:
                requirements.append('responsive_design')
            if tech_seo.get('page_speed', 0) < 80:
                requirements.append('optimize_performance')
                
        return requirements

    def _compile_recommendations(self,
                               visual_analysis: Dict[str, Any],
                               market_analysis: Dict[str, Any],
                               seo_analysis: Dict[str, Any],
                               content_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile and prioritize recommendations from all analyses."""
        recommendations = []
        
        # Visual recommendations
        if 'recommendations' in visual_analysis:
            for rec in visual_analysis['recommendations']:
                recommendations.append({
                    **rec,
                    'category': 'visual',
                    'source': 'visual_analysis'
                })
                
        # Market recommendations
        if 'recommendations' in market_analysis:
            for rec in market_analysis['recommendations']:
                recommendations.append({
                    **rec,
                    'category': 'market',
                    'source': 'market_analysis'
                })
                
        # SEO recommendations
        if 'recommendations' in seo_analysis:
            for rec in seo_analysis['recommendations']:
                recommendations.append({
                    **rec,
                    'category': 'seo',
                    'source': 'seo_analysis'
                })
                
        # Content recommendations
        if 'recommendations' in content_strategy:
            for rec in content_strategy['recommendations']:
                recommendations.append({
                    **rec,
                    'category': 'content',
                    'source': 'content_strategy'
                })
                
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 4))
        
        return recommendations

    def _generate_proposal_document(self,
                                  client_name: str,
                                  project_goals: List[str],
                                  visual_analysis: Dict[str, Any],
                                  market_analysis: Dict[str, Any],
                                  seo_analysis: Dict[str, Any],
                                  content_strategy: Dict[str, Any],
                                  mockups: Dict[str, Any],
                                  recommendations: List[Dict[str, Any]]) -> str:
        """Generate the complete proposal document."""
        sections = []
        
        # Title and Introduction
        sections.append("# Digital Enhancement Proposal")
        sections.append(f"\nPrepared for: {client_name}")
        
        # Executive Summary
        sections.append("\n## Executive Summary")
        sections.append("\nBased on our comprehensive analysis of your digital presence, market position, "
                       "and competitive landscape, we have identified significant opportunities for growth "
                       "and improvement. This proposal outlines our findings and recommendations across "
                       "multiple dimensions including visual design, user experience, SEO, market positioning, "
                       "and content strategy.")
        
        # Project Goals
        sections.append("\n## Project Goals")
        for i, goal in enumerate(project_goals, 1):
            sections.append(f"\n{i}. {goal}")
        
        # Market Analysis
        sections.append("\n## Market Analysis")
        sections.append("\n### Industry Trends")
        for trend in market_analysis.get('trends', []):
            sections.append(f"\n- **{trend['name']}**: {trend['description']}")
            sections.append(f"  - Adoption Rate: {trend.get('adoption_rate', 0)*100:.1f}%")
            sections.append(f"  - Impact: {trend.get('impact', 'Unknown')}")
            
        sections.append("\n### Competitive Landscape")
        sections.append(f"\nAnalyzed {len(market_analysis.get('competitors', []))} competitors:")
        for comp in market_analysis.get('competitors', []):
            sections.append(f"\n- {comp.get('name', 'Unknown')}")
            sections.append(f"  - Market Share: {comp.get('market_share', 0)*100:.1f}%")
            sections.append(f"  - Key Strengths: {', '.join(comp.get('strengths', []))}")
        
        # SEO Analysis
        sections.append("\n## SEO Analysis")
        sections.append("\n### Technical SEO")
        tech_seo = seo_analysis.get('technical', {})
        sections.append(f"\n- Mobile Friendliness: {tech_seo.get('mobile_score', 0)}/100")
        sections.append(f"- Page Speed: {tech_seo.get('page_speed', 0)}/100")
        sections.append(f"- Technical Issues Found: {len(tech_seo.get('issues', []))}")
        
        sections.append("\n### Content SEO")
        content_seo = seo_analysis.get('content', {})
        sections.append(f"\n- Content Quality Score: {content_seo.get('quality_score', 0)}/100")
        sections.append(f"- Keyword Opportunities: {len(content_seo.get('keyword_opportunities', []))}")
        
        # Visual Analysis
        sections.append("\n## Visual Analysis")
        design = visual_analysis.get('design_analysis', {})
        sections.append("\n### Design Elements")
        sections.append(f"\n- Color Harmony: {design.get('colors', {}).get('harmony_score', 0)*100:.1f}%")
        sections.append(f"- Typography Consistency: {design.get('typography', {}).get('consistency_score', 0)*100:.1f}%")
        sections.append(f"- Layout Effectiveness: {design.get('layout', {}).get('effectiveness', 'Not analyzed')}")
        
        # Content Strategy
        sections.append("\n## Content Strategy")
        sections.append("\n### Content Pillars")
        for pillar in content_strategy.get('content_pillars', []):
            sections.append(f"\n- **{pillar['topic']}**")
            sections.append(f"  - Target Keywords: {', '.join(pillar.get('keywords', []))}")
            sections.append(f"  - Content Types: {', '.join(pillar.get('content_types', []))}")
        
        # Proposed Solutions
        sections.append("\n## Proposed Solutions")
        
        # Visual Mockups
        sections.append("\n### Design Mockups")
        sections.append("\nWe have created initial design mockups incorporating our recommendations:")
        sections.append(f"\n- Desktop Version: {mockups.get('files', {}).get('desktop', 'Not available')}")
        sections.append(f"- Mobile Version: {mockups.get('files', {}).get('mobile', 'Not available')}")
        
        # Recommendations
        sections.append("\n### Prioritized Recommendations")
        current_category = None
        for rec in recommendations:
            if rec['category'] != current_category:
                current_category = rec['category']
                sections.append(f"\n#### {current_category.title()} Improvements")
            sections.append(f"\n- **{rec['priority'].upper()}**: {rec['description']}")
        
        # Implementation Plan
        sections.append("\n## Implementation Plan")
        
        sections.append("\n### Phase 1: Foundation (Weeks 1-3)")
        sections.append("1. Technical SEO improvements")
        sections.append("2. Core design system implementation")
        sections.append("3. Basic content structure optimization")
        
        sections.append("\n### Phase 2: Enhancement (Weeks 4-7)")
        sections.append("1. Advanced design implementation")
        sections.append("2. Content creation and optimization")
        sections.append("3. User experience improvements")
        
        sections.append("\n### Phase 3: Optimization (Weeks 8-10)")
        sections.append("1. Performance optimization")
        sections.append("2. Content refinement")
        sections.append("3. Competitive positioning enhancement")
        
        # Investment and ROI
        sections.append("\n## Investment and Expected Returns")
        sections.append("\n### Projected Outcomes")
        sections.append("- Improved search engine rankings")
        sections.append("- Enhanced user engagement")
        sections.append("- Stronger brand presence")
        sections.append("- Increased conversion rates")
        sections.append("- Better competitive positioning")
        
        # Next Steps
        sections.append("\n## Next Steps")
        sections.append("\n1. **Project Review Meeting**: Discuss findings and recommendations")
        sections.append("2. **Scope Refinement**: Adjust implementation plan based on priorities")
        sections.append("3. **Project Kickoff**: Begin with Phase 1 implementation")
        
        return "\n".join(sections) 