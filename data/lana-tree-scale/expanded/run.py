import pathlib,csv,json,random,hashlib,collections,math,subprocess,os,time,signal,re,sys
p=pathlib.Path('/tmp/lana-tree-scale/expanded');root=pathlib.Path('/Users/vijayneelakantan/remote-repos-on-local/lana'); datasets={'banknote':pathlib.Path('/tmp/lana-tree-scale/banknote/data.csv'),'pima':p/'pima.csv'}
meta={};splits={}
for name,path in datasets.items():
 raw=path.read_bytes(); rows=list(csv.reader(raw.decode().splitlines())); header=rows.pop(0) if name=='pima' else ['variance','skewness','curtosis','entropy','class']; width=len(header)-1;groups={};counts=collections.Counter();bad=[]
 for idx,r in enumerate(rows):
  try:
   vals=[float(x) for x in r];assert len(vals)==width+1 and all(math.isfinite(x) for x in vals) and vals[-1] in (0,1)
  except (ValueError,AssertionError):bad.append(idx);continue
  key=tuple(vals[:-1]);label=bool(vals[-1]);counts[str(label)]+=1
  groups.setdefault(key,[]).append({'id':f'row-{idx:04d}','features':{f'x{j}':v for j,v in enumerate(key)},'target':label})
 conflicts=sum(len({row['target'] for row in g})>1 for g in groups.values());assert not bad and not conflicts,(name,bad,conflicts)
 meta[name]={'source':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(rows),'columns':header,'labels':dict(counts),'duplicate_rows':len(rows)-len(groups),'conflicting_feature_groups':conflicts,'zero_counts':{header[j]:sum(float(r[j])==0 for r in rows) for j in range(width)}}
 for seed in (42,43):
  rng=random.Random(seed);train=[];holdout=[]
  for label in (False,True):
   gs=[g for g in groups.values() if g[0]['target']==label];rng.shuffle(gs);target=round(sum(map(len,gs))*.2);count=0
   for g in gs:
    if count<target:holdout.extend(g);count+=len(g)
    else:train.extend(g)
  assert not ({tuple(r['features'].values()) for r in train}&{tuple(r['features'].values()) for r in holdout});assert {r['target'] for r in holdout}=={False,True}
  task={'id':name,'feature_schema':[{'name':f'x{j}','kind':'number','nullable':False,'categories':[]} for j in range(width)],'problem':'classification','labels':[False,True]}
  data={'task':task,'train':train,'holdout':holdout};pathout=p/f'{name}-{seed}.json';pathout.write_text(json.dumps(data,separators=(',',':')))
  splits[f'{name}-{seed}']={'path':str(pathout),'sha256':hashlib.sha256(pathout.read_bytes()).hexdigest(),'train':len(train),'holdout':len(holdout),'train_labels':dict(collections.Counter(str(r['target']) for r in train)),'holdout_labels':dict(collections.Counter(str(r['target']) for r in holdout))}
  if name=='banknote' and seed==42:assert pathout.read_bytes()==pathlib.Path('/tmp/lana-tree-scale/banknote/split.json').read_bytes()
meta['splits']=splits;meta['pima_source']='https://huggingface.co/datasets/khoaguin/pima-indians-diabetes-database/resolve/main/diabetes.csv';(p/'metadata.json').write_text(json.dumps(meta,indent=2));print('DATA',json.dumps(meta),flush=True)
base=p/'baseline.py';base.write_text('''import json,sys\nfrom sklearn.tree import DecisionTreeClassifier\nd=json.load(open(sys.argv[1])); depth=int(sys.argv[2]); n=len(d["task"]["feature_schema"])\ndef xy(rows): return [[r["features"][f"x{i}"] for i in range(n)] for r in rows],[r["target"] for r in rows]\nx,y=xy(d["train"]);h,z=xy(d["holdout"]);m=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=2,random_state=42);m.fit(x,y);pred=m.predict(h).tolist();print(json.dumps({"predictions":[{"id":r["id"],"prediction":bool(v),"target":r["target"]} for r,v in zip(d["holdout"],pred)]}))\n''')
env=os.environ.copy();env['LANA_STDLIB_DIR']=str(root/'stdlib'); results=[]
for name in datasets:
 for seed in (42,43):
  data=p/f'{name}-{seed}.json'
  for depth in (4,6):
   script=p/f'{name}-{seed}-d{depth}.lana';script.write_text(f'import "std/trees" as trees;\nlet data = resolve(result_value(json_parse(read_text("{data}"))));\nlet result = trees.fit(data.task, data.train, data.holdout, {{family: "tree", max_depth: {depth}, min_leaf: 2, ensemble_size: 1, seed: 42}});\nprint(json_stringify(result.validation_report));\n')
   for impl,cmd in [('lana',[str(root/'target/lana/bin/lana'),'run',str(script),'--memory-limit-mib','1024']),('sklearn',['/tmp/lana-tree-scale/venv/bin/python',str(base),str(data),str(depth)])]:
    start=time.monotonic();proc=subprocess.Popen(['/usr/bin/time','-l']+cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,env=env)
    try:out,err=proc.communicate(timeout=30);status='ok' if proc.returncode==0 else 'error'
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate();status='timeout'
    elapsed=round(time.monotonic()-start,4);match=re.search(r'(\d+)\s+maximum resident set size',err);rss=int(match.group(1)) if match else None;prediction=[]
    if status=='ok':
     decoded=json.loads(out);prediction=decoded['holdout_trace'] if impl=='lana' else decoded['predictions'];expected=json.loads(data.read_text())['holdout'];assert [x['id'] for x in prediction]==[x['id'] for x in expected];assert len(prediction)==len(expected)
    record={'dataset':name,'split_seed':seed,'depth':depth,'implementation':impl,'status':status,'exit_code':proc.returncode,'elapsed_seconds':elapsed,'peak_rss_bytes':rss,'correct':sum(x['target']==x['prediction'] for x in prediction) if prediction else None,'count':len(prediction),'predictions':prediction,'stderr':err,'command':cmd};results.append(record);(p/'fits.json').write_text(json.dumps(results,indent=2));print('FIT',name,seed,depth,impl,status,record['correct'],record['count'],elapsed,rss,flush=True)
print('COMPLETED',len(results),flush=True)
