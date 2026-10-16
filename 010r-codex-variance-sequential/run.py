import json, pathlib, subprocess, time, shutil, hashlib, os, sys
ROOT=pathlib.Path(__file__).resolve().parent
WORK=ROOT/'work'
PROMPT='Make `node test.js` pass by fixing the code. Do not edit test.js.'
RESULTS=ROOT/'results'
RESULTS.mkdir(exist_ok=True)

def trial(round_, index, gap, previous_end, clean=False):
    if previous_end is not None:
        deadline=previous_end+gap*60
        while time.monotonic()<deadline:
            left=deadline-time.monotonic()
            print(f'round {round_} run {index}: gap remaining {left:.0f}s',flush=True)
            time.sleep(min(30,left))
    if WORK.exists(): shutil.rmtree(WORK)
    shutil.copytree(ROOT/'fixture',WORK,copy_function=shutil.copy2)
    before=(WORK/'test.js').read_bytes()
    cmd=['codex','exec','--json','--skip-git-repo-check','--dangerously-bypass-approvals-and-sandbox','-m','gpt-6.1-sol','-c','model_reasoning_effort="medium"','-C',str(WORK)]
    if clean: cmd+=['--ignore-user-config','--ignore-rules']
    cmd += [PROMPT]
    start_m=time.monotonic(); start=time.time()
    print(f'START round {round_} run {index} gap={gap}',flush=True)
    try:
        p=subprocess.run(cmd,input='',capture_output=True,text=True,timeout=300)
        stdout,stderr,rc=p.stdout,p.stderr,p.returncode
    except subprocess.TimeoutExpired as e:
        stdout=e.stdout or ''; stderr='TIMEOUT'; rc=-9
        if isinstance(stdout,bytes): stdout=stdout.decode(errors='replace')
    end_m=time.monotonic()
    # Keep only synthetic task events; drop thread/account identifiers and MCP diagnostics.
    events=[]; usage=None; errors=[]
    for line in stdout.splitlines():
        try: ev=json.loads(line)
        except ValueError: continue
        if ev.get('type')=='thread.started': continue
        if ev.get('type')=='turn.completed': usage=ev.get('usage')
        if ev.get('type') in ['error','turn.failed']: errors.append(ev)
        if ev.get('type') == 'turn.completed': events.append(ev)
    stem=f'r{round_}_{index:02d}'
    (RESULTS/f'{stem}.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    chk=subprocess.run(['node','test.js'],cwd=WORK,capture_output=True,timeout=30)
    row=dict(round=round_,run=index,gap_min=gap,start_epoch=start,end_epoch=start+(end_m-start_m),actual_gap_s=None if previous_end is None else start_m-previous_end,wall_s=end_m-start_m,exit_code=rc,passed=chk.returncode==0 and before==(WORK/'test.js').read_bytes(),usage=usage,errors=errors,clean_config=clean)
    if usage:
        inp=usage['input_tokens']; ca=usage['cached_input_tokens']; out=usage['output_tokens']
        row.update(input_tokens=inp,cached_input_tokens=ca,uncached_input_tokens=inp-ca,output_tokens=out,cache_share=ca/inp,cost=((inp-ca)*2+ca*.1+out*10)/1e6)
    with (RESULTS/'runs.jsonl').open('a') as f: f.write(json.dumps(row)+'\n')
    print(json.dumps(row),flush=True)
    return row,end_m

def verdict(rows):
    import numpy as np
    short=[r for r in rows if r['gap_min'] in (0,1) and r['actual_gap_s'] is not None and r.get('usage')]
    long=[r for r in rows if r['gap_min'] in (5,15) and r.get('usage')]
    if not short or not long: return 'STILL INCONCLUSIVE'
    rng=np.random.default_rng(1010)
    a=rng.integers(len(short),size=(50000,len(short))); b=rng.integers(len(long),size=(50000,len(long)))
    rat=np.array([r['cost'] for r in long])[b].mean(1)/np.array([r['cost'] for r in short])[a].mean(1)
    diff=np.array([r['cache_share'] for r in long])[b].mean(1)-np.array([r['cache_share'] for r in short])[a].mean(1)
    lo,hi=np.quantile(rat,[.025,.975]); dl,dh=np.quantile(diff,[.025,.975])
    if dh<0 and lo>1.1:return 'PROVEN'
    if lo>=.9 and hi<=1.1:return 'DISPROVEN'
    return 'STILL INCONCLUSIVE'

if __name__=='__main__':
    if (RESULTS/'runs.jsonl').exists(): sys.exit('Refusing to overwrite existing trials')
    rows=[]; end=None
    for i,gap in enumerate([None,0,15,1,5,0,5,1,15,0],1):
        r,end=trial(1,i,gap,end); rows.append(r)
        if not r.get('usage') or r['exit_code']!=0:
            print('Infrastructure failure: retry once with clean config',flush=True)
            r,end=trial(2,1,0,end,clean=True)
            print('STOP: infrastructure retry complete; scheduled timing study unavailable' if not r.get('usage') else 'Clean baseline recovered; further timing requires amended design',flush=True)
            sys.exit(2)
    v=verdict(rows); print('ROUND 1 '+v,flush=True)
    if v=='STILL INCONCLUSIVE':
        rows=[]
        for i,gap in enumerate([15,0,5,1,1,5,0,15,5,15,1,0,0,1,15,5],1):
            r,end=trial(2,i,gap,end); rows.append(r)
            if not r.get('usage') or r['exit_code']!=0:sys.exit(2)
        print('ROUND 2 '+verdict(rows),flush=True)
