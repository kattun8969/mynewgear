#!/usr/bin/env python3
"""Diagnose payload-specific 403 using isolated private drafts, never live posts."""
import json,re,sys
from pathlib import Path
from wp_sync import WP
P=Path("content/wp-manifests/verocity-yaohshiki/article.html")
def main():
  original=P.read_text(encoding="utf-8")
  nostyle=re.sub(r"<style\b[^>]*>[\s\S]*?</style>","",original,flags=re.I)
  nocomment=re.sub(r"<!--[\s\S]*?-->","",nostyle)
  noattr=re.sub(r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>",lambda m:"<"+m.group(1)+">",nocomment)
  wp=WP()
  tests=[("full",original),("without_style",nostyle),("without_style_comments",nocomment),("no_attributes",noattr)]
  slug="mng-rest-content-diagnostic"
  found=wp.call("GET","/posts",params={"slug":slug,"status":"any","context":"edit","per_page":10})
  if len(found)>1 or (found and found[0].get("status")!="draft"):
    raise ValueError("Existing diagnostic post is unsafe to update")
  id=found[0]["id"] if found else None
  report=[]
  for name,content in tests:
    try:
      payload={"title":"[接続診断] HTMLサンプル (非公開)","slug":slug,"status":"draft","content":content}
      result=wp.call("POST",("/posts/"+str(id)) if id else "/posts",payload)
      id=result["id"]
      report.append({"case":name,"allowed":True,"bytes":len(content),"draft_id":id})
    except Exception as exc:
      report.append({"case":name,"allowed":False,"bytes":len(content),"error":str(exc)[:120]})
  print(json.dumps({"tests":report,"published_content_changed":False},ensure_ascii=False,indent=2))
if __name__=="__main__":
 try:main()
 except Exception as exc:
  print(json.dumps({"setup_error":str(exc)[:140]},ensure_ascii=False))
  sys.exit(1)

# one-time safe run 2026-11-25
