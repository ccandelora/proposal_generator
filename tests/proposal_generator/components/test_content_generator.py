"""Tests for the content generator module."""

import pytest
from src.proposal_generator.components.content_generator import ContentGenerator

@pytest.fixture
def content_generator():
    return ContentGenerator()

@pytest.fixture
def sample_data():
    return {
        'client': {
            'name': 'Test Client',
            'specialties': ['Web Development', 'Mobile Apps'],
            'target_audience': ['Small Business', 'Enterprise'],
            'unique_selling_points': ['Quality', 'Innovation', 'Experience']
        },
        'market_analysis': {
            'trends': ['Digital Transformation', 'Cloud Computing'],
            'opportunities': ['Market Growth', 'New Technologies'],
            'challenges': ['Competition', 'Talent Acquisition']
        },
        'competitors': [
            {
                'name': 'Competitor 1',
                'market_share': 0.3,
                'strengths': ['Brand Recognition']
            }
        ]
    }

def test_content_generator_initialization(content_generator):
    """Test content generator initialization."""
    assert content_generator is not None
    assert content_generator.logger is not None

def test_generate_executive_summary_success(content_generator, sample_data):
    """Test successful executive summary generation."""
    result = content_generator.generate_executive_summary(sample_data)
    assert 'content' in result
    assert 'key_points' in result
    assert isinstance(result['key_points'], list)
    assert 'Test Client' in result['content']
    assert 'Web Development' in result['content']

def test_generate_executive_summary_invalid_data(content_generator):
    """Test executive summary generation with invalid data."""
    with pytest.raises(ValueError, match="Invalid input data"):
        content_generator.generate_executive_summary({})

def test_generate_executive_summary_invalid_client(content_generator):
    """Test executive summary generation with invalid client data."""
    with pytest.raises(ValueError, match="Invalid client data"):
        content_generator.generate_executive_summary({'client': 'invalid'})

def test_generate_market_overview_success(content_generator, sample_data):
    """Test successful market overview generation."""
    result = content_generator.generate_market_overview(sample_data)
    assert 'trends' in result
    assert 'opportunities' in result
    assert 'challenges' in result
    assert isinstance(result['trends'], list)
    assert isinstance(result['opportunities'], list)
    assert isinstance(result['challenges'], list)

def test_generate_market_overview_invalid_data(content_generator):
    """Test market overview generation with invalid data."""
    with pytest.raises(ValueError, match="Invalid market data"):
        content_generator.generate_market_overview({})

def test_generate_competitive_analysis_success(content_generator, sample_data):
    """Test successful competitive analysis generation."""
    result = content_generator.generate_competitive_analysis(sample_data)
    assert 'positioning' in result
    assert 'differentiators' in result
    assert 'recommendations' in result
    assert isinstance(result['differentiators'], list)
    assert isinstance(result['recommendations'], list)

def test_generate_competitive_analysis_invalid_data(content_generator):
    """Test competitive analysis generation with invalid data."""
    with pytest.raises(ValueError, match="Invalid competitor data"):
        content_generator.generate_competitive_analysis({})

def test_generate_solution_proposal_success(content_generator, sample_data):
    """Test successful solution proposal generation."""
    result = content_generator.generate_solution_proposal(sample_data)
    assert 'approach' in result
    assert 'benefits' in result
    assert 'timeline' in result
    assert isinstance(result['benefits'], list)
    assert isinstance(result['timeline'], list)

def test_generate_solution_proposal_invalid_data(content_generator):
    """Test solution proposal generation with invalid data."""
    with pytest.raises(ValueError, match="Invalid input data"):
        content_generator.generate_solution_proposal({})

def test_generate_technical_specifications_success(content_generator, sample_data):
    """Test successful technical specifications generation."""
    result = content_generator.generate_technical_specifications(sample_data)
    assert 'architecture' in result
    assert 'features' in result
    assert 'technologies' in result
    assert isinstance(result['features'], list)
    assert isinstance(result['technologies'], dict)

def test_generate_implementation_plan_success(content_generator, sample_data):
    """Test successful implementation plan generation."""
    result = content_generator.generate_implementation_plan(sample_data)
    assert 'phases' in result
    assert 'milestones' in result
    assert 'resources' in result
    assert isinstance(result['phases'], list)
    assert isinstance(result['milestones'], list)

def test_generate_pricing_model_success(content_generator, sample_data):
    """Test successful pricing model generation."""
    result = content_generator.generate_pricing_model(sample_data)
    assert 'packages' in result
    assert 'breakdown' in result
    assert 'terms' in result
    assert isinstance(result['packages'], list)
    assert isinstance(result['breakdown'], dict)
    assert isinstance(result['terms'], dict)

def test_generate_with_template_success(content_generator, sample_data):
    """Test successful template-based generation."""
    template = {
        'sections': ['executive_summary', 'market_overview'],
        'placeholders': {}
    }
    result = content_generator.generate_with_template(sample_data, template)
    assert 'executive_summary' in result
    assert 'market_overview' in result

def test_extract_key_points(content_generator, sample_data):
    """Test key points extraction."""
    points = content_generator._extract_key_points(sample_data)
    assert isinstance(points, list)
    assert len(points) <= 5  # Should return top 5 points
    assert 'Quality' in points

def test_analyze_market_position(content_generator, sample_data):
    """Test market position analysis."""
    position = content_generator._analyze_market_position(sample_data)
    assert isinstance(position, dict)
    assert 'market_share' in position
    assert 'growth_potential' in position

def test_identify_differentiators(content_generator, sample_data):
    """Test differentiator identification."""
    differentiators = content_generator._identify_differentiators(sample_data)
    assert isinstance(differentiators, list)
    assert 'Quality' in differentiators

def test_design_architecture(content_generator, sample_data):
    """Test architecture design."""
    architecture = content_generator._design_architecture(sample_data)
    assert isinstance(architecture, dict)
    assert 'type' in architecture
    assert 'components' in architecture
    assert 'infrastructure' in architecture

def test_specify_features(content_generator, sample_data):
    """Test feature specification."""
    features = content_generator._specify_features(sample_data)
    assert isinstance(features, list)
    assert len(features) > 0
    assert all('name' in feature for feature in features)
    assert all('priority' in feature for feature in features)

def test_select_technologies(content_generator, sample_data):
    """Test technology selection."""
    technologies = content_generator._select_technologies(sample_data)
    assert isinstance(technologies, dict)
    assert 'frontend' in technologies
    assert 'backend' in technologies
    assert 'infrastructure' in technologies

def test_define_phases(content_generator, sample_data):
    """Test phase definition."""
    phases = content_generator._define_phases(sample_data)
    assert isinstance(phases, list)
    assert len(phases) > 0
    assert all('name' in phase for phase in phases)
    assert all('duration' in phase for phase in phases)
    assert all('deliverables' in phase for phase in phases)

def test_set_milestones(content_generator, sample_data):
    """Test milestone setting."""
    milestones = content_generator._set_milestones(sample_data)
    assert isinstance(milestones, list)
    assert len(milestones) > 0
    assert all('name' in milestone for milestone in milestones)
    assert all('timeline' in milestone for milestone in milestones)
    assert all('criteria' in milestone for milestone in milestones)

def test_allocate_resources(content_generator, sample_data):
    """Test resource allocation."""
    resources = content_generator._allocate_resources(sample_data)
    assert isinstance(resources, list)
    assert len(resources) > 0
    assert all('role' in resource for resource in resources)
    assert all('allocation' in resource for resource in resources)
    assert all('duration' in resource for resource in resources)

def test_create_packages(content_generator, sample_data):
    """Test package creation."""
    packages = content_generator._create_packages(sample_data)
    assert isinstance(packages, list)
    assert len(packages) > 0
    assert all('name' in package for package in packages)
    assert all('price' in package for package in packages)
    assert all('features' in package for package in packages)

def test_create_cost_breakdown(content_generator, sample_data):
    """Test cost breakdown creation."""
    breakdown = content_generator._create_cost_breakdown(sample_data)
    assert isinstance(breakdown, dict)
    assert 'development' in breakdown
    assert 'testing' in breakdown
    assert 'deployment' in breakdown
    assert 'support' in breakdown

def test_define_payment_terms(content_generator, sample_data):
    """Test payment terms definition."""
    terms = content_generator._define_payment_terms(sample_data)
    assert isinstance(terms, dict)
    assert 'schedule' in terms
    assert 'installments' in terms
    assert 'upfront_percentage' in terms

def test_generate_custom_section(content_generator, sample_data):
    """Test custom section generation."""
    section = "custom_section"
    placeholders = {"key": "value"}
    result = content_generator._generate_custom_section(section, placeholders)
    assert isinstance(result, dict)
    assert 'title' in result
    assert 'content' in result
    assert 'placeholders' in result
    assert result['placeholders'] == placeholders 