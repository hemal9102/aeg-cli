from typing import List
from aeg.models.state import Evidence

class TruthGate:
    """
    Implements Idempotent Verification (ADR-007).
    Forces AI to provide empirical evidence that passes quorum tests.
    """
    def __init__(self):
        pass

    def evaluate_quorum(self, task_id: str, runs: List[Evidence]) -> bool:
        """
        Requires 2 out of 3 runs to pass to mitigate flakiness.
        """
        print(f"[TruthGate] Evaluating quorum for task {task_id} across {len(runs)} runs.")
        
        pass_count = sum(1 for e in runs if e.passed)
        fail_count = len(runs) - pass_count
        
        if pass_count >= 2:
            print("[TruthGate] VERIFIED. Quorum reached.")
            return True
            
        print(f"[TruthGate] UNVERIFIED. Failed {fail_count} times.")
        return False

    def verify_action(self, task_id: str, evidence: Evidence) -> bool:
        """
        Strictly blocks action if evidence is not provided or fails.
        """
        if not evidence.passed:
            print(f"[TruthGate] BLOCKED. Action {task_id} failed verification.")
            return False
            
        print(f"[TruthGate] ALLOWED. Action {task_id} passed verification.")
        return True
