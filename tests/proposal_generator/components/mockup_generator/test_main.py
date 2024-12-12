"""Tests for main MockupGenerator class."""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.proposal_generator.components.mockup_generator.main import MockupGenerator
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    MockupRequest,
    LayoutType,
    DeviceType,
    GeneratedMockup,
    DeviceMockup,
    MockupLayout,
    DesignElements,
    ContentElements
)

@pytest.fixture
def sample_request():
    """Sample mockup request."""
    return MockupRequest(
        project_name="Test Project",
        layout_type=LayoutType.LANDING,
        device_types=[DeviceType.DESKTOP, DeviceType.MOBILE],
        requirements=["modern", "responsive"],
        branding={
            'primary_color': '#007bff',
            'secondary_color': '#6c757d',
            'company_name': 'Test Company',
            'tagline': 'Making the world better'
        },
        target_audience="Enterprise",
        style_preferences={
            'color_scheme': 'light',
            'typography': 'modern',
            'spacing': 'comfortable'
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
def mockup_generator():
    """MockupGenerator instance."""
    return MockupGenerator()

@pytest.fixture
def mock_layout():
    """Mock layout."""
    return Mock(spec=MockupLayout)

@pytest.fixture
def mock_design():
    """Mock design elements."""
    return Mock(spec=DesignElements)

@pytest.fixture
def mock_content():
    """Mock content elements."""
    return Mock(spec=ContentElements)

@patch('src.proposal_generator.components.mockup_generator.agents.layout_agent.LayoutAgent')
@patch('src.proposal_generator.components.mockup_generator.agents.design_agent.DesignAgent')
@patch('src.proposal_generator.components.mockup_generator.agents.content_agent.ContentAgent')
@patch('src.proposal_generator.components.mockup_generator.utils.preview_generator.PreviewGenerator')
def test_generate_mockup(
    mock_preview_gen,
    mock_content_agent,
    mock_design_agent,
    mock_layout_agent,
    mockup_generator,
    sample_request,
    mock_layout,
    mock_design,
    mock_content
):
    """Test mockup generation process."""
    # Setup mock returns
    mock_layout_agent.return_value.create_layout.return_value = mock_layout
    mock_design_agent.return_value.create_design.return_value = mock_design
    mock_content_agent.return_value.create_content.return_value = mock_content
    mock_preview_gen.return_value.generate_preview.return_value = "preview.png"
    
    # Generate mockup
    mockup = mockup_generator.generate_mockup(sample_request)
    
    # Verify result
    assert isinstance(mockup, GeneratedMockup)
    assert mockup.project_name == sample_request.project_name
    assert all(device_type in mockup.mockups for device_type in sample_request.device_types)
    assert mockup.shared_assets is not None
    assert mockup.design_system is not None
    assert mockup.metadata is not None
    assert mockup.generation_date is not None

def test_generate_mockup_for_all_devices(mockup_generator, sample_request):
    """Test mockup generation for all device types."""
    sample_request.device_types = [
        DeviceType.DESKTOP,
        DeviceType.TABLET,
        DeviceType.MOBILE
    ]
    
    mockup = mockup_generator.generate_mockup(sample_request)
    
    assert len(mockup.mockups) == 3
    assert all(isinstance(mockup.mockups[device], DeviceMockup) 
              for device in sample_request.device_types)

@patch('src.proposal_generator.components.mockup_generator.utils.preview_generator.PreviewGenerator')
def test_preview_generation_for_desktop(mock_preview_gen, mockup_generator, sample_request):
    """Test preview generation for desktop device."""
    mock_preview_gen.return_value.generate_preview.return_value = "desktop_preview.png"
    
    mockup = mockup_generator.generate_mockup(sample_request)
    desktop_mockup = mockup.mockups[DeviceType.DESKTOP]
    
    # Verify preview generation call
    preview_call = mock_preview_gen.return_value.generate_preview.call_args_list[0]
    assert preview_call.kwargs['width'] == 1920
    assert preview_call.kwargs['height'] == 1080
    assert preview_call.kwargs['full_page'] is True
    assert desktop_mockup.preview_image == "desktop_preview.png"

@patch('src.proposal_generator.components.mockup_generator.utils.preview_generator.PreviewGenerator')
def test_preview_generation_for_mobile(mock_preview_gen, mockup_generator, sample_request):
    """Test preview generation for mobile device."""
    mock_preview_gen.return_value.generate_preview.return_value = "mobile_preview.png"
    
    mockup = mockup_generator.generate_mockup(sample_request)
    mobile_mockup = mockup.mockups[DeviceType.MOBILE]
    
    # Verify preview generation call
    preview_call = mock_preview_gen.return_value.generate_preview.call_args_list[1]
    assert preview_call.kwargs['width'] == 375
    assert preview_call.kwargs['height'] == 812
    assert preview_call.kwargs['full_page'] is False
    assert mobile_mockup.preview_image == "mobile_preview.png"

@patch('src.proposal_generator.components.mockup_generator.utils.preview_generator.PreviewGenerator')
def test_preview_generation_error_handling(mock_preview_gen, mockup_generator, sample_request):
    """Test error handling in preview generation."""
    # Setup preview generator to fail
    mock_preview_gen.return_value.generate_preview.return_value = None
    
    mockup = mockup_generator.generate_mockup(sample_request)
    desktop_mockup = mockup.mockups[DeviceType.DESKTOP]
    
    # Verify fallback behavior
    assert desktop_mockup.preview_image.endswith('_preview.png')

def test_generate_mockup_error_handling(mockup_generator):
    """Test error handling in mockup generation."""
    # Test with invalid layout type
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
        mockup_generator.generate_mockup(request)

def test_generate_mockup_shared_assets(mockup_generator, sample_request):
    """Test shared assets in mockup generation."""
    mockup = mockup_generator.generate_mockup(sample_request)
    
    # Check if shared assets are properly generated
    assert 'logo' in mockup.shared_assets
    assert 'icons' in mockup.shared_assets
    assert 'fonts' in mockup.shared_assets

def test_generate_mockup_design_system(mockup_generator, sample_request):
    """Test design system in mockup generation."""
    mockup = mockup_generator.generate_mockup(sample_request)
    
    # Check if design system contains all required elements
    assert 'colors' in mockup.design_system
    assert 'typography' in mockup.design_system
    assert 'spacing' in mockup.design_system
    assert 'components' in mockup.design_system

@patch('src.proposal_generator.components.mockup_generator.agents.layout_agent.LayoutAgent')
def test_generate_mockup_layout_error(mock_layout_agent, mockup_generator, sample_request):
    """Test handling of layout generation error."""
    mock_layout_agent.return_value.create_layout.side_effect = Exception("Layout generation failed")
    
    with pytest.raises(Exception) as exc_info:
        mockup_generator.generate_mockup(sample_request)
    
    assert "Layout generation failed" in str(exc_info.value)

def test_output_directory_creation(tmp_path):
    """Test output directory creation."""
    # Create generator with custom output path
    generator = MockupGenerator()
    generator.output_dir = tmp_path / 'mockups'
    
    # Verify directory was created
    assert generator.output_dir.exists()
    assert generator.output_dir.is_dir() 