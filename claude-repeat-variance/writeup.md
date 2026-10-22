# Same task, five runs, two agents: Claude Code's bill doesn't wobble. Codex's does.

*10 headless Claude Code runs on 2026-10-15 (IST), compared with the 10 Codex runs from [the Codex version of this experiment](../codex-repeat-variance/).*

Last time I ran the same Codex task five times and the estimated cost moved up to 2.2×, almost all of it from how much of the prompt happened to be cached. So I ran the exact same two tasks on Claude Code 2.1.300 (Opus 5.5, Pro login).

| | Codex, cost min → max | Claude Code, cost min → max |
|---|---|---|
| 14-package fix-up | 6.0¢ → 8.6¢ (1.4×) | 23.9¢ → 25.1¢ (1.05×) |
| One bug behind a noisy test | 2.8¢ → 6.0¢ (2.2×) | 14.0¢ → 14.2¢ (1.01×) |

Claude Code did the same thing every time: 4 model calls, 3 shell commands, the same share of the prompt read from cache (76% / 83%) down to the decimal. Tokens moved by 1% or less.

**Why.** Claude Code sets its own cache breakpoints, so a new run always reuses the same cached system prompt and writes the same new turns. Codex leaves caching to the provider, and that's luck of the timing.

**The catch.** Predictable isn't cheap. At API list prices Claude Code cost about 3.5× as much per run here: Opus 5.5 is pricier, it wrote about twice as much output, and every run pays to write 14–23K tokens into a 1-hour cache.

**Takeaway.** If you're budgeting agent runs, Claude Code's per-task cost is something you can measure once and trust. Codex's needs a range.

*All $ are API-equivalent estimates from each CLI's usage numbers; Pro and Plus aren't billed per token.*
