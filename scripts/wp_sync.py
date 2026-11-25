#!/usr/bin/env python3
"""Restricted WordPress REST publisher for mynewgear.cyou.

Modes:
 check     validate local JSON only; no credentials/network
 preview   create/update a separate private draft for review; never touch the live post
 publish   update the intended post (requires publish_ready=true in manifest)
 taxonomy  create missing curated tags + append them to identified posts (no term deletions)

Uses only WordPress Application Password via HTTPS, never writes credentials to logs.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = {"mynewgear.cyou", "www.mynewgear.cyou"}
MANIFEST_ROOT = Path("content/wp-manifests").resolve()
SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,100}$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_manifest(path):
    candidate = Path(path).resolve()
    require(candidate.is_relative_to(MANIFEST_ROOT), "Manifest must live under content/wp-manifests/")
    require(candidate.suffix == ".json", "Manifest must be .json")
    data = json.loads(candidate.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "Manifest must be an object")
    kind = data.get("kind")
    require(kind in {"post", "taxonomy"}, "kind must be post or taxonomy")
    if kind == "post":
        require(isinstance(data.get("title"), str) and data["title"].strip(), "title is required")
        require(isinstance(data.get("slug"), str) and SAFE_SLUG.fullmatch(data["slug"]), "safe slug is required")
        require(isinstance(data.get("content_file"), str), "content_file required")
        content_path = (candidate.parent / data["content_file"]).resolve()
        require(content_path.is_relative_to(MANIFEST_ROOT), "Content path must stay in content/wp-manifests/")
        require(content_path.suffix in {".html", ".txt"}, "Content must be HTML or text")
        require(content_path.is_file(), "Content file missing")
        data["_content"] = content_path.read_text(encoding="utf-8")
        require(len(data["_content"].strip()) >= 100, "Content too short")
        require(not re.search(r"【編集用|公開前に削除|TODO|href=[\"']#[\"']", data["_content"]), "Unresolved editor placeholder/link")
        require(isinstance(data.get("publish_ready", False), bool), "publish_ready must be boolean")
        if "post_id" in data:
            require(type(data["post_id"]) is int and data["post_id"] > 0, "post_id must be positive integer")
        if "categories" in data:
            require(isinstance(data["categories"], list), "categories must be a list")
        if "tags" in data:
            require(isinstance(data["tags"], list), "tags must be a list")
        for term in data.get("categories", []) + data.get("tags", []):
            require(isinstance(term, str) and SAFE_SLUG.fullmatch(term), "taxonomy slugs must be safe")
    else:
        require(isinstance(data.get("tags"), list) and data["tags"], "tags array required")
        for term in data["tags"]:
            require(isinstance(term, dict), "tags entries must be objects")
            require(isinstance(term.get("name"), str) and term["name"].strip(), "tag.name required")
            require(isinstance(term.get("slug"), str) and SAFE_SLUG.fullmatch(term["slug"]), "safe tag slug required")
        for mapping in data.get("assignments", []):
            require(isinstance(mapping, dict), "assignments must be objects")
            require(isinstance(mapping.get("post_slug"), str) and SAFE_SLUG.fullmatch(mapping["post_slug"]), "post_slug required")
            require(isinstance(mapping.get("tags"), list), "assignment tags list required")
    return data


class WP:
    def __init__(self):
        raw = os.environ.get("WP_SITE_URL", "").rstrip("/")
        parsed = urllib.parse.urlparse(raw)
        require(parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS and parsed.path in {"", "/"}, "WP_SITE_URL must be https://mynewgear.cyou")
        user = os.environ.get("WP_USERNAME", "")
        secret = os.environ.get("WP_APP_PASSWORD", "")
        require(user and secret, "WP_USERNAME and WP_APP_PASSWORD required via GitHub Secrets")
        self.base = raw + "/wp-json/wp/v2"
        self.auth = "Basic " + base64.b64encode((user + ":" + secret).encode("utf-8")).decode("ascii")

    def call(self, method, endpoint, payload=None, params=None):
        # Never allow an absolute or protocol-relative URL supplied by a manifest.
        require(endpoint.startswith("/") and not endpoint.startswith("//"), "unsafe endpoint")
        url = self.base + endpoint
        if params:
            url += "?" + urllib.parse.urlencode(params)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Authorization": self.auth, "Accept": "application/json", "User-Agent": "mng-github-publisher/1.0"}
        if body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                result = response.read()
                return json.loads(result) if result else {}
        except urllib.error.HTTPError as e:
            # Avoid printing server responses: some security plugins echo request data.
            raise RuntimeError(f"WordPress REST {method} {endpoint} returned HTTP {e.code}") from None
        except urllib.error.URLError:
            raise RuntimeError("WordPress REST endpoint unreachable; confirm hosting REST/firewall settings") from None

    def term_id(self, typ, slug, create=False, name=None):
        results = self.call("GET", "/" + typ, params={"slug": slug, "per_page": 100})
        require(len(results) <= 1, f"ambiguous {typ} slug: {slug}")
        if results:
            return results[0]["id"]
        require(create, f"Missing {typ} slug: {slug}. Run taxonomy sync or create it in WP.")
        created = self.call("POST", "/" + typ, {"name": name or slug, "slug": slug})
        return created["id"]

    def find_post(self, slug, post_id=None):
        if post_id:
            found = self.call("GET", f"/posts/{post_id}", params={"context": "edit"})
            require(found["slug"] == slug, f"post_id {post_id} does not match slug {slug}")
            return found
        candidates = self.call("GET", "/posts", params={"slug": slug, "context": "edit", "status": "any", "per_page": 100})
        require(len(candidates) <= 1, f"ambiguous post slug: {slug}")
        return candidates[0] if candidates else None


def post_payload(wp, manifest):
    data = {"title": manifest["title"], "content": manifest["_content"]}
    if "excerpt" in manifest:
        require(isinstance(manifest["excerpt"], str), "excerpt must be text")
        data["excerpt"] = manifest["excerpt"]
    if "categories" in manifest:
        data["categories"] = [wp.term_id("categories", x) for x in manifest["categories"]]
    if "tags" in manifest:
        data["tags"] = [wp.term_id("tags", x) for x in manifest["tags"]]
    return data


def post_sync(wp, manifest, mode):
    slug = manifest["slug"]
    data = post_payload(wp, manifest)
    live = wp.find_post(slug, manifest.get("post_id"))
    if mode == "preview":
        preview_slug = ("mng-preview-" + slug)[:100]
        preview = wp.find_post(preview_slug)
        data.update({"status": "draft", "slug": preview_slug, "title": "[確認用] " + manifest["title"]})
        if preview:
            result = wp.call("POST", f"/posts/{preview['id']}", data)
        else:
            result = wp.call("POST", "/posts", data)
        print(f"PREVIEW_DRAFT post_id={result['id']} target={slug} (live post unchanged)")
        return
    require(mode == "publish", "unsupported mode")
    require(manifest.get("publish_ready") is True, "publish_ready=true required")
    if live:
        # Avoid unintended rewrite of a manually edited post without an explicit ID.
        require("post_id" in manifest, "publishing existing content requires explicit post_id")
        if "expected_modified_gmt" in manifest:
            require(live.get("modified_gmt") == manifest["expected_modified_gmt"], "Live post was edited since approval")
        require(live.get("status") in {"publish", "draft", "pending", "private"}, "Unexpected post status")
        data["status"] = "publish"
        result = wp.call("POST", f"/posts/{live['id']}", data)
    else:
        require(manifest.get("allow_create") is True, "New publication requires allow_create=true")
        data.update({"slug": slug, "status": "publish"})
        result = wp.call("POST", "/posts", data)
    print(f"PUBLISHED post_id={result['id']} url={result.get('link','')}")


def taxonomy_sync(wp, manifest):
    for tag in manifest["tags"]:
        ident = wp.term_id("tags", tag["slug"], create=True, name=tag["name"])
        print(f"TAG {tag['slug']} id={ident}")
    for assignment in manifest.get("assignments", []):
        post = wp.find_post(assignment["post_slug"])
        require(post is not None, f"Missing post for tag assignment: {assignment['post_slug']}")
        require(post.get("status") == "publish", "Tag only published posts in this manifest")
        existing = set(post.get("tags", []))
        additions = {wp.term_id("tags", slug) for slug in assignment["tags"]}
        merged = sorted(existing | additions)
        if merged != sorted(existing):
            wp.call("POST", f"/posts/{post['id']}", {"tags": merged})
        print(f"TAGGED post={assignment['post_slug']} tags={len(merged)}")
    print("Taxonomies synced. No categories, tags or posts were deleted.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", required=True, choices=["check", "preview", "publish", "taxonomy"])
    args = parser.parse_args()
    data = load_manifest(args.manifest)
    if args.mode == "check":
        print(f"VALID {data['kind']} manifest: {args.manifest}")
        return
    require((args.mode == "taxonomy") == (data["kind"] == "taxonomy"), "mode and manifest kind mismatch")
    wp = WP()
    identity = wp.call("GET", "/users/me", params={"context": "edit"})
    print(f"Authenticated WP user id={identity['id']} on mynewgear.cyou")
    if data["kind"] == "taxonomy":
        taxonomy_sync(wp, data)
    else:
        post_sync(wp, data, args.mode)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
