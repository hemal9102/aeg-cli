import typer
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentRole(str, Enum):
    ORCHESTRATOR = "growth_orchestrator"
    AEO_ARCHITECT = "aeo_architect"
    GEO_WRITER = "geo_writer"
    TECHNICAL_SEO = "technical_seo_engineer"
    RESEARCHER = "growth_researcher"
    TRUTH_GATE = "truth_gate_verifier"

class ProjectState(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()

class Task(BaseModel):
    id: str
    description: str
    state: TaskState = TaskState.PENDING
    assigned_to: Optional[AgentRole] = None
    dependencies: List[str] = []

class Evidence(BaseModel):
    id: str
    task_id: str
    type: str  # e.g., "pytest_result", "playwright_trace"
    passed: bool
    payload_path: str
    timestamp: datetime = datetime.now()
