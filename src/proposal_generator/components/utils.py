"""Utility classes and functions."""

from typing import Any, Callable, Dict, Optional

class Tool:
    """Tool class for agent tools."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        return_direct: bool = False
    ):
        """Initialize a tool."""
        self.name = name
        self.func = func
        self.description = description
        self.return_direct = return_direct

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the tool function."""
        return self.func(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'return_direct': self.return_direct
        } 