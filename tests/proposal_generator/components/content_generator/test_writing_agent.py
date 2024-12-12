"""Tests for the writing agent."""
import pytest
from src.proposal_generator.components.content_generator.agents.writing_agent import WritingAgent
from src.proposal_generator.components.content_generator.models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone,
    ContentSection,
    GeneratedContent
)

@pytest.fixture
def writing_agent():
    """Create a writing agent instance."""
    return WritingAgent()

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

@pytest.fixture
def sample_topic_analysis():
    """Sample topic analysis."""
    return {
        'outline': {
            'sections': [
                {
                    'name': 'Executive Summary',
                    'expected_content': 'Overview of the proposal',
                    'key_points': ['Value proposition', 'Key benefits']
                },
                {
                    'name': 'Solution Overview',
                    'expected_content': 'Detailed solution description',
                    'key_points': ['Features', 'Architecture']
                }
            ]
        },
        'themes_by_section': {
            'Executive Summary': ['business value', 'innovation'],
            'Solution Overview': ['scalability', 'security']
        },
        'metadata': {
            'target_length': 1500,
            'complexity_level': 'medium'
        }
    }

def test_writing_agent_initialization(writing_agent):
    """Test writing agent initialization."""
    assert writing_agent is not None

def test_generate_content(writing_agent, sample_request, sample_topic_analysis):
    """Test content generation."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    assert isinstance(content, GeneratedContent)
    assert content.content_type == ContentType.PROPOSAL
    assert len(content.sections) == len(sample_topic_analysis['outline']['sections'])
    assert content.title is not None
    assert content.summary is not None
    assert len(content.recommendations) > 0

def test_generate_section(writing_agent, sample_request, sample_topic_analysis):
    """Test section generation."""
    outline = sample_topic_analysis['outline']['sections'][0]
    themes = sample_topic_analysis['themes_by_section'][outline['name']]
    
    section = writing_agent._generate_section(outline, sample_request, themes)
    
    assert isinstance(section, ContentSection)
    assert section.title == outline['name']
    assert len(section.content) > 0
    assert len(section.keywords) > 0
    assert len(section.metrics) > 0

def test_content_metrics(writing_agent, sample_request, sample_topic_analysis):
    """Test content metrics calculation."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    assert 'word_count' in content.metrics
    assert 'readability_score' in content.metrics
    assert 'keyword_density' in content.metrics
    assert 'quality_score' in content.metrics
    assert 0 <= content.metrics['readability_score'] <= 1
    assert 0 <= content.metrics['quality_score'] <= 1

def test_generate_summary(writing_agent, sample_request, sample_topic_analysis):
    """Test summary generation."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    assert "Executive Summary:" in content.summary
    assert "Content Overview:" in content.summary
    assert str(content.metrics['word_count']) in content.summary
    assert str(round(content.metrics['quality_score'], 2)) in content.summary

def test_generate_recommendations(writing_agent, sample_request, sample_topic_analysis):
    """Test recommendations generation."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    assert len(content.recommendations) > 0
    assert all(isinstance(rec, str) for rec in content.recommendations)
    assert any('content' in rec.lower() for rec in content.recommendations)

def test_error_handling(writing_agent):
    """Test error handling."""
    # Test with invalid request
    content = writing_agent.generate_content(None, {})
    assert isinstance(content, GeneratedContent)
    assert len(content.sections) == 0
    assert content.title == ""
    
    # Test with invalid topic analysis
    content = writing_agent.generate_content(
        ContentRequest(
            content_type=ContentType.PROPOSAL,
            target_audience="Test",
            tone=ContentTone.FORMAL,
            key_points=[],
            keywords=[]
        ),
        None
    )
    assert isinstance(content, GeneratedContent)
    assert len(content.sections) == 0

def test_section_metrics(writing_agent, sample_request, sample_topic_analysis):
    """Test section metrics calculation."""
    outline = sample_topic_analysis['outline']['sections'][0]
    themes = sample_topic_analysis['themes_by_section'][outline['name']]
    
    section = writing_agent._generate_section(outline, sample_request, themes)
    
    assert 'word_count' in section.metrics
    assert 'keyword_count' in section.metrics
    assert 'average_sentence_length' in section.metrics
    assert section.metrics['word_count'] > 0

def test_keyword_extraction(writing_agent):
    """Test keyword extraction."""
    content = "This is a test content about cloud computing and enterprise solutions."
    themes = ["cloud", "enterprise"]
    
    keywords = writing_agent._extract_keywords(content, themes)
    
    assert len(keywords) > 0
    assert "cloud" in keywords
    assert "enterprise" in keywords
    assert any(len(word) > 4 for word in keywords)

def test_content_type_specific_generation(writing_agent, sample_topic_analysis):
    """Test generation for different content types."""
    test_cases = [
        (ContentType.PROPOSAL, "Proposal"),
        (ContentType.TECHNICAL_SPEC, "Technical Specification"),
        (ContentType.MARKET_ANALYSIS, "Market Analysis")
    ]
    
    for content_type, expected_prefix in test_cases:
        request = ContentRequest(
            content_type=content_type,
            target_audience="Test Audience",
            tone=ContentTone.FORMAL,
            key_points=[],
            keywords=[]
        )
        
        content = writing_agent.generate_content(request, sample_topic_analysis)
        assert expected_prefix in content.title

def test_tone_specific_generation(writing_agent, sample_topic_analysis):
    """Test generation for different tones."""
    test_cases = [
        (ContentTone.FORMAL, ["professional", "objective"]),
        (ContentTone.TECHNICAL, ["technical", "specific"]),
        (ContentTone.PERSUASIVE, ["compelling", "benefit"])
    ]
    
    for tone, expected_words in test_cases:
        request = ContentRequest(
            content_type=ContentType.PROPOSAL,
            target_audience="Test Audience",
            tone=tone,
            key_points=[],
            keywords=[]
        )
        
        content = writing_agent.generate_content(request, sample_topic_analysis)
        content_text = " ".join(section.content.lower() for section in content.sections)
        assert any(word in content_text for word in expected_words)

def test_reference_handling(writing_agent, sample_request, sample_topic_analysis):
    """Test handling of reference data."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    # Check if references are included in sections
    has_references = False
    for section in content.sections:
        if section.references:
            has_references = True
            break
    
    assert has_references
    assert any(ref['value'] == "Success story with Client A" 
              for section in content.sections 
              for ref in section.references)

def test_content_length_control(writing_agent, sample_topic_analysis):
    """Test content length control."""
    # Test with different max lengths
    test_lengths = [500, 1000, 2000]
    
    for max_length in test_lengths:
        request = ContentRequest(
            content_type=ContentType.PROPOSAL,
            target_audience="Test Audience",
            tone=ContentTone.FORMAL,
            key_points=[],
            keywords=[],
            max_length=max_length
        )
        
        content = writing_agent.generate_content(request, sample_topic_analysis)
        total_words = sum(len(section.content.split()) for section in content.sections)
        
        # Allow some flexibility in length (±20%)
        assert total_words <= max_length * 1.2
        assert total_words >= max_length * 0.8

def test_quality_metrics(writing_agent, sample_request, sample_topic_analysis):
    """Test quality metrics calculation."""
    content = writing_agent.generate_content(sample_request, sample_topic_analysis)
    
    # Test all quality metrics
    metrics = content.metrics
    assert 0 <= metrics['readability_score'] <= 1
    assert 0 <= metrics['technical_complexity'] <= 1
    assert 0 <= metrics['uniqueness_score'] <= 1
    assert 0 <= metrics['sentiment_score'] <= 1
    assert 0 <= metrics['quality_score'] <= 1
    
    # Test keyword density
    assert isinstance(metrics['keyword_density'], dict)
    assert all(0 <= density <= 1 for density in metrics['keyword_density'].values()) 