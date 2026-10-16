import json,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
def analyze(rows, paired=False):
    rows=[r for r in rows if r['gap_min'] is not None]
    short=[r for r in rows if r['gap_min']<=1]; long=[r for r in rows if r['gap_min']>=5]
    rng=np.random.default_rng(1010)
    def ci(key):
        a=np.array([r[key] for r in short]); b=np.array([r[key] for r in long])
        if paired:
            diffs=np.array([next(r[key] for r in rows[i:i+2] if r['gap_min']==15)-next(r[key] for r in rows[i:i+2] if r['gap_min']==0) for i in range(0,len(rows),2)])
            boot=diffs[rng.integers(len(diffs),size=(100000,len(diffs)))].mean(1)
        else: boot=b[rng.integers(len(b),size=(100000,len(b)))].mean(1)-a[rng.integers(len(a),size=(100000,len(a)))].mean(1)
        return [float(b.mean()-a.mean()),*map(float,np.quantile(boot,[.025,.975]))]
    cost=ci('cost'); cache=ci('cache_share'); margin=.2*np.mean([r['cost'] for r in short])
    allrows=rows
    shares=sum(r['cached_input_tokens'] for r in allrows)/sum(r['input_tokens'] for r in allrows)
    actual=np.array([r['cost'] for r in allrows]); fixed=np.array([(r['input_tokens']*(2-1.9*shares)+10*r['output_tokens'])/1e6 for r in allrows])
    reduction=1-float(np.var(fixed)/np.var(actual))
    supported=cost[1]>0 and cache[2]<0
    absent=cost[1]>-margin and cost[2]<margin
    reverse=cost[2]<0 and cache[1]>0
    verdict='PROVEN' if supported and reduction>=.5 else 'DISPROVEN' if absent or reverse else 'STILL INCONCLUSIVE'
    return dict(verdict=verdict,cost_difference_ci=cost,cache_difference_ci=cache,equivalence_margin=margin,cache_variance_reduction=reduction,n_short=len(short),n_long=len(long))
if __name__=='__main__':
    for p in sorted((ROOT/'results').glob('round[12].json')):
        a=analyze(json.loads(p.read_text()),p.stem=='round2'); print(p.stem,json.dumps(a)); (p.parent/(p.stem+'_analysis.json')).write_text(json.dumps(a,indent=2))
