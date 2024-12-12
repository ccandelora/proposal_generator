"""Tests for the performance analyzer module."""

import pytest
from src.proposal_generator.components.performance_analyzer import PerformanceAnalyzer

@pytest.fixture
def performance_analyzer():
    return PerformanceAnalyzer()

@pytest.fixture
def sample_metrics():
    return {
        'timestamp': 1639152000.0,  # 2021-12-10 12:00:00
        'cpu': {
            'usage': 75.5,
            'cores': 8,
            'frequency': 2.5,
            'temperature': 65.0
        },
        'memory': {
            'total': 16384,  # MB
            'used': 8192,
            'free': 8192,
            'usage': 50.0
        },
        'disk': {
            'total': 512000,  # MB
            'used': 256000,
            'free': 256000,
            'usage': 50.0,
            'read_speed': 150.0,
            'write_speed': 100.0
        },
        'network': {
            'bytes_sent': 1024000,
            'bytes_recv': 2048000,
            'packets_sent': 1000,
            'packets_recv': 2000,
            'usage': 45.0
        }
    }

def test_performance_analyzer_initialization(performance_analyzer):
    """Test performance analyzer initialization."""
    assert performance_analyzer is not None
    assert performance_analyzer.logger is not None
    assert isinstance(performance_analyzer.warning_thresholds, dict)
    assert isinstance(performance_analyzer.critical_thresholds, dict)

def test_validate_metric_value_success(performance_analyzer):
    """Test metric value validation success cases."""
    assert performance_analyzer._validate_metric_value(10.5) == 10.5
    assert performance_analyzer._validate_metric_value(0) == 0.0
    assert performance_analyzer._validate_metric_value("50.5") == 50.5

def test_validate_metric_value_failure(performance_analyzer):
    """Test metric value validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_metric_value(-1)
    with pytest.raises(ValueError):
        performance_analyzer._validate_metric_value("invalid")
    with pytest.raises(ValueError):
        performance_analyzer._validate_metric_value(None)

def test_validate_timestamp_success(performance_analyzer):
    """Test timestamp validation success cases."""
    assert performance_analyzer._validate_timestamp(1639152000.0) == 1639152000.0
    assert performance_analyzer._validate_timestamp(0) == 0.0
    assert performance_analyzer._validate_timestamp("1639152000.0") == 1639152000.0

def test_validate_timestamp_failure(performance_analyzer):
    """Test timestamp validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_timestamp(-1)
    with pytest.raises(ValueError):
        performance_analyzer._validate_timestamp("invalid")
    with pytest.raises(ValueError):
        performance_analyzer._validate_timestamp(None)

def test_validate_percentage_success(performance_analyzer):
    """Test percentage validation success cases."""
    assert performance_analyzer._validate_percentage(50.5) == 50.5
    assert performance_analyzer._validate_percentage(0) == 0.0
    assert performance_analyzer._validate_percentage(100) == 100.0

def test_validate_percentage_failure(performance_analyzer):
    """Test percentage validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_percentage(-1)
    with pytest.raises(ValueError):
        performance_analyzer._validate_percentage(101)
    with pytest.raises(ValueError):
        performance_analyzer._validate_percentage("invalid")

def test_validate_metrics_data_success(performance_analyzer, sample_metrics):
    """Test metrics data validation success cases."""
    performance_analyzer._validate_metrics_data(sample_metrics)
    # Test without timestamp (should be optional)
    metrics_no_timestamp = sample_metrics.copy()
    del metrics_no_timestamp['timestamp']
    performance_analyzer._validate_metrics_data(metrics_no_timestamp)

def test_validate_metrics_data_failure(performance_analyzer):
    """Test metrics data validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_metrics_data({})
    with pytest.raises(ValueError):
        performance_analyzer._validate_metrics_data({'cpu': {}})
    with pytest.raises(ValueError):
        performance_analyzer._validate_metrics_data({'cpu': 'invalid'})

def test_validate_memory_metrics_success(performance_analyzer):
    """Test memory metrics validation success cases."""
    valid_metrics = {
        'total': 16384,
        'used': 8192,
        'free': 8192,
        'usage': 50.0
    }
    performance_analyzer._validate_memory_metrics(valid_metrics)

def test_validate_memory_metrics_failure(performance_analyzer):
    """Test memory metrics validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_memory_metrics({})
    with pytest.raises(ValueError):
        performance_analyzer._validate_memory_metrics({'total': -1})
    with pytest.raises(ValueError):
        performance_analyzer._validate_memory_metrics({'usage': 101})

def test_validate_disk_metrics_success(performance_analyzer):
    """Test disk metrics validation success cases."""
    valid_metrics = {
        'total': 512000,
        'used': 256000,
        'free': 256000,
        'usage': 50.0
    }
    performance_analyzer._validate_disk_metrics(valid_metrics)

def test_validate_disk_metrics_failure(performance_analyzer):
    """Test disk metrics validation failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer._validate_disk_metrics({})
    with pytest.raises(ValueError):
        performance_analyzer._validate_disk_metrics({'total': -1})
    with pytest.raises(ValueError):
        performance_analyzer._validate_disk_metrics({'usage': 101})

def test_analyze_cpu_performance_success(performance_analyzer, sample_metrics):
    """Test CPU performance analysis success cases."""
    result = performance_analyzer.analyze_cpu_performance(sample_metrics['cpu'])
    assert 'utilization' in result
    assert 'bottlenecks' in result
    assert 'recommendations' in result
    assert isinstance(result['utilization'], float)

def test_analyze_cpu_performance_failure(performance_analyzer):
    """Test CPU performance analysis failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer.analyze_cpu_performance({})
    with pytest.raises(ValueError):
        performance_analyzer.analyze_cpu_performance({'usage': 'invalid'})

def test_analyze_memory_usage_success(performance_analyzer, sample_metrics):
    """Test memory usage analysis success cases."""
    result = performance_analyzer.analyze_memory_usage(sample_metrics['memory'])
    assert 'usage_percent' in result
    assert 'total_memory' in result
    assert 'used_memory' in result
    assert 'available_memory' in result
    assert 'usage_pattern' in result
    assert 'health_status' in result
    assert 'recommendations' in result

def test_analyze_memory_usage_failure(performance_analyzer):
    """Test memory usage analysis failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer.analyze_memory_usage({})
    with pytest.raises(ValueError):
        performance_analyzer.analyze_memory_usage({'usage': 'invalid'})

def test_analyze_disk_performance_success(performance_analyzer, sample_metrics):
    """Test disk performance analysis success cases."""
    result = performance_analyzer.analyze_disk_performance(sample_metrics['disk'])
    assert 'usage_percent' in result
    assert 'total_space' in result
    assert 'used_space' in result
    assert 'free_space' in result
    assert 'io_stats' in result
    assert 'health_status' in result
    assert 'recommendations' in result

def test_analyze_disk_performance_failure(performance_analyzer):
    """Test disk performance analysis failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer.analyze_disk_performance({})
    with pytest.raises(ValueError):
        performance_analyzer.analyze_disk_performance({'usage': 'invalid'})

def test_analyze_network_performance_success(performance_analyzer, sample_metrics):
    """Test network performance analysis success cases."""
    result = performance_analyzer.analyze_network_performance(sample_metrics['network'])
    assert 'status' in result
    assert 'throughput' in result
    assert 'current_usage' in result
    assert isinstance(result['throughput'], dict)
    assert 'bytes_per_sec' in result['throughput']
    assert 'packets_per_sec' in result['throughput']

def test_analyze_network_performance_failure(performance_analyzer):
    """Test network performance analysis failure cases."""
    with pytest.raises(ValueError):
        performance_analyzer.analyze_network_performance({})
    with pytest.raises(ValueError):
        performance_analyzer.analyze_network_performance({'usage': 'invalid'}) 