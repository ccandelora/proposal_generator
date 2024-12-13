from crewai import Agent, Task
from typing import Dict, Any, List, Optional, Union
import logging
from ...tools.design_tools import (
    MockupGeneratorTool,
    AssetGeneratorTool,
    ResearchAggregatorTool
)
from pydantic import Field, ConfigDict, BaseModel
from ...config.workflow_config import WorkflowConfig
from ..workflow_models import AgentMessage
from ...knowledge.base import BaseKnowledgeSource

logger = logging.getLogger(__name__)

class DesignAgent(Agent, BaseModel):
    """Agent responsible for design tasks."""
    
    name: str = Field(default="Design Agent")
    role: str = Field(default="UX/UI Design Specialist")
    goal: str = Field(default="Create intuitive and visually appealing design solutions")
    backstory: str = Field(default="""Experienced design professional with expertise in user experience, 
        visual design, and prototyping. Focused on creating engaging and accessible interfaces.""")
    mockup_generator: MockupGeneratorTool = Field(default_factory=MockupGeneratorTool)
    asset_generator: AssetGeneratorTool = Field(default_factory=AssetGeneratorTool)
    research_aggregator: ResearchAggregatorTool = Field(default_factory=ResearchAggregatorTool)
    knowledge_sources: Optional[List[Union[Dict[str, Any], BaseKnowledgeSource]]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, name: str = "Design Agent", **kwargs):
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
            self.mockup_generator,
            self.asset_generator,
            self.research_aggregator
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
    
    async def generate_design_assets(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all required design assets."""
        try:
            # Generate design system and mockups
            mockup_result = await self.mockup_generator._run(requirements)
            
            # Generate brand assets
            asset_result = await self.asset_generator._run({
                **requirements,
                'design_system': mockup_result.get('design_system', {})
            })
            
            # Aggregate research insights
            research_result = await self.research_aggregator._run({
                **requirements,
                'design_system': mockup_result.get('design_system', {}),
                'mockups': mockup_result.get('mockups', {})
            })
            
            return {
                'design_system': mockup_result.get('design_system', {}),
                'mockups': mockup_result.get('mockups', {}),
                'assets': asset_result,
                'research_insights': research_result
            }
            
        except Exception as e:
            logger.error(f"Error generating design assets: {str(e)}")
            raise
    
    async def collaborate(self, task: Task, collaborators: List[str]) -> Dict[str, Any]:
        """Execute task with collaboration from other agents."""
        try:
            # Notify collaborators about the task
            for collaborator in collaborators:
                await self.send_message(
                    collaborator,
                    AgentMessage(
                        type='collaboration_request',
                        content={
                            'task': task.description,
                            'context': task.context
                        },
                        sender=self.role
                    )
                )
            
            # Execute the task using the agent's execute method
            result = await self.execute(task)
            
            # Share results with collaborators
            for collaborator in collaborators:
                await self.send_message(
                    collaborator,
                    AgentMessage(
                        type='collaboration_result',
                        content=result,
                        sender=self.role
                    )
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in collaboration: {str(e)}")
            raise

    async def send_message(self, recipient: str, message: AgentMessage) -> None:
        """Send a message to another agent."""
        try:
            # In a real implementation, this would use some form of agent communication system
            logger.info(f"Sending message to {recipient}: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute the design task."""
        try:
            # Extract requirements from task context
            requirements = {}
            if isinstance(task.context, list):
                for ctx in task.context:
                    if isinstance(ctx, dict):
                        if ctx.get('type') == 'requirements':
                            requirements = ctx.get('data', {})
                        elif ctx.get('type') == 'competitor_analysis':
                            requirements['competitor_analysis'] = ctx.get('data')
            
            # Generate design assets based on task description
            if "design system" in task.description.lower():
                result = await self.mockup_generator._run({
                    **requirements,
                    'task_type': 'design_system'
                })
            elif "mockup" in task.description.lower():
                result = await self.mockup_generator._run({
                    **requirements,
                    'task_type': 'mockups'
                })
            elif "brand" in task.description.lower():
                result = await self.asset_generator._run(requirements)
            elif "research" in task.description.lower():
                result = await self.research_aggregator._run(requirements)
            else:
                # Default to full design asset generation
                result = await self.generate_design_assets(requirements)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing design task: {str(e)}")
            raise