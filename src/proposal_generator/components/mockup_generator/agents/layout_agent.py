"""Layout agent for mockup generation."""
import logging
from typing import Dict, Any, List
from ..models.mockup_model import (
    MockupRequest,
    MockupLayout,
    Section,
    ElementType,
    DeviceType
)

logger = logging.getLogger(__name__)

class LayoutAgent:
    """Agent responsible for generating mockup layouts."""

    def generate_layout(self, request: MockupRequest, device_type: DeviceType) -> MockupLayout:
        """Generate layout for a specific device type."""
        try:
            # Generate sections based on layout type
            sections = self._generate_sections(request, device_type)
            
            # Generate grid system
            grid = self._generate_grid(device_type)
            
            # Generate responsive rules
            responsive_rules = self._generate_responsive_rules(device_type)
            
            # Generate spacing rules
            spacing = self._generate_spacing(device_type)
            
            # Generate breakpoints
            breakpoints = self._generate_breakpoints()
            
            return MockupLayout(
                sections=sections,
                grid=grid,
                responsive_rules=responsive_rules,
                spacing=spacing,
                breakpoints=breakpoints
            )
            
        except Exception as e:
            logger.error(f"Error generating layout: {str(e)}")
            return self._create_default_layout()

    def _generate_sections(self, request: MockupRequest, device_type: DeviceType) -> List[Section]:
        """Generate layout sections."""
        sections = []
        
        # Header section
        sections.append(Section(
            type=ElementType.HEADER,
            width="100%",
            height="auto",
            position={"top": "0", "left": "0"},
            content={"navigation": True, "branding": True},
            style={"fixed": True, "z-index": "1000"}
        ))
        
        # Hero section
        sections.append(Section(
            type=ElementType.HERO,
            width="100%",
            height="80vh" if device_type == DeviceType.DESKTOP else "60vh",
            position={"top": "header", "left": "0"},
            content={"headline": True, "cta": True},
            style={"background": "gradient"}
        ))
        
        # Main content section
        sections.append(Section(
            type=ElementType.CONTENT,
            width="100%",
            height="auto",
            position={"top": "hero", "left": "0"},
            content={"main": True},
            style={"padding": "2rem"}
        ))
        
        # Optional sidebar for desktop
        if device_type == DeviceType.DESKTOP:
            sections.append(Section(
                type=ElementType.SIDEBAR,
                width="25%",
                height="100%",
                position={"top": "hero", "right": "0"},
                content={"widgets": True},
                style={"padding": "1rem"}
            ))
        
        # Footer section
        sections.append(Section(
            type=ElementType.FOOTER,
            width="100%",
            height="auto",
            position={"bottom": "0", "left": "0"},
            content={"links": True, "social": True},
            style={"background": "dark"}
        ))
        
        return sections

    def _generate_grid(self, device_type: DeviceType) -> Dict[str, Any]:
        """Generate grid system."""
        if device_type == DeviceType.DESKTOP:
            return {
                "columns": 12,
                "max_width": "1200px",
                "gap": "2rem",
                "margin": "0 auto"
            }
        elif device_type == DeviceType.TABLET:
            return {
                "columns": 8,
                "max_width": "768px",
                "gap": "1.5rem",
                "margin": "0 auto"
            }
        else:  # Mobile
            return {
                "columns": 4,
                "max_width": "100%",
                "gap": "1rem",
                "margin": "0"
            }

    def _generate_responsive_rules(self, device_type: DeviceType) -> Dict[str, Any]:
        """Generate responsive behavior rules."""
        return {
            "stack_on_mobile": True,
            "hide_sidebar_on_mobile": True,
            "collapse_menu_on_mobile": True,
            "adjust_font_sizes": True,
            "scale_images": True,
            "maintain_spacing_ratio": True
        }

    def _generate_spacing(self, device_type: DeviceType) -> Dict[str, Any]:
        """Generate spacing rules."""
        base_unit = "1rem"
        if device_type == DeviceType.DESKTOP:
            multiplier = 1
        elif device_type == DeviceType.TABLET:
            multiplier = 0.875
        else:  # Mobile
            multiplier = 0.75
            
        return {
            "section_gap": f"{1.5 * multiplier}rem",
            "content_padding": f"{2 * multiplier}rem",
            "element_margin": f"{1 * multiplier}rem",
            "grid_gap": f"{1.5 * multiplier}rem"
        }

    def _generate_breakpoints(self) -> Dict[str, int]:
        """Generate responsive breakpoints."""
        return {
            "mobile": 320,
            "tablet": 768,
            "desktop": 1024,
            "large": 1200,
            "xlarge": 1440
        }

    def _create_default_layout(self) -> MockupLayout:
        """Create a default layout in case of errors."""
        return MockupLayout(
            sections=[
                Section(
                    type=ElementType.HEADER,
                    width="100%",
                    height="auto",
                    position={"top": "0", "left": "0"},
                    content={},
                    style={}
                ),
                Section(
                    type=ElementType.CONTENT,
                    width="100%",
                    height="auto",
                    position={"top": "header", "left": "0"},
                    content={},
                    style={}
                ),
                Section(
                    type=ElementType.FOOTER,
                    width="100%",
                    height="auto",
                    position={"bottom": "0", "left": "0"},
                    content={},
                    style={}
                )
            ],
            grid={"columns": 12, "max_width": "1200px"},
            responsive_rules={},
            spacing={},
            breakpoints={"mobile": 320, "desktop": 1024}
        ) 