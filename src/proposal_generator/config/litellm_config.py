"""LiteLLM configuration."""
from typing import Dict, Any
import os
from litellm import Router

def setup_litellm() -> Router:
    """Set up LiteLLM router with model configurations."""
    model_list = [
        {
            "model_name": "gemini-pro",
            "litellm_params": {
                "model": "gemini/gemini-pro",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "max_tokens": 4096,
                "temperature": 0.7,
            },
        }
    ]
    
    # Initialize router with just the model list
    router = Router(model_list=model_list)
    
    # Set default configuration
    router.set_model_list(model_list)
    
    return router 