"""Data models for mockup generation."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class LayoutType(Enum):
    """Types of layouts."""
    LANDING = "landing"
    PRODUCT = "product"
    BLOG = "blog"
    PORTFOLIO = "portfolio"
    CONTACT = "contact"

class DeviceType(Enum):
    """Types of devices."""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"

class ElementType(Enum):
    """Types of design elements."""
    HEADER = "header"
    HERO = "hero"
    CONTENT = "content"
    SIDEBAR = "sidebar"
    FOOTER = "footer"

@dataclass
class MockupRequest:
    """Request for mockup generation."""
    project_name: str
    layout_type: LayoutType
    device_types: List[DeviceType]
    requirements: List[str]
    branding: Dict[str, Any]
    target_audience: str
    style_preferences: Dict[str, Any]
    content_requirements: Dict[str, Any]
    reference_designs: Optional[List[str]] = None

@dataclass
class Section:
    """Section in a layout."""
    type: ElementType
    width: str
    height: str
    position: Dict[str, str]
    content: Dict[str, Any]
    style: Dict[str, Any]

@dataclass
class MockupLayout:
    """Layout structure for a mockup."""
    sections: List[Section]
    grid: Dict[str, Any]
    responsive_rules: Dict[str, Any]
    spacing: Dict[str, Any]
    breakpoints: Dict[str, int]

@dataclass
class ColorScheme:
    """Color scheme for design elements."""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    links: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class Typography:
    """Typography settings."""
    headings: Dict[str, Dict[str, Any]]
    body: Dict[str, Any]
    special: Dict[str, Any]
    font_pairs: List[tuple]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert tuples to lists for JSON serialization
        data['font_pairs'] = [list(pair) for pair in self.font_pairs]
        return data

@dataclass
class DesignElements:
    """Design elements for a mockup."""
    colors: ColorScheme
    typography: Typography
    spacing: Dict[str, str]
    shadows: Dict[str, str]
    borders: Dict[str, str]
    animations: Dict[str, Any]
    icons: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'colors': self.colors.to_dict(),
            'typography': self.typography.to_dict(),
            'spacing': self.spacing,
            'shadows': self.shadows,
            'borders': self.borders,
            'animations': self.animations,
            'icons': self.icons
        }

@dataclass
class ContentElement:
    """Content element in a mockup."""
    type: str
    content: Any
    style: Dict[str, Any]
    position: Dict[str, str]
    responsive_behavior: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class ContentElements:
    """Content elements for a mockup."""
    header: List[ContentElement]
    hero: List[ContentElement]
    main: List[ContentElement]
    footer: List[ContentElement]
    navigation: List[ContentElement]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'header': [element.to_dict() for element in self.header],
            'hero': [element.to_dict() for element in self.hero],
            'main': [element.to_dict() for element in self.main],
            'footer': [element.to_dict() for element in self.footer],
            'navigation': [element.to_dict() for element in self.navigation]
        }

@dataclass
class DeviceMockup:
    """Mockup for a specific device type."""
    device_type: DeviceType
    layout: MockupLayout
    design: DesignElements
    content: ContentElements
    preview_image: str
    html_code: str
    css_code: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'device_type': self.device_type.value,
            'layout': self.layout.to_dict(),
            'design': self.design.to_dict(),
            'content': self.content.to_dict(),
            'preview_image': self.preview_image,
            'html_code': self.html_code,
            'css_code': self.css_code
        }

@dataclass
class GeneratedMockup:
    """Complete generated mockup."""
    project_name: str
    mockups: Dict[DeviceType, DeviceMockup]
    shared_assets: Dict[str, Any]
    design_system: Dict[str, Any]
    metadata: Dict[str, Any]
    generation_date: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'project_name': self.project_name,
            'mockups': {device_type.value: mockup.to_dict() 
                       for device_type, mockup in self.mockups.items()},
            'shared_assets': self.shared_assets,
            'design_system': self.design_system,
            'metadata': self.metadata,
            'generation_date': self.generation_date
        } 