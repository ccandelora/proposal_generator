"""Tests for design agent."""
import pytest
from unittest.mock import Mock, patch
from src.proposal_generator.components.mockup_generator.agents.design_agent import DesignAgent
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    MockupRequest,
    LayoutType,
    DeviceType,
    DesignElements,
    ColorScheme,
    Typography,
    MockupLayout,
    Section,
    ElementType
)

@pytest.fixture
def sample_request():
    """Sample mockup request."""
    return MockupRequest(
        project_name="Test Project",
        layout_type=LayoutType.LANDING,
        device_types=[DeviceType.DESKTOP],
        requirements=["modern", "minimalist"],
        branding={
            'primary_color': '#007bff',
            'secondary_color': '#6c757d',
            'logo': 'logo.png'
        },
        target_audience="Enterprise",
        style_preferences={
            'color_scheme': 'light',
            'typography': 'modern',
            'spacing': 'comfortable'
        },
        content_requirements={}
    )

@pytest.fixture
def sample_layout():
    """Sample mockup layout."""
    return MockupLayout(
        sections=[
            Section(
                type=ElementType.HEADER,
                width="100%",
                height="auto",
                position={},
                content={},
                style={}
            ),
            Section(
                type=ElementType.HERO,
                width="100%",
                height="500px",
                position={},
                content={},
                style={}
            )
        ],
        grid={"columns": 12},
        responsive_rules={},
        spacing={"gap": "1rem"},
        breakpoints={"mobile": 320, "tablet": 768, "desktop": 1024}
    )

@pytest.fixture
def design_agent():
    """Design agent instance."""
    return DesignAgent()

def test_design_agent_initialization(design_agent):
    """Test DesignAgent initialization."""
    assert isinstance(design_agent, DesignAgent)

def test_create_design_elements(design_agent, sample_request, sample_layout):
    """Test creating design elements."""
    design = design_agent.create_design(sample_request, sample_layout)
    
    assert isinstance(design, DesignElements)
    assert isinstance(design.colors, ColorScheme)
    assert isinstance(design.typography, Typography)
    assert design.spacing is not None
    assert design.shadows is not None
    assert design.borders is not None
    assert design.animations is not None
    assert design.icons is not None

def test_color_scheme_generation(design_agent, sample_request, sample_layout):
    """Test color scheme generation."""
    design = design_agent.create_design(sample_request, sample_layout)
    
    assert design.colors.primary == sample_request.branding['primary_color']
    assert design.colors.secondary == sample_request.branding['secondary_color']
    assert all(color.startswith('#') for color in [
        design.colors.accent,
        design.colors.background,
        design.colors.text,
        design.colors.links
    ])

def test_typography_generation(design_agent, sample_request, sample_layout):
    """Test typography generation."""
    design = design_agent.create_design(sample_request, sample_layout)
    
    assert design.typography.headings is not None
    assert design.typography.body is not None
    assert design.typography.special is not None
    assert isinstance(design.typography.font_pairs, list)
    assert len(design.typography.font_pairs) > 0

def test_design_with_minimalist_style(design_agent, sample_request, sample_layout):
    """Test design generation with minimalist style."""
    sample_request.style_preferences['style'] = 'minimalist'
    design = design_agent.create_design(sample_request, sample_layout)
    
    assert len(design.shadows) <= 2  # Minimalist designs use fewer shadows
    assert len(design.borders) <= 2  # Minimalist designs use fewer border styles
    assert len(design.animations) <= 2  # Minimalist designs use fewer animations

def test_design_with_modern_style(design_agent, sample_request, sample_layout):
    """Test design generation with modern style."""
    sample_request.style_preferences['style'] = 'modern'
    design = design_agent.create_design(sample_request, sample_layout)
    
    assert len(design.shadows) >= 2  # Modern designs often use more shadows
    assert 'gradient' in str(design.borders.values())  # Modern designs often use gradients
    assert len(design.animations) >= 2  # Modern designs use more animations

def test_design_with_dark_mode(design_agent, sample_request, sample_layout):
    """Test design generation with dark mode."""
    sample_request.style_preferences['color_scheme'] = 'dark'
    design = design_agent.create_design(sample_request, sample_layout)
    
    # Convert hex to RGB and check brightness
    def hex_to_brightness(hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r + g + b) / 3
    
    assert hex_to_brightness(design.colors.background) < 128  # Dark background
    assert hex_to_brightness(design.colors.text) > 128  # Light text

def test_responsive_design_elements(design_agent, sample_request, sample_layout):
    """Test responsive design elements generation."""
    design = design_agent.create_design(sample_request, sample_layout)
    
    # Check if typography includes responsive sizes
    heading_styles = str(design.typography.headings)
    assert 'rem' in heading_styles or 'em' in heading_styles
    
    # Check if spacing uses relative units
    assert any('rem' in str(value) or 'em' in str(value) 
              for value in design.spacing.values())

def test_design_with_accessibility_requirements(design_agent, sample_request, sample_layout):
    """Test design generation with accessibility requirements."""
    sample_request.requirements.append('accessibility')
    design = design_agent.create_design(sample_request, sample_layout)
    
    # Function to calculate contrast ratio
    def get_contrast_ratio(hex1, hex2):
        def hex_to_luminance(hex_color):
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = r / 255
            g = g / 255
            b = b / 255
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = hex_to_luminance(hex1)
        l2 = hex_to_luminance(hex2)
        
        if l1 > l2:
            return (l1 + 0.05) / (l2 + 0.05)
        return (l2 + 0.05) / (l1 + 0.05)
    
    # Check contrast ratio between text and background
    contrast_ratio = get_contrast_ratio(design.colors.text, design.colors.background)
    assert contrast_ratio >= 4.5  # WCAG AA standard for normal text

def test_invalid_style_preference(design_agent, sample_request, sample_layout):
    """Test handling of invalid style preference."""
    sample_request.style_preferences['style'] = 'invalid_style'
    design = design_agent.create_design(sample_request, sample_layout)
    
    # Should fall back to default style but still create valid design
    assert isinstance(design, DesignElements)
    assert all(required_attr is not None for required_attr in [
        design.colors,
        design.typography,
        design.spacing,
        design.shadows,
        design.borders,
        design.animations,
        design.icons
    ])

def test_brand_color_validation(design_agent, sample_request, sample_layout):
    """Test validation of brand colors."""
    sample_request.branding['primary_color'] = 'invalid_color'
    
    with pytest.raises(ValueError):
        design_agent.create_design(sample_request, sample_layout) 