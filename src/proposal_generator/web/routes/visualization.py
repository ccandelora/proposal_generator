from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..visualization.expertise_visualizer import ExpertiseVisualizer

router = APIRouter()
visualizer = ExpertiseVisualizer()

@router.get("/expertise-visualization")
async def get_expertise_visualization(
    agent_memory,
    time_range: str = "all",
    domains: List[str] = None,
    agents: List[str] = None,
    metrics: List[str] = None
) -> Dict[str, Any]:
    """Get filtered expertise visualization dashboard."""
    try:
        # Get expertise map
        expertise_map = await agent_memory.get_agent_expertise_map()
        
        # Apply filters
        if agents:
            expertise_map = {k: v for k, v in expertise_map.items() if k in agents}
        
        if domains:
            for agent_id in expertise_map:
                expertise_map[agent_id]['domains'] = {
                    k: v for k, v in expertise_map[agent_id]['domains'].items()
                    if k in domains
                }
        
        # Generate visualizations
        dashboard = visualizer.generate_expertise_dashboard(expertise_map)
        
        # Filter metrics if specified
        if metrics:
            dashboard = {k: v for k, v in dashboard.items() if k in metrics}
        
        return {
            "status": "success",
            "data": dashboard,
            "metadata": {
                "time_range": time_range,
                "filtered_agents": len(expertise_map),
                "filtered_domains": len(next(iter(expertise_map.values()))['domains'])
                if expertise_map else 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        ) 