from crewai import Agent, Task
from typing import Dict, Any, List, Optional, Union
import logging
from ...tools.coding_tools import (
    CodeGeneratorTool,
    CodeReviewTool,
    ArchitecturePlannerTool
)
from pydantic import Field, ConfigDict, BaseModel
from ...config.workflow_config import WorkflowConfig
from ..workflow_models import AgentMessage
from ...knowledge.base import BaseKnowledgeSource

logger = logging.getLogger(__name__)

class CodingAgent(Agent, BaseModel):
    """Agent responsible for coding tasks."""
    
    name: str = Field(default="Coding Agent")
    role: str = Field(default="Senior Software Engineer")
    goal: str = Field(default="Write efficient, maintainable, and secure code")
    backstory: str = Field(default="""Experienced software engineer with expertise in multiple programming languages 
        and software design patterns. Focused on writing clean, efficient, and well-documented code.""")
    code_generator: CodeGeneratorTool = Field(default_factory=CodeGeneratorTool)
    code_reviewer: CodeReviewTool = Field(default_factory=CodeReviewTool)
    architecture_planner: ArchitecturePlannerTool = Field(default_factory=ArchitecturePlannerTool)
    knowledge_sources: Optional[List[Union[Dict[str, Any], BaseKnowledgeSource]]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, name: str = "Coding Agent", **kwargs):
        """Initialize the agent.
        
        Args:
            name: The name of the agent
            **kwargs: Additional arguments passed to the base agent class
        """
        # Process knowledge sources before initialization
        if 'knowledge_sources' in kwargs:
            processed_sources = []
            for source in kwargs['knowledge_sources']:
                if hasattr(source, 'to_dict'):
                    processed_sources.append(source.to_dict())
                elif isinstance(source, dict):
                    if all(k in source for k in ['content', 'name', 'type']):
                        processed_sources.append(source)
            kwargs['knowledge_sources'] = processed_sources
        
        # Initialize BaseModel first to validate fields
        BaseModel.__init__(self, name=name, **kwargs)
        
        # Initialize tools
        tools = [
            self.code_generator,
            self.code_reviewer,
            self.architecture_planner
        ]
        
        # Initialize Agent with validated fields
        agent_kwargs = {
            'name': self.name,
            'role': self.role,
            'goal': self.goal,
            'backstory': self.backstory,
            'tools': tools,
            'verbose': True,
            'allow_delegation': True,
            'llm': {
                'model': 'gemini-pro',
                'temperature': 0.7,
                'max_tokens': 4096
            }
        }
        
        # Add processed knowledge sources
        if self.knowledge_sources:
            agent_kwargs['knowledge_sources'] = self.knowledge_sources
        
        # Initialize the Agent with the processed arguments
        Agent.__init__(self, **agent_kwargs)
    
    async def generate_project_code(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete project codebase."""
        try:
            # Plan architecture first
            architecture = await self.architecture_planner._run(requirements)
            
            # Generate code based on architecture and requirements
            code_result = await self.code_generator._run({
                **requirements,
                'architecture': architecture
            })
            
            # Review generated code
            review_result = await self.code_reviewer._run({
                'code': code_result,
                'requirements': requirements
            })
            
            return {
                'architecture': architecture,
                'code': code_result,
                'review': review_result
            }
            
        except Exception as e:
            logger.error(f"Error generating project code: {str(e)}")
            raise
    
    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute the coding task."""
        try:
            # Extract requirements from task context
            requirements = {}
            if isinstance(task.context, list):
                for ctx in task.context:
                    if isinstance(ctx, dict):
                        if ctx.get('type') == 'requirements':
                            requirements = ctx.get('data', {})
                        elif ctx.get('type') == 'design_assets':
                            requirements['design_assets'] = ctx.get('data')
                        elif ctx.get('type') == 'competitor_analysis':
                            requirements['competitor_analysis'] = ctx.get('data')
                        elif ctx.get('type') == 'code_implementation':
                            requirements['code_implementation'] = ctx.get('data')
                        elif ctx.get('type') == 'ai_integration':
                            requirements['ai_integration'] = ctx.get('data')
            
            # Execute task based on description
            if "architecture" in task.description.lower():
                result = await self.architecture_planner._run(requirements)
            elif "review" in task.description.lower():
                result = await self.code_reviewer._run(requirements)
            else:
                # Default to full project code generation
                result = await self.generate_project_code(requirements)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing coding task: {str(e)}")
            raise