"""Base classes for knowledge sources."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
import google.generativeai as genai
from datetime import datetime, timedelta

class SimpleCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, ttl: int = 3600):  # Default TTL of 1 hour
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self._cache:
            return None
        
        timestamp = self._timestamps[key]
        if datetime.now() - timestamp > timedelta(seconds=self._ttl):
            del self._cache[key]
            del self._timestamps[key]
            return None
            
        return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._timestamps.clear()

class BaseKnowledgeSource(BaseModel):
    """Base class for knowledge sources that can be used with crewAI agents."""
    
    content: str = Field(default="")
    name: str = Field(default="base_source")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    collection_name: Optional[str] = Field(default=None)
    source_type: str = Field(default="knowledge_source")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, content: str = "", name: str = "", metadata: Optional[Dict[str, Any]] = None, **kwargs):
        """Initialize the knowledge source."""
        super().__init__(
            content=content,
            name=name or "base_source",
            metadata=metadata or {},
            **kwargs
        )
        
        if not self.collection_name:
            base_name = f"knowledge_{self.name}"
            self.collection_name = self._sanitize_collection_name(base_name)
        
        # Initialize cache for storing embeddings
        self._cache = SimpleCache()
    
    def _sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name to meet ChromaDB requirements."""
        # Convert to lowercase and replace any non-alphanumeric characters with underscores
        sanitized = ''.join(c if c.isalnum() else '_' for c in name.lower())
        
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'k_' + sanitized
        
        # Ensure it's not too long
        sanitized = sanitized[:63]
        
        # Remove consecutive underscores
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        
        # Remove trailing underscore if present
        sanitized = sanitized.rstrip('_')
        
        # Ensure minimum length
        if len(sanitized) < 3:
            sanitized = f"{sanitized}_collection"
        
        return sanitized
    
    def get_relevant_content(self, query: str) -> str:
        """Get content relevant to the query."""
        # Check cache first
        cache_key = f"query_{query}"
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # If not in cache, return full content
        # In a more sophisticated implementation, we could do semantic search here
        self._cache.set(cache_key, self.content)
        return self.content
    
    def get_context(self) -> Dict[str, Any]:
        """Get the knowledge source context."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "name": self.name,
            "type": self.source_type
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for CrewAI."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "name": self.name,
            "type": self.source_type
        }
    
    def get_relevant_chunks(self, query: str) -> List[str]:
        """Get relevant chunks of content for a query."""
        # For now, just return the entire content as one chunk
        return [self.content]