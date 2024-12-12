import asyncio
import logging
from langchain_core.messages import HumanMessage
from src.proposal_generator.config import Config, get_gemini_llm
from src.proposal_generator.components.search.google_search import GoogleSearchClient
from src.proposal_generator.components.search.search_results_manager import SearchResultsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_configuration():
    try:
        # Initialize config
        config = Config()
        logger.info("Configuration loaded successfully")
        logger.info(f"API Settings: {config.api_settings}")
        
        # Test Gemini API
        logger.info("\nTesting Gemini API...")
        llm = get_gemini_llm()
        messages = [HumanMessage(content="Say hello!")]
        response = await llm.agenerate([messages])
        logger.info(f"Gemini Response: {response.generations[0][0].text}")
        
        # Test Google Search API
        logger.info("\nTesting Google Search API...")
        search_client = GoogleSearchClient(config)
        search_manager = SearchResultsManager(search_client)
        
        # Test search query
        query = "best law firms in California 2024"
        logger.info(f"Testing search with query: {query}")
        
        # Get API info
        api_info = search_client.get_api_info()
        logger.info(f"Search API Configuration: {api_info}")
        
        # Perform search and process results
        results = await search_manager.search_and_process(query, num_results=3)
        
        # Display results
        logger.info(f"\nFound {len(results)} search results:")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. {result.title}")
            logger.info(f"URL: {result.url}")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_configuration()) 