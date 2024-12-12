"""Tests for the main module."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from src.proposal_generator.main import run, train, replay, test

@pytest.fixture
def mock_proposal_generator():
    with patch('src.proposal_generator.main.ProposalGenerator') as mock:
        mock_crew = MagicMock()
        mock_instance = MagicMock()
        mock_instance.crew.return_value = mock_crew
        mock.return_value = mock_instance
        yield mock

def test_run_success(mock_proposal_generator):
    """Test successful run execution."""
    run()
    
    # Verify ProposalGenerator was instantiated
    mock_proposal_generator.assert_called_once()
    
    # Verify crew was created
    mock_instance = mock_proposal_generator.return_value
    mock_instance.crew.assert_called_once()
    
    # Verify kickoff was called with correct inputs
    mock_crew = mock_instance.crew.return_value
    mock_crew.kickoff.assert_called_once_with(inputs={'topic': 'AI LLMs'})

def test_train_success(mock_proposal_generator):
    """Test successful train execution."""
    # Mock sys.argv
    with patch.object(sys, 'argv', ['script.py', '5', 'test.json']):
        train()
        
        # Verify ProposalGenerator was instantiated
        mock_proposal_generator.assert_called_once()
        
        # Verify crew was created
        mock_instance = mock_proposal_generator.return_value
        mock_instance.crew.assert_called_once()
        
        # Verify train was called with correct parameters
        mock_crew = mock_instance.crew.return_value
        mock_crew.train.assert_called_once_with(
            n_iterations=5,
            filename='test.json',
            inputs={'topic': 'AI LLMs'}
        )

def test_train_error(mock_proposal_generator):
    """Test train execution with error."""
    # Mock sys.argv with invalid values
    with patch.object(sys, 'argv', ['script.py']):
        with pytest.raises(Exception) as exc_info:
            train()
        assert "An error occurred while training the crew" in str(exc_info.value)

def test_replay_success(mock_proposal_generator):
    """Test successful replay execution."""
    # Mock sys.argv
    with patch.object(sys, 'argv', ['script.py', 'task_123']):
        replay()
        
        # Verify ProposalGenerator was instantiated
        mock_proposal_generator.assert_called_once()
        
        # Verify crew was created
        mock_instance = mock_proposal_generator.return_value
        mock_instance.crew.assert_called_once()
        
        # Verify replay was called with correct task_id
        mock_crew = mock_instance.crew.return_value
        mock_crew.replay.assert_called_once_with(task_id='task_123')

def test_replay_error(mock_proposal_generator):
    """Test replay execution with error."""
    # Mock sys.argv with missing task_id
    with patch.object(sys, 'argv', ['script.py']):
        with pytest.raises(Exception) as exc_info:
            replay()
        assert "An error occurred while replaying the crew" in str(exc_info.value)

def test_test_success(mock_proposal_generator):
    """Test successful test execution."""
    # Mock sys.argv
    with patch.object(sys, 'argv', ['script.py', '3', 'gpt-4']):
        test()
        
        # Verify ProposalGenerator was instantiated
        mock_proposal_generator.assert_called_once()
        
        # Verify crew was created
        mock_instance = mock_proposal_generator.return_value
        mock_instance.crew.assert_called_once()
        
        # Verify test was called with correct parameters
        mock_crew = mock_instance.crew.return_value
        mock_crew.test.assert_called_once_with(
            n_iterations=3,
            openai_model_name='gpt-4',
            inputs={'topic': 'AI LLMs'}
        )

def test_test_error(mock_proposal_generator):
    """Test test execution with error."""
    # Mock sys.argv with invalid values
    with patch.object(sys, 'argv', ['script.py']):
        with pytest.raises(Exception) as exc_info:
            test()
        assert "An error occurred while replaying the crew" in str(exc_info.value)

def test_run_with_crew_error(mock_proposal_generator):
    """Test run execution when crew raises an error."""
    mock_instance = mock_proposal_generator.return_value
    mock_crew = mock_instance.crew.return_value
    mock_crew.kickoff.side_effect = Exception("Crew error")
    
    with pytest.raises(Exception):
        run()

def test_train_with_crew_error(mock_proposal_generator):
    """Test train execution when crew raises an error."""
    mock_instance = mock_proposal_generator.return_value
    mock_crew = mock_instance.crew.return_value
    mock_crew.train.side_effect = Exception("Training error")
    
    with patch.object(sys, 'argv', ['script.py', '5', 'test.json']):
        with pytest.raises(Exception) as exc_info:
            train()
        assert "An error occurred while training the crew" in str(exc_info.value)

def test_replay_with_crew_error(mock_proposal_generator):
    """Test replay execution when crew raises an error."""
    mock_instance = mock_proposal_generator.return_value
    mock_crew = mock_instance.crew.return_value
    mock_crew.replay.side_effect = Exception("Replay error")
    
    with patch.object(sys, 'argv', ['script.py', 'task_123']):
        with pytest.raises(Exception) as exc_info:
            replay()
        assert "An error occurred while replaying the crew" in str(exc_info.value)

def test_test_with_crew_error(mock_proposal_generator):
    """Test test execution when crew raises an error."""
    mock_instance = mock_proposal_generator.return_value
    mock_crew = mock_instance.crew.return_value
    mock_crew.test.side_effect = Exception("Test error")
    
    with patch.object(sys, 'argv', ['script.py', '3', 'gpt-4']):
        with pytest.raises(Exception) as exc_info:
            test()
        assert "An error occurred while replaying the crew" in str(exc_info.value) 