import os
import httpx
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
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
    def check_circuit_breaker(self):
        """
        Throws an exception if the agent has hallucinated into an infinite loop and exhausted tokens.
        """
        if self.tokens_used > self.token_budget:
            raise RuntimeError(f"Circuit Breaker tripped for {self.role.value}: Token budget exceeded.")

    def run_prompt(self, prompt: str) -> str:
        """
        Executes the prompt against the Anthropic API safely.
        """
        print(f"[{self.role.value.upper()}] Thinking...")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is missing. Cannot wake up the agent.")
            
        self.check_circuit_breaker()
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
                response.raise_for_status()
                
            result = response.json()
            
            # Simple token accounting
            in_tokens = result.get("usage", {}).get("input_tokens", 0)
            out_tokens = result.get("usage", {}).get("output_tokens", 0)
            self.tokens_used += (in_tokens + out_tokens)
            
            reply = result["content"][0]["text"]
            print(f"[{self.role.value.upper()}] Response received ({self.tokens_used}/{self.token_budget} tokens used).")
            return reply
            
        except Exception as e:
            raise RuntimeError(f"LLM API failure: {str(e)}")
