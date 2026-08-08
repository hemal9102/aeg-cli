# Architecture Decisions (ADRs)

## ADR-001: SQLite over PostgreSQL for CLI State
**Decision:** Use embedded SQLite / DuckDB instead of PostgreSQL.
**Reason:** The system is a CLI distributed to local machines. Running PostgreSQL introduces massive dependency and operational friction (requires Docker/services). SQLite is embedded, zero-setup, and handles single-user CLI concurrency perfectly.
**Status:** Accepted

## ADR-002: Git Worktrees for Agent Isolation
**Decision:** Use Git Worktrees when parallelizing Agent Tasks.
**Reason:** If multiple agents (e.g., Security, Performance, Implementation) act on the same local directory, race conditions occur (e.g., modifying identical files, blocking tests). Worktrees provide absolute isolation.
**Status:** Accepted

## ADR-003: SQLite as Source of Truth for Knowledge
**Decision:** The database is the primary state, Obsidian Markdown files are projections.
**Reason:** Prevents "Split-Brain" consistency issues where a DB update succeeds but a Markdown file write fails. The system writes to the SQLite DB, and projects changes out to Obsidian-compatible Markdown for human consumption.
**Status:** Accepted

## ADR-004: Strict Evidence Lifecycle (TTL)
**Decision:** Auto-prune the Evidence Store (Playwright traces, snapshots).
**Reason:** Storing traces for every step will rapidly explode disk space. We only retain traces for *failed* Truth Gate evaluations (for debugging) and the *final* successful run (for records).
**Status:** Accepted

## ADR-005: LSP over Static AST for Dependency Graphing
**Decision:** Query headless Language Servers (pyright, tsserver, intelephense) via RPC instead of building static AST graphs with tree-sitter + NetworkX.
**Reason:** Dynamic languages (Python, PHP, JS) are too complex for static AST parsers to accurately resolve dependencies at scale. LSP handles dynamic imports and dependency injection optimally, avoiding hallucinated edges.
**Status:** Accepted

## ADR-006: Execution Sandboxes (Docker/microVMs)
**Decision:** Agents must execute tests and shell commands inside isolated Docker containers or microVMs.
**Reason:** Prevents "Zombie Process" exhaustion (e.g., orphaned headless Chromium) and provides a secure sandbox against Indirect Prompt Injection (where an agent is tricked into running malicious code on the host machine).
**Status:** Accepted

## ADR-007: Idempotent Truth Gate Verification
**Decision:** The Truth Gate must run E2E/network tests with quorum (e.g., pass 2 out of 3 runs) or use offline mocking (e.g., VCR.py).
**Reason:** Network calls and E2E browsers are inherently flaky. Single-run verification will cause the AI to hallucinate fixes for non-existent code issues when the failure was just a network timeout.
**Status:** Accepted

## ADR-008: Git-Versioned Knowledge Vault Facts
**Decision:** Facts in the Knowledge Vault must be tied to Git Commit Hashes or have a short TTL.
**Reason:** Prevents the AI from making decisions based on stale, outdated memories (e.g., a route changed from /api/users to /api/v2/users). The orchestrator must force agents to re-verify vault facts against the current codebase.
**Status:** Accepted
