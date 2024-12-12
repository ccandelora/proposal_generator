"""UX Capture Agent for analyzing user experience elements."""

from typing import Dict, Any, List
from crewai import Agent
from ..models.task_context import TaskContext
from ..utils.html_utils import extract_text_content

class UXCaptureAgent(Agent):
    """Agent responsible for analyzing user experience elements."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role="UX Analysis Expert",
            goal="Analyze user experience elements and interactions in websites",
            backstory="""You are an expert in user experience analysis with deep knowledge 
            of interaction design, accessibility, and usability principles.""",
            **kwargs
        )

    def analyze_ux(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze UX elements from screenshot and HTML content."""
        if not context.html_content or not context.driver:
            return {"error": "Missing required screenshot or HTML content"}

        # Extract text content for analysis
        text_content = extract_text_content(context.driver)
        
        # Analyze various UX aspects
        navigation = self._analyze_navigation(context)
        forms = self._analyze_forms(context)
        accessibility = self._analyze_accessibility(context)
        content_structure = self._analyze_content_structure(text_content)
        
        return {
            "navigation": navigation,
            "forms": forms,
            "accessibility": accessibility,
            "content_structure": content_structure
        }

    def _analyze_navigation(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze navigation elements and patterns."""
        nav_elements = context.driver.find_elements_by_tag_name("nav")
        links = context.driver.find_elements_by_tag_name("a")
        
        return {
            "nav_count": len(nav_elements),
            "link_count": len(links),
            "menu_structure": self._analyze_menu_structure(nav_elements)
        }

    def _analyze_menu_structure(self, nav_elements: List[Any]) -> Dict[str, Any]:
        """Analyze menu structure and hierarchy."""
        menu_structure = {}
        for nav in nav_elements:
            menu_items = nav.find_elements_by_tag_name("li")
            menu_structure[nav.get_attribute("class")] = {
                "items": len(menu_items),
                "depth": self._calculate_menu_depth(nav)
            }
        return menu_structure

    def _calculate_menu_depth(self, element: Any) -> int:
        """Calculate the depth of nested menus."""
        max_depth = 0
        submenus = element.find_elements_by_tag_name("ul")
        
        for submenu in submenus:
            depth = len(submenu.find_elements_by_xpath("./ancestor::ul"))
            max_depth = max(max_depth, depth)
            
        return max_depth

    def _analyze_forms(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze form elements and interactions."""
        forms = context.driver.find_elements_by_tag_name("form")
        form_analysis = {}
        
        for form in forms:
            inputs = form.find_elements_by_tag_name("input")
            form_analysis[form.get_attribute("id") or "unnamed_form"] = {
                "input_count": len(inputs),
                "input_types": self._get_input_types(inputs),
                "has_validation": bool(form.find_elements_by_css_selector("[required]"))
            }
            
        return form_analysis

    def _get_input_types(self, inputs: List[Any]) -> Dict[str, int]:
        """Get distribution of input types in a form."""
        type_count = {}
        for input_elem in inputs:
            input_type = input_elem.get_attribute("type") or "text"
            type_count[input_type] = type_count.get(input_type, 0) + 1
        return type_count

    def _analyze_accessibility(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze accessibility features."""
        return {
            "alt_texts": self._check_alt_texts(context),
            "aria_labels": self._check_aria_labels(context),
            "heading_structure": self._analyze_heading_structure(context)
        }

    def _check_alt_texts(self, context: TaskContext) -> Dict[str, Any]:
        """Check for presence and quality of alt texts."""
        images = context.driver.find_elements_by_tag_name("img")
        return {
            "total_images": len(images),
            "with_alt": len([img for img in images if img.get_attribute("alt")])
        }

    def _check_aria_labels(self, context: TaskContext) -> Dict[str, Any]:
        """Check for ARIA labels and roles."""
        elements_with_aria = context.driver.find_elements_by_css_selector("[aria-label]")
        elements_with_role = context.driver.find_elements_by_css_selector("[role]")
        
        return {
            "aria_labels": len(elements_with_aria),
            "aria_roles": len(elements_with_role)
        }

    def _analyze_heading_structure(self, context: TaskContext) -> Dict[str, Any]:
        """Analyze heading hierarchy."""
        heading_counts = {}
        for i in range(1, 7):
            headings = context.driver.find_elements_by_tag_name(f"h{i}")
            if headings:
                heading_counts[f"h{i}"] = len(headings)
        return heading_counts

    def _analyze_content_structure(self, text_content: str) -> Dict[str, Any]:
        """Analyze content structure and readability."""
        paragraphs = text_content.split("\n\n")
        words = text_content.split()
        
        return {
            "paragraph_count": len(paragraphs),
            "average_paragraph_length": len(words) / len(paragraphs) if paragraphs else 0,
            "total_words": len(words)
        } 