"""Base agent class for all components."""

import logging
from typing import Dict, Any

class BaseAgent:
    """Base class for all agents."""

    def __init__(self):
        """Initialize the base agent."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(handler)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process method")

    def _handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle errors in a consistent way."""
        self.logger.error(f"Error in {context}: {str(error)}")
        return {'error': str(error)} 