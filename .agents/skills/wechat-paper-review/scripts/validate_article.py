#!/usr/bin/env python3
"""Rule-based article audit. Never substitutes for expert review of paper claims."""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
import fitz

BAD_TITLES=('？','?','震惊','颠覆','揭秘','竟然')
CJK_DIGIT_RE=re.compile(r'\d+(?:\.\d+)?\s*(?:%|Hz|dB|人|例|年|天|个|组|分|岁|年|次|周)')

def norm(s):
    return ''.join(c.lower() for c in unicodedata.normalize('NFKC',s) if not c.isspace())

def audit(path:Path,paper:Path|None=None):
    data=json.loads(path.read_text(encoding='utf-8'))
    errs=[];warn=[]
    if not isinstance(data,dict):
        return ['article.json root must be an object'],warn
    meta=data.get('metadata',{})
    for key in ('original_title','authors','journal','publication_date','wechat_title'):
        if not meta.get(key):errs.append(f'metadata missing: {key}')
    if any(x in str(meta.get('wechat_title','')) for x in BAD_TITLES):
        warn.append('wechat_title should be academic, declarative and non-promotional')
    sections=data.get('sections',[])
    if not sections:errs.append('sections cannot be empty')
    total=''.join(data.get('lead',[]))
    numfig=0
    page_text=[]
    if paper is not None:
        with fitz.open(paper) as doc:
            page_text=[norm(p.get_text('text')) for p in doc]
    for i,s in enumerate(sections,1):
        title=s.get('title','')
        if not title:errs.append(f'section {i} lacks title')
        if any(k in title for k in BAD_TITLES):warn.append(f'section {i} title might be colloquial')
        blocks=list(s.get('blocks',[]))
        for j,sub in enumerate(s.get('subsections',[]),1):
            if not sub.get('title'): errs.append(f'subsection {i}.{j} lacks title')
            blocks.extend(sub.get('blocks',[]))
        for b in blocks:
            kind=b.get('type')
            if kind=='paragraph':
                t=b.get('text','')
                if not t.strip():errs.append(f'empty paragraph in section {i}')
                total+=t
                if CJK_DIGIT_RE.search(t) and not b.get('source_pages'):
                    warn.append(f'Section {i}: quantified claim lacks source_pages: {t[:50]}')
                for pg in b.get('source_pages',[]):
                    if not isinstance(pg,int) or (paper is not None and not (1<=pg<=len(page_text))):
                        errs.append(f'Section {i}: out-of-range source page {pg}')
                if paper is not None:
                    for quote in b.get('evidence',[]):
                        q=norm(quote)
                        if len(q)<8:warn.append(f'Section {i}: evidence quote too short')
                        if q and not any(q in txt for txt in page_text):
                            warn.append(f'Section {i}: evidence quote not text-matchable; manually verify: {quote[:60]}')
            elif kind=='figure':
                numfig+=1
                image=b.get('image','')
                ip=(path.parent/image).resolve()
                if not ip.is_relative_to(path.parent.resolve()):
                    errs.append(f'figure path escapes article directory: {image}')
                elif not ip.is_file():errs.append(f'figure missing: {ip}')
                if not b.get('caption'):errs.append(f'figure missing caption in section {i}')
                if not b.get('original_figure'):
                    warn.append(f'figure in section {i} lacks original_figure attribution')
            else:errs.append(f'unknown block type {kind}')
    if numfig<4:warn.append('Fewer than 4 original figures; may be okay for a short paper')
    if numfig>7:warn.append('More than 7 figures; may be too dense for WeChat')
    han=len(re.findall(r'[\u4e00-\u9fff]',total))
    if han<800:warn.append(f'Article appears short ({han} Chinese characters)')
    if han>3200:warn.append(f'Article may be too long ({han} Chinese characters)')
    if sections:
        end=sections[-1]
        if '个人思考' in end.get('title','') and end.get('subsections'):
            warn.append('Last personal reflection section is normally two paragraphs, without 6.1/6.2')
    return errs,warn

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--article',required=True,type=Path)
    p.add_argument('--paper',type=Path)
    p.add_argument('--strict',action='store_true',help='Treat warnings as errors')
    a=p.parse_args()
    errors,warnings=audit(a.article,a.paper)
    for x in errors: print('ERROR:',x)
    for x in warnings: print('WARNING:',x)
    print(f'Errors: {len(errors)}, warnings: {len(warnings)}')
    raise SystemExit(1 if errors or (a.strict and warnings) else 0)
