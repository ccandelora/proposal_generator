"""Module for analyzing system performance."""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Union
import time
from datetime import datetime
from scipy import stats

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzer for system performance metrics."""

    def __init__(self):
        """Initialize the PerformanceAnalyzer."""
        self.logger = logging.getLogger(__name__)
        self.warning_thresholds = {
            "cpu": 80,
            "memory": 85,
            "disk": 90,
            "network": 75
        }
        self.critical_thresholds = {
            "cpu": 90,
            "memory": 95,
            "disk": 95,
            "network": 90
        }

    def _validate_metric_value(self, value: Any) -> float:
        """Validate and convert a metric value."""
        try:
            value = float(value)
            if value < 0:
                raise ValueError("Metric value cannot be negative")
            return value
        except (TypeError, ValueError):
            raise ValueError(f"Invalid metric value: {value}")

    def _validate_timestamp(self, timestamp: Any) -> float:
        """Validate and convert a timestamp value."""
        try:
            timestamp = float(timestamp)
            if timestamp < 0:
                raise ValueError("Timestamp cannot be negative")
            return timestamp
        except (TypeError, ValueError):
            raise ValueError(f"Invalid timestamp: {timestamp}")

    def _validate_percentage(self, value: Any) -> float:
        """Validate and convert a percentage value."""
        try:
            value = float(value)
            if value < 0 or value > 100:
                raise ValueError("Percentage must be between 0 and 100")
            return value
        except (TypeError, ValueError):
            raise ValueError(f"Invalid percentage value: {value}")

    def _validate_metrics_data(self, metrics: Dict[str, Any]) -> None:
        """Validate metrics data structure."""
        if not metrics or not isinstance(metrics, dict):
            raise ValueError("Invalid metrics data: empty or not a dictionary")
            
        # Make timestamp optional
        if "timestamp" in metrics and not isinstance(metrics["timestamp"], (int, float)):
            raise ValueError("Invalid metrics data: timestamp must be numeric")
            
        required_components = ["cpu", "memory", "disk", "network"]
        if not all(component in metrics for component in required_components):
            raise ValueError("Invalid metrics data: missing required components")
            
        for component in required_components:
            if not isinstance(metrics[component], dict):
                raise ValueError(f"Invalid metrics data: {component} must be a dictionary")

    def _validate_memory_metrics(self, metrics: Dict[str, Any]) -> None:
        """Validate memory metrics."""
        required_fields = ['total', 'used', 'free', 'usage']
        if not all(field in metrics for field in required_fields):
            raise ValueError("Invalid memory metrics: missing required fields")
            
        # Validate numeric values
        for field in ['total', 'used', 'free']:
            if not isinstance(metrics[field], (int, float)):
                raise ValueError(f"Invalid memory metrics: {field} must be numeric")
            if metrics[field] < 0:
                raise ValueError(f"Invalid memory metrics: {field} cannot be negative")
                
        # Validate usage percentage
        if not isinstance(metrics['usage'], (int, float)):
            raise ValueError("Invalid memory metrics: usage must be numeric")
        if not 0 <= metrics['usage'] <= 100:
            raise ValueError("Invalid memory metrics: usage must be between 0 and 100")

    def _validate_disk_metrics(self, metrics: Dict[str, Any]) -> None:
        """Validate disk metrics."""
        required_fields = ['total', 'used', 'free', 'usage']
        if not all(field in metrics for field in required_fields):
            raise ValueError("Invalid disk metrics: missing required fields")
            
        # Validate numeric values
        for field in ['total', 'used', 'free']:
            if not isinstance(metrics[field], (int, float)):
                raise ValueError(f"Invalid disk metrics: {field} must be numeric")
            if metrics[field] < 0:
                raise ValueError(f"Invalid disk metrics: {field} cannot be negative")
                
        # Validate usage percentage
        if not isinstance(metrics['usage'], (int, float)):
            raise ValueError("Invalid disk metrics: usage must be numeric")
        if not 0 <= metrics['usage'] <= 100:
            raise ValueError("Invalid disk metrics: usage must be between 0 and 100")

    def analyze_cpu_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CPU performance metrics."""
        try:
            if not metrics:
                raise ValueError("Invalid metrics data")
            if 'usage' not in metrics:
                raise ValueError("Invalid CPU metrics")

            try:
                usage = float(metrics['usage'])
            except (ValueError, TypeError):
                raise ValueError("Invalid CPU metrics")

            return {
                'utilization': usage,
                'bottlenecks': self._identify_cpu_bottlenecks(usage),
                'recommendations': self._generate_cpu_recommendations(usage)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing CPU performance: {str(e)}")
            raise

    def analyze_memory_usage(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory usage metrics."""
        try:
            self._validate_memory_metrics(metrics)
            
            # Calculate memory usage pattern
            pattern = self._analyze_memory_pattern(metrics)
            health = self._analyze_memory_health(metrics)
            
            return {
                'usage_percent': metrics['usage'],
                'total_memory': metrics['total'],
                'used_memory': metrics['used'],
                'available_memory': metrics['free'],
                'usage_pattern': pattern,
                'health_status': health,
                'recommendations': self._generate_memory_recommendations(metrics)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing memory usage: {str(e)}")
            raise ValueError("Invalid memory metrics") from e

    def analyze_disk_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze disk performance metrics."""
        try:
            self._validate_disk_metrics(metrics)
            
            # Calculate disk performance metrics
            io_stats = self._analyze_disk_io(metrics)
            health = self._analyze_disk_health(metrics)
            
            return {
                'usage_percent': metrics['usage'],
                'total_space': metrics['total'],
                'used_space': metrics['used'],
                'free_space': metrics['free'],
                'io_stats': io_stats,
                'health_status': health,
                'recommendations': self._generate_disk_recommendations(metrics)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing disk performance: {str(e)}")
            raise ValueError("Invalid disk metrics") from e

    def analyze_network_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network performance patterns."""
        if not metrics:
            raise ValueError("Invalid network metrics: empty metrics")
            
        try:
            self._validate_network_metrics(metrics)
            
            # Handle both nested and direct network metrics
            network_metrics = metrics.get("network", metrics)
            
            # Calculate throughput
            throughput = {
                "bytes_per_sec": 0,
                "packets_per_sec": 0,
                "send_rate": 0,
                "receive_rate": 0,
                "total_throughput": 0
            }
            
            if "bytes_sent" in network_metrics and "bytes_recv" in network_metrics:
                throughput["bytes_per_sec"] = (
                    network_metrics["bytes_sent"] + network_metrics["bytes_recv"]
                ) / 2
                throughput["send_rate"] = network_metrics["bytes_sent"]
                throughput["receive_rate"] = network_metrics["bytes_recv"]
                throughput["total_throughput"] = (
                    network_metrics["bytes_sent"] + network_metrics["bytes_recv"]
                )
                
            if "packets_sent" in network_metrics and "packets_recv" in network_metrics:
                throughput["packets_per_sec"] = (
                    network_metrics["packets_sent"] + network_metrics["packets_recv"]
                ) / 2
            
            result = {
                "status": "success",
                "throughput": throughput,
                "current_usage": network_metrics.get("usage", 0)
            }
            
            # Add packet analysis if we have packet data
            if all(k in network_metrics for k in ["packets_sent", "packets_recv"]):
                # Calculate average packet sizes
                avg_packet_size_sent = (
                    network_metrics["bytes_sent"] / network_metrics["packets_sent"]
                    if network_metrics["packets_sent"] > 0 else 0
                )
                avg_packet_size_recv = (
                    network_metrics["bytes_recv"] / network_metrics["packets_recv"]
                    if network_metrics["packets_recv"] > 0 else 0
                )
                
                # Calculate efficiency metrics
                total_bytes = network_metrics["bytes_sent"] + network_metrics["bytes_recv"]
                total_packets = network_metrics["packets_sent"] + network_metrics["packets_recv"]
                avg_packet_size = (avg_packet_size_sent + avg_packet_size_recv) / 2
                
                # Calculate efficiency score (0-100)
                # Factors considered:
                # 1. Average packet size (optimal around 1000-1500 bytes)
                # 2. Send/receive ratio (optimal around 1.0)
                # 3. Error rate
                packet_size_score = min(100, (avg_packet_size / 1000) * 100)
                if avg_packet_size > 1500:
                    packet_size_score = max(0, 200 - (avg_packet_size / 1500) * 100)
                
                ratio = (network_metrics["packets_sent"] / 
                        network_metrics["packets_recv"]
                        if network_metrics["packets_recv"] > 0 else 0)
                ratio_score = 100 - min(100, abs(1 - ratio) * 100)
                
                error_score = 100
                if "errors_in" in network_metrics or "errors_out" in network_metrics:
                    total_errors = (
                        network_metrics.get("errors_in", 0) + 
                        network_metrics.get("errors_out", 0)
                    )
                    if total_packets > 0:
                        error_rate = total_errors / total_packets
                        error_score = max(0, 100 - error_rate * 1000)
                
                efficiency_score = (
                    packet_size_score * 0.4 +
                    ratio_score * 0.4 +
                    error_score * 0.2
                )
                
                result["packet_analysis"] = {
                    "total_packets": total_packets,
                    "send_receive_ratio": ratio,
                    "packets_sent": network_metrics["packets_sent"],
                    "packets_recv": network_metrics["packets_recv"],
                    "avg_packet_size_sent": avg_packet_size_sent,
                    "avg_packet_size_recv": avg_packet_size_recv,
                    "avg_packet_size": avg_packet_size,
                    "efficiency": {
                        "score": efficiency_score,
                        "packet_size_score": packet_size_score,
                        "ratio_score": ratio_score,
                        "error_score": error_score,
                        "details": {
                            "optimal_packet_size": 1000,
                            "optimal_ratio": 1.0,
                            "current_packet_size": avg_packet_size,
                            "current_ratio": ratio
                        }
                    }
                }
            
            # Add error rates if available
            if "errors_in" in network_metrics or "errors_out" in network_metrics:
                result["error_rate"] = {
                    "incoming": network_metrics.get("errors_in", 0),
                    "outgoing": network_metrics.get("errors_out", 0)
                }
            
            # Generate recommendations based on metrics
            recommendations = []
            
            # Check throughput recommendations
            if throughput["bytes_per_sec"] > 100 * 1024 * 1024:  # Over 100MB/s
                recommendations.append({
                    "type": "throughput",
                    "message": "Consider network bandwidth optimization",
                    "priority": "medium"
                })
            
            # Check packet ratio recommendations
            if "packet_analysis" in result:
                ratio = result["packet_analysis"]["send_receive_ratio"]
                if ratio > 2 or ratio < 0.5:
                    recommendations.append({
                        "type": "packet_ratio",
                        "message": "Investigate unbalanced send/receive ratio",
                        "priority": "low"
                    })
                
                # Check packet size recommendations
                avg_size = result["packet_analysis"]["avg_packet_size"]
                if avg_size < 64:  # Too small packets
                    recommendations.append({
                        "type": "packet_size",
                        "message": "Consider packet coalescing - packets are too small",
                        "priority": "medium"
                    })
                elif avg_size > 1500:  # Approaching MTU
                    recommendations.append({
                        "type": "packet_size",
                        "message": "Consider packet fragmentation - packets are too large",
                        "priority": "medium"
                    })
                
                # Check efficiency recommendations
                efficiency = result["packet_analysis"]["efficiency"]
                if efficiency["score"] < 60:
                    recommendations.append({
                        "type": "efficiency",
                        "message": "Network efficiency is low - review packet size and ratio",
                        "priority": "high"
                    })
            
            # Check error rate recommendations
            if "error_rate" in result:
                total_errors = (
                    result["error_rate"]["incoming"] + 
                    result["error_rate"]["outgoing"]
                )
                if total_errors > 0:
                    recommendations.append({
                        "type": "errors",
                        "message": "Network errors detected - check connectivity",
                        "priority": "high"
                    })
            
            result["recommendations"] = recommendations
            return result

        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing network performance: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_performance_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        try:
            if not metrics or not isinstance(metrics, dict):
                raise ValueError("Invalid metrics data")
            
            required_components = ['cpu', 'memory', 'disk', 'network']
            if not all(component in metrics for component in required_components):
                raise ValueError("Missing required components in metrics")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'summary': self._generate_summary(metrics),
                'component_analysis': {
                    'cpu': self.analyze_cpu_performance(metrics['cpu']),
                    'memory': self.analyze_memory_usage(metrics['memory']),
                    'disk': self.analyze_disk_performance(metrics['disk']),
                    'network': self.analyze_network_performance(metrics['network'])
                },
                'correlations': self.analyze_resource_correlations(metrics),
                'recommendations': self._generate_overall_recommendations(metrics)
            }
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            raise ValueError("Invalid metrics data") from e

    def analyze_resource_utilization(self, metrics: Dict[str, Any], historical_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze resource utilization patterns.
        
        Args:
            metrics: Current metrics data point
            historical_data: Optional list of historical metrics for pattern analysis
            
        Returns:
            Dictionary containing utilization analysis results
            
        Raises:
            ValueError: If metrics data is invalid
        """
        if not metrics or not isinstance(metrics, dict):
            raise ValueError("Invalid metrics data: empty or not a dictionary")
            
        try:
            # Check for required components
            required_components = ["cpu", "memory", "disk", "network"]
            missing_components = [c for c in required_components if c not in metrics]
            if missing_components:
                raise ValueError(f"Invalid metrics data: missing components {missing_components}")
            
            current_usage = {}
            for resource in required_components:
                if resource not in metrics:
                    raise ValueError(f"Invalid metrics data: missing {resource} component")
                    
                if not isinstance(metrics[resource], dict):
                    raise ValueError(f"Invalid {resource} metrics: must be a dictionary")
                    
                if "usage" not in metrics[resource]:
                    raise ValueError(f"Invalid {resource} metrics: missing usage field")
                    
                try:
                    usage = self._validate_percentage(metrics[resource]["usage"])
                    current_usage[resource] = usage
                except ValueError as e:
                    raise ValueError(f"Invalid {resource} metrics: {str(e)}")

            # Calculate utilization score (weighted average)
            weights = {
                "cpu": 0.4,
                "memory": 0.3,
                "disk": 0.2,
                "network": 0.1
            }
            
            total_score = 0
            total_weight = 0
            
            for resource, usage in current_usage.items():
                if resource in weights:
                    total_score += usage * weights[resource]
                    total_weight += weights[resource]
            
            utilization_score = total_score / total_weight if total_weight > 0 else 0

            # Identify optimization targets
            optimization_targets = []
            
            # Check for underutilized resources
            for resource, usage in current_usage.items():
                if usage < 20:  # Less than 20% utilization
                    optimization_targets.append({
                        "resource": resource,
                        "current_usage": usage,
                        "recommendation": "Consider resource reallocation",
                        "potential_savings": "high"
                    })
                elif usage > 80:  # Over 80% utilization
                    optimization_targets.append({
                        "resource": resource,
                        "current_usage": usage,
                        "recommendation": "Consider capacity increase",
                        "priority": "high"
                    })

            result = {
                "status": "success",
                "utilization_score": utilization_score,
                "current_usage": current_usage,
                "bottlenecks": [],
                "optimization_targets": optimization_targets
            }

            # Analyze historical patterns if data is available
            if historical_data:
                patterns = {
                    "increasing_resources": [],
                    "decreasing_resources": [],
                    "stable_resources": []
                }
                
                for resource in current_usage.keys():
                    values = []
                    for hist_metrics in historical_data[-3:]:  # Look at last 3 data points
                        if (resource in hist_metrics and 
                            "usage" in hist_metrics[resource]):
                            try:
                                value = self._validate_percentage(
                                    hist_metrics[resource]["usage"]
                                )
                                values.append(value)
                            except ValueError:
                                continue
                    
                    if len(values) >= 2:
                        slope = (values[-1] - values[0]) / (len(values) - 1)
                        if abs(slope) < 1:  # Less than 1% change per interval
                            patterns["stable_resources"].append(resource)
                        elif slope > 0:
                            patterns["increasing_resources"].append(resource)
                        else:
                            patterns["decreasing_resources"].append(resource)
                
                result["historical_patterns"] = patterns

            # Identify potential bottlenecks
            for resource, usage in current_usage.items():
                if usage >= self.warning_thresholds[resource]:
                    result["bottlenecks"].append({
                        "resource": resource,
                        "usage": usage,
                        "threshold": self.warning_thresholds[resource]
                    })

            return result

        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing resource utilization: {str(e)}")
            raise ValueError(f"Error analyzing resource utilization: {str(e)}")

    def analyze_performance_trends(self, metrics_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        try:
            if not metrics_series:
                return {
                    "status": "insufficient_data",
                    "trends": {},
                    "time_range": 0,
                    "data_points": 0
                }
                
            if not isinstance(metrics_series, list):
                return {
                    "status": "error",
                    "error": "Invalid metrics series: must be a list",
                    "trends": {},
                    "time_range": 0,
                    "data_points": 0
                }
                
            if len(metrics_series) < 2:
                return {
                    "status": "insufficient_data",
                    "trends": {},
                    "time_range": 0,
                    "data_points": len(metrics_series)
                }

            # Extract timestamps and validate
            timestamps = []
            for metrics in metrics_series:
                if not isinstance(metrics, dict):
                    return {
                        "status": "error",
                        "error": "Invalid metrics data: must be a dictionary",
                        "trends": {},
                        "time_range": 0,
                        "data_points": len(metrics_series)
                    }
                    
                if "timestamp" not in metrics:
                    return {
                        "status": "error",
                        "error": "Missing timestamp in metrics data",
                        "trends": {},
                        "time_range": 0,
                        "data_points": len(metrics_series)
                    }
                    
                try:
                    timestamps.append(self._validate_timestamp(metrics["timestamp"]))
                except ValueError as e:
                    return {
                        "status": "error",
                        "error": f"Invalid timestamp: {str(e)}",
                        "trends": {},
                        "time_range": 0,
                        "data_points": len(metrics_series)
                    }

            # Calculate time range
            time_range = max(timestamps) - min(timestamps)
            
            # Analyze trends for each resource
            trends = {}
            resources = ["cpu", "memory", "disk", "network"]
            
            for resource in resources:
                values = []
                for metrics in metrics_series:
                    if (resource in metrics and 
                        isinstance(metrics[resource], dict) and
                        "usage" in metrics[resource]):
                        try:
                            usage = self._validate_percentage(
                                metrics[resource]["usage"]
                            )
                            values.append(usage)
                        except ValueError:
                            continue
                
                if len(values) >= 2:
                    # Calculate trend metrics
                    slope = (values[-1] - values[0]) / time_range
                    avg = sum(values) / len(values)
                    variance = sum((x - avg) ** 2 for x in values) / len(values)
                    
                    trends[resource] = {
                        "slope": slope,  # Change per second
                        "rate_per_hour": slope * 3600,  # Change per hour
                        "average": avg,
                        "variance": variance,
                        "r_squared": self._calculate_r_squared(values)
                    }
            
            return {
                "status": "success",
                "trends": trends,
                "time_range": time_range,
                "data_points": len(metrics_series)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "trends": {},
                "time_range": 0,
                "data_points": len(metrics_series) if metrics_series else 0
            }

    def detect_performance_thresholds(self, metrics: Dict[str, Any], historical_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Detect performance threshold violations."""
        try:
            if not metrics or not isinstance(metrics, dict):
                raise ValueError("Invalid metrics data: empty or not a dictionary")
                
            required_components = ["cpu", "memory", "disk", "network"]
            if not all(component in metrics for component in required_components):
                raise ValueError("Invalid metrics data: missing required components")
            
            warnings = []
            critical = []
            oscillating_metrics = []
            
            # Check current thresholds
            for resource in required_components:
                if resource in metrics and "usage" in metrics[resource]:
                    try:
                        usage = self._validate_percentage(metrics[resource]["usage"])
                        
                        # Check warning threshold
                        if usage >= self.warning_thresholds[resource]:
                            warnings.append({
                                "resource": resource,
                                "usage": usage,
                                "threshold": self.warning_thresholds[resource]
                            })
                            
                        # Check critical threshold
                        if usage >= self.critical_thresholds[resource]:
                            critical.append({
                                "resource": resource,
                                "usage": usage,
                                "threshold": self.critical_thresholds[resource]
                            })
                            
                        # Check for oscillation if historical data is available
                        if historical_data and len(historical_data) >= 3:
                            values = []
                            for hist_metrics in historical_data[-3:]:
                                if (resource in hist_metrics and 
                                    "usage" in hist_metrics[resource]):
                                    try:
                                        value = self._validate_percentage(
                                            hist_metrics[resource]["usage"]
                                        )
                                        values.append(value)
                                    except ValueError:
                                        continue
                            
                            if len(values) >= 3:
                                # Check for oscillation pattern
                                # (alternating increases and decreases)
                                diffs = [b - a for a, b in zip(values[:-1], values[1:])]
                                if len(diffs) >= 2:
                                    if (diffs[0] * diffs[1] < 0 and  # Sign changes
                                        abs(diffs[0]) > 5 and  # Significant changes
                                        abs(diffs[1]) > 5):
                                        oscillating_metrics.append({
                                            "resource": resource,
                                            "recent_values": values,
                                            "threshold": self.warning_thresholds[resource]
                                        })
                            
                    except ValueError as e:
                        self.logger.warning(
                            f"Invalid {resource} metrics in threshold detection: {str(e)}"
                        )
            
            return {
                "status": "success",
                "warnings": warnings,
                "critical": critical,
                "oscillating_metrics": oscillating_metrics
            }

        except Exception as e:
            self.logger.error(f"Error detecting performance thresholds: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "warnings": [],
                "critical": [],
                "oscillating_metrics": []
            }

    def analyze_resource_correlations(self, metrics: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze correlations between different system resources."""
        try:
            # Handle time series data
            if isinstance(metrics, list):
                if not metrics or len(metrics) < 2:
                    return {
                        'status': 'insufficient_data',
                        'correlations': {},
                        'strong_correlations': [],
                        'insights': [],
                        'bottlenecks': [],
                        'resource_pressure': 0,
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                # Extract time series for each component
                components = {}
                for component in ['cpu', 'memory', 'disk', 'network']:
                    values = []
                    for m in metrics:
                        if component in m and isinstance(m[component], dict) and 'usage' in m[component]:
                            values.append(m[component]['usage'])
                    if values:
                        components[component] = values
                
                # Need at least two components to calculate correlations
                if len(components) < 2:
                    return {
                        'status': 'insufficient_data',
                        'correlations': {},
                        'strong_correlations': [],
                        'insights': [],
                        'bottlenecks': [],
                        'resource_pressure': 0,
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                
                # Calculate correlations between available components
                correlations = {}
                component_names = list(components.keys())
                for i in range(len(component_names)):
                    for j in range(i + 1, len(component_names)):
                        comp1, comp2 = component_names[i], component_names[j]
                        correlations[f'{comp1}_{comp2}'] = self._calculate_correlation(
                            components[comp1],
                            components[comp2]
                        )
                
            # Handle single point data
            else:
                cpu_usage = metrics['cpu']['usage']
                memory_usage = metrics['memory']['usage']
                disk_usage = metrics['disk']['usage']
                network_usage = metrics['network'].get('usage', 0)
                
                # Create correlation matrix
                correlations = {
                    'cpu_memory': self._calculate_correlation(cpu_usage, memory_usage),
                    'cpu_disk': self._calculate_correlation(cpu_usage, disk_usage),
                    'cpu_network': self._calculate_correlation(cpu_usage, network_usage),
                    'memory_disk': self._calculate_correlation(memory_usage, disk_usage),
                    'memory_network': self._calculate_correlation(memory_usage, network_usage),
                    'disk_network': self._calculate_correlation(disk_usage, network_usage)
                }
            
            # Identify strong correlations (positive or negative)
            strong_correlations = []
            for pair, correlation in correlations.items():
                if abs(correlation) >= 0.7:  # Strong correlation threshold
                    components = pair.split('_')
                    strong_correlations.append({
                        'components': components,
                        'correlation': correlation,
                        'strength': 'strong',
                        'type': 'positive' if correlation > 0 else 'negative'
                    })
                elif abs(correlation) >= 0.4:  # Moderate correlation threshold
                    components = pair.split('_')
                    strong_correlations.append({
                        'components': components,
                        'correlation': correlation,
                        'strength': 'moderate',
                        'type': 'positive' if correlation > 0 else 'negative'
                    })
            
            # Generate insights based on correlations
            insights = []
            for corr in strong_correlations:
                comp1, comp2 = corr['components']
                if corr['correlation'] > 0:
                    insights.append(
                        f"Strong positive correlation between {comp1} and {comp2} "
                        f"usage (correlation: {corr['correlation']:.2f})"
                    )
                else:
                    insights.append(
                        f"Strong negative correlation between {comp1} and {comp2} "
                        f"usage (correlation: {corr['correlation']:.2f})"
                    )
            
            # Identify potential resource bottlenecks
            bottlenecks = []
            if any(corr['correlation'] > 0.8 for corr in strong_correlations):
                bottlenecks.append("High resource coupling detected")
            
            # Calculate overall resource pressure
            if isinstance(metrics, list):
                # Use the latest values for resource pressure
                latest = metrics[-1]
                components_pressure = []
                if 'cpu' in latest and 'usage' in latest['cpu']:
                    components_pressure.append(latest['cpu']['usage'])
                if 'memory' in latest and 'usage' in latest['memory']:
                    components_pressure.append(latest['memory']['usage'])
                if 'disk' in latest and 'usage' in latest['disk']:
                    components_pressure.append(latest['disk']['usage'])
                if 'network' in latest and 'usage' in latest['network']:
                    components_pressure.append(latest['network']['usage'])
                
                resource_pressure = (
                    sum(components_pressure) / len(components_pressure)
                    if components_pressure else 0
                )
            else:
                resource_pressure = (
                    metrics['cpu']['usage'] +
                    metrics['memory']['usage'] +
                    metrics['disk']['usage'] +
                    metrics['network'].get('usage', 0)
                ) / 4
            
            return {
                'status': 'success',
                'correlations': correlations,
                'strong_correlations': strong_correlations,
                'insights': insights,
                'bottlenecks': bottlenecks,
                'resource_pressure': resource_pressure,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing resource correlations: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'correlations': {},
                'strong_correlations': [],
                'insights': [],
                'bottlenecks': [],
                'resource_pressure': 0,
                'analysis_timestamp': datetime.now().isoformat()
            }

    def _calculate_correlation(self, x: Union[float, int, List, np.ndarray], y: Union[float, int, List, np.ndarray]) -> float:
        """Calculate correlation between two metrics."""
        try:
            # For single values, use a simple ratio comparison
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                # Normalize values to 0-1 range
                x_norm = float(x) / 100 if x > 1 else float(x)
                y_norm = float(y) / 100 if y > 1 else float(y)
                
                # Calculate simple correlation
                if x_norm == y_norm:
                    return 1.0
                elif x_norm == 0 or y_norm == 0:
                    return 0.0
                else:
                    # Return a value between -1 and 1 based on the ratio
                    ratio = x_norm / y_norm if y_norm != 0 else 0
                    return max(min(2 * ratio - 1, 1), -1)
                    
            # For time series data, use numpy's corrcoef
            elif isinstance(x, (list, np.ndarray)) and isinstance(y, (list, np.ndarray)):
                if len(x) != len(y):
                    raise ValueError("Time series must have same length")
                    
                x_array = np.array(x)
                y_array = np.array(y)
                
                if len(x_array) < 2:
                    return 0.0
                    
                # Check if all values are identical
                if len(set(x_array)) == 1 and len(set(y_array)) == 1:
                    # If both series are constant, they are perfectly correlated
                    return 1.0
                elif len(set(x_array)) == 1 or len(set(y_array)) == 1:
                    # If only one series is constant, correlation is undefined
                    # We'll return 0 as there's no meaningful correlation
                    return 0.0
                    
                correlation_matrix = np.corrcoef(x_array, y_array)
                correlation = float(correlation_matrix[0, 1])
                
                # Handle NaN (can occur with constant series)
                if np.isnan(correlation):
                    return 1.0 if np.array_equal(x_array, y_array) else 0.0
                    
                return correlation
                
            else:
                raise ValueError("Invalid data types for correlation calculation")
                
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {str(e)}")
            return 0.0

    def _identify_cpu_bottlenecks(self, usage: float) -> List[str]:
        """Identify CPU bottlenecks."""
        bottlenecks = []
        if usage > 80:
            bottlenecks.append("High CPU utilization")
        if usage > 90:
            bottlenecks.append("Critical CPU saturation")
        return bottlenecks

    def _generate_cpu_recommendations(self, usage: float) -> List[str]:
        """Generate CPU optimization recommendations."""
        recommendations = []
        if usage > 80:
            recommendations.append("Consider scaling CPU resources")
        if usage > 90:
            recommendations.append("Urgent: CPU upgrade needed")
        return recommendations

    def _analyze_memory_pattern(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        used_percent = metrics['usage']
        total = metrics['total']
        used = metrics['used']
        free = metrics['free']
        
        # Calculate memory pressure
        pressure = 'low'
        if used_percent >= 90:
            pressure = 'critical'
        elif used_percent >= 75:
            pressure = 'high'
        elif used_percent >= 50:
            pressure = 'moderate'
            
        # Calculate usage level
        usage_level = 'normal'
        if used_percent >= 90:
            usage_level = 'critical'
        elif used_percent >= 75:
            usage_level = 'high'
        elif used_percent >= 50:
            usage_level = 'moderate'
        elif used_percent < 20:
            usage_level = 'low'
            
        # Calculate available ratio
        available_ratio = (free / total) if total > 0 else 0
            
        # Calculate fragmentation estimate
        # (simplified - actual fragmentation would need more detailed metrics)
        fragmentation = 'low'
        if total > 0:
            free_chunks = free / (1024 * 1024)  # Convert to MB
            if free_chunks < 100:  # Less than 100MB free chunks
                fragmentation = 'high'
            elif free_chunks < 500:  # Less than 500MB free chunks
                fragmentation = 'moderate'
        
        return {
            'trend': 'increasing' if used_percent > 75 else 'stable',
            'usage_level': usage_level,
            'pressure': pressure,
            'fragmentation': fragmentation,
            'available_ratio': available_ratio
        }

    def _analyze_memory_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory health status."""
        used_percent = metrics['usage']
        
        status = 'healthy'
        risk_level = 'low'
        warnings = []
        recommendations = []
        
        if used_percent >= 90:
            status = 'critical'
            risk_level = 'critical'
            warnings.append('Memory usage critically high')
            recommendations.append('Immediate memory upgrade required')
            recommendations.append('Consider terminating non-essential processes')
        elif used_percent >= 75:
            status = 'warning'
            risk_level = 'high'
            warnings.append('Memory usage high')
            recommendations.append('Plan for memory upgrade')
            recommendations.append('Monitor memory-intensive processes')
        elif used_percent >= 60:
            status = 'warning'
            risk_level = 'medium'
            warnings.append('Memory usage elevated')
            recommendations.append('Review memory usage patterns')
            
        if metrics['free'] < 1024 * 1024 * 100:  # Less than 100MB free
            status = 'critical'
            risk_level = 'critical'
            warnings.append('Very low free memory')
            recommendations.append('Free up memory immediately')
            recommendations.append('Check for memory leaks')
        elif metrics['free'] < 1024 * 1024 * 500:  # Less than 500MB free
            status = 'warning'
            risk_level = 'high'
            warnings.append('Low free memory')
            recommendations.append('Free up memory soon')
            
        return {
            'status': status,
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendations': recommendations
        }

    def _analyze_disk_io(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze disk I/O patterns."""
        return {
            'usage_percent': metrics['usage'],
            'free_space': int(metrics['total']) - int(metrics['used']) if metrics['total'] > 0 else 0,
            'io_health': 'healthy' if metrics['usage'] < 80 else 'degraded'
        }

    def _analyze_disk_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze disk health status."""
        used_percent = metrics['usage']
        
        status = 'healthy'
        risk_level = 'low'
        warnings = []
        recommendations = []
        
        if used_percent >= 90:
            status = 'critical'
            risk_level = 'critical'
            warnings.append('Disk usage critically high')
            recommendations.append('Immediate disk cleanup required')
            recommendations.append('Consider disk expansion')
        elif used_percent >= 75:
            status = 'warning'
            risk_level = 'high'
            warnings.append('Disk usage high')
            recommendations.append('Plan for disk cleanup')
            recommendations.append('Monitor disk usage trends')
        elif used_percent >= 60:
            status = 'warning'
            risk_level = 'medium'
            warnings.append('Disk usage elevated')
            recommendations.append('Review disk usage patterns')
            
        if metrics['free'] < 1024 * 1024 * 1024:  # Less than 1GB free
            status = 'critical'
            risk_level = 'critical'
            warnings.append('Very low free space')
            recommendations.append('Free up disk space immediately')
            recommendations.append('Archive old files')
        elif metrics['free'] < 1024 * 1024 * 1024 * 5:  # Less than 5GB free
            status = 'warning'
            risk_level = 'high'
            warnings.append('Low free space')
            recommendations.append('Free up disk space soon')
            
        return {
            'status': status,
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendations': recommendations
        }

    def _calculate_r_squared(self, values: List[float]) -> float:
        """Calculate R-squared value for a series of measurements."""
        if len(values) < 2:
            return 0.0
            
        # Calculate mean of y values
        y_mean = sum(values) / len(values)
        
        # Generate x values (time points)
        x_values = list(range(len(values)))
        x_mean = sum(x_values) / len(x_values)
        
        # Calculate slope and intercept
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
            
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        y_pred = [slope * x + intercept for x in x_values]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(values, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        
        if ss_tot == 0:
            return 0.0
            
        return 1 - (ss_res / ss_tot)

    def _generate_memory_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate memory optimization recommendations."""
        recommendations = []
        usage = metrics['usage']
        
        if usage > 90:
            recommendations.append("Critical: Memory upgrade needed")
        elif usage > 80:
            recommendations.append("Consider increasing memory capacity")
        elif usage > 70:
            recommendations.append("Monitor memory usage trends")
            
        free_mb = metrics['free'] / (1024 * 1024)
        if free_mb < 100:
            recommendations.append("Critical: Very low free memory")
        elif free_mb < 500:
            recommendations.append("Low free memory available")
            
        return recommendations

    def _generate_disk_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate disk optimization recommendations."""
        recommendations = []
        usage = metrics['usage']
        
        if usage > 90:
            recommendations.append("Critical: Disk space nearly full")
        elif usage > 80:
            recommendations.append("Consider increasing disk capacity")
        elif usage > 70:
            recommendations.append("Monitor disk usage trends")
            
        free_gb = metrics['free'] / (1024 * 1024 * 1024)
        if free_gb < 1:
            recommendations.append("Critical: Very low free disk space")
        elif free_gb < 5:
            recommendations.append("Low free disk space available")
            
        return recommendations

    def _validate_network_metrics(self, metrics: Dict[str, Any]) -> None:
        """Validate network metrics."""
        # Handle nested network metrics
        if 'network' in metrics:
            network_metrics = metrics['network']
        else:
            network_metrics = metrics
            
        required_fields = ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv']
        if not all(field in network_metrics for field in required_fields):
            raise ValueError("Invalid network metrics: missing required fields")
            
        # Validate numeric values
        for field in required_fields:
            if not isinstance(network_metrics[field], (int, float)):
                raise ValueError(f"Invalid network metrics: {field} must be numeric")
            if network_metrics[field] < 0:
                raise ValueError(f"Invalid network metrics: {field} cannot be negative")
                
        # Validate usage if present
        if 'usage' in network_metrics:
            if not isinstance(network_metrics['usage'], (int, float)):
                raise ValueError("Invalid network metrics: usage must be numeric")
            if not 0 <= network_metrics['usage'] <= 100:
                raise ValueError("Invalid network metrics: usage must be between 0 and 100")

    def _generate_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of overall system performance."""
        try:
            # Calculate overall health score (0-100)
            health_scores = {
                'cpu': 100 - metrics['cpu']['usage'],
                'memory': 100 - metrics['memory']['usage'],
                'disk': 100 - metrics['disk']['usage'],
                'network': 100 - metrics['network'].get('usage', 0)
            }
            
            overall_health = sum(health_scores.values()) / len(health_scores)
            
            # Calculate performance score based on component weights
            weights = {
                'cpu': 0.35,  # CPU has highest weight
                'memory': 0.30,  # Memory second highest
                'disk': 0.20,  # Disk third
                'network': 0.15  # Network least weight
            }
            
            performance_score = sum(
                score * weights[component]
                for component, score in health_scores.items()
            )
            
            # Determine overall status
            status = 'healthy'
            overall_status = 'optimal'
            if overall_health < 60:
                status = 'critical'
                overall_status = 'critical'
            elif overall_health < 75:
                status = 'warning'
                overall_status = 'degraded'
                
            # Identify bottlenecks and critical issues
            bottlenecks = []
            critical_issues = []
            for component, score in health_scores.items():
                if score < 60:
                    issue = {
                        'component': component,
                        'severity': 'critical',
                        'score': score,
                        'description': f"{component.upper()} performance is critically low"
                    }
                    bottlenecks.append(issue)
                    critical_issues.append(issue)
                elif score < 75:
                    bottlenecks.append({
                        'component': component,
                        'severity': 'warning',
                        'score': score
                    })
                    
            # Add additional critical issues
            if metrics['memory']['free'] < 1024 * 1024 * 100:  # Less than 100MB free memory
                critical_issues.append({
                    'component': 'memory',
                    'severity': 'critical',
                    'description': 'Critically low free memory'
                })
                
            if metrics['disk']['free'] < 1024 * 1024 * 1024:  # Less than 1GB free disk
                critical_issues.append({
                    'component': 'disk',
                    'severity': 'critical',
                    'description': 'Critically low free disk space'
                })
            
            # Generate summary text
            summary_text = f"System health is {status} ({overall_health:.1f}%)"
            if bottlenecks:
                summary_text += " with performance bottlenecks detected"
            if critical_issues:
                summary_text += f" and {len(critical_issues)} critical issues"
            
            return {
                'status': status,
                'overall_status': overall_status,
                'health_score': overall_health,
                'performance_score': performance_score,
                'bottlenecks': bottlenecks,
                'critical_issues': critical_issues,
                'summary': summary_text,
                'component_scores': health_scores
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return {
                'status': 'error',
                'overall_status': 'unknown',
                'error': str(e),
                'health_score': 0,
                'performance_score': 0,
                'bottlenecks': [],
                'critical_issues': [],
                'summary': 'Error generating performance summary',
                'component_scores': {}
            }

    def _generate_overall_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate overall system recommendations."""
        recommendations = []
        
        # Check CPU recommendations
        cpu_usage = metrics['cpu']['usage']
        if cpu_usage > 80:
            recommendations.append({
                'component': 'cpu',
                'priority': 'high',
                'message': 'Consider CPU upgrade or load balancing',
                'impact': 'System performance and responsiveness'
            })
        elif cpu_usage > 60:
            recommendations.append({
                'component': 'cpu',
                'priority': 'medium',
                'message': 'Monitor CPU usage trends',
                'impact': 'Proactive capacity planning'
            })
            
        # Check memory recommendations
        memory_usage = metrics['memory']['usage']
        memory_free = metrics['memory']['free']
        if memory_usage > 80:
            recommendations.append({
                'component': 'memory',
                'priority': 'high',
                'message': 'Memory upgrade recommended',
                'impact': 'Application stability and performance'
            })
        elif memory_free < 1024 * 1024 * 500:  # Less than 500MB free
            recommendations.append({
                'component': 'memory',
                'priority': 'high',
                'message': 'Critical: Low memory available',
                'impact': 'System stability at risk'
            })
            
        # Check disk recommendations
        disk_usage = metrics['disk']['usage']
        disk_free = metrics['disk']['free']
        if disk_usage > 85:
            recommendations.append({
                'component': 'disk',
                'priority': 'high',
                'message': 'Disk space critically low',
                'impact': 'System stability and data integrity'
            })
        elif disk_free < 1024 * 1024 * 1024 * 10:  # Less than 10GB free
            recommendations.append({
                'component': 'disk',
                'priority': 'medium',
                'message': 'Plan for disk space expansion',
                'impact': 'Future system operations'
            })
            
        # Check network recommendations
        if 'usage' in metrics['network']:
            network_usage = metrics['network']['usage']
            if network_usage > 75:
                recommendations.append({
                    'component': 'network',
                    'priority': 'medium',
                    'message': 'Network bandwidth may need upgrade',
                    'impact': 'Data transfer speeds and response times'
                })
                
        # Add overall system recommendations
        component_usages = [
            metrics['cpu']['usage'],
            metrics['memory']['usage'],
            metrics['disk']['usage']
        ]
        if 'usage' in metrics['network']:
            component_usages.append(metrics['network']['usage'])
            
        avg_usage = sum(component_usages) / len(component_usages)
        if avg_usage > 75:
            recommendations.append({
                'component': 'system',
                'priority': 'high',
                'message': 'Overall system resources strained',
                'impact': 'General system performance and reliability'
            })
            
        return recommendations