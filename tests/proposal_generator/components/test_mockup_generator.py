import pytest
from pathlib import Path
from src.proposal_generator.components.mockup_generator import MockupGenerator

@pytest.fixture
def generator():
    return MockupGenerator()

def test_mockup_generator_initialization(generator):
    assert generator is not None
    assert generator.logger is not None
    assert isinstance(generator.mockups_dir, Path)

def test_generate_mockup_success(generator):
    test_data = {
        'project': 'Test Project',
        'requirements': ['requirement1', 'requirement2'],
        'page_type': 'homepage'
    }
    
    result = generator.generate_mockup(test_data)
    
    assert result['status'] == 'success'
    assert 'mockup' in result
    assert 'files' in result
    assert 'desktop' in result['files']
    assert 'mobile' in result['files']
    assert result['files']['desktop'].endswith('homepage_mockup.png')
    assert result['files']['mobile'].endswith('homepage_mobile_mockup.png')

def test_generate_mockup_error(generator):
    test_data = None  # This should cause an error
    
    result = generator.generate_mockup(test_data)
    
    assert result['status'] == 'error'
    assert 'message' in result

def test_generate_layout(generator):
    test_data = {'layout': 'test'}
    
    result = generator._generate_layout(test_data)
    
    assert result['type'] == 'layout'
    assert 'sections' in result
    assert isinstance(result['sections'], list)
    assert len(result['sections']) == 3  # header, main, footer

def test_generate_design(generator):
    test_data = {'design': 'test'}
    
    result = generator._generate_design(test_data)
    
    assert result['type'] == 'design'
    assert 'elements' in result
    assert isinstance(result['elements'], list)
    assert any(elem['type'] == 'color_scheme' for elem in result['elements'])

def test_generate_content(generator):
    test_data = {'content': 'test'}
    
    result = generator._generate_content(test_data)
    
    assert result['type'] == 'content'
    assert 'elements' in result
    assert isinstance(result['elements'], list)
    assert any(elem['type'] == 'text' for elem in result['elements'])

def test_get_mockup_files(generator):
    result = generator._get_mockup_files('homepage')
    
    assert 'desktop' in result
    assert 'mobile' in result
    assert result['desktop'].endswith('homepage_mockup.png')
    assert result['mobile'].endswith('homepage_mobile_mockup.png') 