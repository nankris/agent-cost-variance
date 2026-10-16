# Same Codex task, five runs: the tokens barely moved, the bill moved 2×

*Draft. Tech in General experiment #010. 10 headless Codex runs on 2026-10-14.*

You'll hear that running the same agent task twice can cost wildly different amounts (one figure going around says up to 30×). I ran two tasks five times each on Codex CLI (0.162.1, gpt-6.1-sol, ChatGPT Plus login), each run from a fresh copy and with no settings changed.

## The tasks

- **Big:** a folder of 14 tiny JavaScript packages, 13 of them broken. "Make `node run_all.js` pass."
- **Small:** one bug, a duration parser that ignores seconds, behind a test that prints 420 lines of noise.

All 10 runs passed.

## What changed between runs

| | Total tokens, min → max | Est. cost, min → max |
|---|---|---|
| Big task | 95K → 130K (1.4×) | 6.0¢ → 8.6¢ (1.4×) |
| Small task | 75K → 90K (1.2×) | 2.8¢ → 6.0¢ (2.2×) |

The model did nearly the same thing every time: 4 or 5 calls, the same fix, about the same amount of written output. The token counts stayed close.

The cost didn't, and the reason is the prompt cache. Codex resends the conversation on every call. If the provider has seen that prefix recently, those tokens are "cached" and cost $0.10 per million instead of $2. In my runs the cached share swung between 66% and 88%, and that swing alone doubled the bill on the small task.

## The run that used the fewest tokens wasn't the cheapest

On the big task, run 4 used the fewest tokens of all five (95K) and was the second most expensive (8.2¢), because only 66% of its input came from cache. Across the five runs, total tokens and cost were basically uncorrelated (r = −0.04). **If you track your agent's tokens to understand its cost, track the uncached ones.**

## It also depended on timing

On the small task, the first two runs (started together, first) hit the cache 71–77% of the time and cost 5–6¢. The next three, started a minute later, hit 87–88% and cost about 3¢. My guess is the cache was warm by then. I didn't shuffle the order, so take that as a hint, not a result.

## Caveats

- Five runs per task, short tasks, one afternoon. Long agent sessions that try different strategies can spread much more, so this doesn't disprove the 30× figure for that kind of work.
- Runs went two at a time, and another experiment shared the account, which can affect caching.
- Costs are estimates at gpt-6.1-sol API list prices. On ChatGPT Plus you pay a flat fee and these runs used a slice of the 5-hour usage window.

## Takeaway

For short, well-defined Codex tasks, the model's behaviour is steady, but your cost per run can still vary about 2× from cache luck. Average over several runs before you conclude one setup is cheaper than another. I learned that the hard way in the other experiments in this series.

*Code, raw logs and the per-run table: repo `010-codex-repeat-variance`.*
