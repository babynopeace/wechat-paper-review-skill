#!/usr/bin/env python3
"""PDF preflight: extract per-page text and candidate figure captions; render previews."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import fitz

FIG_RE = re.compile(r"\b(?:Fig(?:ure)?\.?|图)\s*([0-9]+)\s*[|.:：-]", re.IGNORECASE)

def run(paper: Path, out: Path, dpi: int = 100, max_pages: int = 0) -> dict:
    if not paper.is_file():
        raise FileNotFoundError(paper)
    if paper.suffix.lower() != ".pdf":
        raise ValueError("Input paper must be PDF")
    out.mkdir(parents=True, exist_ok=True)
    (out / "pages").mkdir(exist_ok=True)
    (out / "text").mkdir(exist_ok=True)
    digest = hashlib.sha256(paper.read_bytes()).hexdigest()
    records = []
    with fitz.open(paper) as doc:
        page_count = len(doc)
        for index in range(page_count if max_pages <= 0 else min(page_count, max_pages)):
            page = doc[index]
            page_no = index + 1
            txt = page.get_text("text", sort=True)
            (out / "text" / f"page-{page_no:03d}.txt").write_text(txt, encoding="utf-8")
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
            pix.save(out / "pages" / f"page-{page_no:03d}.png")
            figs = []
            for match in FIG_RE.finditer(txt):
                figs.append({"figure": match.group(1), "caption_candidate": txt[match.start():match.start()+260].replace("\n", " ")})
            records.append({"page": page_no, "width_pt": round(page.rect.width,1), "height_pt": round(page.rect.height,1), "figure_candidates": figs, "text_chars":len(txt)})
    report = {"paper_name": paper.name,"sha256":digest,"pdf_pages":page_count,"processed_pages":len(records),"pages":records,
              "limitations":"Figure captions are candidate text spans; visually check original pages and figures."}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Processed {len(records)}/{page_count} pages: {out}")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--paper",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--dpi",type=int,default=100)
    p.add_argument("--max-pages",type=int,default=0,help="0 means all pages")
    a=p.parse_args()
    run(a.paper,a.out,a.dpi,a.max_pages)
