import json,sys,time,resource
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
p='/tmp/lana-tree-scale/data-10000-64.json'; data=json.load(open(p)); names=[x['name'] for x in data['task']['feature_schema']]
def xy(rows):return [[v['features'][k] for k in names] for v in rows],[v['target'] for v in rows]
x,y=xy(data['train']);h,z=xy(data['holdout']);family=sys.argv[1]
model={'tree':lambda:DecisionTreeClassifier(max_depth=4,min_samples_leaf=2,random_state=42),'forest':lambda:RandomForestClassifier(max_depth=4,min_samples_leaf=2,n_estimators=5,random_state=42,n_jobs=1),'boosted':lambda:GradientBoostingClassifier(max_depth=4,min_samples_leaf=2,n_estimators=5,learning_rate=0.1,random_state=42)}[family]()
t=time.monotonic();model.fit(x,y);elapsed=time.monotonic()-t
print(json.dumps({'family':family,'train_seconds':elapsed,'accuracy':model.score(h,z),'process_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
