import uuid
from typing import List, Dict
from aeg.models.state import Task, TaskState, AgentRole

class DAGPlanner:
    """
    Takes a high-level goal and breaks it down into a Directed Acyclic Graph (DAG) of tasks.
    """
    def __init__(self):
        pass

    def plan_tasks(self, goal: str) -> List[Task]:
        """
        Stub logic for LLM-based DAG planning.
        In a real system, this calls an LLM to decompose the goal.
        """
        print(f"Planning tasks for goal: {goal}")
        
        # Example hardcoded DAG for demonstration:
        # Task 1 (Research) -> Task 2 (Implement) -> Task 3 (Verify)
        t1_id = f"task_{uuid.uuid4().hex[:8]}"
        t2_id = f"task_{uuid.uuid4().hex[:8]}"
        t3_id = f"task_{uuid.uuid4().hex[:8]}"
        
        t1 = Task(
            id=t1_id,
            description="Analyze requirements and architecture",
            assigned_to=AgentRole.ARCHITECT
        )
        
        t2 = Task(
            id=t2_id,
            description="Implement the logic in a sandboxed worktree",
            assigned_to=AgentRole.DEVELOPER,
            dependencies=[t1_id]
        )
        
        t3 = Task(
            id=t3_id,
            description="Verify implementation via Truth Gate",
            assigned_to=AgentRole.VERIFIER,
            dependencies=[t2_id]
        )
        
        return [t1, t2, t3]

    def get_executable_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Returns tasks whose dependencies are all completed.
        """
        completed_ids = {t.id for t in tasks if t.state == TaskState.COMPLETED}
        
        executable = []
        for t in tasks:
            if t.state == TaskState.PENDING:
                # Check if all dependencies are completed
                if all(dep in completed_ids for dep in t.dependencies):
                    executable.append(t)
                    
        return executable
