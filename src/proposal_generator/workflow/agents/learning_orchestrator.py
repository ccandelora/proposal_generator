from typing import Dict, Any, List, Optional
import logging
from .learning_system import AdaptiveLearningSystem
from .validation_system import ValidationSystem

logger = logging.getLogger(__name__)

class LearningOrchestrator:
    """Orchestrates learning and validation processes."""
    
    def __init__(self):
        self.learning_system = AdaptiveLearningSystem()
        self.validation_system = ValidationSystem()
        self.visualization_cache = {}
    
    async def process_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process new interaction and update learning."""
        try:
            # Learn from interaction
            learning_metrics = await self.learning_system.learn_from_interaction(
                interaction_data
            )
            
            # Validate learning
            validation_results = await self.validation_system.validate_learning(
                self.learning_system.models,
                interaction_data
            )
            
            # Generate visualizations
            visualizations = self._generate_visualizations(
                learning_metrics,
                validation_results
            )
            
            # Cache visualizations
            self.visualization_cache.update(visualizations)
            
            return {
                'learning_metrics': learning_metrics,
                'validation_results': validation_results,
                'visualizations': visualizations
            }
            
        except Exception as e:
            logger.error(f"Error processing interaction: {str(e)}")
            return self._generate_fallback_response()
    
    def _generate_visualizations(self, metrics: Dict[str, Any], 
                               validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive visualizations."""
        try:
            return {
                'learning': self.learning_system.visualize_learning_progress(),
                'validation': self.validation_system.visualize_validation_results(),
                'combined': self._create_combined_visualization(metrics, validation)
            }
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return {} 