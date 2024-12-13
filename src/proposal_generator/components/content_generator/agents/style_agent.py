"""Style guide agent for maintaining consistent branding and tone."""
from typing import Dict, Any, List, Optional
import logging
from ..models.content_model import ContentTone

logger = logging.getLogger(__name__)

class StyleGuideAgent:
    """Agent responsible for maintaining consistent style and branding."""
    
    def __init__(self, progress_callback=None):
        """Initialize style guide agent."""
        self.style_rules = {
            'tone': {},
            'branding': {},
            'formatting': {},
            'language': {}
        }
        self.progress_callback = progress_callback

    def configure_style_guide(self, style_config: Dict[str, Any]) -> None:
        """Configure style guide rules."""
        try:
            # Configure tone rules
            self.style_rules['tone'] = {
                'formal': {
                    'word_choice': ['professional', 'precise', 'objective'],
                    'sentence_structure': 'complex',
                    'prohibited_words': ['slang', 'contractions']
                },
                'technical': {
                    'word_choice': ['specific', 'technical', 'detailed'],
                    'sentence_structure': 'logical',
                    'prohibited_words': ['vague', 'ambiguous']
                },
                'persuasive': {
                    'word_choice': ['compelling', 'action-oriented', 'benefit-focused'],
                    'sentence_structure': 'varied',
                    'prohibited_words': ['weak', 'uncertain']
                }
            }

            # Configure branding rules
            self.style_rules['branding'] = {
                'company_name': style_config.get('company_name', ''),
                'tagline': style_config.get('tagline', ''),
                'values': style_config.get('values', []),
                'voice': style_config.get('voice', 'professional')
            }

            # Configure formatting rules
            self.style_rules['formatting'] = {
                'headings': {
                    'h1': {'case': 'title', 'style': 'bold'},
                    'h2': {'case': 'sentence', 'style': 'bold'},
                    'h3': {'case': 'sentence', 'style': 'regular'}
                },
                'lists': {'style': 'bullet', 'max_items': 7},
                'paragraphs': {'max_length': 150}
            }

            # Configure language rules
            self.style_rules['language'] = {
                'preferred_terms': style_config.get('preferred_terms', {}),
                'avoided_terms': style_config.get('avoided_terms', []),
                'industry_terms': style_config.get('industry_terms', [])
            }

        except Exception as e:
            logger.error(f"Error configuring style guide: {str(e)}")

    def apply_style_rules(self, content: str, tone: ContentTone) -> str:
        """Apply style rules to content."""
        try:
            if self.progress_callback:
                self.progress_callback("Starting style application...", 0)
            
            # Apply tone rules
            if self.progress_callback:
                self.progress_callback("Applying tone rules...", 20)
            content = self._apply_tone_rules(content, tone)
            
            # Apply branding rules
            if self.progress_callback:
                self.progress_callback("Applying branding guidelines...", 40)
            content = self._apply_branding_rules(content)
            
            # Apply formatting rules
            if self.progress_callback:
                self.progress_callback("Formatting content...", 60)
            content = self._apply_formatting_rules(content)
            
            # Apply language rules
            if self.progress_callback:
                self.progress_callback("Optimizing language...", 80)
            content = self._apply_language_rules(content)
            
            # Validate final content
            if self.progress_callback:
                self.progress_callback("Validating style rules...", 90)
            violations = self.validate_style(content, tone)
            
            if not violations:
                if self.progress_callback:
                    self.progress_callback("Style application complete", 100)
            else:
                if self.progress_callback:
                    self.progress_callback(f"Found {len(violations)} style violations", 95)
            
            return content

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error applying style: {str(e)}", 0)
            return content

    def validate_style(self, content: str, tone: ContentTone) -> Dict[str, Any]:
        """Validate content against style rules."""
        try:
            violations = {
                'tone': [],
                'branding': [],
                'formatting': [],
                'language': []
            }

            # Check tone violations
            tone_rules = self.style_rules['tone'].get(tone.value, {})
            for prohibited in tone_rules.get('prohibited_words', []):
                if prohibited.lower() in content.lower():
                    violations['tone'].append(f"Found prohibited word: {prohibited}")

            # Check branding violations
            company_name = self.style_rules['branding']['company_name']
            if company_name and company_name not in content:
                violations['branding'].append("Company name not mentioned")

            # Check formatting violations
            paragraphs = content.split('\n\n')
            for i, para in enumerate(paragraphs):
                if len(para.split()) > self.style_rules['formatting']['paragraphs']['max_length']:
                    violations['formatting'].append(f"Paragraph {i+1} exceeds maximum length")

            # Check language violations
            for term in self.style_rules['language']['avoided_terms']:
                if term.lower() in content.lower():
                    violations['language'].append(f"Found avoided term: {term}")

            return violations

        except Exception as e:
            logger.error(f"Error validating style: {str(e)}")
            return {'error': str(e)}

    def _apply_tone_rules(self, content: str, tone: ContentTone) -> str:
        """Apply tone-specific rules to content."""
        try:
            tone_rules = self.style_rules['tone'].get(tone.value, {})
            
            # Apply word choice rules
            for word_type in tone_rules.get('word_choice', []):
                content = self._enhance_word_choice(content, word_type)
                
            return content

        except Exception as e:
            logger.error(f"Error applying tone rules: {str(e)}")
            return content

    def _apply_branding_rules(self, content: str) -> str:
        """Apply branding rules to content."""
        try:
            branding = self.style_rules['branding']
            
            # Ensure consistent company name usage
            if branding['company_name']:
                content = content.replace('[COMPANY]', branding['company_name'])
                
            # Add tagline where appropriate
            if branding['tagline'] and '[TAGLINE]' in content:
                content = content.replace('[TAGLINE]', branding['tagline'])
                
            return content

        except Exception as e:
            logger.error(f"Error applying branding rules: {str(e)}")
            return content

    def _apply_formatting_rules(self, content: str) -> str:
        """Apply formatting rules to content."""
        try:
            formatting = self.style_rules['formatting']
            
            # Apply heading styles
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    lines[i] = self._format_heading(line, formatting['headings']['h1'])
                elif line.startswith('## '):
                    lines[i] = self._format_heading(line, formatting['headings']['h2'])
                elif line.startswith('### '):
                    lines[i] = self._format_heading(line, formatting['headings']['h3'])
                    
            return '\n'.join(lines)

        except Exception as e:
            logger.error(f"Error applying formatting rules: {str(e)}")
            return content

    def _apply_language_rules(self, content: str) -> str:
        """Apply language rules to content."""
        try:
            language = self.style_rules['language']
            
            # Replace terms with preferred alternatives
            for term, preferred in language['preferred_terms'].items():
                content = content.replace(term, preferred)
                
            return content

        except Exception as e:
            logger.error(f"Error applying language rules: {str(e)}")
            return content

    def _enhance_word_choice(self, content: str, word_type: str) -> str:
        """Enhance word choice based on type."""
        try:
            # Word choice enhancements based on type
            enhancements = {
                'professional': {
                    'good': 'excellent',
                    'bad': 'suboptimal',
                    'big': 'substantial'
                },
                'technical': {
                    'use': 'utilize',
                    'make': 'implement',
                    'fix': 'resolve'
                },
                'compelling': {
                    'help': 'empower',
                    'improve': 'transform',
                    'increase': 'maximize'
                }
            }
            
            word_map = enhancements.get(word_type, {})
            for original, enhanced in word_map.items():
                content = content.replace(f' {original} ', f' {enhanced} ')
                
            return content

        except Exception as e:
            logger.error(f"Error enhancing word choice: {str(e)}")
            return content

    def _format_heading(self, heading: str, style: Dict[str, str]) -> str:
        """Format heading according to style."""
        try:
            # Remove heading markers
            text = heading.lstrip('#').strip()
            
            # Apply case style
            if style['case'] == 'title':
                text = text.title()
            elif style['case'] == 'sentence':
                text = text.capitalize()
                
            # Apply text style
            if style['style'] == 'bold':
                text = f'**{text}**'
                
            return text

        except Exception as e:
            logger.error(f"Error formatting heading: {str(e)}")
            return heading