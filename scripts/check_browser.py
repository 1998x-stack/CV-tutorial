#!/usr/bin/env python3
"""Headless browser contract for the static home and all 28 chapters.

Run after: python3 -m pip install playwright
           python3 -m playwright install chromium
Output: reports/browser/*.png and reports/browser/summary.json
"""
import json
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
OUT = ROOT / "reports/browser"
PATHS = ["index.html"] + [f"chapters/{i:02}.html" for i in range(1,29)]
WIDTHS = [1440, 768, 390, 360]

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors, checks = [], []
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for path in PATHS:
                for width in WIDTHS:
                    page = browser.new_page(viewport={"width":width,"height":900}, device_scale_factor=1)
                    js_errors = []
                    page.on("pageerror", lambda err: js_errors.append(str(err)))
                    # All assets must remain local; external requests are blocked for offline reading QA.
                    page.route("https://**", lambda route: route.abort())
                    response = page.goto(f"{base}/{path}", wait_until="load")
                    page.locator("h1").first.wait_for()
                    page.evaluate("document.fonts.ready")
                    page.locator("img").evaluate_all("(els)=>els.forEach(img=>img.loading='eager')")
                    page.wait_for_function(
                        "()=>Array.from(document.images).every(img=>img.complete&&img.naturalWidth>0)",
                        timeout=10000
                    )
                    page.evaluate("window.scrollTo(0,0)")
                    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                    images = page.locator("img").evaluate_all(
                        "(els)=>els.map(x=>({src:x.getAttribute('src'),ok:x.complete&&x.naturalWidth>0}))")
                    math_geo = page.locator("math").evaluate_all(
                        "(els)=>els.map(x=>({width:x.getBoundingClientRect().width,height:x.getBoundingClientRect().height,ns:x.namespaceURI}))")
                    target = OUT / (path.replace("/", "-").replace(".html", "")+f"-{width}.png")
                    page.screenshot(path=str(target), full_page=False)
                    label = f"{path}@{width}"
                    checks.append({"page":path,"width":width,"overflow_px":overflow,
                                   "images":len(images),"mathml":len(math_geo),"screenshot":target.name})
                    if response is None or response.status != 200:
                        errors.append(f"{label}: HTTP {response.status if response else 'none'}")
                    if overflow > 1:
                        offenders=page.evaluate("""() => Array.from(document.querySelectorAll('body *'))
                          .map(x=>({tag:x.tagName,cls:x.className?.baseVal||x.className||'',
                            right:Math.round(x.getBoundingClientRect().right),
                            width:Math.round(x.getBoundingClientRect().width)}))
                          .filter(x=>x.right>innerWidth+1).slice(0,6)""")
                        errors.append(f"{label}: horizontal document overflow {overflow}px; offenders={offenders}")
                    if page.locator("h1").count() != 1:
                        errors.append(f"{label}: exactly one H1 required")
                    if any(not x["ok"] for x in images):
                        errors.append(f"{label}: broken images {images}")
                    if any(x["width"]<=0 or x["height"]<=0 for x in math_geo):
                        errors.append(f"{label}: MathML has zero geometry")
                    if any(x["ns"] != "http://www.w3.org/1998/Math/MathML" for x in math_geo):
                        errors.append(f"{label}: MathML namespace incorrect")
                    if page.locator("svg math").count():
                        errors.append(f"{label}: MathML nested inside SVG")
                    if js_errors:
                        errors.append(f"{label}: page errors {js_errors}")
                    if width==390 and path!="index.html":
                        page.keyboard.press("Tab")
                        if not page.evaluate("document.activeElement.classList.contains('skip')"):
                            errors.append(f"{label}: skip link is not first keyboard target")
                        first = page.locator("figure").first
                        if first.count():
                            first.scroll_into_view_if_needed()
                            target = OUT/(path.replace("/", "-").replace(".html", "")+"-figure-390.png")
                            page.screenshot(path=str(target), full_page=False)
                    if width==390 and path=="index.html":
                        search=page.locator("#search")
                        search.fill("ResNet")
                        shown=page.locator(".card:visible").count()
                        if shown!=1:errors.append(f"homepage filter: expected 1, got {shown}")
                        search.fill("")
                        if page.locator(".card:visible").count()!=28:
                            errors.append("homepage filter: clear did not restore all cards")
                    if width==390 and path!="index.html":
                        summary=page.locator("details summary").first
                        if summary.count():
                            summary.click()
                            if not summary.evaluate("(el)=>el.parentElement.open"):
                                errors.append(f"{label}: details failed to open")
                    if width==390 and path=="chapters/26.html":
                        slider=page.locator("#mask-ratio")
                        before=page.locator("#mask-output").inner_text()
                        slider.focus()
                        page.keyboard.press("ArrowLeft")
                        after=page.locator("#mask-output").inner_text()
                        if before==after or "50%" not in after or "8 / 16" not in after:
                            errors.append(f"{label}: MAE mask ratio interaction did not change visible token count")
                        page.keyboard.press("ArrowRight")
                        restored=page.locator("#mask-output").inner_text()
                        if restored!=before:
                            errors.append(f"{label}: MAE mask ratio reset did not restore default")
                        aria=page.locator("#mask-output").get_attribute("aria-live")
                        if aria!="polite":
                            errors.append(f"{label}: MAE interaction lacks live output")
                    if width==1440:
                        page.emulate_media(media="print")
                        print_overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                        if print_overflow > 1:
                            errors.append(f"{label}: print layout overflows {print_overflow}px")
                        page.emulate_media(media="screen", reduced_motion="reduce")
                        if not page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"):
                            errors.append(f"{label}: reduced-motion preference was not applied")
                        page.emulate_media(media="screen", reduced_motion="no-preference")
                    page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result={"pages":len(PATHS),"viewports":WIDTHS,"checks":checks,"failures":errors}
    (OUT/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    print(f"Browser QA: {len(checks)} checks; {len(errors)} failures")
    if errors:raise SystemExit("\n".join(errors))
    print("PASS browser width, images, MathML, page errors and interactions")
if __name__=="__main__":run()
