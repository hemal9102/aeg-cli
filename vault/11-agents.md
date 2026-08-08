# Multi-Agent System (MAS) & Roles

The system uses dynamic task decomposition rather than running all agents blindly in parallel. The Orchestrator plans the graph, and assigns isolated work.

## Core Agents

1. **Growth Orchestrator (Director)**
   - Responsible for overall dynamic task planning for growth campaigns.
   - Decomposes high-level requirements (e.g. "Rank for keyword X") into DAG tasks.
2. **AEO Architect**
   - Specializes in Answer Engine Optimization. Designs JSON-LD schemas, Knowledge Graph integrations, and Semantic HTML microdata.
3. **GEO Writer & Context Engineer**
   - Specializes in Generative Engine Optimization. Restructures page content, semantic density, and keyword clustering to dominate Perplexity/ChatGPT RAG systems.
4. **Technical SEO Engineer**
   - The implementation agent. Writes code for programmatic sitemaps, caching, canonicals, robots.txt, and fixes Core Web Vitals (LCP, CLS, INP) directly in Git Worktrees.
5. **Growth Researcher**
   - Interfaces with Google Search Console (GSC), IndexNow APIs, and Analytics to fetch real-world ranking and indexing facts.
6. **The Truth Gate (Fact Verifier)**
   - Determines if the Engineer's claims are true.
   - Demands hard evidence (passing Lighthouse audits, Schema.org validation, HTTP 200 checks).
   - Blocks action if unverified.

## Token Budgets
Each agent operates with a strict token budget to prevent infinite hallucination loops. If the retry threshold (`max_attempts = 3`) is hit, the task is sent to a Dead Letter Queue (DLQ) for human intervention.
