import pytest
from src.proposal_generator.components.base_agent import BaseAgent

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent."""
    def process(self, data):
        if not data:
            raise ValueError("Empty data")
        return {'result': data}

@pytest.fixture
def agent():
    return TestAgent()

def test_base_agent_initialization(agent):
    assert agent.logger is not None
    assert agent.logger.level == 20  # INFO level

def test_process_implementation(agent):
    test_data = {'test': 'data'}
    result = agent.process(test_data)
    assert result == {'result': test_data}

def test_process_error(agent):
    with pytest.raises(ValueError):
        agent.process({})

def test_handle_error(agent):
    error = ValueError("Test error")
    result = agent._handle_error(error, "test context")
    assert result == {'error': 'Test error'} 