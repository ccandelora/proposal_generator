"""Integration tests between major system components."""
import pytest
from src.proposal_generator.components.content_generator.agents.topic_agent import TopicAnalyzerAgent
from src.proposal_generator.components.content_generator.agents.writing_agent import WritingAgent
from src.proposal_generator.components.content_generator.agents.style_agent import StyleGuideAgent
from src.proposal_generator.components.seo_analyzer.main import SEOAnalyzer
from src.proposal_generator.components.market_analyzer.main import MarketAnalyzer
from src.proposal_generator.components.content_generator.models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone
)

@pytest.fixture
def integrated_system():
    """Create integrated system with all components."""
    return {
        'topic_agent': TopicAnalyzerAgent(),
        'writing_agent': WritingAgent(),
        'style_agent': StyleGuideAgent(),
        'seo_analyzer': SEOAnalyzer(),
        'market_analyzer': MarketAnalyzer()
    }

@pytest.fixture
def sample_website_data():
    """Sample website and competitor data."""
    return {
        'website': 'https://example.com',
        'competitors': [
            'https://competitor1.com',
            'https://competitor2.com'
        ],
        'industry': 'Technology',
        'target_market': 'Enterprise'
    }

@pytest.fixture
def sample_market_data():
    """Sample market analysis data."""
    return {
        'market_size': 1000000000,
        'growth_rate': 0.15,
        'key_trends': ['Cloud Adoption', 'Digital Transformation'],
        'competitor_data': {
            'competitor1': {
                'market_share': 0.2,
                'strengths': ['Brand Recognition', 'Product Range'],
                'weaknesses': ['High Prices', 'Complex Solutions']
            },
            'competitor2': {
                'market_share': 0.15,
                'strengths': ['Innovation', 'Customer Service'],
                'weaknesses': ['Limited Market Presence', 'Narrow Focus']
            }
        }
    }

@pytest.mark.asyncio
async def test_seo_to_content_integration(integrated_system, sample_website_data):
    """Test integration between SEO analysis and content generation."""
    # Perform SEO analysis
    seo_results = integrated_system['seo_analyzer'].analyze_seo(
        sample_website_data['website'],
        {'technical': {}, 'content': {}},
        {'backlinks': {}}
    )
    
    # Create content request incorporating SEO insights
    request = ContentRequest(
        content_type=ContentType.PROPOSAL,
        target_audience=sample_website_data['target_market'],
        tone=ContentTone.FORMAL,
        key_points=[
            insight.recommendations[0] 
            for insight in seo_results.values() 
            if insight.recommendations
        ],
        keywords=[
            keyword
            for insight in seo_results.values()
            for finding in insight.findings
            for keyword in finding.get('keywords', [])
        ],
        max_length=2000,
        required_sections=['SEO Strategy', 'Technical Improvements']
    )
    
    # Generate content
    topic_analysis = integrated_system['topic_agent'].analyze_topic(request)
    content = integrated_system['writing_agent'].generate_content(request, topic_analysis)
    
    # Verify SEO insights are incorporated
    all_content = " ".join(section.content for section in content.sections)
    assert any(insight.category in all_content for insight in seo_results.values())
    assert any(
        recommendation in all_content
        for insight in seo_results.values()
        for recommendation in insight.recommendations
    )

@pytest.mark.asyncio
async def test_market_to_content_integration(integrated_system, sample_market_data):
    """Test integration between market analysis and content generation."""
    # Perform market analysis
    market_results = await integrated_system['market_analyzer'].analyze_market({
        'market_data': sample_market_data,
        'competitors': sample_market_data['competitor_data']
    })
    
    # Create content request incorporating market insights
    request = ContentRequest(
        content_type=ContentType.MARKET_ANALYSIS,
        target_audience='Executive Team',
        tone=ContentTone.FORMAL,
        key_points=[
            f"Market size: ${sample_market_data['market_size']:,}",
            f"Growth rate: {sample_market_data['growth_rate']*100}%",
            *sample_market_data['key_trends']
        ],
        keywords=['market', 'growth', 'competition', 'trends'],
        max_length=3000,
        required_sections=['Market Overview', 'Competitive Analysis']
    )
    
    # Generate content
    topic_analysis = integrated_system['topic_agent'].analyze_topic(request)
    content = integrated_system['writing_agent'].generate_content(request, topic_analysis)
    
    # Verify market insights are incorporated
    all_content = " ".join(section.content for section in content.sections)
    assert str(sample_market_data['market_size']) in all_content
    assert all(trend in all_content for trend in sample_market_data['key_trends'])
    assert all(
        competitor in all_content
        for competitor in sample_market_data['competitor_data'].keys()
    )

@pytest.mark.asyncio
async def test_comprehensive_proposal_generation(integrated_system, sample_website_data, sample_market_data):
    """Test generation of comprehensive proposal using all components."""
    # Perform SEO analysis
    seo_results = integrated_system['seo_analyzer'].analyze_seo(
        sample_website_data['website'],
        {'technical': {}, 'content': {}},
        {'backlinks': {}}
    )
    
    # Perform market analysis
    market_results = await integrated_system['market_analyzer'].analyze_market({
        'market_data': sample_market_data,
        'competitors': sample_market_data['competitor_data']
    })
    
    # Create comprehensive content request
    request = ContentRequest(
        content_type=ContentType.PROPOSAL,
        target_audience='Enterprise Decision Makers',
        tone=ContentTone.PERSUASIVE,
        key_points=[
            *sample_market_data['key_trends'],
            *[insight.recommendations[0] for insight in seo_results.values() if insight.recommendations],
            f"Market growth potential: {sample_market_data['growth_rate']*100}%"
        ],
        keywords=[
            'market opportunity',
            'competitive advantage',
            'seo optimization',
            'growth strategy'
        ],
        max_length=5000,
        required_sections=[
            'Executive Summary',
            'Market Analysis',
            'SEO Strategy',
            'Implementation Plan'
        ]
    )
    
    # Generate content
    topic_analysis = integrated_system['topic_agent'].analyze_topic(request)
    content = integrated_system['writing_agent'].generate_content(request, topic_analysis)
    
    # Apply style
    style_config = {
        'company_name': 'TechCorp',
        'tagline': 'Innovating Tomorrow',
        'preferred_terms': {'opportunity': 'potential', 'problem': 'challenge'}
    }
    integrated_system['style_agent'].configure_style_guide(style_config)
    
    for section in content.sections:
        section.content = integrated_system['style_agent'].apply_style_rules(
            section.content,
            request.tone
        )
    
    # Verify comprehensive integration
    all_content = " ".join(section.content for section in content.sections)
    
    # Verify market insights
    assert str(sample_market_data['market_size']) in all_content
    assert all(trend in all_content for trend in sample_market_data['key_trends'])
    
    # Verify SEO insights
    assert any(insight.category in all_content for insight in seo_results.values())
    
    # Verify style application
    assert style_config['company_name'] in all_content
    assert 'potential' in all_content
    assert 'problem' not in all_content

@pytest.mark.asyncio
async def test_competitor_analysis_integration(integrated_system, sample_website_data, sample_market_data):
    """Test integration of competitor analysis across components."""
    # Analyze competitors' SEO
    competitor_seo = {}
    for competitor in sample_website_data['competitors']:
        competitor_seo[competitor] = integrated_system['seo_analyzer'].analyze_seo(
            competitor,
            {'technical': {}, 'content': {}},
            {'backlinks': {}}
        )
    
    # Get competitor market data
    competitor_market = sample_market_data['competitor_data']
    
    # Create competitor analysis request
    request = ContentRequest(
        content_type=ContentType.MARKET_ANALYSIS,
        target_audience='Strategy Team',
        tone=ContentTone.TECHNICAL,
        key_points=[
            f"{name}: {data['market_share']*100}% market share"
            for name, data in competitor_market.items()
        ],
        keywords=['competition', 'market share', 'strengths', 'weaknesses'],
        max_length=3000,
        required_sections=['Competitive Landscape', 'SWOT Analysis']
    )
    
    # Generate content
    topic_analysis = integrated_system['topic_agent'].analyze_topic(request)
    content = integrated_system['writing_agent'].generate_content(request, topic_analysis)
    
    # Verify competitor insights integration
    all_content = " ".join(section.content for section in content.sections)
    
    # Verify market insights
    for competitor, data in competitor_market.items():
        assert competitor in all_content
        assert any(strength in all_content for strength in data['strengths'])
        assert any(weakness in all_content for weakness in data['weaknesses'])
    
    # Verify SEO insights
    for competitor, seo_data in competitor_seo.items():
        assert any(insight.category in all_content for insight in seo_data.values())

@pytest.mark.asyncio
async def test_data_consistency_across_components(integrated_system, sample_website_data, sample_market_data):
    """Test consistency of data across all components."""
    # Gather insights from all components
    seo_results = integrated_system['seo_analyzer'].analyze_seo(
        sample_website_data['website'],
        {'technical': {}, 'content': {}},
        {'backlinks': {}}
    )
    
    market_results = await integrated_system['market_analyzer'].analyze_market({
        'market_data': sample_market_data,
        'competitors': sample_market_data['competitor_data']
    })
    
    # Generate multiple content pieces
    content_types = [
        (ContentType.MARKET_ANALYSIS, 'Market Analysis'),
        (ContentType.TECHNICAL_SPEC, 'Technical Implementation'),
        (ContentType.PROPOSAL, 'Complete Proposal')
    ]
    
    contents = []
    for content_type, title in content_types:
        request = ContentRequest(
            content_type=content_type,
            target_audience='Enterprise Clients',
            tone=ContentTone.FORMAL,
            key_points=[
                *sample_market_data['key_trends'],
                *[insight.recommendations[0] for insight in seo_results.values() if insight.recommendations]
            ],
            keywords=['market', 'seo', 'strategy'],
            max_length=2000,
            required_sections=['Executive Summary', title]
        )
        
        topic_analysis = integrated_system['topic_agent'].analyze_topic(request)
        content = integrated_system['writing_agent'].generate_content(request, topic_analysis)
        contents.append(content)
    
    # Verify data consistency
    for content in contents:
        all_content = " ".join(section.content for section in content.sections)
        
        # Market data should be consistent
        if content.content_type == ContentType.MARKET_ANALYSIS:
            assert str(sample_market_data['market_size']) in all_content
            assert all(trend in all_content for trend in sample_market_data['key_trends'])
        
        # SEO insights should be consistent
        if content.content_type == ContentType.TECHNICAL_SPEC:
            assert any(insight.category in all_content for insight in seo_results.values())
        
        # Comprehensive proposal should include both
        if content.content_type == ContentType.PROPOSAL:
            assert str(sample_market_data['market_size']) in all_content
            assert any(insight.category in all_content for insight in seo_results.values()) 