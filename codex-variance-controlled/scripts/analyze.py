"""Regenerate preregistered analysis and report from append-only local ledger."""
import csv,json,pathlib,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parents[1]; D=R/'results'
p=D/'attempts.jsonl'
allrows=[json.loads(s) for s in p.read_text().splitlines()] if p.exists() else []
rows=sorted({r['id']:r for r in allrows if r['valid'] and r['id']>=0}.values(),key=lambda r:r['id'])
complete=len(rows)==24
pending='PENDING (execution in progress)' if not complete else 'STILL INCONCLUSIVE (fixed sample/time budget exhausted)'
res={'n':len(rows),'complete':complete,'timing_verdict':pending,'cache_verdict':pending,'gpu':'none','CU_used':0}
fig,axs=plt.subplots(1,3,figsize=(14,4))
if rows:
 x=np.array([r['cache_share'] for r in rows]); y=np.array([r['cost'] for r in rows])
 axs[0].scatter(x*100,y*1000,c=[0 if r['arm']=='short' else 1 for r in rows],cmap='coolwarm'); axs[0].set(xlabel='Cached input (%)',ylabel='Cost index (millidollars)')
 axs[1].plot([r['id']+1 for r in rows],y*1000,'k-',alpha=.3)
 for arm,color in [('short','tab:blue'),('spaced','tab:red')]:
  rr=[r for r in rows if r['arm']==arm]; v=np.array([r['cost'] for r in rr])
  if not len(v):continue
  axs[1].scatter([r['id']+1 for r in rr],v*1000,color=color,label=arm)
  g=np.random.default_rng(101006+(arm=='spaced')); ci=np.quantile(v[g.integers(len(v),size=(50000,len(v)))].mean(1),[.025,.975])
  res[arm]={'n':len(v),'mean_cost':float(v.mean()),'mean_cost_CI95':ci.tolist(),'mean_cache_share':float(np.mean([r['cache_share'] for r in rr])),'log_cost_SD':float(np.std(np.log(v),ddof=1)) if len(v)>1 else None,'gap_min_s':min(r['gap_s'] for r in rr),'gap_max_s':max(r['gap_s'] for r in rr)}
 axs[1].set(xlabel='Trial order',ylabel='Cost index (millidollars)'); axs[1].legend()
 a=np.array([r['cost'] for r in rows if r['arm']=='short']); b=np.array([r['cost'] for r in rows if r['arm']=='spaced'])
 if len(a)>1 and len(b)>1:
  g=np.random.default_rng(101004); ratios=b[g.integers(len(b),size=(50000,len(b)))].mean(1)/a[g.integers(len(a),size=(50000,len(a)))].mean(1)
  lo,hi=np.quantile(ratios,[.025,.975]); el,eh=np.quantile(ratios,[.05,.95])
  v='DISPROVEN (equivalent within 10%)' if el>.9 and eh<1.1 else 'PROVEN' if hi<1 or lo>1 else pending
  res.update(ratio=float(b.mean()/a.mean()),ratio_CI95=[float(lo),float(hi)],ratio_CI90=[float(el),float(eh)],timing_verdict=v if complete else pending)
  axs[2].plot([0,0],[lo,hi],color='k');axs[2].scatter([0],[res['ratio']],color='k'); axs[2].axhspan(.9,1.1,alpha=.2);axs[2].axhline(1,color='grey',linestyle='--');axs[2].set(xticks=[],ylabel='Spaced / short mean cost',title='95% bootstrap CI; 10% margin')
 def r2(xx,yy):
  if np.std(xx)==0 or np.std(yy)==0:return float('nan')
  return float(np.corrcoef(xx,yy)[0,1]**2)
 if len(rows)>3:
  g=np.random.default_rng(101005); indices=g.integers(len(rows),size=(50000,len(rows))); bs=np.array([r2(x[k],y[k]) for k in indices]); finite=bs[np.isfinite(bs)]
  if len(finite)==len(bs):
   lo,hi=np.quantile(finite,[.025,.975]); res.update(R2=r2(x,y),R2_CI95=[float(lo),float(hi)],cache_verdict=('PROVEN' if lo>.5 else 'DISPROVEN (R² below 0.50)' if hi<.5 else pending) if complete else pending)
  else: res.update(R2=r2(x,y),undefined_bootstrap_replicates=int((~np.isfinite(bs)).sum()),cache_verdict=pending)
 if len(rows)>4:
  design=np.column_stack([np.ones(len(rows)),x,[r['input'] for r in rows],[r['output'] for r in rows]])
  coef=np.linalg.lstsq(design,y,rcond=None)[0]; pred=design@coef
  res['descriptive_adjusted_regression']={'columns':['intercept','cache_share','input_tokens','output_tokens'],'coefficients':coef.tolist(),'R2':float(1-np.sum((y-pred)**2)/np.sum((y-y.mean())**2)) if np.var(y)>0 else None}
 res['cost_max_min']=float(y.max()/y.min());res['cost_index_total']=float(sum(r.get('cost',0) for r in allrows))
else:
 for ax in axs:ax.axis('off')
fig.suptitle(f'Controlled Codex variance: {len(rows)}/24 trials'+(' (complete)' if complete else ' (in progress)'))
fig.tight_layout();fig.savefig(R/'chart.png',dpi=160);plt.close(fig)
res['overall_verdict']=('DISPROVEN' if any(res[k].startswith('DISPROVEN') for k in ['timing_verdict','cache_verdict']) else 'PROVEN' if all(res[k]=='PROVEN' for k in ['timing_verdict','cache_verdict']) else pending) if complete else pending
(D/'analysis.json').write_text(json.dumps(res,indent=2)+'\n')
if rows:
 fields=['id','arm','attempt','start','end','gap_s','input','cached','output','cache_share','cost','valid']
 with (D/'runs.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
lines=['# Controlled Codex variance','','Follow-up to [the original run](../codex-repeat-variance/) and [the sequential re-test](../codex-variance-sequential/).','',f"Overall verdict: **{res['overall_verdict']}**. Completed {len(rows)}/24 preregistered scored trials.",'','|Arm|n|Mean cost index|95% bootstrap CI|Mean cached input|','|---|---:|---:|---|---:|']
for arm in ['short','spaced']:
 if arm not in res:continue
 z=res[arm];lines.append(f"|{arm}|{z['n']}|${z['mean_cost']:.6f}|[{z['mean_cost_CI95'][0]:.6f}, {z['mean_cost_CI95'][1]:.6f}]|{z['mean_cache_share']:.2%}|")
lines+=['','|Hypothesis|Estimate and intervals|Verdict|','|---|---|---|']
if 'ratio' in res:lines.append(f"|Spacing changes mean cost|Ratio {res['ratio']:.4f}; 95% CI {res['ratio_CI95']}; 90% CI {res['ratio_CI90']}|{res['timing_verdict']}|")
if 'R2' in res:lines.append(f"|Cache share explains R² > .50|R² {res['R2']:.4f}; 95% CI {res.get('R2_CI95','undefined bootstrap replicates')}|{res['cache_verdict']}|")
lines+=['','Decision rules were committed before the first call. The timing rule tests superiority with a 95% percentile bootstrap interval excluding 1, and equivalence with a 90% interval wholly inside [0.90, 1.10]; equivalence takes priority. Cache-share R² uses a 95% pairs-bootstrap interval against .50. Each uses 50,000 resamples and the preregistered seeds. Arm-mean intervals are descriptive. No significance-based stopping or retrospective margin changes.','', 'Twelve blocks each contain one short and one spaced trial, with seeded randomized order. Warm-ups and invalid attempts remain in attempts.jsonl and raw event logs, excluded from inference. Per-attempt results are written locally and the ledger fsynced immediately. See runs.csv for timestamps, gaps, and token counts.','', 'Prices are frozen accounting weights ($2/M uncached input, $0.10/M cached input, $10/M output), not current price claims or actual subscription charges. Cache/cost association is partly built into that formula and does not establish causation. Other account activity and provider routing remain uncontrolled. Independent-trial bootstrap intervals may understate uncertainty if sequential dependence persists. Inference applies to this fixed source-output task, not the earlier tool-using repair workflow or long agent sessions. With only 12 observations per arm, precision can remain inadequate if task variance exceeds the .08 log-SD planning assumption.','', 'GPU: none. Experiment CU used: **0**. Hosted Codex CLI on the inherited default account; no Colab session created and none stopped. Public/synthetic fixture only.']
if complete:
 lines+=['',f"All 24 trials completed. Short gaps {res['short']['gap_min_s']:.3f}–{res['short']['gap_max_s']:.3f}s; spaced gaps {res['spaced']['gap_min_s']:.3f}–{res['spaced']['gap_max_s']:.3f}s. Cost max/min {res['cost_max_min']:.3f}×. Observed within-arm log-cost SD: short {res['short']['log_cost_SD']:.4f}, spaced {res['spaced']['log_cost_SD']:.4f}."]
(R/'writeup.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(res,indent=2))
