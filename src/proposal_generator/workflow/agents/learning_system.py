from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """Metrics for learning system performance."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    learning_rate: float
    convergence_rate: float
    adaptation_speed: float
    prediction_confidence: float

class AdaptiveLearningSystem:
    """System for adaptive learning from agent interactions."""
    
    def __init__(self):
        self.models = {
            'feedback': RandomForestRegressor(),
            'resolution': RandomForestRegressor(),
            'synthesis': RandomForestRegressor()
        }
        self.historical_data = []
        self.performance_metrics = []
        self.validation_scores = []
    
    async def learn_from_interaction(self, interaction_data: Dict[str, Any]) -> LearningMetrics:
        """Learn from new interaction data."""
        try:
            # Process interaction data
            processed_data = self._process_interaction_data(interaction_data)
            
            # Update models
            metrics = await self._update_models(processed_data)
            
            # Validate learning
            validation_result = self._validate_learning(metrics)
            
            # Store results
            self._store_learning_results(processed_data, metrics, validation_result)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in learning system: {str(e)}")
            return self._generate_default_metrics()
    
    def visualize_learning_progress(self) -> Dict[str, Any]:
        """Generate visualizations of learning progress."""
        try:
            figures = {
                'learning_curve': self._create_learning_curve(),
                'performance_metrics': self._create_metrics_visualization(),
                'model_comparison': self._create_model_comparison(),
                'adaptation_analysis': self._create_adaptation_analysis()
            }
            return figures
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            return {}
    
    def _create_learning_curve(self) -> go.Figure:
        """Create learning curve visualization."""
        metrics_df = pd.DataFrame(self.performance_metrics)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics_df.index,
            y=metrics_df['accuracy'],
            mode='lines+markers',
            name='Accuracy'
        ))
        fig.add_trace(go.Scatter(
            x=metrics_df.index,
            y=metrics_df['learning_rate'],
            mode='lines',
            name='Learning Rate'
        ))
        
        fig.update_layout(
            title='Learning Progress Over Time',
            xaxis_title='Interactions',
            yaxis_title='Score',
            template='plotly_white'
        )
        
        return fig
    
    def _create_metrics_visualization(self) -> go.Figure:
        """Create performance metrics visualization."""
        metrics_df = pd.DataFrame(self.performance_metrics)
        
        fig = px.line(
            metrics_df,
            x=metrics_df.index,
            y=['precision', 'recall', 'f1_score'],
            title='Performance Metrics Evolution'
        )
        
        fig.update_layout(
            xaxis_title='Interactions',
            yaxis_title='Score',
            template='plotly_white'
        )
        
        return fig

class ValidationSystem:
    """Enhanced validation system with multiple methods."""
    
    def __init__(self):
        self.validation_methods = {
            'cross_validation': self._perform_cross_validation,
            'holdout_validation': self._perform_holdout_validation,
            'bootstrap_validation': self._perform_bootstrap_validation,
            'time_series_validation': self._perform_time_series_validation
        }
        self.validation_history = []
    
    async def validate_learning(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive validation."""
        try:
            validation_results = {}
            
            for method_name, method in self.validation_methods.items():
                result = await method(model, data)
                validation_results[method_name] = result
            
            # Aggregate validation results
            aggregated_results = self._aggregate_validation_results(validation_results)
            
            # Store validation history
            self._store_validation_results(aggregated_results)
            
            return aggregated_results
            
        except Exception as e:
            logger.error(f"Error in validation: {str(e)}")
            return self._generate_default_validation()
    
    async def _perform_cross_validation(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform k-fold cross validation."""
        try:
            cv_results = cross_validate(
                model,
                data['X'],
                data['y'],
                cv=5,
                scoring=['accuracy', 'precision', 'recall', 'f1']
            )
            
            return {
                'mean_scores': {
                    metric: np.mean(scores)
                    for metric, scores in cv_results.items()
                },
                'std_scores': {
                    metric: np.std(scores)
                    for metric, scores in cv_results.items()
                }
            }
        except Exception as e:
            logger.error(f"Error in cross validation: {str(e)}")
            return {}
    
    def visualize_validation_results(self) -> Dict[str, Any]:
        """Create visualizations of validation results."""
        try:
            figures = {
                'validation_comparison': self._create_validation_comparison(),
                'method_performance': self._create_method_performance(),
                'confidence_intervals': self._create_confidence_intervals(),
                'error_analysis': self._create_error_analysis()
            }
            return figures
        except Exception as e:
            logger.error(f"Error creating validation visualizations: {str(e)}")
            return {} 