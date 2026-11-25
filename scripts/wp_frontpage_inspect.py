#!/usr/bin/env python3
"""Read-only inspection of live homepage and its current sound/budget links."""
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from wp_sync import WP

LABELS=("軽い歪み","迫力のある歪み","ファズ","ディレイ","マルチエフェクター","1万円","3万円","5万円")

class Scan(HTMLParser):
    def __init__(self):
        super().__init__();self.href=None;self.buffer=[];self.links=[];self.body_classes=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="body":self.body_classes=a.get("class","")
        if tag=="a":self.href=a.get("href","");self.buffer=[]
    def handle_data(self,data):
        if self.href is not None:self.buffer.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.href is not None:
            label=" ".join(" ".join(self.buffer).split())
            if any(q in label for q in LABELS):
                self.links.append({"label":label[:85],"href":self.href[:200]})
            self.href=None;self.buffer=[]

def main():
    # Public HTML is readable without WordPress administrator-level /settings.
    req=urllib.request.Request("https://mynewgear.cyou/",headers={"User-Agent":"MyNewGear-ReadOnly-Audit/1.0"})
    with urllib.request.urlopen(req,timeout=25) as response:
        html=response.read(1800000).decode("utf-8","replace")
    scanner=Scan();scanner.feed(html)
    classes=scanner.body_classes.split()
    m=next((re.fullmatch(r"page-id-(\d+)",v) for v in classes if re.fullmatch(r"page-id-(\d+)",v)),None)
    result={"body_classes":classes[:25],"page_id_from_html":int(m.group(1)) if m else None,"links":scanner.links,"read_only":True}
    # Get raw editability only when a page ID exists; never require /settings.
    if m:
        try:
            wp=WP();page=wp.call("GET",f"/pages/{m.group(1)}",params={"context":"edit"})
            content=page.get("content",{}).get("raw","")
            result["page"]={"id":page.get("id"),"slug":page.get("slug"),"status":page.get("status"),"modified_gmt":page.get("modified_gmt"),"raw_content_length":len(content),"contains_discovery_shortcode":"[mng_discovery" in content,"contains_budget_heading":"予算から探す" in content}
        except Exception as ex:
            result["page_lookup"]="Not accessible by current REST user; may be theme/template-driven."
    else:
        result["page_lookup"]="No WordPress page-id body class; possibly theme/template-driven."
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("INSPECTION_ERROR: "+type(exc).__name__,file=sys.stderr)
        sys.exit(1)
