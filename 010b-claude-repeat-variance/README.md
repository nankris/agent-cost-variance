# #010b Same task, five runs (Claude Code side): how random is the bill?

**Question.** Codex #010 ran 2 tasks × 5 identical runs and saw cost spread 1.4–2.2×. Does Claude Code behave the same?

**Short answer.** No. Claude Code was almost deterministic in usage: **total tokens moved 1.1% (SUITE14) and 0.1% (N02)**, cost **1.05× and 1.01×** max/min (CV 1.7% and 0.5%). All 10 runs passed, every run used exactly 4 model calls and 3 Bash calls, and the cache-read share was 75.7–76.0% / 82.8–82.9% every time. Codex's spread came from cache-hit variance (66–88%); Claude Code's explicit cache breakpoints make the cache hit identical run to run. The flip side: at list prices Claude Code (Opus 5.5) was **3.4× (SUITE14) and 3.5× (N02) more expensive per run** than Codex (gpt-6.1-sol): $0.245 vs $0.072 and $0.141 vs $0.040 mean.

## Setup
- Claude Code 2.1.300, default model `claude-opus-5-5`, default effort, Claude Pro sign-in. Headless: `claude -p "<prompt>" --output-format stream-json --verbose --dangerously-skip-permissions --strict-mcp-config --no-session-persistence` in a fresh temp copy of the fixture. `--strict-mcp-config` only drops the account's 3 claude.ai connectors (see #007); everything else is default.
- Same tasks and prompts as Codex #010: `SUITE14` (14 packages, 13 broken, prompt in `scripts/prompt.txt`, pass = `node run_all.js` exits 0 and no test.js/run_all.js changed) and `N02_duration` (prompt ``Make `node test.js` pass by fixing the code. Do not edit test.js.``). 5 runs each, 2 at a time, 2026-10-14 19:43–19:45 UTC.
- Est. $ = Claude Code's `total_cost_usd` (list API price, implied ≈ $4/M input, $8/M 1-hour cache write, $0.20/M cache read, $20/M output). Codex numbers are copied from `../010-codex-repeat-variance/results/runs.csv` (gpt-6.1-sol list price). **All $ are API-equivalent estimates; neither Pro nor Plus is billed per token.**

## Exact commands
```bash
source /workspace/tools/setup.sh
scripts/harness/driver_cc.sh scripts/jobs.txt 2 results/driver.log
/workspace/tools/mlenv/bin/python scripts/analyze.py
```

## Results (10 runs, 10/10 pass)
| Agent | Task | Total tokens min–max | Uncached (cache write+input) | Output | Cache-read share | Calls | Est. $ min–max | Cost max/min (CV) |
|---|---|---|---|---|---|---|---|---|
| Claude Code | SUITE14 | 98,400–99,487 | 23,100–23,614 | 1,949–2,357 | 75.7–76.0% | 4 | $0.239–0.251 | **1.05× (1.7%)** |
| Claude Code | N02_duration | 85,115–85,220 | 14,514–14,540 | 500–588 | 82.8–82.9% | 4 | $0.140–0.142 | **1.01× (0.5%)** |
| Codex (#010) | SUITE14 | 94,920–129,628 | 19,671–33,226 | 1,123–1,406 | 66–84% | 4–5 | $0.060–0.086 | 1.44× (15%) |
| Codex (#010) | N02_duration | 75,126–90,156 | 8,854–24,986 | 338–408 | 71–88% | 4 | $0.028–0.060 | 2.16× (34%) |

`results/summary.csv`, `results/runs.csv` (per run, includes 5-hour/7-day Pro window utilisation from Claude's `rate_limit_event`), raw stream-json in `results/raw/`. Chart: `results/chart.png`.

### Reading it
- Output tokens varied ±6–7% (the model wrote slightly different fixes/explanations) — about the same as Codex — but that's a small slice of the bill.
- The input side didn't vary at all: Claude Code marks cache breakpoints itself, so a fresh run reuses the same ~8.6K cached system prefix and writes the same new turns. No "warm vs cold" luck.
- Claude wrote ~2× the output tokens Codex did on SUITE14 and paid $8/M to *write* 14–23K tokens into the 1-hour cache each run. That (plus Opus pricing) is most of the 3.4× gap.
- Wall time: Claude 26–41 s on SUITE14 and 15 s on N02, vs Codex 45–109 s and 62–75 s (Codex runs shared the account with other jobs and hit 429 retries).

## Caveats
- 5 runs per task, short single-session tasks, one evening; runs 2 at a time. Long branching tasks could still diverge.
- Different models and prices: this compares the two CLIs as shipped, not model quality.
- Each Claude run used ~1.3% of the Pro 5-hour window on average (from `rl_5h_util`; coarse, 2 decimals).
