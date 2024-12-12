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

from ..workflow.proposal_workflow import ProposalWorkflowManager
from ..workflow.workflow_models import WorkflowConfig, EnumEncoder
from .export_manager import ExportManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
app.json_encoder = EnumEncoder

# Configure caching
cache_config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 500
}
cache = Cache(app, config=cache_config)

# Initialize managers
workflow_manager = ProposalWorkflowManager(WorkflowConfig(
    output_dir=Path("output"),
    cache_results=True,
    cache_dir=Path("cache"),
    google_search_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
    google_custom_search_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ID"),
    gemini_api_key=os.getenv("GEMINI_API_KEY")
))
export_manager = ExportManager(output_dir="exports")

def cache_key(*args, **kwargs):
    """Generate cache key from request data."""
    key_dict = {
        'args': args,
        'kwargs': kwargs,
        'form': request.form.to_dict() if request.form else None,
        'json': request.get_json(silent=True)
    }
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()

def cached_proposal(timeout=300):
    """Decorator for caching proposal results."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key_str = cache_key(*args, **kwargs)
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result
            result = f(*args, **kwargs)
            cache.set(cache_key_str, result, timeout=timeout)
            return result
        return decorated_function
    return decorator

@app.route('/')
async def index():
    """Render the proposal form."""
    return await render_template('proposal_form.html')

@app.route('/generate', methods=['POST'])
async def generate_proposal():
    """Generate proposal based on form data."""
    try:
        # Get JSON data from request
        data = await request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Log received data
        logger.info(f"Received proposal request: {json.dumps(data, default=str)}")

        # Extract topic and requirements from data
        topic = f"{data['business_name']} - {data['project_description']}"
        requirements = {
            'target_audience': data['target_market'],
            'industry': data['industry'],
            'client_name': data['client_name'],
            'business_name': data['business_name'],
            'website': data.get('website', ''),
            'competitors': data.get('competitors', []),
            'features': data.get('requirements', {}).get('features', []),
            'project_description': data['project_description']
        }

        # Create workflow config
        config = WorkflowConfig(
            concurrent_analysis=True,
            max_workers=4,
            include_mockups=True,
            include_seo=True,
            include_market=True,
            include_content=True,
            google_search_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
            google_custom_search_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ID"),
            gemini_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Initialize workflow manager
        workflow_manager = ProposalWorkflowManager(config)
        
        # Generate proposal with both topic and requirements
        logger.info("Starting proposal generation...")
        result = await workflow_manager.generate_proposal(topic, requirements)
        logger.info("Proposal generation completed")
        
        # Convert result to JSON-serializable format
        response_data = result.to_dict()
        logger.info(f"Sending response: {json.dumps(response_data, default=str)}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/<result_key>/<format>')
def export_proposal(result_key: str, format: str):
    """Export proposal in specified format."""
    try:
        # Retrieve cached result
        result = cache.get(result_key)
        if not result:
            return jsonify({
                'success': False,
                'errors': ['Proposal result not found or expired']
            }), 404
        
        # Prepare proposal data
        proposal_data = {
            'client_name': result.client_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_description': result.project_description,
            'industry': result.industry,
            'target_market': result.target_market,
            'seo_insights': result.seo_insights,
            'market_insights': result.market_insights,
            'content_plan': result.content_plan,
            'mockups': result.mockups
        }
        
        # Export based on format
        if format == 'pdf':
            output_path = export_manager.export_pdf(proposal_data)
            return send_file(output_path, mimetype='application/pdf')
            
        elif format == 'pptx':
            output_path = export_manager.export_pptx(proposal_data)
            return send_file(output_path, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            
        elif format == 'json':
            output_path = export_manager.export_json(proposal_data)
            return send_file(output_path, mimetype='application/json')
            
        elif format == 'zip':
            output_path = export_manager.export_archive(proposal_data)
            return send_file(output_path, mimetype='application/zip')
            
        else:
            return jsonify({
                'success': False,
                'errors': ['Invalid export format']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [str(e)]
        }), 500

@app.route('/api/progress/<result_key>')
def get_progress(result_key: str):
    """Get proposal generation progress."""
    try:
        result = cache.get(result_key)
        if not result:
            return jsonify({
                'success': False,
                'errors': ['Proposal result not found or expired']
            }), 404
            
        return jsonify({
            'success': True,
            'progress': result.progress.__dict__ if result.progress else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [str(e)]
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the cache."""
    try:
        cache.clear()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [str(e)]
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 