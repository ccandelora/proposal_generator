"""Brand Analyzer Agent for analyzing brand elements and consistency."""

from typing import Dict, Any, List
from crewai import Agent
from ..models.task_context import TaskContext
from ..utils.color_utils import normalize_color, hex_to_hsl
from ..utils.html_utils import extract_text_content, get_element_styles

class BrandAnalyzerAgent(Agent):
    """Agent responsible for analyzing brand elements and consistency."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role="Brand Analysis Expert",
            goal="Analyze brand elements and consistency across websites",
            backstory="""You are an expert in brand analysis with deep knowledge 
            of brand identity, visual consistency, and brand messaging.""",
            **kwargs
        )

    def analyze_brand(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze brand elements from screenshot and HTML content."""
        if not context.html_content or not context.driver:
            return {"error": "Missing required screenshot or HTML content"}

        # Get text and style information
        text_content = extract_text_content(context.driver)
        styles = get_element_styles(context.driver)
        
        # Perform brand analysis
        visual_identity = self._analyze_visual_identity(styles)
        messaging = self._analyze_messaging(text_content)
        consistency = self._analyze_consistency(context)
        
        return {
            "visual_identity": visual_identity,
            "messaging": messaging,
            "consistency": consistency
        }

    def _analyze_visual_identity(self, styles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze visual brand identity elements."""
        return {
            "color_scheme": self._analyze_color_scheme(styles),
            "typography": self._analyze_typography(styles),
            "logo_presence": self._analyze_logo_presence(styles)
        }

    def _analyze_color_scheme(self, styles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze brand color scheme usage."""
        colors = {}
        for style in styles:
            if "color" in style:
                color = normalize_color(style["color"])
                if color:
                    hsl = hex_to_hsl(color)
                    colors[color] = {
                        "hsl": hsl,
                        "frequency": colors.get(color, {}).get("frequency", 0) + 1
                    }
            if "background-color" in style:
                bg_color = normalize_color(style["background-color"])
                if bg_color:
                    hsl = hex_to_hsl(bg_color)
                    colors[bg_color] = {
                        "hsl": hsl,
                        "frequency": colors.get(bg_color, {}).get("frequency", 0) + 1
                    }
        
        # Identify primary and secondary colors
        sorted_colors = sorted(colors.items(), key=lambda x: x[1]["frequency"], reverse=True)
        
        return {
            "primary_colors": [color for color, _ in sorted_colors[:3]],
            "secondary_colors": [color for color, _ in sorted_colors[3:6]],
            "color_distribution": colors
        }

    def _analyze_typography(self, styles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze brand typography usage."""
        fonts = {}
        sizes = {}
        weights = {}
        
        for style in styles:
            if "font-family" in style:
                font = style["font-family"]
                fonts[font] = fonts.get(font, 0) + 1
            if "font-size" in style:
                size = style["font-size"]
                sizes[size] = sizes.get(size, 0) + 1
            if "font-weight" in style:
                weight = style["font-weight"]
                weights[weight] = weights.get(weight, 0) + 1
                
        return {
            "primary_font": max(fonts.items(), key=lambda x: x[1])[0] if fonts else None,
            "font_distribution": fonts,
            "size_distribution": sizes,
            "weight_distribution": weights
        }

    def _analyze_logo_presence(self, styles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logo presence and placement."""
        logo_indicators = [
            "logo", "brand", "company-name", "site-title"
        ]
        
        logo_elements = []
        for style in styles:
            element_class = style.get("class", "").lower()
            element_id = style.get("id", "").lower()
            
            if any(indicator in element_class or indicator in element_id 
                  for indicator in logo_indicators):
                logo_elements.append(style)
                
        return {
            "logo_count": len(logo_elements),
            "positions": [elem.get("position", "static") for elem in logo_elements]
        }

    def _analyze_messaging(self, text_content: str) -> Dict[str, Any]:
        """Analyze brand messaging and tone."""
        # Split into sentences for analysis
        sentences = [s.strip() for s in text_content.split(".") if s.strip()]
        
        return {
            "message_count": len(sentences),
            "tone_indicators": self._analyze_tone(sentences),
            "key_phrases": self._extract_key_phrases(sentences)
        }

    def _analyze_tone(self, sentences: List[str]) -> Dict[str, int]:
        """Analyze the tone of brand messaging."""
        tone_indicators = {
            "professional": ["expert", "professional", "leading", "trusted"],
            "friendly": ["welcome", "help", "support", "together"],
            "innovative": ["innovative", "cutting-edge", "advanced", "modern"],
            "authoritative": ["best", "top", "premier", "superior"]
        }
        
        tone_counts = {tone: 0 for tone in tone_indicators}
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for tone, indicators in tone_indicators.items():
                if any(indicator in sentence_lower for indicator in indicators):
                    tone_counts[tone] += 1
                    
        return tone_counts

    def _extract_key_phrases(self, sentences: List[str]) -> List[str]:
        """Extract key brand phrases and messaging."""
        key_phrase_indicators = [
            "mission", "vision", "values", "promise", "commitment",
            "dedicated", "specializing", "leading"
        ]
        
        key_phrases = []
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in key_phrase_indicators):
                key_phrases.append(sentence)
                
        return key_phrases[:5]  # Return top 5 key phrases

    def _analyze_consistency(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze brand consistency across pages and competitors."""
        competitor_consistency = {}
        
        if context.competitor_data:
            for competitor in context.competitor_data:
                if "visual_identity" in competitor:
                    similarity = self._calculate_brand_similarity(
                        competitor["visual_identity"],
                        self._analyze_visual_identity(get_element_styles(context.driver))
                    )
                    competitor_consistency[competitor.get("name", "unnamed")] = similarity
                    
        return {
            "competitor_consistency": competitor_consistency,
            "brand_strength": self._calculate_brand_strength(context)
        }

    def _calculate_brand_similarity(self, brand1: Dict[str, Any], 
                                  brand2: Dict[str, Any]) -> float:
        """Calculate similarity between two brand identities."""
        similarity_score = 0.0
        
        # Compare color schemes
        if "color_scheme" in brand1 and "color_scheme" in brand2:
            common_colors = set(brand1["color_scheme"].get("primary_colors", [])) & \
                          set(brand2["color_scheme"].get("primary_colors", []))
            similarity_score += len(common_colors) * 0.2
            
        # Compare typography
        if "typography" in brand1 and "typography" in brand2:
            if brand1["typography"].get("primary_font") == \
               brand2["typography"].get("primary_font"):
                similarity_score += 0.3
                
        return min(similarity_score, 1.0)

    def _calculate_brand_strength(self, context: TaskContext) -> float:
        """Calculate overall brand strength score."""
        strength_score = 0.0
        
        # Check for consistent visual identity
        visual_identity = self._analyze_visual_identity(get_element_styles(context.driver))
        if visual_identity["color_scheme"]["primary_colors"]:
            strength_score += 0.3
        if visual_identity["typography"]["primary_font"]:
            strength_score += 0.2
            
        # Check for logo presence
        if visual_identity["logo_presence"]["logo_count"] > 0:
            strength_score += 0.2
            
        # Check for clear messaging
        text_content = extract_text_content(context.driver)
        messaging = self._analyze_messaging(text_content)
        if messaging["key_phrases"]:
            strength_score += 0.3
            
        return min(strength_score, 1.0) 