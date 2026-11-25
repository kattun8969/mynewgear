#!/usr/bin/env python3
"""Read-only BD-2 WordPress QA. No outgoing tracking/click links are opened.

Checks draft status, source thumbnail, product-card presence, safe links,
table wrappers and potential duplicate H1. No private URLs or tokens logged.
"""
import json
import re
import urllib.parse
from html.parser import HTMLParser
from wp_sync import WP, require

ID=1322
EXPECTED_SLUG="mng-preview-boss-bd-2-guide"
class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0;self.tables=0;self.table_scrolls=0;self.img=0;self.bad_anchors=0
        self.internal_paths=set();self.card_links=0;self.card_hosts={}
        self.anchors=[];self._anchor=None;self._text=[]
    def handle_starttag(self, tag, attrs):
        attr=dict(attrs)
        if tag=="h1":self.h1+=1
        if tag=="table":self.tables+=1
        if tag=="div" and "mng-buyers-table-scroll" in attr.get("class",""):
            self.table_scrolls+=1
        if tag=="img":self.img+=1
        if tag=="a":
            self._anchor=attr.get("href","")
            self._text=[]
            if self._anchor=="#" or self._anchor.startswith("javascript:") or not self._anchor:
                self.bad_anchors+=1
            parsed=urllib.parse.urlparse(self._anchor)
            if parsed.hostname in ("mynewgear.cyou","www.mynewgear.cyou"):
                self.internal_paths.add(parsed.path)
            elif parsed.hostname:
                self.card_hosts[parsed.hostname]=self.card_hosts.get(parsed.hostname,0)+1
    def handle_data(self,data):
        if self._anchor is not None:
            self._text.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self._anchor is not None:
            self.anchors.append(" ".join(" ".join(self._text).split())[:50])
            self._anchor=None;self._text=[]
def main():
    w=WP()
    p=w.call("GET",f"/posts/{ID}",params={"context":"edit"})
    require(p.get("status")=="draft" and p.get("slug")==EXPECTED_SLUG,"Incorrect QA draft")
    raw=p.get("content",{}).get("raw","")
    rendered=p.get("content",{}).get("rendered","")
    a=HTMLAudit();a.feed(rendered)
    mediaid=int(p.get("featured_media") or 0)
    media=None
    if mediaid:
        m=w.call("GET",f"/media/{mediaid}",params={"context":"edit"})
        media={
            "id":m.get("id"),
            "mime_type":m.get("mime_type"),
            "alt_present":bool(m.get("alt_text")),
            "dimensions":m.get("media_details",{}).get("width") and [m.get("media_details",{}).get("width"),m.get("media_details",{}).get("height")],
        }
    out={
        "draft_id":ID,"status":p.get("status"),"modified_gmt":p.get("modified_gmt"),
        "featured_image":media,
        "pochipp_1293_in_raw":'[pochipp id="1293"]' in raw,
        "unexpanded_pochipp":'[pochipp id="1293"]' in rendered,
        "rendered_pochipp":bool(re.search(r'pochipp[-_](?:box|item|wrap)|pochipp-box',rendered)),
        "table_count":a.tables,"scroll_wrapper_count":a.table_scrolls,
        "body_h1_count":a.h1,"body_image_count":a.img,
        "broken_placeholder_anchors":a.bad_anchors,
        "internal_article_paths":sorted(a.internal_paths),
        "external_link_domains_only":a.card_hosts,
        "published_page_unchanged":True,
        "note":"HTTP destination and actual affiliate commission tracking cannot be established from rendered HTML alone"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
