from typing import Dict, Any, List, Optional
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class MonitoringMetrics:
    """Real-time monitoring metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time: float
    queue_size: int
    active_tasks: int
    error_rate: float
    throughput: float

class RealTimeMonitor:
    """Real-time monitoring and visualization system."""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_usage': 0.8,
            'memory_usage': 0.8,
            'response_time': 2.0,
            'error_rate': 0.05
        }
        self.visualization_buffer = pd.DataFrame()
        self.update_interval = 1.0  # seconds
    
    async def update_metrics(self, new_metrics: MonitoringMetrics) -> None:
        """Update monitoring metrics in real-time."""
        self.metrics_history.append(new_metrics)
        self._update_visualization_buffer(new_metrics)
        await self._check_alerts(new_metrics)
    
    def create_dashboard(self) -> Dict[str, go.Figure]:
        """Create comprehensive monitoring dashboard."""
        return {
            'system_metrics': self._create_system_metrics_plot(),
            'performance_metrics': self._create_performance_plot(),
            'error_analysis': self._create_error_analysis_plot(),
            'resource_usage': self._create_resource_usage_plot(),
            'task_distribution': self._create_task_distribution_plot(),
            'trend_analysis': self._create_trend_analysis_plot()
        }
    
    def _create_system_metrics_plot(self) -> go.Figure:
        """Create system metrics visualization."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'CPU Usage', 'Memory Usage',
                'Response Time', 'Error Rate'
            )
        )
        
        # CPU Usage gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=self.visualization_buffer['cpu_usage'].iloc[-1],
                domain={'row': 0, 'column': 0},
                title={'text': "CPU Usage"},
                gauge={'axis': {'range': [0, 1]}}
            ),
            row=1, col=1
        )
        
        # Memory Usage gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=self.visualization_buffer['memory_usage'].iloc[-1],
                domain={'row': 0, 'column': 1},
                title={'text': "Memory Usage"},
                gauge={'axis': {'range': [0, 1]}}
            ),
            row=1, col=2
        )
        
        # Response Time trend
        fig.add_trace(
            go.Scatter(
                x=self.visualization_buffer.index,
                y=self.visualization_buffer['response_time'],
                mode='lines',
                name='Response Time'
            ),
            row=2, col=1
        )
        
        # Error Rate trend
        fig.add_trace(
            go.Scatter(
                x=self.visualization_buffer.index,
                y=self.visualization_buffer['error_rate'],
                mode='lines',
                name='Error Rate'
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False)
        return fig
    
    def _create_task_distribution_plot(self) -> go.Figure:
        """Create task distribution visualization."""
        fig = go.Figure()
        
        # Task status distribution
        task_status = self.visualization_buffer['active_tasks'].value_counts()
        fig.add_trace(go.Pie(
            labels=task_status.index,
            values=task_status.values,
            hole=0.3
        ))
        
        fig.update_layout(
            title="Task Distribution",
            showlegend=True
        )
        
        return fig
    
    def _create_trend_analysis_plot(self) -> go.Figure:
        """Create trend analysis visualization."""
        fig = go.Figure()
        
        # Add performance trend
        fig.add_trace(go.Scatter(
            x=self.visualization_buffer.index,
            y=self._calculate_performance_trend(),
            mode='lines+markers',
            name='Performance Trend'
        ))
        
        # Add prediction interval
        upper, lower = self._calculate_prediction_intervals()
        fig.add_trace(go.Scatter(
            x=self.visualization_buffer.index,
            y=upper,
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Upper Bound'
        ))
        
        fig.add_trace(go.Scatter(
            x=self.visualization_buffer.index,
            y=lower,
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Lower Bound'
        ))
        
        fig.update_layout(
            title="Performance Trend Analysis",
            xaxis_title="Time",
            yaxis_title="Performance Score"
        )
        
        return fig
    
    async def _check_alerts(self, metrics: MonitoringMetrics) -> None:
        """Check for alert conditions."""
        alerts = []
        
        for metric, threshold in self.alert_thresholds.items():
            current_value = getattr(metrics, metric)
            if current_value > threshold:
                alerts.append({
                    'metric': metric,
                    'value': current_value,
                    'threshold': threshold,
                    'timestamp': metrics.timestamp
                })
        
        if alerts:
            await self._handle_alerts(alerts)
    
    def _calculate_performance_trend(self) -> np.ndarray:
        """Calculate performance trend using exponential smoothing."""
        performance_metrics = self.visualization_buffer['response_time'].values
        return pd.Series(performance_metrics).ewm(span=20).mean()
    
    def _calculate_prediction_intervals(self, confidence: float = 0.95) -> tuple:
        """Calculate prediction intervals for trend analysis."""
        trend = self._calculate_performance_trend()
        std = self.visualization_buffer['response_time'].rolling(window=20).std()
        z_score = 1.96  # 95% confidence interval
        
        upper = trend + (z_score * std)
        lower = trend - (z_score * std)
        
        return upper, lower 