# -*- coding: utf-8 -*-
"""Phase-2 FM/Pseudocode section library: extract accepted FM blocks from completed
docs, and provide building blocks to insert them into target docs."""
import copy
from docx import Document
from docx.oxml.ns import qn

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))

def pstyle(p):
    pPr=p.find(qn('w:pPr'))
    if pPr is None: return None
    st=pPr.find(qn('w:pStyle'))
    return st.get(qn('w:val')) if st is not None else None

def is_heading(el):
    if el.tag!=qn('w:p'): return False
    s=pstyle(el)
    return bool(s and s.lower().startswith('heading'))

def heading_text(el):
    return ptext(el).strip()

def extract_sections(path):
    """Return dict name -> {'fm':[elems], 'pseudo':[elems]} from a completed doc."""
    doc=Document(path)
    body=doc.element.body
    blocks=list(body)
    # locate section boundaries
    idx={}
    order=[]
    for i,el in enumerate(blocks):
        if is_heading(el):
            t=heading_text(el)
            idx[t]=i
            order.append((t,i))
    def find(name_pred):
        for t,i in order:
            if name_pred(t): return i
        return None
    fm_start=find(lambda t:'Function Module' in t)
    ps_start=find(lambda t: t=='Pseudocode')
    # end of pseudocode = next heading after ps_start
    def next_heading_after(i):
        for j in range(i+1,len(blocks)):
            if is_heading(blocks[j]): return j
        return len(blocks)
    fm_end=next_heading_after(fm_start) if fm_start is not None else None
    ps_end=next_heading_after(ps_start) if ps_start is not None else None
    res={}
    def split_fm(lo,hi):
        cur=None
        for el in blocks[lo+1:hi]:
            if el.tag==qn('w:p'):
                txt=ptext(el).strip()
                if txt.startswith('Function:'):
                    cur=txt.split(':',1)[1].strip()
                    res.setdefault(cur,{'fm':[],'pseudo':[]})
            if cur is not None:
                yield cur,el
    if fm_start is not None:
        for name,el in split_fm(fm_start,fm_end):
            res[name]['fm'].append(el)
    # pseudocode
    if ps_start is not None:
        cur=None
        for el in blocks[ps_start+1:ps_end]:
            if el.tag==qn('w:p'):
                txt=ptext(el).strip()
                if txt.startswith('Function:'):
                    cur=txt.split(':',1)[1].strip()
                    res.setdefault(cur,{'fm':[],'pseudo':[]})
            if cur is not None:
                res[cur]['pseudo'].append(el)
    return res

if __name__=='__main__':
    import sys
    r=extract_sections(sys.argv[1])
    for name,d in r.items():
        print(f"{name:40s} fm_elems={len(d['fm']):3d} pseudo_elems={len(d['pseudo']):3d}")
