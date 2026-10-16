import json,pathlib,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import verdict
R=pathlib.Path(__file__).resolve().parent
rows=[json.loads(s) for s in (R/'results/runs.jsonl').read_text().splitlines()]
valid=[r for r in rows if r.get('usage') and r['exit_code']==0 and r['passed'] and r['run']>0]
table=['|Round|Run|Gap (min)|Actual gap (s)|Cached|Uncached|Output|Cache %|Est. cost|Pass|','|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    if r.get('usage'):
        table.append(f"|{r['round']}|{r['run']}|{r['gap_min']}|{r['actual_gap_s'] if r['actual_gap_s'] is not None else 'baseline'}|{r['cached_input_tokens']}|{r['uncached_input_tokens']}|{r['output_tokens']}|{100*r['cache_share']:.2f}|${r['cost']:.5f}|{r['passed']}|")
    else:table.append(f"|{r['round']}|{r['run']}|{r['gap_min']}|—|—|—|—|—|—|False|")
lines=['# Sequential Codex timing/cache rerun','',*table,'']
summary={}
costs=lambda rs:np.array([r['cost'] for r in rs])
for round_ in sorted(set(r['round'] for r in rows)):
    rr=[r for r in valid if r['round']==round_]
    short=[r for r in rr if r['gap_min'] in (0,1) and r['actual_gap_s'] is not None]
    long=[r for r in rr if r['gap_min'] in (5,15)]
    complete = len(rr)==(10 if round_==1 else 16)
    v=verdict(rr) if complete else 'STILL INCONCLUSIVE'
    info={'verdict':v,'n':len(rr),'complete':complete}
    lines += [f'## Round {round_}',f'Valid scored trials: {len(rr)}. Complete scheduled round: {complete}. Verdict: **{v}**.']
    if len(short)>=2 and len(long)>=2:
        rng=np.random.default_rng(1010)
        a=rng.integers(len(short),size=(50000,len(short))); b=rng.integers(len(long),size=(50000,len(long)))
        costs=lambda rs:np.array([r['cost'] for r in rs])
        cache=lambda rs:np.array([r['cache_share'] for r in rs])
        ratios=costs(long)[b].mean(1)/costs(short)[a].mean(1)
        diffs=cache(long)[b].mean(1)-cache(short)[a].mean(1)
        info.update(cost_ratio=costs(long).mean()/costs(short).mean(),cost_ratio_ci=np.quantile(ratios,[.025,.975]).tolist(),cache_difference=cache(long).mean()-cache(short).mean(),cache_difference_ci=np.quantile(diffs,[.025,.975]).tolist())
        lines += [f"Long/short mean cost ratio: {info['cost_ratio']:.3f}, 95% bootstrap CI {info['cost_ratio_ci']}. Long − short cache share: {100*info['cache_difference']:.2f} percentage points, 95% CI {[100*x for x in info['cache_difference_ci']]}. Short n={len(short)}, long n={len(long)}."]
    elif short or long:
        lines += ['Timing-effect CI not estimable reliably: fewer than two observations in at least one timing group.']
    if len(rr)>1:
        def reduction(rs):
            inp=np.array([r['input_tokens'] for r in rs]); ca=np.array([r['cached_input_tokens'] for r in rs]); out=np.array([r['output_tokens'] for r in rs]); co=costs(rs)
            share=ca.sum()/inp.sum(); cf=(inp*(2-1.9*share)+out*10)/1e6
            return 1-np.var(cf)/np.var(co) if np.var(co)>0 else float('nan')
        rng=np.random.default_rng(1011)
        red=[reduction([rr[i] for i in ix]) for ix in rng.integers(len(rr),size=(50000,len(rr)))]
        ci=np.nanquantile(red,[.025,.975]); info.update(cache_variance_reduction=reduction(rr),cache_variance_reduction_ci=ci.tolist(),cost_spread=max(r['cost'] for r in rr)/min(r['cost'] for r in rr))
        lines += [f"Cost max/min: {info['cost_spread']:.3f}×. Cache-normalized variance reduction: {reduction(rr):.3f}, 95% bootstrap CI {ci.tolist()}. Cache accounting explains most variance by the secondary rule: {bool(ci[0]>.5)}."]
    summary[str(round_)]=info
    lines+=['']
final=list(summary.values())[-1]['verdict']
lines += ['95% CIs are percentile bootstrap intervals with 50,000 resamples (seed 1010; variance accounting seed 1011). Warm-up runs 0 and -1 are excluded from all scored statistics. Missing timing arms have no estimable CI.', '', f'Final verdict: **{final}**.','', 'Interpretation: fixed task, fixed path and fresh sessions reduce local concurrency and changing-path confounds, but the interruption and five accidental low-effort trials limit causal interpretation. Other users of the account and provider routing/cache state remain uncontrolled. These data cannot establish the cause of the original historical spread. Timing groups have few observations; percentile bootstrap intervals are exploratory and conditional on these trials. Round 1 was interrupted after four trials; round 2 is the single allowed redesign, using 16 balanced trials. Round 2 was interrupted after seven scored trials and resumed after an excluded warm-up (-1), then interrupted again after run 9. Run 10 has an extended gap of 48.4 minutes rather than 15; the final run 16 retry also has an extended gap. Sensitivity analysis excludes extended gaps. The original run 16 failed at the subscription limit and is preserved, without scoring it. Five accidental low-effort trials are preserved separately and excluded. Earlier first-round usage files were reconstructed from canonical runs.jsonl after accidental overwrite. See README for the deviation record. Round 1 intervals describe its incomplete subset only and do not establish a verdict. Other account activity was observed, so this is not an isolated-account experiment. Dollar values are estimates using the original experiment’s fixed token weights, not actual Plus charges.', '', 'GPU: none. Experiment CU used: **0**. No Colab session created; before/after usage snapshots are account-level and can include others. All task data are synthetic.']
(R/'writeup.md').write_text('\n'.join(lines)+'\n')
(R/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
fig,axs=plt.subplots(1,3,figsize=(13,4))
for round_ in sorted(set(r['round'] for r in valid)):
    rr=[r for r in valid if r['round']==round_]
    x=np.arange(len(rr))+1
    axs[0].plot(x,[100*r['cache_share'] for r in rr],'o-',label=f'Round {round_}')
    axs[1].plot(x,[100*r['cost'] for r in rr],'o-',label=f'Round {round_}')
    for gap in [0,1,5,15]:
        g=[r for r in rr if r['gap_min']==gap]
        axs[2].scatter([gap]*len(g),[100*r['cost'] for r in g],alpha=.7)
axs[0].set(xlabel='Sequential run',ylabel='Cached input (%)'); axs[1].set(xlabel='Sequential run',ylabel='Estimated cost (cents)');axs[2].set(xlabel='Assigned gap (minutes)',ylabel='Estimated cost (cents)',xticks=[0,1,5,15])
for ax in axs:ax.grid(alpha=.2)
if valid:axs[0].legend()
fig.suptitle('010r: fixed task, sequential Codex sessions — '+final);fig.tight_layout();fig.savefig(R/'chart.png',dpi=180)
print(json.dumps(summary,indent=2))

# Publish usage events only; full historical streams remain local and untracked.
public=R/'results'/'usage-only'
public.mkdir(exist_ok=True)
for row in rows:
    if row.get('usage'):
        target=public/f"r{row['round']}_{row['run']:02d}.jsonl"
        target.write_text(json.dumps({'type':'turn.completed','usage':row['usage']})+'\n')
fields=['round','run','gap_min','actual_gap_s','wall_s','exit_code','passed','input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens','cache_share','cost']
with (R/'results'/'runs.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
