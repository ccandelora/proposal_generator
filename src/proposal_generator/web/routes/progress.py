from typing import Dict, Any, List
from fastapi import HTTPException
from fastapi.routing import APIRouter
from datetime import datetime, timedelta
import networkx as nx

router = APIRouter()

class TaskTracker:
    """Track detailed task progress and dependencies."""
    
    def __init__(self):
        self.task_graph = nx.DiGraph()
        self.start_times = {}
        self.estimated_durations = {
            'website_analysis': 180,  # seconds
            'market_analysis': 240,
            'competitor_analysis': 300,
            'design_system': 420,
            'mockup_generation': 600,
            'code_architecture': 360,
            'code_generation': 900,
            'ai_analysis': 240,
            'recommendation_generation': 300
        }
        self.task_priorities = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
    
    def get_task_dependencies(self) -> Dict[str, List[str]]:
        """Get task dependency mapping."""
        return {
            'market_analysis': ['website_analysis'],
            'competitor_analysis': ['website_analysis', 'market_analysis'],
            'design_system': ['competitor_analysis'],
            'mockup_generation': ['design_system'],
            'code_architecture': ['competitor_analysis', 'design_system'],
            'code_generation': ['code_architecture'],
            'ai_analysis': ['website_analysis', 'market_analysis'],
            'recommendation_generation': ['ai_analysis', 'competitor_analysis']
        }
    
    def calculate_completion_times(self) -> Dict[str, datetime]:
        """Calculate estimated completion times for each task."""
        now = datetime.now()
        completion_times = {}
        
        # Build dependency graph
        dependencies = self.get_task_dependencies()
        for task, deps in dependencies.items():
            for dep in deps:
                self.task_graph.add_edge(dep, task)
        
        # Calculate completion times based on dependencies
        sorted_tasks = list(nx.topological_sort(self.task_graph))
        
        for task in sorted_tasks:
            deps = dependencies.get(task, [])
            if deps:
                # Task starts after all dependencies complete
                start_time = max(completion_times[dep] for dep in deps)
            else:
                # No dependencies, start from current time
                start_time = now
            
            duration = timedelta(seconds=self.estimated_durations.get(task, 300))
            completion_times[task] = start_time + duration
        
        return completion_times
    
    def calculate_critical_path(self) -> Dict[str, Any]:
        """Calculate critical path and task slack times."""
        try:
            # Calculate earliest start times
            earliest_start = {}
            for task in nx.topological_sort(self.task_graph):
                predecessors = list(self.task_graph.predecessors(task))
                if not predecessors:
                    earliest_start[task] = 0
                else:
                    earliest_start[task] = max(
                        earliest_start[p] + self.estimated_durations[p]
                        for p in predecessors
                    )
            
            # Calculate latest start times
            latest_start = {}
            for task in reversed(list(nx.topological_sort(self.task_graph))):
                successors = list(self.task_graph.successors(task))
                if not successors:
                    latest_start[task] = earliest_start[task]
                else:
                    latest_start[task] = min(
                        latest_start[s] - self.estimated_durations[task]
                        for s in successors
                    )
            
            # Calculate slack time and identify critical path
            critical_path = []
            task_slack = {}
            for task in self.task_graph.nodes():
                slack = latest_start[task] - earliest_start[task]
                task_slack[task] = slack
                if slack == 0:
                    critical_path.append(task)
            
            return {
                'critical_path': critical_path,
                'slack_times': task_slack,
                'earliest_start': earliest_start,
                'latest_start': latest_start
            }
            
        except Exception as e:
            logger.error(f"Error calculating critical path: {str(e)}")
            return {}
    
    def prioritize_tasks(self) -> Dict[str, Any]:
        """Prioritize tasks based on multiple factors."""
        try:
            critical_path_info = self.calculate_critical_path()
            task_priorities = {}
            
            for task in self.task_graph.nodes():
                # Calculate priority score based on multiple factors
                score = self._calculate_priority_score(
                    task,
                    critical_path_info['slack_times'].get(task, 0),
                    critical_path_info['critical_path'],
                    len(list(self.task_graph.successors(task)))
                )
                
                # Determine priority level
                if score >= 8:
                    priority = 'high'
                elif score >= 5:
                    priority = 'medium'
                else:
                    priority = 'low'
                
                task_priorities[task] = {
                    'priority': priority,
                    'score': score,
                    'factors': {
                        'on_critical_path': task in critical_path_info['critical_path'],
                        'slack_time': critical_path_info['slack_times'].get(task, 0),
                        'blocking_tasks': len(list(self.task_graph.successors(task))),
                        'dependencies_met': self._check_dependencies_met(task)
                    }
                }
            
            return task_priorities
            
        except Exception as e:
            logger.error(f"Error prioritizing tasks: {str(e)}")
            return {}
    
    def _calculate_priority_score(self, task: str, slack: float, 
                                critical_path: List[str], blocking_count: int) -> float:
        """Calculate task priority score."""
        score = 0
        
        # Critical path factor (0-4 points)
        if task in critical_path:
            score += 4
        
        # Slack time factor (0-3 points)
        if slack == 0:
            score += 3
        elif slack <= 300:  # 5 minutes
            score += 2
        elif slack <= 600:  # 10 minutes
            score += 1
        
        # Blocking factor (0-2 points)
        score += min(blocking_count, 2)
        
        # Dependencies factor (0-1 point)
        if self._check_dependencies_met(task):
            score += 1
        
        return score
    
    def _check_dependencies_met(self, task: str) -> bool:
        """Check if all dependencies for a task are completed."""
        return all(
            self._get_task_status(dep) == 'completed'
            for dep in self.task_graph.predecessors(task)
        )
    
    def _get_task_status(self, task: str) -> str:
        """Get current status of a task."""
        # Implementation depends on how you track task status
        pass

@router.get("/agent-progress")
async def get_agent_progress() -> Dict[str, Any]:
    """Get detailed progress for all agents."""
    try:
        tracker = TaskTracker()
        completion_times = tracker.calculate_completion_times()
        critical_path_info = tracker.calculate_critical_path()
        task_priorities = tracker.prioritize_tasks()
        
        return {
            "overall_status": "in progress",
            "estimated_completion": max(completion_times.values()).isoformat(),
            "task_dependencies": tracker.get_task_dependencies(),
            "critical_path": critical_path_info['critical_path'],
            "task_priorities": task_priorities,
            "competitor_agent": {
                "progress": 45,
                "status": "In Progress",
                "tasks": [
                    {
                        "name": "Website Analysis",
                        "status": "Completed",
                        "progress": 100,
                        "started_at": datetime.now().isoformat(),
                        "estimated_completion": completion_times['website_analysis'].isoformat(),
                        "dependencies": [],
                        "blocking": ["market_analysis", "competitor_analysis"],
                        "priority": task_priorities['website_analysis']['priority'],
                        "on_critical_path": "website_analysis" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('website_analysis', 0)
                    },
                    {
                        "name": "Market Position Analysis",
                        "status": "In Progress",
                        "progress": 60,
                        "started_at": datetime.now().isoformat(),
                        "estimated_completion": completion_times['market_analysis'].isoformat(),
                        "dependencies": ["website_analysis"],
                        "blocking": ["competitor_analysis"],
                        "priority": task_priorities['market_analysis']['priority'],
                        "on_critical_path": "market_analysis" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('market_analysis', 0)
                    },
                    {
                        "name": "Differentiator Analysis",
                        "status": "Pending",
                        "progress": 0,
                        "estimated_completion": completion_times['competitor_analysis'].isoformat(),
                        "dependencies": ["website_analysis", "market_analysis"],
                        "blocking": ["design_system", "code_architecture"],
                        "priority": task_priorities['competitor_analysis']['priority'],
                        "on_critical_path": "competitor_analysis" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('competitor_analysis', 0)
                    }
                ]
            },
            "design_agent": {
                "progress": 30,
                "status": "In Progress",
                "tasks": [
                    {
                        "name": "Design System Creation",
                        "status": "In Progress",
                        "progress": 75,
                        "started_at": datetime.now().isoformat(),
                        "estimated_completion": completion_times['design_system'].isoformat(),
                        "dependencies": ["competitor_analysis"],
                        "blocking": ["mockup_generation", "code_architecture"],
                        "priority": task_priorities['design_system']['priority'],
                        "on_critical_path": "design_system" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('design_system', 0)
                    },
                    {
                        "name": "Mockup Generation",
                        "status": "Pending",
                        "progress": 0,
                        "estimated_completion": completion_times['mockup_generation'].isoformat(),
                        "dependencies": ["design_system"],
                        "blocking": [],
                        "priority": task_priorities['mockup_generation']['priority'],
                        "on_critical_path": "mockup_generation" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('mockup_generation', 0)
                    }
                ]
            },
            "code_agent": {
                "progress": 15,
                "status": "Waiting",
                "tasks": [
                    {
                        "name": "Architecture Planning",
                        "status": "In Progress",
                        "progress": 40,
                        "started_at": datetime.now().isoformat(),
                        "estimated_completion": completion_times['code_architecture'].isoformat(),
                        "dependencies": ["competitor_analysis", "design_system"],
                        "blocking": ["code_generation"],
                        "priority": task_priorities['code_architecture']['priority'],
                        "on_critical_path": "code_architecture" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('code_architecture', 0)
                    },
                    {
                        "name": "Code Generation",
                        "status": "Pending",
                        "progress": 0,
                        "estimated_completion": completion_times['code_generation'].isoformat(),
                        "dependencies": ["code_architecture"],
                        "blocking": [],
                        "priority": task_priorities['code_generation']['priority'],
                        "on_critical_path": "code_generation" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('code_generation', 0)
                    }
                ]
            },
            "ai_agent": {
                "progress": 20,
                "status": "In Progress",
                "tasks": [
                    {
                        "name": "Data Analysis",
                        "status": "Completed",
                        "progress": 100,
                        "started_at": datetime.now().isoformat(),
                        "estimated_completion": completion_times['ai_analysis'].isoformat(),
                        "dependencies": ["website_analysis", "market_analysis"],
                        "blocking": ["recommendation_generation"],
                        "priority": task_priorities['ai_analysis']['priority'],
                        "on_critical_path": "ai_analysis" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('ai_analysis', 0)
                    },
                    {
                        "name": "Recommendation Generation",
                        "status": "In Progress",
                        "progress": 30,
                        "estimated_completion": completion_times['recommendation_generation'].isoformat(),
                        "dependencies": ["ai_analysis", "competitor_analysis"],
                        "blocking": [],
                        "priority": task_priorities['recommendation_generation']['priority'],
                        "on_critical_path": "recommendation_generation" in critical_path_info['critical_path'],
                        "slack_time": critical_path_info['slack_times'].get('recommendation_generation', 0)
                    }
                ]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting agent progress: {str(e)}"
        ) 