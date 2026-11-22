#!/usr/bin/env python3
"""Build one publishable Pages root from the canonical docs/ source."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
src, out = ROOT / "docs", ROOT / "_site"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(src, out)
for i in range(1, 29):
    n = f"{i:02}"
    alias = f"chapters/{n}.html"
    (out / f"{n}.html").write_text(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta http-equiv="refresh" content="0;url={alias}">'
        f'<link rel="canonical" href="{alias}">'
        f'<title>第{i}章 · 已迁移</title></head><body>'
        f'<p>请前往 <a href="{alias}">第{i}章</a>。</p>'
        '</body></html>', encoding="utf-8"
    )
assert (out / "index.html").exists()
assert len(list((out / "chapters").glob("[0-9][0-9].html"))) == 28
print(f"Built {out}: canonical root + 28 legacy aliases")
