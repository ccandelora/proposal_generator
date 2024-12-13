from crewai import Agent, Task
from typing import Dict, Any, List, Optional
import logging
from ..agent_memory import AgentMemory
from ..workflow_models import AgentMessage, AgentContext
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

class CollaborationMode(Enum):
    """Supported collaboration modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ITERATIVE = "iterative"
    REVIEW = "review"
    CONSENSUS = "consensus"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CollaborationRequest:
    """Collaboration request details."""
    task: Task
    mode: CollaborationMode
    participants: List[str]
    deadline: Optional[datetime] = None
    requirements: Dict[str, Any] = None
    review_criteria: Dict[str, Any] = None

@dataclass
class CollaborationResponse:
    """Collaboration response details."""
    request_id: str
    participant: str
    status: str
    result: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

@dataclass
class FeedbackMetrics:
    """Metrics for feedback evaluation."""
    quality_score: float
    confidence_score: float
    agreement_level: float
    impact_score: float
    implementation_feasibility: float

@dataclass
class ConflictResolution:
    """Conflict resolution details."""
    conflict_type: str
    participants: List[str]
    proposals: Dict[str, Any]
    resolution_strategy: str
    resolution_result: Any
    consensus_level: float

class ResultSynthesizer:
    """Helper class for result synthesis."""
    
    @staticmethod
    def synthesize(results: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Synthesize results with weighted contributions."""
        if not weights:
            weights = {participant: 1.0/len(results) for participant in results}
        
        synthesized = {
            'primary_results': {},
            'alternative_proposals': [],
            'confidence_scores': {},
            'implementation_risks': [],
            'integration_points': []
        }
        
        for participant, result in results.items():
            weight = weights.get(participant, 1.0)
            ResultSynthesizer._integrate_weighted_result(synthesized, result, weight)
        
        return synthesized
    
    @staticmethod
    def _integrate_weighted_result(synthesized: Dict[str, Any], result: Dict[str, Any], weight: float):
        """Integrate weighted result into synthesis."""
        # Implementation details...

class BaseAgent(Agent, BaseModel):
    """Enhanced base class for all specialized agents."""
    
    name: str = Field(default="Base Agent")
    role: str = Field(default="Generic Agent")
    goal: str = Field(default="Execute assigned tasks")
    backstory: str = Field(default="A versatile agent capable of handling various tasks.")
    config: Dict[str, Any] = Field(default_factory=dict)
    memory: Optional[AgentMemory] = Field(default=None)
    context: Optional[AgentContext] = Field(default=None)
    message_queue: List[AgentMessage] = Field(default_factory=list)
    active_collaborations: Dict[str, CollaborationRequest] = Field(default_factory=dict)
    collaboration_results: Dict[str, List[CollaborationResponse]] = Field(default_factory=dict)
    task_results: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, config: Dict[str, Any]):
        # Initialize BaseModel first
        BaseModel.__init__(self, config=config)
        
        # Initialize Agent with validated fields
        agent_kwargs = {
            'name': self.name,
            'role': self.role,
            'goal': self.goal,
            'backstory': self.backstory
        }
        Agent.__init__(self, **agent_kwargs)
        
        # Initialize other attributes
        self.memory = AgentMemory()
        self.context = AgentContext()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.collaboration_handlers = {
            CollaborationMode.SEQUENTIAL: self._handle_sequential_collaboration,
            CollaborationMode.PARALLEL: self._handle_parallel_collaboration,
            CollaborationMode.ITERATIVE: self._handle_iterative_collaboration,
            CollaborationMode.REVIEW: self._handle_review_collaboration,
            CollaborationMode.CONSENSUS: self._handle_consensus_collaboration
        }
    
    async def initialize(self) -> None:
        """Initialize agent with required setup."""
        try:
            await self.load_memory()
            await self.setup_communication_channels()
            await self.register_capabilities()
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    async def load_memory(self) -> None:
        """Load agent's previous experiences and knowledge."""
        self.experiences = await self.memory.get_agent_experiences(self.agent.role)
        self.knowledge = await self.memory.get_agent_knowledge(self.agent.role)
    
    async def setup_communication_channels(self) -> None:
        """Setup inter-agent communication channels."""
        self.channels = {
            'design': 'design_channel',
            'code': 'code_channel',
            'analysis': 'analysis_channel',
            'ai': 'ai_channel'
        }
    
    async def register_capabilities(self) -> None:
        """Register agent's capabilities for discovery."""
        self.capabilities = {
            'role': self.agent.role,
            'specialties': self.get_specialties(),
            'tools': [tool.__class__.__name__ for tool in self.agent.tools],
            'collaboration_modes': self.get_collaboration_modes()
        }
    
    async def send_message(self, recipient: str, message: AgentMessage) -> None:
        """Send message to another agent."""
        try:
            channel = self.channels.get(recipient)
            if channel:
                await self.context.publish_message(channel, message)
            else:
                logger.warning(f"No channel found for recipient: {recipient}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Handle incoming message from another agent."""
        try:
            self.message_queue.append(message)
            if message.priority == 'high':
                await self.process_urgent_message(message)
            else:
                await self.process_message(message)
        except Exception as e:
            logger.error(f"Error receiving message: {str(e)}")
    
    async def process_message(self, message: AgentMessage) -> None:
        """Process regular message."""
        try:
            # Update context with message content
            self.context.update_from_message(message)
            
            # Generate response if needed
            if message.requires_response:
                response = await self.generate_response(message)
                await self.send_message(message.sender, response)
            
            # Store interaction in memory
            await self.memory.store_interaction(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    async def process_urgent_message(self, message: AgentMessage) -> None:
        """Process high-priority message immediately."""
        try:
            # Pause current task if any
            current_task = self.context.get_current_task()
            if current_task:
                await self.pause_task(current_task)
            
            # Process urgent message
            await self.process_message(message)
            
            # Resume paused task if any
            if current_task:
                await self.resume_task(current_task)
                
        except Exception as e:
            logger.error(f"Error processing urgent message: {str(e)}")
    
    async def collaborate(self, task: Task, collaborators: List[str], 
                        mode: CollaborationMode = CollaborationMode.SEQUENTIAL,
                        **kwargs) -> Dict[str, Any]:
        """Enhanced collaboration with multiple modes."""
        try:
            request = CollaborationRequest(
                task=task,
                mode=mode,
                participants=collaborators,
                deadline=kwargs.get('deadline'),
                requirements=kwargs.get('requirements'),
                review_criteria=kwargs.get('review_criteria')
            )
            
            # Store active collaboration
            request_id = f"{task.id}_{datetime.now().timestamp()}"
            self.active_collaborations[request_id] = request
            
            # Get appropriate handler
            handler = self.collaboration_handlers.get(mode)
            if not handler:
                raise ValueError(f"Unsupported collaboration mode: {mode}")
            
            # Execute collaboration
            result = await handler(request_id, request)
            
            # Process and store results
            await self._process_collaboration_results(request_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in collaboration: {str(e)}")
            raise
    
    async def _handle_sequential_collaboration(self, request_id: str, request: CollaborationRequest) -> Dict[str, Any]:
        """Handle sequential collaboration pattern."""
        try:
            results = []
            current_context = request.task.context
            
            for participant in request.participants:
                # Update task context with previous results
                request.task.context = {
                    **current_context,
                    'previous_results': results
                }
                
                # Execute task using the agent's execute method
                result = await self.execute(request.task)
                results.append({
                    'participant': participant,
                    'result': result
                })
                
                # Update context for next participant
                current_context = request.task.context
            
            return {
                'mode': CollaborationMode.SEQUENTIAL.value,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in sequential collaboration: {str(e)}")
            raise
    
    async def _handle_parallel_collaboration(self, request_id: str, request: CollaborationRequest) -> Dict[str, Any]:
        """Handle parallel collaboration mode."""
        try:
            tasks = []
            for participant in request.participants:
                # Create task copy for each participant
                participant_task = Task(
                    description=request.task.description,
                    agent=self,
                    context=request.task.context
                )
                tasks.append(self.execute(participant_task))
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks)
            
            return {
                'mode': CollaborationMode.PARALLEL.value,
                'results': [
                    {'participant': p, 'result': r}
                    for p, r in zip(request.participants, results)
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in parallel collaboration: {str(e)}")
            raise
    
    async def _handle_iterative_collaboration(self, request_id: str, request: CollaborationRequest) -> Dict[str, Any]:
        """Handle iterative collaboration mode."""
        try:
            iterations = []
            current_result = None
            
            for i in range(3):  # Maximum 3 iterations
                iteration_results = []
                
                for participant in request.participants:
                    # Update task context with previous iteration result
                    request.task.context = {
                        **request.task.context,
                        'previous_iteration': current_result
                    }
                    
                    # Execute task using the agent's execute method
                    result = await self.execute(request.task)
                    iteration_results.append({
                        'participant': participant,
                        'result': result
                    })
                
                # Combine iteration results
                current_result = self._combine_iteration_results(iteration_results)
                iterations.append({
                    'iteration': i + 1,
                    'results': iteration_results,
                    'combined_result': current_result
                })
                
                # Check if convergence is reached
                if self._check_convergence(iterations):
                    break
            
            return {
                'mode': CollaborationMode.ITERATIVE.value,
                'iterations': iterations,
                'final_result': current_result
            }
            
        except Exception as e:
            logger.error(f"Error in iterative collaboration: {str(e)}")
            raise
    
    async def _handle_review_collaboration(self, request_id: str, request: CollaborationRequest) -> Dict[str, Any]:
        """Handle review collaboration mode."""
        try:
            # Execute initial task using the agent's execute method
            initial_result = await self.execute(request.task)
            
            reviews = []
            for reviewer in request.participants:
                # Create review task
                review_task = Task(
                    description=f"Review the following work: {request.task.description}",
                    agent=self,
                    context={
                        **request.task.context,
                        'work_to_review': initial_result,
                        'review_criteria': request.review_criteria
                    }
                )
                
                # Execute review using the agent's execute method
                review_result = await self.execute(review_task)
                reviews.append({
                    'reviewer': reviewer,
                    'review': review_result
                })
            
            # Process reviews and update result
            final_result = await self._process_reviews(initial_result, reviews)
            
            return {
                'mode': CollaborationMode.REVIEW.value,
                'initial_result': initial_result,
                'reviews': reviews,
                'final_result': final_result
            }
            
        except Exception as e:
            logger.error(f"Error in review collaboration: {str(e)}")
            raise
    
    async def _handle_consensus_collaboration(self, request_id: str, request: CollaborationRequest) -> Dict[str, Any]:
        """Handle consensus collaboration mode."""
        try:
            # Get initial proposals
            proposals = []
            for participant in request.participants:
                result = await self.execute(request.task)
                proposals.append({
                    'participant': participant,
                    'proposal': result
                })
            
            # Consensus building rounds
            consensus_rounds = []
            current_proposals = proposals
            
            for round_num in range(3):  # Maximum 3 rounds
                round_results = []
                
                for participant in request.participants:
                    # Create consensus task
                    consensus_task = Task(
                        description="Review proposals and suggest consensus",
                        agent=self,
                        context={
                            **request.task.context,
                            'current_proposals': current_proposals,
                            'round': round_num + 1
                        }
                    )
                    
                    # Execute consensus task using the agent's execute method
                    result = await self.execute(consensus_task)
                    round_results.append({
                        'participant': participant,
                        'result': result
                    })
                
                # Update current proposals
                current_proposals = round_results
                consensus_rounds.append({
                    'round': round_num + 1,
                    'results': round_results
                })
                
                # Check if consensus is reached
                if self._check_consensus(round_results):
                    break
            
            # Generate final consensus
            final_consensus = self._generate_consensus(consensus_rounds)
            
            return {
                'mode': CollaborationMode.CONSENSUS.value,
                'initial_proposals': proposals,
                'consensus_rounds': consensus_rounds,
                'final_consensus': final_consensus
            }
            
        except Exception as e:
            logger.error(f"Error in consensus collaboration: {str(e)}")
            raise
    
    async def _request_collaboration(self, participant: str, 
                                  request: CollaborationRequest) -> CollaborationResponse:
        """Send collaboration request to participant."""
        message = AgentMessage(
            type='collaboration_request',
            content={
                'task': request.task,
                'mode': request.mode.value,
                'requirements': request.requirements,
                'deadline': request.deadline
            },
            sender=self.agent.role,
            priority=MessagePriority.HIGH.value
        )
        
        await self.send_message(participant, message)
        return await self._wait_for_response(participant)
    
    async def _wait_for_response(self, participant: str) -> CollaborationResponse:
        """Wait for response from participant with timeout."""
        timeout = 300  # 5 minutes default timeout
        
        async def check_queue():
            while True:
                for message in self.message_queue:
                    if message.sender == participant and message.type == 'collaboration_response':
                        self.message_queue.remove(message)
                        return CollaborationResponse(
                            request_id=message.content.get('request_id'),
                            participant=participant,
                            status='completed',
                            result=message.content.get('result'),
                            feedback=message.content.get('feedback')
                        )
                await asyncio.sleep(0.1)
        
        try:
            return await asyncio.wait_for(check_queue(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for response from {participant}")
            return CollaborationResponse(
                request_id='timeout',
                participant=participant,
                status='timeout'
            )
    
    def _synthesize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced result synthesis with detailed analysis."""
        try:
            # Calculate participant weights based on expertise and contribution
            weights = self._calculate_participant_weights(results)
            
            # Synthesize results using ResultSynthesizer
            synthesized = ResultSynthesizer.synthesize(results, weights)
            
            # Enhance synthesis with additional analysis
            enhanced = {
                **synthesized,
                'meta_analysis': {
                    'confidence_level': self._calculate_confidence_level(synthesized),
                    'implementation_risks': self._identify_implementation_risks(synthesized),
                    'integration_points': self._identify_integration_points(synthesized),
                    'optimization_opportunities': self._identify_optimizations(synthesized)
                },
                'quality_metrics': {
                    'completeness': self._assess_completeness(synthesized),
                    'consistency': self._assess_consistency(synthesized),
                    'feasibility': self._assess_feasibility(synthesized),
                    'innovation_level': self._assess_innovation(synthesized)
                },
                'recommendations': {
                    'primary': self._generate_primary_recommendations(synthesized),
                    'alternatives': self._generate_alternative_recommendations(synthesized),
                    'implementation': self._generate_implementation_guidelines(synthesized)
                }
            }
            
            # Store synthesis for learning
            self.memory.store_synthesis(enhanced)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in enhanced synthesis: {str(e)}")
            return self._generate_fallback_synthesis(results)
    
    def _calculate_participant_weights(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate weights for participant contributions."""
        weights = {}
        total_score = 0
        
        for participant, result in results.items():
            # Calculate base score
            expertise_score = self._evaluate_expertise(participant)
            contribution_score = self._evaluate_contribution(result)
            historical_score = self._evaluate_historical_performance(participant)
            
            # Combine scores
            participant_score = (
                expertise_score * 0.4 +
                contribution_score * 0.4 +
                historical_score * 0.2
            )
            
            weights[participant] = participant_score
            total_score += participant_score
        
        # Normalize weights
        if total_score > 0:
            return {p: w/total_score for p, w in weights.items()}
        return {p: 1.0/len(results) for p in results}
    
    async def _gather_participant_feedback(self, request: CollaborationRequest, 
                                        current_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather and process participant feedback."""
        feedback_list = []
        
        for participant in request.participants:
            # Request feedback
            feedback = await self._request_feedback(participant, current_result)
            
            # Process feedback
            metrics = await self._process_feedback(feedback)
            
            feedback_list.append({
                'participant': participant,
                'feedback': feedback,
                'metrics': metrics
            })
        
        return feedback_list
    
    def _check_convergence(self, feedback_list: List[Dict[str, Any]], 
                          threshold: float) -> bool:
        """Check if feedback indicates convergence."""
        if not feedback_list:
            return False
        
        # Calculate average agreement level
        agreement_levels = [
            feedback['metrics'].agreement_level 
            for feedback in feedback_list
        ]
        
        avg_agreement = sum(agreement_levels) / len(agreement_levels)
        return avg_agreement >= threshold
    
    async def _process_feedback(self, feedback: Dict[str, Any]) -> FeedbackMetrics:
        """Process and evaluate feedback."""
        try:
            metrics = FeedbackMetrics(
                quality_score=self._evaluate_quality(feedback),
                confidence_score=self._evaluate_confidence(feedback),
                agreement_level=self._evaluate_agreement(feedback),
                impact_score=self._evaluate_impact(feedback),
                implementation_feasibility=self._evaluate_feasibility(feedback)
            )
            
            # Store feedback metrics
            await self.memory.store_feedback_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return FeedbackMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
    
    async def _resolve_conflict(self, conflict: Dict[str, Any]) -> ConflictResolution:
        """Resolve conflicts between participants."""
        try:
            # Identify conflict type
            conflict_type = self._identify_conflict_type(conflict)
            
            # Choose resolution strategy
            strategy = self._select_resolution_strategy(conflict_type, conflict)
            
            # Apply resolution strategy
            resolution = await self._apply_resolution_strategy(strategy, conflict)
            
            # Validate resolution
            if not self._validate_resolution(resolution):
                resolution = await self._apply_fallback_resolution(conflict)
            
            return ConflictResolution(
                conflict_type=conflict_type,
                participants=conflict['participants'],
                proposals=conflict['proposals'],
                resolution_strategy=strategy,
                resolution_result=resolution,
                consensus_level=self._calculate_consensus_level(resolution)
            )
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            return self._generate_fallback_resolution(conflict)
    
    def get_specialties(self) -> List[str]:
        """Get agent's specialized capabilities."""
        raise NotImplementedError("Subclasses must implement get_specialties")
    
    def get_collaboration_modes(self) -> List[str]:
        """Get agent's supported collaboration modes."""
        raise NotImplementedError("Subclasses must implement get_collaboration_modes")
    
    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a task and store its results."""
        try:
            # Execute the task
            result = await self._execute_task(task)
            
            # Store the result
            task_id = str(uuid.uuid4())
            self.task_results[task_id] = {
                'task': task,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            # Store in memory for persistence
            self.memory[task_id] = {
                'type': 'task_result',
                'data': result,
                'metadata': {
                    'task_id': task_id,
                    'timestamp': datetime.now().isoformat(),
                    'task_type': task.__class__.__name__
                }
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            raise

    async def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Internal method to execute a task."""
        try:
            # Get the appropriate tool for the task
            tool = self._get_tool_for_task(task)
            
            # Execute the task using the tool
            result = await tool._run(**task.context)
            
            return result
        except Exception as e:
            self.logger.error(f"Error in _execute_task: {str(e)}")
            raise

    def _get_tool_for_task(self, task: Task) -> Any:
        """Get the appropriate tool for a task."""
        # This should be implemented by child classes
        raise NotImplementedError

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task result by ID."""
        return self.task_results.get(task_id)

    def get_all_task_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored task results."""
        return self.task_results
 