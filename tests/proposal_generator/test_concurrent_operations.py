"""Tests for concurrent component operations."""
import pytest
import asyncio
from typing import List, Dict, Any
from src.proposal_generator.components.content_generator.agents.topic_agent import TopicAnalyzerAgent
from src.proposal_generator.components.content_generator.agents.writing_agent import WritingAgent
from src.proposal_generator.components.content_generator.agents.style_agent import StyleGuideAgent
from src.proposal_generator.components.seo_analyzer.main import SEOAnalyzer
from src.proposal_generator.components.market_analyzer.main import MarketAnalyzer
from src.proposal_generator.components.content_generator.models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone,
    GeneratedContent
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
def sample_websites():
    """Sample website data for concurrent analysis."""
    return [
        {
            'website': 'https://example1.com',
            'competitors': ['https://competitor1.com', 'https://competitor2.com'],
            'industry': 'Technology'
        },
        {
            'website': 'https://example2.com',
            'competitors': ['https://competitor3.com', 'https://competitor4.com'],
            'industry': 'E-commerce'
        },
        {
            'website': 'https://example3.com',
            'competitors': ['https://competitor5.com', 'https://competitor6.com'],
            'industry': 'Healthcare'
        }
    ]

@pytest.fixture
def sample_market_data():
    """Sample market data for concurrent analysis."""
    return [
        {
            'market_size': 1000000000,
            'growth_rate': 0.15,
            'key_trends': ['Cloud Adoption', 'Digital Transformation'],
            'industry': 'Technology'
        },
        {
            'market_size': 500000000,
            'growth_rate': 0.25,
            'key_trends': ['Mobile Commerce', 'Social Shopping'],
            'industry': 'E-commerce'
        },
        {
            'market_size': 750000000,
            'growth_rate': 0.10,
            'key_trends': ['Telemedicine', 'AI Diagnostics'],
            'industry': 'Healthcare'
        }
    ]

async def analyze_website(seo_analyzer: SEOAnalyzer, website_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single website."""
    return {
        'website': website_data['website'],
        'seo_results': seo_analyzer.analyze_seo(
            website_data['website'],
            {'technical': {}, 'content': {}},
            {'backlinks': {}}
        )
    }

async def analyze_market(market_analyzer: MarketAnalyzer, market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single market."""
    results = await market_analyzer.analyze_market({
        'market_data': market_data,
        'competitors': {}
    })
    return {
        'industry': market_data['industry'],
        'market_results': results
    }

async def generate_content(
    topic_agent: TopicAnalyzerAgent,
    writing_agent: WritingAgent,
    style_agent: StyleGuideAgent,
    request: ContentRequest
) -> GeneratedContent:
    """Generate content for a single request."""
    topic_analysis = topic_agent.analyze_topic(request)
    content = writing_agent.generate_content(request, topic_analysis)
    
    # Apply style
    for section in content.sections:
        section.content = style_agent.apply_style_rules(section.content, request.tone)
    
    return content

@pytest.mark.asyncio
async def test_concurrent_seo_analysis(integrated_system, sample_websites):
    """Test concurrent SEO analysis of multiple websites."""
    tasks = [
        analyze_website(integrated_system['seo_analyzer'], website_data)
        for website_data in sample_websites
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(sample_websites)
    for result in results:
        assert 'website' in result
        assert 'seo_results' in result
        assert result['seo_results'] is not None

@pytest.mark.asyncio
async def test_concurrent_market_analysis(integrated_system, sample_market_data):
    """Test concurrent market analysis."""
    tasks = [
        analyze_market(integrated_system['market_analyzer'], market_data)
        for market_data in sample_market_data
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(sample_market_data)
    for result in results:
        assert 'industry' in result
        assert 'market_results' in result
        assert result['market_results'] is not None

@pytest.mark.asyncio
async def test_concurrent_content_generation(integrated_system):
    """Test concurrent content generation."""
    content_requests = [
        ContentRequest(
            content_type=content_type,
            target_audience="Enterprise Clients",
            tone=ContentTone.FORMAL,
            key_points=["Scalability", "Security"],
            keywords=["enterprise", "solution"],
            max_length=2000,
            required_sections=["Executive Summary"]
        )
        for content_type in [
            ContentType.PROPOSAL,
            ContentType.TECHNICAL_SPEC,
            ContentType.MARKET_ANALYSIS
        ]
    ]
    
    tasks = [
        generate_content(
            integrated_system['topic_agent'],
            integrated_system['writing_agent'],
            integrated_system['style_agent'],
            request
        )
        for request in content_requests
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(content_requests)
    for result, request in zip(results, content_requests):
        assert isinstance(result, GeneratedContent)
        assert result.content_type == request.content_type
        assert len(result.sections) > 0

@pytest.mark.asyncio
async def test_mixed_concurrent_operations(integrated_system, sample_websites, sample_market_data):
    """Test mixed concurrent operations across all components."""
    # Create tasks for different operations
    seo_tasks = [
        analyze_website(integrated_system['seo_analyzer'], website_data)
        for website_data in sample_websites
    ]
    
    market_tasks = [
        analyze_market(integrated_system['market_analyzer'], market_data)
        for market_data in sample_market_data
    ]
    
    content_tasks = [
        generate_content(
            integrated_system['topic_agent'],
            integrated_system['writing_agent'],
            integrated_system['style_agent'],
            ContentRequest(
                content_type=ContentType.PROPOSAL,
                target_audience=f"{data['industry']} Clients",
                tone=ContentTone.FORMAL,
                key_points=data['key_trends'],
                keywords=["market", "growth"],
                max_length=2000,
                required_sections=["Executive Summary"]
            )
        )
        for data in sample_market_data
    ]
    
    # Run all tasks concurrently
    all_results = await asyncio.gather(
        *seo_tasks,
        *market_tasks,
        *content_tasks
    )
    
    # Verify results
    seo_results = all_results[:len(seo_tasks)]
    market_results = all_results[len(seo_tasks):len(seo_tasks) + len(market_tasks)]
    content_results = all_results[len(seo_tasks) + len(market_tasks):]
    
    # Check SEO results
    assert len(seo_results) == len(sample_websites)
    for result in seo_results:
        assert 'website' in result
        assert 'seo_results' in result
    
    # Check market results
    assert len(market_results) == len(sample_market_data)
    for result in market_results:
        assert 'industry' in result
        assert 'market_results' in result
    
    # Check content results
    assert len(content_results) == len(sample_market_data)
    for result in content_results:
        assert isinstance(result, GeneratedContent)
        assert len(result.sections) > 0

@pytest.mark.asyncio
async def test_concurrent_competitor_analysis(integrated_system, sample_websites):
    """Test concurrent competitor analysis."""
    async def analyze_competitor(website: str) -> Dict[str, Any]:
        """Analyze a single competitor."""
        seo_results = integrated_system['seo_analyzer'].analyze_seo(
            website,
            {'technical': {}, 'content': {}},
            {'backlinks': {}}
        )
        return {'website': website, 'results': seo_results}
    
    # Gather all competitor websites
    all_competitors = [
        competitor
        for website_data in sample_websites
        for competitor in website_data['competitors']
    ]
    
    # Analyze all competitors concurrently
    tasks = [analyze_competitor(website) for website in all_competitors]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(all_competitors)
    for result in results:
        assert 'website' in result
        assert 'results' in result
        assert result['results'] is not None

@pytest.mark.asyncio
async def test_concurrent_content_updates(integrated_system, sample_market_data):
    """Test concurrent content updates based on real-time data changes."""
    async def update_content(market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update content based on market changes."""
        # Generate initial content
        request = ContentRequest(
            content_type=ContentType.MARKET_ANALYSIS,
            target_audience=f"{market_data['industry']} Clients",
            tone=ContentTone.FORMAL,
            key_points=market_data['key_trends'],
            keywords=["market", "growth"],
            max_length=2000,
            required_sections=["Market Overview"]
        )
        
        initial_content = await generate_content(
            integrated_system['topic_agent'],
            integrated_system['writing_agent'],
            integrated_system['style_agent'],
            request
        )
        
        # Simulate market data update
        updated_market_data = dict(market_data)
        updated_market_data['growth_rate'] += 0.05
        updated_market_data['key_trends'].append("New Trend")
        
        # Generate updated content
        updated_request = ContentRequest(
            content_type=ContentType.MARKET_ANALYSIS,
            target_audience=f"{updated_market_data['industry']} Clients",
            tone=ContentTone.FORMAL,
            key_points=[*updated_market_data['key_trends']],
            keywords=["market", "growth", "trend"],
            max_length=2000,
            required_sections=["Market Overview"]
        )
        
        updated_content = await generate_content(
            integrated_system['topic_agent'],
            integrated_system['writing_agent'],
            integrated_system['style_agent'],
            updated_request
        )
        
        return {
            'industry': market_data['industry'],
            'initial_content': initial_content,
            'updated_content': updated_content
        }
    
    # Update content for all markets concurrently
    tasks = [update_content(data) for data in sample_market_data]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(sample_market_data)
    for result in results:
        assert 'industry' in result
        assert isinstance(result['initial_content'], GeneratedContent)
        assert isinstance(result['updated_content'], GeneratedContent)
        # Verify content was actually updated
        initial_text = " ".join(s.content for s in result['initial_content'].sections)
        updated_text = " ".join(s.content for s in result['updated_content'].sections)
        assert initial_text != updated_text 