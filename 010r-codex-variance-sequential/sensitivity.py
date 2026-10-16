"""Descriptive interruption sensitivity; does not replace the original decision rule."""
import json,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parent
rows=[json.loads(s) for s in (R/'results/runs.jsonl').read_text().splitlines()]
rr=[r for r in rows if r['round']==2 and r['run']>0 and r.get('usage')]
rng=np.random.default_rng(1010); B=50000
out={}
for name,rs in [('segment_1',[r for r in rr if r['run']<=7]),('segment_2',[r for r in rr if 8<=r['run']<=9]),('segment_3',[r for r in rr if r['run']>=11]),('exclude_extended_gap',[r for r in rr if r['actual_gap_s'] <= r['gap_min']*60+5])]:
    s=[r for r in rs if r['gap_min']<=1]; l=[r for r in rs if r['gap_min']>=5]
    if not s or not l: continue
    def boot(group,key):
        x=np.array([r[key] for r in group]); return x[rng.integers(len(x),size=(B,len(x)))].mean(1)
    lc=boot(l,'cost');sc=boot(s,'cost');ld=boot(l,'cache_share');sd=boot(s,'cache_share')
    out[name]={'n':len(rs),'ratio':np.mean([r['cost'] for r in l])/np.mean([r['cost'] for r in s]),'ratio_ci':np.quantile(lc/sc,[.025,.975]).tolist(),'cache_difference_ci':np.quantile(ld-sd,[.025,.975]).tolist()}
(R/'results/sensitivity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
