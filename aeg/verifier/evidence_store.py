import os
from pathlib import Path
from aeg.models.state import Evidence

class EvidenceStore:
    """
    Manages TTL and persistence for raw evidence artifacts (Playwright traces, snapshots, logs).
    """
    def __init__(self, project_root: str):
        self.evidence_dir = Path(project_root) / ".aeg" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
    def save_evidence(self, task_id: str, evidence_type: str, payload: bytes) -> str:
        """
        Saves raw payload and returns the path.
        """
        task_dir = self.evidence_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        file_path = task_dir / f"{evidence_type}.log"
        with open(file_path, "wb") as f:
            f.write(payload)
            
        print(f"[EvidenceStore] Saved {evidence_type} for task {task_id}")
        return str(file_path)

    def prune_old_evidence(self):
        """
        Implements ADR-004: TTL for Evidence.
        Retains only failures and the final success.
        """
        print("[EvidenceStore] Pruning old evidence traces...")
        # Stub implementation
        pass
