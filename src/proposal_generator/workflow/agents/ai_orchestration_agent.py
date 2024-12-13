from typing import Dict, Any, List, Optional, Union
import logging
from pydantic import BaseModel, Field, ConfigDict

from crewai import Agent
from ...config.workflow_config import WorkflowConfig
from ...tools.ai_tools import (
    MLModelSelectionTool,
    AIIntegrationTool,
    OptimizationTool
)
from ...models.task import Task
from ...knowledge.base import BaseKnowledgeSource

logger = logging.getLogger(__name__)

class AIOrchestrationAgent(Agent, BaseModel):
    """Agent responsible for AI strategy and integration planning."""
    
    name: str = Field(default="AI Orchestration Agent")
    role: str = Field(default="AI Strategy Specialist")
    goal: str = Field(default="Design and plan effective AI integrations and strategies")
    backstory: str = Field(default="""Expert AI strategist with deep knowledge of machine learning, 
        neural networks, and practical AI implementation. Focused on creating scalable and ethical AI solutions.""")
    config: Optional[WorkflowConfig] = Field(default=None)
    model_selector: MLModelSelectionTool = Field(default_factory=MLModelSelectionTool)
    integration_planner: AIIntegrationTool = Field(default_factory=AIIntegrationTool)
    optimizer: OptimizationTool = Field(default_factory=OptimizationTool)
    knowledge_sources: Optional[List[Union[Dict[str, Any], BaseKnowledgeSource]]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, name: str = "AI Orchestration Agent", **kwargs):
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
            self.model_selector,
            self.integration_planner,
            self.optimizer
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
    
    async def generate_ai_insights(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations."""
        try:
            # Select appropriate ML models
            model_task = Task(
                description="Select appropriate ML models",
                expected_output="ML model recommendations and implementation plan",
                context=[{
                    "type": "requirements",
                    "data": requirements,
                    "description": "Project requirements and specifications",
                    "expected_output": "Structured requirements data"
                }]
            )
            model_recommendations = await self.model_selector._run(model_task)
            
            # Plan AI integration
            integration_task = Task(
                description="Plan AI integration",
                expected_output="AI integration plan and strategy",
                context=[{
                    "type": "requirements",
                    "data": requirements,
                    "description": "Project requirements and specifications",
                    "expected_output": "Structured requirements data"
                }, {
                    "type": "model_recommendations",
                    "data": model_recommendations,
                    "description": "ML model recommendations",
                    "expected_output": "Model selection details"
                }]
            )
            integration_plan = await self.integration_planner._run(integration_task)
            
            # Generate optimization recommendations
            optimization_task = Task(
                description="Generate optimization recommendations",
                expected_output="Performance optimization recommendations",
                context=[{
                    "type": "requirements",
                    "data": requirements,
                    "description": "Project requirements and specifications",
                    "expected_output": "Structured requirements data"
                }, {
                    "type": "integration_plan",
                    "data": integration_plan,
                    "description": "AI integration plan",
                    "expected_output": "Integration details"
                }]
            )
            optimization_recommendations = await self.optimizer._run(optimization_task)
            
            return {
                'model_recommendations': model_recommendations,
                'integration_plan': integration_plan,
                'optimization_recommendations': optimization_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            raise
            
    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute AI orchestration task."""
        try:
            # Extract requirements from task context
            requirements = {}
            if isinstance(task.context, list):
                for ctx in task.context:
                    if isinstance(ctx, dict):
                        if ctx.get('type') == 'requirements':
                            requirements = ctx.get('data', {})
                        elif ctx.get('type') == 'code_implementation':
                            requirements['code_implementation'] = ctx.get('data')
            
            # Generate insights based on task description
            if "model" in task.description.lower():
                result = await self.model_selector._run(requirements)
            elif "integration" in task.description.lower():
                result = await self.integration_planner._run(requirements)
            elif "optimization" in task.description.lower():
                result = await self.optimizer._run(requirements)
            else:
                # Default to full AI insights generation
                result = await self.generate_ai_insights(requirements)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing AI orchestration task: {str(e)}")
            raise 