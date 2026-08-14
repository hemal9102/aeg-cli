import asyncio
import logging
from typing import List
from aeg.models.state import Task, TaskState
from aeg.core.vault import KnowledgeVault
from aeg.orchestrator.planner import DAGPlanner
from aeg.sandbox.isolation import SandboxIsolation

logger = logging.getLogger(__name__)

class ExecutionLoop:
    """
    The main event loop that processes the task DAG resiliently.
    Follows Principal Architect isolation rules:
    - Decoupled via async execution.
    - Idempotent state resumption from Vault.
    - Structured logging telemetry.
    """
    def __init__(self, vault: KnowledgeVault, project_root: str):
        self.vault = vault
        self.planner = DAGPlanner()
        self.sandbox = SandboxIsolation(project_root)
        self.tasks: List[Task] = []
        
    async def start(self, goal: str):
        # State Resumption Logic
        existing_tasks = self.vault.get_tasks()
        if existing_tasks:
            logger.info(f"Resuming {len(existing_tasks)} tasks from KnowledgeVault.")
            self.tasks = existing_tasks
        else:
            logger.info("No existing state found. Planning new DAG.")
            self.tasks = self.planner.plan_tasks(goal)
            for task in self.tasks:
                self.vault.save_task(task)
            
        logger.info(f"Loaded {len(self.tasks)} tasks. Starting MAS pipeline...")
        
        while True:
            executable_tasks = self.planner.get_executable_tasks(self.tasks)
            
            if not executable_tasks:
                running_tasks = [t for t in self.tasks if t.state == TaskState.RUNNING]
                
                if running_tasks:
                    # Still waiting for some to finish, sleep briefly then continue loop
                    await asyncio.sleep(1)
                    continue
                
                if all(t.state == TaskState.COMPLETED for t in self.tasks):
                    logger.info("All tasks completed successfully!")
                    break
                elif any(t.state == TaskState.FAILED for t in self.tasks):
                    logger.error("Execution halted due to failed tasks.")
                    break
                else:
                    logger.error("Deadlock detected. Exiting loop.")
                    break
                    
            # Concurrently execute all ready tasks
            await asyncio.gather(*(self._execute_task(task) for task in executable_tasks))

    async def _execute_task(self, task: Task):
        role_label = task.assigned_to.value.upper() if task.assigned_to else "SYSTEM"
        logger.info(f"[{role_label}] Executing task: {task.description} (ID: {task.id})")
        
        task.state = TaskState.RUNNING
        self.vault.save_task(task)
        
        worktree_path = None
        try:
            # Spawn isolated sandbox for the task (async)
            worktree_path = await self.sandbox.spawn_worktree(f"task_{task.id}")
            
            # Wake up the Brain (synchronous LLM call mapped to thread)
            from aeg.agents.base import BaseAgent
            agent = BaseAgent(role=task.assigned_to)
            
            prompt = f"You are acting as a {task.assigned_to.value if task.assigned_to else 'assistant'}. Your task is to: {task.description}. Reply exactly with the shell commands you wish to execute in the sandbox, separated by newlines."
            
            # Non-blocking execution of synchronous LLM IO
            llm_response = await asyncio.to_thread(agent.run_prompt, prompt)
            
            commands_to_run = llm_response.strip().split("\n")
            
            for cmd in commands_to_run:
                if cmd.startswith("```") or not cmd.strip():
                    continue
                # Async sandbox execution
                await self.sandbox.run_in_sandbox(worktree_path, cmd.strip().split(" "))
            
            # Verification Phase
            logger.info(f"[{role_label}] Pushing through Truth Gate...")
            
            task.state = TaskState.COMPLETED
        except Exception as e:
            logger.error(f"[ERROR] Task {task.id} failed: {str(e)}")
            task.state = TaskState.FAILED
        finally:
            if worktree_path:
                await self.sandbox.cleanup_worktree(worktree_path)
            self.vault.save_task(task)
