"""Writing agent for content generation."""
from typing import Dict, Any, List, Optional
import logging
from ..models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone,
    ContentSection,
    GeneratedContent,
    ContentMetrics
)

logger = logging.getLogger(__name__)

class WritingAgent:
    """Agent responsible for generating content."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def generate_content(self, request: ContentRequest, topic_analysis: Dict[str, Any]) -> GeneratedContent:
        """Generate content based on request and topic analysis."""
        try:
            if self.progress_callback:
                self.progress_callback("Starting content generation...", 0)
            
            # Generate sections
            sections = []
            total_sections = len(topic_analysis['outline']['sections'])
            
            for i, section_outline in enumerate(topic_analysis['outline']['sections']):
                if self.progress_callback:
                    progress = int((i / total_sections) * 80)  # 0-80%
                    self.progress_callback(f"Generating section: {section_outline['name']}", progress)
                
                # Get themes for this section
                section_themes = topic_analysis['outline']['themes_by_section'].get(section_outline['name'], [])
                
                # Generate section content
                section_content = self._generate_section_content(
                    section_outline['name'],
                    section_outline['expected_content'],
                    section_outline['key_points'],
                    section_themes,
                    request
                )
                
                # Create section
                section = ContentSection(
                    title=section_outline['name'],
                    content=section_content,
                    keywords=self._extract_keywords(section_content, section_themes),
                    metrics=self._calculate_section_metrics(section_content),
                    references=self._gather_references(section_content, request.reference_data)
                )
                sections.append(section)

            # Calculate overall metrics
            metrics = self._calculate_content_metrics(sections)
            
            # Generate summary and recommendations
            if self.progress_callback:
                self.progress_callback("Generating summary...", 90)
            summary = self._generate_summary(sections)
            
            if self.progress_callback:
                self.progress_callback("Generating recommendations...", 95)
            recommendations = self._generate_recommendations(sections)
            
            if self.progress_callback:
                self.progress_callback("Content generation complete", 100)

            return GeneratedContent(
                content_type=request.content_type,
                title=self._generate_title(request, sections),
                sections=sections,
                metadata={
                    'target_audience': request.target_audience,
                    'tone': request.tone.value,
                    'analysis': topic_analysis['metadata']
                },
                metrics=metrics,
                summary=summary,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return self._create_empty_content(request)

    def _generate_section_content(self, section_name: str, expected_content: str, 
                                key_points: List[str], themes: List[Dict[str, Any]], 
                                request: ContentRequest) -> str:
        """Generate content for a section."""
        try:
            # Get selected features
            features = request.reference_data.get('requirements', {}).get('features', [])
            
            # Build section context with more data
            context = {
                'section_name': section_name,
                'expected_content': expected_content,
                'key_points': key_points,
                'themes': themes,
                'target_audience': request.target_audience,
                'tone': request.tone.value,
                'business_name': request.reference_data.get('business_name', ''),
                'industry': request.reference_data.get('industry', ''),
                'website': request.reference_data.get('website', ''),
                'competitors': request.reference_data.get('competitors', []),
                'features': features,
                'project_description': request.reference_data.get('project_description', '')
            }
            
            # Generate section content based on type
            if section_name == 'Executive Summary':
                return self._generate_executive_summary(context)
            elif section_name == 'Project Overview':
                return self._generate_project_overview(context)
            elif section_name == 'Solution Details':
                return self._generate_solution_details(context)
            elif section_name == 'Implementation Plan':
                return self._generate_implementation_plan(context)
            elif section_name == 'Timeline and Deliverables':
                return self._generate_timeline(context)
            elif section_name == 'Investment':
                return self._generate_investment(context)
            else:
                return self._generate_generic_section(context)
                
        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            return f"Error generating content for {section_name}"

    def _calculate_content_metrics(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """Calculate comprehensive metrics for the content."""
        try:
            # Combine all content
            all_content = " ".join(section.content for section in sections)
            all_keywords = set()
            for section in sections:
                all_keywords.update(section.keywords)

            # Calculate base metrics
            base_metrics = {
                'word_count': len(all_content.split()),
                'readability_score': self._calculate_readability(all_content),
                'keyword_density': self._calculate_keyword_density(all_content, all_keywords),
                'sentiment_score': self._calculate_sentiment(all_content),
                'technical_complexity': self._calculate_technical_complexity(all_content),
                'uniqueness_score': self._calculate_uniqueness(all_content)
            }

            # Calculate SEO metrics
            seo_metrics = {
                'keyword_optimization': self._calculate_keyword_optimization(all_content, all_keywords),
                'content_structure': self._analyze_content_structure(sections),
                'meta_data_quality': self._analyze_meta_data(sections)
            }

            # Calculate engagement metrics
            engagement_metrics = {
                'readability': {
                    'score': base_metrics['readability_score'],
                    'grade_level': self._calculate_grade_level(all_content),
                    'reading_time': len(all_content.split()) / 200  # Average reading speed
                },
                'content_quality': {
                    'technical_accuracy': base_metrics['technical_complexity'],
                    'uniqueness': base_metrics['uniqueness_score'],
                    'sentiment': base_metrics['sentiment_score']
                }
            }

            # Calculate ROI metrics
            roi_metrics = self._calculate_roi_metrics(sections)

            # Combine all metrics
            metrics = {
                **base_metrics,
                'seo_metrics': seo_metrics,
                'engagement_metrics': engagement_metrics,
                'roi_metrics': roi_metrics,
                'quality_score': self._calculate_quality_score(base_metrics)
            }

            return metrics

        except Exception as e:
            logger.error(f"Error calculating content metrics: {str(e)}")
            return {
                'word_count': 0,
                'readability_score': 0.0,
                'keyword_density': {},
                'sentiment_score': 0.0,
                'technical_complexity': 0.0,
                'uniqueness_score': 0.0,
                'quality_score': 0.0
            }

    def _calculate_roi_metrics(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """Calculate ROI-related metrics."""
        try:
            return {
                'traffic_potential': {
                    'organic_growth': '150-200%',
                    'mobile_traffic': '200-250%',
                    'bounce_rate_reduction': '25-35%'
                },
                'conversion_potential': {
                    'lead_generation': '75-100%',
                    'conversion_rate': '25-40%',
                    'engagement': '40-60%'
                },
                'efficiency_gains': {
                    'content_updates': '60%',
                    'maintenance': '40%',
                    'customer_service': '35%'
                }
            }
        except Exception:
            return {}

    def _generate_summary(self, sections: List[ContentSection]) -> str:
        """Generate content summary."""
        try:
            summary_points = []
            for section in sections:
                # Extract first sentence of each section
                content = section.content.strip()
                first_sentence = content.split('.')[0] + '.'
                summary_points.append(f"- {section.title}: {first_sentence}")
            
            return "\n".join(summary_points)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""

    def _generate_recommendations(self, sections: List[ContentSection]) -> List[str]:
        """Generate recommendations based on content and client needs."""
        try:
            pain_points = self.context.get('requirements', {}).get('pain_points', [])
            goals = self.context.get('requirements', {}).get('goals', [])
            analytics = self.context.get('analytics', {})
            
            recommendations = []
            
            # Performance recommendations
            if 'slow_performance' in pain_points:
                recommendations.extend([
                    "Implement server-side caching and CDN for improved performance",
                    "Optimize images and media content",
                    "Minimize JavaScript and CSS bundles"
                ])
                
            # Mobile recommendations
            if 'poor_mobile' in pain_points:
                recommendations.extend([
                    "Implement mobile-first responsive design",
                    "Optimize touch targets and navigation for mobile users",
                    "Ensure fast loading on mobile networks"
                ])
                
            # SEO recommendations
            if 'poor_seo' in pain_points or 'seo' in goals:
                recommendations.extend([
                    "Implement structured data markup",
                    "Optimize meta tags and content structure",
                    "Create XML sitemap and robots.txt"
                ])
                
            # Conversion recommendations
            if 'low_conversion' in pain_points or 'lead_generation' in goals:
                recommendations.extend([
                    "Implement clear calls-to-action",
                    "Optimize form design and placement",
                    "Add social proof and testimonials"
                ])
                
            # Analytics recommendations
            if analytics.get('bounce_rate', 0) > 50:
                recommendations.extend([
                    "Improve page load times to reduce bounce rate",
                    "Enhance content engagement",
                    "Optimize landing page experience"
                ])
                
            # Add general recommendations
            recommendations.extend([
                "Regular performance monitoring and optimization",
                "Monthly SEO and analytics reporting",
                "Quarterly strategy reviews and updates"
            ])
            
            return recommendations[:10]  # Return top 10 most relevant recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return [
                "Implement responsive design for optimal mobile experience",
                "Focus on SEO optimization to improve search visibility",
                "Enhance user experience through modern design principles"
            ]

    def _create_empty_content(self, request: ContentRequest) -> GeneratedContent:
        """Create empty content structure."""
        return GeneratedContent(
            content_type=request.content_type,
            title=f"Proposal for {request.reference_data.get('business_name', '')}",
            sections=[],
            metadata={
                'target_audience': request.target_audience,
                'tone': request.tone.value,
                'analysis': {}
            },
            metrics={},
            summary="",
            recommendations=[]
        )

    def _create_empty_section(self, name: str) -> ContentSection:
        """Create empty content section."""
        return ContentSection(
            title=name,
            content="",
            keywords=[],
            metrics={},
            references=[]
        )

    def _generate_title(self, request: ContentRequest, sections: List[ContentSection]) -> str:
        """Generate proposal title."""
        return f"Website Redesign Proposal for {request.reference_data.get('business_name', '')}"

    def _generate_introduction(self, section_name: str, expected_content: str,
                             tone: ContentTone) -> str:
        """Generate section introduction."""
        try:
            if tone == ContentTone.FORMAL:
                return f"This section provides {expected_content.lower()}."
            elif tone == ContentTone.TECHNICAL:
                return f"Technical overview of {section_name.lower()}."
            else:
                return f"Overview of {expected_content.lower()}."
        except Exception:
            return f"Introduction to {section_name}"

    def _generate_point_content(self, point: str, themes: List[str],
                              tone: ContentTone, audience: str) -> str:
        """Generate content for a key point."""
        try:
            if tone == ContentTone.TECHNICAL:
                return f"Technical analysis shows that {point.lower()}."
            elif tone == ContentTone.PERSUASIVE:
                return f"It is evident that {point.lower()}, which benefits {audience}."
            else:
                return f"{point}."
        except Exception:
            return point

    def _generate_supporting_details(self, themes: List[str],
                                   tone: ContentTone) -> str:
        """Generate supporting details."""
        try:
            if tone == ContentTone.TECHNICAL:
                return "Technical details: " + ", ".join(themes)
            elif tone == ContentTone.PERSUASIVE:
                return "Key benefits include: " + ", ".join(themes)
            else:
                return "Additional details: " + ", ".join(themes)
        except Exception:
            return "Supporting details not available"

    def _generate_conclusion(self, section_name: str, key_points: List[str],
                           tone: ContentTone) -> str:
        """Generate section conclusion."""
        try:
            if tone == ContentTone.FORMAL:
                return f"In conclusion, {section_name.lower()} demonstrates {', '.join(key_points[:2])}."
            elif tone == ContentTone.PERSUASIVE:
                return f"As shown, {', '.join(key_points[:2])} make this solution ideal."
            else:
                return f"To summarize: {', '.join(key_points[:2])}."
        except Exception:
            return f"Conclusion of {section_name}"

    def _extract_keywords(self, content: str, themes: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from content."""
        try:
            # Start with theme names as keywords
            keywords = [theme['name'] for theme in themes]
            
            # Add common industry terms
            industry_terms = [
                'website', 'redesign', 'responsive', 'SEO',
                'user experience', 'conversion', 'optimization'
            ]
            keywords.extend(industry_terms)
            
            # Remove duplicates and sort
            return sorted(list(set(keywords)))
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []

    def _calculate_section_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate metrics for a section."""
        try:
            return {
                'word_count': len(content.split()),
                'readability_score': self._calculate_readability(content),
                'sentiment_score': self._calculate_sentiment(content),
                'technical_complexity': self._calculate_technical_complexity(content)
            }
        except Exception as e:
            logger.error(f"Error calculating section metrics: {str(e)}")
            return {}

    def _gather_references(self, content: str, reference_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather references used in content."""
        try:
            references = []
            if reference_data.get('competitors'):
                references.append({
                    'type': 'competitor_analysis',
                    'sources': reference_data['competitors']
                })
            if reference_data.get('industry'):
                references.append({
                    'type': 'industry_research',
                    'source': f"Industry analysis for {reference_data['industry']}"
                })
            return references
        except Exception as e:
            logger.error(f"Error gathering references: {str(e)}")
            return []

    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score."""
        try:
            words = len(text.split())
            sentences = len(text.split('.'))
            if sentences == 0:
                return 0.0
            return min(1.0, words / (sentences * 20))  # Simple readability metric
        except Exception:
            return 0.0

    def _calculate_keyword_density(self, text: str, keywords: set) -> Dict[str, float]:
        """Calculate keyword density."""
        try:
            word_count = len(text.split())
            return {
                keyword: text.lower().count(keyword.lower()) / max(word_count, 1)
                for keyword in keywords
            }
        except Exception:
            return {}

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score."""
        try:
            # Simple sentiment based on positive/negative word count
            positive_words = ['improve', 'enhance', 'optimize', 'benefit', 'success']
            negative_words = ['problem', 'issue', 'challenge', 'difficult', 'risk']
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total = positive_count + negative_count
            if total == 0:
                return 0.5
            return positive_count / total
        except Exception:
            return 0.5

    def _calculate_technical_complexity(self, text: str) -> float:
        """Calculate technical complexity score."""
        try:
            technical_terms = [
                'implementation', 'architecture', 'infrastructure',
                'optimization', 'integration', 'deployment'
            ]
            words = text.lower().split()
            technical_count = sum(1 for word in words if word in technical_terms)
            return min(1.0, technical_count / len(words) * 10)
        except Exception:
            return 0.0

    def _calculate_uniqueness(self, text: str) -> float:
        """Calculate content uniqueness score."""
        try:
            # Simple uniqueness based on word variety
            words = text.lower().split()
            unique_words = len(set(words))
            return min(1.0, unique_words / len(words))
        except Exception:
            return 0.0

    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        try:
            weights = {
                'readability_score': 0.3,
                'technical_complexity': 0.2,
                'uniqueness_score': 0.2,
                'sentiment_score': 0.3
            }

            score = sum(
                metrics[metric] * weight
                for metric, weight in weights.items()
                if metric in metrics
            )

            return max(0.0, min(1.0, score))

        except Exception:
            return 0.0

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text."""
        try:
            sentences = text.split('.')
            # Consider sentences that start with key phrases
            key_phrases = ['this shows', 'importantly', 'notably', 'key',
                         'significant', 'essential', 'critical']
            key_points = []

            for sentence in sentences:
                sentence = sentence.strip().lower()
                if any(sentence.startswith(phrase) for phrase in key_phrases):
                    key_points.append(sentence.capitalize())

            return key_points[:3]  # Return top 3 key points

        except Exception:
            return [] 

    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive summary section with enhanced analytics."""
        features_list = self._format_features_list(context['features'])
        competitor_analysis = self._analyze_competitors(context['competitors'])
        current_website = self._analyze_current_website(context)
        business_goals = self._analyze_business_goals(context)
        
        return f"""
For {context['business_name']}, we propose a comprehensive website redesign solution 
that will transform your online presence and drive business growth in the {context['industry']} industry.

Current Situation:
{current_website}

Business Goals:
{business_goals}

Market Analysis:
{competitor_analysis}

Target Audience:
- Demographics: {context.get('target_details', {}).get('demographics', 'Not specified')}
- Key Interests: {context.get('target_details', {}).get('interests', 'Not specified')}

Proposed Solution:
We will create a modern, high-performance website that incorporates:
{features_list}

Key Benefits:
- Enhanced user experience optimized for {context['target_audience']}
- Improved search engine visibility and rankings
- Increased lead generation and conversion rates
- Stronger brand presence in the {context['industry']} market
- Competitive advantage through modern functionality

Timeline and Budget:
- Timeline: {context.get('timeline', 'Standard')} implementation
- Budget Range: {context.get('budget_range', 'Custom')} investment

Our solution directly addresses your requirements for {context['project_description']} while
ensuring scalability and future growth potential.
"""

    def _generate_project_overview(self, context: Dict[str, Any]) -> str:
        """Generate project overview section."""
        competitor_insights = self._analyze_competitor_websites(context['competitors'])
        industry_trends = self._analyze_industry_trends(context['industry'])
        
        return f"""
Current Situation:
{context['business_name']} requires a website redesign to better serve its 
{context['target_audience']} and strengthen its position in the {context['industry']}
industry. Our analysis of your current website ({context['website']}) reveals:

Website Analysis:
- Current online presence assessment
- User experience evaluation
- Technical performance metrics
- SEO positioning review

Market Research:
{industry_trends}

Competitive Landscape:
{competitor_insights}

Project Objectives:
{self._format_list(context['key_points'])}

Success Criteria:
- Increased website traffic and engagement metrics
- Higher conversion rates for key actions
- Improved search engine rankings
- Enhanced brand perception and professionalism
"""

    def _generate_solution_details(self, context: Dict[str, Any]) -> str:
        """Generate solution details section."""
        features_list = self._format_features_list(context['features'])
        market_insights = self._generate_market_insights(context)
        tech_stack = self._recommend_tech_stack(context['features'])
        
        return f"""
Market Analysis:
{market_insights}

Proposed Solution:
For {context['business_name']}, we will create a modern, responsive website that 
delivers exceptional user experience and drives business results. Our solution 
incorporates industry best practices and proven technologies.

Technical Architecture:
{tech_stack}

Key Features and Benefits:
{features_list}

Implementation Approach:
Our solution leverages modern web technologies and proven development practices to 
ensure a robust, maintainable website that will serve {context['business_name']} 
well into the future.

Performance Targets:
- Page load time under 2 seconds
- Mobile responsiveness score > 90/100
- SEO optimization score > 90/100
- Security compliance with industry standards
- 99.9% uptime guarantee
"""

    def _generate_market_insights(self, context: Dict[str, Any]) -> str:
        """Generate market insights based on research."""
        return f"""
Our research into the {context['industry']} market reveals:
- Growing demand for digital solutions
- Increasing focus on mobile users
- Rising importance of personalized experiences
- Shift towards integrated digital services
- Emphasis on data security and privacy

Target Audience Analysis ({context['target_audience']}):
- Primary user demographics and behaviors
- Key user journey touchpoints
- Common pain points and needs
- Preferred interaction patterns
- Device usage patterns
"""

    def _recommend_tech_stack(self, features: List[str]) -> str:
        """Recommend technology stack based on requirements."""
        tech_recommendations = {
            'responsive': """
Frontend Technologies:
- React.js for dynamic user interfaces
- Bootstrap for responsive design
- Progressive Web App capabilities""",
            'seo': """
SEO Optimization:
- Server-side rendering
- Structured data implementation
- Performance optimization tools""",
            'cms': """
Content Management:
- Headless CMS integration
- Custom workflow automation
- Media optimization""",
            'ecommerce': """
E-commerce Features:
- Secure payment processing
- Inventory management
- Order fulfillment automation"""
        }
        
        selected_tech = [tech_recommendations.get(f, "") for f in features]
        return "\n".join(filter(None, selected_tech))

    def _generate_implementation_plan(self, context: Dict[str, Any]) -> str:
        """Generate implementation plan section."""
        return f"""
Implementation Strategy:
Our structured approach ensures a smooth, efficient website redesign process for 
{context['business_name']}. We follow industry best practices and maintain clear 
communication throughout the project.

Project Phases:
1. Discovery and Planning
   - Requirements gathering
   - Technical assessment
   - Content strategy development

2. Design and Development
   - UI/UX design
   - Frontend development
   - Backend implementation
   - Content integration

3. Testing and Optimization
   - Quality assurance
   - Performance testing
   - SEO optimization
   - User testing

4. Launch and Support
   - Final review
   - Deployment
   - Training
   - Post-launch support

Resources and Team:
- Project Manager
- UI/UX Designer
- Frontend Developer
- Backend Developer
- QA Engineer
- SEO Specialist
"""

    def _generate_timeline(self, context: Dict[str, Any]) -> str:
        """Generate timeline and deliverables section."""
        return f"""
Project Timeline:
The website redesign project for {context['business_name']} will be completed in 
12 weeks, with key milestones and deliverables throughout the process.

Week 1-2: Discovery Phase
- Project kickoff
- Requirements documentation
- Technical specifications
- Content strategy

Week 3-4: Design Phase
- Wireframes
- Visual designs
- Design approval

Week 5-8: Development Phase
- Frontend development
- Backend implementation
- Content integration
- Initial testing

Week 9-10: Testing Phase
- Quality assurance
- Performance optimization
- User acceptance testing
- SEO implementation

Week 11-12: Launch Phase
- Final testing
- Content migration
- Launch preparation
- Go-live and monitoring

Key Deliverables:
{self._format_list(context['key_points'])}
"""

    def _generate_investment(self, context: Dict[str, Any]) -> str:
        """Generate investment section."""
        try:
            # Get budget range and features
            budget_range = context.get('budget_range', '20k-50k')
            features = context.get('features', [])
            
            # Base costs for different budget ranges
            cost_ranges = {
                '5k-10k': {
                    'discovery': '1,000',
                    'design': '2,000',
                    'development': '3,000',
                    'testing': '500',
                    'support': '500'
                },
                '10k-20k': {
                    'discovery': '2,000',
                    'design': '4,000',
                    'development': '8,000',
                    'testing': '1,000',
                    'support': '1,000'
                },
                '20k-50k': {
                    'discovery': '4,000',
                    'design': '8,000',
                    'development': '20,000',
                    'testing': '3,000',
                    'support': '3,000'
                },
                '50k+': {
                    'discovery': '8,000',
                    'design': '15,000',
                    'development': '35,000',
                    'testing': '5,000',
                    'support': '5,000'
                }
            }
            
            # Get costs for selected budget range
            costs = cost_ranges.get(budget_range, cost_ranges['20k-50k'])
            
            # Feature-specific costs
            feature_costs = {
                'responsive': '3,000',
                'seo': '2,500',
                'cms': '5,000',
                'ecommerce': '8,000'
            }
            
            # Calculate feature costs
            selected_feature_costs = []
            for feature in features:
                if feature in feature_costs:
                    selected_feature_costs.append(f"- {feature.title()} Implementation: ${feature_costs[feature]}")
            
            # Calculate ROI projections
            roi_analysis = self._calculate_roi_projections(context)
            
            return f"""
Investment Overview:
Our comprehensive website redesign solution for {context['business_name']} represents 
a strategic investment in your digital presence and business growth.

Core Development Costs:
- Discovery and Planning: ${costs['discovery']}
- Design and UX: ${costs['design']}
- Development: ${costs['development']}
- Testing and QA: ${costs['testing']}
- Support and Training: ${costs['support']}

Additional Feature Costs:
{chr(10).join(selected_feature_costs) if selected_feature_costs else "No additional features selected"}

Return on Investment Analysis:
{roi_analysis}

Payment Schedule:
- 30% upon project initiation (${int(int(costs['development']) * 0.3):,})
- 30% upon design approval (${int(int(costs['development']) * 0.3):,})
- 30% upon development completion (${int(int(costs['development']) * 0.3):,})
- 10% upon successful launch (${int(int(costs['development']) * 0.1):,})

Value-Added Services:
- 3 months post-launch support
- SEO optimization and monitoring
- Performance analytics
- Security monitoring
- Training and documentation
- Monthly performance reports
"""
        except Exception as e:
            logger.error(f"Error generating investment section: {str(e)}")
            return "Error generating content for Investment"

    def _calculate_roi_projections(self, context: Dict[str, Any]) -> str:
        """Generate ROI projections."""
        return f"""
Projected Benefits (12-month outlook):
1. Traffic Growth
   - Organic traffic increase: 150-200%
   - Mobile traffic increase: 200-250%
   - Reduced bounce rate: 25-35%

2. Conversion Optimization
   - Lead generation increase: 75-100%
   - Conversion rate improvement: 25-40%
   - User engagement increase: 40-60%

3. Operational Efficiency
   - Content update time reduced by 60%
   - Technical maintenance costs reduced by 40%
   - Customer service efficiency improved by 35%

4. Market Position
   - Brand visibility increase: 100-150%
   - Market share growth: 15-25%
   - Customer satisfaction improvement: 40-50%
"""

    def _generate_cost_breakdown(self, features: List[str]) -> str:
        """Generate detailed cost breakdown."""
        base_costs = """
Core Development:
- Discovery and Planning: $X,XXX
- Design and UX: $XX,XXX
- Frontend Development: $XX,XXX
- Backend Development: $XX,XXX"""
        
        feature_costs = {
            'responsive': "- Responsive Design Implementation: $X,XXX",
            'seo': "- SEO Optimization Package: $X,XXX",
            'cms': "- CMS Integration: $XX,XXX",
            'ecommerce': "- E-commerce Implementation: $XX,XXX"
        }
        
        selected_costs = [feature_costs.get(f, "") for f in features]
        return base_costs + "\n" + "\n".join(filter(None, selected_costs))

    def _generate_generic_section(self, context: Dict[str, Any]) -> str:
        """Generate content for a generic section."""
        return f"""
{context['section_name']}:
{context['expected_content']}

Key Points:
{self._format_list(context['key_points'])}

Additional Considerations:
- Tailored for {context['target_audience']}
- Industry-specific best practices for {context['industry']}
- Proven methodologies and approaches
"""

    def _format_list(self, items: List[str]) -> str:
        """Format a list of items with bullet points."""
        return "\n".join(f"- {item}" for item in items) 

    def _format_features_list(self, features: List[str]) -> str:
        """Format features with descriptions."""
        feature_descriptions = {
            'responsive': '- Responsive Design: Optimal viewing experience across all devices',
            'seo': '- SEO Optimization: Enhanced visibility and organic traffic growth',
            'cms': '- Content Management System: Easy content updates and management',
            'ecommerce': '- E-commerce Functionality: Secure online transaction capabilities'
        }
        return '\n'.join(feature_descriptions.get(f, f"- {f.title()}") for f in features)

    def _analyze_competitors(self, competitors: List[str]) -> str:
        """Generate competitor analysis summary."""
        if not competitors:
            return ""
        
        return f"""
Our analysis of {len(competitors)} competitor websites reveals opportunities to differentiate
through superior user experience, modern design, and optimized performance."""

    def _analyze_competitor_websites(self, competitors: List[str]) -> str:
        """Generate detailed competitor analysis."""
        if not competitors:
            return "No direct competitors provided for analysis."
        
        return f"""
Based on analysis of {len(competitors)} competitor websites, we've identified:
- Common industry features and functionalities
- Design trends and user experience patterns
- Content strategy approaches
- Technical implementations
- Market positioning strategies

This analysis reveals opportunities to:
- Differentiate through superior user experience
- Implement innovative features
- Optimize for target audience engagement
- Establish unique market positioning
"""

    def _analyze_industry_trends(self, industry: str) -> str:
        """Generate industry trends analysis."""
        return f"""
Key {industry} Industry Trends:
- Mobile-first design approach
- AI-powered user interactions
- Enhanced security measures
- Performance optimization
- Accessibility compliance
- Data-driven decision making
"""

    def _analyze_current_website(self, context: Dict[str, Any]) -> str:
        """Analyze current website performance."""
        analytics = context.get('analytics', {})
        pain_points = context.get('requirements', {}).get('pain_points', [])
        
        current_state = """
Current Website Analysis:
- Monthly Visitors: {:,}
- Bounce Rate: {}%
- Performance Issues: {}
- Mobile Experience: {}
- SEO Status: {}
- Design Assessment: {}
""".format(
            analytics.get('monthly_visitors', 0),
            analytics.get('bounce_rate', 0),
            'Major concerns' if 'slow_performance' in pain_points else 'Acceptable',
            'Needs improvement' if 'poor_mobile' in pain_points else 'Satisfactory',
            'Underperforming' if 'poor_seo' in pain_points else 'Adequate',
            'Outdated' if 'outdated_design' in pain_points else 'Current'
        )
        
        return current_state

    def _analyze_business_goals(self, context: Dict[str, Any]) -> str:
        """Analyze business goals and requirements."""
        goals = context.get('requirements', {}).get('goals', [])
        goal_descriptions = {
            'lead_generation': 'Increase qualified leads and conversions',
            'brand_awareness': 'Enhance brand visibility and recognition',
            'sales': 'Drive online sales and revenue growth',
            'customer_service': 'Improve customer service and support'
        }
        
        selected_goals = [goal_descriptions.get(g, g) for g in goals]
        return "\n".join(f"- {goal}" for goal in selected_goals)

    def _generate_timeline_based_on_preferences(self, context: Dict[str, Any]) -> str:
        """Generate timeline based on client preferences."""
        timeline_pref = context.get('timeline', 'flexible')
        timeline_adjustments = {
            'asap': {
                'discovery': '1 week',
                'design': '2 weeks',
                'development': '3-4 weeks',
                'testing': '1 week',
                'launch': '1 week'
            },
            '1-2months': {
                'discovery': '2 weeks',
                'design': '2-3 weeks',
                'development': '4-5 weeks',
                'testing': '1-2 weeks',
                'launch': '1 week'
            },
            '3-4months': {
                'discovery': '3-4 weeks',
                'design': '4-5 weeks',
                'development': '6-8 weeks',
                'testing': '2-3 weeks',
                'launch': '1-2 weeks'
            }
        }
        
        timeline = timeline_adjustments.get(timeline_pref, timeline_adjustments['3-4months'])
        return f"""
Project Timeline (Based on {context.get('timeline', 'standard')} timeline preference):

1. Discovery and Planning Phase: {timeline['discovery']}
   - Initial consultation and requirements gathering
   - Technical assessment and planning
   - Content strategy development

2. Design Phase: {timeline['design']}
   - Wireframe development
   - Visual design creation
   - Design review and approval

3. Development Phase: {timeline['development']}
   - Frontend development
   - Backend implementation
   - Content integration
   - Initial testing

4. Testing Phase: {timeline['testing']}
   - Quality assurance
   - Performance optimization
   - User acceptance testing
   - Final adjustments

5. Launch Phase: {timeline['launch']}
   - Final testing
   - Content migration
   - Launch preparation
   - Go-live and monitoring
"""

    def _generate_cost_breakdown(self, context: Dict[str, Any]) -> str:
        """Generate cost breakdown based on requirements and budget."""
        budget_range = context.get('budget_range', '20k-50k')
        features = context.get('requirements', {}).get('features', [])
        
        # Base costs for different budget ranges
        cost_ranges = {
            '5k-10k': {
                'discovery': '1,000',
                'design': '2,000',
                'development': '3,000',
                'testing': '500',
                'support': '500'
            },
            '10k-20k': {
                'discovery': '2,000',
                'design': '4,000',
                'development': '8,000',
                'testing': '1,000',
                'support': '1,000'
            },
            '20k-50k': {
                'discovery': '4,000',
                'design': '8,000',
                'development': '20,000',
                'testing': '3,000',
                'support': '3,000'
            },
            '50k+': {
                'discovery': '8,000',
                'design': '15,000',
                'development': '35,000',
                'testing': '5,000',
                'support': '5,000'
            }
        }
        
        costs = cost_ranges.get(budget_range, cost_ranges['20k-50k'])
        
        # Feature-specific costs
        feature_costs = {
            'responsive': '- Responsive Design Implementation: $3,000',
            'seo': '- SEO Optimization Package: $2,500',
            'cms': '- CMS Integration: $5,000',
            'ecommerce': '- E-commerce Implementation: $8,000'
        }
        
        selected_features = [feature_costs.get(f, "") for f in features]
        
        return f"""
Core Development:
- Discovery and Planning: ${costs['discovery']}
- Design and UX: ${costs['design']}
- Development: ${costs['development']}
- Testing and QA: ${costs['testing']}
- Support and Training: ${costs['support']}

Additional Features:
{chr(10).join(filter(None, selected_features))}
"""