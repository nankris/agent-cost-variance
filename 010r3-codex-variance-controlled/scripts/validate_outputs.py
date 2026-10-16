"""Descriptive correctness audit; never changes trial inclusion."""
import json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[1];D=R/'results'; out=[]
for row in [json.loads(s) for s in (D/'attempts.jsonl').read_text().splitlines()]:
 if not row['valid']:continue
 raw=D/f"{row['id']:02d}-{row['attempt']:02d}.jsonl"
 events=[json.loads(s) for s in raw.read_text().splitlines()]
 source='\n'.join(e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message')
 source=source.strip()
 if source.startswith('```'):source='\n'.join(source.splitlines()[1:-1])
 test='''
const testedParser=module.exports.parseDuration;
for (const [s,want] of [['1h30m',5400],['45m',2700],['2h',7200],['90s',90],['1h2m3s',3723],['0s',0],['',0]]) {
if(testedParser(s)!==want) throw Error(s);
}
'''
 try:
  r=subprocess.run(['node','-e',source+'\n'+test],capture_output=True,text=True,timeout=5)
  out.append({'id':row['id'],'attempt':row['attempt'],'passes':r.returncode==0,'stderr':r.stderr})
 except Exception as e:out.append({'id':row['id'],'attempt':row['attempt'],'passes':False,'error':str(e)})
(D/'correctness.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checked':len(out),'passed':sum(r['passes'] for r in out)}))
