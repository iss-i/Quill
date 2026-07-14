# -*- coding: utf-8 -*-
import sys, io, glob, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import xml.etree.ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

targets = {
 'Conditioned Medium':'Phase 2 XSteps/SMPL- Conditioned Medium/SMPL_Conditioned Medium XStep Design Specification.docx',
 'Flask Number':'Phase 2 XSteps/SMPL- Flask Number/SMPL_Flask Number XStep Design Specification.docx',
 'Flow Rate Determination':'Phase 2 XSteps/SMPL- Flow Rate Determination/SMPL_Flow Rate Determination XStep Design Specification.docx',
 'Harvest Log':'Phase 2 XSteps/SMPL- Harvest Log/SMPL_Harvest Log XStep Design Specification.docx',
 'Harvest Sampling Calculations':'Phase 2 XSteps/SMPL- Harvest Sampling Calculations/SMPL_Harvest Sampling Calculations XStep Design Specification.docx',
 'Label Control and Reconciliation':'Phase 2 XSteps/SMPL- Label Control and Reconciliation/SMPL_Label Control and Reconciliation XStep Design Specification.docx',
}
def ptext(p): return ''.join(n.text or '' for n in p.iter(W+'t'))
def style(p):
    pPr=p.find(W+'pPr')
    if pPr is None: return None
    st=pPr.find(W+'pStyle'); return st.get(W+'val') if st is not None else None
def numid(p):
    pPr=p.find(W+'pPr')
    if pPr is None: return None
    np=pPr.find(W+'numPr')
    if np is None: return None
    ni=np.find(W+'numId'); return ni.get(W+'val') if ni is not None else None

for name,path in targets.items():
    z=zipfile.ZipFile(path)
    x=z.read('word/document.xml')
    root=ET.fromstring(x)
    body=root.find(W+'body')
    print('='*70); print(name)
    heads=[]
    for el in body:
        if el.tag==W+'p':
            s=style(el)
            if s and s.lower().startswith('heading'):
                heads.append((s,numid(el),ptext(el).strip()))
    for s,ni,t in heads:
        print(f'   {s} num={ni} | {t}')
    # has FM/Pseudo?
    htexts=[t for _,_,t in heads]
    print('   HAS Function Module(s):', any('Function Module' in t for t in htexts),
          '| HAS Pseudocode:', any('Pseudocode'==t or 'Pseudocode' in t for t in htexts))
    # TOC sdt? pgNumType?
    xs=x.decode('utf-8',errors='ignore')
    print('   pgNumType count:', xs.count('<w:pgNumType'), '| sdt TOC:', 'Table of Contents' in xs or 'TOC \\' in xs, '| numId6 defined:', 'w:numId w:val="6"' in xs)
