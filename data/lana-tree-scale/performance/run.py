import json,pathlib,hashlib,subprocess,os,time,signal,re,statistics,platform
src=pathlib.Path('/tmp/lana-tree-scale/expanded');dest=pathlib.Path('/tmp/lana-tree-scale/performance');root=pathlib.Path('/Users/vijayneelakantan/remote-repos-on-local/lana');metadata=json.loads((src/'metadata.json').read_text());old=json.loads((src/'fits.json').read_text());exe=root/'target/lana/bin/lana';baseline=src/'baseline.py';env=os.environ.copy();env['LANA_STDLIB_DIR']=str(root/'stdlib')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(src/(k+'.json'))==v['sha256'] for k,v in metadata['splits'].items())
files=[exe,baseline]+[src/(k+'.json') for k in metadata['splits']]+sorted(src.glob('*-d*.lana')); manifest={'hashes':{str(f):digest(f) for f in files},'lana_version':subprocess.check_output([str(exe),'version'],text=True).strip(),'python_version':subprocess.check_output(['/tmp/lana-tree-scale/venv/bin/python','--version'],text=True).strip(),'sklearn_version':subprocess.check_output(['/tmp/lana-tree-scale/venv/bin/python','-c','import sklearn;print(sklearn.__version__)'],text=True).strip(),'platform':platform.platform(),'machine':platform.machine()};(dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
records=[]
for name in ('banknote','pima'):
 for seed in (42,43):
  for depth in (4,6):
   path=src/f'{name}-{seed}.json';script=src/f'{name}-{seed}-d{depth}.lana';data=json.loads(path.read_text());prior={x['implementation']:x for x in old if x['dataset']==name and x['split_seed']==seed and x['depth']==depth};assert len(prior)==2
   commands={'lana':[str(exe),'run',str(script),'--memory-limit-mib','1024'],'sklearn':['/tmp/lana-tree-scale/venv/bin/python',str(baseline),str(path),str(depth)]}
   for iteration in range(4):
    order=('lana','sklearn') if iteration%2==0 else ('sklearn','lana')
    for impl in order:
     cmd=commands[impl];start=time.monotonic();proc=subprocess.Popen(['/usr/bin/time','-l']+cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,env=env)
     try:out,err=proc.communicate(timeout=30);status='ok' if proc.returncode==0 else 'error'
     except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate();status='timeout'
     elapsed=time.monotonic()-start; match=re.search(r'(\d+)\s+maximum resident set size',err);rss=int(match.group(1)) if match else None;pred=[];same=None;correct=None
     if status=='ok':
      try:
       decoded=json.loads(out);pred=decoded['holdout_trace'] if impl=='lana' else decoded['predictions']; assert [x['id'] for x in pred]==[x['id'] for x in data['holdout']];same=pred==prior[impl]['predictions'];correct=sum(x['prediction']==x['target'] for x in pred)
      except Exception as e:status='invalid-output';err+=f'\n{e!r}'
     item={'dataset':name,'split':seed,'depth':depth,'iteration':iteration,'phase':'warmup' if iteration==0 else 'measured','implementation':impl,'status':status,'exit_code':proc.returncode,'seconds':elapsed,'peak_rss_bytes':rss,'correct':correct,'count':len(pred),'matches_previous_predictions':same,'predictions':pred,'stderr':err,'command':cmd};records.append(item)
     with (dest/'measurements.jsonl').open('a') as f:f.write(json.dumps(item)+'\n')
    print(f'{name} {seed} depth={depth} iteration={iteration} complete',flush=True)
print('FINISHED',len(records),flush=True)
