#!/usr/bin/env python3
"""Create a private DRAFT copy of TOP with sound/budget links corrected.

Never modifies the published homepage. Fails closed on unknown markup.
"""
import hashlib
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from wp_sync import WP, require

LABELS = {
  "軽い歪み": "sound-light-drive",
  "迫力のある歪み": "sound-heavy-drive",
  "ファズ": "sound-fuzz",
  "ディレイ・残響": "sound-delay-reverb",
  "マルチエフェクター": "sound-multi-effects",
  "1万円前後": "budget-around-10000",
  "3万円前後": "budget-around-30000",
  "5万円前後": "budget-around-50000",
}
PAGE_CLASS = re.compile(r"page-id-([0-9]+)")
ANCHOR = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<label>[^<]+)</a>", re.I)
HREF = re.compile(r"\bhref\s*=\s*(?P<q>[\"'])(?P<url>.*?)(?P=q)", re.I)

class Body(HTMLParser):
  def __init__(self):
    super().__init__(); self.classes = ""
  def handle_starttag(self, tag, attrs):
    if tag == "body": self.classes = dict(attrs).get("class", "")

def main():
  wp=WP()
  req=urllib.request.Request("https://mynewgear.cyou/", headers={"User-Agent":"MyNewGear-SafePreview/1.0"})
  with urllib.request.urlopen(req, timeout=25) as r:
    html=r.read(1800000).decode("utf-8","replace")
  parser=Body(); parser.feed(html)
  classes=parser.classes.split()
  page_ids=[int(PAGE_CLASS.fullmatch(cls).group(1)) for cls in classes if PAGE_CLASS.fullmatch(cls)]
  require(len(page_ids)==1, "No unique static WordPress page id: homepage may be theme-generated")
  original=wp.call("GET",f"/pages/{page_ids[0]}",params={"context":"edit"})
  require(original.get("status")=="publish", "Homepage is not a published static page")
  raw=original.get("content",{}).get("raw","")
  require(len(raw)>=300, "Homepage raw content unexpectedly short")
  modified=original.get("modified_gmt")
  require(modified, "Homepage revision timestamp missing")
  terms={}
  for label,slug in LABELS.items():
    options=wp.call("GET","/tags",params={"slug":slug,"per_page":100})
    require(len(options)==1, f"Expected one tag for {slug}; run taxonomy sync first")
    term=options[0]
    terms[label]=(str(term.get("link","")),int(term.get("count",0)))
    require(term["link"].startswith("https://mynewgear.cyou/"), "Tag URL outside intended site")

  changed=[]
  def fix(match):
    attrs=match.group("attrs")
    label=" ".join(match.group("label").split())
    if label not in LABELS:return match.group(0)
    href=HREF.search(attrs)
    require(href is not None, f"Missing href on TOP chip: {label}")
    link,count=terms[label]
    changed.append({"label":label,"old":href.group("url")[:100],"new":link if count else "(disabled)"})
    if count:
      # Preserve all existing class/style/data attributes, replace href only.
      fixed=attrs[:href.start("url")]+link.replace("&","&amp;")+attrs[href.end("url"):]
      return "<a"+fixed+">"+match.group("label")+"</a>"
    # No matching published article: render a non-link. Keep styling and add aria-disabled.
    attrs_without_link=attrs[:href.start()]+attrs[href.end():]
    return "<span"+attrs_without_link+' aria-disabled="true" title="記事準備中">'+match.group("label")+"</span>"
  updated=ANCHOR.sub(fix,raw)
  require(len(changed)>=5, "Fewer than five expected TOP chips in raw page content; abort")
  require(len({x["label"] for x in changed})==len(changed), "Duplicated link label, abort instead of partial rewrite")
  require(raw!=updated,"No changes needed")
  require(len(updated)>len(raw)*0.80, "Unexpectedly large content change")

  # Double-check WP homepage has not changed during inspection.
  second=wp.call("GET",f"/pages/{page_ids[0]}",params={"context":"edit"})
  require(second.get("modified_gmt")==modified, "Homepage changed while preparing preview")
  draft_slug="mng-preview-home-discovery-tags"
  matches=wp.call("GET","/pages",params={"slug":draft_slug,"status":"any","context":"edit","per_page":50})
  require(len(matches)<=1,"Ambiguous preview page")
  data={"title":"[確認用] TOP 音色・予算リンク改善","slug":draft_slug,"status":"draft","content":updated}
  if matches:result=wp.call("POST",f"/pages/{matches[0]['id']}",data)
  else:result=wp.call("POST","/pages",data)
  print(json.dumps({
    "status":"private_draft_created","draft_id":result["id"],"draft_edit_link":f"https://mynewgear.cyou/wp-admin/post.php?post={result['id']}&action=edit",
    "original_page_id":page_ids[0],"original_modified_gmt":modified,"original_sha256":hashlib.sha256(raw.encode()).hexdigest(),
    "changed_links":changed,"published_homepage_unchanged":True
  },ensure_ascii=False,indent=2))

if __name__=="__main__":
  try:main()
  except Exception as e:
    print("SAFE_PREVIEW_STOP: "+str(e)[:350],file=sys.stderr)
    sys.exit(1)

# One-time audit request: 2026-11-25. Safe preview only.
