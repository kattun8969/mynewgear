#!/usr/bin/env python3
"""Inspect the WordPress front page without modifying anything.

Prints only page ID, type, editable-status and public link targets; no content or secrets.
"""
import json
import re
import sys
from html.parser import HTMLParser
from wp_sync import WP

LABELS=("軽い歪み","迫力のある歪み","ファズ","ディレイ","マルチエフェクター","1万円","3万円","5万円")
class AnchorScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href=None
        self.text=[]
        self.matches=[]
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            self.href=dict(attrs).get("href","")
            self.text=[]
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag=="a" and self.href is not None:
            label=" ".join(" ".join(self.text).split())
            if any(q in label for q in LABELS):
                self.matches.append({"label":label[:60],"href":self.href[:180]})
            self.href=None
            self.text=[]

def main():
    wp=WP()
    settings=wp.call("GET","/settings")
    page_id=int(settings.get("page_on_front") or 0)
    page_mode=settings.get("show_on_front")
    output={"show_on_front":page_mode,"page_on_front":page_id,"source":"WordPress authenticated REST only"}
    if page_mode=="page" and page_id:
        page=wp.call("GET",f"/pages/{page_id}",params={"context":"edit"})
        content=page.get("content",{}).get("raw","")
        scanner=AnchorScan()
        scanner.feed(content)
        output.update({"type":"page","status":page.get("status"),"slug":page.get("slug"),"modified_gmt":page.get("modified_gmt"),"content_length":len(content),"anchors":scanner.matches})
    else:
        output["warning"]="Front page is not a static WP page. It may be a theme template and cannot be rewritten via the pages REST API."
    print(json.dumps(output,ensure_ascii=False,indent=2))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("INSPECTION_ERROR:",str(exc)[:220],file=sys.stderr)
        sys.exit(1)
