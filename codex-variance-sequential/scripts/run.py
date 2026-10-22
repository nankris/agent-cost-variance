import pathlib, subprocess, json, time, random, shutil, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROMPT='Make `node test.js` pass by fixing the code. Do not edit test.js.'
rng=random.Random(1010)
def run(roundno, gaps):
    rows=[]
    last=None
    for i,gap in enumerate(gaps):
        if last is not None:
            due=last+60*gap
            print(json.dumps({'round':roundno,'next_run':i+1,'gap_minutes':gap,'due_epoch':due}),flush=True)
            while time.time()<due: time.sleep(min(30,due-time.time()))
        work=ROOT/'work'
        if work.exists(): shutil.rmtree(work)
        shutil.copytree(ROOT/'fixture',work)
        before=hashlib.sha256((work/'test.js').read_bytes()).hexdigest()
        start=time.time()
        stem=ROOT/'results'/f'r{roundno}_{i+1:02}'
        cmd=['codex','exec','--json','--skip-git-repo-check','--dangerously-bypass-approvals-and-sandbox','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"','-C',str(work),PROMPT]
        with open(str(stem)+'.jsonl','w') as out,open(str(stem)+'.stderr','w') as err:
            p=subprocess.run(cmd,stdout=out,stderr=err,timeout=600)
        end=time.time()
        events=[json.loads(s) for s in pathlib.Path(str(stem)+'.jsonl').read_text().splitlines() if s.strip()]
        usage=[e['usage'] for e in events if e.get('type')=='turn.completed']
        if p.returncode or len(usage)!=1: raise RuntimeError('Failed execution/missing usage; no fabricated result')
        u=usage[0]; inp=u['input_tokens']; cached=u['cached_input_tokens']; out=u['output_tokens']
        check=subprocess.run(['node','test.js'],cwd=work,capture_output=True)
        row=dict(round=roundno,run=i+1,gap_min=gap,actual_gap_s=None if last is None else start-last,start_epoch=start,end_epoch=end,wall_s=end-start,input_tokens=inp,cached_input_tokens=cached,uncached_input_tokens=inp-cached,output_tokens=out,cache_share=cached/inp,cost=(2*(inp-cached)+.1*cached+10*out)/1e6,passed=check.returncode==0 and before==hashlib.sha256((work/'test.js').read_bytes()).hexdigest(),errors=[e for e in events if e.get('type') in ['error','turn.failed']])
        rows.append(row); (ROOT/'results'/f'round{roundno}.json').write_text(json.dumps(rows,indent=2)); print(json.dumps(row),flush=True)
        last=end
    return rows
if __name__=='__main__':
    gaps=[0,0,0,1,1,5,5,15,15]; rng.shuffle(gaps)
    run(1,[None]+gaps)
