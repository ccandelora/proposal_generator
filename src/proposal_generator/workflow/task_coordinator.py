from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)

class TaskCoordinator:
    """Coordinates task execution and handles dependencies."""
    
    def __init__(self, execution_plan: Dict[str, Any]):
        self.execution_plan = execution_plan
        self.completed_tasks = set()
        self.task_results = {}
        
    async def can_execute_task(self, task_name: str) -> bool:
        """Check if a task's dependencies are met."""
        dependencies = self.execution_plan.get('dependencies', {}).get(task_name, [])
        return all(dep in self.completed_tasks for dep in dependencies)
    
    async def execute_phase(self, phase: Dict[str, Any], crews: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a phase of tasks."""
        if phase.get('parallel_tasks'):
            # Execute tasks in parallel
            tasks = []
            for task in phase['parallel_tasks']:
                if await self.can_execute_task(task['task']):
                    crew = crews[task['agent']]
                    tasks.append(crew.kickoff())
            
            results = await asyncio.gather(*tasks)
            
            # Update completed tasks
            for task in phase['parallel_tasks']:
                self.completed_tasks.add(task['task'])
            
            return results
        else:
            # Execute tasks sequentially
            results = []
            for task in phase['sequential_tasks']:
                if await self.can_execute_task(task['task']):
                    crew = crews[task['agent']]
                    result = await crew.kickoff()
                    results.append(result)
                    self.completed_tasks.add(task['task'])
            
            return results 