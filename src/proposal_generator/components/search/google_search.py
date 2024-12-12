"""Google Search module with rate limiting and API support."""
from typing import List, Dict, Any
import time
import logging
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ratelimit import limits, sleep_and_retry
from ...config import Config

logger = logging.getLogger(__name__)

class GoogleSearchClient:
    """Client for performing Google searches with rate limiting and API support."""
    
    def __init__(self, config: Config):
        """Initialize Google search client."""
        self.api_key = config.google_search_api_key
        self.custom_search_id = config.google_custom_search_id
        
        if not self.api_key or not self.custom_search_id:
            raise ValueError("Google Search API key and Custom Search ID are required")
            
        logger.info(f"Initializing search client with Project 2 API key ending in: {self.api_key[-4:]}")
        
        self.service = build(
            'customsearch', 'v1',
            developerKey=self.api_key,
            cache_discovery=False
        )
        
        logger.info("Google Search Client initialized with Custom Search API")

    @sleep_and_retry
    @limits(calls=10, period=60)  # Rate limit: 10 calls per minute
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Perform a Google search."""
        try:
            logger.info(f"Executing Google search for: {query}")
            results = []
            start_index = 1
            
            while len(results) < num_results:
                # Execute search request
                response = self.service.cse().list(
                    q=query,
                    cx=self.custom_search_id,
                    num=min(10, num_results - len(results)),
                    start=start_index
                ).execute()
                
                # Debug: Print raw response
                logger.debug(f"Raw API response: {response}")
                
                if 'items' not in response:
                    logger.warning("No items in search response")
                    logger.debug(f"Response keys: {response.keys()}")
                    break
                
                # Process results
                for item in response['items']:
                    # Debug: Print raw item
                    logger.debug(f"Processing search result item: {item}")
                    
                    link = item.get('link')
                    if not link:
                        logger.warning(f"Missing URL in item: {item}")
                        continue
                        
                    # Validate URL format
                    if not (link.startswith('http://') or link.startswith('https://')):
                        logger.warning(f"Invalid URL format: {link}")
                        continue
                    
                    try:
                        results.append({
                            'url': link,
                            'title': item.get('title', 'No Title'),
                            'snippet': item.get('snippet', 'No Snippet'),
                            'source': 'google_api',
                            'metadata': {
                                'domain': item.get('displayLink', ''),
                                'cached_page': item.get('cacheId', ''),
                                'page_map': item.get('pagemap', {}),
                                'mime_type': item.get('mime', 'text/html'),
                                'file_format': item.get('fileFormat', ''),
                                'language': item.get('language', 'en')
                            }
                        })
                        logger.info(f"Successfully added result: {link}")
                    except Exception as e:
                        logger.error(f"Error processing item {link}: {str(e)}")
                        continue
                
                if len(response['items']) < 10:
                    break
                    
                start_index += 10
            
            # Debug: Print final results
            logger.info(f"Search completed. Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                logger.info(f"{i}. URL: {result['url']}")
                logger.info(f"   Title: {result['title']}")
            
            return results[:num_results]

        except HttpError as e:
            logger.error(f"Google API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error performing Google search: {str(e)}")
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """Get information about the API configuration."""
        return {
            'using_api': True,
            'search_engine': 'Google Custom Search API',
            'custom_search_id': self.custom_search_id[-4:],  # Last 4 chars for security
            'rate_limit': '10 queries per minute'
        } 