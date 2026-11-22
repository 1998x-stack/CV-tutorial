#!/usr/bin/env python3
"""Execute the precise Python code blocks published in chapters 06–20.

Optional dependency: pip install torch (CPU build is sufficient).
The snippets are run in isolated namespaces; no external images or weights used.
"""
from html.parser import HTMLParser
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
class Snippets(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_pre = False
        self.in_code = False
        self.current = []
        self.snippets = []
    def handle_starttag(self, tag, attrs):
        if tag == "pre": self.in_pre = True
        elif tag == "code" and self.in_pre:
            self.in_code = True
            self.current = []
    def handle_data(self, text):
        if self.in_code: self.current.append(text)
    def handle_endtag(self, tag):
        if tag == "code" and self.in_code:
            self.snippets.append("".join(self.current))
            self.in_code = False
        elif tag == "pre": self.in_pre = False

def main():
    count=0
    for n in range(6,22):
        path=ROOT / "docs/chapters" / f"{n:02}.html"
        p=Snippets()
        p.feed(path.read_text(encoding="utf-8"))
        if not p.snippets: raise AssertionError(f"{path}: no runnable snippets")
        for j,source in enumerate(p.snippets,1):
            if "assert " not in source:raise AssertionError(f"{path}: snippet {j} lacks assertion")
            namespace={"__name__":"__main__"}
            with redirect_stdout(StringIO()):
                exec(compile(source,f"{path.name} snippet {j}","exec"),namespace)
            count+=1
            print(f"PASS chapter {n:02} snippet {j}")
    print(f"Executed {count} published code samples successfully")

if __name__=="__main__":main()
