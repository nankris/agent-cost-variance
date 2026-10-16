import math,json
from pathlib import Path
phi=lambda x:(1+math.erf(x/math.sqrt(2)))/2
out={}
for sd in [.08,.22]:
 se=sd*math.sqrt(2/12); d=math.log(1.1)/se
 lower=math.log(.9)+1.6448536269514722*se
 upper=math.log(1.1)-1.6448536269514722*se
 out[f'12/12,sd={sd}']={'SE':se,'equivalence_power_approx':max(0,phi(upper/se)-phi(lower/se)) if upper>lower else 0,'superiority_power_approx':phi(d-1.959963984540054)+phi(-d-1.959963984540054)}
for true in [.8,.95]:
 delta=(math.atanh(math.sqrt(true))-math.atanh(math.sqrt(.5)))*math.sqrt(24-3)
 out[f'R2={true}']={'power_approx':phi(delta-1.959963984540054)}
text=json.dumps(out,indent=2); print(text)
(Path(__file__).resolve().parents[1]/'results/power.json').write_text(text+'\n')
