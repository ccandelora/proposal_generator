from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
import logging
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pydantic import Field, ConfigDict

logger = logging.getLogger(__name__)

class TaskDelegationTool(BaseTool):
    """Tool for delegating and managing tasks."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm: Optional[ChatGoogleGenerativeAI] = Field(default=None)
    
    def __init__(self):
        super().__init__(
            name="Task Delegator",
            description="Delegates and manages project tasks"
        )
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
                
            genai.configure(api_key=api_key)
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.7,
                google_api_key=api_key
            )
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            return None
    
    async def _run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate and manage tasks."""
        try:
            # Analyze task requirements
            task_analysis = await self._analyze_task_requirements(task_data)
            
            # Generate task assignments
            assignments = await self._generate_task_assignments(task_analysis)
            
            # Create timeline
            timeline = await self._create_task_timeline(assignments)
            
            # Generate coordination plan
            coordination = await self._generate_coordination_plan(assignments, timeline)
            
            return {
                'task_analysis': task_analysis,
                'assignments': assignments,
                'timeline': timeline,
                'coordination_plan': coordination,
                'dependencies': await self._identify_dependencies(assignments),
                'resource_allocation': await self._allocate_resources(assignments)
            }
        except Exception as e:
            logger.error(f"Error in task delegation: {str(e)}")
            return {}
    
    async def _analyze_task_requirements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task requirements and constraints."""
        try:
            prompt = f"""Analyze these task requirements:
            Task Description: {task_data.get('description', '')}
            Objectives: {task_data.get('objectives', [])}
            Constraints: {task_data.get('constraints', [])}
            Resources: {task_data.get('available_resources', [])}
            
            Provide detailed analysis of:
            1. Core requirements
            2. Critical dependencies
            3. Resource needs
            4. Risk factors
            5. Success criteria"""
            
            response = await self.llm.apredict(prompt)
            return {'analysis': response}
        except Exception as e:
            logger.error(f"Error analyzing task requirements: {str(e)}")
            return {}
    
    async def _generate_task_assignments(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate task assignments based on analysis."""
        try:
            prompt = f"""Based on this analysis: {analysis.get('analysis', '')},
            generate task assignments including:
            1. Task owner and responsibilities
            2. Required skills and expertise
            3. Expected deliverables
            4. Time estimates
            5. Quality criteria
            
            Format as structured task assignments."""
            
            response = await self.llm.apredict(prompt)
            return [{'task': t.strip()} for t in response.split('\n') if t.strip()]
        except Exception as e:
            logger.error(f"Error generating task assignments: {str(e)}")
            return []
    
    async def _create_task_timeline(self, assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create timeline for task execution."""
        try:
            prompt = f"""Create a timeline for these tasks:
            {assignments}
            
            Include:
            1. Start and end dates
            2. Milestones
            3. Dependencies
            4. Critical path
            5. Buffer periods
            
            Format as a structured timeline."""
            
            response = await self.llm.apredict(prompt)
            return {'timeline': response}
        except Exception as e:
            logger.error(f"Error creating task timeline: {str(e)}")
            return {}
    
    async def _generate_coordination_plan(self, assignments: List[Dict[str, Any]], timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plan for task coordination."""
        try:
            prompt = f"""Create a coordination plan for:
            Tasks: {assignments}
            Timeline: {timeline.get('timeline', '')}
            
            Include:
            1. Communication protocols
            2. Progress tracking
            3. Issue resolution
            4. Change management
            5. Status reporting
            
            Format as a structured coordination plan."""
            
            response = await self.llm.apredict(prompt)
            return {'coordination_plan': response}
        except Exception as e:
            logger.error(f"Error generating coordination plan: {str(e)}")
            return {}
    
    async def _identify_dependencies(self, assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify dependencies between tasks."""
        try:
            prompt = f"""Identify dependencies between these tasks:
            {assignments}
            
            For each dependency identify:
            1. Predecessor task
            2. Successor task
            3. Dependency type
            4. Impact level
            5. Risk factors
            
            Format as a structured dependency list."""
            
            response = await self.llm.apredict(prompt)
            return [{'dependency': d.strip()} for d in response.split('\n') if d.strip()]
        except Exception as e:
            logger.error(f"Error identifying dependencies: {str(e)}")
            return []
    
    async def _allocate_resources(self, assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Allocate resources to tasks."""
        try:
            prompt = f"""Allocate resources for these tasks:
            {assignments}
            
            For each task specify:
            1. Required personnel
            2. Equipment needs
            3. Budget allocation
            4. Time resources
            5. Support requirements
            
            Format as a structured resource allocation plan."""
            
            response = await self.llm.apredict(prompt)
            return {'resource_allocation': response}
        except Exception as e:
            logger.error(f"Error allocating resources: {str(e)}")
            return {}

class QualityAssuranceTool(BaseTool):
    """Tool for quality assurance and testing."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm: Optional[ChatGoogleGenerativeAI] = Field(default=None)
    
    def __init__(self):
        super().__init__(
            name="Quality Assurance",
            description="Ensures quality and performs testing"
        )
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
                
            genai.configure(api_key=api_key)
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.7,
                google_api_key=api_key
            )
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            return None
    
    async def _run(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality assurance and testing."""
        try:
            # Generate test plan
            test_plan = await self._generate_test_plan(project_data)
            
            # Define quality criteria
            quality_criteria = await self._define_quality_criteria(project_data)
            
            # Perform quality checks
            quality_checks = await self._perform_quality_checks(project_data, quality_criteria)
            
            # Generate test results
            test_results = await self._generate_test_results(test_plan, quality_checks)
            
            return {
                'test_plan': test_plan,
                'quality_criteria': quality_criteria,
                'quality_checks': quality_checks,
                'test_results': test_results,
                'recommendations': await self._generate_recommendations(test_results),
                'compliance_report': await self._generate_compliance_report(test_results)
            }
        except Exception as e:
            logger.error(f"Error in quality assurance: {str(e)}")
            return {}
    
    async def _generate_test_plan(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test plan."""
        try:
            prompt = f"""Generate a test plan for:
            Project Type: {project_data.get('type', '')}
            Requirements: {project_data.get('requirements', [])}
            Constraints: {project_data.get('constraints', [])}
            
            Include:
            1. Test objectives
            2. Test scope
            3. Test methodology
            4. Test scenarios
            5. Test schedule
            
            Format as a structured test plan."""
            
            response = await self.llm.apredict(prompt)
            return {'test_plan': response}
        except Exception as e:
            logger.error(f"Error generating test plan: {str(e)}")
            return {}
    
    async def _define_quality_criteria(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define quality criteria and standards."""
        try:
            prompt = f"""Define quality criteria for:
            Project Requirements: {project_data.get('requirements', [])}
            Industry Standards: {project_data.get('standards', [])}
            Best Practices: {project_data.get('best_practices', [])}
            
            Include criteria for:
            1. Functionality
            2. Performance
            3. Reliability
            4. Usability
            5. Security
            
            Format as specific, measurable criteria."""
            
            response = await self.llm.apredict(prompt)
            return [{'criterion': c.strip()} for c in response.split('\n') if c.strip()]
        except Exception as e:
            logger.error(f"Error defining quality criteria: {str(e)}")
            return []
    
    async def _perform_quality_checks(self, project_data: Dict[str, Any], criteria: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform quality checks against defined criteria."""
        try:
            prompt = f"""Perform quality checks for:
            Project Data: {project_data}
            Quality Criteria: {criteria}
            
            For each criterion:
            1. Evaluate compliance
            2. Identify issues
            3. Measure performance
            4. Document findings
            5. Suggest improvements
            
            Format as detailed check results."""
            
            response = await self.llm.apredict(prompt)
            return [{'check': c.strip()} for c in response.split('\n') if c.strip()]
        except Exception as e:
            logger.error(f"Error performing quality checks: {str(e)}")
            return []
    
    async def _generate_test_results(self, test_plan: Dict[str, Any], quality_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive test results."""
        try:
            prompt = f"""Generate test results for:
            Test Plan: {test_plan.get('test_plan', '')}
            Quality Checks: {quality_checks}
            
            Include:
            1. Test execution summary
            2. Pass/fail status
            3. Issues found
            4. Performance metrics
            5. Coverage analysis
            
            Format as a detailed test report."""
            
            response = await self.llm.apredict(prompt)
            return {'test_results': response}
        except Exception as e:
            logger.error(f"Error generating test results: {str(e)}")
            return {}
    
    async def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on test results."""
        try:
            prompt = f"""Based on these test results:
            {test_results.get('test_results', '')}
            
            Generate recommendations for:
            1. Quality improvements
            2. Process enhancements
            3. Risk mitigation
            4. Performance optimization
            5. Best practices adoption
            
            Format as actionable recommendations."""
            
            response = await self.llm.apredict(prompt)
            return [{'recommendation': r.strip()} for r in response.split('\n') if r.strip()]
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def _generate_compliance_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report based on test results."""
        try:
            prompt = f"""Generate a compliance report based on:
            Test Results: {test_results.get('test_results', '')}
            
            Include:
            1. Compliance status
            2. Standard adherence
            3. Regulatory alignment
            4. Policy compliance
            5. Required actions
            
            Format as a formal compliance report."""
            
            response = await self.llm.apredict(prompt)
            return {'compliance_report': response}
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            return {} 