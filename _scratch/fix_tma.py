# -*- coding: utf-8 -*-
"""Convert Total Medium Addition from the old full template to the standardized
13-section Phase-2 template: fix title wording, remove the extra sections / group
headers / technical subsections, rename the layout heading."""
from docx import Document
from docx.oxml.ns import qn
from p2lib import is_heading, heading_text
from build_phase2 import set_para_text, neutralise_empty_headings, remove_pgnumtype, fix_toc, set_update_fields, strip_header_shd

P="../Phase 2 XSteps/SMPL- Total Medium Addition/SMPL_Total Medium Added XStep Design Specification.docx"
doc=Document(P); body=doc.element.body

# 1. Title wording -> standard template
TITLE_MAP={
 'V 1.0':'Phase 2',
 'April 2026':'June 2026',
 'Functional & Technical XStep Specification':'XStep Design Specification',
}
p0=body[0]
n_title=0
for t in p0.iter(qn('w:t')):
    if t.text in TITLE_MAP:
        t.text=TITLE_MAP[t.text]; n_title+=1
print("title runs replaced:",n_title)

def heading_level(el):
    if el.tag!=qn('w:p'): return None
    pPr=el.find(qn('w:pPr'))
    if pPr is None: return None
    st=pPr.find(qn('w:pStyle'))
    if st is None: return None
    v=st.get(qn('w:val')) or ''
    if v.lower().startswith('heading'):
        try: return int(v[7:])
        except: return 2
    return None

# 2. Remove a heading + its content up to next H1/H2
def remove_section(text):
    els=list(body)
    start=None
    for i,el in enumerate(els):
        if el.tag==qn('w:p') and is_heading(el) and heading_text(el)==text:
            start=i; break
    if start is None:
        print("  NOT FOUND:",text); return 0
    rm=[els[start]]
    for el in els[start+1:]:
        lvl=heading_level(el)
        if lvl is not None and lvl<=2: break
        rm.append(el)
    for el in rm: body.remove(el)
    return len(rm)

for sec in ['Functional Item','Functional Requirements','Security Objects','Development Type',
            'Processing Options','Functional Mapping Rules for Fields',
            'General Technical Specification','XStep Technical Specification']:
    n=remove_section(sec)
    print(f"  removed '{sec}': {n} elements")

# 3. Rename layout heading
for p in body.findall(qn('w:p')):
    if is_heading(p) and heading_text(p)=='Technical XStep Layout Design':
        set_para_text(p,'XStep Layout Design'); print("renamed Technical XStep Layout Design -> XStep Layout Design"); break

# 4. doc-wide fixes
neutralise_empty_headings(body); remove_pgnumtype(doc); fix_toc(doc); set_update_fields(doc)
doc.save(P); strip_header_shd(P)
print("saved.")

# verify heading sequence
doc2=Document(P)
heads=[heading_text(el) for el in doc2.element.body if el.tag==qn('w:p') and is_heading(el) and heading_text(el)]
print("\nFINAL HEADINGS:")
for h in heads: print("  ",h)
