#!/usr/bin/env python3
"""Read-only BD-2 draft Pochipp rendered-content inspection (no URL tokens printed)."""
import json, re, urllib.parse
from html.parser import HTMLParser
from wp_sync import WP

class Parser(HTMLParser):
 def __init__(self):
  super().__init__(); self.hosts={};self.images=0;self.links=0;self.bad_count=0
 def handle_starttag(self,tag,attrs):
  if tag=="img":self.images+=1
  if tag=="a":
   self.links+=1;href=dict(attrs).get("href","")
   host=urllib.parse.urlparse(href).hostname or ""
   if host and host.endswith(("amazon.co.jp","rakuten.co.jp","yahoo.co.jp","soundhouse.co.jp","moshimo.com","valuecommerce.ne.jp","accesstrade.net")):self.hosts[host]=self.hosts.get(host,0)+1

wp=WP()
p=wp.call("GET","/posts/1322",params={"context":"edit"})
assert p.get("status")=="draft" and p.get("slug")=="mng-preview-boss-bd-2-guide","Not isolated BD2 draft"
raw=p["content"].get("raw","")
html=p["content"].get("rendered","")
parser=Parser();parser.feed(html)
print(json.dumps({
 "post_id":1322,"status":"draft","raw_has_product_id_1293":'[pochipp id="1293"]' in raw,
 "rendered_has_pochipp_markup":bool(re.search(r'pochipp[-_](?:box|item|wrap)|pochipp-box',html)),
 "rendered_has_unexpanded_shortcode":'[pochipp id="1293"]' in html,
 "rendered_image_count":parser.images,"rendered_anchor_count":parser.links,
 "known_store_hosts_only":parser.hosts,"public_post_changed":False
},ensure_ascii=False,indent=2))

# first BD2 rendered product-card audit
