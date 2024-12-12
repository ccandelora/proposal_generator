import pytest
import logging
import asyncio

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.fixture
def mock_url():
    """Provide a valid test URL."""
    return 'https://example.com'

@pytest.fixture
def valid_priorities():
    """Valid priority levels for SEO insights."""
    return ['critical', 'high', 'medium', 'low']

@pytest.fixture
def valid_categories():
    """Valid SEO analysis categories."""
    return ['technical_seo', 'content_seo', 'backlinks']

@pytest.fixture
def mock_crew_context():
    """Mock CrewAI context for testing."""
    return {
        'task_id': 'test_task',
        'agent_id': 'test_agent',
        'execution_id': 'test_execution'
    }

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def pytest_collection_modifyitems(items):
    """Add markers to tests based on their categories."""
    for item in items:
        if 'edge_cases' in item.nodeid:
            item.add_marker(pytest.mark.edge_cases)
        if 'test_technical' in item.nodeid:
            item.add_marker(pytest.mark.technical)
        if 'test_content' in item.nodeid:
            item.add_marker(pytest.mark.content)
        if 'test_backlinks' in item.nodeid:
            item.add_marker(pytest.mark.backlinks) 