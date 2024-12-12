import asyncio
import logging
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.proposal_generator.config import Config
from src.proposal_generator.components.search.google_search import GoogleSearchClient
from src.proposal_generator.components.search.search_results_manager import SearchResultsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search():
    try:
        # Initialize config and clients
        config = Config()
        search_client = GoogleSearchClient(config)
        search_manager = SearchResultsManager(search_client)
        
        # Test search query
        query = "best law firms in California 2024"
        
        logger.info(f"Testing search with query: {query}")
        
        # Get API info
        api_info = search_client.get_api_info()
        logger.info(f"API Configuration: {api_info}")
        
        # Perform search and process results
        results = await search_manager.search_and_process(query, num_results=5)
        
        # Display results
        logger.info(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. {result.title}")
            logger.info(f"URL: {result.url}")
            logger.info(f"Relevance Score: {result.relevance_score}")
            logger.info(f"Content Preview: {result.content[:200]}...")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search()) 