# Randomized prompt nonce: does busting the cache raise cost?

This is a follow-up to [the original run](../codex-repeat-variance/), [the sequential re-test](../codex-variance-sequential/) and [the controlled re-test](../codex-variance-controlled/).

Protocol fixed before trials, 2026-10-16. Hypothesis: cache materially reduces estimated cost; busted/cacheable paired mean cost ratio exceeds 1.15. The 15% threshold is the smallest premium I'd call practically material. The prompt and cost estimator are copied from [the controlled re-test](../codex-variance-controlled/).

Twenty blocks, one identical cacheable prompt and one prompt with a unique random 64-character alphanumeric nonce at its very start (then newline). Within-block order shuffled by Python Random(1010); nonces generated deterministically with separate seed 1011 and persisted before execution. Fresh ephemeral codex exec, gpt-6.1-sol, low reasoning, default inherited account, no CODEX_HOME override. No warmup or idle gaps. Unlike the controlled re-test's 15-minute expiry proxy (4/24 trials completed before it was interrupted), this directly changes the user prompt prefix, keeping model/task fixed. The nonce does not change the CLI's preceding system prefix; actual cache measurements are essential to interpretation.

## Fixed decision and analysis
Primary estimator: arithmetic mean of the twenty within-block cost ratios busted/cacheable. Resample complete blocks with replacement, 20,000 percentile bootstrap draws, seed 1012, 95% CI. PROVEN if lower endpoint >1.15; DISPROVEN if upper endpoint <1.15 (includes practically insufficient effects); otherwise STILL INCONCLUSIVE at fixed sample/time budget exhaustion. No optional stopping or extra samples. Also report ratio of arm means descriptively. Threshold tests concern this manipulation and task, not whether cache discounts exist generally.

Secondary: OLS R² of cost on cached_input/input across all 40 calls, with block-bootstrap 95% CI, 20,000 draws, seed 1013. The same hypothesis as in the controlled re-test applies: R² >.50: PROVEN if lower >.50, DISPROVEN if upper <.50, otherwise inconclusive. Undefined constant predictor/outcome is reported explicitly. Secondary does not override primary. Association partly reflects the estimator's arithmetic.

Quick planning calculation: for paired log-ratio SD .10, n=20 gives SE .02236 and 95% halfwidth .04383. Approximate power to put the entire CI below log(1.15) at true ratio 1 is >99.99%; power to put it above at true ratio 1.25 is 96.0%. At SD .20 these powers are 87.8% and 46.1%. Normal log-scale planning approximates the arithmetic-ratio bootstrap, and is not a guarantee. Twenty fixed pairs can resolve no effect or a substantial premium without huge equivalence samples.

Cost index (frozen weights from the controlled re-test, not current price or actual subscription billing): ((input-cached)*2 + cached*.10 + output*10)/1e6 dollars. Output includes any reasoning tokens; do not add reasoning twice. Record separately reported reasoning or null if CLI omits it; never infer zero.

## Persistence and execution
Run `python3 scripts/run.py`, then `python scripts/analyze.py`. Schedule and started/completed attempt events persist on disk. Raw stdout/stderr stream directly to results per call; each completion fsyncs the ledger. Resume skips completed valid trial IDs and recovers finished raw calls after interruption, recording interrupted attempts. Retain failures; at most two attempts per trial and 55 minutes wall time from first trial (persisted across reruns). No sample changes on rerun. A lock prevents concurrent runners.

Public/synthetic duration-parser task only. No Colab runtime is needed for hosted Codex calls or local analysis, and results are written locally immediately. GPU: none. CU used: 0 (cap was 5). No Colab session was started. The existing CLI configuration was used.

## Final execution record
All 20 blocks / 40 calls completed in 3.97 minutes with no retries; resumption check added no attempts. Primary STILL INCONCLUSIVE: paired mean ratio 1.110844, 95% CI [1.012589, 1.258045], crossing 1.15 after the fixed 40-call budget. Time/CU were not exhausted; no unplanned calls added. Secondary R² 0.999889, CI [0.999771, 1.000000], PROVEN against .50. Two rare higher-cache calls drive primary uncertainty. GPU none; CU used 0.  Full findings in writeup.md.
