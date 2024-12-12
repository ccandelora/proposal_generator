import pytest
from src.proposal_generator import (
    MockupGenerator,
    SEOAnalyzer,
    MarketAnalyzer,
    SEOScreenshotter
)
from src.proposal_generator.crew import ProposalGenerator

@pytest.fixture
def sample_data():
    return {
        'website': 'https://example.com',
        'project_type': 'website',
        'requirements': ['responsive', 'seo-friendly'],
        'competitors': ['https://competitor1.com', 'https://competitor2.com']
    }

@pytest.mark.asyncio
async def test_full_proposal_generation(sample_data):
    # Initialize all components
    mockup_gen = MockupGenerator()
    seo_analyzer = SEOAnalyzer()
    market_analyzer = MarketAnalyzer()
    screenshotter = SEOScreenshotter()
    
    # Create proposal generator
    generator = ProposalGenerator()
    
    # Test mockup generation
    mockup_result = mockup_gen.generate_mockup(sample_data)
    assert mockup_result['status'] == 'success'
    
    # Test SEO analysis
    seo_result = seo_analyzer.analyze_seo(
        sample_data['website'],
        {'technical': {}},
        {'backlinks': {}}
    )
    assert isinstance(seo_result, dict)
    assert 'technical' in seo_result
    
    # Test market analysis
    market_result = await market_analyzer.analyze_market(sample_data)
    assert market_result['status'] == 'success'
    
    # Test screenshot analysis
    screenshot_result = screenshotter.process({
        'website': sample_data['website'],
        'competitors': sample_data['competitors']
    })
    assert 'error' not in screenshot_result

def test_component_initialization():
    # Test that all components can be initialized
    assert MockupGenerator()
    assert SEOAnalyzer()
    assert MarketAnalyzer()
    assert SEOScreenshotter()
    assert ProposalGenerator()

@pytest.mark.asyncio
async def test_crew_execution(sample_data):
    generator = ProposalGenerator()
    result = await generator.crew.kickoff()
    assert result is not None

def test_error_handling_integration(sample_data):
    # Test error handling across components
    mockup_gen = MockupGenerator()
    seo_analyzer = SEOAnalyzer()
    
    # Test with invalid data
    mockup_result = mockup_gen.generate_mockup({})
    assert mockup_result['status'] == 'error'
    
    # Test with invalid URL
    with pytest.raises(ValueError):
        seo_analyzer.analyze_seo('', {}, {})

@pytest.mark.asyncio
async def test_concurrent_execution(sample_data):
    # Test that components can run concurrently
    market_analyzer = MarketAnalyzer()
    screenshotter = SEOScreenshotter()
    
    # Run analyses concurrently
    results = await asyncio.gather(
        market_analyzer.analyze_market(sample_data),
        screenshotter.process({'website': sample_data['website']})
    )
    
    assert all(isinstance(result, dict) for result in results) 