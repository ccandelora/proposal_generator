import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from crewai import Process
import asyncio
from src.proposal_generator.components.market_analyzer import MarketAnalyzer

@pytest.fixture
def market_analyzer():
    return MarketAnalyzer()

@pytest.fixture
def sample_market_data():
    return {
        'competitors': ['comp1.com', 'comp2.com'],
        'industry': 'Technology',
        'region': 'North America',
        'target_market': 'B2B',
        'market_size': 1000000,
        'growth_rate': 15
    }

@pytest.mark.asyncio
async def test_market_analyzer_initialization(market_analyzer):
    assert market_analyzer.trend_analyzer is not None
    assert market_analyzer.demographic_analyzer is not None
    assert market_analyzer.opportunity_analyzer is not None
    assert market_analyzer.competition_analyzer is not None

@pytest.mark.asyncio
async def test_analyze_market_success(market_analyzer, sample_market_data):
    with patch('src.proposal_generator.components.market_analyzer.Task') as MockTask:
        mock_task = MagicMock()
        mock_task.description = "Test task"
        mock_task.agent = None
        mock_task.expected_output = "Analysis results"
        mock_task.context = []
        mock_task.id = "test_task"
        MockTask.return_value = mock_task

        with patch('src.proposal_generator.components.market_analyzer.Crew') as MockCrew:
            mock_crew = MagicMock()
            mock_result = {
                'test_task': {
                    'trends': {'growth_rate': 15},
                    'demographics': {'primary_age': '25-34'},
                    'opportunities': ['opportunity1', 'opportunity2'],
                    'competition': {'market_leaders': ['comp1']}
                }
            }
            # Create an async mock for kickoff
            async def mock_kickoff():
                return mock_result
            mock_crew.kickoff = mock_kickoff
            MockCrew.return_value = mock_crew

            result = await market_analyzer.analyze_market(sample_market_data)

            assert result['status'] == 'success'
            assert 'analysis' in result
            assert 'timestamp' in result
            assert isinstance(result['timestamp'], str)
            
            # Verify crew was created with correct parameters
            MockCrew.assert_called_once()
            crew_call_kwargs = MockCrew.call_args[1]
            assert len(crew_call_kwargs['tasks']) == 4
            assert crew_call_kwargs['process'] == Process.sequential

@pytest.mark.asyncio
async def test_analyze_market_error(market_analyzer):
    with patch('src.proposal_generator.components.market_analyzer.Task') as MockTask:
        mock_task = MagicMock()
        mock_task.description = "Test task"
        mock_task.agent = None
        mock_task.expected_output = "Analysis results"
        mock_task.context = []
        MockTask.return_value = mock_task

        with patch('src.proposal_generator.components.market_analyzer.Crew') as MockCrew:
            async def mock_kickoff():
                raise Exception("Test error")
            mock_crew = MagicMock()
            mock_crew.kickoff = mock_kickoff
            MockCrew.return_value = mock_crew

            result = await market_analyzer.analyze_market({})

            assert result['status'] == 'error'
            assert 'message' in result
            assert 'timestamp' in result
            assert isinstance(result['timestamp'], str)

@pytest.mark.asyncio
async def test_analyze_market_empty_data(market_analyzer):
    with patch('src.proposal_generator.components.market_analyzer.Task') as MockTask:
        mock_task = MagicMock()
        mock_task.description = "Test task"
        mock_task.agent = None
        mock_task.expected_output = "Analysis results"
        mock_task.context = []
        mock_task.id = "test_task"
        MockTask.return_value = mock_task

        with patch('src.proposal_generator.components.market_analyzer.Crew') as MockCrew:
            mock_crew = MagicMock()
            # Create an async mock for kickoff
            async def mock_kickoff():
                return {'test_task': {}}
            mock_crew.kickoff = mock_kickoff
            MockCrew.return_value = mock_crew

            result = await market_analyzer.analyze_market({})

            assert result['status'] == 'success'
            assert 'analysis' in result
            assert 'timestamp' in result
            assert isinstance(result['timestamp'], str) 