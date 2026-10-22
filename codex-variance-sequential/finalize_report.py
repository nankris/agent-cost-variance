import json,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parent
rows=[json.loads(s) for s in (R/'results/runs.jsonl').read_text().splitlines()]
rr=[r for r in rows if r['round']==2 and r['run']>0 and r.get('usage') and r['passed']]
text=['\n## Second-round timing groups','', '|Gap (min)|n|Mean estimated cost|95% bootstrap CI|Mean cached input|', '|---|---:|---:|---|---:|']
rng=np.random.default_rng(1012)
for gap in [0,1,5,15]:
    g=[r for r in rr if r['gap_min']==gap]
    if not g: continue
    x=np.array([r['cost'] for r in g]); v=x[rng.integers(len(x),size=(50000,len(x)))].mean(1);lo,hi=np.quantile(v,[.025,.975])
    text.append(f"|{gap}|{len(g)}|${x.mean():.5f}|[${lo:.5f}, ${hi:.5f}]|{100*np.mean([r['cache_share'] for r in g]):.2f}%|")
text+=['', 'Per-gap intervals are descriptive percentile bootstraps (50,000 resamples, seed 1012). The 15-minute group includes the documented 48.4-minute restart gap; the final five-minute retry also has an extended interruption gap. Two interrupted rounds were attempted; the second was attempted across resumptions; see the complete-round status above. No third round was launched.', '', 'Cache-normalized variance reduction measures the effect of replacing every observed cache share with the pooled share in the price formula. This accounting calculation does not prove timing, account concurrency, or provider routing caused the cache variation.', '', 'Interruption sensitivity (descriptive; see results/sensitivity.json):']
s=json.loads((R/'results/sensitivity.json').read_text())
for name,x in s.items():
    text.append(f"- {name}: n={x['n']}, long/short cost ratio {x['ratio']:.3f}, 95% CI [{x['ratio_ci'][0]:.3f}, {x['ratio_ci'][1]:.3f}].")
with (R/'writeup.md').open('a') as f:f.write('\n'.join(text)+'\n')
