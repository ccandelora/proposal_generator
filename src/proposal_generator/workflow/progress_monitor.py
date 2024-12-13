from typing import Dict, Any, List, Optional
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ProgressMonitor(BaseModel):
    """Monitor and track workflow progress."""
    
    current_phase: int = Field(default=0, description="Current phase number")
    total_phases: int = Field(default=0, description="Total number of phases")
    phase_progress: float = Field(default=0.0, description="Progress of current phase (0-100)")
    overall_progress: float = Field(default=0.0, description="Overall workflow progress (0-100)")
    status: str = Field(default="initializing", description="Current status of the workflow")
    message: str = Field(default="", description="Current status message")
    errors: List[str] = Field(default_factory=list, description="List of errors")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    completed_tasks: List[str] = Field(default_factory=list, description="List of completed tasks")
    remaining_tasks: List[str] = Field(default_factory=list, description="List of remaining tasks")
    phase_details: Dict[int, Dict[str, Any]] = Field(default_factory=dict, description="Details for each phase")
    
    def start_workflow(self, total_phases: int, tasks: List[str]):
        """Initialize workflow progress tracking."""
        self.total_phases = total_phases
        self.current_phase = 1
        self.phase_progress = 0.0
        self.overall_progress = 0.0
        self.status = "running"
        self.message = "Workflow started"
        self.remaining_tasks = tasks.copy()
        self.completed_tasks = []
        
    def start_phase(self, phase_number: int, phase_tasks: List[str]):
        """Start tracking a new phase."""
        self.current_phase = phase_number
        self.phase_progress = 0.0
        self.status = f"phase_{phase_number}"
        self.message = f"Starting phase {phase_number}"
        self.phase_details[phase_number] = {
            'tasks': phase_tasks,
            'completed': [],
            'status': 'running',
            'start_time': None,
            'end_time': None
        }
        
    def complete_task(self, task_name: str):
        """Mark a task as completed."""
        if task_name in self.remaining_tasks:
            self.remaining_tasks.remove(task_name)
            self.completed_tasks.append(task_name)
            
            # Update phase progress
            if self.current_phase in self.phase_details:
                phase = self.phase_details[self.current_phase]
                phase['completed'].append(task_name)
                total_tasks = len(phase['tasks'])
                completed_tasks = len(phase['completed'])
                self.phase_progress = (completed_tasks / total_tasks) * 100
                
            # Update overall progress
            total_tasks = len(self.completed_tasks) + len(self.remaining_tasks)
            self.overall_progress = (len(self.completed_tasks) / total_tasks) * 100
            
    def complete_phase(self, phase_number: int):
        """Mark a phase as completed."""
        if phase_number in self.phase_details:
            self.phase_details[phase_number]['status'] = 'completed'
            self.phase_progress = 100.0
            
            if phase_number < self.total_phases:
                self.current_phase = phase_number + 1
                self.phase_progress = 0.0
            else:
                self.status = "completed"
                self.message = "Workflow completed"
                
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.status = "error"
        self.message = f"Error: {error}"
        
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
        
    def update_status(self, status: str, message: Optional[str] = None):
        """Update workflow status."""
        self.status = status
        if message:
            self.message = message
            
    def get_phase_details(self, phase_number: int) -> Dict[str, Any]:
        """Get details for a specific phase."""
        return self.phase_details.get(phase_number, {})
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow progress."""
        return {
            'current_phase': self.current_phase,
            'total_phases': self.total_phases,
            'phase_progress': self.phase_progress,
            'overall_progress': self.overall_progress,
            'status': self.status,
            'message': self.message,
            'completed_tasks': len(self.completed_tasks),
            'remaining_tasks': len(self.remaining_tasks),
            'errors': len(self.errors),
            'warnings': len(self.warnings)
        }
        
    def update_phase_progress(self, progress: float, message: Optional[str] = None):
        """Update the progress of the current phase.
        
        Args:
            progress: Progress value between 0 and 100
            message: Optional status message
        """
        self.phase_progress = min(max(progress, 0.0), 100.0)
        
        if message:
            self.message = message
            
        # Update overall progress based on phase progress
        if self.total_phases > 0:
            completed_phases = self.current_phase - 1
            current_contribution = self.phase_progress / self.total_phases
            self.overall_progress = (completed_phases * 100.0 / self.total_phases) + current_contribution
            
        # Update phase details
        if self.current_phase in self.phase_details:
            self.phase_details[self.current_phase]['progress'] = self.phase_progress 