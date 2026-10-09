"""Two-pass build: html -> pdf (Edge), read TOC link targets for page numbers, rebuild, check.
usage: python make.py <out.pdf>"""
import json
import subprocess
import sys
from pathlib import Path

import pymupdf

from build import PARTS

HERE = Path(__file__).parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html = HERE / "guide.html"
pdf = Path(sys.argv[1])
pages_json = HERE / "pages.json"


def render():
    subprocess.run([sys.executable, str(HERE / "build.py"), str(html), str(pages_json)], check=True)
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True, timeout=180)


def toc_pages():
    doc = pymupdf.open(pdf)
    ids = [pid for pid, _, _ in PARTS]
    found = {}
    for ln in doc[1].get_links():
        dest = ln.get("nameddest")
        if dest in ids and "page" in ln:
            found.setdefault(dest, ln["page"] + 1)
    doc.close()
    return found


pages_json.write_text("{}")
render()
pg = toc_pages()
print("toc pages", pg)
pages_json.write_text(json.dumps(pg))
render()
pg2 = toc_pages()
print("second pass", pg2, "stable" if pg == pg2 else "CHANGED")
doc = pymupdf.open(pdf)
print("pages:", len(doc))
