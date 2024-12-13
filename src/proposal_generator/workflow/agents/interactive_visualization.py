from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class InteractiveConfig:
    """Configuration for interactive visualizations."""
    update_interval: float = 1.0
    max_points: int = 1000
    animation_duration: int = 500
    hover_data: List[str] = None

class InteractiveVisualizer:
    """Enhanced interactive visualization system."""
    
    def __init__(self, config: InteractiveConfig = None):
        self.config = config or InteractiveConfig()
        self.figures = {}
        self.callbacks = {}
    
    def create_interactive_dashboard(self, data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Create interactive dashboard with linked views."""
        try:
            return {
                'metrics': self._create_interactive_metrics(data),
                'timeline': self._create_interactive_timeline(data),
                'correlations': self._create_interactive_correlations(data),
                'distributions': self._create_interactive_distributions(data)
            }
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return {}
    
    def _create_interactive_metrics(self, data: Dict[str, Any]) -> go.Figure:
        """Create interactive metrics visualization."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(data.keys()),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                  [{'type': 'indicator'}, {'type': 'indicator'}]]
        )
        
        for i, (metric, values) in enumerate(data.items()):
            row = i // 2 + 1
            col = i % 2 + 1
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta+gauge",
                    value=values[-1],
                    delta={'reference': values[-2]},
                    gauge={
                        'axis': {'range': [0, max(values)]},
                        'steps': [
                            {'range': [0, max(values)*0.5], 'color': "lightgray"},
                            {'range': [max(values)*0.5, max(values)*0.8], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': max(values)*0.8
                        }
                    }
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Real-time Metrics Dashboard",
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': True}}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'type': 'buttons'
            }]
        )
        
        return fig 