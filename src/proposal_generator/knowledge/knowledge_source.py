"""Knowledge source implementations."""
from typing import Dict, Any, Optional
from pydantic import Field, ConfigDict
from .base import BaseKnowledgeSource

class StringKnowledgeSource(BaseKnowledgeSource):
    """Knowledge source that stores content as strings."""
    
    content: str = Field(default="")
    name: str = Field(default="string_source")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_type: str = Field(default="string_knowledge")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, content: str = "", name: str = "", metadata: Optional[Dict[str, Any]] = None, **kwargs):
        """Initialize the string knowledge source."""
        super().__init__(
            content=content,
            name=name or "string_source",
            metadata=metadata or {},
            source_type="string_knowledge",
            **kwargs
        )
    
    def get_relevant_content(self, query: str) -> str:
        """Get content relevant to the query."""
        # For string sources, we return the entire content
        # In a more sophisticated implementation, we could do semantic search here
        return self.content
    
    def get_context(self) -> Dict[str, Any]:
        """Get the knowledge source context."""
        return {
            "content": self.content,
            "metadata": {
                **self.metadata,
                "type": "string",
                "length": len(self.content),
                "format": "text"
            },
            "name": self.name,
            "type": self.source_type
        }
    
    def append_content(self, content: str) -> None:
        """Add content to the knowledge source."""
        self.content += "\n" + content
    
    def __str__(self) -> str:
        return self.content