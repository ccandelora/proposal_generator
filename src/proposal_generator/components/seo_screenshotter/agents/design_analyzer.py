"""Design Analyzer Agent for analyzing visual design elements."""

from typing import Dict, Any
from crewai import Agent
from ..models.task_context import TaskContext
from ..utils.color_utils import normalize_color, hex_to_hsl
from ..utils.html_utils import get_element_styles

class DesignAnalyzerAgent(Agent):
    """Agent responsible for analyzing design elements in screenshots."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role="Design Analysis Expert",
            goal="Analyze visual design elements and patterns in website screenshots",
            backstory="""You are an expert in visual design analysis with deep knowledge 
            of color theory, typography, and layout principles.""",
            **kwargs
        )

    def analyze_design(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze design elements from screenshot and HTML content."""
        if not context.html_content or not context.driver:
            return {"error": "Missing required screenshot or HTML content"}

        design_elements = get_element_styles(context.driver)
        
        # Analyze colors
        colors = self._analyze_colors(design_elements)
        
        # Analyze typography
        typography = self._analyze_typography(design_elements)
        
        # Analyze layout
        layout = self._analyze_layout(design_elements)
        
        return {
            "colors": colors,
            "typography": typography,
            "layout": layout
        }

    def _analyze_colors(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze color usage and patterns."""
        colors = {}
        for element in elements:
            if "color" in element:
                normalized = normalize_color(element["color"])
                if normalized:
                    hsl = hex_to_hsl(normalized)
                    colors[normalized] = {
                        "hsl": hsl,
                        "frequency": colors.get(normalized, {}).get("frequency", 0) + 1
                    }
        return colors

    def _analyze_typography(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze typography usage."""
        fonts = {}
        sizes = {}
        for element in elements:
            if "font-family" in element:
                font = element["font-family"]
                fonts[font] = fonts.get(font, 0) + 1
            if "font-size" in element:
                size = element["font-size"]
                sizes[size] = sizes.get(size, 0) + 1
        return {
            "fonts": fonts,
            "sizes": sizes
        }

    def _analyze_layout(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze layout patterns."""
        return {
            "spacing": self._analyze_spacing(elements),
            "alignment": self._analyze_alignment(elements)
        }

    def _analyze_spacing(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spacing patterns."""
        spacing = {}
        for element in elements:
            if "margin" in element:
                spacing["margin"] = spacing.get("margin", []) + [element["margin"]]
            if "padding" in element:
                spacing["padding"] = spacing.get("padding", []) + [element["padding"]]
        return spacing

    def _analyze_alignment(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze alignment patterns."""
        alignment = {}
        for element in elements:
            if "text-align" in element:
                align = element["text-align"]
                alignment[align] = alignment.get(align, 0) + 1
        return alignment 