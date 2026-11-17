import json,random,pathlib,subprocess,time,re,os,sys
p=pathlib.Path('/tmp/lana-tree-scale'); family=sys.argv[1]; n=int(sys.argv[2]); d=int(sys.argv[3]); binary=sys.argv[4]
r=random.Random(42); schema=[dict(name=f'x{i}',kind='number',nullable=False,categories=[]) for i in range(d)]
def rows(count,prefix):
 out=[]
 for j in range(count):
  x=[round(r.random(),4) for i in range(d)];out.append(dict(id=f'{prefix}{j}',features={f'x{i}':v for i,v in enumerate(x)},target=x[0]+x[1]>1))
 return out
data=dict(task=dict(id='scale',feature_schema=schema,problem='classification',labels=[False,True]),train=rows(n,'t'),holdout=rows(200,'h'))
path=p/f'data-{n}-{d}.json';path.write_text(json.dumps(data,separators=(',',':')))
script=p/f'run-{family}-{n}-{d}.lana';script.write_text(f'import "std/trees" as trees;\nlet data = resolve(result_value(json_parse(read_text("{path}"))));\nlet result = trees.fit(data.task, data.train, data.holdout, {{family: "{family}", max_depth: 4, min_leaf: 2, ensemble_size: {1 if family=="tree" else 5}, seed: 42}});\nprint(json_stringify(result.validation_report.metrics));\n')
env=os.environ.copy();env['LANA_STDLIB_DIR']=str(p/'candidate/stdlib');env['LANA_COMPILER_PATH']=str(pathlib.Path.cwd()/'target/lana/bin/lana-compiler.labc')
t=time.monotonic()
try:
 v=subprocess.run(['/usr/bin/time','-l',binary,'run',str(script)],capture_output=True,text=True,timeout=30,env=env); out={'family':family,'rows':n,'features':d,'seconds':round(time.monotonic()-t,3),'exit':v.returncode,'stdout':v.stdout[-2000:],'stderr':v.stderr[-2000:]}
except subprocess.TimeoutExpired as e: out={'family':family,'rows':n,'features':d,'seconds':round(time.monotonic()-t,3),'status':'timeout','stdout':str(e.stdout),'stderr':str(e.stderr)}
print(json.dumps(out),flush=True)
with (p/'results.jsonl').open('a') as f:f.write(json.dumps(out)+'\n')
