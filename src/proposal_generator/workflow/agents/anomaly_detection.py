from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection."""
    contamination: float = 0.1
    n_estimators: int = 100
    window_size: int = 20
    threshold: float = 3.0
    pca_components: int = 3

class AnomalyDetector:
    """Enhanced anomaly detection system."""
    
    def __init__(self, config: AnomalyConfig = None):
        self.config = config or AnomalyConfig()
        self.models = {
            'isolation_forest': IsolationForest(
                contamination=self.config.contamination,
                n_estimators=self.config.n_estimators
            ),
            'statistical': self._statistical_detector,
            'pca': self._pca_detector,
            'ensemble': self._ensemble_detector
        }
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=self.config.pca_components)
        self.anomaly_history = []
    
    async def detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using multiple methods."""
        try:
            # Prepare data
            processed_data = self._preprocess_data(data)
            
            # Run detection methods
            results = {}
            for method_name, detector in self.models.items():
                if callable(detector):
                    results[method_name] = await detector(processed_data)
                else:
                    results[method_name] = self._run_model(detector, processed_data)
            
            # Ensemble results
            ensemble_results = self._combine_detection_results(results)
            
            # Store results
            self._store_anomaly_results(ensemble_results)
            
            return {
                'detailed_results': results,
                'ensemble_results': ensemble_results,
                'anomaly_scores': self._calculate_anomaly_scores(results),
                'visualizations': self._create_anomaly_visualizations(results)
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return {}
    
    def _statistical_detector(self, data: np.ndarray) -> Dict[str, Any]:
        """Statistical anomaly detection using Z-score method."""
        try:
            z_scores = np.abs((data - np.mean(data, axis=0)) / np.std(data, axis=0))
            anomalies = z_scores > self.config.threshold
            
            return {
                'anomalies': anomalies,
                'scores': z_scores,
                'threshold': self.config.threshold
            }
        except Exception as e:
            logger.error(f"Error in statistical detection: {str(e)}")
            return {}
    
    def _pca_detector(self, data: np.ndarray) -> Dict[str, Any]:
        """PCA-based anomaly detection."""
        try:
            # Transform data
            transformed = self.pca.fit_transform(data)
            reconstructed = self.pca.inverse_transform(transformed)
            
            # Calculate reconstruction error
            reconstruction_error = np.square(data - reconstructed).sum(axis=1)
            threshold = np.mean(reconstruction_error) + self.config.threshold * np.std(reconstruction_error)
            anomalies = reconstruction_error > threshold
            
            return {
                'anomalies': anomalies,
                'scores': reconstruction_error,
                'threshold': threshold,
                'components': transformed
            }
        except Exception as e:
            logger.error(f"Error in PCA detection: {str(e)}")
            return {}
    
    def _ensemble_detector(self, data: np.ndarray) -> Dict[str, Any]:
        """Ensemble-based anomaly detection."""
        try:
            # Get results from all detectors
            results = []
            for detector in [self.models['isolation_forest'], 
                           self._statistical_detector,
                           self._pca_detector]:
                if callable(detector):
                    result = detector(data)
                else:
                    result = self._run_model(detector, data)
                results.append(result.get('anomalies', np.zeros(len(data), dtype=bool)))
            
            # Combine results using majority voting
            ensemble_anomalies = np.sum(results, axis=0) >= len(results) // 2
            
            return {
                'anomalies': ensemble_anomalies,
                'individual_results': results,
                'confidence': np.mean(results, axis=0)
            }
        except Exception as e:
            logger.error(f"Error in ensemble detection: {str(e)}")
            return {}
    
    def _create_anomaly_visualizations(self, results: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Create interactive visualizations of anomaly detection results."""
        try:
            return {
                'time_series': self._create_anomaly_timeseries(results),
                'scatter': self._create_anomaly_scatter(results),
                'distribution': self._create_anomaly_distribution(results),
                'correlation': self._create_anomaly_correlation(results)
            }
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            return {} 