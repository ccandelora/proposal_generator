"""Tests for CSS generator."""
import pytest
from src.proposal_generator.components.mockup_generator.utils.css_generator import CSSGenerator
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    DesignElements,
    ColorScheme,
    Typography,
    DeviceType
)

@pytest.fixture
def sample_design():
    """Sample design elements."""
    return DesignElements(
        colors=ColorScheme(
            primary="#007bff",
            secondary="#6c757d",
            accent="#ff9900",
            background="#ffffff",
            text="#212529",
            links="#007bff"
        ),
        typography=Typography(
            headings={
                'h1': {'font-size': '2.5rem', 'font-weight': '700'},
                'h2': {'font-size': '2rem', 'font-weight': '600'},
                'h3': {'font-size': '1.75rem', 'font-weight': '600'}
            },
            body={'font-size': '1rem', 'line-height': '1.5'},
            special={'font-size': '1.25rem'},
            font_pairs=[('Arial', 'Helvetica')]
        ),
        spacing={'base': '1rem', 'gap': '2rem'},
        shadows={'default': 'box-shadow: 0 2px 4px rgba(0,0,0,0.1)'},
        borders={'default': '1px solid rgba(0,0,0,0.1)'},
        animations={'transition': '0.3s ease-in-out'},
        icons={'menu': 'menu-icon'}
    )

def test_generate_css(sample_design):
    """Test CSS generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check if all major sections are present
    assert '/* Reset styles */' in css
    assert '/* CSS Variables */' in css
    assert '/* Base styles */' in css
    assert '/* Typography */' in css
    assert '/* Layout */' in css
    assert '/* Components */' in css
    assert '/* Responsive styles */' in css
    assert '/* Utility classes */' in css
    assert '/* Animations */' in css

def test_generate_variables(sample_design):
    """Test CSS variables generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check color variables
    assert '--color-primary: #007bff;' in css
    assert '--color-secondary: #6c757d;' in css
    assert '--color-accent: #ff9900;' in css
    assert '--color-background: #ffffff;' in css
    assert '--color-text: #212529;' in css
    
    # Check spacing variables
    assert '--space-xs:' in css
    assert '--space-sm:' in css
    assert '--space-md:' in css
    assert '--space-lg:' in css
    assert '--space-xl:' in css
    
    # Check other variables
    assert '--radius-' in css
    assert '--transition-' in css

def test_generate_typography_styles(sample_design):
    """Test typography styles generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check heading styles
    assert 'font-size: 2.5rem;' in css
    assert 'font-size: 2rem;' in css
    assert 'font-size: 1.75rem;' in css
    
    # Check body styles
    assert 'font-size: 1rem;' in css
    assert 'line-height: 1.5;' in css

def test_generate_layout_styles(sample_design):
    """Test layout styles generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check container styles
    assert '.container {' in css
    assert 'max-width: 1200px;' in css
    
    # Check grid styles
    assert '.grid {' in css
    assert 'display: grid;' in css
    assert 'gap: 2rem;' in css
    
    # Check section styles
    assert 'header {' in css
    assert 'main {' in css
    assert 'footer {' in css

def test_generate_component_styles(sample_design):
    """Test component styles generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check card styles
    assert '.card {' in css
    assert 'border-radius: var(--radius-md);' in css
    
    # Check form styles
    assert '.form-field {' in css
    assert '.form-field input,' in css
    assert '.form-field textarea,' in css
    
    # Check button styles
    assert '.button {' in css
    assert 'background-color: var(--color-primary);' in css

def test_generate_responsive_styles():
    """Test responsive styles generation."""
    # Test mobile styles
    mobile_css = CSSGenerator.generate_css(sample_design, DeviceType.MOBILE)
    assert '@media (max-width: 768px)' in mobile_css
    assert 'html { font-size: 14px; }' in mobile_css
    assert 'grid-template-columns: 1fr;' in mobile_css
    
    # Test tablet styles
    tablet_css = CSSGenerator.generate_css(sample_design, DeviceType.TABLET)
    assert '@media (max-width: 1024px)' in tablet_css
    assert 'grid-template-columns: repeat(6, 1fr);' in tablet_css

def test_generate_utility_classes(sample_design):
    """Test utility classes generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check text alignment classes
    assert '.text-center' in css
    assert '.text-left' in css
    assert '.text-right' in css
    
    # Check margin classes
    assert '.mt-' in css
    assert '.mb-' in css
    
    # Check display classes
    assert '.hidden' in css
    assert '.visible' in css
    
    # Check flex classes
    assert '.flex' in css
    assert '.flex-col' in css
    assert '.items-center' in css
    assert '.justify-center' in css

def test_generate_animations(sample_design):
    """Test animations generation."""
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    # Check keyframe animations
    assert '@keyframes fadeIn' in css
    assert '@keyframes slideIn' in css
    assert '@keyframes scaleIn' in css
    
    # Check animation classes
    assert '.animate-fade-in' in css
    assert '.animate-slide-in' in css
    assert '.animate-scale-in' in css

def test_generate_dark_mode(sample_design):
    """Test dark mode styles generation."""
    # Modify colors for dark mode
    sample_design.colors = ColorScheme(
        primary="#007bff",
        secondary="#6c757d",
        accent="#ff9900",
        background="#1a1a1a",
        text="#ffffff",
        links="#66b3ff"
    )
    
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    assert '--color-background: #1a1a1a;' in css
    assert '--color-text: #ffffff;' in css

def test_generate_custom_spacing(sample_design):
    """Test custom spacing generation."""
    # Modify spacing
    sample_design.spacing = {
        'base': '1.5rem',
        'gap': '3rem',
        'section': '6rem'
    }
    
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    assert 'gap: 3rem;' in css
    assert 'padding: 6rem' in css

def test_generate_custom_shadows(sample_design):
    """Test custom shadows generation."""
    # Modify shadows
    sample_design.shadows = {
        'small': 'box-shadow: 0 1px 2px rgba(0,0,0,0.1)',
        'large': 'box-shadow: 0 4px 8px rgba(0,0,0,0.2)',
        'inset': 'box-shadow: inset 0 2px 4px rgba(0,0,0,0.1)'
    }
    
    css = CSSGenerator.generate_css(sample_design, DeviceType.DESKTOP)
    
    for shadow in sample_design.shadows.values():
        assert shadow in css 