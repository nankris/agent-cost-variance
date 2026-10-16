# Experiment 010 round 3: controlled Codex variance

Protocol written before any model trials. Public/synthetic data only; original and round-2 folders are read-only sources.

## Hypotheses and changes
H1: cache-hit share explains a practically substantial fraction of estimated cost variation (population linear regression R² > 0.50). H2: spacing fresh sessions by >=900 seconds changes mean cost relative to sessions launched <=120 seconds after the preceding session ends.

Earlier rounds mixed noisy tool execution, variable trajectories, 0/1/5/15-minute gaps, interruptions and too few observations. This round uses one fixed small task: return the corrected duration-parser source, with no tool calls or filesystem changes. The buggy source is copied from round 2; the prompt embeds it. Fresh ephemeral sessions, one model and reasoning level, identical prompt and working path. This narrows inference to a fixed response task; it does not replicate the earlier agent repair workflow. No other account is used.

## Dated deviation — 2026-10-16, before any trial
Hari approved execution with 12 back-to-back and 12 spaced trials, interleaved, replacing the unrun 40-trial options. At amendment time no attempts ledger or trial outputs exist. Twelve blocks each contain one short and one spaced trial; within-block order is independently randomized with seed 101003. This ensures interleaving over the three-hour idle period while varying order. Spaced calls start >=900 seconds after the preceding call ends; short calls start <=120 seconds after it ends. One unscored warm-up establishes the first gap. Fixed 24 successful compliant trials; no significance-based stopping. Four-hour wall budget, including retries. Failed calls retain logs, count as cache exposures, and trigger a full assigned delay before retry. Interrupted short trials require a logged unscored warm-up before resuming. No concurrent experiment calls are launched by this runner.

## Fixed decision rules
Prices are frozen accounting weights from prior rounds: $2/M uncached input, $0.10/M cached input, $10/M output. These are a comparable cost index, not verified current prices or actual subscription charges.

Timing: ratio = spaced mean cost / short mean cost. Resample trials within arms, 50,000 percentile bootstrap replicates, seed 101004. PROVEN if the 95% CI excludes 1 (report direction). DISPROVEN/equivalent if the 90% CI is wholly inside [0.90,1.10], the bootstrap analogue of two one-sided 5% tests. Equivalence has priority if both hold: a detectable tiny change can still be practically equivalent. Ten percent is the smallest worthwhile scheduling saving, versus earlier 40–120% spreads. Otherwise STILL INCONCLUSIVE, explicitly identified as precision/time budget exhausted; never label absence of significance as equivalence.

Cache: OLS cost ~ intercept + cached_input/input, pooled over both arms. Pairs-bootstrap 50,000, seed 101005, 95% percentile CI for R². PROVEN if lower bound >0.50; DISPROVEN as practically insufficient if upper bound <0.50; otherwise STILL INCONCLUSIVE when the fixed sample/time budget ends. Constant predictor or outcome => undefined, not zero R². Also report regression including total input/output as descriptive accounting; cache/cost correlation is partly mathematical and is not causal proof. Each hypothesis receives its own verdict; overall PROVEN only if both are PROVEN, DISPROVEN if either disproven, otherwise STILL INCONCLUSIVE.

## Quick power calculation (recomputed before trials)
At 12/12, assuming log-cost SD .08, SE=.03266. Using both asymmetric log equivalence bounds log(.90) and log(1.10), approximate equivalence power at ratio 1 is 84.2%; two-sided superiority power at ratio 1.10 is 83.1%. With earlier-round SD .22, equivalence power is effectively zero and superiority power only 18.6%. Thus conclusiveness is likely only if the fixed-output design substantially reduces noise; this is an honest limitation, not a guarantee. The 10% practical margin and decision rules remain unchanged. For cache R² at n=24, a Fisher-z approximation gives about 73% power at true R²=.80 versus threshold .50, and >99% at .95. scripts/power.py saves exact planning approximations. The time budget cannot accommodate the much larger sample needed if prior variance persists.

## Resumption and artifacts
scripts/run.py persists each attempt's JSON event stream and metadata directly in results, fsyncs the ledger, and resumes by successful trial ID. No Colab or GPU computation is needed for remotely hosted Codex. GPU: none; experiment CU used: 0 (limit 5). Execution-time Colab usage checked first: 174.70 CU, two active assignments owned by others. No session created, so none to stop. Local incremental persistence replaces Colab download because no output resides in Colab. Never stop another experiment's sessions.

No credential values inspected. Default inherited Codex authentication only; no CODEX_HOME override. CLI version recorded. Run with `source /workspace/tools/setup.sh; python3 scripts/run.py`. Analyze with `/workspace/tools/mlenv/bin/python scripts/analyze.py`. No pushing.
