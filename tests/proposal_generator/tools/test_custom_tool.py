"""Tests for the custom tool module."""

import pytest
from src.proposal_generator.tools.custom_tool import MyCustomTool, MyCustomToolInput

@pytest.fixture
def custom_tool():
    return MyCustomTool()

def test_custom_tool_initialization(custom_tool):
    """Test custom tool initialization."""
    assert custom_tool is not None
    assert custom_tool.name == "Name of my tool"
    assert isinstance(custom_tool.description, str)
    assert len(custom_tool.description) > 0
    assert custom_tool.args_schema == MyCustomToolInput

def test_custom_tool_input_schema():
    """Test custom tool input schema."""
    # Test valid input
    valid_input = MyCustomToolInput(argument="test argument")
    assert valid_input.argument == "test argument"

    # Test missing argument
    with pytest.raises(ValueError):
        MyCustomToolInput()

def test_custom_tool_run(custom_tool):
    """Test custom tool run method."""
    result = custom_tool._run(argument="test argument")
    assert isinstance(result, str)
    assert len(result) > 0

def test_custom_tool_run_with_schema(custom_tool):
    """Test custom tool run with input schema."""
    input_data = MyCustomToolInput(argument="test argument")
    result = custom_tool._run(argument=input_data.argument)
    assert isinstance(result, str)
    assert len(result) > 0

def test_custom_tool_description():
    """Test custom tool description format."""
    tool = MyCustomTool()
    assert isinstance(tool.description, str)
    assert len(tool.description) > 0
    # Description should be clear and helpful
    assert len(tool.description.split()) > 5  # At least 5 words

def test_custom_tool_name():
    """Test custom tool name format."""
    tool = MyCustomTool()
    assert isinstance(tool.name, str)
    assert len(tool.name) > 0
    # Name should be concise
    assert len(tool.name.split()) <= 5  # At most 5 words 