"""Tests for mockup generator models."""
import pytest
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    LayoutType,
    DeviceType,
    ElementType,
    MockupRequest,
    Section,
    MockupLayout,
    ColorScheme,
    Typography,
    DesignElements,
    ContentElement,
    ContentElements,
    DeviceMockup,
    GeneratedMockup
)

@pytest.fixture
def sample_branding():
    """Sample branding data."""
    return {
        'primary_color': '#007bff',
        'secondary_color': '#6c757d',
        'accent_color': '#ff9900',
        'logo': 'logo.png',
        'favicon': 'favicon.ico'
    }

@pytest.fixture
def sample_style_preferences():
    """Sample style preferences."""
    return {
        'heading_font': 'Roboto',
        'body_font': 'Open Sans',
        'special_font': 'Montserrat',
        'icon_set': 'material'
    }

@pytest.fixture
def sample_content_requirements():
    """Sample content requirements."""
    return {
        'headline': 'Welcome to Our Website',
        'subheadline': 'Your Digital Solution',
        'features': [
            {'title': 'Feature 1', 'description': 'Description 1'},
            {'title': 'Feature 2', 'description': 'Description 2'}
        ]
    }

def test_layout_type_enum():
    """Test LayoutType enumeration."""
    assert LayoutType.LANDING.value == "landing"
    assert LayoutType.PRODUCT.value == "product"
    assert LayoutType.BLOG.value == "blog"
    assert LayoutType.PORTFOLIO.value == "portfolio"
    assert LayoutType.CONTACT.value == "contact"

def test_device_type_enum():
    """Test DeviceType enumeration."""
    assert DeviceType.DESKTOP.value == "desktop"
    assert DeviceType.TABLET.value == "tablet"
    assert DeviceType.MOBILE.value == "mobile"

def test_element_type_enum():
    """Test ElementType enumeration."""
    assert ElementType.HEADER.value == "header"
    assert ElementType.HERO.value == "hero"
    assert ElementType.CONTENT.value == "content"
    assert ElementType.SIDEBAR.value == "sidebar"
    assert ElementType.FOOTER.value == "footer"

def test_mockup_request(sample_branding, sample_style_preferences, sample_content_requirements):
    """Test MockupRequest data class."""
    request = MockupRequest(
        project_name="Test Project",
        layout_type=LayoutType.LANDING,
        device_types=[DeviceType.DESKTOP, DeviceType.MOBILE],
        requirements=["responsive", "modern"],
        branding=sample_branding,
        target_audience="Enterprise",
        style_preferences=sample_style_preferences,
        content_requirements=sample_content_requirements,
        reference_designs=["ref1.png", "ref2.png"]
    )
    
    assert request.project_name == "Test Project"
    assert request.layout_type == LayoutType.LANDING
    assert len(request.device_types) == 2
    assert request.branding == sample_branding
    assert request.style_preferences == sample_style_preferences
    assert request.content_requirements == sample_content_requirements

def test_section():
    """Test Section data class."""
    section = Section(
        type=ElementType.HEADER,
        width="100%",
        height="auto",
        position={"top": "0", "left": "0"},
        content={"navigation": True},
        style={"background": "white"}
    )
    
    assert section.type == ElementType.HEADER
    assert section.width == "100%"
    assert section.height == "auto"
    assert section.position["top"] == "0"
    assert section.content["navigation"] is True
    assert section.style["background"] == "white"

def test_mockup_layout():
    """Test MockupLayout data class."""
    layout = MockupLayout(
        sections=[
            Section(
                type=ElementType.HEADER,
                width="100%",
                height="auto",
                position={},
                content={},
                style={}
            )
        ],
        grid={"columns": 12},
        responsive_rules={"stack_on_mobile": True},
        spacing={"gap": "1rem"},
        breakpoints={"mobile": 320, "desktop": 1024}
    )
    
    assert len(layout.sections) == 1
    assert layout.grid["columns"] == 12
    assert layout.responsive_rules["stack_on_mobile"] is True
    assert layout.spacing["gap"] == "1rem"
    assert layout.breakpoints["mobile"] == 320

def test_color_scheme():
    """Test ColorScheme data class."""
    colors = ColorScheme(
        primary="#007bff",
        secondary="#6c757d",
        accent="#ff9900",
        background="#ffffff",
        text="#212529",
        links="#007bff"
    )
    
    assert colors.primary == "#007bff"
    assert colors.secondary == "#6c757d"
    assert colors.accent == "#ff9900"
    assert colors.background == "#ffffff"
    assert colors.text == "#212529"
    assert colors.links == "#007bff"

def test_typography():
    """Test Typography data class."""
    typography = Typography(
        headings={
            'h1': {'font-size': '2.5rem'},
            'h2': {'font-size': '2rem'}
        },
        body={'font-size': '1rem'},
        special={'font-size': '1.25rem'},
        font_pairs=[('Arial', 'Helvetica')]
    )
    
    assert typography.headings['h1']['font-size'] == '2.5rem'
    assert typography.body['font-size'] == '1rem'
    assert typography.special['font-size'] == '1.25rem'
    assert typography.font_pairs[0] == ('Arial', 'Helvetica')

def test_design_elements():
    """Test DesignElements data class."""
    design = DesignElements(
        colors=ColorScheme(
            primary="#007bff",
            secondary="#6c757d",
            accent="#ff9900",
            background="#ffffff",
            text="#212529",
            links="#007bff"
        ),
        typography=Typography(
            headings={'h1': {}},
            body={},
            special={},
            font_pairs=[]
        ),
        spacing={'base': '1rem'},
        shadows={'default': '0 2px 4px rgba(0,0,0,0.1)'},
        borders={'default': '1px solid'},
        animations={'transition': '0.3s'},
        icons={'menu': 'menu-icon'}
    )
    
    assert design.colors.primary == "#007bff"
    assert design.spacing['base'] == '1rem'
    assert design.shadows['default'] == '0 2px 4px rgba(0,0,0,0.1)'
    assert design.borders['default'] == '1px solid'
    assert design.animations['transition'] == '0.3s'
    assert design.icons['menu'] == 'menu-icon'

def test_content_element():
    """Test ContentElement data class."""
    element = ContentElement(
        type="heading",
        content={"text": "Welcome"},
        style={"font-size": "2rem"},
        position={"top": "0"},
        responsive_behavior={"mobile": {"font-size": "1.5rem"}}
    )
    
    assert element.type == "heading"
    assert element.content["text"] == "Welcome"
    assert element.style["font-size"] == "2rem"
    assert element.position["top"] == "0"
    assert element.responsive_behavior["mobile"]["font-size"] == "1.5rem"

def test_content_elements():
    """Test ContentElements data class."""
    elements = ContentElements(
        header=[ContentElement(type="logo", content={}, style={}, position={}, responsive_behavior={})],
        hero=[ContentElement(type="heading", content={}, style={}, position={}, responsive_behavior={})],
        main=[ContentElement(type="text", content={}, style={}, position={}, responsive_behavior={})],
        footer=[ContentElement(type="copyright", content={}, style={}, position={}, responsive_behavior={})],
        navigation=[ContentElement(type="menu", content={}, style={}, position={}, responsive_behavior={})]
    )
    
    assert len(elements.header) == 1
    assert len(elements.hero) == 1
    assert len(elements.main) == 1
    assert len(elements.footer) == 1
    assert len(elements.navigation) == 1

def test_device_mockup():
    """Test DeviceMockup data class."""
    mockup = DeviceMockup(
        device_type=DeviceType.DESKTOP,
        layout=MockupLayout(
            sections=[],
            grid={},
            responsive_rules={},
            spacing={},
            breakpoints={}
        ),
        design=DesignElements(
            colors=ColorScheme(
                primary="", secondary="", accent="",
                background="", text="", links=""
            ),
            typography=Typography(
                headings={}, body={}, special={}, font_pairs=[]
            ),
            spacing={},
            shadows={},
            borders={},
            animations={},
            icons={}
        ),
        content=ContentElements(
            header=[], hero=[], main=[], footer=[], navigation=[]
        ),
        preview_image="preview.png",
        html_code="<html></html>",
        css_code="body {}"
    )
    
    assert mockup.device_type == DeviceType.DESKTOP
    assert mockup.preview_image == "preview.png"
    assert mockup.html_code == "<html></html>"
    assert mockup.css_code == "body {}"

def test_generated_mockup():
    """Test GeneratedMockup data class."""
    mockup = GeneratedMockup(
        project_name="Test Project",
        mockups={
            DeviceType.DESKTOP: DeviceMockup(
                device_type=DeviceType.DESKTOP,
                layout=MockupLayout(
                    sections=[], grid={}, responsive_rules={},
                    spacing={}, breakpoints={}
                ),
                design=DesignElements(
                    colors=ColorScheme(
                        primary="", secondary="", accent="",
                        background="", text="", links=""
                    ),
                    typography=Typography(
                        headings={}, body={}, special={}, font_pairs=[]
                    ),
                    spacing={}, shadows={}, borders={},
                    animations={}, icons={}
                ),
                content=ContentElements(
                    header=[], hero=[], main=[], footer=[], navigation=[]
                ),
                preview_image="",
                html_code="",
                css_code=""
            )
        },
        shared_assets={'logo': 'logo.png'},
        design_system={'colors': {}},
        metadata={'version': '1.0'},
        generation_date="2024-01-01"
    )
    
    assert mockup.project_name == "Test Project"
    assert DeviceType.DESKTOP in mockup.mockups
    assert mockup.shared_assets['logo'] == 'logo.png'
    assert mockup.generation_date == "2024-01-01" 