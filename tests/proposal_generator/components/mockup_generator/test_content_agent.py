"""Tests for content agent."""
import pytest
from unittest.mock import Mock, patch
from src.proposal_generator.components.mockup_generator.agents.content_agent import ContentAgent
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    MockupRequest,
    LayoutType,
    DeviceType,
    ContentElements,
    ContentElement,
    MockupLayout,
    Section,
    ElementType,
    DesignElements,
    ColorScheme,
    Typography
)

@pytest.fixture
def sample_request():
    """Sample mockup request."""
    return MockupRequest(
        project_name="Test Project",
        layout_type=LayoutType.LANDING,
        device_types=[DeviceType.DESKTOP],
        requirements=["modern", "engaging"],
        branding={
            'primary_color': '#007bff',
            'company_name': 'Test Company',
            'tagline': 'Making the world better'
        },
        target_audience="Enterprise",
        style_preferences={
            'tone': 'professional',
            'writing_style': 'concise'
        },
        content_requirements={
            'sections': ['hero', 'features', 'about'],
            'key_messages': [
                'Industry leading solution',
                'Enterprise grade security',
                '24/7 support'
            ]
        }
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
            ),
            Section(
                type=ElementType.CONTENT,
                width="100%",
                height="auto",
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
            headings={'h1': {'font-size': '2.5rem'}},
            body={'font-size': '1rem'},
            special={'font-size': '1.25rem'},
            font_pairs=[('Arial', 'Helvetica')]
        ),
        spacing={'base': '1rem'},
        shadows={'default': '0 2px 4px rgba(0,0,0,0.1)'},
        borders={'default': '1px solid'},
        animations={'transition': '0.3s'},
        icons={'menu': 'menu-icon'}
    )

@pytest.fixture
def content_agent():
    """Content agent instance."""
    return ContentAgent()

def test_content_agent_initialization(content_agent):
    """Test ContentAgent initialization."""
    assert isinstance(content_agent, ContentAgent)

def test_create_content_elements(content_agent, sample_request, sample_layout, sample_design):
    """Test creating content elements."""
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    assert isinstance(content, ContentElements)
    assert len(content.header) > 0
    assert len(content.hero) > 0
    assert len(content.main) > 0
    assert len(content.footer) > 0
    assert len(content.navigation) > 0

def test_header_content_generation(content_agent, sample_request, sample_layout, sample_design):
    """Test header content generation."""
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Check if company name and navigation are in header
    header_content = str([elem.content for elem in content.header])
    assert sample_request.branding['company_name'] in header_content
    assert 'navigation' in header_content.lower()

def test_hero_content_generation(content_agent, sample_request, sample_layout, sample_design):
    """Test hero content generation."""
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Check if tagline and call-to-action are in hero
    hero_content = str([elem.content for elem in content.hero])
    assert sample_request.branding['tagline'] in hero_content
    assert any('cta' in str(elem.type).lower() for elem in content.hero)

def test_main_content_generation(content_agent, sample_request, sample_layout, sample_design):
    """Test main content generation."""
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Check if key messages are included in main content
    main_content = str([elem.content for elem in content.main])
    for message in sample_request.content_requirements['key_messages']:
        assert message in main_content

def test_responsive_content_behavior(content_agent, sample_request, sample_layout, sample_design):
    """Test responsive content behavior."""
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Check if content elements have responsive behavior
    for section in [content.header, content.hero, content.main, content.footer]:
        for element in section:
            assert element.responsive_behavior is not None
            assert 'mobile' in element.responsive_behavior

def test_content_with_different_layout_types(content_agent, sample_request, sample_layout, sample_design):
    """Test content generation for different layout types."""
    # Test product layout
    sample_request.layout_type = LayoutType.PRODUCT
    product_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    assert any('product' in str(elem.type).lower() for elem in product_content.main)
    
    # Test blog layout
    sample_request.layout_type = LayoutType.BLOG
    blog_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    assert any('post' in str(elem.type).lower() for elem in blog_content.main)
    
    # Test portfolio layout
    sample_request.layout_type = LayoutType.PORTFOLIO
    portfolio_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    assert any('project' in str(elem.type).lower() for elem in portfolio_content.main)

def test_content_style_adaptation(content_agent, sample_request, sample_layout, sample_design):
    """Test content adaptation to different styles."""
    # Test professional tone
    sample_request.style_preferences['tone'] = 'professional'
    professional_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    prof_content_str = str([elem.content for elem in professional_content.main])
    assert any(word in prof_content_str.lower() for word in ['solution', 'enterprise', 'professional'])
    
    # Test casual tone
    sample_request.style_preferences['tone'] = 'casual'
    casual_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    casual_content_str = str([elem.content for elem in casual_content.main])
    assert any(word in casual_content_str.lower() for word in ['get started', 'join', 'try'])

def test_content_target_audience_adaptation(content_agent, sample_request, sample_layout, sample_design):
    """Test content adaptation to different target audiences."""
    # Test enterprise audience
    sample_request.target_audience = "Enterprise"
    enterprise_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    ent_content_str = str([elem.content for elem in enterprise_content.main])
    assert any(word in ent_content_str.lower() for word in ['enterprise', 'business', 'solution'])
    
    # Test consumer audience
    sample_request.target_audience = "Consumer"
    consumer_content = content_agent.create_content(sample_request, sample_layout, sample_design)
    cons_content_str = str([elem.content for elem in consumer_content.main])
    assert any(word in cons_content_str.lower() for word in ['personal', 'home', 'lifestyle'])

def test_content_with_missing_branding(content_agent, sample_request, sample_layout, sample_design):
    """Test content generation with missing branding information."""
    sample_request.branding = {}
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Should still generate valid content with defaults
    assert isinstance(content, ContentElements)
    assert all(len(section) > 0 for section in [
        content.header,
        content.hero,
        content.main,
        content.footer,
        content.navigation
    ])

def test_content_accessibility(content_agent, sample_request, sample_layout, sample_design):
    """Test content accessibility features."""
    sample_request.requirements.append('accessibility')
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Check for alt text in images and aria labels
    for section in [content.header, content.hero, content.main, content.footer]:
        for element in section:
            if 'image' in str(element.type).lower():
                assert 'alt' in str(element.content)
            if 'button' in str(element.type).lower():
                assert 'aria-label' in str(element.content)

def test_invalid_content_requirements(content_agent, sample_request, sample_layout, sample_design):
    """Test handling of invalid content requirements."""
    sample_request.content_requirements['sections'] = ['invalid_section']
    content = content_agent.create_content(sample_request, sample_layout, sample_design)
    
    # Should still generate valid content with default sections
    assert isinstance(content, ContentElements)
    assert all(len(section) > 0 for section in [
        content.header,
        content.hero,
        content.main,
        content.footer,
        content.navigation
    ]) 