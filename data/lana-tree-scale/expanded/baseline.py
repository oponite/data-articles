import json,sys
from sklearn.tree import DecisionTreeClassifier
d=json.load(open(sys.argv[1])); depth=int(sys.argv[2]); n=len(d["task"]["feature_schema"])
def xy(rows): return [[r["features"][f"x{i}"] for i in range(n)] for r in rows],[r["target"] for r in rows]
x,y=xy(d["train"]);h,z=xy(d["holdout"]);m=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=2,random_state=42);m.fit(x,y);pred=m.predict(h).tolist();print(json.dumps({"predictions":[{"id":r["id"],"prediction":bool(v),"target":r["target"]} for r,v in zip(d["holdout"],pred)]}))
