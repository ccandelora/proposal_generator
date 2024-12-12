import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from src.cli import main, get_boolean_input

@pytest.fixture
def sample_client_brief():
    return {
        "client_name": "Test Client",
        "industry": "Technology",
        "client_website": "https://example.com",
        "project_type": "Website",
        "target_audience": "B2B",
        "description": "Test project",
        "features": ["feature1", "feature2"],
        "timeline": "3 months",
        "budget_range": "$10k-$20k"
    }

def test_get_boolean_input():
    with patch('builtins.input', side_effect=['y']):
        assert get_boolean_input("Test prompt") is True
    
    with patch('builtins.input', side_effect=['n']):
        assert get_boolean_input("Test prompt") is False
    
    with patch('builtins.input', side_effect=['invalid', 'y']):
        assert get_boolean_input("Test prompt") is True

@patch('argparse.ArgumentParser.parse_args')
@patch('json.load')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
@patch('src.proposal_generator.generator.ProposalGenerator')
def test_main_with_input_file(mock_generator, mock_makedirs, mock_open, mock_json_load, mock_parse_args, sample_client_brief):
    # Setup mocks
    mock_args = MagicMock()
    mock_args.input = 'input.json'
    mock_args.template = 'default'
    mock_args.output_dir = 'output'
    mock_parse_args.return_value = mock_args
    
    mock_json_load.return_value = sample_client_brief
    
    mock_generator_instance = MagicMock()
    mock_generator_instance.create_proposal.return_value = {
        'proposal': 'Test proposal',
        'mockups': {'homepage': 'mockup.png'}
    }
    mock_generator.return_value = mock_generator_instance
    
    # Run main
    main()
    
    # Verify
    mock_open.assert_called()
    mock_makedirs.assert_called_with('output', exist_ok=True)
    mock_generator_instance.create_proposal.assert_called_with(sample_client_brief)

@patch('argparse.ArgumentParser.parse_args')
@patch('builtins.input')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
@patch('src.proposal_generator.generator.ProposalGenerator')
def test_main_interactive_mode(mock_generator, mock_makedirs, mock_open, mock_input, mock_parse_args):
    # Setup mocks
    mock_args = MagicMock()
    mock_args.input = None
    mock_args.template = 'default'
    mock_args.output_dir = 'output'
    mock_parse_args.return_value = mock_args
    
    mock_input.side_effect = [
        'Test Client',  # client_name
        'Technology',   # industry
        'example.com',  # website
        'Website',      # project_type
        'B2B',         # target_audience
        'Description', # description
        'feat1,feat2', # features
        '3 months',    # timeline
        '$10k',        # budget
        'y',           # website_analysis
        'n',           # competitor_analysis
        'y',           # seo_analysis
        'n',           # performance_analysis
        'y',           # design_mockups
        'n'            # sentiment_analysis
    ]
    
    mock_generator_instance = MagicMock()
    mock_generator_instance.create_proposal.return_value = {
        'proposal': 'Test proposal',
        'mockups': None
    }
    mock_generator.return_value = mock_generator_instance
    
    # Run main
    main()
    
    # Verify
    mock_makedirs.assert_called_with('output', exist_ok=True)
    mock_generator_instance.create_proposal.assert_called()
    assert mock_open().write.called

@patch('argparse.ArgumentParser.parse_args')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
@patch('src.proposal_generator.generator.ProposalGenerator')
def test_main_pdf_generation_error(mock_generator, mock_makedirs, mock_open, mock_parse_args, sample_client_brief):
    # Setup mocks
    mock_args = MagicMock()
    mock_args.input = 'input.json'
    mock_args.template = 'default'
    mock_args.output_dir = 'output'
    mock_parse_args.return_value = mock_args
    
    mock_generator_instance = MagicMock()
    mock_generator_instance.create_proposal.return_value = {'proposal': 'Test proposal'}
    mock_generator_instance.generate_pdf.side_effect = Exception('PDF error')
    mock_generator.return_value = mock_generator_instance
    
    # Run main
    with patch('builtins.print') as mock_print:
        main()
    
    # Verify error handling
    mock_print.assert_any_call('Could not generate PDF: PDF error') 