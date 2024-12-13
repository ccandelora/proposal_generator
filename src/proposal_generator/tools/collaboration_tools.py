from crewai.tools import BaseTool
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TaskDelegationTool(BaseTool):
    """Tool for delegating and coordinating tasks between agents."""
    
    def __init__(self):
        super().__init__(
            name="Task Delegation Tool",
            description="Coordinates work between different specialized agents"
        )
    
    async def run(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return {
                "assigned_agent": task_details.get("best_suited_agent"),
                "dependencies": task_details.get("dependencies", []),
                "priority": task_details.get("priority", "medium"),
                "estimated_time": task_details.get("estimated_time", "1h"),
                "required_tools": task_details.get("required_tools", [])
            }
        except Exception as e:
            logger.error(f"Error in task delegation: {str(e)}")
            return {}

class QualityAssuranceTool(BaseTool):
    """Tool for checking work quality and consistency."""
    
    def __init__(self):
        super().__init__(
            name="Quality Assurance Tool",
            description="Validates work against quality standards"
        )
    
    async def run(self, content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            checks = {
                "completeness": self._check_completeness(content),
                "consistency": self._check_consistency(content),
                "accuracy": self._check_accuracy(content),
                "formatting": self._check_formatting(content)
            }
            return {
                "passed": all(checks.values()),
                "checks": checks,
                "recommendations": self._generate_recommendations(checks)
            }
        except Exception as e:
            logger.error(f"Error in quality assurance: {str(e)}")
            return {} 