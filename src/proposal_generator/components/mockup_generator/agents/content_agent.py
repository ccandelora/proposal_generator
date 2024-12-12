"""Content agent for mockup generation."""
import logging
from typing import Dict, Any, List
from ..models.mockup_model import (
    MockupRequest,
    ContentElements,
    ContentElement,
    DeviceType,
    ElementType
)

logger = logging.getLogger(__name__)

class ContentAgent:
    """Agent responsible for generating mockup content elements."""

    def generate_content(self, request: MockupRequest, device_type: DeviceType) -> ContentElements:
        """Generate content elements for a specific device type."""
        try:
            # Generate header content
            header = self._generate_header_content(request, device_type)
            
            # Generate hero content
            hero = self._generate_hero_content(request, device_type)
            
            # Generate main content
            main = self._generate_main_content(request, device_type)
            
            # Generate footer content
            footer = self._generate_footer_content(request, device_type)
            
            # Generate navigation content
            navigation = self._generate_navigation_content(request, device_type)
            
            return ContentElements(
                header=header,
                hero=hero,
                main=main,
                footer=footer,
                navigation=navigation
            )
            
        except Exception as e:
            logger.error(f"Error generating content elements: {str(e)}")
            return self._create_default_content()

    def _generate_header_content(self, request: MockupRequest, device_type: DeviceType) -> List[ContentElement]:
        """Generate header content elements."""
        elements = []
        
        # Logo
        elements.append(ContentElement(
            type="logo",
            content={
                "image": request.branding.get('logo', 'default-logo.png'),
                "alt": request.project_name
            },
            style={
                "max-height": "40px",
                "margin": "1rem"
            },
            position={
                "left": "0",
                "top": "50%",
                "transform": "translateY(-50%)"
            },
            responsive_behavior={
                "mobile": {"max-height": "30px"}
            }
        ))
        
        # Navigation menu
        if device_type == DeviceType.DESKTOP:
            elements.append(ContentElement(
                type="menu",
                content={
                    "items": [
                        {"text": "Home", "link": "#"},
                        {"text": "Features", "link": "#features"},
                        {"text": "About", "link": "#about"},
                        {"text": "Contact", "link": "#contact"}
                    ]
                },
                style={
                    "display": "flex",
                    "gap": "2rem"
                },
                position={
                    "right": "0",
                    "top": "50%",
                    "transform": "translateY(-50%)"
                },
                responsive_behavior={
                    "mobile": {"display": "none"}
                }
            ))
        else:
            elements.append(ContentElement(
                type="menu-button",
                content={
                    "icon": "menu",
                    "aria-label": "Open menu"
                },
                style={
                    "padding": "0.5rem"
                },
                position={
                    "right": "1rem",
                    "top": "50%",
                    "transform": "translateY(-50%)"
                },
                responsive_behavior={}
            ))
        
        return elements

    def _generate_hero_content(self, request: MockupRequest, device_type: DeviceType) -> List[ContentElement]:
        """Generate hero content elements."""
        elements = []
        
        # Headline
        elements.append(ContentElement(
            type="heading",
            content={
                "text": request.content_requirements.get('headline', 'Welcome to ' + request.project_name),
                "level": 1
            },
            style={
                "font-size": "3rem" if device_type == DeviceType.DESKTOP else "2rem",
                "text-align": "center",
                "margin-bottom": "1rem"
            },
            position={
                "center": True,
                "top": "30%"
            },
            responsive_behavior={
                "mobile": {
                    "font-size": "2rem",
                    "padding": "0 1rem"
                }
            }
        ))
        
        # Subheadline
        elements.append(ContentElement(
            type="text",
            content={
                "text": request.content_requirements.get('subheadline', 'Your compelling subheadline here')
            },
            style={
                "font-size": "1.5rem",
                "text-align": "center",
                "margin-bottom": "2rem"
            },
            position={
                "center": True,
                "top": "45%"
            },
            responsive_behavior={
                "mobile": {
                    "font-size": "1.25rem",
                    "padding": "0 1rem"
                }
            }
        ))
        
        # Call to action button
        elements.append(ContentElement(
            type="button",
            content={
                "text": request.content_requirements.get('cta_text', 'Get Started'),
                "link": "#"
            },
            style={
                "padding": "1rem 2rem",
                "font-size": "1.25rem",
                "border-radius": "0.5rem"
            },
            position={
                "center": True,
                "top": "60%"
            },
            responsive_behavior={
                "mobile": {
                    "padding": "0.75rem 1.5rem",
                    "font-size": "1rem"
                }
            }
        ))
        
        return elements

    def _generate_main_content(self, request: MockupRequest, device_type: DeviceType) -> List[ContentElement]:
        """Generate main content elements."""
        elements = []
        
        # Features section
        features = request.content_requirements.get('features', [
            {'title': 'Feature 1', 'description': 'Description 1'},
            {'title': 'Feature 2', 'description': 'Description 2'},
            {'title': 'Feature 3', 'description': 'Description 3'}
        ])
        
        for i, feature in enumerate(features):
            elements.append(ContentElement(
                type="feature",
                content={
                    "title": feature['title'],
                    "description": feature['description'],
                    "icon": f"feature-{i+1}"
                },
                style={
                    "text-align": "center",
                    "padding": "2rem",
                    "flex": "1"
                },
                position={
                    "grid-column": f"span {12 // len(features)}"
                },
                responsive_behavior={
                    "mobile": {
                        "grid-column": "span 12"
                    }
                }
            ))
        
        return elements

    def _generate_footer_content(self, request: MockupRequest, device_type: DeviceType) -> List[ContentElement]:
        """Generate footer content elements."""
        elements = []
        
        # Copyright
        elements.append(ContentElement(
            type="text",
            content={
                "text": f"© {request.project_name} {2024}. All rights reserved."
            },
            style={
                "text-align": "center",
                "padding": "1rem"
            },
            position={
                "bottom": "0",
                "center": True
            },
            responsive_behavior={}
        ))
        
        # Social links
        social_links = [
            {"platform": "facebook", "url": "#"},
            {"platform": "twitter", "url": "#"},
            {"platform": "instagram", "url": "#"}
        ]
        
        elements.append(ContentElement(
            type="social-links",
            content={
                "links": social_links
            },
            style={
                "display": "flex",
                "gap": "1rem",
                "justify-content": "center",
                "padding": "1rem"
            },
            position={
                "bottom": "40px",
                "center": True
            },
            responsive_behavior={}
        ))
        
        return elements

    def _generate_navigation_content(self, request: MockupRequest, device_type: DeviceType) -> List[ContentElement]:
        """Generate navigation content elements."""
        nav_items = request.content_requirements.get('nav_items', [
            {"text": "Home", "link": "#"},
            {"text": "Features", "link": "#features"},
            {"text": "About", "link": "#about"},
            {"text": "Contact", "link": "#contact"}
        ])
        
        elements = []
        
        for item in nav_items:
            elements.append(ContentElement(
                type="nav-item",
                content={
                    "text": item["text"],
                    "link": item["link"]
                },
                style={
                    "padding": "0.5rem 1rem",
                    "text-decoration": "none"
                },
                position={},
                responsive_behavior={
                    "mobile": {
                        "padding": "1rem",
                        "border-bottom": "1px solid #eee"
                    }
                }
            ))
        
        return elements

    def _create_default_content(self) -> ContentElements:
        """Create default content elements in case of errors."""
        default_element = ContentElement(
            type="text",
            content={"text": "Default content"},
            style={},
            position={},
            responsive_behavior={}
        )
        
        return ContentElements(
            header=[default_element],
            hero=[default_element],
            main=[default_element],
            footer=[default_element],
            navigation=[default_element]
        ) 