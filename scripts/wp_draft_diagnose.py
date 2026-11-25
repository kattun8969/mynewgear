#!/usr/bin/env python3
"""WordPress REST write diagnostic. Never publishes or modifies production posts.
Test small draft payload, then larger plain-text payload, then sanitized HTML sample.
No WP response bodies or secrets printed.
"""
import json, os, sys, urllib.error
from wp_sync import WP

def run():
    wp=WP()
    me=wp.call("GET","/users/me",params={"context":"edit"})
    result={"authenticated_user_id":me.get("id"),"roles":me.get("roles",[]),"tests":[]}
    # Explicit limited, non-public test posts. No publish or page writes.
    fixtures=[
        ("small", "<p>GitHub WordPress REST diagnostic: private draft. No customer content.</p>"),
        ("large_plain", "<p>" + "WordPress draft diagnostic text. " * 220 + "</p>"),
        ("structured_html", '<section class="mng-diagnostic"><h2>WordPress下書き確認</h2><p>HTML構造と日本語を含む投稿テストです。</p><ul><li>ペダル</li><li>ギター</li></ul></section>')
    ]
    for name, body in fixtures:
        try:
            payload={"status":"draft","title":"[接続診断] WordPress REST "+name,"slug":"mng-rest-diagnostic-"+name,"content":body}
            # If a previous test exists, update ONLY the specifically named private diagnostic post.
            found=wp.call("GET","/posts",params={"slug":payload["slug"],"context":"edit","status":"any","per_page":10})
            if len(found)>1: raise ValueError("ambiguous diagnostic post slug")
            if found:
                if found[0].get("status")!="draft":raise ValueError("diagnostic post not draft")
                post=wp.call("POST","/posts/"+str(found[0]["id"]),payload)
            else:post=wp.call("POST","/posts",payload)
            result["tests"].append({"case":name,"success":True,"draft_id":post.get("id")})
        except Exception as exc:
            result["tests"].append({"case":name,"success":False,"error":str(exc)[:140]})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    # Testing failures are expected diagnostics; report outcome without exiting nonzero.
if __name__=="__main__":
    try:run()
    except Exception as exc:
        print(json.dumps({"diagnostic_setup_error":str(exc)[:180]}))
        sys.exit(1)

# Trigger: safe diagnosis, 2026-11-25.
