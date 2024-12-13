from crewai.tools import BaseTool
from typing import Dict, Any, List
import logging
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet
import tensorflow as tf

logger = logging.getLogger(__name__)

class CompetitiveForecastingTool(BaseTool):
    """Tool for forecasting competitive landscape changes."""
    
    def __init__(self):
        super().__init__(
            name="Competitive Forecaster",
            description="Forecasts competitive landscape changes and market dynamics"
        )
        self.models = {
            'trend': Prophet(),
            'ml': RandomForestRegressor(),
            'deep': self._build_deep_learning_model()
        }
    
    async def run(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive forecasts."""
        try:
            historical_data = self._prepare_historical_data(competitor_data)
            market_indicators = self._analyze_market_indicators(competitor_data)
            
            forecasts = {
                'market_evolution': self._forecast_market_evolution(historical_data),
                'competitor_trajectories': self._forecast_competitor_trajectories(historical_data),
                'technology_trends': self._forecast_technology_trends(market_indicators),
                'market_share_predictions': self._forecast_market_share(historical_data),
                'disruption_risks': self._assess_disruption_risks(market_indicators)
            }
            
            return {
                'forecasts': forecasts,
                'confidence_intervals': self._calculate_confidence_intervals(forecasts),
                'risk_assessment': self._assess_forecast_risks(forecasts),
                'strategic_implications': self._analyze_strategic_implications(forecasts),
                'visualization': self._create_forecast_visualizations(forecasts)
            }
            
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            return {}
    
    def _forecast_market_evolution(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Forecast overall market evolution."""
        try:
            # Prepare market evolution data
            market_data = self._prepare_market_data(historical_data)
            
            # Generate forecasts using different models
            prophet_forecast = self._generate_prophet_forecast(market_data)
            ml_forecast = self._generate_ml_forecast(market_data)
            deep_forecast = self._generate_deep_forecast(market_data)
            
            # Ensemble the forecasts
            ensemble_forecast = self._ensemble_forecasts([
                prophet_forecast,
                ml_forecast,
                deep_forecast
            ])
            
            return {
                'market_size': ensemble_forecast['market_size'],
                'growth_rate': ensemble_forecast['growth_rate'],
                'segment_evolution': ensemble_forecast['segment_evolution'],
                'key_drivers': self._identify_growth_drivers(market_data)
            }
        except Exception as e:
            logger.error(f"Error forecasting market evolution: {str(e)}")
            return {}
    
    def _forecast_competitor_trajectories(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Forecast individual competitor trajectories."""
        try:
            competitor_forecasts = {}
            
            for competitor in historical_data['competitors'].unique():
                competitor_data = historical_data[
                    historical_data['competitors'] == competitor
                ]
                
                trajectory = {
                    'market_share': self._forecast_share_trajectory(competitor_data),
                    'growth_potential': self._forecast_growth_potential(competitor_data),
                    'innovation_trajectory': self._forecast_innovation_path(competitor_data),
                    'competitive_strength': self._forecast_competitive_strength(competitor_data)
                }
                
                competitor_forecasts[competitor] = trajectory
            
            return {
                'individual_trajectories': competitor_forecasts,
                'relative_positions': self._analyze_relative_positions(competitor_forecasts),
                'competitive_dynamics': self._analyze_competitive_dynamics(competitor_forecasts)
            }
        except Exception as e:
            logger.error(f"Error forecasting competitor trajectories: {str(e)}")
            return {}
    
    def _forecast_technology_trends(self, market_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast technology adoption and innovation trends."""
        try:
            return {
                'emerging_technologies': self._forecast_tech_emergence(market_indicators),
                'adoption_curves': self._forecast_tech_adoption(market_indicators),
                'innovation_cycles': self._forecast_innovation_cycles(market_indicators),
                'disruption_potential': self._assess_tech_disruption(market_indicators)
            }
        except Exception as e:
            logger.error(f"Error forecasting technology trends: {str(e)}")
            return {}
    
    def _assess_disruption_risks(self, market_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential market disruption risks."""
        try:
            return {
                'new_entrants': self._assess_new_entrant_risks(market_indicators),
                'technology_disruption': self._assess_tech_disruption_risks(market_indicators),
                'business_model_disruption': self._assess_model_disruption_risks(market_indicators),
                'regulatory_changes': self._assess_regulatory_risks(market_indicators),
                'market_shifts': self._assess_market_shift_risks(market_indicators)
            }
        except Exception as e:
            logger.error(f"Error assessing disruption risks: {str(e)}")
            return {}
    
    def _build_deep_learning_model(self) -> tf.keras.Model:
        """Build deep learning model for forecasting."""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def _create_forecast_visualizations(self, forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualizations of forecasts."""
        try:
            return {
                'market_evolution': self._create_evolution_chart(forecasts['market_evolution']),
                'competitor_trajectories': self._create_trajectory_chart(
                    forecasts['competitor_trajectories']
                ),
                'technology_trends': self._create_tech_trend_chart(
                    forecasts['technology_trends']
                ),
                'disruption_risks': self._create_risk_heatmap(forecasts['disruption_risks'])
            }
        except Exception as e:
            logger.error(f"Error creating forecast visualizations: {str(e)}")
            return {} 