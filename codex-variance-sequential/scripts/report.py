import json,pathlib,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import analyze,ROOT
rounds=[]
for p in sorted((ROOT/'results').glob('round[12].json')):
    rows=json.loads(p.read_text()); a=analyze(rows,p.stem=='round2'); rounds.append((p.stem,rows,a))
    (p.parent/(p.stem+'_analysis.json')).write_text(json.dumps(a,indent=2))
rows=[r for _,rs,_ in rounds for r in rs]
with (ROOT/'results'/'runs.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
fig,axs=plt.subplots(1,3,figsize=(13,4))
for name,rs,a in rounds:
    xs=np.arange(len(rs))+1
    axs[0].plot(xs,[r['cost']*100 for r in rs],'o-',label=name)
    for x,r in zip(xs,rs): axs[0].annotate('baseline' if r['gap_min'] is None else str(r['gap_min'])+'m',(x,r['cost']*100),xytext=(0,8),textcoords='offset points',fontsize=8)
    axs[1].scatter([r['gap_min'] for r in rs if r['gap_min'] is not None],[r['cache_share']*100 for r in rs if r['gap_min'] is not None],label=name)
    axs[2].scatter([r['cache_share']*100 for r in rs],[r['cost']*100 for r in rs],label=name)
axs[0].set(xlabel='Run order (labels: preceding gap)',ylabel='API-equivalent cost (cents)')
axs[1].set(xlabel='Idle gap (minutes)',ylabel='Cached input (%)')
axs[2].set(xlabel='Cached input (%)',ylabel='API-equivalent cost (cents)')
for ax in axs: ax.grid(alpha=.2); ax.legend()
fig.suptitle('Strictly sequential fixed-task repetitions'); fig.tight_layout(); fig.savefig(ROOT/'chart.png',dpi=160)
text='# Sequential Codex timing/cache variance\n\n'
for name,rs,a in rounds:
    text+=f'## {name}: {a["verdict"]}\n\n'
    text+='| Run | Gap min | Input | Cached | Uncached | Output | Cache % | Cost cents | Pass |\n|---|---|---|---|---|---|---|---|---|\n'
    for r in rs:
        text+=f'| {r["run"]} | {r["gap_min"]} | {r["input_tokens"]} | {r["cached_input_tokens"]} | {r["uncached_input_tokens"]} | {r["output_tokens"]} | {100*r["cache_share"]:.1f} | {100*r["cost"]:.3f} | {r["passed"]} |\n'
    d,lo,hi=a['cost_difference_ci']; cd,cl,ch=a['cache_difference_ci']
    text+=f'\nLong-minus-short cost: {100*d:.3f} cents, bootstrap 95% CI [{100*lo:.3f}, {100*hi:.3f}]. Cache share difference: {100*cd:.2f} percentage points, 95% CI [{100*cl:.2f}, {100*ch:.2f}]. Equivalence margin: ±{100*a["equivalence_margin"]:.3f} cents. Cache normalization changes variance by {100*a["cache_variance_reduction"]:.1f}% reduction.\n\n'
text+=f'Final verdict: **{rounds[-1][2]["verdict"]}**. '
text+='Two rounds are the preregistered maximum.\n\n' if len(rounds)==2 else 'The round-one rule settled the specified hypothesis.\n\n'
text+='![Results](chart.png)\n\nCosts use the original frozen price weights and are not measured billing. Confidence intervals are exploratory percentile bootstrap intervals from few repetitions; dependence through cache history limits causal inference. Fixed path and low reasoning effort differ from the original, deliberately reducing avoidable variability. This agent kept child runs sequential; exclusive account access is not established. Common prompt prefixes may be warmed by other account traffic. Cache-normalized variance is accounting attribution, not a random-cache mechanism test. One task cannot establish behavior for longer or harder tasks. GPU: none. Experiment Colab CU: 0; no session allocated.\n'
(ROOT/'writeup.md').write_text(text)
print(json.dumps(rounds[-1][2]))
