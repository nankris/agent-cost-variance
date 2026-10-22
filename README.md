# agent-cost-variance

How much does the bill for the same agent task move from run to run, and why? Independent studies, each with its own README, code, raw results, chart and verdict.

- [`codex-repeat-variance`](codex-repeat-variance/): same task, five runs (Codex CLI): how random is the bill?
- [`claude-repeat-variance`](claude-repeat-variance/): same task, five runs (Claude Code side): how random is the bill?
- [`codex-variance-sequential`](codex-variance-sequential/): sequential Codex timing/cache re-test, **STILL INCONCLUSIVE**
- [`codex-cache-ab`](codex-cache-ab/): randomized prompt nonce to bust the cache, **STILL INCONCLUSIVE**
- [`codex-variance-controlled`](codex-variance-controlled/): controlled Codex variance with a fixed task and spaced vs back-to-back sessions (the saved results cover 4 of the 24 planned trials)
