"""Tests for preview generator."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.proposal_generator.components.mockup_generator.utils.preview_generator import PreviewGenerator

@pytest.fixture
def sample_html():
    """Sample HTML content."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Preview</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Test Heading</h1>
        <p>Test paragraph content.</p>
    </div>
</body>
</html>"""

@pytest.fixture
def sample_css():
    """Sample CSS content."""
    return """
body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

h1 {
    color: #333;
    font-size: 2rem;
}

p {
    color: #666;
    line-height: 1.5;
}"""

@pytest.fixture
def preview_generator():
    """Preview generator instance."""
    return PreviewGenerator()

@pytest.fixture
def mock_driver():
    """Mock Chrome driver."""
    driver = Mock(spec=webdriver.Chrome)
    driver.execute_script.return_value = 'complete'
    return driver

@patch('selenium.webdriver.Chrome')
def test_preview_generation(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test preview image generation."""
    # Setup mock driver
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    mock_driver.execute_script.return_value = 'complete'
    
    # Generate preview
    output_path = tmp_path / 'preview.png'
    result = preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path
    )
    
    # Verify driver configuration
    assert mock_chrome.called
    
    # Verify screenshot was taken
    assert mock_driver.save_screenshot.called
    assert mock_driver.save_screenshot.call_args[0][0] == str(output_path)
    
    # Verify cleanup
    assert mock_driver.quit.called
    assert not (tmp_path / 'temp').exists()

@patch('selenium.webdriver.Chrome')
def test_preview_generation_with_custom_size(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test preview generation with custom dimensions."""
    # Setup mock driver
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    
    # Generate preview with custom size
    output_path = tmp_path / 'preview.png'
    preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path,
        width=1024,
        height=768
    )
    
    # Verify window size was set
    chrome_options = mock_chrome.call_args[1]['options']
    assert '--window-size=1024,768' in chrome_options.arguments

@patch('selenium.webdriver.Chrome')
def test_preview_generation_with_high_dpi(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test preview generation with high DPI setting."""
    # Setup mock driver
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    
    # Generate preview with high DPI
    output_path = tmp_path / 'preview.png'
    preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path,
        device_pixel_ratio=3
    )
    
    # Verify DPI setting
    chrome_options = mock_chrome.call_args[1]['options']
    assert '--force-device-scale-factor=3' in chrome_options.arguments

@patch('selenium.webdriver.Chrome')
def test_preview_generation_full_page(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test full page preview generation."""
    # Setup mock driver
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    mock_driver.execute_script.return_value = 2000  # Mock page height
    
    # Generate full page preview
    output_path = tmp_path / 'preview.png'
    preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path,
        full_page=True
    )
    
    # Verify full page height was used
    assert mock_driver.set_window_size.called
    assert mock_driver.set_window_size.call_args[0][1] == 2000

@patch('selenium.webdriver.Chrome')
def test_preview_generation_error_handling(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test error handling in preview generation."""
    # Setup mock driver to raise exception
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    mock_driver.save_screenshot.side_effect = Exception("Screenshot failed")
    
    # Attempt to generate preview
    output_path = tmp_path / 'preview.png'
    result = preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path
    )
    
    # Verify error handling
    assert result is None
    assert mock_driver.quit.called
    assert not (tmp_path / 'temp').exists()

@patch('selenium.webdriver.Chrome')
def test_preview_generation_wait_behavior(mock_chrome, tmp_path, preview_generator, sample_html, sample_css):
    """Test wait behavior during preview generation."""
    # Setup mock driver
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver
    
    # Generate preview with wait options
    output_path = tmp_path / 'preview.png'
    preview_generator.generate_preview(
        html_content=sample_html,
        css_content=sample_css,
        output_path=output_path,
        wait_for_network=True,
        wait_for_animations=True
    )
    
    # Verify wait behavior
    assert mock_driver.execute_script.called  # Waited for readyState
    assert mock_driver.implicitly_wait.called  # Waited for animations

def test_chrome_driver_options(preview_generator):
    """Test Chrome driver options configuration."""
    options = preview_generator._get_chrome_driver(1920, 1080, 2).options
    
    # Verify essential options
    assert '--headless=new' in options.arguments
    assert '--no-sandbox' in options.arguments
    assert '--disable-dev-shm-usage' in options.arguments
    assert '--disable-gpu' in options.arguments
    
    # Verify window configuration
    assert '--window-size=1920,1080' in options.arguments
    assert '--force-device-scale-factor=2' in options.arguments
    
    # Verify additional options
    assert '--hide-scrollbars' in options.arguments
    assert '--disable-notifications' in options.arguments
    assert '--disable-popup-blocking' in options.arguments
    assert '--disable-extensions' in options.arguments 