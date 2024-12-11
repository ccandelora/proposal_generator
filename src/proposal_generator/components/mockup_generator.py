from typing import Dict, List, Any
import os
from PIL import Image, ImageDraw, ImageFont
import platform
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MockupGenerator(BaseAgent):
    """Generates website mockups based on analysis."""
    
    def __init__(self):
        super().__init__()
        self.mockups_dir = os.path.join(os.getcwd(), 'src', 'mockups')
        os.makedirs(self.mockups_dir, exist_ok=True)
        logger.info(f"Mockups will be saved to: {self.mockups_dir}")

    def process(self, client_brief: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate mockups based on client brief and analysis."""
        try:
            # Extract relevant information
            website_analysis = context.get('website_analysis', {}) if context else {}
            competitive_analysis = context.get('competitive_analysis', {}) if context else {}
            
            # Generate mockups for key pages
            mockups = {
                'home': self._generate_home_mockup(client_brief, website_analysis),
                'services': self._generate_services_mockup(client_brief),
                'portfolio': self._generate_portfolio_mockup(client_brief),
                'about': self._generate_about_mockup(client_brief),
                'contact': self._generate_contact_mockup(client_brief)
            }
            
            # Add custom pages based on features
            if client_brief.get('features'):
                for feature in client_brief['features']:
                    if 'portal' in feature.lower():
                        mockups['client_portal'] = self._generate_portal_mockup(client_brief)
                    elif 'case stud' in feature.lower():
                        mockups['case_studies'] = self._generate_case_studies_mockup(client_brief)
            
            return {
                'mockups': mockups,
                'design_system': self._generate_design_system(client_brief, website_analysis),
                'responsive_layouts': self._generate_responsive_layouts()
            }
            
        except Exception as e:
            logger.error(f"Error generating mockups: {str(e)}")
            return {
                'error': str(e),
                'mockups': {}
            }

    def _generate_home_mockup(self, client_brief: Dict[str, Any], website_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate home page mockup."""
        return {
            'layout': 'modern-hero',
            'sections': [
                {
                    'type': 'hero',
                    'content': {
                        'headline': f"Welcome to {client_brief.get('client_name', 'Our Company')}",
                        'subheadline': client_brief.get('description', ''),
                        'cta': 'Get Started'
                    }
                },
                {
                    'type': 'services-grid',
                    'content': {
                        'title': 'Our Services',
                        'services': self._extract_services(client_brief)
                    }
                },
                {
                    'type': 'testimonials',
                    'content': {
                        'title': 'Client Success Stories',
                        'testimonials': self._generate_sample_testimonials()
                    }
                }
            ]
        }

    def _generate_services_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate services page mockup."""
        return {
            'layout': 'services-showcase',
            'sections': [
                {
                    'type': 'header',
                    'content': {
                        'title': 'Our Services',
                        'description': 'Comprehensive solutions for your business needs'
                    }
                },
                {
                    'type': 'service-cards',
                    'content': {
                        'services': self._extract_services(client_brief)
                    }
                }
            ]
        }

    def _generate_portfolio_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio page mockup."""
        return {
            'layout': 'portfolio-grid',
            'sections': [
                {
                    'type': 'header',
                    'content': {
                        'title': 'Our Work',
                        'description': 'Recent projects and success stories'
                    }
                },
                {
                    'type': 'project-grid',
                    'content': {
                        'projects': self._generate_sample_projects()
                    }
                }
            ]
        }

    def _generate_about_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate about page mockup."""
        return {
            'layout': 'about-us',
            'sections': [
                {
                    'type': 'company-intro',
                    'content': {
                        'title': f"About {client_brief.get('client_name', 'Us')}",
                        'description': client_brief.get('description', '')
                    }
                },
                {
                    'type': 'team',
                    'content': {
                        'title': 'Our Team',
                        'team_members': self._generate_sample_team()
                    }
                }
            ]
        }

    def _generate_contact_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contact page mockup."""
        return {
            'layout': 'contact-split',
            'sections': [
                {
                    'type': 'contact-form',
                    'content': {
                        'title': 'Get in Touch',
                        'form_fields': [
                            {'type': 'text', 'label': 'Name'},
                            {'type': 'email', 'label': 'Email'},
                            {'type': 'text', 'label': 'Company'},
                            {'type': 'textarea', 'label': 'Message'}
                        ]
                    }
                },
                {
                    'type': 'contact-info',
                    'content': {
                        'address': '123 Tech Street, San Francisco, CA',
                        'email': 'contact@example.com',
                        'phone': '(555) 123-4567'
                    }
                }
            ]
        }

    def _generate_portal_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate client portal mockup."""
        return {
            'layout': 'portal-dashboard',
            'sections': [
                {
                    'type': 'login',
                    'content': {
                        'title': 'Client Portal',
                        'form_fields': [
                            {'type': 'email', 'label': 'Email'},
                            {'type': 'password', 'label': 'Password'}
                        ]
                    }
                },
                {
                    'type': 'dashboard',
                    'content': {
                        'widgets': [
                            {'type': 'projects', 'title': 'Active Projects'},
                            {'type': 'documents', 'title': 'Recent Documents'},
                            {'type': 'messages', 'title': 'Messages'},
                            {'type': 'timeline', 'title': 'Project Timeline'}
                        ]
                    }
                }
            ]
        }

    def _generate_case_studies_mockup(self, client_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate case studies page mockup."""
        return {
            'layout': 'case-studies-grid',
            'sections': [
                {
                    'type': 'header',
                    'content': {
                        'title': 'Case Studies',
                        'description': 'Explore our successful client projects'
                    }
                },
                {
                    'type': 'case-studies',
                    'content': {
                        'studies': self._generate_sample_case_studies()
                    }
                }
            ]
        }

    def _generate_design_system(self, client_brief: Dict[str, Any], website_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate design system specifications."""
        return {
            'colors': {
                'primary': '#0066CC',
                'secondary': '#2E3B4E',
                'accent': '#FF6B35',
                'background': '#FFFFFF',
                'text': '#333333'
            },
            'typography': {
                'headings': 'Montserrat',
                'body': 'Open Sans',
                'sizes': {
                    'h1': '2.5rem',
                    'h2': '2rem',
                    'h3': '1.75rem',
                    'body': '1rem'
                }
            },
            'components': {
                'buttons': {
                    'primary': {'background': '#0066CC', 'text': '#FFFFFF'},
                    'secondary': {'background': '#2E3B4E', 'text': '#FFFFFF'},
                    'outline': {'border': '#0066CC', 'text': '#0066CC'}
                },
                'cards': {
                    'shadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'radius': '8px'
                }
            }
        }

    def _generate_responsive_layouts(self) -> Dict[str, Any]:
        """Generate responsive layout specifications."""
        return {
            'breakpoints': {
                'mobile': '320px',
                'tablet': '768px',
                'desktop': '1024px',
                'wide': '1440px'
            },
            'grid': {
                'columns': {
                    'mobile': 4,
                    'tablet': 8,
                    'desktop': 12
                },
                'gutter': '24px'
            },
            'navigation': {
                'mobile': 'hamburger',
                'tablet': 'horizontal',
                'desktop': 'horizontal'
            }
        }

    def _extract_services(self, client_brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract services from client brief."""
        features = client_brief.get('features', [])
        return [{'title': feature, 'description': f"Detailed description of {feature}"} for feature in features]

    def _generate_sample_testimonials(self) -> List[Dict[str, Any]]:
        """Generate sample testimonials."""
        return [
            {
                'text': 'Outstanding service and technical expertise. Highly recommended!',
                'author': 'John Smith',
                'company': 'Tech Solutions Inc.'
            },
            {
                'text': 'Transformed our business with innovative solutions.',
                'author': 'Sarah Johnson',
                'company': 'Digital Ventures'
            }
        ]

    def _generate_sample_projects(self) -> List[Dict[str, Any]]:
        """Generate sample portfolio projects."""
        return [
            {
                'title': 'E-Commerce Platform',
                'description': 'Modern e-commerce solution with advanced features',
                'image': 'project1.jpg'
            },
            {
                'title': 'Enterprise Dashboard',
                'description': 'Data visualization and analytics platform',
                'image': 'project2.jpg'
            }
        ]

    def _generate_sample_team(self) -> List[Dict[str, Any]]:
        """Generate sample team members."""
        return [
            {
                'name': 'Michael Chen',
                'role': 'Technical Director',
                'image': 'team1.jpg'
            },
            {
                'name': 'Emily Rodriguez',
                'role': 'UX Designer',
                'image': 'team2.jpg'
            }
        ]

    def _generate_sample_case_studies(self) -> List[Dict[str, Any]]:
        """Generate sample case studies."""
        return [
            {
                'title': 'Digital Transformation',
                'client': 'Global Retail Corp',
                'challenge': 'Legacy system modernization',
                'solution': 'Cloud migration and modern architecture',
                'results': ['50% faster processing', '30% cost reduction']
            },
            {
                'title': 'Customer Experience Enhancement',
                'client': 'FinTech Solutions',
                'challenge': 'Poor user engagement',
                'solution': 'UX redesign and mobile app',
                'results': ['200% increase in user engagement', '45% higher conversion']
            }
        ]