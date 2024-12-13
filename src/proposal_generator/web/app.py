"""Web interface for proposal generator."""
from quart import Quart, render_template, request, jsonify, send_file
from flask_caching import Cache
from pathlib import Path
import hashlib
import json
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional
import logging
import os
import asyncio
import traceback
import base64
import plotly

from ..workflow.proposal_workflow import ProposalWorkflowManager
from ..workflow.workflow_models import EnumEncoder
from ..components.export_manager import ExportManager
from ..config.workflow_config import WorkflowConfig, validate_api_keys, initialize_apis
from ..visualization.expertise_visualizer import ExpertiseVisualizer
from ..workflow.agent_memory import AgentMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
app.json_encoder = EnumEncoder

# Validate API keys on startup
api_status = validate_api_keys()
initialize_apis()

# Configure caching
cache_config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 500
}
cache = Cache(app, config=cache_config)

# Initialize managers and visualizers
workflow_manager = ProposalWorkflowManager(WorkflowConfig(
    output_dir=Path("output"),
    cache_results=True,
    cache_dir=Path("cache"),
    google_search_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
    google_custom_search_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ID"),
    gemini_api_key=os.getenv("GEMINI_API_KEY")
))
export_manager = ExportManager(output_dir="exports")
expertise_visualizer = ExpertiseVisualizer()
agent_memory = AgentMemory(db_path="data/agent_memory.db") 