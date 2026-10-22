"""Approved 12/12 interleaved schedule; default account, no Colab."""
import argparse, json, os, pathlib, random, subprocess, time
R=pathlib.Path(__file__).resolve().parents[1]; D=R/'results'; D.mkdir(exist_ok=True)
config={'mode':'approved_12_12','seed':101003,'short':12,'spaced':12}
cf=D/'schedule.json'
if cf.exists():
 old=json.loads(cf.read_text()); assert old['config']==config,'Cannot alter a started schedule'
 labels=old['labels']
else:
 rng=random.Random(config['seed']); labels=[]
 for _ in range(12):
  block=['short','spaced']; rng.shuffle(block); labels.extend(block)
 cf.write_text(json.dumps({'config':config,'labels':labels},indent=2))
ledger=D/'attempts.jsonl'
rows=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={r['id'] for r in rows if r['valid']}; start_budget=rows[0]['start'] if rows else time.time()
end_budget=start_budget+4*3600
prompt=('Fix the following JavaScript duration parser so h, m, and s units all work. '
        'Return only the entire corrected source. Do not use tools or inspect files.\n\n'+(R/'fixture/broken.js').read_text())
(R/'prompt.txt').write_text(prompt)
work=R/'work'; work.mkdir(exist_ok=True)
previous=rows[-1]['end'] if rows else None
queue=[(-1,'warmup')]+list(enumerate(labels))
# On restart establish a fresh short-gap exposure, preserving all prior attempts.
next_pending=next(((i,a) for i,a in queue if i not in done),None)
if rows and next_pending and next_pending[1]=='short' and time.time()-previous>120:
 warm_id=min([-1]+[r['id'] for r in rows])-1
 queue=[(warm_id,'warmup')]+queue
for i,label in queue:
 if i in done: continue
 attempt=1+sum(r['id']==i for r in rows)
 while True:
  delay=900 if label=='spaced' else 0
  target=(previous+delay) if previous else time.time()
  if label=='short' and previous and time.time()-previous>120:
   # A resumed short trial cannot be treated as short without an intervening exposure.
   raise SystemExit('Short-arm timing interrupted: resume requires documented unscored warm-up; no automatic relabeling.')
  if target+180>end_budget: raise SystemExit('Wall-time budget exhausted; analyze available trials.')
  while time.time()<target:
   print(json.dumps({'status':'waiting','trial':i,'arm':label,'remaining_s':round(target-time.time())}),flush=True)
   time.sleep(min(30,max(0,target-time.time())))
  stem=f'{i:02d}-{attempt:02d}'; start=time.time(); gap=None if previous is None else start-previous
  cmd=['codex','exec','--json','--ephemeral','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--sandbox','read-only','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"','-C',str(work),prompt]
  raw=D/(stem+'.jsonl'); err=D/(stem+'.stderr')
  with raw.open('w') as out,err.open('w') as e:
   try: result=subprocess.run(cmd,stdout=out,stderr=e,input='',text=True,timeout=180); rc=result.returncode
   except subprocess.TimeoutExpired: rc=-9
  end=time.time(); events=[]
  for line in raw.read_text().splitlines():
   try: events.append(json.loads(line))
   except ValueError: pass
  usage=next((e['usage'] for e in reversed(events) if e.get('type')=='turn.completed'),None)
  tool_calls=sum(e.get('item',{}).get('type') in ('command_execution','mcp_tool_call','file_change') for e in events if e.get('type')=='item.completed')
  valid=rc==0 and usage is not None and tool_calls==0 and (label=='warmup' or (gap is not None and (gap>=900 if label=='spaced' else gap<=120)))
  row=dict(id=i,arm=label,attempt=attempt,start=start,end=end,gap_s=gap,exit_code=rc,valid=valid,tool_calls=tool_calls,usage=usage)
  if usage:
   n=usage['input_tokens']; c=usage['cached_input_tokens']; o=usage['output_tokens']
   row.update(input=n,cached=c,output=o,cache_share=c/n,cost=((n-c)*2+c*.1+o*10)/1e6)
  with ledger.open('a') as f: f.write(json.dumps(row)+'\n'); f.flush(); os.fsync(f.fileno())
  rows.append(row); previous=end; print(json.dumps(row),flush=True)
  if valid: break
  attempt+=1
  # Rate-limit pauses preserve the failed trial and redo the assigned delay.
  if time.time()+delay+180>end_budget: raise SystemExit('Insufficient time budget to retry')
  if not usage: time.sleep(60)
