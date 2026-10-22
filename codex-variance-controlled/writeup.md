# Controlled Codex variance

Follow-up to [the original run](../codex-repeat-variance/) and [the sequential re-test](../codex-variance-sequential/).

Overall verdict: **PENDING (execution in progress)**. Completed 4/24 preregistered scored trials.

|Arm|n|Mean cost index|95% bootstrap CI|Mean cached input|
|---|---:|---:|---|---:|
|short|2|$0.006923|[0.006923, 0.006923]|85.81%|
|spaced|2|$0.006923|[0.006923, 0.006923]|85.81%|

|Hypothesis|Estimate and intervals|Verdict|
|---|---|---|
|Spacing changes mean cost|Ratio 1.0000; 95% CI [1.0, 1.0]; 90% CI [1.0, 1.0]|PENDING (execution in progress)|
|Cache share explains R² > .50|R² nan; 95% CI undefined bootstrap replicates|PENDING (execution in progress)|

Decision rules were committed before the first call. The timing rule tests superiority with a 95% percentile bootstrap interval excluding 1, and equivalence with a 90% interval wholly inside [0.90, 1.10]; equivalence takes priority. Cache-share R² uses a 95% pairs-bootstrap interval against .50. Each uses 50,000 resamples and the preregistered seeds. Arm-mean intervals are descriptive. No significance-based stopping or retrospective margin changes.

Twelve blocks each contain one short and one spaced trial, with seeded randomized order. Warm-ups and invalid attempts remain in attempts.jsonl and raw event logs, excluded from inference. Per-attempt results are written locally and the ledger fsynced immediately. See runs.csv for timestamps, gaps, and token counts.

Prices are frozen accounting weights ($2/M uncached input, $0.10/M cached input, $10/M output), not current price claims or actual subscription charges. Cache/cost association is partly built into that formula and does not establish causation. Other account activity and provider routing remain uncontrolled. Independent-trial bootstrap intervals may understate uncertainty if sequential dependence persists. Inference applies to this fixed source-output task, not the earlier tool-using repair workflow or long agent sessions. With only 12 observations per arm, precision can remain inadequate if task variance exceeds the .08 log-SD planning assumption.

GPU: none. Experiment CU used: **0**. Hosted Codex CLI on the inherited default account; no Colab session created and none stopped. Public/synthetic fixture only.
