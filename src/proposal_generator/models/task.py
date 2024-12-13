from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

class Task(BaseModel):
    """Represents a task to be executed by an agent."""
    
    name: str = Field(description="Name of the task")
    description: str = Field(description="Description of what needs to be done")
    context: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(
        default_factory=list,
        description="Context data needed to execute the task"
    )
    expected_output: str = Field(description="Description of the expected output format")
    agent_name: Optional[str] = Field(
        default=None,
        description="Name of the agent assigned to this task"
    )
    status: str = Field(
        default="pending",
        description="Current status of the task (pending, in_progress, completed, failed)"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Result of the task execution"
    )
    
    model_config = ConfigDict(arbitrary_types_allowed=True)