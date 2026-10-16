import csv, statistics as S, os
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cc = list(csv.DictReader(open(f"{D}/results/runs.csv")))
cx = list(csv.DictReader(open("/workspace/work/tig/010-codex-repeat-variance/results/runs.csv")))
def cv(x): return S.pstdev(x)/S.mean(x)
def ok(r): return r["passed"] in ("True","true","1")
out=[]
for agent, rows in (("claude", cc), ("codex", cx)):
    for cond, task in (("default","SUITE14"),("small_N02","N02_duration")):
        rs=[r for r in rows if r["cond"]==cond and r["task"]==task]
        tot=[float(r["total_tokens"]) for r in rs]; cost=[float(r["est_cost_usd"]) for r in rs]
        if agent=="claude":
            unc=[float(r["input_tokens"])+float(r["cache_creation_tokens"]) for r in rs]; calls=[int(r["num_turns"]) for r in rs]
            share=[float(r["cache_share"]) for r in rs]
        else:
            unc=[float(r["uncached_input_tokens"]) for r in rs]; calls=[int(r["model_calls"]) for r in rs]; share=[float(r["cache_share"]) for r in rs]
        outt=[float(r["output_tokens"]) for r in rs]
        out.append(dict(agent=agent, task=task, n=len(rs), passed=sum(ok(r) for r in rs),
            tok_min=int(min(tot)), tok_max=int(max(tot)), tok_ratio=round(max(tot)/min(tot),3), tok_cv=round(cv(tot),4),
            uncached_min=int(min(unc)), uncached_max=int(max(unc)), uncached_ratio=round(max(unc)/min(unc),3),
            out_min=int(min(outt)), out_max=int(max(outt)), out_cv=round(cv(outt),4),
            cache_share_min=round(min(share),3), cache_share_max=round(max(share),3),
            cost_min=round(min(cost),4), cost_max=round(max(cost),4), cost_mean=round(S.mean(cost),4), cost_ratio=round(max(cost)/min(cost),3), cost_cv=round(cv(cost),4),
            calls=f"{min(calls)}-{max(calls)}", wall_min=min(float(r['wall_s']) for r in rs), wall_max=max(float(r['wall_s']) for r in rs)))
w=csv.DictWriter(open(f"{D}/results/summary.csv","w"),fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o)
fig,axes=plt.subplots(1,2,figsize=(12,4.8))
for ax,(cond,task) in zip(axes,[("default","SUITE14"),("small_N02","N02_duration")]):
    for i,(agent,rows,col) in enumerate((("Claude Code (opus-5-5)",cc,"#d17b4a"),("Codex (gpt-6.1-sol)",cx,"#4a7bd1"))):
        cost=[float(r["est_cost_usd"]) for r in rows if r["cond"]==cond and r["task"]==task]
        x=np.arange(1,len(cost)+1)+(i-0.5)*0.36
        ax.bar(x,cost,0.36,color=col,label=f"{agent}: max/min {max(cost)/min(cost):.2f}×")
    ax.set_title(f"{task}: est. $ per run, 5 identical runs",fontsize=10); ax.set_xlabel("run"); ax.set_ylabel("API-equivalent est. $"); ax.legend(fontsize=8,loc="upper center"); ax.set_ylim(0,ax.get_ylim()[1]*1.3)
plt.suptitle("Same task 5×: Claude Code's cost spread ≤1.05×, Codex's 1.4–2.2× (but Claude ≈3–5× pricier per run)",fontsize=11)
plt.tight_layout(); plt.savefig(f"{D}/results/chart.png",dpi=110)
