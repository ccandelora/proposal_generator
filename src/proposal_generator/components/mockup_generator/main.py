"""Main mockup generator module."""
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from .models.mockup_model import (
    MockupRequest,
    GeneratedMockup,
    DeviceMockup,
    DeviceType
)
from .agents.layout_agent import LayoutAgent
from .agents.design_agent import DesignAgent
from .agents.content_agent import ContentAgent
from .utils.html_generator import HTMLGenerator
from .utils.css_generator import CSSGenerator
from .utils.preview_generator import PreviewGenerator

logger = logging.getLogger(__name__)

class MockupGenerator:
    """Generator for website mockups and design proposals."""

    def __init__(self):
        """Initialize the MockupGenerator."""
        self.layout_agent = LayoutAgent()
        self.design_agent = DesignAgent()
        self.content_agent = ContentAgent()
        self.html_generator = HTMLGenerator()
        self.css_generator = CSSGenerator()
        self.preview_generator = PreviewGenerator()
        self.output_dir = Path(__file__).parent.parent.parent / 'mockups'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_mockup(self, request: MockupRequest) -> GeneratedMockup:
        """
        Generate a complete mockup based on the request.
        
        Args:
            request: MockupRequest containing all requirements
            
        Returns:
            GeneratedMockup containing all generated assets
        """
        try:
            mockups = {}
            shared_assets = {}
            design_system = {}
            
            # Generate mockups for each device type
            for device_type in request.device_types:
                mockups[device_type] = self._generate_device_mockup(request, device_type)
            
            # Collect shared assets
            shared_assets = self._collect_shared_assets(request)
            
            # Create design system documentation
            design_system = self._create_design_system(request)
            
            return GeneratedMockup(
                project_name=request.project_name,
                mockups=mockups,
                shared_assets=shared_assets,
                design_system=design_system,
                metadata=self._create_metadata(request),
                generation_date=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating mockup: {str(e)}")
            raise

    def _generate_device_mockup(self, request: MockupRequest, device_type: DeviceType) -> DeviceMockup:
        """Generate mockup for a specific device type."""
        try:
            # Generate layout structure
            layout = self.layout_agent.create_layout(request, device_type)
            
            # Generate design elements
            design = self.design_agent.create_design(request, layout)
            
            # Generate content elements
            content = self.content_agent.create_content(request, layout, design)
            
            # Generate HTML code
            html_code = self.html_generator.generate_html(content, device_type)
            
            # Generate CSS code
            css_code = self.css_generator.generate_css(design, device_type)
            
            # Generate preview image
            preview_image = self._generate_preview_image(
                request.project_name,
                device_type,
                html_code,
                css_code
            )
            
            return DeviceMockup(
                device_type=device_type,
                layout=layout,
                design=design,
                content=content,
                preview_image=preview_image,
                html_code=html_code,
                css_code=css_code
            )
            
        except Exception as e:
            logger.error(f"Error generating device mockup: {str(e)}")
            raise

    def _generate_preview_image(
        self,
        project_name: str,
        device_type: DeviceType,
        html_code: str,
        css_code: str
    ) -> str:
        """Generate preview image for the mockup."""
        # Determine dimensions based on device type
        dimensions = {
            DeviceType.DESKTOP: (1920, 1080),
            DeviceType.TABLET: (1024, 768),
            DeviceType.MOBILE: (375, 812)
        }
        width, height = dimensions[device_type]
        
        # Create output path
        filename = f"{project_name.lower().replace(' ', '_')}_{device_type.value}_preview.png"
        output_path = self.output_dir / filename
        
        # Generate preview
        preview_path = self.preview_generator.generate_preview(
            html_content=html_code,
            css_content=css_code,
            output_path=output_path,
            width=width,
            height=height,
            device_pixel_ratio=2,  # Use 2x for retina displays
            wait_for_network=True,
            wait_for_animations=True,
            full_page=device_type == DeviceType.DESKTOP  # Full page for desktop only
        )
        
        if not preview_path:
            logger.warning(f"Failed to generate preview for {device_type.value}")
            return str(output_path)  # Return expected path even if generation failed
        
        return preview_path

    def _collect_shared_assets(self, request: MockupRequest) -> Dict[str, Any]:
        """Collect shared assets like images, fonts, and icons."""
        return {
            'logo': request.branding.get('logo', ''),
            'icons': request.branding.get('icons', {}),
            'fonts': request.style_preferences.get('fonts', []),
            'images': request.content_requirements.get('images', [])
        }

    def _create_design_system(self, request: MockupRequest) -> Dict[str, Any]:
        """Create design system documentation."""
        return {
            'colors': {
                'primary': request.branding.get('primary_color', ''),
                'secondary': request.branding.get('secondary_color', ''),
                'accent': request.branding.get('accent_color', '')
            },
            'typography': request.style_preferences.get('typography', {}),
            'spacing': request.style_preferences.get('spacing', {}),
            'components': {
                'buttons': {
                    'primary': {'background': 'var(--color-primary)', 'color': 'white'},
                    'secondary': {'background': 'var(--color-secondary)', 'color': 'white'}
                },
                'cards': {
                    'default': {'padding': 'var(--space-md)', 'border-radius': 'var(--radius-md)'}
                },
                'forms': {
                    'inputs': {'border': '1px solid var(--color-border)'},
                    'labels': {'font-weight': '500'}
                }
            }
        }

    def _create_metadata(self, request: MockupRequest) -> Dict[str, Any]:
        """Create metadata for the mockup."""
        return {
            'version': '1.0',
            'generator': 'MockupGenerator',
            'project': request.project_name,
            'target_audience': request.target_audience,
            'requirements': request.requirements,
            'device_types': [dt.value for dt in request.device_types],
            'generation_date': datetime.now().isoformat()
        }