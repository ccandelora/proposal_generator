from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging
from sklearn.metrics import cohen_kappa_score
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class FeedbackEvaluation:
    """Comprehensive feedback evaluation metrics."""
    content_quality: float
    technical_accuracy: float
    implementation_feasibility: float
    innovation_level: float
    risk_assessment: float
    resource_efficiency: float
    scalability: float
    maintainability: float
    security_compliance: float
    user_experience: float
    cross_functional_impact: float
    long_term_viability: float

class FeedbackEvaluator:
    """Enhanced feedback evaluation system."""
    
    def __init__(self):
        self.historical_evaluations: List[FeedbackEvaluation] = []
        self.evaluation_weights = self._initialize_weights()
    
    async def evaluate_feedback(self, feedback: Dict[str, Any]) -> FeedbackEvaluation:
        """Perform comprehensive feedback evaluation."""
        try:
            # Extract feedback components
            content = self._extract_content_feedback(feedback)
            technical = self._extract_technical_feedback(feedback)
            implementation = self._extract_implementation_feedback(feedback)
            
            # Calculate primary metrics
            content_quality = self._evaluate_content_quality(content)
            technical_accuracy = self._evaluate_technical_accuracy(technical)
            implementation_feasibility = self._evaluate_implementation_feasibility(implementation)
            
            # Calculate advanced metrics
            evaluation = FeedbackEvaluation(
                content_quality=content_quality,
                technical_accuracy=technical_accuracy,
                implementation_feasibility=implementation_feasibility,
                innovation_level=self._evaluate_innovation(feedback),
                risk_assessment=self._evaluate_risks(feedback),
                resource_efficiency=self._evaluate_efficiency(feedback),
                scalability=self._evaluate_scalability(feedback),
                maintainability=self._evaluate_maintainability(feedback),
                security_compliance=self._evaluate_security(feedback),
                user_experience=self._evaluate_user_experience(feedback),
                cross_functional_impact=self._evaluate_cross_functional_impact(feedback),
                long_term_viability=self._evaluate_long_term_viability(feedback)
            )
            
            # Store evaluation for learning
            self.historical_evaluations.append(evaluation)
            
            # Update weights based on new data
            self._update_weights(evaluation)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating feedback: {str(e)}")
            return self._generate_default_evaluation() 