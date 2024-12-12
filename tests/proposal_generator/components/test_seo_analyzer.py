import pytest
from src.proposal_generator.components.seo_analyzer import (
    SEOAnalyzer, SEOInsight, TechnicalSEOAgent, 
    ContentSEOAgent, BacklinkAnalyzerAgent
)

@pytest.fixture
def seo_analyzer():
    return SEOAnalyzer()

@pytest.fixture
def technical_agent():
    return TechnicalSEOAgent()

@pytest.fixture
def content_agent():
    return ContentSEOAgent()

@pytest.fixture
def backlink_agent():
    return BacklinkAnalyzerAgent()

@pytest.fixture
def sample_page_data():
    return {
        'performance': {
            'first_contentful_paint': 1500,
            'largest_contentful_paint': 2000,
            'time_to_first_byte': 200,
            'time_to_interactive': 3000
        },
        'mobile': {
            'has_viewport_meta': True,
            'viewport_config': {'width': 'device-width'},
            'text_size': {'too_small': False},
            'tap_targets': {'too_close': False}
        },
        'meta': {
            'title': {'present': True, 'optimal_length': True},
            'description': {'present': True},
            'robots': {'present': True},
            'canonical': {'present': True}
        },
        'keywords': {
            'primary': {'present': True, 'density': 2.0},
            'secondary': ['keyword1', 'keyword2'],
            'density': {'overall': 2.5},
            'placement': {'in_title': True, 'in_headings': True}
        },
        'structure': {
            'headings': {'has_h1': True, 'multiple_h1': False},
            'paragraphs': {'avg_length': 150},
            'lists': {'present': True},
            'images': {'has_alt_text': True}
        },
        'quality': {
            'readability': {'score': 55},
            'engagement': {'bounce_rate': 45},
            'uniqueness': {'score': 95},
            'freshness': {'days_since_update': 30}
        }
    }

@pytest.fixture
def sample_backlink_data():
    return {
        'profile': {
            'total': 500,
            'referring_domains': 200,
            'growth': {'trend': 1},
            'anchor_text': {'branded': 0.6, 'generic': 0.4}
        },
        'quality': {
            'authority': {'high_authority': 0.3},
            'spam_score': {'average': 15},
            'follow_ratio': {'nofollow': 0.3},
            'relevance': {'score': 0.8}
        },
        'competitors': {
            'link_gap': {'total': 800},
            'domain_overlap': {'percentage': 25},
            'opportunities': {'count': 100},
            'industry_average': {'percentile': 60}
        }
    }

def test_seo_analyzer_initialization(seo_analyzer):
    assert seo_analyzer is not None
    assert isinstance(seo_analyzer.technical_agent, TechnicalSEOAgent)
    assert isinstance(seo_analyzer.content_agent, ContentSEOAgent)
    assert isinstance(seo_analyzer.backlink_agent, BacklinkAnalyzerAgent)

def test_seo_insight_dataclass():
    insight = SEOInsight(
        category='test',
        score=0.8,
        findings=[{'issue': 'test'}],
        recommendations=['fix it'],
        priority='high',
        metadata={'key': 'value'}
    )
    assert insight.category == 'test'
    assert insight.score == 0.8
    assert len(insight.findings) == 1
    assert len(insight.recommendations) == 1
    assert insight.priority == 'high'
    assert insight.metadata == {'key': 'value'}

def test_technical_seo_analysis(technical_agent, sample_page_data):
    result = technical_agent.analyze_technical_seo('https://example.com', sample_page_data)
    assert isinstance(result, SEOInsight)
    assert result.category == 'technical_seo'
    assert result.score > 0
    assert len(result.findings) >= 0
    assert len(result.recommendations) >= 0
    assert result.priority in ['critical', 'high', 'medium', 'low', 'unknown']

def test_content_seo_analysis(content_agent, sample_page_data):
    result = content_agent.analyze_content_seo('https://example.com', sample_page_data)
    assert isinstance(result, SEOInsight)
    assert result.category == 'content_seo'
    assert result.score > 0
    assert len(result.findings) >= 0
    assert len(result.recommendations) >= 0
    assert result.priority in ['critical', 'high', 'medium', 'low', 'unknown']

def test_backlink_analysis(backlink_agent, sample_backlink_data):
    result = backlink_agent.analyze_backlinks('https://example.com', sample_backlink_data)
    assert isinstance(result, SEOInsight)
    assert result.category == 'backlinks'
    assert result.score > 0
    assert len(result.findings) >= 0
    assert len(result.recommendations) >= 0
    assert result.priority in ['critical', 'high', 'medium', 'low', 'unknown']

def test_full_seo_analysis(seo_analyzer, sample_page_data, sample_backlink_data):
    result = seo_analyzer.analyze_seo(
        'https://example.com',
        sample_page_data,
        sample_backlink_data
    )
    assert isinstance(result, dict)
    assert 'technical' in result
    assert 'content' in result
    assert 'backlinks' in result
    assert all(isinstance(insight, SEOInsight) for insight in result.values())

def test_seo_analysis_with_empty_data(seo_analyzer):
    result = seo_analyzer.analyze_seo('https://example.com', {}, {})
    assert isinstance(result, dict)
    assert all(insight.score == 0.0 for insight in result.values())
    assert all(insight.priority == 'unknown' for insight in result.values())

def test_seo_analysis_invalid_url(seo_analyzer, sample_page_data, sample_backlink_data):
    with pytest.raises(ValueError, match="Invalid URL"):
        seo_analyzer.analyze_seo('', sample_page_data, sample_backlink_data)
    
    with pytest.raises(ValueError, match="Invalid URL format"):
        seo_analyzer.analyze_seo('example.com', sample_page_data, sample_backlink_data) 

def test_technical_seo_empty_data(technical_agent):
    result = technical_agent.analyze_technical_seo('https://example.com', {})
    assert result.score == 0.0
    assert result.priority == 'unknown'
    assert not result.findings
    assert not result.recommendations

def test_technical_seo_error_handling(technical_agent):
    result = technical_agent.analyze_technical_seo('https://example.com', None)
    assert result.score == 0.0
    assert result.priority == 'unknown'
    assert not result.findings

def test_analyze_page_speed(technical_agent, sample_page_data):
    result = technical_agent._analyze_page_speed(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_page_speed_error(technical_agent):
    result = technical_agent._analyze_page_speed(None)
    assert result['score'] == 0.0
    assert not result['findings']
    assert not result['metrics']

def test_analyze_mobile_friendliness(technical_agent, sample_page_data):
    result = technical_agent._analyze_mobile_friendliness(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_mobile_friendliness_error(technical_agent):
    result = technical_agent._analyze_mobile_friendliness(None)
    assert result['score'] == 0.0
    assert not result['findings']
    assert not result['metrics']

def test_analyze_technical_elements(technical_agent, sample_page_data):
    result = technical_agent._analyze_technical_elements(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'elements' in result
    assert 'score' in result

def test_calculate_technical_score(technical_agent):
    score = technical_agent._calculate_technical_score(
        {'score': 0.8},
        {'score': 0.7},
        {'score': 0.9}
    )
    assert 0 <= score <= 1

def test_calculate_speed_score(technical_agent):
    score = technical_agent._calculate_speed_score({
        'fcp': 1500,
        'lcp': 2000
    })
    assert 0 <= score <= 1

def test_calculate_mobile_score(technical_agent):
    score = technical_agent._calculate_mobile_score({
        'has_viewport': True,
        'text_size': {'too_small': False},
        'tap_targets': {'too_close': False}
    })
    assert 0 <= score <= 1

def test_determine_priority(technical_agent):
    priority = technical_agent._determine_priority(0.8, 0.7, 0.9)
    assert priority in ['critical', 'high', 'medium', 'low']

def test_generate_technical_recommendations(technical_agent):
    recommendations = technical_agent._generate_technical_recommendations(
        {'findings': [{'impact': 'critical', 'recommendation': 'Fix this'}]},
        {'findings': [{'impact': 'high', 'recommendation': 'Fix that'}]},
        {'findings': [{'impact': 'low', 'recommendation': 'Optional fix'}]}
    )
    assert len(recommendations) == 2  # Only critical and high impact

def test_content_seo_empty_data(content_agent):
    result = content_agent.analyze_content_seo('https://example.com', {})
    assert result.score == 0.0
    assert result.priority == 'unknown'
    assert not result.findings

def test_analyze_keyword_usage(content_agent, sample_page_data):
    result = content_agent._analyze_keyword_usage(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_content_structure(content_agent, sample_page_data):
    result = content_agent._analyze_content_structure(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_content_quality(content_agent, sample_page_data):
    result = content_agent._analyze_content_quality(sample_page_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_backlink_empty_data(backlink_agent):
    result = backlink_agent.analyze_backlinks('https://example.com', {})
    assert result.score == 0.0
    assert result.priority == 'unknown'
    assert not result.findings

def test_analyze_backlink_profile(backlink_agent, sample_backlink_data):
    result = backlink_agent._analyze_backlink_profile(sample_backlink_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_link_quality(backlink_agent, sample_backlink_data):
    result = backlink_agent._analyze_link_quality(sample_backlink_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_analyze_competitor_backlinks(backlink_agent, sample_backlink_data):
    result = backlink_agent._analyze_competitor_backlinks(sample_backlink_data)
    assert isinstance(result, dict)
    assert 'findings' in result
    assert 'metrics' in result
    assert 'score' in result

def test_seo_analyzer_error_handling(seo_analyzer):
    with pytest.raises(ValueError):
        seo_analyzer.analyze_seo(None, {}, {})

def test_technical_calculation_error(technical_agent):
    score = technical_agent._calculate_technical_score(None, None, None)
    assert score == 0.0

def test_content_calculation_error(content_agent):
    score = content_agent._calculate_content_score(None, None, None)
    assert score == 0.0

def test_backlink_calculation_error(backlink_agent):
    score = backlink_agent._calculate_backlink_score(None, None, None)
    assert score == 0.0