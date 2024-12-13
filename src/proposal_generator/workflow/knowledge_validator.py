"""Knowledge source validation system."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)

class KnowledgeValidationRule(BaseModel):
    """Validation rule for knowledge sources."""
    required_sections: List[str] = Field(default_factory=list)
    required_keywords: List[str] = Field(default_factory=list)
    min_length: int = Field(default=100)
    max_length: int = Field(default=10000)
    format_rules: List[str] = Field(default_factory=list)

class KnowledgeValidator:
    """Validator for knowledge sources."""
    
    def __init__(self):
        self.validation_rules = {
            'pricing': KnowledgeValidationRule(
                required_sections=['Base Pricing', 'Feature Costs', 'Timeline Factors'],
                required_keywords=['cost', 'price', 'budget', 'investment'],
                min_length=200,
                format_rules=['Must include numeric values', 'Must include price ranges']
            ),
            'technical': KnowledgeValidationRule(
                required_sections=['Technologies', 'Architecture', 'Infrastructure'],
                required_keywords=['implementation', 'development', 'deployment'],
                min_length=300
            ),
            'industry': KnowledgeValidationRule(
                required_sections=['Features', 'Requirements', 'Best Practices'],
                required_keywords=['industry', 'specific', 'requirements'],
                min_length=250
            )
        }
    
    def validate_knowledge_source(self, content: str, source_type: str) -> Dict[str, Any]:
        """Validate a knowledge source against its rules."""
        try:
            rule = self.validation_rules.get(source_type)
            if not rule:
                return {'valid': False, 'errors': ['Unknown source type']}
            
            errors = []
            
            # Check length
            if len(content) < rule.min_length:
                errors.append(f'Content too short (min {rule.min_length} chars)')
            if len(content) > rule.max_length:
                errors.append(f'Content too long (max {rule.max_length} chars)')
            
            # Check required sections
            for section in rule.required_sections:
                if section.lower() not in content.lower():
                    errors.append(f'Missing required section: {section}')
            
            # Check required keywords
            for keyword in rule.required_keywords:
                if keyword.lower() not in content.lower():
                    errors.append(f'Missing required keyword: {keyword}')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
        except Exception as e:
            logger.error(f"Error validating knowledge source: {str(e)}")
            return {'valid': False, 'errors': [str(e)]} 