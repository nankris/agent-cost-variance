import json,math,pathlib
cdf=lambda z:(1+math.erf(z/math.sqrt(2)))/2
out=[]
for sd in [.1,.2]:
 se=sd/math.sqrt(20)
 out.append(dict(log_ratio_sd=sd,n=20,se=se,halfwidth=1.96*se,power_disprove_at_ratio_1=cdf(math.log(1.15)/se-1.96),power_prove_at_ratio_1_25=cdf(math.log(1.25/1.15)/se-1.96)))
path=pathlib.Path(__file__).resolve().parents[1]/'results/power.json';path.write_text(json.dumps(out,indent=2)+'\n');print(path.read_text())
