from aeg.models.state import AgentRole

class BaseAgent:
    """
    Base restricted agent class with token budgets and circuit breakers.
    """
    def __init__(self, role: AgentRole, model_name: str = "claude-3-5-sonnet-20240620"):
        self.role = role
        self.model_name = model_name
        self.token_budget = 100000  # Example strict budget
        self.tokens_used = 0
        
    def check_circuit_breaker(self):
        """
        Throws an exception if the agent has hallucinated into an infinite loop and exhausted tokens.
        """
        if self.tokens_used > self.token_budget:
            raise RuntimeError(f"Circuit Breaker tripped for {self.role.value}: Token budget exceeded.")

    def run_prompt(self, prompt: str) -> str:
        """
        Stub for LLM execution via MCP.
        """
        print(f"[{self.role.value.upper()}] Thinking...")
        self.tokens_used += len(prompt) * 2  # Naive stub token calculation
        self.check_circuit_breaker()
        return "Action completed successfully."
