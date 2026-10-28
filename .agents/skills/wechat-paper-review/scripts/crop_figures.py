#!/usr/bin/env python3
"""Crop original paper figures with explicit human-approved PDF page bounding boxes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import fitz

def crop(paper:Path, regions_file:Path, out:Path, scale:float=2.5, preview:bool=False)->list:
    if scale <= 0 or scale>8:
        raise ValueError("scale must be >0 and <=8")
    regions=json.loads(regions_file.read_text(encoding="utf-8"))
    if not isinstance(regions,list):
        raise ValueError("Regions JSON should contain a list")
    out.mkdir(parents=True,exist_ok=True)
    used_names=set()
    records=[]
    with fitz.open(paper) as doc:
        for r in regions:
            n=int(r["page"])
            if n<1 or n>len(doc):
                raise ValueError(f"Page out of range: {n}")
            page=doc[n-1]
            if len(r["bbox"]) != 4:
                raise ValueError("bbox needs 4 coordinates")
            x0,y0,x1,y1=map(float,r["bbox"])
            if not (0 <= x0 < x1 <= page.rect.width and 0 <= y0 < y1 <= page.rect.height):
                raise ValueError(f"bbox out of page bounds: {r}")
            fn=Path(r.get("filename",r.get("id",f"fig{len(records)+1}")+".png"))
            if fn.name != str(fn) or fn.suffix.lower() != ".png":
                raise ValueError("filename must be a simple PNG name")
            if fn.name in used_names:
                raise ValueError(f"Repeated figure filename: {fn.name}")
            used_names.add(fn.name)
            clip=fitz.Rect(x0,y0,x1,y1)
            pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip,alpha=False)
            pix.save(out / fn.name)
            if preview:
                from PIL import Image, ImageDraw
                from io import BytesIO
                orig=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
                im=Image.open(BytesIO(orig.tobytes("png"))).convert("RGB")
                d=ImageDraw.Draw(im)
                d.rectangle([x0*1.5,y0*1.5,x1*1.5,y1*1.5],outline="#DC2626",width=4)
                im.save(out / f"preview-{fn.stem}.png")
            records.append({"id":r.get("id",fn.stem),"page":n,"bbox":[x0,y0,x1,y1],"file":fn.name,"resolution_px":[pix.width,pix.height]})
    manifest={"source_pdf_name":paper.name,"source_pdf_sha256":hashlib.sha256(paper.read_bytes()).hexdigest(),"figures":records}
    (out / "figure_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Cropped {len(records)} original figures into {out}")
    return records

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--paper",type=Path,required=True)
    p.add_argument("--regions",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--scale",type=float,default=2.5)
    p.add_argument("--preview",action="store_true")
    a=p.parse_args()
    crop(a.paper,a.regions,a.out,a.scale,a.preview)
