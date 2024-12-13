"""Configuration for the proposal generation workflow."""
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field, ConfigDict
import os
import logging
import google.generativeai as genai
from googleapiclient.discovery import build
import requests
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pathlib import Path
from newsapi import NewsApiClient
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .litellm_config import setup_litellm

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LiteLLM
litellm_router = setup_litellm()

class APIKeyValidator:
    """Validates API keys and provides status information."""
    
    @staticmethod
    def validate_gemini_key(api_key: str) -> bool:
        """Validate Gemini API key."""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Test")
            return True
        except Exception as e:
            logger.error(f"Gemini API key validation failed: {str(e)}")
            return False
            
    @staticmethod
    def validate_google_search(api_key: str, cx: str) -> bool:
        """Validate Google Custom Search setup."""
        try:
            service = build('customsearch', 'v1', developerKey=api_key)
            result = service.cse().list(q='test', cx=cx, num=1).execute()
            return 'items' in result
        except Exception as e:
            if 'Quota exceeded' in str(e):
                logger.warning("Google Search API daily quota exceeded, but API key is valid")
                return True  # Consider the API key valid even if quota is exceeded
            logger.error(f"Google Search API validation failed: {str(e)}")
            return False
            
    @staticmethod
    def validate_news_api(api_key: str) -> bool:
        """Validate News API key."""
        try:
            url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
            response = requests.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"News API validation failed: {str(e)}")
            return False

def validate_api_keys() -> Dict[str, bool]:
    """Validate all API keys and return their status."""
    validator = APIKeyValidator()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    google_search_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    google_cx = os.getenv('GOOGLE_CUSTOM_SEARCH_ID')
    news_api_key = os.getenv('NEWS_API_KEY')
    
    status = {
        'gemini': validator.validate_gemini_key(gemini_key) if gemini_key else False,
        'google_search': validator.validate_google_search(google_search_key, google_cx) 
                        if google_search_key and google_cx else False,
        'news_api': validator.validate_news_api(news_api_key) if news_api_key else False
    }
    
    # Log validation results
    for api, is_valid in status.items():
        if is_valid:
            logger.info(f"{api} API key is valid and working")
        else:
            logger.warning(f"{api} API key is invalid or missing")
    
    return status

def get_api_config() -> Dict[str, Any]:
    """Get API configuration with validated keys."""
    return {
        'gemini': {
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': os.getenv('GEMINI_MODEL', 'gemini-pro')
        },
        'google_search': {
            'api_key': os.getenv('GOOGLE_SEARCH_API_KEY'),
            'cx': os.getenv('GOOGLE_CUSTOM_SEARCH_ID')
        },
        'news_api': {
            'api_key': os.getenv('NEWS_API_KEY')
        },
        'serper': {
            'api_key': os.getenv('SERPER_API_KEY')
        }
    }

def initialize_apis() -> None:
    """Initialize API clients with validated configurations."""
    config = get_api_config()
    
    # Initialize Gemini
    if config['gemini']['api_key']:
        genai.configure(api_key=config['gemini']['api_key'])
        
    # Log initialization status
    logger.info("API initialization completed")

class WorkflowConfig(BaseModel):
    """Configuration for the proposal generation workflow."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow',
        validate_assignment=True
    )
    
    # General settings
    verbose: bool = Field(default=True, description="Enable verbose logging")
    debug: bool = Field(default=False, description="Enable debug mode")
    output_dir: Path = Field(default=Path("output"), description="Output directory for generated files")
    cache_results: bool = Field(default=True, description="Enable result caching")
    cache_dir: Path = Field(default=Path("cache"), description="Directory for cached results")
    
    # API settings
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    google_search_api_key: Optional[str] = Field(default=None, description="Google Search API key")
    google_custom_search_id: Optional[str] = Field(default=None, description="Google Custom Search ID")
    
    # Project settings
    project_name: str = Field(default="", description="Name of the project")
    project_type: str = Field(default="web", description="Type of project (web, mobile, etc.)")
    project_requirements: List[str] = Field(default_factory=list, description="List of project requirements")
    
    # Workflow settings
    max_retries: int = Field(default=3, description="Maximum number of retries for failed tasks")
    timeout_seconds: int = Field(default=300, description="Timeout in seconds for each task")
    parallel_execution: bool = Field(default=True, description="Enable parallel task execution")
    
    # Agent settings
    agent_memory_size: int = Field(default=1000, description="Size of agent memory in tokens")
    agent_temperature: float = Field(default=0.7, description="Temperature for agent LLM responses")
    
    # Knowledge storage settings
    embeddings_instance: Optional[GoogleGenerativeAIEmbeddings] = Field(default=None, exclude=True)
    
    # Tool settings
    enabled_tools: List[str] = Field(
        default_factory=lambda: [
            "TaskDelegationTool",
            "QualityAssuranceTool",
            "CodeGeneratorTool",
            "CodeOptimizerTool",
            "AIRecommendationTool",
            "PredictiveAnalyticsTool",
            "SEOAnalysisTool",
            "UXAnalysisTool",
            "CompetitorAnalysisTool",
            "CostEstimationTool",
            "SecurityAssessmentTool",
            "PerformanceOptimizationTool",
            "ContentStrategyTool"
        ],
        description="List of enabled tools"
    )
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration settings")
    
    # API instances
    gemini: Optional[ChatGoogleGenerativeAI] = Field(default=None, exclude=True)
    google_search: Optional[Any] = Field(default=None, exclude=True)
    news_api: Optional[NewsApiClient] = Field(default=None, exclude=True)

    def __init__(self, **kwargs):
        """Initialize the workflow configuration."""
        # Ensure environment variables are loaded
        load_dotenv()
        
        # Get API keys from environment
        api_keys = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'google_search_api_key': os.getenv('GOOGLE_SEARCH_API_KEY'),
            'google_custom_search_id': os.getenv('GOOGLE_CUSTOM_SEARCH_ID')
        }
        
        # Update kwargs with API keys
        kwargs.update(api_keys)
        
        # Initialize parent class first
        super().__init__(**kwargs)
        
        # Initialize APIs after parent class is initialized
        self.initialize_apis()
        
    def initialize_apis(self) -> None:
        """Initialize API clients."""
        try:
            # Initialize Gemini
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
                
            genai.configure(api_key=self.gemini_api_key)
            self.gemini = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.7,
                max_output_tokens=4096,
                convert_system_message_to_human=True,
                google_api_key=self.gemini_api_key  # Pass API key directly
            )
            
            # Test Gemini
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Test connection")
            if response:
                logger.info("gemini API key is valid and working")
            
            # Initialize Google Search
            if self.google_search_api_key and self.google_custom_search_id:
                try:
                    self.google_search = build(
                        "customsearch", "v1", 
                        developerKey=self.google_search_api_key
                    )
                    # Test Google Search
                    search_response = self.google_search.cse().list(
                        q="test",
                        cx=self.google_custom_search_id
                    ).execute()
                    if search_response:
                        logger.info("google_search API key is valid and working")
                except Exception as e:
                    logger.warning(f"Google Search initialization failed: {str(e)}")
                    self.google_search = None
            else:
                logger.warning("Google Search API keys not found, skipping initialization")
                self.google_search = None
            
            # Initialize News API if key is available
            news_api_key = os.getenv('NEWS_API_KEY')
            if news_api_key:
                try:
                    self.news_api = NewsApiClient(api_key=news_api_key)
                    # Test News API
                    news_response = self.news_api.get_everything(q="test", page_size=1)
                    if news_response:
                        logger.info("news_api API key is valid and working")
                except Exception as e:
                    logger.warning(f"News API initialization failed: {str(e)}")
                    self.news_api = None
            else:
                logger.warning("NEWS_API_KEY not found, skipping News API initialization")
                self.news_api = None
            
            logger.info("API initialization completed")
            
        except Exception as e:
            logger.error(f"Error initializing APIs: {str(e)}")
            raise
    
    def get_gemini_llm(self) -> ChatGoogleGenerativeAI:
        """Get the Gemini LLM instance."""
        return self.gemini

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Get or initialize the embedding model for knowledge storage."""
        if not self.embeddings_instance:
            try:
                self.embeddings_instance = GoogleGenerativeAIEmbeddings(
                    google_api_key=self.gemini_api_key or os.getenv("GEMINI_API_KEY"),
                    model="models/embedding-001"
                )
            except Exception as e:
                logger.error(f"Error initializing embeddings model: {str(e)}")
                raise
        return self.embeddings_instance