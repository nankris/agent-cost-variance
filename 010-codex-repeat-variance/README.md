# #010 Same task, five runs (Codex CLI): how random is the bill?

**Question.** Run the same Codex task with the same config several times. How much do tokens and cost move?

**Short answer.** On two tasks with 5 runs each, every run passed. Total tokens varied only **1.2–1.4×** between the cheapest and dearest run. **Estimated cost varied 1.4–2.2×**, because cost follows the cache hit rate, not the token count. On the 14-package suite, the run with the *fewest* tokens was the *second most expensive* (66% cache hits against 79–84% for the cheap runs). Across those 5 runs, total tokens and cost were uncorrelated (r = −0.04). I didn't see anything like the cited 30× spread. Two of the cited result's conditions are missing here: these are short runs, and the model always found the same fix.

## Setup
- Codex CLI 0.162.1, `gpt-6.1-sol`, default reasoning effort, ChatGPT Plus sign-in, headless `codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C <fresh copy>`. No config overrides.
- Task A, `default` rows: `SUITE14`, 14 small JS packages (13 broken) in one dir. Prompt in `scripts/prompt.txt`. Pass = `node run_all.js` exits 0 and no test.js changed. 5 runs, 2 at a time, 2026-10-14 14:53–14:56 UTC.
- Task B, `small_N02` rows: `N02_duration`, one duration-parser bug with a 420-line noisy test log. Prompt: ``Make `node test.js` pass by fixing the code. Do not edit test.js.`` 5 runs, 2 at a time, 15:02–15:05 UTC.
- Every run starts from a fresh copy of the fixture in a new temp dir.
- Est. cost at gpt-6.1-sol API list price ($2/M uncached input, $0.10/M cached input, $10/M output; https://developers.openai.com/api/docs/models/gpt-6.1-sol). It's an estimate. Plus isn't billed per token.

## Exact commands
```bash
source /workspace/tools/setup.sh
scripts/harness/driver.sh scripts/jobs.txt 2 results/driver.log            # SUITE14 x5
scripts/harness/driver.sh scripts/jobs_small.txt 2 results/driver_small.log # N02_duration x5
/workspace/tools/mlenv/bin/python scripts/analyze.py
# single run, e.g.
python3 scripts/harness/run_one.py --exp . --cond default --task scripts/harness/fixtures/SUITE14 --rep 1 \
  --check 'node run_all.js' --prompt "$(cat scripts/prompt.txt)" --timeout 1200
```

## Results (10 runs, 10/10 pass)

Per run:

| Task | Run | Total tokens | Cached | Uncached | Output | Cache share | Model calls | Est. cost |
|---|---|---|---|---|---|---|---|---|
| SUITE14 | 1 | 107,411 | 86,528 | 19,671 | 1,212 | 81% | 4 | $0.0601 |
| SUITE14 | 2 | 102,346 | 79,872 | 21,073 | 1,401 | 79% | 4 | $0.0641 |
| SUITE14 | 3 | 129,628 | 107,520 | 20,702 | 1,406 | 84% | 5 | $0.0662 |
| SUITE14 | 4 | 94,920 | 62,080 | 31,561 | 1,279 | 66% | 4 | $0.0821 |
| SUITE14 | 5 | 120,365 | 86,016 | 33,226 | 1,123 | 72% | 5 | $0.0863 |
| N02_duration | 1 | 85,545 | 60,160 | 24,986 | 399 | 71% | 4 | $0.0600 |
| N02_duration | 2 | 90,156 | 69,504 | 20,244 | 408 | 77% | 4 | $0.0515 |
| N02_duration | 3 | 75,126 | 65,920 | 8,854 | 352 | 88% | 4 | $0.0278 |
| N02_duration | 4 | 75,453 | 66,048 | 9,063 | 342 | 88% | 4 | $0.0282 |
| N02_duration | 5 | 80,314 | 69,376 | 10,600 | 338 | 87% | 4 | $0.0315 |

Spread (max/min, and coefficient of variation):

| Task | Total tokens | Uncached input | Est. cost | Model calls |
|---|---|---|---|---|
| SUITE14 | 1.37× (CV 13%) | 1.69× (CV 26%) | 1.44× (CV 16%) | 4–5 |
| N02_duration | 1.20× (CV 8%) | 2.82× (CV 50%) | 2.16× (CV 38%) | 4 every time |

Chart: `results/chart.png`. One row per task: tokens per run split cached/uncached/output, est. cost, and cache share.

### Reading it
- **The model's behaviour was steady.** Same number of calls (4–5), about the same output (CV 9–10%), same fix every time.
- **What moved the bill was the cache.** Uncached input swung 1.7–2.8× between runs, and at $2/M against $0.10/M for cached input it decides the cost. Total tokens are a bad proxy for cost here: r = −0.04 between total tokens and cost on SUITE14 (r = 0.87 on N02).
- **Order mattered on the small task.** Runs 1–2, which started together and first, had 71–77% cache hits and cost 5–6¢. Runs 3–5, which started a minute later, had 87–88% and cost about 3¢. That looks like prompt-cache warmth. It's an inference: I didn't randomise order, so I can't separate warmth from chance.
- The other 2 identical-config SUITE14 runs, in #011 (`nobudget`), cost $0.059 and $0.053, inside this range.

## Caveats
- 5 runs per task, short single-session tasks, same afternoon. Long agentic runs that branch into different strategies can spread far more. This doesn't refute the 30× figure for that kind of task.
- Runs went 2 at a time, and another Codex experiment shared the account at the same time. Both affect caching and latency (wall time varied 2.4× on SUITE14, mostly 429 retries on run 4).
- Cost is an API-price estimate. On Plus the marginal cost of a run is usage-window percentage, not dollars.

## Files
- `scripts/harness/` (runner, driver, fixtures), `scripts/jobs.txt`, `scripts/jobs_small.txt`, `scripts/prompt.txt`, `scripts/analyze.py`
- `results/runs.csv`, `results/summary.csv`, `results/chart.png`, `results/raw/*.jsonl` (raw `codex exec --json` streams)
