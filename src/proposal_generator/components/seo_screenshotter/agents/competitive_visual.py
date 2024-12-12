"""Competitive Visual Agent for analyzing competitive visual elements."""

from typing import Dict, Any, List
from crewai import Agent
from ..models.task_context import TaskContext
from ..utils.color_utils import normalize_color, hex_to_hsl
from ..utils.html_utils import extract_text_content, get_element_styles

class CompetitiveVisualAgent(Agent):
    """Agent responsible for analyzing competitive visual elements."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role="Competitive Analysis Expert",
            goal="Analyze and compare visual elements across competitor websites",
            backstory="""You are an expert in competitive analysis with deep knowledge 
            of visual design trends, market positioning, and competitive differentiation.""",
            **kwargs
        )

    def analyze_competitive(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze competitive visual elements from screenshot and HTML content."""
        if not context.html_content or not context.driver or not context.competitor_data:
            return {"error": "Missing required data for competitive analysis"}

        # Get current site's visual elements
        current_styles = get_element_styles(context.driver)
        current_text = extract_text_content(context.driver)
        
        # Analyze competitive aspects
        visual_comparison = self._analyze_visual_comparison(current_styles, context)
        content_comparison = self._analyze_content_comparison(current_text, context)
        market_positioning = self._analyze_market_positioning(context)
        
        return {
            "visual_comparison": visual_comparison,
            "content_comparison": content_comparison,
            "market_positioning": market_positioning,
            "differentiation_score": self._calculate_differentiation_score(context)
        }

    def _analyze_visual_comparison(self, current_styles: List[Dict[str, Any]], 
                                 context: TaskContext) -> Dict[str, Any]:
        """Compare visual elements with competitors."""
        comparisons = {}
        
        for competitor in context.competitor_data:
            if "styles" in competitor:
                comp_name = competitor.get("name", "unnamed")
                comparisons[comp_name] = {
                    "color_similarity": self._compare_colors(
                        current_styles, competitor["styles"]
                    ),
                    "layout_similarity": self._compare_layouts(
                        current_styles, competitor["styles"]
                    ),
                    "typography_similarity": self._compare_typography(
                        current_styles, competitor["styles"]
                    )
                }
                
        return {
            "competitor_comparisons": comparisons,
            "unique_elements": self._identify_unique_elements(current_styles, context)
        }

    def _compare_colors(self, styles1: List[Dict[str, Any]], 
                       styles2: List[Dict[str, Any]]) -> float:
        """Compare color schemes between two sites."""
        colors1 = set()
        colors2 = set()
        
        for style in styles1:
            if "color" in style:
                color = normalize_color(style["color"])
                if color:
                    colors1.add(color)
            if "background-color" in style:
                bg_color = normalize_color(style["background-color"])
                if bg_color:
                    colors1.add(bg_color)
                    
        for style in styles2:
            if "color" in style:
                color = normalize_color(style["color"])
                if color:
                    colors2.add(color)
            if "background-color" in style:
                bg_color = normalize_color(style["background-color"])
                if bg_color:
                    colors2.add(bg_color)
                    
        if not colors1 or not colors2:
            return 0.0
            
        similarity = len(colors1.intersection(colors2)) / len(colors1.union(colors2))
        return similarity

    def _compare_layouts(self, styles1: List[Dict[str, Any]], 
                        styles2: List[Dict[str, Any]]) -> float:
        """Compare layout patterns between two sites."""
        layout_patterns1 = self._extract_layout_patterns(styles1)
        layout_patterns2 = self._extract_layout_patterns(styles2)
        
        if not layout_patterns1 or not layout_patterns2:
            return 0.0
            
        common_patterns = set(layout_patterns1.keys()) & set(layout_patterns2.keys())
        all_patterns = set(layout_patterns1.keys()) | set(layout_patterns2.keys())
        
        if not all_patterns:
            return 0.0
            
        return len(common_patterns) / len(all_patterns)

    def _extract_layout_patterns(self, styles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract layout patterns from styles."""
        patterns = {}
        for style in styles:
            if "display" in style:
                patterns[f"display_{style['display']}"] = \
                    patterns.get(f"display_{style['display']}", 0) + 1
            if "position" in style:
                patterns[f"position_{style['position']}"] = \
                    patterns.get(f"position_{style['position']}", 0) + 1
            if "flex-direction" in style:
                patterns[f"flex_{style['flex-direction']}"] = \
                    patterns.get(f"flex_{style['flex-direction']}", 0) + 1
        return patterns

    def _compare_typography(self, styles1: List[Dict[str, Any]], 
                          styles2: List[Dict[str, Any]]) -> float:
        """Compare typography between two sites."""
        fonts1 = self._extract_typography(styles1)
        fonts2 = self._extract_typography(styles2)
        
        if not fonts1 or not fonts2:
            return 0.0
            
        common_fonts = set(fonts1.keys()) & set(fonts2.keys())
        all_fonts = set(fonts1.keys()) | set(fonts2.keys())
        
        if not all_fonts:
            return 0.0
            
        return len(common_fonts) / len(all_fonts)

    def _extract_typography(self, styles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract typography information from styles."""
        fonts = {}
        for style in styles:
            if "font-family" in style:
                font = style["font-family"]
                fonts[font] = fonts.get(font, 0) + 1
        return fonts

    def _identify_unique_elements(self, current_styles: List[Dict[str, Any]], 
                                context: TaskContext) -> List[Dict[str, Any]]:
        """Identify unique visual elements not present in competitor sites."""
        unique_elements = []
        competitor_elements = set()
        
        # Collect all competitor elements
        for competitor in context.competitor_data:
            if "styles" in competitor:
                for style in competitor["styles"]:
                    element_key = f"{style.get('tag', '')}_{style.get('class', '')}"
                    competitor_elements.add(element_key)
        
        # Find unique elements
        for style in current_styles:
            element_key = f"{style.get('tag', '')}_{style.get('class', '')}"
            if element_key not in competitor_elements:
                unique_elements.append({
                    "element_type": style.get("tag", "unknown"),
                    "class": style.get("class", ""),
                    "styles": style
                })
                
        return unique_elements[:5]  # Return top 5 unique elements

    def _analyze_content_comparison(self, current_text: str, 
                                  context: TaskContext) -> Dict[str, Any]:
        """Compare content patterns with competitors."""
        current_patterns = self._extract_content_patterns(current_text)
        competitor_patterns = {}
        
        for competitor in context.competitor_data:
            if "text_content" in competitor:
                comp_name = competitor.get("name", "unnamed")
                comp_patterns = self._extract_content_patterns(competitor["text_content"])
                competitor_patterns[comp_name] = {
                    "similarity": self._calculate_pattern_similarity(
                        current_patterns, comp_patterns
                    ),
                    "patterns": comp_patterns
                }
                
        return {
            "current_patterns": current_patterns,
            "competitor_patterns": competitor_patterns
        }

    def _extract_content_patterns(self, text: str) -> Dict[str, Any]:
        """Extract content patterns from text."""
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        
        return {
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            "keyword_density": self._calculate_keyword_density(text),
            "content_structure": self._analyze_content_structure(sentences)
        }

    def _calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """Calculate keyword density in text."""
        words = text.lower().split()
        total_words = len(words)
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Convert to density
        return {word: count/total_words 
                for word, count in sorted(word_freq.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True)[:10]}

    def _analyze_content_structure(self, sentences: List[str]) -> Dict[str, Any]:
        """Analyze content structure patterns."""
        return {
            "total_sentences": len(sentences),
            "sentence_types": self._categorize_sentences(sentences)
        }

    def _categorize_sentences(self, sentences: List[str]) -> Dict[str, int]:
        """Categorize sentences by type."""
        categories = {
            "question": ["?", "what", "how", "why", "when", "where", "who"],
            "statement": [".", "is", "are", "was", "were"],
            "call_to_action": ["click", "sign up", "contact", "learn more", "get"]
        }
        
        sentence_types = {category: 0 for category in categories}
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for category, indicators in categories.items():
                if any(indicator in sentence_lower for indicator in indicators):
                    sentence_types[category] += 1
                    
        return sentence_types

    def _analyze_market_positioning(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze market positioning based on visual elements."""
        positioning_scores = {
            "premium": self._calculate_premium_score(context),
            "innovative": self._calculate_innovative_score(context),
            "trustworthy": self._calculate_trust_score(context),
            "user_friendly": self._calculate_usability_score(context)
        }
        
        return {
            "positioning_scores": positioning_scores,
            "market_segment": self._determine_market_segment(positioning_scores),
            "competitive_advantages": self._identify_competitive_advantages(context)
        }

    def _calculate_premium_score(self, context: TaskContext) -> float:
        """Calculate premium positioning score."""
        score = 0.0
        styles = get_element_styles(context.driver)
        
        # Check for premium design elements
        for style in styles:
            if "box-shadow" in style or "gradient" in style.get("background-image", ""):
                score += 0.1
            if "animation" in style or "transition" in style:
                score += 0.1
                
        # Check for premium typography
        if any("serif" in style.get("font-family", "").lower() for style in styles):
            score += 0.2
            
        return min(score, 1.0)

    def _calculate_innovative_score(self, context: TaskContext) -> float:
        """Calculate innovative positioning score."""
        score = 0.0
        styles = get_element_styles(context.driver)
        
        # Check for modern design elements
        for style in styles:
            if "transform" in style or "animation" in style:
                score += 0.15
            if "grid" in style.get("display", "") or "flex" in style.get("display", ""):
                score += 0.15
                
        # Check for innovative features
        if context.html_content and "data-" in context.html_content:
            score += 0.2
            
        return min(score, 1.0)

    def _calculate_trust_score(self, context: TaskContext) -> float:
        """Calculate trust positioning score."""
        score = 0.0
        text = extract_text_content(context.driver)
        
        # Check for trust indicators
        trust_words = ["secure", "trusted", "certified", "guaranteed", "privacy"]
        for word in trust_words:
            if word in text.lower():
                score += 0.15
                
        # Check for security elements
        if "https" in context.html_content:
            score += 0.2
        if "privacy-policy" in context.html_content or "terms-of-service" in context.html_content:
            score += 0.15
            
        return min(score, 1.0)

    def _calculate_usability_score(self, context: TaskContext) -> float:
        """Calculate usability positioning score."""
        score = 0.0
        styles = get_element_styles(context.driver)
        
        # Check for user-friendly elements
        for style in styles:
            if "hover" in style or "focus" in style:
                score += 0.1
            if "padding" in style and float(style.get("padding", "0").replace("px", "")) > 10:
                score += 0.1
                
        # Check for navigation elements
        if context.driver.find_elements_by_tag_name("nav"):
            score += 0.2
        if context.driver.find_elements_by_tag_name("button"):
            score += 0.1
            
        return min(score, 1.0)

    def _determine_market_segment(self, scores: Dict[str, float]) -> str:
        """Determine market segment based on positioning scores."""
        max_score = max(scores.items(), key=lambda x: x[1])
        if max_score[1] > 0.7:
            return f"High-end {max_score[0]}"
        elif max_score[1] > 0.4:
            return f"Mid-market {max_score[0]}"
        else:
            return "Mass market"

    def _identify_competitive_advantages(self, context: TaskContext) -> List[Dict[str, Any]]:
        """Identify competitive advantages based on visual analysis."""
        advantages = []
        styles = get_element_styles(context.driver)
        
        # Check for unique design elements
        unique_elements = self._identify_unique_elements(styles, context)
        if unique_elements:
            advantages.append({
                "type": "unique_design",
                "elements": unique_elements
            })
            
        # Check for superior usability
        usability_score = self._calculate_usability_score(context)
        competitor_usability = []
        for competitor in context.competitor_data:
            if "usability_score" in competitor:
                competitor_usability.append(competitor["usability_score"])
                
        if competitor_usability and usability_score > max(competitor_usability):
            advantages.append({
                "type": "superior_usability",
                "score_difference": usability_score - max(competitor_usability)
            })
            
        return advantages

    def _calculate_differentiation_score(self, context: TaskContext) -> float:
        """Calculate overall differentiation score."""
        score = 0.0
        
        # Check visual uniqueness
        unique_elements = self._identify_unique_elements(
            get_element_styles(context.driver), context
        )
        score += len(unique_elements) * 0.1
        
        # Check positioning uniqueness
        positioning = self._analyze_market_positioning(context)
        competitor_segments = set()
        for competitor in context.competitor_data:
            if "market_segment" in competitor:
                competitor_segments.add(competitor["market_segment"])
                
        if positioning["market_segment"] not in competitor_segments:
            score += 0.3
            
        # Check content uniqueness
        content_comparison = self._analyze_content_comparison(
            extract_text_content(context.driver), context
        )
        
        # Calculate average similarity only if there are competitor patterns
        competitor_patterns = content_comparison["competitor_patterns"]
        if competitor_patterns:
            avg_similarity = sum(comp["similarity"] 
                               for comp in competitor_patterns.values()) / \
                            len(competitor_patterns)
            score += (1 - avg_similarity) * 0.3
        else:
            # If no competitor patterns, assume maximum differentiation for this aspect
            score += 0.3
        
        return min(score, 1.0) 