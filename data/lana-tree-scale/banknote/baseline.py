import json
from sklearn.tree import DecisionTreeClassifier
p='/tmp/lana-tree-scale/banknote/split.json'; d=json.load(open(p))
def xy(rows): return [[r['features'][f'x{i}'] for i in range(4)] for r in rows],[r['target'] for r in rows]
x,y=xy(d['train']);h,z=xy(d['holdout']);m=DecisionTreeClassifier(max_depth=4,min_samples_leaf=2,random_state=42);m.fit(x,y);pred=m.predict(h).tolist()
print(json.dumps({'correct':sum(a==b for a,b in zip(pred,z)),'count':len(z),'accuracy':m.score(h,z),'predictions':pred}))
