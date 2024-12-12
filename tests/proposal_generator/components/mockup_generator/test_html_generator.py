"""Tests for HTML generator."""
import pytest
from src.proposal_generator.components.mockup_generator.utils.html_generator import HTMLGenerator
from src.proposal_generator.components.mockup_generator.models.mockup_model import (
    ContentElements,
    ContentElement,
    DeviceType
)

@pytest.fixture
def sample_content():
    """Sample content elements."""
    return ContentElements(
        header=[
            ContentElement(
                type="heading",
                content={"text": "Company Name", "level": 1},
                style={},
                position={},
                responsive_behavior={}
            )
        ],
        navigation=[
            ContentElement(
                type="link",
                content={"text": "Home", "href": "#"},
                style={},
                position={},
                responsive_behavior={}
            ),
            ContentElement(
                type="link",
                content={"text": "About", "href": "#about"},
                style={},
                position={},
                responsive_behavior={}
            )
        ],
        hero=[
            ContentElement(
                type="heading",
                content={"text": "Welcome", "level": 2},
                style={},
                position={},
                responsive_behavior={}
            ),
            ContentElement(
                type="button",
                content={"text": "Get Started"},
                style={},
                position={},
                responsive_behavior={}
            )
        ],
        main=[
            ContentElement(
                type="section",
                content={
                    "children": [
                        ContentElement(
                            type="heading",
                            content={"text": "Features", "level": 2},
                            style={},
                            position={},
                            responsive_behavior={}
                        ),
                        ContentElement(
                            type="list",
                            content={
                                "type": "ul",
                                "items": ["Feature 1", "Feature 2", "Feature 3"]
                            },
                            style={},
                            position={},
                            responsive_behavior={}
                        )
                    ]
                },
                style={},
                position={},
                responsive_behavior={}
            )
        ],
        footer=[
            ContentElement(
                type="paragraph",
                content={"text": "© 2024 Company Name"},
                style={},
                position={},
                responsive_behavior={}
            )
        ]
    )

def test_generate_html(sample_content):
    """Test HTML generation."""
    html = HTMLGenerator.generate_html(sample_content, DeviceType.DESKTOP)
    
    # Check basic structure
    assert '<!DOCTYPE html>' in html
    assert '<html lang="en">' in html
    assert '<head>' in html
    assert '<body class="device-desktop">' in html
    assert '</html>' in html
    
    # Check meta tags
    assert '<meta charset="UTF-8">' in html
    assert '<meta name="viewport"' in html
    
    # Check content sections
    assert '<header>' in html
    assert '<nav>' in html
    assert '<section class="hero">' in html
    assert '<main>' in html
    assert '<footer>' in html

def test_generate_elements(sample_content):
    """Test element generation."""
    html = HTMLGenerator.generate_html(sample_content, DeviceType.DESKTOP)
    
    # Check heading
    assert '<h1' in html
    assert 'Company Name' in html
    
    # Check navigation links
    assert '<a href="#"' in html
    assert '>Home<' in html
    assert '<a href="#about"' in html
    assert '>About<' in html
    
    # Check hero content
    assert '<h2' in html
    assert 'Welcome' in html
    assert '<button' in html
    assert 'Get Started' in html
    
    # Check main content
    assert 'Features' in html
    assert '<ul' in html
    assert '<li>Feature 1</li>' in html
    
    # Check footer
    assert '© 2024 Company Name' in html

def test_generate_form():
    """Test form generation."""
    form_element = ContentElement(
        type="form",
        content={
            "fields": [
                {
                    "type": "text",
                    "label": "Name",
                    "name": "name",
                    "required": True,
                    "placeholder": "Enter your name"
                },
                {
                    "type": "email",
                    "label": "Email",
                    "name": "email",
                    "required": True,
                    "placeholder": "Enter your email"
                },
                {
                    "type": "textarea",
                    "label": "Message",
                    "name": "message",
                    "placeholder": "Your message"
                },
                {
                    "type": "select",
                    "label": "Subject",
                    "name": "subject",
                    "options": [
                        {"value": "general", "label": "General Inquiry"},
                        {"value": "support", "label": "Support"}
                    ]
                }
            ]
        },
        style={},
        position={},
        responsive_behavior={}
    )
    
    html = HTMLGenerator._generate_element(form_element)
    
    # Check form structure
    assert '<form' in html
    assert '<div class="form-field">' in html
    
    # Check text input
    assert '<input type="text"' in html
    assert 'name="name"' in html
    assert 'required' in html
    
    # Check email input
    assert '<input type="email"' in html
    assert 'name="email"' in html
    
    # Check textarea
    assert '<textarea' in html
    assert 'name="message"' in html
    
    # Check select
    assert '<select' in html
    assert '<option value="general"' in html
    assert 'General Inquiry' in html

def test_generate_with_accessibility():
    """Test accessibility attributes generation."""
    element = ContentElement(
        type="button",
        content={
            "text": "Close",
            "aria": {
                "label": "Close dialog",
                "expanded": "false"
            },
            "role": "button"
        },
        style={},
        position={},
        responsive_behavior={}
    )
    
    html = HTMLGenerator._generate_element(element)
    
    assert 'aria-label="Close dialog"' in html
    assert 'aria-expanded="false"' in html
    assert 'role="button"' in html

def test_generate_with_data_attributes():
    """Test data attributes generation."""
    element = ContentElement(
        type="div",
        content={
            "text": "Content",
            "data": {
                "test": "value",
                "index": "1"
            }
        },
        style={},
        position={},
        responsive_behavior={}
    )
    
    html = HTMLGenerator._generate_element(element)
    
    assert 'data-test="value"' in html
    assert 'data-index="1"' in html

def test_generate_nested_content():
    """Test nested content generation."""
    element = ContentElement(
        type="container",
        content={
            "children": [
                ContentElement(
                    type="heading",
                    content={"text": "Title", "level": 2},
                    style={},
                    position={},
                    responsive_behavior={}
                ),
                ContentElement(
                    type="paragraph",
                    content={"text": "Description"},
                    style={},
                    position={},
                    responsive_behavior={}
                )
            ]
        },
        style={},
        position={},
        responsive_behavior={}
    )
    
    html = HTMLGenerator._generate_element(element)
    
    assert '<div class="container">' in html
    assert '<h2' in html
    assert 'Title' in html
    assert '<p' in html
    assert 'Description' in html

def test_generate_with_custom_attributes():
    """Test custom attributes generation."""
    element = ContentElement(
        type="div",
        content={
            "text": "Content",
            "attributes": {
                "data-custom": "value",
                "tabindex": "0"
            }
        },
        style={},
        position={},
        responsive_behavior={}
    )
    
    html = HTMLGenerator._generate_element(element)
    
    assert 'data-custom="value"' in html
    assert 'tabindex="0"' in html 