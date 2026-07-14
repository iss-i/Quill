# -*- coding: utf-8 -*-
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn
from p2lib import ptext, pstyle, is_heading, heading_text
SECT={'Purpose','Overview','Reasons for developing','Authorization','Assumptions/ Dependencies',
      'Validation Checks','XStep Layout Design','Configuration Specification','Configuration Specifications',
      'Test Scenarios','Document References','Revision History','Functional Requirements'}
targets={
 'Theoretical No. of Vials':'Phase 2 XSteps/SMPL- Theoretical No. of Vials/SMPL_Theoretical No. of Vials XStep Design Specification.docx',
 'Three Variable Calc':'Phase 2 XSteps/SMPL- Three Variable Calc/SMPL_Three Variable Calc XStep Design Specification.docx',
 'Total Medium Addition':'Phase 2 XSteps/SMPL- Total Medium Addition/SMPL_Total Medium Added XStep Design Specification.docx',
 'Yield Calculations':'Phase 2 XSteps/SMPL- Yield Calculations/SMPL_Yield Calculations XStep Design Specification.docx',
}
def numid(p):
    pPr=p.find(qn('w:pPr'))
    if pPr is None: return None
    np=pPr.find(qn('w:numPr'))
    if np is None: return None
    ni=np.find(qn('w:numId')); return ni.get(qn('w:val')) if ni is not None else None
for name,path in targets.items():
    print('='*60, name)
    doc=Document('../'+path); body=doc.element.body
    for el in body:
        if el.tag!=qn('w:p'): continue
        t=ptext(el).strip()
        if is_heading(el) and t:
            print(f"  HEAD  {pstyle(el)} num={numid(el)} | {t}")
        elif t in SECT:  # section-name text NOT styled as heading
            print(f"  !!MIS-STYLED [{pstyle(el)}] num={numid(el)} | {t}")
    import zipfile
    z=zipfile.ZipFile('../'+path); dx=z.read('word/document.xml').decode('utf-8')
    print("  HAS FM:", 'Function Module' in dx, "| ConfigSpec wording:",
          'Configuration Specifications' if 'Configuration Specifications' in dx else 'Configuration Specification')
