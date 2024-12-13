from crewai.tools import BaseTool
from typing import Dict, Any, List
import logging
from PIL import Image
import io
import requests
from jinja2 import Template
import yaml
import markdown
import json

logger = logging.getLogger(__name__)

class MockupGeneratorTool(BaseTool):
    """Tool for generating project mockups and prototypes."""
    
    def __init__(self):
        super().__init__(
            name="Mockup Generator",
            description="Generates interactive mockups and prototypes"
        )
    
    async def _run(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project mockups."""
        try:
            return {
                'wireframes': await self._generate_wireframes(requirements),
                'prototypes': await self._generate_prototypes(requirements),
                'interactive_demos': await self._generate_interactive_demos(requirements),
                'responsive_previews': await self._generate_responsive_previews(requirements)
            }
        except Exception as e:
            logger.error(f"Error generating mockups: {str(e)}")
            return {}

class AssetGeneratorTool(BaseTool):
    """Tool for generating project assets."""
    
    def __init__(self):
        super().__init__(
            name="Asset Generator",
            description="Generates project assets and resources"
        )
    
    async def _run(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project assets."""
        try:
            return {
                'images': await self._generate_images(requirements),
                'icons': await self._generate_icons(requirements),
                'illustrations': await self._generate_illustrations(requirements),
                'animations': await self._generate_animations(requirements),
                'videos': await self._generate_videos(requirements)
            }
        except Exception as e:
            logger.error(f"Error generating assets: {str(e)}")
            return {}

class ResearchAggregatorTool(BaseTool):
    """Tool for aggregating research data."""
    
    def __init__(self):
        super().__init__(
            name="Research Aggregator",
            description="Aggregates and analyzes research data"
        )
    
    async def _run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate research data."""
        try:
            return {
                'market_analysis': await self._analyze_market_data(data),
                'competitor_analysis': await self._analyze_competitor_data(data),
                'trends': await self._analyze_trends(data),
                'insights': await self._generate_insights(data),
                'recommendations': await self._generate_recommendations(data)
            }
        except Exception as e:
            logger.error(f"Error aggregating research: {str(e)}")
            return {}

class ProjectPlannerTool(BaseTool):
    """Tool for project planning."""
    
    def __init__(self):
        super().__init__(
            name="Project Planner",
            description="Creates detailed project plans and timelines"
        )
    
    async def _run(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create project plan."""
        try:
            return {
                'timeline': await self._create_timeline(requirements),
                'milestones': await self._define_milestones(requirements),
                'resources': await self._allocate_resources(requirements),
                'dependencies': await self._identify_dependencies(requirements),
                'risks': await self._assess_risks(requirements)
            }
        except Exception as e:
            logger.error(f"Error creating project plan: {str(e)}")
            return {}

class ContentGeneratorTool(BaseTool):
    """Tool for generating website content."""
    
    def __init__(self):
        super().__init__(
            name="Content Generator",
            description="Generates website content and copy"
        )
    
    async def _run(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate website content."""
        try:
            return {
                'page_content': await self._generate_page_content(requirements),
                'seo_content': await self._generate_seo_content(requirements),
                'blog_posts': await self._generate_blog_posts(requirements),
                'product_descriptions': await self._generate_product_content(requirements),
                'meta_content': await self._generate_meta_content(requirements)
            }
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {}

class MarketingMaterialsTool(BaseTool):
    """Tool for generating marketing materials."""
    
    def __init__(self):
        super().__init__(
            name="Marketing Materials Generator",
            description="Generates marketing and promotional materials"
        )
    
    async def _run(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing materials."""
        try:
            return {
                'social_media': await self._generate_social_media_content(requirements),
                'email_templates': await self._generate_email_templates(requirements),
                'promotional_graphics': await self._generate_promo_graphics(requirements),
                'ad_materials': await self._generate_ad_materials(requirements),
                'press_kit': await self._generate_press_kit(requirements)
            }
        except Exception as e:
            logger.error(f"Error generating marketing materials: {str(e)}")
            return {} 