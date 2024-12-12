"""Tests for the topic analyzer agent."""
import pytest
from src.proposal_generator.components.content_generator.agents.topic_agent import TopicAnalyzerAgent
from src.proposal_generator.components.content_generator.models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone
)

@pytest.fixture
def topic_agent():
    """Create a topic analyzer instance."""
    return TopicAnalyzerAgent()

@pytest.fixture
def sample_request():
    """Sample content request."""
    return ContentRequest(
        content_type=ContentType.PROPOSAL,
        target_audience="Enterprise Clients",
        tone=ContentTone.FORMAL,
        key_points=["Scalability", "Security", "Performance"],
        keywords=["cloud", "enterprise", "solution"],
        max_length=2000,
        required_sections=["Executive Summary", "Solution Overview"],
        reference_data={
            "case_study_1": "Success story with Client A",
            "testimonial_1": "Great service and support"
        },
        style_guide={
            "voice": "professional",
            "formatting": "standard"
        }
    )

def test_topic_agent_initialization(topic_agent):
    """Test topic agent initialization."""
    assert topic_agent is not None

def test_analyze_topic(topic_agent, sample_request):
    """Test topic analysis."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    assert 'outline' in analysis
    assert 'themes_by_section' in analysis
    assert 'metadata' in analysis
    assert len(analysis['outline']['sections']) > 0
    assert all(section['name'] in analysis['themes_by_section'] 
              for section in analysis['outline']['sections'])

def test_section_hierarchy(topic_agent):
    """Test section hierarchy determination."""
    test_sections = [
        ('executive_summary', 1),
        ('problem_statement', 1),
        ('implementation_details', 2),
        ('technical_specifications', 2)
    ]
    
    for section_name, expected_level in test_sections:
        level = topic_agent._determine_section_level(section_name)
        assert level == expected_level

def test_parent_section_determination(topic_agent):
    """Test parent section determination."""
    test_cases = [
        ('performance_requirements', 'system_overview'),
        ('security_considerations', 'system_overview'),
        ('deployment_guide', 'implementation_plan'),
        ('random_section', None)
    ]
    
    for section_name, expected_parent in test_cases:
        parent = topic_agent._determine_parent_section(section_name, [])
        assert parent == expected_parent

def test_child_sections_determination(topic_agent):
    """Test child sections determination."""
    sections = [
        {'name': 'system_overview'},
        {'name': 'performance_requirements'},
        {'name': 'security_considerations'},
        {'name': 'other_section'}
    ]
    
    children = topic_agent._determine_child_sections('system_overview', sections)
    
    assert 'performance_requirements' in children
    assert 'security_considerations' in children
    assert 'other_section' not in children

def test_required_sections_inclusion(topic_agent, sample_request):
    """Test that required sections are included in analysis."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    section_names = [section['name'] for section in analysis['outline']['sections']]
    for required_section in sample_request.required_sections:
        assert required_section in section_names

def test_theme_generation(topic_agent, sample_request):
    """Test theme generation for sections."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    for section_name, themes in analysis['themes_by_section'].items():
        assert len(themes) > 0
        assert any(keyword in ' '.join(themes).lower() 
                  for keyword in sample_request.keywords)

def test_content_type_specific_analysis(topic_agent):
    """Test analysis for different content types."""
    test_cases = [
        (ContentType.PROPOSAL, ["Executive Summary", "Solution"]),
        (ContentType.TECHNICAL_SPEC, ["Architecture", "Implementation"]),
        (ContentType.MARKET_ANALYSIS, ["Market Overview", "Competition"])
    ]
    
    for content_type, expected_sections in test_cases:
        request = ContentRequest(
            content_type=content_type,
            target_audience="Test",
            tone=ContentTone.FORMAL,
            key_points=[],
            keywords=[]
        )
        
        analysis = topic_agent.analyze_topic(request)
        section_names = [section['name'] for section in analysis['outline']['sections']]
        assert any(expected in ' '.join(section_names) 
                  for expected in expected_sections)

def test_tone_influence(topic_agent):
    """Test how tone influences analysis."""
    test_cases = [
        (ContentTone.FORMAL, ["professional", "comprehensive"]),
        (ContentTone.TECHNICAL, ["technical", "detailed"]),
        (ContentTone.PERSUASIVE, ["benefits", "value"])
    ]
    
    for tone, expected_themes in test_cases:
        request = ContentRequest(
            content_type=ContentType.PROPOSAL,
            target_audience="Test",
            tone=tone,
            key_points=[],
            keywords=[]
        )
        
        analysis = topic_agent.analyze_topic(request)
        all_themes = [theme for themes in analysis['themes_by_section'].values() 
                     for theme in themes]
        assert any(expected in ' '.join(all_themes).lower() 
                  for expected in expected_themes)

def test_metadata_generation(topic_agent, sample_request):
    """Test metadata generation."""
    analysis = topic_agent.analyze_topic(sample_request)
    metadata = analysis['metadata']
    
    assert 'target_length' in metadata
    assert 'complexity_level' in metadata
    assert metadata['target_length'] <= sample_request.max_length

def test_error_handling(topic_agent):
    """Test error handling."""
    # Test with None request
    analysis = topic_agent.analyze_topic(None)
    assert isinstance(analysis, dict)
    assert len(analysis['outline']['sections']) == 0
    
    # Test with minimal request
    minimal_request = ContentRequest(
        content_type=ContentType.PROPOSAL,
        target_audience="Test",
        tone=ContentTone.FORMAL,
        key_points=[],
        keywords=[]
    )
    analysis = topic_agent.analyze_topic(minimal_request)
    assert isinstance(analysis, dict)
    assert len(analysis['outline']['sections']) > 0

def test_section_content_generation(topic_agent, sample_request):
    """Test section content generation."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    for section in analysis['outline']['sections']:
        assert 'name' in section
        assert 'expected_content' in section
        assert 'key_points' in section
        assert len(section['key_points']) > 0

def test_theme_relevance(topic_agent, sample_request):
    """Test theme relevance to keywords and key points."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    all_themes = [theme for themes in analysis['themes_by_section'].values() 
                 for theme in themes]
    
    # Check if themes relate to keywords and key points
    relevant_terms = set(sample_request.keywords + sample_request.key_points)
    theme_words = set(' '.join(all_themes).lower().split())
    
    assert any(term.lower() in theme_words for term in relevant_terms)

def test_section_ordering(topic_agent, sample_request):
    """Test logical ordering of sections."""
    analysis = topic_agent.analyze_topic(sample_request)
    sections = analysis['outline']['sections']
    
    # Executive Summary should come first if present
    if any(section['name'] == "Executive Summary" for section in sections):
        assert sections[0]['name'] == "Executive Summary"
    
    # Implementation/technical sections should come after overview sections
    section_names = [section['name'] for section in sections]
    if "Solution Overview" in section_names and "Implementation Details" in section_names:
        overview_index = section_names.index("Solution Overview")
        impl_index = section_names.index("Implementation Details")
        assert overview_index < impl_index

def test_theme_consistency(topic_agent, sample_request):
    """Test consistency of themes across related sections."""
    analysis = topic_agent.analyze_topic(sample_request)
    
    # Get themes for related sections
    overview_themes = set(analysis['themes_by_section'].get("Solution Overview", []))
    details_themes = set(analysis['themes_by_section'].get("Implementation Details", []))
    
    # Related sections should share some themes
    if overview_themes and details_themes:
        assert len(overview_themes.intersection(details_themes)) > 0 