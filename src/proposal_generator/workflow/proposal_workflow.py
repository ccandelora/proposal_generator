"""Proposal generation workflow."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from functools import partial
import logging
import os
import json
from pathlib import Path
from pydantic import BaseModel
import uuid
from abc import ABC, abstractmethod

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

from ..knowledge.knowledge_source import StringKnowledgeSource
from ..config.workflow_config import WorkflowConfig
from .workflow_models import ProposalOutput, ResearchResult, TechnicalAnalysis, ProposalMetrics
from .knowledge_validator import KnowledgeValidator
from .agents.manager_agent import ManagerAgent
from .progress_monitor import ProgressMonitor
from .agent_memory import AgentMemory
from .agents import (
    DesignAgent,
    CodingAgent,
    CompetitorAnalysisAgent,
    AIOrchestrationAgent
)

from ..tools.specialized_tools import (
    SEOAnalysisTool,
    UXAnalysisTool,
    CompetitorAnalysisTool,
    SecurityAssessmentTool,
    PerformanceOptimizationTool
)

from ..tools.design_tools import (
    MockupGeneratorTool,
    AssetGeneratorTool
)

from ..tools.coding_tools import (
    CodeGeneratorTool,
    TechnologyStackAnalyzerTool
)

from ..tools.ai_tools import (
    MLModelSelectionTool,
    AIIntegrationTool,
    OptimizationTool
)

logger = logging.getLogger(__name__)

class ProposalWorkflowManager:
    """Manages the proposal generation workflow."""
    
    def __init__(self, config: WorkflowConfig):
        """Initialize the workflow manager."""
        try:
            self.config = config
            self.logger = logging.getLogger(__name__)
            self.progress_monitor = ProgressMonitor()
            self.agent_memory = AgentMemory()
            self.phase_results = {}
            self.aggregated_results = {}
            
            # Initialize phases with consistent naming
            self.phases = [
                "Research & Analysis",
                "Design & Planning",
                "Development & Implementation",
                "AI Integration",
                "Review & Optimization"
            ]
            
            # Initialize phase status
            self.phase_status = {
                phase: {
                    'status': 'pending',
                    'progress': 0,
                    'tasks': []
                }
                for phase in self.phases
            }
            
            # Initialize knowledge sources
            self.setup_knowledge_sources()
            
            # Initialize industry-specific pricing
            self.setup_industry_pricing_knowledge()
            
            # Initialize agents
            self.setup_agents()
            
            # Initialize task tracking
            self.tasks = []
            self.completed_tasks = set()
            self.task_results = {}
            
        except Exception as e:
            logger.error(f"Error initializing workflow manager: {e}")
            raise
            
    def setup_knowledge_sources(self):
        """Setup comprehensive knowledge sources for the agents."""
        
        self.tech_stack_knowledge = StringKnowledgeSource(
            content="""
            Modern Web Technology Stacks 2024:

            1. Frontend Technologies:
            - React 18+ with Server Components
            - Next.js 14+ for SSR/SSG
            - TypeScript for type safety
            - Tailwind CSS for styling
            - Redux Toolkit for state management
            - React Query for data fetching
            - Testing: Jest, React Testing Library
            
            2. Backend Technologies:
            - Python FastAPI/Django
            - Node.js with Express/NestJS
            - GraphQL with Apollo
            - PostgreSQL/MongoDB
            - Redis for caching
            - Elasticsearch for search
            - RabbitMQ/Redis for queues
            
            3. DevOps & Infrastructure:
            - Docker containerization
            - Kubernetes orchestration
            - AWS/GCP/Azure cloud services
            - GitHub Actions/GitLab CI
            - Terraform for IaC
            - ELK stack for logging
            - Prometheus/Grafana monitoring
            """,
            metadata={"category": "technology", "year": "2024"}
        )

        self.industry_knowledge = StringKnowledgeSource(
            content="""
            Industry Best Practices 2024:

            1. E-commerce:
            - Seamless checkout process
            - Product recommendation engines
            - Inventory management systems
            - Multi-currency support
            - Mobile-first shopping experience
            - Secure payment gateways
            - Order tracking systems

            2. Healthcare:
            - HIPAA compliance
            - Patient portal integration
            - Electronic health records
            - Telemedicine capabilities
            - Appointment scheduling
            - Medical billing integration
            - Secure messaging systems

            3. Finance:
            - Banking regulations compliance
            - Real-time transaction processing
            - Multi-factor authentication
            - Fraud detection systems
            - Investment portfolio tracking
            - Financial reporting tools
            - API banking integration
            """,
            metadata={"category": "industry", "year": "2024"}
        )

        self.pricing_knowledge = StringKnowledgeSource(
            content="""
            Web Development Pricing Guidelines 2024:

            1. Basic Website Development:
            - Landing Page: $2,000-$5,000
            - Multi-page Site: $5,000-$15,000
            - Corporate Site: $15,000-$40,000
            - E-commerce Basic: $10,000-$25,000
            - E-commerce Advanced: $25,000-$100,000+

            2. Feature-based Pricing:
            - Custom CMS: $5,000-$15,000
            - E-commerce Integration: $3,000-$10,000
            - Payment Gateway: $1,000-$3,000
            - User Authentication: $2,000-$5,000
            - Search Functionality: $1,500-$4,000
            - API Integration: $2,000-$6,000 per API
            - Custom Database: $3,000-$10,000
            """,
            metadata={"category": "pricing", "year": "2024"}
        )

        self.security_knowledge = StringKnowledgeSource(
            content="""
            Web Security Standards 2024:

            1. Authentication & Authorization:
            - OAuth 2.0 with PKCE
            - JWT with short expiration
            - Multi-factor authentication
            - Role-based access control
            - Session management best practices
            
            2. Data Protection:
            - End-to-end encryption
            - At-rest encryption (AES-256)
            - TLS 1.3 for transit
            - Regular security audits
            - Automated vulnerability scanning
            
            3. Compliance Requirements:
            - GDPR compliance
            - CCPA requirements
            - PCI DSS for e-commerce
            - HIPAA for healthcare
            - SOC 2 certification process
            """,
            metadata={"category": "security", "year": "2024"}
        )

        self.ux_design_knowledge = StringKnowledgeSource(
            content="""
            UX Design Best Practices 2024:

            1. Design Principles:
            - Mobile-first approach
            - Accessibility (WCAG 2.1)
            - Minimalist interfaces
            - Consistent navigation
            - Clear visual hierarchy
            
            2. User Interaction:
            - Micro-interactions
            - Gesture controls
            - Voice interfaces
            - Dark mode support
            - Responsive breakpoints
            
            3. Performance Metrics:
            - Core Web Vitals
            - First Contentful Paint
            - Time to Interactive
            - Cumulative Layout Shift
            - First Input Delay
            """,
            metadata={"category": "design", "year": "2024"}
        )

        self.seo_knowledge = StringKnowledgeSource(
            content="""
            SEO Optimization Strategies 2024:

            1. Technical SEO:
            - Schema markup implementation
            - XML sitemap structure
            - Robots.txt configuration
            - Canonical URL usage
            - Mobile optimization
            
            2. Content Strategy:
            - Keyword research methods
            - Content clustering
            - Topic authority building
            - Meta tag optimization
            - Internal linking structure
            
            3. Performance SEO:
            - Core Web Vitals optimization
            - Mobile-first indexing
            - Page speed optimization
            - Image optimization
            - Lazy loading implementation
            """,
            metadata={"category": "seo", "year": "2024"}
        )

        self.market_trends_knowledge = StringKnowledgeSource(
            content="""
            Web Development Market Trends 2024:

            1. Emerging Technologies:
            - AI/ML integration
            - WebAssembly adoption
            - Edge computing
            - Serverless architecture
            - Web3 integration
            
            2. User Experience Trends:
            - Voice interfaces
            - AR/VR experiences
            - Progressive Web Apps
            - Micro-frontends
            - Headless CMS
            
            3. Development Practices:
            - JAMstack architecture
            - Zero-trust security
            - Green hosting
            - API-first development
            - Low-code integration
            """,
            metadata={"category": "trends", "year": "2024"}
        )

        self.roi_metrics_knowledge = StringKnowledgeSource(
            content="""
            ROI and Performance Metrics 2024:

            1. Business Metrics:
            - Conversion rate benchmarks
            - Customer acquisition cost
            - Customer lifetime value
            - Return on ad spend
            - Market penetration rates
            
            2. Technical Metrics:
            - Server response time
            - Error rate thresholds
            - Uptime guarantees
            - Resource utilization
            - Scalability metrics
            
            3. User Engagement:
            - Session duration
            - Bounce rate standards
            - Page views per session
            - User retention rates
            - Mobile engagement metrics
            """,
            metadata={"category": "metrics", "year": "2024"}
        )

        # Update the crew configuration to use all knowledge sources
        self.knowledge_sources = [
            self.industry_knowledge,
            self.pricing_knowledge,
            self.tech_stack_knowledge,
            self.security_knowledge,
            self.ux_design_knowledge,
            self.seo_knowledge,
            self.market_trends_knowledge,
            self.roi_metrics_knowledge
        ]
        
    def setup_industry_pricing_knowledge(self):
        """Setup industry-specific pricing guidelines."""
        self.industry_pricing = {
            'retail': StringKnowledgeSource(
                content="""
                Retail E-commerce Pricing Guidelines 2024:
                
                Base Implementation:
                - Small Store (up to 500 products): $8,000-$15,000
                - Medium Store (up to 5000 products): $15,000-$30,000
                - Large Store (5000+ products): $30,000-$75,000
                
                Feature Costs:
                - Product Import/Sync: $2,000-$4,000
                - Inventory Management: $3,000-$6,000
                - Multi-channel Integration: $4,000-$8,000
                - Custom Product Filters: $2,500-$5,000
                - Wishlist/Favorites: $1,500-$3,000
                
                Timeline Factors:
                - Basic Setup: 6-8 weeks
                - Full Featured: 12-16 weeks
                - Enterprise: 16-24 weeks
                """,
                metadata={"category": "pricing", "industry": "retail", "year": "2024"}
            ),
            
            'restaurant': StringKnowledgeSource(
                content="""
                Restaurant Website Pricing Guidelines 2024:
                
                Base Implementation:
                - Basic Menu Site: $5,000-$10,000
                - Full-Featured Site: $10,000-$20,000
                - Enterprise Solution: $20,000-$40,000
                
                Feature Costs:
                - Online Ordering: $3,000-$6,000
                - Reservation System: $2,000-$4,000
                - Menu Management: $1,500-$3,000
                - Kitchen Integration: $4,000-$8,000
                - Delivery Integration: $2,500-$5,000
                
                Timeline Factors:
                - Basic Setup: 4-6 weeks
                - Full Featured: 8-12 weeks
                - Enterprise: 12-16 weeks
                """,
                metadata={"category": "pricing", "industry": "restaurant", "year": "2024"}
            ),
            
            'professional_services': StringKnowledgeSource(
                content="""
                Professional Services Pricing Guidelines 2024:
                
                Base Implementation:
                - Basic Presence: $6,000-$12,000
                - Full Service Site: $12,000-$25,000
                - Enterprise Portal: $25,000-$50,000
                
                Feature Costs:
                - Appointment Scheduling: $2,000-$4,000
                - Client Portal: $4,000-$8,000
                - Document Management: $3,000-$6,000
                - Video Consultation: $3,500-$7,000
                - CRM Integration: $2,500-$5,000
                
                Timeline Factors:
                - Basic Setup: 5-7 weeks
                - Full Featured: 10-14 weeks
                - Enterprise: 14-20 weeks
                """,
                metadata={"category": "pricing", "industry": "professional_services", "year": "2024"}
            )
        }

    def setup_agents(self):
        """Set up all agents needed for the workflow."""
        try:
            # Get embeddings for knowledge sources
            embeddings = self.config.get_embeddings()
            
            # Initialize knowledge sources with proper names
            self.knowledge_sources = {
                'competitor_data': StringKnowledgeSource(
                    name='competitor_data',
                    content='',
                    metadata={'category': 'competitor_analysis'},
                    embeddings=embeddings
                ),
                'market_research': StringKnowledgeSource(
                    name='market_research',
                    content='',
                    metadata={'category': 'market_analysis'},
                    embeddings=embeddings
                ),
                'technical_specs': StringKnowledgeSource(
                    name='technical_specs',
                    content='',
                    metadata={'category': 'technical_analysis'},
                    embeddings=embeddings
                )
            }
            
            # Convert knowledge sources dictionary to list for agent initialization
            knowledge_sources_list = list(self.knowledge_sources.values())
            
            # Initialize agents with knowledge sources and embeddings
            self.design_agent = DesignAgent(
                name="Design Agent",
                knowledge_sources=knowledge_sources_list,
                embeddings=embeddings
            )
            
            self.coding_agent = CodingAgent(
                name="Coding Agent",
                knowledge_sources=knowledge_sources_list,
                embeddings=embeddings
            )
            
            self.competitor_agent = CompetitorAnalysisAgent(
                name="Competitor Analysis Agent",
                knowledge_sources=knowledge_sources_list,
                embeddings=embeddings
            )
            
            self.ai_agent = AIOrchestrationAgent(
                name="AI Orchestration Agent",
                knowledge_sources=knowledge_sources_list,
                embeddings=embeddings
            )
            
            # Update crew configuration
            self.agents = [
                self.design_agent,
                self.coding_agent,
                self.competitor_agent,
                self.ai_agent
            ]
            
            logger.info("Successfully set up all agents")
            
        except Exception as e:
            logger.error(f"Error setting up agents: {str(e)}")
            raise