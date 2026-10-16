import json,time
from run import trial,RESULTS
rows=[json.loads(s) for s in (RESULTS/'runs.jsonl').read_text().splitlines()]
existing=[r for r in rows if r['round']==2 and r['run']>0]
if [r['run'] for r in existing]!=list(range(1,8)): raise SystemExit('Unexpected existing trials; refuse overwrite')
r,end=trial(2,-1,None,None)
if not r.get('usage'): raise SystemExit('Restart baseline failed')
for i,gap in enumerate([15,5,15,1,0,0,1,15,5],8):
    r,end=trial(2,i,gap,end)
    if not r.get('usage') or r['exit_code']!=0: raise SystemExit('Infrastructure failure; stop at second round')
