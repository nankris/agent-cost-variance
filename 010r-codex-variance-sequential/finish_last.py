import json,time
from run import trial,RESULTS
rows=[json.loads(s) for s in (RESULTS/'runs.jsonl').read_text().splitlines()]
rr=[r for r in rows if r['round']==2 and r['run']>0]
assert [r['run'] for r in rr]==list(range(1,15))
end=time.monotonic()-(time.time()-rr[-1]['end_epoch'])
for i,gap in [(15,15),(16,5)]:
    r,end=trial(2,i,gap,end)
    if not r.get('usage') or r['exit_code']!=0:raise SystemExit('Infrastructure failure; no third round')
