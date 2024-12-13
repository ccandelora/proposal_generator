"""Web-friendly progress tracking utilities."""
from typing import List, Dict, Any, Optional
import time
from dataclasses import dataclass
from datetime import datetime
import asyncio
from fastapi import WebSocket

@dataclass
class SubTaskProgress:
    """Progress information for a subtask."""
    name: str
    status: str
    progress: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

@dataclass
class ProgressState:
    """Progress state for web interface."""
    status: str
    progress: int
    completed_steps: List[str]
    current_step: str
    sub_tasks: Dict[str, SubTaskProgress]
    elapsed_time: int
    stage: str
    is_complete: bool
    error: str = ""
    estimated_time_remaining: Optional[int] = None

class WebProgressTracker:
    """Track progress for web interface."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.current_status = ""
        self.overall_progress = 0
        self.completed_steps = []
        self.start_time = time.time()
        self.stage_times = {}
        self.stage_progress = {}
        self.last_update = time.time()
        self.progress_history = []

    def get_default_state(self) -> Dict[str, Any]:
        """Get default progress state."""
        return {
            'status': self.current_status,
            'progress': self.overall_progress,
            'completed_steps': self.completed_steps,
            'elapsed_time': int(time.time() - self.start_time),
            'estimated_remaining': None,
            'stage_progress': self.stage_progress,
            'current_stage': self.current_status.split(':')[0] if ':' in self.current_status else self.current_status,
            'error': None
        }

    async def update(self, status: str, progress: float, completed_steps: List[str]) -> Dict[str, Any]:
        """Update progress and return current state."""
        try:
            self.current_status = status
            self.overall_progress = progress
            self.completed_steps = completed_steps
            
            # Update stage progress
            if ':' in status:
                stage, detail = status.split(':', 1)
                stage = stage.strip()
                if stage not in self.stage_times:
                    self.stage_times[stage] = time.time()
                self.stage_progress[stage] = progress
            
            # Track progress history
            self.progress_history.append({
                'time': time.time(),
                'status': status,
                'progress': progress
            })
            
            # Calculate estimated time remaining
            estimated_remaining = self._estimate_remaining_time()
            
            # Return current state
            return {
                'status': self.current_status,
                'progress': self.overall_progress,
                'completed_steps': self.completed_steps,
                'elapsed_time': int(time.time() - self.start_time),
                'estimated_remaining': estimated_remaining,
                'stage_progress': self.stage_progress,
                'current_stage': status.split(':')[0] if ':' in status else status,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")
            # Return default state with error
            state = self.get_default_state()
            state['error'] = str(e)
            return state

    def _estimate_remaining_time(self) -> Optional[int]:
        """Estimate remaining time in seconds."""
        if len(self.progress_history) < 2:
            return None
            
        # Calculate progress speed
        recent_history = [
            p for p in self.progress_history
            if time.time() - p['time'] < 60  # Last minute
        ]
        
        if len(recent_history) < 2:
            return None
            
        progress_diff = recent_history[-1]['progress'] - recent_history[0]['progress']
        time_diff = recent_history[-1]['time'] - recent_history[0]['time']
        
        if time_diff <= 0 or progress_diff <= 0:
            return None
            
        progress_per_second = progress_diff / time_diff
        remaining_progress = 100 - self.overall_progress
        
        return int(remaining_progress / progress_per_second)