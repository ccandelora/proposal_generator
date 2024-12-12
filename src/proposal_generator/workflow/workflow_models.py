"""Workflow models for proposal generation."""
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json

class EnumEncoder(json.JSONEncoder):
    """JSON encoder that handles Enum values."""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

class WorkflowStatus(Enum):
    """Status of workflow execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    RESUMING = "resuming"

    def to_dict(self):
        """Convert to dictionary."""
        return self.value

class ComponentStatus(Enum):
    """Status of individual component execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CACHED = "cached"

    def to_dict(self):
        """Convert to dictionary."""
        return self.value

class QualityLevel(Enum):
    """Quality level of generated content."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

    def to_dict(self):
        """Convert to dictionary."""
        return self.value

@dataclass
class ComponentProgress:
    """Progress tracking for a workflow component."""
    component_name: str
    status: ComponentStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percent: float = 0.0
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component_name': self.component_name,
            'status': self.status.value if isinstance(self.status, ComponentStatus) else self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'progress_percent': self.progress_percent,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'cache_hit': self.cache_hit
        }

    def __str__(self) -> str:
        """String representation."""
        return f"{self.component_name}: {self.status.value} ({self.progress_percent:.1%})"

@dataclass
class QualityMetrics:
    """Quality metrics for generated content."""
    completeness: float  # 0-1 score
    relevance: float    # 0-1 score
    accuracy: float     # 0-1 score
    consistency: float  # 0-1 score
    readability: float  # 0-1 score
    overall_quality: QualityLevel
    validation_errors: List[str]
    warnings: List[str]
    suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['overall_quality'] = self.overall_quality.value
        return data

@dataclass
class WorkflowProgress:
    """Progress tracking for the entire workflow."""
    workflow_id: str
    status: WorkflowStatus
    start_time: datetime
    last_update_time: datetime
    estimated_completion_time: Optional[datetime]
    overall_progress: float  # 0-1
    current_phase: str
    component_progress: Dict[str, ComponentProgress]
    quality_metrics: Optional[QualityMetrics] = None
    checkpoints: Dict[str, Any] = None
    error_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'workflow_id': self.workflow_id,
            'status': self.status.value if isinstance(self.status, WorkflowStatus) else self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'estimated_completion_time': self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            'overall_progress': self.overall_progress,
            'current_phase': self.current_phase,
            'component_progress': {k: v.to_dict() for k, v in self.component_progress.items()},
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'checkpoints': {k: v.to_dict() for k, v in self.checkpoints.items()} if self.checkpoints else None,
            'error_count': self.error_count,
            'warning_count': self.warning_count
        }

@dataclass
class ValidationRule:
    """Rule for content validation."""
    rule_id: str
    component: str
    check_type: str
    severity: str  # error, warning, suggestion
    condition: str
    message: str
    fix_suggestion: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of content validation."""
    rule_id: str
    passed: bool
    severity: str
    message: str
    fix_suggestion: Optional[str]
    affected_content: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class WorkflowCheckpoint:
    """Checkpoint for workflow resumption."""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime
    phase: str
    component_states: Dict[str, Any]
    completed_steps: List[str]
    intermediate_results: Dict[str, Any]
    cache_keys: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'checkpoint_id': self.checkpoint_id,
            'workflow_id': self.workflow_id,
            'timestamp': self.timestamp.isoformat(),
            'phase': self.phase,
            'component_states': {
                k: {
                    **v,
                    'status': v['status'].value if isinstance(v['status'], ComponentStatus) else v['status']
                } for k, v in self.component_states.items()
            },
            'completed_steps': self.completed_steps,
            'intermediate_results': self.intermediate_results,
            'cache_keys': self.cache_keys
        }
        return data

@dataclass
class ResumptionStrategy:
    """Strategy for workflow resumption after failure."""
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    fallback_options: Dict[str, Any] = None
    skip_failed_components: bool = False
    use_cached_results: bool = True
    validation_level: str = "strict"  # strict, lenient, skip

@dataclass
class WorkflowConfig:
    """Configuration for proposal workflow."""
    # API Keys and Configuration
    google_search_api_key: Optional[str] = None
    google_custom_search_id: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Output Configuration
    output_dir: Path = Path("output")
    cache_dir: Path = Path("cache")
    cache_results: bool = True
    
    # Feature Flags
    concurrent_analysis: bool = True
    include_mockups: bool = True
    include_seo: bool = True
    include_market: bool = True
    include_content: bool = True
    
    # Performance Settings
    max_workers: int = 4
    timeout: int = 300

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)

@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    success: bool
    workflow_id: str
    proposal_path: Optional[str] = None
    mockups: Optional[Dict[str, Any]] = None
    seo_insights: Optional[Dict[str, Any]] = None
    market_insights: Optional[Dict[str, Any]] = None
    content_plan: Optional[Dict[str, Any]] = None
    progress: Optional[WorkflowProgress] = None
    quality_metrics: Optional[QualityMetrics] = None
    validation_results: Optional[List[ValidationResult]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    execution_time: float = 0.0
    completion_date: str = ""
    checkpoints: Optional[List[WorkflowCheckpoint]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'success': self.success,
            'workflow_id': self.workflow_id,
            'proposal_path': self.proposal_path,
            'mockups': self.mockups,
            'seo_insights': self.seo_insights,
            'market_insights': self.market_insights,
            'content_plan': self.content_plan,
            'progress': self.progress.to_dict() if self.progress else None,
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'validation_results': [r.to_dict() for r in self.validation_results] if self.validation_results else None,
            'errors': self.errors,
            'warnings': self.warnings,
            'execution_time': self.execution_time,
            'completion_date': self.completion_date,
            'checkpoints': [c.to_dict() for c in self.checkpoints] if self.checkpoints else None
        }
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), cls=EnumEncoder) 