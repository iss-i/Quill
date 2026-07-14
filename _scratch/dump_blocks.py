# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx.oxml.ns import qn
from p2lib import extract_sections, ptext

path=sys.argv[1]; fm=sys.argv[2]; sec=sys.argv[3] if len(sys.argv)>3 else 'fm'
r=extract_sections(path)
els=r[fm][sec]
for i,el in enumerate(els):
    if el.tag==qn('w:p'):
        runs=el.findall('.//'+qn('w:r'))
        bold=False
        for ru in runs:
            rpr=ru.find(qn('w:rPr'))
            if rpr is not None and rpr.find(qn('w:b')) is not None: bold=True
        pPr=el.find(qn('w:pPr'))
        ind=''
        if pPr is not None:
            indel=pPr.find(qn('w:ind'))
            if indel is not None: ind='IND('+(indel.get(qn('w:left')) or indel.get(qn('w:start')) or '?')+')'
            np=pPr.find(qn('w:numPr'))
            if np is not None: ind+='NUMPR'
        print(f"{i:2d} P bold={int(bold)} {ind} | {ptext(el)!r}")
    else:
        rows=el.findall(qn('w:tr'))
        print(f"{i:2d} TBL rows={len(rows)} cols={len(rows[0].findall(qn('w:tc'))) if rows else 0}")
        for ri,tr in enumerate(rows):
            cells=[ptext(tc) for tc in tr.findall(qn('w:tc'))]
            print('       ',cells)
