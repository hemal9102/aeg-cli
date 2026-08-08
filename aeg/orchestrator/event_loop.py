import time
from typing import List
from aeg.models.state import Task, TaskState
from aeg.core.vault import KnowledgeVault
from aeg.orchestrator.planner import DAGPlanner
from aeg.sandbox.isolation import SandboxIsolation

class ExecutionLoop:
    """
    The main event loop that processes the task DAG resiliently.
    Follows Principal Architect isolation rules.
    """
    def __init__(self, vault: KnowledgeVault, project_root: str):
        self.vault = vault
        self.planner = DAGPlanner()
        self.sandbox = SandboxIsolation(project_root)
        self.tasks: List[Task] = []
        
    def start(self, goal: str):
        self.tasks = self.planner.plan_tasks(goal)
        
        for task in self.tasks:
            self.vault.save_task(task)
            
        print(f"Generated {len(self.tasks)} tasks. Starting MAS pipeline...")
        
        while True:
            executable_tasks = self.planner.get_executable_tasks(self.tasks)
            
            if not executable_tasks:
                if all(t.state == TaskState.COMPLETED for t in self.tasks):
                    print("All tasks completed successfully!")
                    break
                elif any(t.state == TaskState.FAILED for t in self.tasks):
                    print("Execution halted due to failed tasks.")
                    break
                else:
                    print("Deadlock detected. Exiting loop.")
                    break
                    
            for task in executable_tasks:
                self._execute_task(task)

    def _execute_task(self, task: Task):
        print(f"[{task.assigned_to.value.upper()}] Executing task: {task.description}")
        task.state = TaskState.RUNNING
        self.vault.save_task(task)
        
        worktree_path = None
        try:
            # Spawn isolated sandbox for the task
            worktree_path = self.sandbox.spawn_worktree(f"task_{task.id}")
            
            # TODO: LLM agent execution would go here.
            # Using Ponytail dummy execution for now:
            self.sandbox.run_in_sandbox(worktree_path, ["echo", "Running agent logic..."])
            
            # Verification Phase
            print(f"[{task.assigned_to.value.upper()}] Pushing through Truth Gate...")
            
            task.state = TaskState.COMPLETED
        except Exception as e:
            print(f"[ERROR] Task failed: {str(e)}")
            task.state = TaskState.FAILED
        finally:
            if worktree_path:
                self.sandbox.cleanup_worktree(worktree_path)
            self.vault.save_task(task)
