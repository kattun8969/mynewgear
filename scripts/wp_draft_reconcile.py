#!/usr/bin/env python3
"""Read-only WP draft reconciliation; no customer content or credentials in logs."""
import json,sys
from wp_sync import WP
SLUGS=["mng-preview-jcm800verocity","mng-preview-home-discovery-tags","mng-preview-mng-overdrive-guide-sample","mng-rest-content-diagnostic"]
def main():
 w=WP()
 res=[]
 for s in SLUGS:
  for path in ["posts","pages"]:
   try:
    items=w.call("GET",f"/{path}",params={"context":"edit","status":"any","slug":s,"per_page":20})
    res.append({"slug":s,"type":path,"found":len(items),"ids":[x["id"] for x in items],"statuses":[x["status"] for x in items]})
   except Exception as exc:
    res.append({"slug":s,"type":path,"error":str(exc)[:90]})
 print(json.dumps({"read_only":True,"checks":res},ensure_ascii=False,indent=2))
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("ERROR:",str(e)[:150],file=sys.stderr);sys.exit(1)
