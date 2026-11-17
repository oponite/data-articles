import csv,random,json,hashlib,pathlib,collections
p=pathlib.Path('/tmp/lana-tree-scale/banknote'); raw=(p/'data.csv').read_bytes();assert hashlib.sha256(raw).hexdigest()=='d0539aaed2139ba7a587b3e34fb345ce503ff7d5d33dbf9912d8e195ce425cb9'
rows=list(csv.reader(raw.decode().splitlines()));groups={}
for i,r in enumerate(rows):
 key=tuple(float(x) for x in r[:4]); groups.setdefault(key,[]).append({'id':f'row-{i:04d}','features':{f'x{j}':v for j,v in enumerate(key)},'target':bool(int(r[4]))})
rng=random.Random(42);train=[];test=[]
for label in (False,True):
 g=[v for v in groups.values() if v[0]['target']==label];rng.shuffle(g);limit=round(sum(map(len,g))*0.2);count=0
 for group in g:
  if count<limit: test.extend(group);count+=len(group)
  else: train.extend(group)
assert not ({tuple(x['features'].values()) for x in train}&{tuple(x['features'].values()) for x in test})
task={'id':'banknote','feature_schema':[{'name':f'x{i}','kind':'number','nullable':False,'categories':[]} for i in range(4)],'problem':'classification','labels':[False,True]}
data={'task':task,'train':train,'holdout':test};(p/'split.json').write_text(json.dumps(data,separators=(',',':')))
print(json.dumps({'train':len(train),'test':len(test),'train_labels':dict(collections.Counter(str(x['target']) for x in train)),'test_labels':dict(collections.Counter(str(x['target']) for x in test)),'unique_rows':len(groups),'split_sha256':hashlib.sha256((p/'split.json').read_bytes()).hexdigest()}))
