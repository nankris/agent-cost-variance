import fcntl,json,os,pathlib,random,string,subprocess,time
R=pathlib.Path(__file__).resolve().parents[1]; D=R/'results'
lock=(D/'runner.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def save_event(e):
 with (D/'attempts.jsonl').open('a') as f: f.write(json.dumps(e)+'\n'); f.flush(); os.fsync(f.fileno())
p=D/'schedule.json'
if not p.exists():
 rng=random.Random(1010); nr=random.Random(1011); schedule=[]
 for b in range(20):
  arms=['cacheable','busted']; rng.shuffle(arms)
  nonce=''.join(nr.choices(string.ascii_letters+string.digits,k=64))
  for arm in arms: schedule.append(dict(id=len(schedule),block=b,arm=arm,nonce=nonce if arm=='busted' else ''))
 p.write_text(json.dumps(schedule,indent=2))
schedule=json.loads(p.read_text()); prompt=(R/'prompt.txt').read_text()
budget=D/'budget.json'
if not budget.exists(): budget.write_text(json.dumps({'deadline':time.time()+55*60}))
deadline=json.loads(budget.read_text())['deadline']
subprocess.run(['codex','--version'],stdout=(D/'cli-version.txt').open('w'))
def parse(raw):
 events=[]
 for line in raw.read_text().splitlines():
  try: events.append(json.loads(line))
  except ValueError: pass
 usage=next((e['usage'] for e in reversed(events) if e.get('type')=='turn.completed'),None)
 tools=sum(e.get('item',{}).get('type') in ('command_execution','mcp_tool_call','file_change') for e in events if e.get('type')=='item.completed')
 return usage,tools
for trial in schedule:
 events=[json.loads(s) for s in (D/'attempts.jsonl').read_text().splitlines()] if (D/'attempts.jsonl').exists() else []
 if any(e.get('status')=='completed' and e['id']==trial['id'] and e['valid'] for e in events): continue
 for old in [e for e in events if e.get('status')=='started' and e['id']==trial['id']]:
  if any(e.get('status')=='completed' and e['stem']==old['stem'] for e in events): continue
  usage,tools=parse(D/(old['stem']+'.jsonl'))
  if usage and tools==0:
   save_event(dict(old,status='completed',valid=True,usage=usage,recovered=True,end=time.time()))
   break
  save_event(dict(old,status='completed',valid=False,usage=usage,end=time.time(),interrupted=True))
 else:
  usage=None
 if usage and tools==0: continue
 for attempt in range(1,3):
  stem=f"{trial['id']:02d}-{attempt:02d}"
  if (D/(stem+'.jsonl')).exists(): continue
  if time.time()>deadline: raise SystemExit('Wall budget exhausted')
  row=dict(trial,stem=stem,attempt=attempt,start=time.time(),status='started'); save_event(row)
  text=trial['nonce']+'\n'+prompt if trial['nonce'] else prompt
  cmd=['codex','exec','--json','--ephemeral','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--sandbox','read-only','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"','-C',str(R/'work'),text]
  with (D/(stem+'.jsonl')).open('w') as out,(D/(stem+'.stderr')).open('w') as err:
   try: rc=subprocess.run(cmd,stdout=out,stderr=err,input='',text=True,timeout=180).returncode
   except subprocess.TimeoutExpired: rc=-9
  usage,tools=parse(D/(stem+'.jsonl')); valid=rc==0 and usage is not None and tools==0
  row.update(status='completed',end=time.time(),exit_code=rc,usage=usage,tool_calls=tools,valid=valid); save_event(row)
  print(json.dumps(row),flush=True)
  if valid: break
 else: raise SystemExit('Trial exhausted two attempts; analyze available data')
