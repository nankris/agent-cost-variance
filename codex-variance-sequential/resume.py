"""Single allowed redesign after interrupted round 1; never overwrite prior data."""
import json
from run import RESULTS, trial, verdict
rows=[json.loads(s) for s in (RESULTS/'runs.jsonl').read_text().splitlines()]
if any(r['round']==2 for r in rows):
    raise SystemExit('Round 2 already started; refusing duplicate trials')
r,end=trial(2,0,None,None)
if not r.get('usage') or r['exit_code']!=0: raise SystemExit('Warm-up failed')
rows=[]
for i,gap in enumerate([15,0,5,1,1,5,0,15,5,15,1,0,0,1,15,5],1):
    r,end=trial(2,i,gap,end)
    rows.append(r)
    if not r.get('usage') or r['exit_code']!=0: raise SystemExit('Infrastructure failure; stop at round 2')
print('ROUND 2 '+verdict(rows),flush=True)
