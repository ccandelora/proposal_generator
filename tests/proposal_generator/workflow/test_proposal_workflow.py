"""Tests for proposal workflow manager."""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from proposal_generator.workflow.workflow_models import (
    WorkflowConfig, WorkflowStatus, ComponentStatus, WorkflowProgress,
    ComponentProgress, QualityMetrics, ValidationResult, WorkflowResult,
    WorkflowCheckpoint, QualityLevel, ValidationRule, ResumptionStrategy
)
from proposal_generator.workflow.proposal_workflow import ProposalWorkflowManager

@pytest.fixture
def workflow_config():
    """Create test workflow configuration."""
    return WorkflowConfig(
        concurrent_analysis=True,
        max_workers=2,
        include_mockups=True,
        include_seo=True,
        include_market=True,
        include_content=True,
        output_dir=Path("./test_output"),
        cache_results=True,
        cache_dir=Path("./test_cache"),
        progress_tracking=True,
        quality_validation=True,
        validation_rules=[
            ValidationRule(
                rule_id="test_rule_1",
                component="mockup_generator",
                check_type="completeness",
                severity="error",
                condition="required_fields",
                message="Missing required fields",
                fix_suggestion="Add all required fields"
            )
        ],
        resumption_strategy=ResumptionStrategy(
            max_retries=2,
            retry_delay=1,
            skip_failed_components=True
        )
    )

@pytest.fixture
def workflow_manager(workflow_config):
    """Create test workflow manager."""
    return ProposalWorkflowManager(workflow_config)

@pytest.fixture
def client_info():
    """Create test client information."""
    return {
        "client_name": "Test Client",
        "business_name": "Test Business",
        "industry": "Technology",
        "target_market": "Small Businesses",
        "website": "https://example.com",
        "project_description": "Test project",
        "competitors": ["https://competitor1.com", "https://competitor2.com"],
        "requirements": {"design": "modern", "features": ["responsive", "fast"]}
    }

def test_workflow_initialization(workflow_manager):
    """Test workflow manager initialization."""
    assert workflow_manager.workflow_id is not None
    assert workflow_manager.progress.status == WorkflowStatus.NOT_STARTED
    assert len(workflow_manager.progress.component_progress) == 4
    assert all(c.status == ComponentStatus.PENDING 
              for c in workflow_manager.progress.component_progress.values())

def test_progress_tracking(workflow_manager):
    """Test progress tracking functionality."""
    component = "mockup_generator"
    workflow_manager._update_progress(component, ComponentStatus.RUNNING, "Testing", 0.5)
    
    progress = workflow_manager.progress.component_progress[component]
    assert progress.status == ComponentStatus.RUNNING
    assert progress.current_step == "Testing"
    assert progress.progress_percent == 0.5
    assert workflow_manager.progress.overall_progress > 0

def test_checkpoint_creation(workflow_manager):
    """Test checkpoint creation."""
    workflow_manager._update_progress("mockup_generator", ComponentStatus.RUNNING)
    checkpoint = workflow_manager._create_checkpoint()
    
    assert checkpoint.workflow_id == workflow_manager.workflow_id
    assert checkpoint.phase == workflow_manager.progress.current_phase
    assert len(checkpoint.component_states) == len(workflow_manager.progress.component_progress)

def test_validation(workflow_manager):
    """Test component output validation."""
    component = "mockup_generator"
    output = {"design": "modern"}  # Missing required fields
    
    results = workflow_manager._validate_component_output(component, output)
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].severity == "error"

def test_quality_metrics(workflow_manager):
    """Test quality metrics calculation."""
    outputs = {
        "mockup_generator": {"design": "modern", "layout": "responsive"},
        "seo_analyzer": {"score": 85, "recommendations": []},
        "market_analyzer": {"competitors": 5, "insights": []},
        "content_generator": {"sections": 3, "words": 1000}
    }
    
    metrics = workflow_manager._calculate_quality_metrics(outputs)
    assert isinstance(metrics, QualityMetrics)
    assert isinstance(metrics.overall_quality, QualityLevel)

@pytest.mark.asyncio
async def test_successful_proposal_generation(workflow_manager, client_info):
    """Test successful proposal generation workflow."""
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.return_value = {"test": "result"}
        
        result = workflow_manager.generate_proposal(client_info)
        
        assert result.success is True
        assert result.workflow_id == workflow_manager.workflow_id
        assert workflow_manager.progress.status == WorkflowStatus.COMPLETED
        assert result.execution_time > 0
        assert all(c.status in (ComponentStatus.COMPLETED, ComponentStatus.CACHED)
                  for c in workflow_manager.progress.component_progress.values())

@pytest.mark.asyncio
async def test_component_failure_handling(workflow_manager, client_info):
    """Test component failure handling and retry logic."""
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.side_effect = [
            Exception("Test error"),  # First attempt fails
            {"test": "result"}        # Retry succeeds
        ]
        
        result = workflow_manager.generate_proposal(client_info)
        
        comp_progress = next(iter(workflow_manager.progress.component_progress.values()))
        assert comp_progress.retry_count == 1
        assert result.success is True

@pytest.mark.asyncio
async def test_workflow_resumption(workflow_manager, client_info):
    """Test workflow resumption from checkpoint."""
    # Create a failed state
    workflow_manager._update_progress("mockup_generator", ComponentStatus.FAILED)
    checkpoint = workflow_manager._create_checkpoint()
    
    # Resume workflow
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.return_value = {"test": "result"}
        
        result = workflow_manager.resume_workflow(checkpoint.checkpoint_id)
        
        assert result.success is True
        assert workflow_manager.progress.status == WorkflowStatus.COMPLETED

def test_concurrent_execution(workflow_manager, client_info):
    """Test concurrent component execution."""
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.return_value = {"test": "result"}
        
        results = workflow_manager._run_concurrent_analysis(client_info)
        
        assert len(results) == len(workflow_manager.progress.component_progress)
        mock_execute.assert_called()

def test_sequential_execution(workflow_manager, client_info):
    """Test sequential component execution."""
    workflow_manager.config.concurrent_analysis = False
    
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.return_value = {"test": "result"}
        
        results = workflow_manager._run_sequential_analysis(client_info)
        
        assert len(results) == len(workflow_manager.progress.component_progress)
        assert mock_execute.call_count == len(workflow_manager.progress.component_progress)

def test_caching(workflow_manager, client_info):
    """Test result caching functionality."""
    component = "mockup_generator"
    test_result = {"test": "cached_result"}
    
    # Cache a result
    workflow_manager._cache_result(component, client_info, test_result)
    
    # Retrieve cached result
    cached = workflow_manager._get_cached_result(component, client_info)
    assert cached == test_result

def test_progress_estimation(workflow_manager):
    """Test completion time estimation."""
    start_time = datetime.now()
    workflow_manager.progress.start_time = start_time
    
    # Simulate 50% progress
    workflow_manager._update_progress("mockup_generator", ComponentStatus.RUNNING, progress=0.5)
    
    assert workflow_manager.progress.estimated_completion_time is not None
    estimated_duration = (
        workflow_manager.progress.estimated_completion_time - start_time
    ).total_seconds()
    assert estimated_duration > 0

def test_quality_validation_rules(workflow_manager):
    """Test quality validation rules."""
    component = "mockup_generator"
    output = {
        "design": "modern",
        "layout": "responsive",
        "assets": [],  # Missing required assets
    }
    
    # Add a specific validation rule
    workflow_manager.config.validation_rules.append(
        ValidationRule(
            rule_id="assets_check",
            component="mockup_generator",
            check_type="completeness",
            severity="warning",
            condition="has_assets",
            message="No assets provided",
            fix_suggestion="Add at least one asset"
        )
    )
    
    results = workflow_manager._validate_component_output(component, output)
    assert len(results) == 2  # Both rules should be checked
    assert any(r.rule_id == "assets_check" for r in results)

def test_error_handling(workflow_manager, client_info):
    """Test error handling and reporting."""
    with patch.object(workflow_manager, '_execute_component') as mock_execute:
        mock_execute.side_effect = Exception("Critical error")
        
        result = workflow_manager.generate_proposal(client_info)
        
        assert result.success is False
        assert len(result.errors) == 1
        assert workflow_manager.progress.status == WorkflowStatus.FAILED

def test_component_status_transitions(workflow_manager):
    """Test component status transitions."""
    component = "mockup_generator"
    progress = workflow_manager.progress.component_progress[component]
    
    # Test all status transitions
    workflow_manager._update_progress(component, ComponentStatus.RUNNING)
    assert progress.status == ComponentStatus.RUNNING
    
    workflow_manager._update_progress(component, ComponentStatus.COMPLETED)
    assert progress.status == ComponentStatus.COMPLETED
    
    workflow_manager._update_progress(component, ComponentStatus.FAILED)
    assert progress.status == ComponentStatus.FAILED
    
    workflow_manager._update_progress(component, ComponentStatus.SKIPPED)
    assert progress.status == ComponentStatus.SKIPPED 