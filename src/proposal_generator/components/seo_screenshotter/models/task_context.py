"""Task context model for SEO Screenshotter."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path

class TaskContext(BaseModel):
    """Model for Task context."""
    description: str = Field(default="Visual analysis context")
    expected_output: str = Field(default="Visual analysis results")
    screenshot: Optional[bytes] = Field(default=None, exclude=True)  # Exclude from JSON
    html_content: Optional[str] = Field(default=None)
    driver: Optional[Any] = Field(default=None, exclude=True)  # Exclude from JSON
    competitor_data: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            Path: str,
            bytes: lambda v: None  # Don't include binary data in JSON
        }
    } 