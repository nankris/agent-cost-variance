# Sequential Codex timing/cache re-test

This is a follow-up re-test of [the original run](../codex-repeat-variance/).

|Round|Run|Gap (min)|Actual gap (s)|Cached|Uncached|Output|Cache %|Est. cost|Pass|
|---|---|---|---|---|---|---|---|---|---|
|1|1|None|baseline|74496|15477|423|82.80|$0.04263|True|
|1|2|0|0.13152554499998814|70784|11281|423|86.25|$0.03387|True|
|1|3|15|900.114599902|69504|10758|422|86.60|$0.03269|True|
|1|4|1|60.010967028000096|69120|12940|418|84.23|$0.03697|True|
|2|0|None|baseline|59520|22545|421|72.53|$0.05525|True|
|2|1|15|900.0121906960001|59776|20380|400|74.57|$0.05074|True|
|2|2|0|0.06020324300016|93312|11479|465|89.05|$0.03694|True|
|2|3|5|300.017011057|74496|15483|434|82.79|$0.04276|True|
|2|4|1|60.01791438600003|61440|12948|326|82.59|$0.03530|True|
|2|5|1|60.03223921799986|62336|10796|426|85.24|$0.03209|True|
|2|6|5|300.02596824700004|68480|21457|403|76.14|$0.05379|True|
|2|7|0|0.051056379000101515|69760|10718|426|86.68|$0.03267|True|
|2|-1|None|baseline|72960|16196|572|81.83|$0.04541|True|
|2|8|15|900.072441695|74624|15516|475|82.79|$0.04324|True|
|2|9|5|300.0163067829999|59776|20596|419|74.37|$0.05136|True|
|2|10|15|2906.227817486894|74496|15429|403|82.84|$0.04234|True|
|2|11|1|60.025856202999876|62208|27793|453|69.12|$0.06634|True|
|2|12|0|0.2719906269999228|68480|21437|395|76.16|$0.05367|True|
|2|13|0|0.20687301499992827|79360|10608|412|88.21|$0.03327|True|
|2|14|1|60.16978751199986|74624|15609|518|82.70|$0.04386|True|
|2|15|15|900.1982910409338|95744|20624|415|82.28|$0.05497|True|
|2|16|5|—|—|—|—|—|—|False|
|2|16|5|11974.052042154344|93440|11669|470|88.90|$0.03738|True|

## Round 1
Valid scored trials: 4. Complete scheduled round: False. Verdict: **STILL INCONCLUSIVE**.
Timing-effect CI not estimable reliably: fewer than two observations in at least one timing group.
Cost max/min: 1.304×. Cache-normalized variance reduction: 0.856, 95% bootstrap CI [0.6551356479340054, 0.999719975372417]. Cache accounting explains most variance by the secondary rule: True.

## Round 2
Valid scored trials: 16. Complete scheduled round: True. Verdict: **STILL INCONCLUSIVE**.
Long/short mean cost ratio: 1.127, 95% bootstrap CI [0.9153339467938104, 1.3820462444660213]. Long − short cache share: -1.88 percentage points, 95% CI [-7.097659491653649, 3.7596569234940405]. Short n=8, long n=8.
Cost max/min: 2.067×. Cache-normalized variance reduction: 0.714, 95% bootstrap CI [0.3787381157642637, 0.9021641072909433]. Cache accounting explains most variance by the secondary rule: False.

95% CIs are percentile bootstrap intervals with 50,000 resamples (seed 1010; variance accounting seed 1011). Warm-up runs 0 and -1 are excluded from all scored statistics. Missing timing arms have no estimable CI.

Final verdict: **STILL INCONCLUSIVE**.

Interpretation: fixed task, fixed path and fresh sessions reduce local concurrency and changing-path confounds, but the interruption and five accidental low-effort trials limit causal interpretation. Other users of the account and provider routing/cache state remain uncontrolled. These data cannot establish the cause of the original historical spread. Timing groups have few observations; percentile bootstrap intervals are exploratory and conditional on these trials. Round 1 was interrupted after four trials; round 2 is the single allowed redesign, using 16 balanced trials. Round 2 was interrupted after seven scored trials and resumed after an excluded warm-up (-1), then interrupted again after run 9. Run 10 has an extended gap of 48.4 minutes rather than 15; the final run 16 retry also has an extended gap. Sensitivity analysis excludes extended gaps. The original run 16 failed at the subscription limit and is preserved, without scoring it. Five accidental low-effort trials are preserved separately and excluded. Earlier first-round usage files were reconstructed from canonical runs.jsonl after accidental overwrite. See the README for the deviation record. Round 1 intervals describe its incomplete subset only and do not establish a verdict. Other account activity was observed, so this is not an isolated-account experiment. Dollar values are estimates using the original experiment’s fixed token weights, not actual Plus charges.

GPU: none. Experiment CU used: **0**. No Colab session created; before/after usage snapshots are account-level and can include others. All task data are synthetic.

## Second-round timing groups

|Gap (min)|n|Mean estimated cost|95% bootstrap CI|Mean cached input|
|---|---:|---:|---|---:|
|0|4|$0.03914|[$0.03297, $0.04857]|85.02%|
|1|4|$0.04440|[$0.03369, $0.05858]|79.91%|
|5|4|$0.04632|[$0.04007, $0.05258]|80.55%|
|15|4|$0.04782|[$0.04279, $0.05285]|80.62%|

Per-gap intervals are descriptive percentile bootstraps (50,000 resamples, seed 1012). The 15-minute group includes the documented 48.4-minute restart gap; the final five-minute retry also has an extended interruption gap. Two interrupted rounds were attempted; the second was attempted across resumptions; see the complete-round status above. No third round was launched.

Cache-normalized variance reduction measures the effect of replacing every observed cache share with the pooled share in the price formula. This accounting calculation does not prove timing, account concurrency, or provider routing caused the cache variation.

Interruption sensitivity (descriptive; see results/sensitivity.json):
- segment_1: n=7, long/short cost ratio 1.433, 95% CI [1.257, 1.597].
- segment_3: n=6, long/short cost ratio 0.937, 95% CI [0.650, 1.340].
- exclude_extended_gap: n=14, long/short cost ratio 1.185, 95% CI [0.963, 1.447].
