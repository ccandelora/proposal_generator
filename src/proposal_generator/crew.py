from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .config import create_agent, configure_crew, get_gemini_llm
from langchain.tools import Tool, tool
from pydantic import BaseModel, Field
from typing import List, Optional
import yaml
import os

class WebSearchArgs(BaseModel):
    """Arguments for web search tool."""
    query: str = Field(description="The search query to find relevant information")
    model_config = {
        "json_schema_extra": {
            "examples": [{"query": "latest web development trends 2024"}]
        }
    }

class SEOAnalyzerArgs(BaseModel):
    """Arguments for SEO analyzer tool."""
    url: str = Field(description="The URL to analyze for SEO")
    model_config = {
        "json_schema_extra": {
            "examples": [{"url": "https://example.com"}]
        }
    }

class DocumentWriterArgs(BaseModel):
    """Arguments for document writer tool."""
    content: str = Field(description="The content to write to the document")
    format: str = Field(description="The format of the document (markdown, html, etc.)")
    model_config = {
        "json_schema_extra": {
            "examples": [{"content": "# Example Document", "format": "markdown"}]
        }
    }

class MockupGeneratorArgs(BaseModel):
    """Arguments for mockup generator tool."""
    requirements: List[str] = Field(description="List of design requirements")
    device_type: str = Field(description="Type of device (desktop, mobile)")
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "requirements": ["responsive", "modern design"],
                "device_type": "desktop"
            }]
        }
    }

@CrewBase
class ProposalGenerator():
    """ProposalGenerator crew"""

    def __init__(self):
        """Initialize the crew with configuration files."""
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
        
        # Set default LLM
        self.default_llm = get_gemini_llm()
        
        # Initialize tools
        self.tools = self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all tools with proper schemas."""
        @tool
        def web_search(query: str) -> str:
            """Search the web for information."""
            # Implementation
            return f"Search results for: {query}"

        @tool
        def seo_analyzer(url: str) -> str:
            """Analyze a URL for SEO metrics."""
            # Implementation
            return f"SEO analysis for: {url}"

        @tool
        def document_writer(content: str, format: str = "markdown") -> str:
            """Write content to a document."""
            # Implementation
            return f"Document written in {format} format"

        @tool
        def mockup_generator(requirements: List[str], device_type: str) -> str:
            """Generate website mockups."""
            # Implementation
            return f"Generated mockup for {device_type}"

        return {
            "web_search": Tool.from_function(
                func=web_search,
                name="web_search",
                description="Search the web for information",
                args_schema=WebSearchArgs
            ),
            "seo_analyzer": Tool.from_function(
                func=seo_analyzer,
                name="seo_analyzer",
                description="Analyze a URL for SEO metrics",
                args_schema=SEOAnalyzerArgs
            ),
            "document_writer": Tool.from_function(
                func=document_writer,
                name="document_writer",
                description="Write content to a document",
                args_schema=DocumentWriterArgs
            ),
            "mockup_generator": Tool.from_function(
                func=mockup_generator,
                name="mockup_generator",
                description="Generate website mockups",
                args_schema=MockupGeneratorArgs
            )
        }

    @agent
    def researcher(self) -> Agent:
        """Create the researcher agent with Gemini."""
        return create_agent(self.agents_config['researcher'])

    @agent
    def reporting_analyst(self) -> Agent:
        """Create the reporting analyst agent with Gemini."""
        return create_agent(self.agents_config['reporting_analyst'])

    @agent
    def mockup_designer(self) -> Agent:
        """Create the mockup designer agent with Gemini."""
        return create_agent(self.agents_config['mockup_designer'])

    @task
    def research_task(self) -> Task:
        return Task(
            description=self.tasks_config['research_task']['description'],
            expected_output=self.tasks_config['research_task']['expected_output'],
            tools=[self.tools["web_search"], self.tools["seo_analyzer"]],
            llm=self.default_llm
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            description=self.tasks_config['reporting_task']['description'],
            expected_output=self.tasks_config['reporting_task']['expected_output'],
            tools=[self.tools["document_writer"]],
            output_file='report.md',
            llm=self.default_llm
        )

    @task
    def mockup_generation_task(self) -> Task:
        return Task(
            description=self.tasks_config['mockup_generation_task']['description'],
            expected_output=self.tasks_config['mockup_generation_task']['expected_output'],
            tools=[self.tools["mockup_generator"]],
            output_file='mockups.json',
            llm=self.default_llm
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProposalGenerator crew"""
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Configure crew to use Gemini
        return configure_crew(crew)
