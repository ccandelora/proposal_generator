from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Crew
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
from dotenv import load_dotenv

class Config:
    """Configuration class for managing environment variables and settings."""
    
    def __init__(self):
        """Initialize configuration."""
        # Load environment variables
        load_dotenv()
        
        # Project 1: Gemini API settings
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Project 2: Search API settings
        self.google_search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')  # Changed from GOOGLE_API_KEY
        self.google_custom_search_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ID')
        
        # Validate required settings
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        if not self.google_search_api_key:
            raise ValueError("GOOGLE_SEARCH_API_KEY not found in environment variables")
        if not self.google_custom_search_id:
            raise ValueError("GOOGLE_CUSTOM_SEARCH_ID not found in environment variables")

    @property
    def api_settings(self) -> dict:
        """Get API-related settings."""
        return {
            'project1': {
                'name': 'Gemini Project',
                'api_key': self.gemini_api_key[-4:],
            },
            'project2': {
                'name': 'Search Project',
                'api_key': self.google_search_api_key[-4:],
                'custom_search_id': self.google_custom_search_id[-4:],
            }
        }

def get_gemini_llm():
    """Get the Gemini LLM configuration."""
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        verbose=True,
        temperature=0.7,
        google_api_key=os.getenv("GEMINI_API_KEY"),  # Project 1
    )

def create_agent(config: dict) -> Agent:
    """Create an agent with Gemini LLM."""
    return Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        llm=get_gemini_llm(),
        verbose=True,
        allow_delegation=False  # Disable delegation to prevent OpenAI fallback
    )

def configure_crew(crew: Crew) -> Crew:
    """Configure the crew to use Gemini LLM."""
    # Set default LLM for the crew
    crew.llm = get_gemini_llm()
    
    # Ensure all agents use Gemini
    for agent in crew.agents:
        agent.llm = get_gemini_llm()
        agent.allow_delegation = False  # Disable delegation to prevent OpenAI fallback
    
    return crew 