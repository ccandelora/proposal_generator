"""Integration tests for content generation components."""
import pytest
from src.proposal_generator.components.content_generator.agents.topic_agent import TopicAnalyzerAgent
from src.proposal_generator.components.content_generator.agents.writing_agent import WritingAgent
from src.proposal_generator.components.content_generator.agents.style_agent import StyleGuideAgent
from src.proposal_generator.components.content_generator.models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone,
    GeneratedContent
)

@pytest.fixture
def content_generation_system():
    """Create integrated content generation system."""
    return {
        'topic_agent': TopicAnalyzerAgent(),
        'writing_agent': WritingAgent(),
        'style_agent': StyleGuideAgent()
    }

@pytest.fixture
def style_config():
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

def test_end_to_end_content_generation(content_generation_system, sample_request, style_config):
    """Test complete content generation flow."""
    # Configure style agent
    content_generation_system['style_agent'].configure_style_guide(style_config)
    
    # Generate topic analysis
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
    assert topic_analysis is not None
    assert 'outline' in topic_analysis
    
    # Generate content
    content = content_generation_system['writing_agent'].generate_content(
        sample_request,
        topic_analysis
    )
    assert isinstance(content, GeneratedContent)
    
    # Apply style to each section
    for section in content.sections:
        section.content = content_generation_system['style_agent'].apply_style_rules(
            section.content,
            sample_request.tone
        )
    
    # Verify end-to-end results
    assert content.title is not None
    assert len(content.sections) > 0
    assert content.summary is not None
    assert len(content.recommendations) > 0
    
    # Verify style application
    for section in content.sections:
        # Check branding
        assert style_config['company_name'] in section.content
        
        # Check preferred terms
        assert 'utilize' in section.content.lower()
        assert 'use' not in section.content.lower()
        
        # Check avoided terms
        for term in style_config['avoided_terms']:
            assert term not in section.content.lower()

def test_topic_to_writing_integration(content_generation_system, sample_request):
    """Test integration between topic analyzer and writing agent."""
    # Generate topic analysis
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
    
    # Verify topic analysis structure
    assert 'outline' in topic_analysis
    assert 'themes_by_section' in topic_analysis
    assert len(topic_analysis['outline']['sections']) > 0
    
    # Generate content using topic analysis
    content = content_generation_system['writing_agent'].generate_content(
        sample_request,
        topic_analysis
    )
    
    # Verify content matches topic analysis
    section_names = [section.title for section in content.sections]
    analysis_sections = [section['name'] for section in topic_analysis['outline']['sections']]
    assert all(name in section_names for name in analysis_sections)
    
    # Verify themes are used in content
    for section in content.sections:
        themes = topic_analysis['themes_by_section'].get(section.title, [])
        assert any(theme.lower() in section.content.lower() for theme in themes)

def test_writing_to_style_integration(content_generation_system, sample_request, style_config):
    """Test integration between writing agent and style agent."""
    # Configure style agent
    content_generation_system['style_agent'].configure_style_guide(style_config)
    
    # Generate content
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
    content = content_generation_system['writing_agent'].generate_content(
        sample_request,
        topic_analysis
    )
    
    # Apply style to content
    original_sections = [section.content for section in content.sections]
    styled_sections = []
    
    for section_content in original_sections:
        styled_content = content_generation_system['style_agent'].apply_style_rules(
            section_content,
            sample_request.tone
        )
        styled_sections.append(styled_content)
        
        # Verify style rules are applied
        assert styled_content != section_content
        assert style_config['company_name'] in styled_content
        
        # Verify preferred terms
        for original, preferred in style_config['preferred_terms'].items():
            if original in section_content:
                assert preferred in styled_content
                assert original not in styled_content

def test_content_consistency(content_generation_system, sample_request, style_config):
    """Test consistency across multiple content generations."""
    content_generation_system['style_agent'].configure_style_guide(style_config)
    
    # Generate content multiple times
    contents = []
    for _ in range(3):
        topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
        content = content_generation_system['writing_agent'].generate_content(
            sample_request,
            topic_analysis
        )
        
        # Apply style
        for section in content.sections:
            section.content = content_generation_system['style_agent'].apply_style_rules(
                section.content,
                sample_request.tone
            )
            
        contents.append(content)
    
    # Verify consistent structure
    section_counts = [len(content.sections) for content in contents]
    assert len(set(section_counts)) == 1  # All should have same number of sections
    
    # Verify consistent styling
    for content in contents:
        for section in content.sections:
            assert style_config['company_name'] in section.content
            assert all(term not in section.content.lower() 
                      for term in style_config['avoided_terms'])

def test_error_handling_integration(content_generation_system):
    """Test error handling across components."""
    # Test with invalid request
    invalid_request = None
    
    # Topic analysis should handle error gracefully
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(invalid_request)
    assert isinstance(topic_analysis, dict)
    assert len(topic_analysis.get('outline', {}).get('sections', [])) == 0
    
    # Writing agent should handle invalid topic analysis
    content = content_generation_system['writing_agent'].generate_content(
        invalid_request,
        topic_analysis
    )
    assert isinstance(content, GeneratedContent)
    assert len(content.sections) == 0
    
    # Style agent should handle invalid content
    styled_content = content_generation_system['style_agent'].apply_style_rules(
        None,
        ContentTone.FORMAL
    )
    assert styled_content is None

def test_content_requirements_integration(content_generation_system, sample_request, style_config):
    """Test that content requirements are maintained through the pipeline."""
    content_generation_system['style_agent'].configure_style_guide(style_config)
    
    # Add specific requirements
    sample_request.required_sections = ["Executive Summary", "Technical Architecture"]
    sample_request.key_points.extend(["Reliability", "Maintainability"])
    sample_request.keywords.extend(["microservices", "containerization"])
    
    # Generate content
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
    content = content_generation_system['writing_agent'].generate_content(
        sample_request,
        topic_analysis
    )
    
    # Apply style
    for section in content.sections:
        section.content = content_generation_system['style_agent'].apply_style_rules(
            section.content,
            sample_request.tone
        )
    
    # Verify requirements are met
    section_titles = [section.title for section in content.sections]
    assert all(required in section_titles for required in sample_request.required_sections)
    
    # Verify key points and keywords are included
    all_content = " ".join(section.content.lower() for section in content.sections)
    assert all(point.lower() in all_content for point in sample_request.key_points)
    assert all(keyword.lower() in all_content for keyword in sample_request.keywords)

def test_metadata_consistency(content_generation_system, sample_request, style_config):
    """Test consistency of metadata through the pipeline."""
    content_generation_system['style_agent'].configure_style_guide(style_config)
    
    # Generate content
    topic_analysis = content_generation_system['topic_agent'].analyze_topic(sample_request)
    content = content_generation_system['writing_agent'].generate_content(
        sample_request,
        topic_analysis
    )
    
    # Verify metadata consistency
    assert content.metadata['target_audience'] == sample_request.target_audience
    assert content.metadata['tone'] == sample_request.tone.value
    assert 'analysis' in content.metadata
    
    # Verify metrics are calculated
    assert 'word_count' in content.metrics
    assert 'readability_score' in content.metrics
    assert 'keyword_density' in content.metrics
    
    # Verify style influence on metrics
    for section in content.sections:
        styled_content = content_generation_system['style_agent'].apply_style_rules(
            section.content,
            sample_request.tone
        )
        section.content = styled_content
        
    # Recalculate metrics after styling
    final_metrics = content_generation_system['writing_agent']._calculate_content_metrics(
        content.sections
    )
    
    # Verify metrics changed after styling
    assert final_metrics['readability_score'] != content.metrics['readability_score'] 