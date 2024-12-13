from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sqlite3
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class AgentMemory:
    """Memory management for agents."""
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        """Initialize agent memory."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.db_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.setup_database()
            self.migrate_database()
            
        except Exception as e:
            logger.error(f"Error initializing agent memory: {str(e)}")
            raise

    def setup_database(self):
        """Setup database tables."""
        try:
            cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_expertise (
                    agent_id TEXT PRIMARY KEY,
                    expertise_data TEXT,
                    domain TEXT,
                    skill_level REAL,
                    success_rate REAL,
                    specializations TEXT,
                    experience_count INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    task_type TEXT,
                    result_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agent_expertise(agent_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phase_results (
                    phase_id TEXT PRIMARY KEY,
                    phase_name TEXT,
                    result_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            raise

    def migrate_database(self):
        """Migrate database schema if needed."""
        try:
            cursor = self.conn.cursor()
            
            # Check if expertise_data column exists
            cursor.execute("PRAGMA table_info(agent_expertise)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'expertise_data' not in columns:
                # Add expertise_data column
                cursor.execute("ALTER TABLE agent_expertise ADD COLUMN expertise_data TEXT")
                
                # Migrate existing data
                cursor.execute("""
                    UPDATE agent_expertise 
                    SET expertise_data = json_object(
                        'domain', domain,
                        'skill_level', skill_level,
                        'success_rate', success_rate,
                        'specializations', specializations,
                        'experience_count', experience_count
                    )
                    WHERE expertise_data IS NULL
                """)
                
                self.conn.commit()
                
            # Initialize default expertise if table is empty
            cursor.execute("SELECT COUNT(*) FROM agent_expertise")
            count = cursor.fetchone()[0]
            
            if count == 0:
                default_agents = {
                    'research_agent': ['market_research', 'competitor_analysis', 'trend_analysis'],
                    'design_agent': ['ui_design', 'ux_optimization', 'visual_design'],
                    'coding_agent': ['frontend_development', 'backend_development', 'api_integration'],
                    'ai_agent': ['ml_integration', 'nlp_processing', 'ai_optimization']
                }
                
                for agent_id, expertise in default_agents.items():
                    cursor.execute(
                        "INSERT OR IGNORE INTO agent_expertise (agent_id, expertise_data) VALUES (?, ?)",
                        (agent_id, json.dumps(expertise))
                    )
                
                self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error migrating database: {str(e)}")
            raise

    async def store_task_result(self, task_id: str, agent_id: str, task_type: str, result: Dict[str, Any]):
        """Store a task result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO task_results (task_id, agent_id, task_type, result_data) VALUES (?, ?, ?, ?)",
                (task_id, agent_id, task_type, json.dumps(result))
            )
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing task result: {str(e)}")
            raise

    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT result_data FROM task_results WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving task result: {str(e)}")
            raise

    async def store_phase_result(self, phase_id: str, phase_name: str, result: Dict[str, Any]):
        """Store a phase result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO phase_results (phase_id, phase_name, result_data) VALUES (?, ?, ?)",
                (phase_id, phase_name, json.dumps(result))
            )
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing phase result: {str(e)}")
            raise

    async def get_phase_result(self, phase_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a phase result."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT result_data FROM phase_results WHERE phase_id = ?", (phase_id,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving phase result: {str(e)}")
            raise

    async def get_agent_expertise_map(self) -> Dict[str, List[str]]:
        """Get map of agent expertise."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT agent_id, expertise_data FROM agent_expertise")
            rows = cursor.fetchall()
            
            expertise_map = {}
            for row in rows:
                agent_id, expertise_data = row
                if expertise_data:
                    expertise_map[agent_id] = json.loads(expertise_data)
                else:
                    # Provide default expertise if data is missing
                    expertise_map[agent_id] = ['general']
            
            # Ensure we always return something
            if not expertise_map:
                expertise_map = {
                    'default_agent': ['general']
                }
                
            return expertise_map
            
        except Exception as e:
            logger.error(f"Error retrieving agent expertise map: {str(e)}")
            raise

    async def update_agent_expertise(self, agent_id: str, expertise: List[str]):
        """Update an agent's expertise."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO agent_expertise (agent_id, expertise_data) VALUES (?, ?)",
                (agent_id, json.dumps(expertise))
            )
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating agent expertise: {str(e)}")
            raise

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
