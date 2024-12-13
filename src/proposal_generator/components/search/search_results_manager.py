"""Manager for storing and processing search results."""
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from .google_search import GoogleSearchClient
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for storing search result information."""
    url: str
    title: str
    snippet: str
    content: str
    metadata: Dict[str, Any]
    retrieved_at: datetime
    relevance_score: float = 0.0

class SearchResultsManager:
    """Manager for search results and content extraction."""
    
    def __init__(self, search_client: GoogleSearchClient, progress_callback=None):
        """Initialize search results manager."""
        self.search_client = search_client
        self.progress_callback = progress_callback
        self.results: List[SearchResult] = []
        self.processed_urls = set()

    async def search_and_process(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform search and process results."""
        try:
            if self.progress_callback:
                self.progress_callback("Search", "Initializing search...", 0)
            
            # Perform search
            if self.progress_callback:
                self.progress_callback("Search", f"Searching for: {query}", 10)
            
            logger.info(f"Executing search for: {query}")
            search_results = self.search_client.search(query, num_results)
            logger.info(f"Got {len(search_results)} raw results")
            
            if self.progress_callback:
                self.progress_callback("Search", "Processing results...", 30)
            
            # Process results
            total_results = len(search_results)
            processed_results = []
            
            for i, result in enumerate(search_results):
                if result.get('url') and result['url'] not in self.processed_urls:
                    if self.progress_callback:
                        progress = 30 + int((i / total_results) * 60)  # 30-90%
                        self.progress_callback(
                            "Search", 
                            f"Processing result {i+1}/{total_results}: {result.get('title', '')[:30]}...", 
                            progress
                        )
                    
                    try:
                        processed = await self._process_result(result)
                        if processed:
                            processed_results.append(processed)
                            self.processed_urls.add(result['url'])
                            logger.info(f"Successfully processed: {result['url']}")
                        else:
                            logger.warning(f"Failed to process result: {result['url']}")
                    except Exception as e:
                        logger.error(f"Error processing result {result.get('url')}: {str(e)}")
            
            # Sort by relevance
            processed_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            if self.progress_callback:
                self.progress_callback(
                    "Search", 
                    f"Found {len(processed_results)} relevant results", 
                    100
                )
            
            logger.info(f"Search complete. Processed {len(processed_results)} results")
            return processed_results

        except Exception as e:
            logger.error(f"Error in search and process: {str(e)}")
            if self.progress_callback:
                self.progress_callback("Search", f"Error: {str(e)}", 0)
            return []

    async def _process_result(self, result: Dict[str, Any]) -> Optional[SearchResult]:
        """Process a single search result."""
        try:
            url = result.get('url')
            if not url:
                logger.warning("Skipping result with no URL")
                return None

            # Extract content from URL
            content = await self._extract_content(url)
            if not content:
                logger.warning(f"No content extracted from {url}")
                return None
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(
                content,
                result.get('title', ''),
                result.get('snippet', '')
            )
            
            # Only return results with meaningful content
            if relevance_score > 0:
                return SearchResult(
                    url=url,
                    title=result.get('title', ''),
                    snippet=result.get('snippet', ''),
                    content=content,
                    metadata=result.get('metadata', {}),
                    retrieved_at=datetime.now(),
                    relevance_score=relevance_score
                )
            else:
                logger.warning(f"Skipping low relevance result: {url}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing result {result.get('url', 'unknown')}: {str(e)}")
            return None

    async def _extract_content(self, url: str) -> str:
        """Extract main content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: Status {response.status}")
                        return ''
                        
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'form']):
                        element.decompose()
                    
                    # Try different content containers
                    content_elements = [
                        soup.find('main'),
                        soup.find('article'),
                        soup.find('div', {'class': ['content', 'main-content', 'post-content']}),
                        soup.find('body')
                    ]
                    
                    for element in content_elements:
                        if element:
                            # Clean up text
                            text = ' '.join(element.stripped_strings)
                            cleaned = self._clean_content(text)
                            if cleaned:
                                return cleaned
                    
                    return ''
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ''

    def _clean_content(self, content: str) -> str:
        """Clean extracted content."""
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Remove very short lines
        lines = [line for line in content.split('\n') if len(line.strip()) > 30]
        
        return '\n'.join(lines)

    def _calculate_relevance(self, content: str, title: str, snippet: str) -> float:
        """Calculate relevance score for content."""
        try:
            score = 0.0
            
            # Check content length
            if len(content) > 1000:
                score += 0.3
            
            # Check if title is meaningful
            if title and len(title) > 10:
                score += 0.2
            
            # Check if snippet is meaningful
            if snippet and len(snippet) > 30:
                score += 0.2
            
            # Check content quality (basic check)
            sentences = content.split('.')
            if len(sentences) > 5:
                score += 0.3
            
            return min(1.0, score)
            
        except Exception:
            return 0.0

    def get_relevant_content(self, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get relevant content for proposal generation.
        
        Args:
            min_score: Minimum relevance score to include
            
        Returns:
            List of relevant content pieces
        """
        relevant_results = [
            result for result in self.results
            if result.relevance_score >= min_score
        ]
        
        return [{
            'url': result.url,
            'title': result.title,
            'content': result.content,
            'relevance_score': result.relevance_score,
            'retrieved_at': result.retrieved_at.isoformat()
        } for result in relevant_results]

    def clear_results(self):
        """Clear stored results."""
        self.results.clear()
        self.processed_urls.clear() 