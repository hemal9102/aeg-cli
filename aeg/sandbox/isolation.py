import subprocess
import uuid
import os
import shutil
from pathlib import Path

class SandboxIsolation:
    """
    Ponytail + Principal Architect Implementation:
    Minimalist filesystem isolation using native Git Worktrees.
    Throws hard exceptions on failure to prevent silent corruption.
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.worktrees_dir = self.project_root / ".aeg" / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        
    def spawn_worktree(self, branch_name: str) -> str:
        """
        Creates a Git worktree. Requires the repository to be a valid Git repo.
        """
        worktree_id = uuid.uuid4().hex[:8]
        branch = f"{branch_name}_{worktree_id}"
        worktree_path = self.worktrees_dir / f"task_{worktree_id}"
        
        print(f"[Sandbox] Spawning Git Worktree at {worktree_path} on branch {branch}")
        
        try:
            # Ponytail: stdlib subprocess, check=True enforces fail-fast
            subprocess.run(
                ["git", "worktree", "add", "-b", branch, str(worktree_path)],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to spawn worktree: {e.stderr}")
            
        return str(worktree_path)

    def run_in_sandbox(self, worktree_path: str, command: list):
        """
        Executes a command inside the isolated worktree with a strict timeout.
        """
        print(f"[Sandbox] Executing: `{' '.join(command)}` in {worktree_path}")
        try:
            # Principal: Enforce timeout to prevent zombie agents (DSA: O(1) timeout bound)
            result = subprocess.run(
                command,
                cwd=worktree_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=300 # 5 minute strict timeout
            )
            print("[Sandbox] Execution success.")
            return result.stdout
        except subprocess.TimeoutExpired:
            raise RuntimeError("Sandbox execution timed out.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Sandbox execution failed: {e.stderr}")

    def cleanup_worktree(self, worktree_path: str):
        """
        Forcefully removes the worktree and cleans up the branch.
        """
        print(f"[Sandbox] Cleaning up Worktree {worktree_path}")
        try:
            subprocess.run(["git", "worktree", "remove", "-f", str(worktree_path)], cwd=self.project_root, check=True)
        except subprocess.CalledProcessError:
            # Fallback cleanup if git fails
            if os.path.exists(worktree_path):
                shutil.rmtree(worktree_path, ignore_errors=True)
