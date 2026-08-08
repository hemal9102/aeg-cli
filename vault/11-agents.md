# Multi-Agent System (MAS) & Roles

The system uses dynamic task decomposition rather than running all agents blindly in parallel. The Orchestrator plans the graph, and assigns isolated work.

## Core Agents

1. **Orchestrator (CTO)**
   - Responsible for overall dynamic task planning.
   - Decomposes high-level requirements into DAG tasks (Task 1 -> Task 2).
2. **Architect**
   - Reviews system design, sets constraints, reads codebase graph.
3. **Researcher (SEO/Growth)**
   - GSC, GA4, Bing integrations. Analyzes traffic and performance facts.
4. **Developer**
   - Implementation agent. Writes code within isolated Git Worktrees.
5. **Tester & Security**
   - Writes API contracts, pytest fixtures, and Playwright scripts. 
   - Uses OWASP ZAP, Semgrep for vulns.
6. **Reviewer**
   - Distinct from Developer. Critiques the code (e.g., via `adversarial-review-master-skill`).
7. **Fact Verifier (The Truth Gate)**
   - Determines if the Developer's claims are true.
   - Demands hard evidence (passing tests, HTTP 200s, DB state).
   - Blocks action if unverified.

## Token Budgets
Each agent operates with a strict token budget to prevent infinite hallucination loops. If the retry threshold (`max_attempts = 3`) is hit, the task is sent to a Dead Letter Queue (DLQ) for human intervention.
