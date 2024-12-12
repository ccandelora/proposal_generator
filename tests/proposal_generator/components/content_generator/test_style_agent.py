"""Tests for the style guide agent."""
import pytest
from src.proposal_generator.components.content_generator.agents.style_agent import StyleGuideAgent
from src.proposal_generator.components.content_generator.models.content_model import ContentTone

@pytest.fixture
def style_agent():
    """Create a style agent instance."""
    return StyleGuideAgent()

@pytest.fixture
def sample_style_config():
    """Sample style configuration."""
    return {
        'company_name': 'TechCorp',
        'tagline': 'Innovating Tomorrow',
        'values': ['Innovation', 'Quality', 'Integrity'],
        'voice': 'professional',
        'preferred_terms': {
            'use': 'utilize',
            'problem': 'challenge',
            'good': 'excellent'
        },
        'avoided_terms': ['bad', 'poor', 'terrible'],
        'industry_terms': ['API', 'SaaS', 'Cloud']
    }

@pytest.fixture
def configured_style_agent(style_agent, sample_style_config):
    """Create a configured style agent."""
    style_agent.configure_style_guide(sample_style_config)
    return style_agent

def test_style_agent_initialization(style_agent):
    """Test style agent initialization."""
    assert style_agent is not None
    assert style_agent.style_rules is not None
    assert 'tone' in style_agent.style_rules
    assert 'branding' in style_agent.style_rules
    assert 'formatting' in style_agent.style_rules
    assert 'language' in style_agent.style_rules

def test_configure_style_guide(style_agent, sample_style_config):
    """Test style guide configuration."""
    style_agent.configure_style_guide(sample_style_config)
    
    # Check branding rules
    assert style_agent.style_rules['branding']['company_name'] == 'TechCorp'
    assert style_agent.style_rules['branding']['tagline'] == 'Innovating Tomorrow'
    assert 'Innovation' in style_agent.style_rules['branding']['values']
    
    # Check language rules
    assert 'utilize' in style_agent.style_rules['language']['preferred_terms'].values()
    assert 'bad' in style_agent.style_rules['language']['avoided_terms']

def test_apply_style_rules(configured_style_agent):
    """Test applying style rules to content."""
    content = "We use good solutions to fix bad problems."
    styled_content = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    
    # Check word replacements
    assert 'utilize' in styled_content
    assert 'excellent' in styled_content
    assert 'challenge' in styled_content
    assert 'bad' not in styled_content

def test_validate_style(configured_style_agent):
    """Test style validation."""
    content = "This is a bad solution that we use."
    violations = configured_style_agent.validate_style(content, ContentTone.FORMAL)
    
    # Check violations
    assert len(violations['language']) > 0  # Should find 'bad' as avoided term
    assert len(violations['branding']) > 0  # Should note missing company name

def test_tone_rules(configured_style_agent):
    """Test tone-specific rules."""
    content = "This is a good and simple solution."
    
    # Test formal tone
    formal = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    assert 'excellent' in formal
    
    # Test technical tone
    technical = configured_style_agent.apply_style_rules(content, ContentTone.TECHNICAL)
    assert 'implement' in technical or 'utilize' in technical

def test_formatting_rules(configured_style_agent):
    """Test formatting rules."""
    content = "# Main Title\n## Subtitle\nContent here"
    formatted = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    
    # Check heading formatting
    assert '**' in formatted  # Should have bold formatting
    assert 'Main Title' in formatted
    assert 'Subtitle' in formatted

def test_branding_rules(configured_style_agent):
    """Test branding rules."""
    content = "Welcome to [COMPANY]. [TAGLINE]"
    branded = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    
    assert 'TechCorp' in branded
    assert 'Innovating Tomorrow' in branded

def test_language_rules(configured_style_agent):
    """Test language rules."""
    content = "We use advanced solutions."
    styled = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    
    assert 'utilize' in styled
    assert 'use' not in styled

def test_style_validation_empty_content(configured_style_agent):
    """Test style validation with empty content."""
    violations = configured_style_agent.validate_style("", ContentTone.FORMAL)
    
    assert isinstance(violations, dict)
    assert 'branding' in violations
    assert len(violations['branding']) > 0  # Should note missing company name

def test_style_validation_long_paragraphs(configured_style_agent):
    """Test style validation for paragraph length."""
    long_paragraph = " ".join(["word"] * 200)  # Create paragraph > max length
    violations = configured_style_agent.validate_style(long_paragraph, ContentTone.FORMAL)
    
    assert 'formatting' in violations
    assert len(violations['formatting']) > 0  # Should flag long paragraph

def test_error_handling(style_agent):
    """Test error handling in style agent."""
    # Test with invalid configuration
    style_agent.configure_style_guide(None)
    assert style_agent.style_rules['tone'] == {}
    
    # Test with invalid content
    result = style_agent.apply_style_rules(None, ContentTone.FORMAL)
    assert result == None

def test_word_choice_enhancement(configured_style_agent):
    """Test word choice enhancement."""
    test_cases = [
        ("This is good", "This is excellent"),  # Professional enhancement
        ("We will fix it", "We will resolve it"),  # Technical enhancement
        ("This will help you", "This will empower you")  # Compelling enhancement
    ]
    
    for original, expected in test_cases:
        enhanced = configured_style_agent.apply_style_rules(original, ContentTone.FORMAL)
        assert expected.lower() in enhanced.lower()

def test_heading_formatting(configured_style_agent):
    """Test heading formatting."""
    test_cases = [
        ("# test heading", "**Test Heading**"),  # H1 formatting
        ("## test heading", "**Test heading**"),  # H2 formatting
        ("### test heading", "Test heading")  # H3 formatting
    ]
    
    for original, expected in test_cases:
        formatted = configured_style_agent.apply_style_rules(original, ContentTone.FORMAL)
        assert expected in formatted

def test_multiple_style_rules(configured_style_agent):
    """Test applying multiple style rules together."""
    content = """# Welcome to [COMPANY]
    
    We use good solutions to fix bad problems.
    
    [TAGLINE]"""
    
    styled = configured_style_agent.apply_style_rules(content, ContentTone.FORMAL)
    
    # Check multiple rules applied
    assert 'TechCorp' in styled  # Branding
    assert 'excellent' in styled  # Word choice
    assert 'resolve' in styled or 'implement' in styled  # Technical terms
    assert 'Innovating Tomorrow' in styled  # Tagline
    assert '**Welcome' in styled  # Formatting 