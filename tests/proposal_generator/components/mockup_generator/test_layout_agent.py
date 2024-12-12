"""Tests for layout agent."""
import pytest
from unittest.mock import Mock, patch
from src.proposal_generator.components.mockup_generator.agents.layout_agent import LayoutAgent
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    MockupRequest,
    LayoutType,
    DeviceType,
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
        requirements=["responsive", "modern"],
        branding={
            'primary_color': '#007bff',
            'logo': 'logo.png'
        },
        target_audience="Enterprise",
        style_preferences={
            'layout_style': 'minimal',
            'spacing': 'comfortable'
        },
        content_requirements={
            'sections': ['hero', 'features', 'contact']
        }
    )

@pytest.fixture
def layout_agent():
    """Layout agent instance."""
    return LayoutAgent()

def test_layout_agent_initialization(layout_agent):
    """Test LayoutAgent initialization."""
    assert isinstance(layout_agent, LayoutAgent)

def test_create_landing_layout(layout_agent, sample_request):
    """Test creating landing page layout."""
    layout = layout_agent.create_layout(sample_request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert len(layout.sections) > 0
    assert any(section.type == ElementType.HEADER for section in layout.sections)
    assert any(section.type == ElementType.HERO for section in layout.sections)
    assert layout.grid is not None
    assert layout.responsive_rules is not None
    assert layout.spacing is not None
    assert layout.breakpoints is not None

def test_create_product_layout(layout_agent):
    """Test creating product page layout."""
    request = MockupRequest(
        project_name="Product Page",
        layout_type=LayoutType.PRODUCT,
        device_types=[DeviceType.DESKTOP],
        requirements=["e-commerce"],
        branding={},
        target_audience="Consumers",
        style_preferences={},
        content_requirements={
            'sections': ['product-gallery', 'description', 'specs']
        }
    )
    
    layout = layout_agent.create_layout(request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert len(layout.sections) > 0
    assert any(section.type == ElementType.CONTENT for section in layout.sections)
    assert layout.grid is not None

def test_create_blog_layout(layout_agent):
    """Test creating blog layout."""
    request = MockupRequest(
        project_name="Blog",
        layout_type=LayoutType.BLOG,
        device_types=[DeviceType.DESKTOP],
        requirements=["readable"],
        branding={},
        target_audience="Readers",
        style_preferences={},
        content_requirements={
            'sections': ['posts', 'sidebar']
        }
    )
    
    layout = layout_agent.create_layout(request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert len(layout.sections) > 0
    assert any(section.type == ElementType.CONTENT for section in layout.sections)
    assert any(section.type == ElementType.SIDEBAR for section in layout.sections)

def test_create_portfolio_layout(layout_agent):
    """Test creating portfolio layout."""
    request = MockupRequest(
        project_name="Portfolio",
        layout_type=LayoutType.PORTFOLIO,
        device_types=[DeviceType.DESKTOP],
        requirements=["grid-based"],
        branding={},
        target_audience="Clients",
        style_preferences={},
        content_requirements={
            'sections': ['projects', 'about']
        }
    )
    
    layout = layout_agent.create_layout(request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert len(layout.sections) > 0
    assert layout.grid is not None
    assert 'columns' in layout.grid

def test_create_contact_layout(layout_agent):
    """Test creating contact page layout."""
    request = MockupRequest(
        project_name="Contact",
        layout_type=LayoutType.CONTACT,
        device_types=[DeviceType.DESKTOP],
        requirements=["form"],
        branding={},
        target_audience="Visitors",
        style_preferences={},
        content_requirements={
            'sections': ['contact-form', 'map']
        }
    )
    
    layout = layout_agent.create_layout(request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert len(layout.sections) > 0
    assert any(section.type == ElementType.CONTENT for section in layout.sections)

def test_responsive_layout_creation(layout_agent, sample_request):
    """Test creating responsive layouts for different devices."""
    desktop_layout = layout_agent.create_layout(sample_request, DeviceType.DESKTOP)
    tablet_layout = layout_agent.create_layout(sample_request, DeviceType.TABLET)
    mobile_layout = layout_agent.create_layout(sample_request, DeviceType.MOBILE)
    
    assert desktop_layout.breakpoints["desktop"] > tablet_layout.breakpoints["tablet"]
    assert tablet_layout.breakpoints["tablet"] > mobile_layout.breakpoints["mobile"]
    
    # Check responsive rules
    assert "stack_on_mobile" in mobile_layout.responsive_rules
    assert mobile_layout.grid != desktop_layout.grid

def test_layout_with_custom_requirements(layout_agent):
    """Test layout creation with custom requirements."""
    request = MockupRequest(
        project_name="Custom",
        layout_type=LayoutType.LANDING,
        device_types=[DeviceType.DESKTOP],
        requirements=["accessibility", "dark-mode"],
        branding={},
        target_audience="All",
        style_preferences={
            'color_scheme': 'dark',
            'layout_style': 'accessible'
        },
        content_requirements={}
    )
    
    layout = layout_agent.create_layout(request, DeviceType.DESKTOP)
    
    assert isinstance(layout, MockupLayout)
    assert any('accessibility' in str(rule) for rule in layout.responsive_rules.values())

def test_invalid_layout_type(layout_agent):
    """Test handling of invalid layout type."""
    with pytest.raises(ValueError):
        request = MockupRequest(
            project_name="Invalid",
            layout_type="invalid_type",  # type: ignore
            device_types=[DeviceType.DESKTOP],
            requirements=[],
            branding={},
            target_audience="",
            style_preferences={},
            content_requirements={}
        )
        layout_agent.create_layout(request, DeviceType.DESKTOP)

def test_invalid_device_type(layout_agent, sample_request):
    """Test handling of invalid device type."""
    with pytest.raises(ValueError):
        layout_agent.create_layout(sample_request, "invalid_device")  # type: ignore 