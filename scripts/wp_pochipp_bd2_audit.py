#!/usr/bin/env python3
"""Read-only discovery of Pochipp registry and candidate BD-2 product IDs.

Never prints affiliate URLs, credentials, meta fields or product configuration.
"""
import json
from wp_sync import WP

def run():
  wp=WP()
  out={"mode":"read_only","candidates":[],"rest_types":[]}
  types=wp.call("GET","/types",params={"context":"edit"})
  names=[(key,val) for key,val in types.items() if "pochipp" in key.lower() or "pochipp" in str(val.get("name","")).lower()]
  out["rest_types"]=[{"key":key,"rest_base":val.get("rest_base")} for key,val in names]
  endpoints=list(dict.fromkeys(["/pochipps"]+["/"+str(v.get("rest_base") or k) for k,v in names]))
  for endpoint in endpoints:
    try:
      posts=wp.call("GET",endpoint,params={"context":"edit","search":"BD-2","per_page":50,"status":"any"})
      for post in posts:
        name=post.get("title",{})
        if isinstance(name,dict):name=name.get("raw") or name.get("rendered") or ""
        # Only report title and WP internal ID, never links, meta, or ASP credentials.
        out["candidates"].append({"endpoint":endpoint,"id":post.get("id"),"title":str(name)[:110],"status":post.get("status")})
    except Exception as e:
      out.setdefault("endpoint_results",[]).append({"endpoint":endpoint,"error":str(e)[:110]})
  print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":run()
