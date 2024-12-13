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
    
    def __init__(self, config: Config, progress_callback=None):
        """Initialize Google search client."""
        self.api_key = config.google_search_api_key
        self.custom_search_id = config.google_custom_search_id
        self.progress_callback = progress_callback
        
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
        """Perform Google search."""
        try:
            if self.progress_callback:
                self.progress_callback("Search", "Starting Google search...", 0)
            
            results = []
            start_index = 1
            
            while len(results) < num_results:
                if self.progress_callback:
                    progress = int((len(results) / num_results) * 90)  # 0-90%
                    self.progress_callback("Search", f"Searching batch {start_index}...", progress)
                
                # Execute search
                response = self.service.cse().list(
                    q=query,
                    cx=self.custom_search_id,
                    start=start_index
                ).execute()
                
                # Process results
                if 'items' in response:
                    for item in response['items']:
                        if len(results) >= num_results:
                            break
                            
                        results.append({
                            'url': item.get('link'),
                            'title': item.get('title'),
                            'snippet': item.get('snippet'),
                            'metadata': {
                                'type': item.get('mime'),
                                'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('date'),
                                'source': item.get('displayLink')
                            }
                        })
                        
                        if self.progress_callback:
                            self.progress_callback(
                                "Search", 
                                f"Found result: {item.get('title')[:30]}...", 
                                90 + int((len(results) / num_results) * 10)  # 90-100%
                            )
                
                if len(response.get('items', [])) < 10:
                    break
                    
                start_index += 10
            
            if self.progress_callback:
                self.progress_callback("Search", f"Found {len(results)} results", 100)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Google search: {str(e)}")
            if self.progress_callback:
                self.progress_callback("Search", f"Error: {str(e)}", 0)
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """Get information about the API configuration."""
        return {
            'using_api': True,
            'search_engine': 'Google Custom Search API',
            'custom_search_id': self.custom_search_id[-4:],  # Last 4 chars for security
            'rate_limit': '10 queries per minute'
        } 