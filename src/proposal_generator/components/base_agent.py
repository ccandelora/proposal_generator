from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all proposal generator agents."""
    
    def __init__(self):
        self.results = {}
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results."""
        pass
    
    def _handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle errors in a consistent way across agents."""
        logger.error(f"Error in {context}: {str(error)}")
        return {'error': str(error), 'context': context} 