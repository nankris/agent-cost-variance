import json,time,shutil
from run import trial,RESULTS
rows=[json.loads(s) for s in (RESULTS/'runs.jsonl').read_text().splitlines()]
valid=[r for r in rows if r['round']==2 and r['run']>0 and r.get('usage') and r['exit_code']==0 and r['passed']]
assert [r['run'] for r in valid]==list(range(1,16))
raw=RESULTS/'r2_16.jsonl'
if raw.exists(): shutil.copy2(raw,RESULTS/'failed_r2_16.jsonl')
previous=time.monotonic()-(time.time()-valid[-1]['end_epoch'])
r,end=trial(2,16,5,previous)
if not r.get('usage') or r['exit_code']!=0:raise SystemExit('Final retry failed; stop after two rounds')
