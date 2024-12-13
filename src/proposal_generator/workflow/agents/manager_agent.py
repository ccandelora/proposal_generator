from crewai import Agent
from ...config.workflow_config import WorkflowConfig
import sys
import os
import importlib
import logging
from typing import Optional
from pydantic import Field, ConfigDict, BaseModel

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the entire module
from src.proposal_generator.tools import management_tools

logger = logging.getLogger(__name__)

class ManagerAgent(Agent, BaseModel):
    """Agent responsible for managing and coordinating the proposal generation process."""
    
    name: str = Field(default="Manager Agent")
    role: str = Field(default="Project Manager")
    goal: str = Field(default="Manage and coordinate the proposal generation process")
    backstory: str = Field(default="""Experienced project manager with expertise in coordinating complex proposals.
        Your role is to ensure efficient task delegation, quality control, and timely delivery.""")
    task_tool: Optional[management_tools.TaskDelegationTool] = Field(default=None)
    qa_tool: Optional[management_tools.QualityAssuranceTool] = Field(default=None)
    config: Optional[WorkflowConfig] = Field(default=None)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, config: WorkflowConfig):
        try:
            # Initialize BaseModel first to validate fields
            BaseModel.__init__(self, config=config)
            
            # Initialize tools
            task_tool = management_tools.TaskDelegationTool()
            qa_tool = management_tools.QualityAssuranceTool()
            
            # Initialize Agent with validated fields
            agent_kwargs = {
                'name': self.name,
                'role': self.role,
                'goal': self.goal,
                'backstory': self.backstory,
                'tools': [task_tool, qa_tool],
                'verbose': True
            }
            Agent.__init__(self, **agent_kwargs)
            
            # Set tool fields
            object.__setattr__(self, 'task_tool', task_tool)
            object.__setattr__(self, 'qa_tool', qa_tool)
            
        except Exception as e:
            logger.error(f"Error initializing ManagerAgent: {e}")
            raise
            
    async def create_execution_plan(self, requirements: dict) -> dict:
        """Create an optimized execution plan based on requirements."""
        try:
            # Use the task delegation tool to analyze requirements and create a plan
            task_result = await self.task_tool._run({
                'description': 'Create execution plan for proposal generation',
                'objectives': requirements.get('objectives', []),
                'constraints': requirements.get('constraints', []),
                'available_resources': requirements.get('resources', [])
            })
            
            # Extract relevant information from the task analysis
            task_analysis = task_result.get('task_analysis', {})
            assignments = task_result.get('assignments', [])
            timeline = task_result.get('timeline', {})
            dependencies = task_result.get('dependencies', [])
            
            # Structure the execution plan
            return {
                "phases": [
                    {
                        "name": "Research & Analysis",
                        "parallel_tasks": [
                            {"agent": "research", "task": "market_analysis"},
                            {"agent": "technical", "task": "tech_assessment"}
                        ]
                    },
                    {
                        "name": "Solution Design",
                        "parallel_tasks": [
                            {"agent": "ux", "task": "ux_design"},
                            {"agent": "seo", "task": "seo_strategy"}
                        ]
                    },
                    {
                        "name": "Cost & Timeline",
                        "sequential_tasks": [
                            {"agent": "cost", "task": "cost_estimation"},
                            {"agent": "planning", "task": "timeline_planning"}
                        ]
                    }
                ],
                "dependencies": {
                    "cost_estimation": ["tech_assessment", "ux_design"],
                    "timeline_planning": ["cost_estimation"]
                },
                "analysis": task_analysis,
                "assignments": assignments,
                "timeline": timeline,
                "task_dependencies": dependencies
            }
        except Exception as e:
            logger.error(f"Error creating execution plan: {str(e)}")
            return {}