# 010r: sequential Codex timing/cache rerun

## Hypothesis and decision rule
Hypothesis: long idle gaps (5/15 minutes) produce colder cache and materially higher estimated cost than short gaps (0/1 minute) on one fixed task.
The existing runner and interrupted writeup establish the original rule: PROVEN if the bootstrap 95% CI of long/short mean cost lies entirely above 1.10 AND long-minus-short cache share CI lies below zero; DISPROVEN if the cost-ratio CI lies entirely in [0.90, 1.10]; otherwise STILL INCONCLUSIVE. Bootstrap: 50,000 resamples, seed 1010, resampling independently within timing groups. Cache-accounting secondary rule: pooled-cache-share normalization reduces cost variance by >50%, with bootstrap lower bound >50% (seed 1011).
A complete round is required for a verdict. Incomplete rounds remain inconclusive regardless of intervals. This README reconstructs the earlier rule from preserved run.py/analyze.py; the earlier README was inadvertently overwritten on resumption. The reconstruction and new completion schedule are recorded before further launches.

## Existing experiment and resumption
Original untouched: ../010-codex-repeat-variance. Synthetic N02_duration task copied here. Fixed model gpt-6.1-sol, medium reasoning, identical prompt, fixed working path reset from fixture, fresh CLI sessions, sequential trials. Usage comes from --json turn.completed.usage, including cached and uncached input. Cost estimates use original frozen weights: $2/M uncached, $0.10/M cached, $10/M output; not actual billing.
Round 1 schedule: baseline,0,15,1,5,0,5,1,15,0; interrupted after four completed trials.
Round 2 single redesign: excluded warm-up plus 16 balanced trials, gaps [15,0,5,1,1,5,0,15,5,15,1,0,0,1,15,5]. Seven scored trials and warm-up already existed when this turn began. Complete remaining trials 8–16, never launch another redesigned round. Because of the interruption, restart with an excluded warm-up numbered -1; all nine remaining assigned gaps are measured from an actual preceding trial completion. Analyze round 2 with and without interruption segment stratification as a sensitivity check. Completion is the same second round, not a new design.

## Protocol deviation, preserved evidence
Destination already contained an interrupted attempt. This was discovered after five additional low-effort trials had been run; those trials are preserved under additional_attempt and excluded from the confirmatory second-round analysis because their configuration differed. No concurrent child task was found. They warmed account prefixes, so causal isolation is weakened. The destination was not genuinely new at this turn's start. The accidentally overwritten first four raw usage files are reconstructed from the preserved canonical results/runs.jsonl, explicitly identified as reconstructed; no full raw content is claimed for them. Earlier run.py and analyze.py, raw second-round usage, logs and canonical results are retained. No historical data is silently pooled with the extra trials. Two planned rounds maximum; no third designed round will be run.

## Compute and environment
GPU: none. Experiment CU: 0. No Colab session created; other people's sessions untouched.
This turn's before usage: balance 181.82 CU, rate 3.08/h, two existing assignments. Earlier before snapshots are in results. Global balance changes are others' usage, not experiment CU.
Cloud runtime skill read; environment_status tool and /etc/codex/network-policy.json unavailable. Existing CLI authentication used without inspecting secrets.
Run: source /workspace/tools/setup.sh; python3 finish_round2.py. Analyze: /workspace/tools/mlenv/bin/python analyze.py.

## Second resumption (2026-10-15)
No surviving trial driver exists. Round 2 has scored runs 1–9. Complete runs 10–16 with the already assigned gaps [15,1,0,0,1,15,5]; the first gap is measured from run 9's recorded wall-clock end, translated to monotonic time. A process interruption can make this gap longer than assigned; record the actual gap and report this deviation. No additional round or configuration change. Before balance: 180.02 CU; active Colab assignments: zero. GPU none, 0 CU. Official JSON event reference: https://developers.openai.com/codex/noninteractive/ .

## Artifact handling
The committed results/usage-only files retain only each --json turn.completed usage event; results/runs.jsonl and runs.csv retain the trial metrics. Full historical event streams, old driver logs and accidental additional_attempt remain on disk but are excluded from the commit to avoid exporting unrelated context. Earlier reconstructed usage records remain explicitly labeled in this README. The original directory is untouched. Cache normalization is an accounting counterfactual (fix cache share while retaining input/output volume), not independent evidence that elapsed time caused cache misses.

## Final resumption
Resume from 14 completed scored second-round trials. Finish only assigned runs 15 (15 minutes) and 16 (5 minutes), with the existing hypothesis and decision rule unchanged. Measure run 15 from recorded run 14 completion; any excess idle time is a protocol deviation, and sensitivity excludes every assigned gap exceeded by more than 5 seconds. Before account balance 179.58 CU, two unrelated active assignments; this experiment creates no Colab sessions and uses 0 CU. Other experiment processes are active, so account isolation cannot be claimed.

Final-resumption run 15 achieved 900.20 seconds idle (assigned 900); it is not an extended-gap deviation. Only run 10 currently exceeds its assigned idle gap by more than five seconds. Historical results/round1.json belongs to the excluded additional attempt and is not the canonical first round; analysis uses results/runs.jsonl exclusively.

## Final failed-trial recovery (2026-10-15 06:49 UTC)
Run 16 failed without usage at the subscription limit; 15 valid second-round trials exist. Retry only that failed trial once, using the same task/configuration and measuring actual idle time from run 15. The long interruption exceeds the assigned five-minute gap, so the existing sensitivity rule excludes this retry. Preserve the failed record and its raw usage file under a failure-specific name before retrying. This is completion of round 2, with no third round or change to the decision rule. Failure records are not scored; complete-round checks count unique successful run IDs. GPU none; experiment CU remains 0.

Final recovery: run 16 passed with 11,974.05 seconds actual idle (199.57 minutes), rather than five minutes. Exclude runs 10 and 16 in the predefined extended-gap sensitivity. Both failed and successful run-16 records remain in runs.jsonl; only the successful record is scored. Before and after account balance: 178.36 CU; after rate 3.08 CU/h with two unrelated assignments. No experiment session was created, so none requires stopping. GPU none, experiment CU 0. The initial recovery command lacked codex on PATH and launched no model; sourcing setup.sh resolved this.
