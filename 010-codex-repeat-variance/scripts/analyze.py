#!/usr/bin/env python3
"""#010: same task, same config, 5 fresh runs each, for two tasks:
  default   = SUITE14 (14 packages, one exec)      small_N02 = N02_duration (one noisy-log bug)
Writes results/summary.csv (spread stats per task) and results/chart.png."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(HERE, "results", "runs.csv")).sort_values(["cond", "rep"])
names = {"default": "SUITE14 (14 packages)", "small_N02": "N02_duration (1 bug)"}
metrics = ["total_tokens", "input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens",
           "cache_share", "est_cost_usd", "model_calls", "tool_calls", "wall_s"]
out = []
for cond, g in df.groupby("cond"):
    for m in metrics:
        out.append(dict(task=names.get(cond, cond), metric=m, runs=len(g), passes=int(g.passed.sum()), mean=g[m].mean(),
                        sd=g[m].std(), min=g[m].min(), max=g[m].max(), max_over_min=g[m].max() / g[m].min(),
                        cv=g[m].std() / g[m].mean()))
stats = pd.DataFrame(out)
stats.round(4).to_csv(os.path.join(HERE, "results", "summary.csv"), index=False)
print(df[["cond", "rep", "passed"] + metrics].to_string(index=False))
print()
print(stats.round(3).to_string(index=False))
print("corr(total_tokens, cost) per task:", df.groupby("cond").apply(lambda g: round(g.total_tokens.corr(g.est_cost_usd), 3)).to_dict())

conds = [c for c in ["default", "small_N02"] if c in set(df.cond)]
fig, ax = plt.subplots(len(conds), 3, figsize=(15, 4.2 * len(conds)), squeeze=False)
for row, cond in enumerate(conds):
    g = df[df.cond == cond]
    x = g.rep.astype(str)
    a = ax[row]
    a[0].bar(x, g.cached_input_tokens / 1000, color="#8fbcd4", label="cached input")
    a[0].bar(x, g.uncached_input_tokens / 1000, bottom=g.cached_input_tokens / 1000, color="#e3a07a", label="uncached input")
    a[0].bar(x, g.output_tokens / 1000, bottom=g.input_tokens / 1000, color="#c44e52", label="output")
    a[0].set_title(f"{names[cond]}: tokens per run (K)", fontsize=10)
    a[0].legend(fontsize=7, loc="lower right")
    a[1].bar(x, g.est_cost_usd * 100, color="#55a868")
    for i, (c, p) in enumerate(zip(g.est_cost_usd, g.passed)):
        a[1].text(i, c * 100 * 1.01, ("pass" if p else "FAIL"), ha="center", fontsize=8)
    rt = g.total_tokens.max() / g.total_tokens.min()
    rc = g.est_cost_usd.max() / g.est_cost_usd.min()
    a[1].set_title(f"Est. API cost per run (US cents)  max/min {rc:.2f}x (tokens {rt:.2f}x)", fontsize=10)
    a[2].bar(x, g.cache_share * 100, color="#4c72b0")
    a[2].set_ylim(0, 100)
    a[2].set_title("Share of input served from cache (%)", fontsize=10)
    for s in a:
        s.set_xlabel("run #")
        s.grid(axis="y", alpha=0.3)
fig.suptitle("Codex 0.162.1 (gpt-6.1-sol): same task, same config, 5 fresh runs each", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "results", "chart.png"), dpi=130)
print("wrote chart")
