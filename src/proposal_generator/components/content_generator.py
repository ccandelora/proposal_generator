"""Module for generating proposal content."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generator for proposal content sections."""

    def __init__(self):
        """Initialize the ContentGenerator."""
        self.logger = logger

    def generate_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary section."""
        try:
            if not data or 'client' not in data:
                raise ValueError("Invalid input data")

            client = data['client']
            if not isinstance(client, dict):
                raise ValueError("Invalid client data")

            return {
                'content': self._generate_summary_content(client),
                'key_points': self._extract_key_points(data)
            }
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {str(e)}")
            raise

    def generate_market_overview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market overview section."""
        try:
            if not data or 'market_analysis' not in data:
                raise ValueError("Invalid market data")

            market = data['market_analysis']
            return {
                'trends': market.get('trends', []),
                'opportunities': market.get('opportunities', []),
                'challenges': market.get('challenges', [])
            }
        except Exception as e:
            self.logger.error(f"Error generating market overview: {str(e)}")
            raise

    def generate_competitive_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive analysis section."""
        try:
            if not data or 'competitors' not in data:
                raise ValueError("Invalid competitor data")

            return {
                'positioning': self._analyze_market_position(data),
                'differentiators': self._identify_differentiators(data),
                'recommendations': []
            }
        except Exception as e:
            self.logger.error(f"Error generating competitive analysis: {str(e)}")
            raise

    def generate_solution_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate solution proposal section."""
        try:
            if not data or 'client' not in data:
                raise ValueError("Invalid input data")

            return {
                'approach': self._generate_approach(data),
                'benefits': self._identify_benefits(data),
                'timeline': []
            }
        except Exception as e:
            self.logger.error(f"Error generating solution proposal: {str(e)}")
            raise

    def generate_technical_specifications(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical specifications section."""
        try:
            return {
                'architecture': self._design_architecture(data),
                'features': self._specify_features(data),
                'technologies': self._select_technologies(data)
            }
        except Exception as e:
            self.logger.error(f"Error generating technical specifications: {str(e)}")
            raise

    def generate_implementation_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation plan section."""
        try:
            return {
                'phases': self._define_phases(data),
                'milestones': self._set_milestones(data),
                'resources': self._allocate_resources(data)
            }
        except Exception as e:
            self.logger.error(f"Error generating implementation plan: {str(e)}")
            raise

    def generate_pricing_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pricing model section."""
        try:
            return {
                'packages': self._create_packages(data),
                'breakdown': self._create_cost_breakdown(data),
                'terms': self._define_payment_terms(data)
            }
        except Exception as e:
            self.logger.error(f"Error generating pricing model: {str(e)}")
            raise

    def generate_with_template(self, data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using a custom template."""
        try:
            result = {}
            for section in template['sections']:
                if hasattr(self, f"generate_{section}"):
                    method = getattr(self, f"generate_{section}")
                    result[section] = method(data)
                else:
                    result[section] = self._generate_custom_section(section, template['placeholders'])
            return result
        except Exception as e:
            self.logger.error(f"Error generating content with template: {str(e)}")
            raise

    def _generate_summary_content(self, client: Dict[str, Any]) -> str:
        """Generate the main content for executive summary."""
        return (
            f"Proposal for {client.get('name', 'Client')}: "
            f"Specializing in {', '.join(client.get('specialties', []))} "
            f"with a focus on {', '.join(client.get('target_audience', []))}. "
            f"Key strengths include {', '.join(client.get('unique_selling_points', []))}."
        )

    def _extract_key_points(self, data: Dict[str, Any]) -> List[str]:
        """Extract key points for executive summary."""
        points = []
        if 'client' in data:
            points.extend(data['client'].get('unique_selling_points', []))
        if 'market_analysis' in data:
            points.extend(data['market_analysis'].get('opportunities', []))
        return points[:5]  # Return top 5 points

    def _analyze_market_position(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market positioning."""
        return {
            'market_share': 0.0,
            'growth_potential': 'high'
        }

    def _identify_differentiators(self, data: Dict[str, Any]) -> List[str]:
        """Identify key differentiators."""
        client = data.get('client', {})
        return client.get('unique_selling_points', [])

    def _generate_approach(self, data: Dict[str, Any]) -> str:
        """Generate solution approach."""
        client = data.get('client', {})
        return f"Customized solution for {client.get('name', 'client')} focusing on their specific needs."

    def _identify_benefits(self, data: Dict[str, Any]) -> List[str]:
        """Identify solution benefits."""
        client = data.get('client', {})
        return [
            f"Specialized expertise in {', '.join(client.get('specialties', []))}",
            "Customized approach",
            "Proven track record"
        ]

    def _design_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design system architecture."""
        return {
            'type': 'web_application',
            'components': ['frontend', 'backend', 'database', 'api'],
            'infrastructure': 'cloud_based'
        }

    def _specify_features(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Specify system features."""
        return [
            {
                'name': 'User Authentication',
                'priority': 'high',
                'complexity': 'medium'
            },
            {
                'name': 'Document Management',
                'priority': 'high',
                'complexity': 'high'
            }
        ]

    def _select_technologies(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Select implementation technologies."""
        return {
            'frontend': ['React', 'TypeScript', 'Material-UI'],
            'backend': ['Python', 'FastAPI', 'PostgreSQL'],
            'infrastructure': ['AWS', 'Docker', 'Kubernetes']
        }

    def _define_phases(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define implementation phases."""
        return [
            {
                'name': 'Planning and Design',
                'duration': '4 weeks',
                'deliverables': ['Technical Design', 'Project Plan']
            },
            {
                'name': 'Development',
                'duration': '12 weeks',
                'deliverables': ['Core Features', 'Initial Testing']
            }
        ]

    def _set_milestones(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Set project milestones."""
        return [
            {
                'name': 'Design Approval',
                'timeline': 'Week 4',
                'criteria': ['Technical design approved', 'Project plan finalized']
            },
            {
                'name': 'MVP Release',
                'timeline': 'Week 12',
                'criteria': ['Core features implemented', 'Initial testing completed']
            }
        ]

    def _allocate_resources(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Allocate project resources."""
        return [
            {
                'role': 'Project Manager',
                'allocation': '100%',
                'duration': '20 weeks'
            },
            {
                'role': 'Senior Developer',
                'allocation': '100%',
                'duration': '16 weeks'
            }
        ]

    def _create_packages(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create pricing packages."""
        return [
            {
                'name': 'Basic',
                'price': 50000,
                'features': ['Core Features', 'Basic Support']
            },
            {
                'name': 'Premium',
                'price': 100000,
                'features': ['All Features', '24/7 Support', 'Priority Updates']
            }
        ]

    def _create_cost_breakdown(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Create cost breakdown."""
        return {
            'development': 60000.0,
            'testing': 20000.0,
            'deployment': 10000.0,
            'support': 10000.0
        }

    def _define_payment_terms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Define payment terms."""
        return {
            'schedule': 'monthly',
            'installments': 4,
            'upfront_percentage': 25
        }

    def _generate_custom_section(self, section: str, placeholders: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom section content."""
        return {
            'title': section.replace('_', ' ').title(),
            'content': 'Custom section content',
            'placeholders': placeholders
        }

    def generate_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a content strategy based on analysis data.
        
        Args:
            data: Dictionary containing analysis data including:
                - market_analysis: Market analysis results
                - seo_analysis: SEO analysis results
                - target_audience: List of target audience segments
                - key_services: List of key services/products
                
        Returns:
            Dict containing content strategy recommendations
        """
        try:
            # Extract data
            market_analysis = data.get('market_analysis', {})
            seo_analysis = data.get('seo_analysis', {})
            target_audience = data.get('target_audience', [])
            key_services = data.get('key_services', [])

            # Generate content pillars
            content_pillars = []
            
            # Add service-based content pillars
            for service in key_services:
                content_pillars.append({
                    'topic': service,
                    'keywords': self._generate_keywords(service, seo_analysis),
                    'content_types': self._recommend_content_types(service, target_audience)
                })

            # Add market trend-based content pillars
            if isinstance(market_analysis, dict):
                for trend in market_analysis.get('trends', []):
                    if isinstance(trend, dict):
                        content_pillars.append({
                            'topic': trend.get('name', ''),
                            'keywords': self._generate_keywords(trend.get('name', ''), seo_analysis),
                            'content_types': self._recommend_content_types(trend.get('name', ''), target_audience)
                        })

            # Generate recommendations
            recommendations = []
            
            # Add content type recommendations
            recommendations.extend([
                {
                    'type': 'content_type',
                    'priority': 'high',
                    'description': 'Create in-depth blog posts about industry topics'
                },
                {
                    'type': 'content_type',
                    'priority': 'medium',
                    'description': 'Develop video content for product demonstrations'
                }
            ])

            # Add SEO recommendations
            if isinstance(seo_analysis, dict):
                content_seo = seo_analysis.get('content', {})
                if isinstance(content_seo, dict):
                    for opportunity in content_seo.get('keyword_opportunities', []):
                        if isinstance(opportunity, dict):
                            recommendations.append({
                                'type': 'seo',
                                'priority': 'high',
                                'description': f"Target keyword: {opportunity.get('keyword', '')}"
                            })

            return {
                'content_pillars': content_pillars,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"Error generating content strategy: {str(e)}")
            return {
                'content_pillars': [],
                'recommendations': [
                    {
                        'type': 'error',
                        'priority': 'high',
                        'description': f'Error generating strategy: {str(e)}'
                    }
                ]
            }

    def _generate_keywords(self, topic: str, seo_analysis: Dict[str, Any]) -> List[str]:
        """Generate relevant keywords for a topic."""
        # Placeholder implementation
        base_keywords = [topic.lower()]
        modifiers = ['guide', 'tutorial', 'tips', 'best practices']
        return [f"{topic} {modifier}" for modifier in modifiers]

    def _recommend_content_types(self, topic: str, target_audience: List[str]) -> List[str]:
        """Recommend content types based on topic and audience."""
        # Placeholder implementation
        return ['blog posts', 'videos', 'infographics', 'case studies']