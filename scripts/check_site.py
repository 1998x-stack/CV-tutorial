#!/usr/bin/env python3
"""Dependency-free static site audit; run from any working directory."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json, re, sys, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.headings=[]; self.ids=[]; self.images=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag in {"a","link"} and "href" in a: self.links.append(a["href"])
        if tag in {"script","img"} and "src" in a: self.links.append(a["src"])
        if tag == "img": self.images.append(a)
        if tag == "h1": self.headings.append(tag)
def check():
    errors=[]
    def bad(msg): errors.append(msg)
    chapters=json.loads((SITE/"courses.json").read_text(encoding="utf-8"))["chapters"]
    nums=[c["num"] for c in chapters]
    if nums != [f"{i:02}" for i in range(1,29)]: bad("courses.json: chapter numbers must be 01–28 in order")
    if len(set(c["file"] for c in chapters))!=28: bad("courses.json: duplicate chapter paths")
    for c in chapters:
        if not (SITE/c["file"]).is_file(): bad("missing chapter: "+c["file"])
    home_html=(SITE/"index.html").read_text(encoding="utf-8")
    if home_html.count('class="state"') != 25: bad("home: exactly 25 chapters should be visibly refined")
    files=[SITE/"index.html"]+sorted((SITE/"chapters").glob("*.html"))
    for file in files:
        html=file.read_text(encoding="utf-8")
        p=Page(); p.feed(html)
        if file.name!="index.html" and len(p.headings)!=1 and file.name in {f"{i:02}.html" for i in range(1,26)}:
            bad(str(file.relative_to(ROOT))+": expected exactly one H1")
        if file.parent.name=="chapters" and file.name in {f"{i:02}.html" for i in range(6,26)}:
            n=int(file.stem)
            if html.count("<figure>") < (4 if n in (10,14,15,20,21,22,23,24,25) else 3): bad(f"{file.name}: insufficient illustrations")
            if "<math " not in html: bad(f"{file.name}: MathML equation missing")
            if "<pre>" not in html or "assert " not in html: bad(f"{file.name}: runnable test/assertion missing")
            for image in p.images:
                if not image.get("alt"): bad(f"{file.name}: figure image missing meaningful alt")
        if len(p.ids)!=len(set(p.ids)): bad(str(file.relative_to(ROOT))+": duplicate element IDs")
        if file.parent.name=="chapters" and file.name in {f"{i:02}.html" for i in range(1,26)}:
            for link in p.links:
                if link.startswith("#") and link[1:] not in p.ids: bad(f"{file.name}: broken local anchor {link}")
        for link in p.links:
            if link.startswith(("https:","http:","mailto:","tel:","javascript:","data:","#")): continue
            path=unquote(urlsplit(link).path)
            if not path: continue
            if not (file.parent/path).exists(): bad(f"{file.relative_to(ROOT)}: missing relative reference {link}")
    svgfiles=list((SITE/"assets/svg").glob("*.svg"))
    if len(svgfiles)<85: bad("expected at least 85 SVGs (home + chapters 01–25, including detection, segmentation and deployment diagrams)")
    for f in svgfiles:
        try:
            node=ET.parse(f).getroot()
            if not node.tag.endswith("svg") or not node.attrib.get("viewBox"): bad(f"{f.name}: SVG/viewBox missing")
            titles=[e for e in node.iter() if e.tag.endswith("title")]
            desc=[e for e in node.iter() if e.tag.endswith("desc")]
            if not titles or not desc: bad(f"{f.name}: accessible title/desc missing")
        except ET.ParseError as ex: bad(f"{f.name}: invalid XML {ex}")
    for n in range(1,29):
        old=ROOT/f"{n:02}.html"
        if not old.exists() or f"docs/chapters/{n:02}.html" not in old.read_text(encoding="utf8"): bad(f"legacy redirect missing for {n:02}")
    return files,svgfiles,errors
if __name__=="__main__":
    files,svgfiles,errors=check()
    print(f"Audit: {len(files)} HTML, {len(svgfiles)} SVG, 28 chapter entries")
    if errors:
        print("\n".join("ERROR "+e for e in errors))
        sys.exit(1)
    print("PASS static references and SVG/XML contracts")
