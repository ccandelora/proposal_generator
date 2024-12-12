"""Topic analysis agent."""
from typing import Dict, Any, List, Optional
import logging
from ..models.content_model import ContentRequest, ContentType, ContentTone

logger = logging.getLogger(__name__)

class TopicAnalyzerAgent:
    """Agent for analyzing topics and structuring content."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def analyze_topic(self, request: ContentRequest) -> Dict[str, Any]:
        """
        Analyze topic and generate content structure.
        
        Args:
            request: Content generation request
            
        Returns:
            Dict containing topic analysis and content structure
        """
        try:
            if self.progress_callback:
                self.progress_callback("Starting topic analysis...", 0)
            
            # Analyze requirements
            requirements = self._analyze_requirements(request)
            if self.progress_callback:
                self.progress_callback("Analyzing requirements...", 25)
            
            # Generate structure
            structure = self._generate_structure(request, requirements)
            if self.progress_callback:
                self.progress_callback("Generating content structure...", 50)
            
            # Identify themes
            themes = self._identify_themes(request)
            if self.progress_callback:
                self.progress_callback("Identifying themes...", 75)
            
            # Generate outline
            outline = self._generate_outline(structure, themes)
            if self.progress_callback:
                self.progress_callback("Topic analysis complete", 100)
            
            return {
                'requirements': requirements,
                'structure': structure,
                'themes': themes,
                'outline': outline,
                'metadata': {
                    'content_type': request.content_type.value,
                    'tone': request.tone.value,
                    'target_audience': request.target_audience
                }
            }

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error in topic analysis: {str(e)}", 0)
            return self._create_empty_analysis()

    def _analyze_requirements(self, request: ContentRequest) -> Dict[str, Any]:
        """Analyze content requirements."""
        try:
            requirements = {
                'essential_elements': [],
                'optional_elements': [],
                'constraints': {}
            }
            
            # Add type-specific requirements
            if request.content_type == ContentType.PROPOSAL:
                requirements['essential_elements'].extend([
                    'executive_summary',
                    'problem_statement',
                    'proposed_solution',
                    'implementation_plan',
                    'pricing',
                    'timeline'
                ])
                requirements['optional_elements'].extend([
                    'case_studies',
                    'team_bios',
                    'testimonials'
                ])
                
            elif request.content_type == ContentType.TECHNICAL_SPEC:
                requirements['essential_elements'].extend([
                    'system_overview',
                    'architecture',
                    'components',
                    'interfaces',
                    'data_model'
                ])
                requirements['optional_elements'].extend([
                    'performance_requirements',
                    'security_considerations',
                    'deployment_guide'
                ])
                
            # Add tone-specific requirements
            if request.tone == ContentTone.TECHNICAL:
                requirements['constraints']['language'] = 'technical'
                requirements['constraints']['detail_level'] = 'high'
            elif request.tone == ContentTone.PERSUASIVE:
                requirements['constraints']['language'] = 'persuasive'
                requirements['constraints']['detail_level'] = 'medium'
                
            # Add length constraints
            if request.max_length:
                requirements['constraints']['max_length'] = request.max_length
                
            return requirements
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {str(e)}")
            return {'essential_elements': [], 'optional_elements': [], 'constraints': {}}

    def _generate_structure(self, request: ContentRequest, 
                          requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content structure."""
        try:
            structure = {
                'sections': [],
                'flow': [],
                'hierarchy': {}
            }
            
            # Add required sections
            for element in requirements['essential_elements']:
                structure['sections'].append({
                    'name': element,
                    'type': 'required',
                    'expected_length': self._estimate_section_length(element, request)
                })
                
            # Add optional sections if appropriate
            for element in requirements['optional_elements']:
                if self._should_include_optional_section(element, request):
                    structure['sections'].append({
                        'name': element,
                        'type': 'optional',
                        'expected_length': self._estimate_section_length(element, request)
                    })
                    
            # Define content flow
            structure['flow'] = self._determine_content_flow(structure['sections'])
            
            # Define section hierarchy
            structure['hierarchy'] = self._define_section_hierarchy(structure['sections'])
            
            return structure
            
        except Exception as e:
            logger.error(f"Error generating structure: {str(e)}")
            return {'sections': [], 'flow': [], 'hierarchy': {}}

    def _identify_themes(self, request: ContentRequest) -> List[Dict[str, Any]]:
        """Identify key themes from the request."""
        try:
            themes = []
            
            # Extract themes from key points
            for point in request.key_points:
                themes.append({
                    'name': point,
                    'type': 'key_point',
                    'relevance': self._calculate_theme_relevance(point, request)
                })
                
            # Extract themes from keywords
            for keyword in request.keywords:
                themes.append({
                    'name': keyword,
                    'type': 'keyword',
                    'relevance': self._calculate_theme_relevance(keyword, request)
                })
                
            # Sort themes by relevance
            themes.sort(key=lambda x: x['relevance'], reverse=True)
            
            return themes
            
        except Exception as e:
            logger.error(f"Error identifying themes: {str(e)}")
            return []

    def _generate_outline(self, structure: Dict[str, Any], 
                         themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content outline."""
        try:
            outline = {
                'sections': [],
                'themes_by_section': {},
                'estimated_lengths': {}
            }
            
            # Create outline for each section
            for section in structure['sections']:
                section_outline = {
                    'name': section['name'],
                    'subsections': self._generate_subsections(section, themes),
                    'key_points': self._identify_section_key_points(section, themes),
                    'expected_content': self._describe_expected_content(section)
                }
                outline['sections'].append(section_outline)
                
            # Map themes to sections
            outline['themes_by_section'] = self._map_themes_to_sections(
                outline['sections'],
                themes
            )
            
            # Estimate section lengths
            outline['estimated_lengths'] = {
                section['name']: section['expected_length']
                for section in structure['sections']
            }
            
            return outline
            
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            return {'sections': [], 'themes_by_section': {}, 'estimated_lengths': {}}

    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty topic analysis."""
        return {
            'requirements': {
                'essential_elements': [],
                'optional_elements': [],
                'constraints': {}
            },
            'structure': {
                'sections': [],
                'flow': [],
                'hierarchy': {}
            },
            'themes': [],
            'outline': {
                'sections': [],
                'themes_by_section': {},
                'estimated_lengths': {}
            },
            'metadata': {}
        }

    def _estimate_section_length(self, section: str, request: ContentRequest) -> int:
        """Estimate appropriate length for a section."""
        try:
            base_lengths = {
                'executive_summary': 300,
                'problem_statement': 400,
                'proposed_solution': 800,
                'implementation_plan': 600,
                'pricing': 300,
                'timeline': 300,
                'system_overview': 500,
                'architecture': 700,
                'components': 1000,
                'interfaces': 500,
                'data_model': 600
            }
            
            # Get base length
            base_length = base_lengths.get(section, 500)
            
            # Adjust for content type
            if request.content_type == ContentType.TECHNICAL_SPEC:
                base_length *= 1.5
            elif request.content_type == ContentType.EXECUTIVE_SUMMARY:
                base_length *= 0.7
                
            # Adjust for max length constraint
            if request.max_length:
                total_base_length = sum(base_lengths.values())
                if total_base_length > request.max_length:
                    base_length *= (request.max_length / total_base_length)
                    
            return int(base_length)
            
        except Exception:
            return 500

    def _should_include_optional_section(self, section: str, 
                                       request: ContentRequest) -> bool:
        """Determine if an optional section should be included."""
        try:
            # Include based on content type
            if request.content_type == ContentType.TECHNICAL_SPEC:
                technical_sections = [
                    'performance_requirements',
                    'security_considerations',
                    'deployment_guide'
                ]
                if section in technical_sections:
                    return True
                    
            # Include based on required sections
            if request.required_sections and section in request.required_sections:
                return True
                
            # Include based on reference data
            if request.reference_data and section in request.reference_data:
                return True
                
            return False
            
        except Exception:
            return False

    def _determine_content_flow(self, sections: List[Dict[str, Any]]) -> List[str]:
        """Determine logical flow of content sections."""
        try:
            # Extract section names
            section_names = [section['name'] for section in sections]
            
            # Define standard flows for different content types
            flows = {
                'proposal': [
                    'executive_summary',
                    'problem_statement',
                    'proposed_solution',
                    'implementation_plan',
                    'pricing',
                    'timeline'
                ],
                'technical_spec': [
                    'system_overview',
                    'architecture',
                    'components',
                    'interfaces',
                    'data_model'
                ]
            }
            
            # Find best matching flow
            for flow in flows.values():
                if all(section in section_names for section in flow):
                    return flow
                    
            # Default to original order
            return section_names
            
        except Exception:
            return []

    def _define_section_hierarchy(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define hierarchical relationship between sections."""
        try:
            hierarchy = {}
            
            for section in sections:
                name = section['name']
                hierarchy[name] = {
                    'level': self._determine_section_level(name),
                    'parent': self._determine_parent_section(name, sections),
                    'children': self._determine_child_sections(name, sections)
                }
                
            return hierarchy
            
        except Exception:
            return {}

    def _calculate_theme_relevance(self, theme: str, request: ContentRequest) -> float:
        """Calculate theme relevance score."""
        try:
            relevance = 0.0
            
            # Check presence in key points
            if theme in request.key_points:
                relevance += 0.4
                
            # Check presence in keywords
            if theme in request.keywords:
                relevance += 0.3
                
            # Check presence in reference data
            if request.reference_data:
                ref_data_str = str(request.reference_data)
                if theme.lower() in ref_data_str.lower():
                    relevance += 0.3
                    
            return min(1.0, relevance)
            
        except Exception:
            return 0.0

    def _generate_subsections(self, section: Dict[str, Any], 
                            themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate subsections for a section."""
        try:
            subsections = []
            
            # Get relevant themes
            relevant_themes = [
                theme for theme in themes
                if theme['relevance'] > 0.5
            ]
            
            # Create subsections based on section type
            if section['name'] == 'proposed_solution':
                subsections.extend([
                    {'name': 'Overview', 'themes': relevant_themes[:2]},
                    {'name': 'Key Features', 'themes': relevant_themes[2:5]},
                    {'name': 'Benefits', 'themes': relevant_themes[5:]}
                ])
            elif section['name'] == 'implementation_plan':
                subsections.extend([
                    {'name': 'Phases', 'themes': []},
                    {'name': 'Resources', 'themes': []},
                    {'name': 'Milestones', 'themes': []}
                ])
                
            return subsections
            
        except Exception:
            return []

    def _identify_section_key_points(self, section: Dict[str, Any], 
                                   themes: List[Dict[str, Any]]) -> List[str]:
        """Identify key points for a section."""
        try:
            # Get relevant themes
            relevant_themes = [
                theme['name'] for theme in themes
                if theme['relevance'] > 0.5
            ]
            
            # Select themes based on section
            if section['name'] == 'executive_summary':
                return relevant_themes[:3]
            elif section['name'] == 'problem_statement':
                return relevant_themes[3:6]
            else:
                return relevant_themes[:2]
                
        except Exception:
            return []

    def _describe_expected_content(self, section: Dict[str, Any]) -> str:
        """Generate description of expected content."""
        try:
            descriptions = {
                'executive_summary': 'Brief overview of the entire proposal',
                'problem_statement': 'Clear description of the challenge or need',
                'proposed_solution': 'Detailed description of the solution',
                'implementation_plan': 'Step-by-step plan for implementation',
                'pricing': 'Cost breakdown and pricing details',
                'timeline': 'Project timeline and milestones'
            }
            
            return descriptions.get(
                section['name'],
                f"Content for {section['name']}"
            )
            
        except Exception:
            return ""

    def _map_themes_to_sections(self, sections: List[Dict[str, Any]], 
                              themes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Map themes to relevant sections."""
        try:
            theme_map = {}
            
            for section in sections:
                theme_map[section['name']] = [
                    theme['name'] for theme in themes
                    if self._is_theme_relevant_to_section(theme, section)
                ]
                
            return theme_map
            
        except Exception:
            return {}

    def _is_theme_relevant_to_section(self, theme: Dict[str, Any], 
                                    section: Dict[str, Any]) -> bool:
        """Determine if a theme is relevant to a section."""
        try:
            # Check theme relevance score
            if theme['relevance'] < 0.5:
                return False
                
            # Check section-specific relevance
            if section['name'] == 'executive_summary':
                return theme['relevance'] > 0.8
            elif section['name'] == 'problem_statement':
                return theme['type'] == 'key_point'
            elif section['name'] == 'proposed_solution':
                return theme['type'] in ['key_point', 'keyword']
                
            return True
            
        except Exception:
            return False

    def _determine_section_level(self, section_name: str) -> int:
        """Determine hierarchy level for a section."""
        try:
            top_level_sections = {
                'executive_summary',
                'problem_statement',
                'proposed_solution',
                'implementation_plan'
            }
            
            return 1 if section_name in top_level_sections else 2
            
        except Exception:
            return 1

    def _determine_parent_section(self, section_name: str, 
                                sections: List[Dict[str, Any]]) -> Optional[str]:
        """Determine parent section if any."""
        try:
            section_hierarchy = {
                'performance_requirements': 'system_overview',
                'security_considerations': 'system_overview',
                'deployment_guide': 'implementation_plan',
                'case_studies': 'proposed_solution',
                'team_bios': 'implementation_plan',
                'testimonials': 'proposed_solution'
            }
            
            return section_hierarchy.get(section_name)
            
        except Exception:
            return None

    def _determine_child_sections(self, section_name: str, 
                                sections: List[Dict[str, Any]]) -> List[str]:
        """Determine child sections if any."""
        try:
            children = []
            
            for section in sections:
                parent = self._determine_parent_section(section['name'], sections)
                if parent == section_name:
                    children.append(section['name'])
                    
            return children
            
        except Exception:
            return []