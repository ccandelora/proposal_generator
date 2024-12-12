"""Progress visualization utilities."""
import sys
import time
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.style import Style

class ProgressVisualizer:
    """Visualize workflow progress with rich formatting."""
    
    def __init__(self):
        """Initialize progress visualizer."""
        self.console = Console()
        self.current_status = ""
        self.current_stage = None
        self.overall_progress = 0
        self.completed_steps = []
        self.start_time = time.time()
        self.stage_times: Dict[str, float] = {}
        self.stage_progress: Dict[str, int] = {}
        self.last_update = time.time()
        self.progress_history = []
        
        # Create progress bars
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        
        self.overall_task = self.progress.add_task("Overall Progress", total=100)

    def update(self, status: str, progress: int, completed_steps: List[str]):
        """Update progress visualization."""
        self.current_status = status
        self.overall_progress = progress
        self.completed_steps = completed_steps
        
        # Update stage progress
        if ':' in status:
            stage, detail = status.split(':', 1)
            self.current_stage = stage.strip()
            if stage not in self.stage_times:
                self.stage_times[stage] = time.time()
            self.stage_progress[stage] = progress
        
        # Track progress history
        self.progress_history.append({
            'time': time.time(),
            'progress': progress,
            'status': status
        })
        
        # Update progress bar
        self.progress.update(self.overall_task, completed=progress)
        
        # Create status display
        self._render_status()

    def _render_status(self):
        """Render current status and completed steps."""
        # Clear previous output
        self.console.clear()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header"),
            Layout(name="main"),
            Layout(name="footer")
        )
        
        # Create main status table
        main_table = Table(show_header=False, box=None, padding=(0, 2))
        main_table.add_column("Status", style="cyan")
        
        # Add current status with detail
        if ':' in self.current_status:
            stage, detail = self.current_status.split(':', 1)
            main_table.add_row(
                Text.assemble(
                    ("Current Stage: ", "bold cyan"),
                    (stage, "cyan"),
                    ("\nDetail: ", "bold"),
                    (detail.strip(), "")
                )
            )
        else:
            main_table.add_row(f"Current Stage: {self.current_status}")
        
        # Add stage progress
        if self.current_stage:
            main_table.add_row("\nStage Progress:")
            stage_time = time.time() - self.stage_times.get(self.current_stage, time.time())
            progress_detail = self._get_stage_details()
            main_table.add_row(f"└── {progress_detail}")
            main_table.add_row(f"└── Time in stage: {int(stage_time)}s")
        
        # Add completed steps with timing
        if self.completed_steps:
            completed_text = Text("\nCompleted Steps:", style="green")
            for step in self.completed_steps:
                duration = ""
                if step in self.stage_times:
                    next_stage_time = self._get_next_stage_time(step)
                    duration = f" ({int(next_stage_time - self.stage_times[step])}s)"
                completed_text.append(f"\n✓ {step}{duration}", style="green")
            main_table.add_row(completed_text)
        
        # Add timing information
        elapsed = time.time() - self.start_time
        estimated = self._estimate_completion_time()
        main_table.add_row(Text("\nTiming Information:", style="bold"))
        main_table.add_row(f"├── Elapsed Time: {self._format_time(elapsed)}")
        if estimated:
            main_table.add_row(f"├── Estimated Remaining: {self._format_time(estimated)}")
            main_table.add_row(f"└── Estimated Completion: {self._format_datetime(time.time() + estimated)}")
        
        # Add progress metrics
        if self.progress_history:
            speed = self._calculate_progress_speed()
            if speed > 0:
                main_table.add_row(Text("\nProgress Metrics:", style="bold"))
                main_table.add_row(f"└── Speed: {speed:.1f}% per minute")
        
        # Create panel with all information
        panel = Panel(
            main_table,
            title="[bold blue]Proposal Generation Progress",
            border_style="blue",
            padding=(1, 2)
        )
        
        # Display everything
        with Live(panel, console=self.console, refresh_per_second=4):
            self.progress.update(self.overall_task, advance=0)  # Force refresh

    def _get_stage_details(self) -> str:
        """Get detailed progress information for current stage."""
        if not self.current_stage:
            return ""
            
        progress = self.stage_progress.get(self.current_stage, 0)
        time_in_stage = time.time() - self.stage_times.get(self.current_stage, time.time())
        
        if progress > 0:
            time_per_percent = time_in_stage / progress
            remaining_percent = 100 - progress
            estimated_remaining = time_per_percent * remaining_percent
            return f"Progress: {progress}% (Est. {self._format_time(estimated_remaining)} remaining)"
        
        return f"Progress: {progress}%"

    def _estimate_completion_time(self) -> Optional[float]:
        """Estimate time remaining based on progress history."""
        if len(self.progress_history) < 2:
            return None
            
        # Calculate progress speed
        speed = self._calculate_progress_speed()
        if speed <= 0:
            return None
            
        # Estimate remaining time
        remaining_progress = 100 - self.overall_progress
        return (remaining_progress / speed) * 60  # Convert to seconds

    def _calculate_progress_speed(self) -> float:
        """Calculate progress speed in percent per minute."""
        if len(self.progress_history) < 2:
            return 0.0
            
        # Get progress over last minute
        current_time = time.time()
        minute_ago = current_time - 60
        
        recent_history = [
            p for p in self.progress_history
            if p['time'] > minute_ago
        ]
        
        if len(recent_history) < 2:
            return 0.0
            
        progress_diff = recent_history[-1]['progress'] - recent_history[0]['progress']
        time_diff = recent_history[-1]['time'] - recent_history[0]['time']
        
        if time_diff <= 0:
            return 0.0
            
        return (progress_diff / time_diff) * 60  # Convert to per minute

    def _get_next_stage_time(self, stage: str) -> float:
        """Get the start time of the stage that followed the given stage."""
        stage_list = list(self.stage_times.items())
        for i, (s, t) in enumerate(stage_list):
            if s == stage and i + 1 < len(stage_list):
                return stage_list[i + 1][1]
        return time.time()

    def _format_time(self, seconds: float) -> str:
        """Format time duration."""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _format_datetime(self, timestamp: float) -> str:
        """Format datetime."""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%H:%M:%S")

    def complete(self):
        """Mark progress as complete."""
        self.progress.update(self.overall_task, completed=100)
        
        # Calculate statistics
        total_time = time.time() - self.start_time
        stage_durations = {}
        for stage in self.completed_steps:
            next_time = self._get_next_stage_time(stage)
            duration = next_time - self.stage_times[stage]
            stage_durations[stage] = duration
        
        # Show completion message and summary
        self.console.print("\n[bold green]✓ Proposal generation complete![/]")
        
        # Create summary table
        table = Table(title="Generation Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Add summary rows
        table.add_row("Total Time", self._format_time(total_time))
        table.add_row("Steps Completed", str(len(self.completed_steps)))
        table.add_row("Average Speed", f"{self._calculate_progress_speed():.1f}% per minute")
        
        # Add stage timing breakdown
        table.add_row("", "")
        table.add_row("Stage Breakdown", "")
        for stage, duration in stage_durations.items():
            table.add_row(f"  {stage}", self._format_time(duration))
        
        self.console.print(table)

    def error(self, error_message: str):
        """Display error message."""
        self.console.print(f"\n[bold red]Error: {error_message}[/]")
        
        # Show error summary
        table = Table(title="Error Details", show_header=True)
        table.add_column("Metric", style="red")
        table.add_column("Value", style="white")
        
        table.add_row("Failed Stage", self.current_stage or "Unknown")
        table.add_row("Progress", f"{self.overall_progress}%")
        table.add_row("Time Elapsed", self._format_time(time.time() - self.start_time))
        table.add_row("Error Message", error_message)
        
        self.console.print(table)