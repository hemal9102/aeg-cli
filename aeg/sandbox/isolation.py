import asyncio
import uuid
import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SandboxIsolation:
    """
    Minimalist filesystem isolation using native Git Worktrees.
    Now utilizes asyncio for non-blocking I/O and more robust cleanup.
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.worktrees_dir = self.project_root / ".aeg" / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        
    async def spawn_worktree(self, branch_name: str) -> str:
        """
        Creates a Git worktree. Requires the repository to be a valid Git repo.
        """
        worktree_id = uuid.uuid4().hex[:8]
        branch = f"{branch_name}_{worktree_id}"
        worktree_path = self.worktrees_dir / f"task_{worktree_id}"
        
        logger.info(f"Spawning Git Worktree at {worktree_path} on branch {branch}")
        
        proc = await asyncio.create_subprocess_exec(
            "git", "worktree", "add", "-b", branch, str(worktree_path),
            cwd=str(self.project_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to spawn worktree: {stderr.decode()}")
            
        return str(worktree_path)

    async def run_in_sandbox(self, worktree_path: str, command: list):
        """
        Executes a command inside the isolated worktree with a strict timeout.
        """
        logger.info(f"Executing: `{' '.join(command)}` in {worktree_path}")
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                cwd=worktree_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Enforce strict 300s timeout per Principal Architect review
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            
            if proc.returncode != 0:
                raise RuntimeError(f"Sandbox execution failed: {stderr.decode()}")
                
            logger.info("Execution success.")
            return stdout.decode()
            
        except asyncio.TimeoutError:
            # Kill process if it times out
            try:
                proc.kill()
            except Exception:
                pass
            raise RuntimeError("Sandbox execution timed out after 300s.")

    async def cleanup_worktree(self, worktree_path: str):
        """
        Forcefully removes the worktree and cleans up the branch.
        Uses fail-safe robust cleanup instead of brittle assumptions.
        """
        logger.info(f"Cleaning up Worktree {worktree_path}")
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "worktree", "remove", "-f", str(worktree_path),
                cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            logger.warning(f"Git worktree remove failed: {e}")
            
        # Hard fallback cleanup to avoid zombie directories
        if os.path.exists(worktree_path):
            try:
                shutil.rmtree(worktree_path, ignore_errors=True)
            except Exception as cleanup_err:
                logger.error(f"Failed hard cleanup of {worktree_path}: {cleanup_err}")
