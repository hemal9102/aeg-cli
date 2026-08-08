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
        Uses the Orchestrator LLM to decompose a goal into a DAG.
        """
        import json
        from aeg.agents.base import BaseAgent
        
        print(f"[ORCHESTRATOR] Planning tasks for goal: {goal}")
        agent = BaseAgent(role=AgentRole.ORCHESTRATOR)
        
        prompt = f"""
You are the Growth Orchestrator for an SEO/AEO/GEO automation platform.
Break the following goal into a sequence of dependent tasks.
Goal: {goal}

Available roles: {', '.join([r.value for r in AgentRole if r != AgentRole.ORCHESTRATOR])}

Return EXACTLY a JSON array of objects, with no markdown formatting.
Schema:
[
  {{
    "id": "task_1",
    "description": "string",
    "assigned_to": "role_string",
    "dependencies": []
  }}
]
"""
        response_text = agent.run_prompt(prompt).strip()
        
        # Clean up possible markdown code blocks if the LLM ignores instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        try:
            tasks_data = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Orchestrator failed to return valid JSON: {str(e)}\nResponse: {response_text}")
            
        planned_tasks = []
        for td in tasks_data:
            planned_tasks.append(
                Task(
                    id=td["id"],
                    description=td["description"],
                    assigned_to=AgentRole(td["assigned_to"]),
                    dependencies=td.get("dependencies", [])
                )
            )
            
        return planned_tasks

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
