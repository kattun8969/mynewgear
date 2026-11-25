#!/usr/bin/env python3
"""Compile editorial Markdown into safe review-only HTML, leaving originals untouched.

Never publishes. Editor-only placeholder lines are excluded; real links and original
purchase comparisons remain. Output is a local article.html for the private draft.
"""
import json,re,sys
from pathlib import Path
from html import escape
import markdown

def compile_article(manifest_path):
    path=Path(manifest_path).resolve()
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind")!="post":
        raise ValueError("Not a post manifest")
    if not data.get("markdown_source"):
        return
    source=(path.parent/data["markdown_source"]).resolve()
    if not source.is_relative_to(Path("content/wp-manifests").resolve()):
        raise ValueError("Unsafe markdown source")
    lines=[]
    for line in source.read_text(encoding="utf-8").splitlines():
        # Editorial production markers are not visitor-facing copy.
        if re.match(r"^\s*>\s*【(?:画像|商品カード|動画|②編集|編集|公開後|WP|Work)",line):
            continue
        if re.match(r"^\s*<!--",line):
            continue
        lines.append(line)
    # WP template renders the post title, so omit the first Markdown H1.
    for index, item in enumerate(lines):
        if item.startswith("# "):
            lines.pop(index)
            break
    raw="\n".join(lines)
    raw=re.sub(r"(?m)^>\s*【[^】]+】.*\n?","",raw)
    html=markdown.markdown(raw,extensions=["tables","fenced_code","sane_lists"],output_format="html")
    # Keep wide comparison tables inside a horizontal scroll area on small phones.
    html = re.sub(
        r"(<table\b[^>]*>[\s\S]*?</table>)",
        r'<div class="mng-buyers-table-scroll" style="max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch">\1</div>',
        html,
        flags=re.I,
    )
    if len(html)<500 or "TODO" in html or "【画像" in html or "【商品カード" in html:
        raise ValueError("Unresolved placeholder or too-short article")
    intro='<p class="mng-pr-disclosure">PR：本記事にはアフィリエイト広告が含まれる場合があります。</p>\n'
    (path.parent/data["content_file"]).write_text(intro+html+"\n",encoding="utf-8")
    print("BUILT "+str(path.parent/data["content_file"])+" length="+str(len(html)))

if __name__=="__main__":
    try:compile_article(sys.argv[1])
    except Exception as exc:
        print("BUILD_ERROR: "+str(exc),file=sys.stderr)
        sys.exit(1)
