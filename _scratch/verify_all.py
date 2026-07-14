# -*- coding: utf-8 -*-
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn
from p2lib import extract_sections, is_heading, heading_text
import zipfile
from build_phase2 import PATHS, ORDERS

for key in ['cm','fn','fr','hl','hsc','lcr']:
    P='../'+PATHS[key]
    name,order=ORDERS[key]
    doc=Document(P); body=doc.element.body
    heads=[heading_text(el) for el in body if el.tag==qn('w:p') and is_heading(el)]
    # placement check
    try:
        fi=heads.index('Function Module(s)'); pi=heads.index('Pseudocode'); ci=[i for i,h in enumerate(heads) if 'Configuration Specification' in h][0]
        placed = fi< pi < ci and heads[fi-1] in ('XStep Layout Design','Validation Checks')
    except Exception as e:
        placed=f'ERR {e}'
    z=zipfile.ZipFile(P); dx=z.read('word/document.xml').decode('utf-8')
    sett=doc.settings.element.find(qn('w:updateFields')) is not None
    pg=len(body.findall('.//'+qn('w:pgNumType')))
    empt=sum(1 for el in body if el.tag==qn('w:p') and is_heading(el) and heading_text(el)=='')
    r=extract_sections(P)
    print(f"### {name} [{key}]")
    print(f"   placement_ok={placed}  pgNumType={pg}  updateFields={sett}  empty_head={empt}  TOCfield={' TOC ' in dx}")
    print(f"   FM order matches XStep ({len(order)}): {list(r.keys())==order}")
    # table sanity: every param table has >=2 rows; cols 3 for param, 2 for exc
    for fm,d in r.items():
        for el in d['fm']:
            if el.tag==qn('w:tbl'):
                rows=el.findall(qn('w:tr')); cols=len(rows[0].findall(qn('w:tc')))
                if len(rows)<2: print(f"   !! {fm} empty table");
    miss=[o for o in order if o not in r]
    if miss: print("   !! MISSING:",miss)
