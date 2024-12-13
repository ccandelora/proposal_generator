"""Base tool class for proposal generator."""
from typing import Dict, Any, Optional, Callable
import logging
from abc import ABC, abstractmethod
from crewai.tools import BaseTool as CrewAIBaseTool
from pydantic import Field, ConfigDict

logger = logging.getLogger(__name__)

class BaseTool(CrewAIBaseTool):
    """Base class for all tools."""
    
    name: str = Field(default="Base Tool")
    description: str = Field(default="Base tool class that all tools inherit from")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    async def _run(self, **kwargs) -> Dict[str, Any]:
        """Run the tool's main functionality."""
        raise NotImplementedError("Tool must implement _run method")
    
    def _run_sync(self, **kwargs) -> Dict[str, Any]:
        """Synchronous run method required by crewai."""
        import asyncio
        return asyncio.run(self._run(**kwargs))
    
    @property
    def func(self) -> Callable:
        """Return the function to be called by crewai."""
        return self._run_sync