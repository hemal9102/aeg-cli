import sqlite3
import os
import yaml
from pathlib import Path
from aeg.models.state import ProjectState, Task

class KnowledgeVault:
    """
    Manages the SQLite state and projects out human-readable Obsidian Markdown files.
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.aeg_dir = self.project_root / ".aeg"
        self.db_path = self.aeg_dir / "state.db"
        self.vault_dir = self.aeg_dir / "vault"
        
    def init_vault(self, project_name: str, project_type: str):
        self.aeg_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite DB
        self.conn = sqlite3.connect(self.db_path)
        self._create_schema()
        
        # Initial Project State
        state = ProjectState(name=project_name, type=project_type)
        
        # Project YAML configuration
        project_yaml_path = self.aeg_dir / "project.yaml"
        with open(project_yaml_path, "w") as f:
            yaml.dump(state.model_dump(), f)
            
        # Create default Obsidian markdown structure
        self._write_markdown_projection(
            "01-business.md", 
            f"# Business Context\nProject: {project_name}\nType: {project_type}\n"
        )
        
        print(f"Vault initialized at {self.aeg_dir}")

    def _create_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            description TEXT,
            state TEXT,
            assigned_to TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            type TEXT,
            passed BOOLEAN,
            payload_path TEXT,
            timestamp DATETIME
        )
        """)
        self.conn.commit()

    def _write_markdown_projection(self, filename: str, content: str):
        filepath = self.vault_dir / filename
        with open(filepath, "w") as f:
            f.write(content)

    def save_task(self, task: Task):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO tasks (id, description, state, assigned_to) VALUES (?, ?, ?, ?)",
            (task.id, task.description, task.state.value, task.assigned_to.value if task.assigned_to else None)
        )
        self.conn.commit()
