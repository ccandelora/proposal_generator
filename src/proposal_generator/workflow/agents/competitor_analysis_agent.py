from typing import Dict, Any, List, Optional, Union
import logging
from collections import Counter
from pydantic import BaseModel, Field, ConfigDict

from crewai import Agent
from ...config.workflow_config import WorkflowConfig
from ...tools.competitor_tools import (
    WebsiteAnalyzerTool,
    MarketPositioningTool,
    DifferentiatorAnalysisTool,
    SEOComparisonTool
)
from ...models.task import Task
from ...knowledge.base import BaseKnowledgeSource

logger = logging.getLogger(__name__)

class CompetitorAnalysisAgent(Agent, BaseModel):
    """Agent responsible for analyzing competitors and market positioning."""
    
    name: str = Field(default="Competitor Analysis Agent")
    role: str = Field(default="Competitive Intelligence Specialist")
    goal: str = Field(default="Provide detailed competitor analysis and market positioning insights")
    backstory: str = Field(default="""Expert market analyst with extensive experience in competitive intelligence 
        and digital strategy. Specialized in identifying market opportunities and competitive advantages.""")
    config: Optional[WorkflowConfig] = Field(default=None)
    website_analyzer: WebsiteAnalyzerTool = Field(default_factory=WebsiteAnalyzerTool)
    market_analyzer: MarketPositioningTool = Field(default_factory=MarketPositioningTool)
    differentiator_analyzer: DifferentiatorAnalysisTool = Field(default_factory=DifferentiatorAnalysisTool)
    seo_analyzer: SEOComparisonTool = Field(default_factory=SEOComparisonTool)
    knowledge_sources: Optional[List[Union[Dict[str, Any], BaseKnowledgeSource]]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, name: str = "Competitor Analysis Agent", **kwargs):
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
            self.website_analyzer,
            self.market_analyzer,
            self.differentiator_analyzer,
            self.seo_analyzer
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
    
    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute the competitor analysis task."""
        try:
            # Extract competitor URLs from task context
            competitor_urls = task.context.get('competitor_urls', [])
            if not competitor_urls:
                logger.warning("No competitor URLs provided in task context")
                return {}
            
            # Analyze each competitor
            competitor_analyses = []
            for url in competitor_urls:
                analysis = {}
                
                # Website analysis
                analysis['website'] = await self.website_analyzer._run(url)
                
                # Market positioning analysis
                analysis['market_position'] = await self.market_analyzer._run({
                    'url': url,
                    'industry': task.context.get('industry', 'technology')
                })
                
                # Differentiator analysis
                analysis['differentiators'] = await self.differentiator_analyzer._run({
                    'url': url,
                    'industry': task.context.get('industry', 'technology'),
                    'market_position': analysis['market_position']
                })
                
                # SEO analysis
                analysis['seo_metrics'] = await self.seo_analyzer._run({
                    'url': url,
                    'keywords': task.context.get('keywords', [])
                })
                
                competitor_analyses.append({
                    'url': url,
                    'analysis': analysis
                })
            
            # Aggregate insights
            aggregated_insights = self._aggregate_competitor_insights(competitor_analyses)
            
            return {
                'competitor_analyses': competitor_analyses,
                'aggregated_insights': aggregated_insights,
                'recommendations': self._generate_recommendations(aggregated_insights)
            }
            
        except Exception as e:
            logger.error(f"Error executing competitor analysis: {str(e)}")
            return {}
            
    def _aggregate_competitor_insights(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate insights from multiple competitor analyses."""
        try:
            tech_stacks = Counter()
            market_positions = Counter()
            seo_strengths = Counter()
            content_types = Counter()
            
            for analysis in analyses:
                # Aggregate technology stacks
                tech_stack = analysis['analysis']['tech_stack']
                for tech in tech_stack.get('technologies', []):
                    tech_stacks[tech] += 1
                    
                # Aggregate market positions
                position = analysis['analysis']['market_position']
                market_positions[position.get('segment', 'unknown')] += 1
                
                # Aggregate SEO strengths
                seo = analysis['analysis']['seo_metrics']
                for strength in seo.get('strengths', []):
                    seo_strengths[strength] += 1
                    
                # Aggregate content strategies
                content = analysis['analysis']['content_strategy']
                for content_type in content.get('types', []):
                    content_types[content_type] += 1
            
            return {
                'common_technologies': dict(tech_stacks.most_common(5)),
                'market_segments': dict(market_positions.most_common()),
                'seo_focus_areas': dict(seo_strengths.most_common(5)),
                'popular_content_types': dict(content_types.most_common())
            }
            
        except Exception as e:
            logger.error(f"Error aggregating competitor insights: {str(e)}")
            return {}
            
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on competitor insights."""
        try:
            recommendations = []
            
            # Technology recommendations
            if insights.get('common_technologies'):
                tech_rec = "Consider adopting or evaluating these widely-used technologies: "
                tech_rec += ", ".join(insights['common_technologies'].keys())
                recommendations.append(tech_rec)
            
            # Market positioning recommendations
            if insights.get('market_segments'):
                segments = insights['market_segments']
                main_segment = max(segments.items(), key=lambda x: x[1])[0]
                recommendations.append(
                    f"Focus on differentiating from competitors in the {main_segment} segment"
                )
            
            # SEO recommendations
            if insights.get('seo_focus_areas'):
                seo_rec = "Prioritize these SEO areas for competitive advantage: "
                seo_rec += ", ".join(insights['seo_focus_areas'].keys())
                recommendations.append(seo_rec)
            
            # Content strategy recommendations
            if insights.get('popular_content_types'):
                content_rec = "Develop content in these popular formats: "
                content_rec += ", ".join(insights['popular_content_types'].keys())
                recommendations.append(content_rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []