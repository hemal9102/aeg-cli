# Autonomous Engineering & Growth CLI (AEG)

AEG is a terminal-driven, multi-agent AI framework designed for strict execution, isolation, and safety. Rather than giving LLMs raw access to your computer, AEG restricts AI agents inside isolated Git worktrees and forces their outputs through an idempotent verification layer (The Truth Gate) before merging code.

## 🌟 Core Philosophy

1. **AI is NOT the source of truth:** Code is driven by facts, tools, and evidence—not hallucinations.
2. **Strict Sandbox Isolation:** All tasks spawn unique Git Worktrees. If an agent breaks the code, the worktree is simply deleted. The main branch is never touched until tests pass.
3. **The Truth Gate:** An idempotent verification layer blocks any AI action that fails automated tests.
4. **Token Circuit Breakers:** Protects against infinite loops by enforcing strict token and time limits on agent subshells.

## 🚀 Installation

Ensure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/hemal9102/aeg-cli.git
cd aeg-cli

# Install the CLI globally (in editable mode)
pip install -e .
```

## ⚙️ Configuration

AEG uses Anthropic (Claude 3.5 Sonnet) as its core reasoning brain. You must export your API key before running the CLI:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 🛠️ Usage

### 1. Initialize a Project Vault
Set up the SQLite database and Obsidian markdown vault inside your project directory to persist the agent's memory:
```bash
aeg init
```

### 2. Start the Execution Loop
Assign a goal to the orchestrator. The CLI will decompose the task into a DAG, spawn the Git sandbox, wake up the AI brain, and pass the code through the Truth Gate:
```bash
aeg loop "Implement the login API with FastAPI"
```

## 🏗️ Architecture

- `aeg.core.vault`: Manages the local SQLite database and syncs it with `.md` files for human-readable long-term memory.
- `aeg.sandbox.isolation`: Manages Git Worktrees for zero-dependency physical isolation.
- `aeg.orchestrator.event_loop`: A Write-Ahead Log (WAL) powered DAG task executor.
- `aeg.verifier.truth_gate`: Enforces pass-rates and idempotency on AI code submissions.
- `aeg.agents.base`: Wraps `httpx` to communicate with the Anthropic API with strict token budgeting.

## License
MIT
