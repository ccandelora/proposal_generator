import pytest
from src.proposal_generator.components.utils import Tool

def dummy_function(x):
    return x * 2

@pytest.fixture
def sample_tool():
    return Tool(
        name="test_tool",
        func=dummy_function,
        description="Test tool",
        return_direct=False
    )

def test_tool_initialization(sample_tool):
    assert sample_tool.name == "test_tool"
    assert sample_tool.description == "Test tool"
    assert sample_tool.return_direct is False

def test_tool_call(sample_tool):
    result = sample_tool(5)
    assert result == 10

def test_tool_to_dict(sample_tool):
    tool_dict = sample_tool.to_dict()
    assert tool_dict == {
        'name': 'test_tool',
        'description': 'Test tool',
        'return_direct': False
    }

def test_tool_with_different_return_direct():
    tool = Tool(
        name="direct_tool",
        func=dummy_function,
        description="Direct return tool",
        return_direct=True
    )
    assert tool.return_direct is True 