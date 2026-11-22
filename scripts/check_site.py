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
        if not c.get("refined"): bad("all 28 chapters should be refined: "+c["num"])
    home_html=(SITE/"index.html").read_text(encoding="utf-8")
    if home_html.count('class="state"') != 28: bad("home: exactly 28 chapters should be visibly refined")
    if home_html.count('class="card"') != 28: bad("home: expected 28 static cards")
    for c in chapters:
        if f'href="{c["file"]}"' not in home_html: bad("home: missing card path "+c["file"])
    files=[SITE/"index.html"]+sorted((SITE/"chapters").glob("*.html"))
    for file in files:
        html=file.read_text(encoding="utf-8")
        p=Page(); p.feed(html)
        if file.name!="index.html" and len(p.headings)!=1 and file.name in {f"{i:02}.html" for i in range(1,29)}:
            bad(str(file.relative_to(ROOT))+": expected exactly one H1")
        if file.parent.name=="chapters" and file.name in {f"{i:02}.html" for i in range(1,6)}:
            if html.count("<figure>") < 5: bad(f"{file.name}: expected at least five substantive figures")
            if html.count("<pre><code>") < 2: bad(f"{file.name}: expected at least two executable examples")
            if "<math " not in html: bad(f"{file.name}: MathML equation missing")
            if html.count('class="equation" role="region" tabindex="0"') < html.count("<math "):
                bad(f"{file.name}: every display equation needs a focusable named region")
            for math_tag in re.findall(r"<math\b[^>]*>", html):
                if "aria-label=" not in math_tag:
                    bad(f"{file.name}: MathML expression lacks an accessible description")
            for image in p.images:
                if not image.get("alt"): bad(f"{file.name}: figure image missing meaningful alt")
            if html.count("<figcaption>") < html.count("<figure>"):
                bad(f"{file.name}: every figure needs a caption")
        if file.parent.name=="chapters" and file.name in {f"{i:02}.html" for i in range(6,29)}:
            n=int(file.stem)
            required = 5 if n >= 26 else (4 if n in (10,14,15,20,21,22,23,24,25) else 3)
            if html.count("<figure>") < required: bad(f"{file.name}: insufficient illustrations")
            if "<math " not in html: bad(f"{file.name}: MathML equation missing")
            if "<pre>" not in html or "assert " not in html: bad(f"{file.name}: runnable test/assertion missing")
            for image in p.images:
                if not image.get("alt"): bad(f"{file.name}: figure image missing meaningful alt")
        if len(p.ids)!=len(set(p.ids)): bad(str(file.relative_to(ROOT))+": duplicate element IDs")
        if file.parent.name=="chapters" and file.name in {f"{i:02}.html" for i in range(1,29)}:
            for link in p.links:
                if link.startswith("#") and link[1:] not in p.ids: bad(f"{file.name}: broken local anchor {link}")
        for link in p.links:
            if link.startswith(("https:","http:","mailto:","tel:","javascript:","data:","#")): continue
            path=unquote(urlsplit(link).path)
            if not path: continue
            if not (file.parent/path).exists(): bad(f"{file.relative_to(ROOT)}: missing relative reference {link}")
    foundation_evidence=json.loads((SITE/"evidence/01-05.json").read_text(encoding="utf-8"))["entries"]
    if len(foundation_evidence) < 25: bad("evidence: chapters 01–05 require at least 25 claim/source records")
    foundation_ids=set()
    for claim in foundation_evidence:
        if not claim.get("id") or claim.get("id") in foundation_ids: bad("foundation evidence: missing or duplicate ID "+str(claim.get("id")))
        foundation_ids.add(claim.get("id"))
        if claim.get("chapter") not in ("01","02","03","04","05"): bad("foundation evidence: invalid chapter "+str(claim.get("id")))
        if not claim.get("source_url","").startswith("https://"): bad("foundation evidence: source URL missing "+str(claim.get("id")))
        if not claim.get("locator"): bad("foundation evidence: locator missing "+str(claim.get("id")))
        if claim.get("status") not in ("verified","derived","illustrative"): bad("foundation evidence: invalid status "+str(claim.get("id")))
    evidence=json.loads((SITE/"evidence/26-28.json").read_text(encoding="utf-8"))["entries"]
    if len(evidence) < 18: bad("evidence: at least 18 source-linked records required for 26–28")
    ids=set()
    for claim in evidence:
        if claim.get("id") in ids: bad("evidence: duplicate claim ID "+str(claim.get("id")))
        ids.add(claim.get("id"))
        if claim.get("chapter") not in (26,27,28): bad("evidence: wrong chapter "+str(claim.get("id")))
        if claim.get("status") not in ("verified","derived","illustrative"): bad("evidence: invalid status "+str(claim.get("id")))
        if not claim.get("source_url","").startswith("https://"): bad("evidence: source URL missing "+str(claim.get("id")))
        if not claim.get("locator"): bad("evidence: source locator missing "+str(claim.get("id")))
    svgfiles=list((SITE/"assets/svg").glob("*.svg"))
    if len(svgfiles)<115: bad("expected at least 115 SVGs (home + chapters 01–28 after the foundation visual audit)")
    for f in svgfiles:
        try:
            node=ET.parse(f).getroot()
            if not node.tag.endswith("svg") or not node.attrib.get("viewBox"): bad(f"{f.name}: SVG/viewBox missing")
            titles=[e for e in node.iter() if e.tag.endswith("title")]
            desc=[e for e in node.iter() if e.tag.endswith("desc")]
            if not titles or not desc: bad(f"{f.name}: accessible title/desc missing")
            if f.name[:2] in {"01","02","03","04","05"}:
                texts=[e for e in node.iter() if e.tag.endswith("text")]
                if len(texts) < 5: bad(f"{f.name}: diagram has too few explanatory labels")
                for label in texts:
                    size=label.attrib.get("font-size")
                    if size is not None and float(size.replace("px","")) < 13:
                        bad(f"{f.name}: SVG label below 13px ({size})")
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
