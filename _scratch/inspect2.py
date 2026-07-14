# -*- coding: utf-8 -*-
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
import zipfile
import xml.etree.ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
targets={
 'Material Consumption':'Phase 2 XSteps/SMPL- Material Consumption/SMPL_Material Consumption XStep Design Specification.docx',
 'PCV Measurement':'Phase 2 XSteps/SMPL- PCV Measurement/SMPL_PCV Measurement XStep Design Specification.docx',
 'Rocker Bag Daily Sample':'Phase 2 XSteps/SMPL- Rocker Bag Daily Sample/SMPL_Rocker Bag Daily Sample XStep Design Specification.docx',
 'Solution Summary':'Phase 2 XSteps/SMPL- Solution Summary - Data Recording/SMPL_Solution Summary - Data Recording Var XStep Design Specification.docx',
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
import os
for name,path in targets.items():
    print('='*60, name)
    if not os.path.exists(path): print('  MISSING FILE'); continue
    z=zipfile.ZipFile(path); x=z.read('word/document.xml'); root=ET.fromstring(x)
    body=root.find(W+'body')
    for el in body:
        if el.tag==W+'p' and style(el) and style(el).lower().startswith('heading'):
            t=ptext(el).strip()
            if t: print(f'   num={numid(el)} | {t}')
    xs=x.decode('utf-8','ignore')
    print('   HAS FM:', 'Function Module' in xs, '| pgNumType:', xs.count('<w:pgNumType'), '| TOC sdt:', 'Table of Contents' in xs)
