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
    """Track progress for web interface with WebSocket support."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.start_time = time.time()
        self.current_status = ""
        self.overall_progress = 0
        self.completed_steps = []
        self.current_stage = ""
        self.is_complete = False
        self.error = ""
        self.sub_tasks: Dict[str, SubTaskProgress] = {}
        self.active_connections: List[WebSocket] = []
        self.last_update_time = time.time()
        self.progress_history: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket):
        """Handle new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send current state to new connection
        await self.send_update(websocket, self.get_state())

    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        self.active_connections.remove(websocket)

    async def broadcast_update(self, state: Dict[str, Any]):
        """Broadcast update to all connected clients."""
        for connection in self.active_connections:
            await self.send_update(connection, state)

    async def send_update(self, websocket: WebSocket, state: Dict[str, Any]):
        """Send update to specific WebSocket connection."""
        try:
            await websocket.send_json(state)
        except Exception:
            await self.disconnect(websocket)

    def start_subtask(self, name: str, status: str = "Starting...") -> None:
        """Start tracking a new subtask."""
        self.sub_tasks[name] = SubTaskProgress(
            name=name,
            status=status,
            progress=0,
            started_at=datetime.now()
        )
        asyncio.create_task(self._broadcast_state())

    def update_subtask(self, name: str, progress: int, status: str = None) -> None:
        """Update subtask progress."""
        if name in self.sub_tasks:
            task = self.sub_tasks[name]
            task.progress = progress
            if status:
                task.status = status
            if progress >= 100:
                task.completed_at = datetime.now()
            asyncio.create_task(self._broadcast_state())

    async def update(self, status: str, progress: int, completed_steps: List[str]) -> Dict[str, Any]:
        """Update progress and broadcast state."""
        self.current_status = status
        self.overall_progress = progress
        self.completed_steps = completed_steps
        
        # Calculate rate of progress
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        if time_diff > 0:
            progress_diff = progress - self.progress_history[-1]['progress'] if self.progress_history else 0
            progress_rate = progress_diff / time_diff
            
            # Estimate time remaining
            if progress_rate > 0:
                remaining_progress = 100 - progress
                estimated_seconds = remaining_progress / progress_rate
                self.estimated_time_remaining = int(estimated_seconds)
        
        # Update history
        state = self.get_state()
        self.progress_history.append(state)
        self.last_update_time = current_time
        
        # Broadcast update
        await self._broadcast_state()
        return state

    async def _broadcast_state(self):
        """Broadcast current state to all connections."""
        state = self.get_state()
        await self.broadcast_update(state)

    def get_state(self) -> Dict[str, Any]:
        """Get current progress state for web interface."""
        current_time = time.time()
        return {
            'status': self.current_status,
            'progress': self.overall_progress,
            'completed_steps': self.completed_steps,
            'elapsed_time': int(current_time - self.start_time),
            'stage': self.current_stage,
            'is_complete': self.is_complete,
            'error': self.error,
            'timestamp': datetime.now().isoformat(),
            'sub_tasks': {
                name: {
                    'name': task.name,
                    'status': task.status,
                    'progress': task.progress,
                    'started_at': task.started_at.isoformat(),
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'error': task.error
                }
                for name, task in self.sub_tasks.items()
            },
            'estimated_time_remaining': self.estimated_time_remaining,
            'progress_rate': self._calculate_progress_rate(),
            'detailed_status': self._generate_detailed_status()
        }

    def _calculate_progress_rate(self) -> Optional[float]:
        """Calculate progress rate per minute."""
        if len(self.progress_history) < 2:
            return None
            
        latest = self.progress_history[-1]
        minute_ago = next(
            (state for state in reversed(self.progress_history)
             if state['timestamp'] < latest['timestamp'] - 60),
            None
        )
        
        if minute_ago:
            progress_diff = latest['progress'] - minute_ago['progress']
            return progress_diff

        return None

    def _generate_detailed_status(self) -> Dict[str, Any]:
        """Generate detailed status information."""
        return {
            'active_tasks': [
                task for task in self.sub_tasks.values()
                if not task.completed_at
            ],
            'recent_completions': [
                task for task in self.sub_tasks.values()
                if task.completed_at and 
                (datetime.now() - task.completed_at).total_seconds() < 300
            ],
            'current_phase': self.current_stage,
            'phase_progress': self._get_phase_progress()
        }

    def _get_phase_progress(self) -> Dict[str, Any]:
        """Get detailed progress for current phase."""
        return {
            'name': self.current_stage,
            'progress': self.overall_progress,
            'sub_tasks_complete': len([t for t in self.sub_tasks.values() if t.completed_at]),
            'sub_tasks_total': len(self.sub_tasks)
        }