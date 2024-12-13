from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import silhouette_score
import logging

logger = logging.getLogger(__name__)

@dataclass
class SynthesisMetrics:
    """Comprehensive metrics for result synthesis."""
    coherence_score: float
    diversity_score: float
    novelty_score: float
    relevance_score: float
    impact_score: float
    risk_score: float
    implementation_complexity: float
    resource_efficiency: float
    scalability_score: float
    maintainability_score: float
    confidence_intervals: Dict[str, tuple]
    cross_validation_scores: List[float]

class MetricsCalculator:
    """Calculator for synthesis metrics."""
    
    @staticmethod
    def calculate_metrics(synthesis: Dict[str, Any]) -> SynthesisMetrics:
        """Calculate comprehensive synthesis metrics."""
        try:
            return SynthesisMetrics(
                coherence_score=MetricsCalculator._calculate_coherence(synthesis),
                diversity_score=MetricsCalculator._calculate_diversity(synthesis),
                novelty_score=MetricsCalculator._calculate_novelty(synthesis),
                relevance_score=MetricsCalculator._calculate_relevance(synthesis),
                impact_score=MetricsCalculator._calculate_impact(synthesis),
                risk_score=MetricsCalculator._calculate_risk(synthesis),
                implementation_complexity=MetricsCalculator._calculate_complexity(synthesis),
                resource_efficiency=MetricsCalculator._calculate_efficiency(synthesis),
                scalability_score=MetricsCalculator._calculate_scalability(synthesis),
                maintainability_score=MetricsCalculator._calculate_maintainability(synthesis),
                confidence_intervals=MetricsCalculator._calculate_confidence_intervals(synthesis),
                cross_validation_scores=MetricsCalculator._perform_cross_validation(synthesis)
            )
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return MetricsCalculator._generate_default_metrics() 