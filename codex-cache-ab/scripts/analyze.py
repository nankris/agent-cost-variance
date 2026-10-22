import csv,json,pathlib,subprocess,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parents[1]; D=R/'results'
rows={}
for line in (D/'attempts.jsonl').read_text().splitlines():
 r=json.loads(line)
 if r.get('status')!='completed' or not r['valid']: continue
 u=r['usage']; n=u['input_tokens']; c=u['cached_input_tokens']; o=u['output_tokens']
 r.update(input=n,cached_input=c,output=o,reasoning=u.get('reasoning_output_tokens',u.get('reasoning_tokens')),cache_share=c/n,cost=((n-c)*2+c*.1+o*10)/1e6)
 rows[r['id']]=r
rows=list(sorted(rows.values(),key=lambda r:r['id']))
fields=['id','block','arm','attempt','input','cached_input','output','reasoning','cache_share','cost']
with (D/'runs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
pairs=[]
for b in range(20):
 pair={r['arm']:r for r in rows if r['block']==b}
 if len(pair)==2:pairs.append(pair)
if not pairs:raise SystemExit('No complete pairs')
a=np.array([p['cacheable']['cost'] for p in pairs]);b=np.array([p['busted']['cost'] for p in pairs]); ratios=b/a
idx=np.random.default_rng(1012).integers(0,len(pairs),(20000,len(pairs)))
ci=np.quantile(ratios[idx].mean(axis=1),[.025,.975])
def verdict(ci,t):return 'PROVEN' if ci[0]>t else 'DISPROVEN' if ci[1]<t else 'STILL INCONCLUSIVE'
def r2(x,y):
 if np.ptp(x)==0 or np.ptp(y)==0:return float('nan')
 return float(np.corrcoef(x,y)[0,1]**2)
x=np.array([[p[s]['cache_share'] for s in ['cacheable','busted']] for p in pairs]);y=np.stack([a,b],axis=1)
r2est=r2(x.flatten(),y.flatten()); rng=np.random.default_rng(1013)
boot=np.array([r2(x[i].flatten(),y[i].flatten()) for i in rng.integers(0,len(pairs),(20000,len(pairs)))])
finite=boot[np.isfinite(boot)]; rci=np.quantile(finite,[.025,.975]) if len(finite) else [float('nan')]*2
v=verdict(ci,1.15) if len(pairs)==20 else 'STILL INCONCLUSIVE'
audit=[]
for row in rows:
 ev=[json.loads(s) for s in (D/(row['stem']+'.jsonl')).read_text().splitlines()]
 source='\n'.join(e['item']['text'] for e in ev if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message').strip()
 if source.startswith('```'):source='\n'.join(source.splitlines()[1:-1])
 test="\nfor(const [s,w] of [['1h30m',5400],['45m',2700],['2h',7200],['90s',90],['1h2m3s',3723],['0s',0],['',0]])if(module.exports.parseDuration(s)!==w)throw Error(s);"
 try: rc=subprocess.run(['node','-e',source+test],capture_output=True,text=True,timeout=5);audit.append(dict(id=row['id'],passes=rc.returncode==0,stderr=rc.stderr))
 except Exception as e:audit.append(dict(id=row['id'],passes=False,error=str(e)))
(D/'correctness.json').write_text(json.dumps(audit,indent=2))
stats=dict(n_calls=len(rows),n_pairs=len(pairs),ratio=float(ratios.mean()),ratio_ci=ci.tolist(),ratio_of_means=float(b.mean()/a.mean()),verdict=v,r2=r2est,r2_ci=list(rci),r2_undefined_bootstraps=int(20000-len(finite)),secondary_verdict=verdict(rci,.5),total_cost=sum(r['cost'] for r in rows),passed=sum(r['passes'] for r in audit))
(D/'analysis.json').write_text(json.dumps(stats,indent=2,allow_nan=True)+'\n')
fig,axs=plt.subplots(1,3,figsize=(13,4))
axs[0].plot(np.arange(len(pairs))+1,a*1000,'o-',label='Cacheable');axs[0].plot(np.arange(len(pairs))+1,b*1000,'s-',label='Nonce');axs[0].set(xlabel='Block',ylabel='Estimated cost (millidollars)');axs[0].legend()
axs[1].plot(np.arange(len(pairs))+1,ratios,'o');axs[1].axhline(1.15,color='red',ls='--');axs[1].axhspan(*ci,alpha=.15);axs[1].set(xlabel='Block',ylabel='Nonce / cacheable cost',title=f'Mean {ratios.mean():.3f}; 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]')
axs[2].scatter(x.flatten(),y.flatten()*1000);axs[2].set(xlabel='Cache-hit share',ylabel='Estimated cost (millidollars)',title=f'R²={r2est:.6f} [{rci[0]:.6f}, {rci[1]:.6f}]')
fig.suptitle(f'Randomized prompt nonce: {v} at 15% threshold');fig.tight_layout();fig.savefig(R/'chart.png',dpi=160);plt.close(fig)
summary=[]
for arm in ['cacheable','busted']:
 armrows=[r for r in rows if r['arm']==arm]
 summary.append('| '+arm+' | '+str(len(armrows))+' | '+' | '.join(f'{np.mean([r[k] for r in armrows]):.6f}' for k in ['input','cached_input','output','cache_share','cost'])+' |')
write=f'''# Randomized prompt nonce: results

Follow-up to [the original run](../codex-repeat-variance/), [the sequential re-test](../codex-variance-sequential/) and [the controlled re-test](../codex-variance-controlled/).

Primary verdict: **{v}** for a practically material (>15%) cost premium from prepending a nonce to this fixed user prompt.

| Arm | n | Mean input | Mean cached input | Mean output | Mean cache share | Mean cost index ($) |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(summary)+f'''

{len(pairs)}/20 complete randomized blocks. Mean paired busted/cacheable cost ratio **{ratios.mean():.6f}**, block-bootstrap 95% CI **[{ci[0]:.6f}, {ci[1]:.6f}]** (20,000 draws). Ratio of arm means {b.mean()/a.mean():.6f}. Fixed boundary 1.15; this verdict follows the preregistered CI rule. The prespecified 20-block (40-call) sample budget is exhausted; the CI crosses 1.15. Wall time and CU were not exhausted. Adding calls would violate the fixed design.

Secondary R² of cost on cache share: **{r2est:.6f}**, block-bootstrap 95% CI **[{rci[0]:.6f}, {rci[1]:.6f}]**; {stats['secondary_verdict']} against .50. Undefined resamples: {stats['r2_undefined_bootstraps']}/20,000. This association partly follows directly from the cost formula and does not establish causation.

Correctness audit: {stats['passed']}/{len(rows)} outputs pass seven duration-parser examples, without changing inclusion. Reasoning tokens are recorded as null when not separately exposed by CLI; output tokens remain included once in cost. All calls use the default inherited account and fresh ephemeral sessions with the same model/reasoning. Raw streams and attempts ledger retained. Total estimated cost index ${stats['total_cost']:.6f}; actual subscription charges are not measured.

Two cacheable calls (blocks 11 and 18, zero-based) received 14,080 cached tokens instead of 12,288, halving their cost approximately; all nonce calls and the other 18 cacheable calls received 12,288. These two rare warmer-cache events widen the paired-ratio interval. All calls returned 163 output tokens and separately reported zero reasoning tokens. The observed paired-ratio variability exceeded the optimistic planning assumption; the planned sample could not resolve the threshold. No observations were removed.

The nonce begins the user prompt, not the full serialized request: the CLI's system prefix can still be cached. This experiment tests this prescribed cache-busting intervention, not a server-side cache-disable switch. Shared-account activity and provider routing can affect cache hits. No claim extends beyond this synthetic prompt and model configuration.

GPU: none; Colab CU consumed: **0**. No runtime was created. Account-level usage changes seen in the final snapshot came from other work, not this experiment; experiment CU remains zero. Results were written locally after each call, so a runtime loss cannot erase prior batches. See `results/analysis.json`, `results/runs.csv`, `results/attempts.jsonl`, and `chart.png`. Reproduce with the scripts in the README; resume never reruns completed trial IDs.
'''
(R/'writeup.md').write_text(write)
print(json.dumps(stats,indent=2))
