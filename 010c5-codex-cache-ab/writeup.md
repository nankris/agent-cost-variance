# Round 5 results

Primary verdict: **STILL INCONCLUSIVE** for a practically material (>15%) cost premium from prepending a nonce to this fixed user prompt.

| Arm | n | Mean input | Mean cached input | Mean output | Mean cache share | Mean cost index ($) |
|---|---:|---:|---:|---:|---:|---:|
| cacheable | 20 | 14318.000000 | 12467.200000 | 163.000000 | 0.870736 | 0.006578 |
| busted | 20 | 14362.000000 | 12288.000000 | 163.000000 | 0.855591 | 0.007007 |

20/20 complete randomized blocks. Mean paired busted/cacheable cost ratio **1.110844**, block-bootstrap 95% CI **[1.012589, 1.258045]** (20,000 draws). Ratio of arm means 1.065135. Fixed boundary 1.15; this verdict follows the preregistered CI rule. The prespecified 20-block (40-call) sample budget is exhausted; the CI crosses 1.15. Wall time and CU were not exhausted. Adding calls would violate the fixed design.

Secondary R² of cost on cache share: **0.999889**, block-bootstrap 95% CI **[0.999771, 1.000000]**; PROVEN against .50. Undefined resamples: 0/20,000. This association partly follows directly from the cost formula and does not establish causation.

Correctness audit: 40/40 outputs pass seven duration-parser examples, without changing inclusion. Reasoning tokens are recorded as null when not separately exposed by CLI; output tokens remain included once in cost. All calls use the default inherited account and fresh ephemeral sessions with the same model/reasoning. Raw streams and attempts ledger retained. Total estimated cost index $0.271702; actual subscription charges are not measured.

Two cacheable calls (blocks 11 and 18, zero-based) received 14,080 cached tokens instead of 12,288, halving their cost approximately; all nonce calls and the other 18 cacheable calls received 12,288. These two rare warmer-cache events widen the paired-ratio interval. All calls returned 163 output tokens and separately reported zero reasoning tokens. The observed paired-ratio variability exceeded the optimistic planning assumption; the planned sample could not resolve the threshold. No observations were removed.

The nonce begins the user prompt, not the full serialized request: the CLI's system prefix can still be cached. This experiment tests this prescribed cache-busting intervention, not a server-side cache-disable switch. Shared-account activity and provider routing can affect cache hits. No claim extends beyond this synthetic prompt and model configuration.

GPU: none; Colab CU consumed: **0**. No runtime created or stopped. Account-wide balance changed from 171.05 to 170.81 CU and two assignments appeared by the final usage check; these are not sessions started by this experiment and were left untouched. Experiment CU remains zero. Results were written locally after each call, so a runtime loss cannot erase prior batches. See `results/analysis.json`, `results/runs.csv`, `results/attempts.jsonl`, and `chart.png`. Reproduce with scripts in README; resume never reruns completed trial IDs.
