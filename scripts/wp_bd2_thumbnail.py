#!/usr/bin/env python3
"""Upload original editorial PNG and attach it to the isolated BD-2 draft.

Safety:
 - Creates/updates media by exact slug; never publishes posts.
 - Only updates featured_media of known preview draft ID 1322.
 - WordPress product photos/affiliate settings remain untouched.
 - No credentials, source URLs, or private post content printed.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from wp_sync import WP, require

IMAGE_SLUG="mng-bd2-guide-original-cover"
PREVIEW_ID=1322
def run():
    wp=WP()
    img=Path("build/bd2-cover.png")
    require(img.is_file() and img.stat().st_size > 20000,"Cover not rendered")
    draft=wp.call("GET",f"/posts/{PREVIEW_ID}",params={"context":"edit"})
    require(draft.get("status")=="draft" and draft.get("slug")=="mng-preview-boss-bd-2-guide",
            "Target is not the isolated BOSS BD-2 draft")
    media=wp.call("GET","/media",params={"search":IMAGE_SLUG,"context":"edit","per_page":50})
    exact=[x for x in media if x.get("slug")==IMAGE_SLUG]
    require(len(exact)<=1,"Ambiguous media slug, refusing to update")
    if exact:
        chosen=exact[0]
    else:
        url=wp.base+"/media"
        req=urllib.request.Request(
            url,data=img.read_bytes(),method="POST",
            headers={
                "Authorization":wp.auth,"Accept":"application/json",
                "Content-Type":"image/png",
                "Content-Disposition":'attachment; filename="mng-bd2-guide-original-cover.png"',
                "User-Agent":"mng-github-publisher/1.0"
            }
        )
        try:
            with urllib.request.urlopen(req,timeout=45) as response:
                chosen=json.loads(response.read())
        except urllib.error.HTTPError as ex:
            raise RuntimeError("WordPress media upload rejected: HTTP "+str(ex.code)) from None
        except urllib.error.URLError:
            raise RuntimeError("WordPress media upload unreachable") from None
        # Avoid duplicate media when the script is rerun.
        chosen=wp.call("POST",f"/media/{chosen['id']}",{
            "slug":IMAGE_SLUG,
            "title":"BD-2購入ガイド｜編集部オリジナル図",
            "alt_text":"BOSS BD-2購入ガイドの文字入りイラスト。青いエフェクターを抽象的に描いたもので実製品の写真ではありません。",
            "caption":"編集部作成のイメージイラスト。実際のBD-2本体写真とは異なります。"
        })
    image_id=chosen["id"]
    # Double-check target draft before any update; this never changes publication status.
    again=wp.call("GET",f"/posts/{PREVIEW_ID}",params={"context":"edit"})
    require(again.get("status")=="draft" and again.get("slug")=="mng-preview-boss-bd-2-guide",
            "Review draft changed while preparing image")
    attached=wp.call("POST",f"/posts/{PREVIEW_ID}",{"featured_media":image_id})
    require(attached.get("status")=="draft","Unexpected publication status after thumbnail set")
    print(json.dumps({"status":"draft_updated","post_id":PREVIEW_ID,"featured_media_id":image_id,
                      "media_reused":bool(exact),"image_dimensions":[1600,900],
                      "public_post_unchanged":True},ensure_ascii=False))

def comparison_diagram():
    """Register original three-model comparison art in WP media, without editing posts."""
    wp=WP()
    slug="mng-bd2-sd1-od3-visual"
    path=Path("build/bd2-drive-comparison.png")
    require(path.exists() and path.stat().st_size>10000,"Comparison illustration absent")
    rows=wp.call("GET","/media",params={"search":slug,"context":"edit","per_page":50})
    matches=[r for r in rows if r.get("slug")==slug]
    require(len(matches)<=1,"Ambiguous comparison media")
    if matches:
        item=matches[0]
    else:
        req=urllib.request.Request(wp.base+"/media",data=path.read_bytes(),method="POST",headers={
            "Authorization":wp.auth,"Content-Type":"image/png",
            "Content-Disposition":'attachment; filename="mng-bd2-sd1-od3-visual.png"'})
        try:
            with urllib.request.urlopen(req,timeout=45) as response:
                item=json.loads(response.read())
        except urllib.error.HTTPError as err:
            raise RuntimeError("WordPress media HTTP "+str(err.code)) from None
        item=wp.call("POST",f"/media/{item['id']}",{
            "slug":slug,"title":"BD-2・SD-1・OD-3の比較イラスト",
            "alt_text":"BD-2のタッチ、SD-1の中域、OD-3の太さを比較した編集部作成の模式図",
            "caption":"実際の商品写真ではなく編集部による比較図です。"})
    url=item.get("source_url","")
    require(url.startswith("https://mynewgear.cyou/"),"Unexpected image URL")
    print(json.dumps({"comparison_media_id":item["id"],"comparison_url":url,
                      "published_posts_changed":False},ensure_ascii=False))

if __name__=="__main__":
    try:
        run()
        comparison_diagram()
    except Exception as exc:
        print("MEDIA_QA_ERROR: "+str(exc)[:220],file=sys.stderr)
        sys.exit(1)
