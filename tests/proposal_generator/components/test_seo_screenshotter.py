"""Tests for the SEO Screenshotter module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from src.proposal_generator.components.seo_screenshotter.main import SEOScreenshotter
from src.proposal_generator.components.seo_screenshotter.agents.design_analyzer import DesignAnalyzerAgent
from src.proposal_generator.components.seo_screenshotter.agents.ux_capture import UXCaptureAgent
from src.proposal_generator.components.seo_screenshotter.agents.brand_analyzer import BrandAnalyzerAgent
from src.proposal_generator.components.seo_screenshotter.agents.competitive_visual import CompetitiveVisualAgent
from src.proposal_generator.components.seo_screenshotter.models.task_context import TaskContext
from src.proposal_generator.components.seo_screenshotter.utils.color_utils import normalize_color, hex_to_hsl
from src.proposal_generator.components.seo_screenshotter.utils.html_utils import extract_text_content, get_element_styles

@pytest.fixture
def mock_driver():
    """Create a mock Selenium WebDriver."""
    with patch('selenium.webdriver.Chrome') as mock:
        driver = mock.return_value
        driver.page_source = '<html><body><div class="hero">Test</div></body></html>'
        driver.get_screenshot_as_png.return_value = b'fake_screenshot'
        driver.find_elements.return_value = []
        driver.execute_script.return_value = {}
        yield driver

@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return '''
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <nav class="main-nav">
                <a href="#">Home</a>
                <a href="#">About</a>
            </nav>
            <div class="hero">
                <h1 style="color: #333;">Welcome</h1>
                <p>Test content</p>
                <a href="#" class="cta">Get Started</a>
            </div>
            <form>
                <input type="text" required>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    '''

@pytest.fixture
def task_context(mock_driver, sample_html):
    """Create a task context for testing."""
    return TaskContext(
        description="Test analysis",
        expected_output="Test results",
        screenshot=b'fake_screenshot',
        html_content=sample_html,
        driver=mock_driver
    )

@pytest.fixture
def screenshotter():
    """Create a screenshotter instance."""
    return SEOScreenshotter()

def test_screenshotter_initialization(screenshotter):
    """Test screenshotter initialization."""
    assert isinstance(screenshotter.design_analyzer, DesignAnalyzerAgent)
    assert isinstance(screenshotter.ux_capture, UXCaptureAgent)
    assert isinstance(screenshotter.brand_analyzer, BrandAnalyzerAgent)
    assert isinstance(screenshotter.competitive_visual, CompetitiveVisualAgent)

def test_analyze_website(screenshotter, mock_driver):
    """Test website analysis."""
    result = screenshotter.analyze_website("https://example.com")
    
    assert isinstance(result, dict)
    assert "url" in result
    assert "design_analysis" in result
    assert "ux_analysis" in result
    assert "brand_analysis" in result
    assert "competitive_analysis" not in result  # No competitors provided

def test_analyze_website_with_competitors(screenshotter, mock_driver):
    """Test website analysis with competitors."""
    result = screenshotter.analyze_website(
        "https://example.com",
        competitor_urls=["https://competitor1.com", "https://competitor2.com"]
    )
    
    assert isinstance(result, dict)
    assert "competitive_analysis" in result
    assert result["competitive_analysis"] is not None

def test_get_visual_recommendations(screenshotter):
    """Test visual recommendations generation."""
    analysis_results = {
        "design_analysis": {
            "colors": {"harmony_score": 0.5}
        },
        "ux_analysis": {
            "accessibility": {"aria_usage": {"total_aria_attributes": 5}}
        },
        "brand_analysis": {
            "consistency": {"brand_strength": 0.4}
        },
        "competitive_analysis": {
            "differentiation_score": 0.3
        }
    }
    
    recommendations = screenshotter.get_visual_recommendations(analysis_results)
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(rec, dict) for rec in recommendations)
    assert all("category" in rec for rec in recommendations)
    assert all("priority" in rec for rec in recommendations)
    assert all("description" in rec for rec in recommendations)

def test_generate_visual_report(screenshotter):
    """Test visual report generation."""
    analysis_results = {
        "url": "https://example.com",
        "design_analysis": {
            "colors": {
                "primary_colors": ["#333333", "#666666"],
                "harmony_type": "monochromatic",
                "harmony_score": 0.5  # Low harmony score to trigger recommendation
            },
            "typography": {
                "primary_font": "Arial",
                "font_distribution": {"Arial": 10, "Helvetica": 5}
            }
        },
        "ux_analysis": {
            "navigation": {
                "menu_structure": "hierarchical"
            },
            "accessibility": {
                "aria_usage": {"total_aria_attributes": 5},  # Low ARIA count to trigger recommendation
                "keyboard_navigation": {"focusable_elements": 20}
            }
        },
        "brand_analysis": {
            "visual_identity": {
                "logo_presence": {"logo_count": 2}
            },
            "consistency": {"brand_strength": 0.4}  # Low brand strength to trigger recommendation
        },
        "competitive_analysis": {
            "market_positioning": {
                "market_segment": "premium",
                "differentiation_score": 0.3  # Low differentiation to trigger recommendation
            }
        }
    }
    
    report = screenshotter.generate_visual_report(analysis_results)
    
    assert isinstance(report, str)
    assert "Visual Analysis Report" in report
    assert "Design Analysis" in report
    assert "User Experience Analysis" in report
    assert "Brand Analysis" in report
    assert "Competitive Analysis" in report
    assert "Recommendations" in report

def test_design_analyzer_agent(task_context):
    """Test design analyzer agent."""
    agent = DesignAnalyzerAgent()
    result = agent.analyze_design(task_context)
    
    assert isinstance(result, dict)
    assert "colors" in result
    assert "typography" in result
    assert "layout" in result

def test_ux_capture_agent(task_context):
    """Test UX capture agent."""
    agent = UXCaptureAgent()
    result = agent.analyze_ux(task_context)
    
    assert isinstance(result, dict)
    assert "navigation" in result
    assert "forms" in result
    assert "accessibility" in result
    assert "content_structure" in result

def test_brand_analyzer_agent(task_context):
    """Test brand analyzer agent."""
    agent = BrandAnalyzerAgent()
    result = agent.analyze_brand(task_context)
    
    assert isinstance(result, dict)
    assert "visual_identity" in result
    assert "messaging" in result
    assert "consistency" in result

def test_competitive_visual_agent(task_context):
    """Test competitive visual agent."""
    agent = CompetitiveVisualAgent()
    task_context.competitor_data = [{
        "url": "https://competitor.com",
        "design_analysis": {"colors": {"primary_colors": ["#333333"]}},
        "ux_analysis": {"navigation": {"menu_structure": "flat"}},
        "brand_analysis": {"visual_identity": {"logo_presence": {"logo_count": 1}}}
    }]
    
    result = agent.analyze_competitive(task_context)
    
    assert isinstance(result, dict)
    assert "visual_comparison" in result
    assert "content_comparison" in result
    assert "market_positioning" in result
    assert "differentiation_score" in result

def test_color_utils():
    """Test color utility functions."""
    # Test normalize_color
    assert normalize_color("#333") == "#333333"
    assert normalize_color("rgb(51, 51, 51)") == "#333333"
    assert normalize_color("rgba(51, 51, 51, 0.5)") == "#333333"
    assert normalize_color("invalid") is None
    
    # Test hex_to_hsl
    hsl = hex_to_hsl("#333333")
    assert isinstance(hsl, dict)
    assert "hue" in hsl
    assert "saturation" in hsl
    assert "lightness" in hsl

def test_html_utils(mock_driver, sample_html):
    """Test HTML utility functions."""
    # Test extract_text_content
    text = extract_text_content(mock_driver)
    assert isinstance(text, str)
    
    # Test get_element_styles
    styles = get_element_styles(mock_driver)
    assert isinstance(styles, list)
    assert all(isinstance(style, dict) for style in styles)

def test_task_context():
    """Test TaskContext model."""
    context = TaskContext(
        description="Test analysis",
        expected_output="Test results",
        screenshot=b'fake_screenshot',
        html_content="<html></html>",
        driver=None
    )
    
    assert context.description == "Test analysis"
    assert context.expected_output == "Test results"
    assert context.screenshot == b'fake_screenshot'
    assert context.html_content == "<html></html>"
    assert context.driver is None
    assert isinstance(context.competitor_data, list)
    assert len(context.competitor_data) == 0 