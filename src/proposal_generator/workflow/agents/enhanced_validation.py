from typing import Dict, Any, List, Optional
import logging
from sklearn.model_selection import (
    cross_validate,
    TimeSeriesSplit,
    ShuffleSplit,
    StratifiedKFold
)
from sklearn.metrics import (
    make_scorer,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationConfig:
    """Configuration for validation methods."""
    cv_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    n_bootstrap: int = 1000
    time_series_splits: int = 3

class EnhancedValidation:
    """Enhanced validation system with multiple methods."""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.scorers = self._setup_scorers()
        self.validation_methods = {
            'standard_cv': self._standard_cross_validation,
            'stratified_cv': self._stratified_cross_validation,
            'time_series_cv': self._time_series_cross_validation,
            'bootstrap': self._bootstrap_validation,
            'monte_carlo': self._monte_carlo_validation,
            'bayesian': self._bayesian_validation,
            'adversarial': self._adversarial_validation,
            'drift_detection': self._drift_detection
        }
    
    def _setup_scorers(self) -> Dict[str, Any]:
        """Setup scoring metrics."""
        return {
            'accuracy': make_scorer(accuracy_score),
            'precision': make_scorer(precision_score, average='weighted'),
            'recall': make_scorer(recall_score, average='weighted'),
            'f1': make_scorer(f1_score, average='weighted'),
            'roc_auc': make_scorer(roc_auc_score, needs_proba=True)
        }
    
    async def validate(self, model: Any, data: Dict[str, Any], 
                      methods: List[str] = None) -> Dict[str, Any]:
        """Perform validation using specified methods."""
        try:
            methods = methods or list(self.validation_methods.keys())
            results = {}
            
            for method in methods:
                if method in self.validation_methods:
                    results[method] = await self.validation_methods[method](model, data)
            
            # Aggregate results
            aggregated = self._aggregate_validation_results(results)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(results)
            
            return {
                'detailed_results': results,
                'aggregated_results': aggregated,
                'confidence_intervals': confidence_intervals,
                'recommendations': self._generate_validation_recommendations(results)
            }
            
        except Exception as e:
            logger.error(f"Error in validation: {str(e)}")
            return self._generate_fallback_validation()
    
    async def _monte_carlo_validation(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Monte Carlo cross-validation."""
        try:
            n_iterations = 100
            results = []
            
            for _ in range(n_iterations):
                # Random split
                cv = ShuffleSplit(
                    n_splits=1,
                    test_size=self.config.test_size,
                    random_state=np.random.randint(0, 10000)
                )
                
                # Perform validation
                scores = cross_validate(
                    model,
                    data['X'],
                    data['y'],
                    cv=cv,
                    scoring=self.scorers
                )
                
                results.append(scores)
            
            # Aggregate results
            aggregated = self._aggregate_monte_carlo_results(results)
            
            return {
                'scores': aggregated,
                'n_iterations': n_iterations,
                'convergence_analysis': self._analyze_convergence(results)
            }
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo validation: {str(e)}")
            return {}
    
    def _calculate_confidence_intervals(self, results: Dict[str, Any], 
                                     confidence: float = 0.95) -> Dict[str, Any]:
        """Calculate confidence intervals for validation results."""
        intervals = {}
        
        for method, result in results.items():
            method_intervals = {}
            for metric, scores in result.get('scores', {}).items():
                if isinstance(scores, (list, np.ndarray)):
                    mean = np.mean(scores)
                    std = np.std(scores)
                    z_score = 1.96  # 95% confidence interval
                    
                    method_intervals[metric] = {
                        'mean': mean,
                        'lower': mean - (z_score * std),
                        'upper': mean + (z_score * std)
                    }
            
            intervals[method] = method_intervals
        
        return intervals 
    
    async def _bayesian_validation(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Bayesian validation."""
        try:
            import pymc3 as pm
            
            with pm.Model() as validation_model:
                # Define priors
                accuracy = pm.Beta('accuracy', alpha=2, beta=2)
                precision = pm.Beta('precision', alpha=2, beta=2)
                recall = pm.Beta('recall', alpha=2, beta=2)
                
                # Perform MCMC sampling
                trace = pm.sample(2000, tune=1000)
                
                # Calculate posterior statistics
                stats = pm.summary(trace)
                
                return {
                    'posterior_stats': stats.to_dict(),
                    'trace': trace,
                    'convergence_stats': pm.diagnostics.gelman_rubin(trace)
                }
                
        except Exception as e:
            logger.error(f"Error in Bayesian validation: {str(e)}")
            return {}
    
    async def _adversarial_validation(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform adversarial validation."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            # Create adversarial dataset
            X_train = data['X_train']
            X_test = data['X_test']
            
            # Label train as 0, test as 1
            y_adv = np.concatenate([np.zeros(len(X_train)), np.ones(len(X_test))])
            X_adv = np.vstack([X_train, X_test])
            
            # Train adversarial classifier
            adv_clf = RandomForestClassifier(n_estimators=100)
            adv_scores = cross_validate(adv_clf, X_adv, y_adv, cv=5)
            
            return {
                'adversarial_scores': adv_scores,
                'similarity_score': 1 - np.mean(adv_scores['test_score'])
            }
            
        except Exception as e:
            logger.error(f"Error in adversarial validation: {str(e)}")
            return {}
    
    async def _drift_detection(self, model: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect data drift between training and validation sets."""
        try:
            from scipy import stats
            
            drift_scores = {}
            for feature in data['feature_names']:
                # Perform Kolmogorov-Smirnov test
                ks_stat, p_value = stats.ks_2samp(
                    data['X_train'][feature],
                    data['X_test'][feature]
                )
                
                drift_scores[feature] = {
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'has_drift': p_value < 0.05
                }
            
            return {
                'drift_scores': drift_scores,
                'total_drift': sum(1 for score in drift_scores.values() if score['has_drift']),
                'drift_features': [f for f, score in drift_scores.items() if score['has_drift']]
            }
            
        except Exception as e:
            logger.error(f"Error in drift detection: {str(e)}")
            return {}