# Business Context & Goals

## The Product
**Autonomous Engineering & Growth CLI (AEG)**

A command-line interface tool (`aeg`) that leverages a Multi-Agent System (MAS) to autonomously perform engineering, testing, security auditing, and SEO optimizations on any local or GitHub-hosted codebase.

## Core Philosophy
**AI is NOT the source of truth.**
`FACT → TOOL → EVIDENCE → AI ANALYSIS → DECISION → EXECUTION → VERIFICATION`

The system demands concrete evidence (Playwright trace, pytest result, AST graph) before allowing an AI to make decisions or commit code.

## Key Objectives
1. **Zero / Near-Zero False Positives:** Verify everything via the "Truth Gate".
2. **Reusability:** Works on JobRecruitment (PHP/Laravel), ecommerce (Next.js/Node), or SEO platforms.
3. **Persistent Knowledge:** The system must remember past project contexts, architecture decisions, and failures in a Knowledge Vault, avoiding repeated mistakes.
4. **Safety:** Keep production safe. Agents operate in dev/test sandboxes, isolated via Git worktrees, requiring human/truth-gate approval to merge.
