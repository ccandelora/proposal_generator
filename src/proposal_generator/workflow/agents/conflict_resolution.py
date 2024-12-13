from enum import Enum
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Types of conflicts that can occur."""
    TECHNICAL = "technical"
    DESIGN = "design"
    RESOURCE = "resource"
    PRIORITY = "priority"
    APPROACH = "approach"
    IMPLEMENTATION = "implementation"
    REQUIREMENT = "requirement"

class ResolutionStrategy(Enum):
    """Available conflict resolution strategies."""
    CONSENSUS_BUILDING = "consensus_building"
    MEDIATION = "mediation"
    VOTING = "voting"
    EXPERT_DECISION = "expert_decision"
    COMPROMISE = "compromise"
    INTEGRATION = "integration"
    ESCALATION = "escalation"

@dataclass
class ResolutionHistory:
    """History of conflict resolutions."""
    conflict_type: ConflictType
    strategy_used: ResolutionStrategy
    success_rate: float
    resolution_time: float
    participant_satisfaction: float
    long_term_impact: float

class ConflictResolver:
    """Enhanced conflict resolution system."""
    
    def __init__(self):
        self.resolution_history: Dict[str, List[ResolutionHistory]] = {}
        self.learning_rate = 0.1
    
    async def resolve_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflict using learned strategies."""
        try:
            # Identify conflict type
            conflict_type = self._identify_conflict_type(conflict)
            
            # Get historical performance
            history = self._get_resolution_history(conflict_type)
            
            # Select best strategy based on history
            strategy = self._select_optimal_strategy(conflict_type, history)
            
            # Apply resolution strategy
            resolution = await self._apply_strategy(strategy, conflict)
            
            # Validate resolution
            if self._validate_resolution(resolution):
                # Update history with success
                self._update_resolution_history(
                    conflict_type,
                    strategy,
                    resolution,
                    success=True
                )
                return resolution
            
            # If primary strategy fails, try fallback
            fallback_resolution = await self._apply_fallback_strategy(conflict)
            self._update_resolution_history(
                conflict_type,
                ResolutionStrategy.ESCALATION,
                fallback_resolution,
                success=False
            )
            return fallback_resolution
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            return self._generate_emergency_resolution(conflict)
    
    def _select_optimal_strategy(self, conflict_type: ConflictType, 
                               history: List[ResolutionHistory]) -> ResolutionStrategy:
        """Select best strategy based on historical performance."""
        if not history:
            return self._get_default_strategy(conflict_type)
        
        # Calculate strategy scores
        strategy_scores = {}
        for record in history:
            score = (
                record.success_rate * 0.4 +
                record.participant_satisfaction * 0.3 +
                record.long_term_impact * 0.2 +
                (1.0 / record.resolution_time) * 0.1
            )
            strategy_scores[record.strategy_used] = score
        
        # Select best strategy
        return max(strategy_scores.items(), key=lambda x: x[1])[0] 