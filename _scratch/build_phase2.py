# -*- coding: utf-8 -*-
"""Insert Function Module(s) + Pseudocode sections into a Phase-2 XStep design doc.
Shared FMs are transplanted (raw XML) from accepted Phase-2 docs (golden = Additional
pH Monitoring, biosamp = Bioreactor Sampling). New/custom FMs are authored from data
using templates cloned from the golden doc, so they match the accepted style exactly."""
import sys, io, copy, hashlib, zipfile, shutil, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from p2lib import extract_sections, ptext, pstyle, is_heading, heading_text

ROOT='..'
GOLDEN=ROOT+'/Phase 2 XSteps/SMPL- Additional pH Monitoring/SMPL_Additional pH Monitoring XStep Design Specification.docx'
BIOSAMP=ROOT+'/Phase 2 XSteps/AZP2 - Bioreactor/SMPL- Bioreactor Sampling/SMPL_Bioreactor Sampling XStep Design Specification.docx'

_g=extract_sections(GOLDEN)
_b=extract_sections(BIOSAMP)

# ---- templates (live elements in golden doc; deepcopy before use) ----
_cond=_g['ZSMPL_FM_COND_AVG']
_vs=_g['/SMPL/PPPI_FM_VALI_SUPE_SIG']
T_LABEL=_cond['fm'][1]      # bold "Import Parameters:"
T_BLANK=_cond['fm'][3]      # empty normal para
T_PTABLE=_cond['fm'][2]     # 3-col param table
T_ETABLE=_vs['fm'][8]       # 2-col exception table
T_PLAIN=_cond['pseudo'][1]  # plain normal line
T_BULLET=_cond['pseudo'][4] # bullet line (indent 360)

def set_para_text(p, text):
    runs=p.findall(qn('w:r'))
    if not runs:
        r=OxmlElement('w:r'); p.append(r); runs=[r]
    first=runs[0]
    for r in runs[1:]:
        p.remove(r)
    for t in first.findall(qn('w:t')):
        first.remove(t)
    # also remove any br/tab in first run
    t=OxmlElement('w:t'); t.set(qn('xml:space'),'preserve'); t.text=text
    first.append(t)

def set_cell_text(tc, text):
    p=tc.find(qn('w:p'))
    set_para_text(p, text)

def mk_label(text):
    p=copy.deepcopy(T_LABEL); set_para_text(p,text); return p
def mk_blank():
    return copy.deepcopy(T_BLANK)
def mk_plain(text):
    p=copy.deepcopy(T_PLAIN); set_para_text(p,text); return p
def mk_bullet(text):
    p=copy.deepcopy(T_BULLET); set_para_text(p,'•  '+text); return p

def mk_table(template, rows):
    t=copy.deepcopy(template)
    trs=t.findall(qn('w:tr'))
    rowtmpl=copy.deepcopy(trs[1])
    for tr in trs[1:]:
        t.remove(tr)
    for r in rows:
        nr=copy.deepcopy(rowtmpl)
        tcs=nr.findall(qn('w:tc'))
        for i,val in enumerate(r):
            set_cell_text(tcs[i], val)
        t.append(nr)
    return t

def authored_fm_elems(d):
    name=d['name']
    els=[mk_label('Function: '+name)]
    if d.get('imports'):
        els+=[mk_label('Import Parameters:'), mk_table(T_PTABLE,d['imports']), mk_blank()]
    if d.get('exports'):
        els+=[mk_label('Export Parameters:'), mk_table(T_PTABLE,d['exports']), mk_blank()]
    if d.get('changing'):
        els+=[mk_label('Changing Parameters:'), mk_table(T_PTABLE,d['changing']), mk_blank()]
    if d.get('exceptions'):
        els+=[mk_label('Exceptions:'), mk_table(T_ETABLE,d['exceptions']), mk_blank()]
    return els

def authored_pseudo_elems(d):
    els=[mk_label('Function: '+d['name'])]
    for kind,text in d['pseudo']:
        els.append(mk_bullet(text) if kind=='b' else mk_plain(text))
    els.append(mk_blank())
    return els

# ---- FM data for authored (new + restyled) FMs ----
from fmdata import FMDATA

def lib_fm_elems(name):
    if name in _g: return [copy.deepcopy(e) for e in _g[name]['fm']]
    if name in _b: return [copy.deepcopy(e) for e in _b[name]['fm']]
    if name in FMDATA: return authored_fm_elems(FMDATA[name])
    raise KeyError('No FM source for '+name)

def lib_pseudo_elems(name):
    if name in _g: return [copy.deepcopy(e) for e in _g[name]['pseudo']]
    if name in _b: return [copy.deepcopy(e) for e in _b[name]['pseudo']]
    if name in FMDATA: return authored_pseudo_elems(FMDATA[name])
    raise KeyError('No pseudo source for '+name)

# ---- heading clone w/ bookmark ----
def max_bookmark_id(body):
    mx=0
    for bm in body.iter(qn('w:bookmarkStart')):
        try: mx=max(mx,int(bm.get(qn('w:id'))))
        except: pass
    return mx

def make_heading_like(anchor, text, bid):
    h=copy.deepcopy(anchor)
    for bm in h.findall(qn('w:bookmarkStart'))+h.findall(qn('w:bookmarkEnd')):
        h.remove(bm)
    set_para_text(h, text)
    pPr=h.find(qn('w:pPr'))
    bmname='_heading=h.'+hashlib.md5(text.encode()).hexdigest()[:11]
    bms=OxmlElement('w:bookmarkStart')
    bms.set(qn('w:id'),str(bid)); bms.set(qn('w:name'),bmname)
    bms.set(qn('w:colFirst'),'0'); bms.set(qn('w:colLast'),'0')
    pPr.addnext(bms)
    bme=OxmlElement('w:bookmarkEnd'); bme.set(qn('w:id'),str(bid))
    h.append(bme)
    return h

# ---- doc-wide fixes ----
def neutralise_empty_headings(body):
    for p in body.findall(qn('w:p')):
        if is_heading(p) and heading_text(p)=='':
            pPr=p.find(qn('w:pPr'))
            st=pPr.find(qn('w:pStyle'))
            if st is not None: pPr.remove(st)
            np=pPr.find(qn('w:numPr'))
            if np is not None: pPr.remove(np)

def remove_pgnumtype(doc):
    for pg in doc.element.body.iter(qn('w:pgNumType')):
        pg.getparent().remove(pg)

def fix_toc(doc):
    body=doc.element.body
    for sdt in body.iter(qn('w:sdt')):
        gallery=sdt.find('.//'+qn('w:docPartGallery'))
        if gallery is None: continue
        if gallery.get(qn('w:val'))!='Table of Contents': continue
        content=sdt.find(qn('w:sdtContent'))
        if content is None: continue
        for ch in list(content):
            content.remove(ch)
        p=OxmlElement('w:p')
        def run_with(child):
            r=OxmlElement('w:r'); r.append(child); return r
        fb=OxmlElement('w:fldChar'); fb.set(qn('w:fldCharType'),'begin'); fb.set(qn('w:dirty'),'true')
        it=OxmlElement('w:instrText'); it.set(qn('xml:space'),'preserve')
        it.text=' TOC \\h \\u \\z \\t "Heading 1,1,Heading 2,2,Heading 3,3,Heading 4,4,Heading 5,5,Heading 6,6" '
        fs=OxmlElement('w:fldChar'); fs.set(qn('w:fldCharType'),'separate')
        plr=OxmlElement('w:r'); plt=OxmlElement('w:t'); plt.set(qn('xml:space'),'preserve'); plt.text='Right-click and choose Update Field to build the table of contents.'; plr.append(plt)
        fe=OxmlElement('w:fldChar'); fe.set(qn('w:fldCharType'),'end')
        for child in (fb,it,fs):
            p.append(run_with(child))
        p.append(plr)
        p.append(run_with(fe))
        content.append(p)
        return True
    return False

def set_update_fields(doc):
    s=doc.settings.element
    if s.find(qn('w:updateFields')) is None:
        uf=OxmlElement('w:updateFields'); uf.set(qn('w:val'),'true')
        s.insert(0, uf)

def strip_header_shd(path):
    # post-save: remove <w:shd> from header paragraph pPr (pale band in Google Docs)
    tmp=path+'.tmp'
    changed=False
    with zipfile.ZipFile(path) as zin:
        names=zin.namelist()
        data={n:zin.read(n) for n in names}
    for n in list(data):
        if re.match(r'word/header\d+\.xml$', n):
            x=data[n].decode('utf-8')
            x2=re.sub(r'<w:shd[^/]*?/>','',x)
            if x2!=x:
                data[n]=x2.encode('utf-8'); changed=True
    if changed:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, data[n])
        shutil.move(tmp, path)
    return changed

def build_replace(target_path, out_path, fm_order):
    """For docs that ALREADY have Function Module(s)/Pseudocode headings (old full
    template): replace the content under each existing heading instead of creating new."""
    doc=Document(target_path); body=doc.element.body
    children=list(body)
    def find_heading(pred, start_after=None):
        started = start_after is None
        for el in body:
            if start_after is not None and el is start_after:
                started=True; continue
            if not started: continue
            if el.tag==qn('w:p') and is_heading(el) and pred(heading_text(el)):
                return el
        return None
    fm_h=find_heading(lambda t:t=='Function Module(s)')
    ps_h=find_heading(lambda t:t=='Pseudocode', start_after=fm_h)
    cfg_h=find_heading(lambda t:'Configuration Specification' in t, start_after=ps_h)
    assert fm_h is not None and ps_h is not None and cfg_h is not None, 'missing FM/Pseudo/Config heading'
    def remove_between(a,b):
        rm=[]; started=False
        for el in body:
            if el is a: started=True; continue
            if el is b: break
            if started: rm.append(el)
        for el in rm: body.remove(el)
    remove_between(fm_h, ps_h)
    seq=[]
    for name in fm_order: seq+=lib_fm_elems(name)
    for el in seq: ps_h.addprevious(el)
    remove_between(ps_h, cfg_h)
    seq=[]
    for name in fm_order: seq+=lib_pseudo_elems(name)
    for el in seq: cfg_h.addprevious(el)
    neutralise_empty_headings(body)
    remove_pgnumtype(doc); fix_toc(doc); set_update_fields(doc)
    doc.save(out_path); strip_header_shd(out_path)
    print('replaced FM/Pseudo in',out_path,'with',len(fm_order),'FMs')

def remove_stray_headings(body, names):
    for p in list(body.findall(qn('w:p'))):
        if is_heading(p) and heading_text(p) in names:
            body.remove(p)

def build(target_path, out_path, fm_order, remove_headings=None):
    doc=Document(target_path)
    body=doc.element.body
    if remove_headings:
        remove_stray_headings(body, remove_headings)
    anchor=None
    for key in ('Configuration Specification','Test Scenarios'):
        for el in body:
            if is_heading(el) and key in heading_text(el):
                anchor=el; break
        if anchor is not None: break
    assert anchor is not None, 'no Config Spec / Test Scenarios anchor heading'
    bid=max_bookmark_id(body)+1
    fmh=make_heading_like(anchor,'Function Module(s)',bid)
    psh=make_heading_like(anchor,'Pseudocode',bid+1)
    seq=[fmh]
    for name in fm_order:
        seq+=lib_fm_elems(name)
    seq.append(psh)
    for name in fm_order:
        seq+=lib_pseudo_elems(name)
    for el in seq:
        anchor.addprevious(el)
    neutralise_empty_headings(body)
    remove_pgnumtype(doc)
    fix_toc(doc)
    set_update_fields(doc)
    doc.save(out_path)
    strip_header_shd(out_path)
    print('built',out_path,'with',len(fm_order),'FMs')

# ---- per-doc FM orders ----
ORDERS={
 'cm':('Conditioned Medium', ['ZSMPL_FM_CUSTOM_INDEX','ZSMPL_FM_ENTRY_VALIDATION1','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_VALI_SUPE_SIG','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_ADD_PERFORM','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'fn':('Flask Number', ['ZSMPL_FM_FLASK_NUMBER','ZSMPL_FM_FLASK_NUMBER_UPD_TV','ZSMPL_FM_FLASK_NUMBER_MANUAL','ZSMPL_FM_GET_EXP_DATE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'fr':('Flow Rate Determination', ['ZSMPL_FM_CUSTOM_INDEX','ZSMPL_FM_VALIDATE_FLOW','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_VALI_SUPE_SIG','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_ADD_PERFORM','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'hl':('Harvest Log', ['/SMPL/PPPI_FM_GET_DATE_TIME','/SMPL/PPPI_FM_CALC_EXECUTE','/SMPL/PPPI_FM_MIN_MAX','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_VALI_SUPE_SIG','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_ADD_PERFORM','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'hsc':('Harvest Sampling Calculations', ['/SMPL/PPPI_FM_CALC_VALIDATE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'lcr':('Label Control and Reconciliation', ['/SMPL/PPPI_FM_CALC_EXECUTE','/SMPL/PPPI_FM_MIN_MAX','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_VALI_SUPE_SIG','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_ADD_PERFORM','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'mc':('Material Consumption', ['/SMPL/PPPI_FM_GET_MAT_ITEMS','ZSMPL_FM_GET_MAT_ITEMS_EBR','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'pcv':('PCV Measurement', ['/SMPL/PPPI_FM_CALC_EXECUTE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'rb':('Rocker Bag Daily Sample', ['ZSMPL_FM_GET_ASSIGNED_EQUI_EBR','ZSMPL_FM_RANGE_YES_NO','/SMPL/PPPI_FM_GET_DATE_TIME','/SMPL/PPPI_FM_SET_LINE_IDX','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_VALI_SUPE_SIG','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_ADD_PERFORM','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'ss':('Solution Summary - Data Recording', ['ZSMPL_FM_GET_ASSIGNED_EQUI_EBR','/SMPL/ELB_FM_GET_ASS_EQ_VALID','/SMPL/PPPI_FM_MIN_MAX','/SMPL/PPPI_FM_SIG_ADD_DB_CB','/SMPL/PPPI_FM_SIG_VALIDATION','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'tnv':('Theoretical No. of Vials', ['ZSMPL_FM_GET_FLASKS','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'tvc':('Three Variable Calc', ['/SMPL/PPPI_FM_CALC_SETUP','/SMPL/PPPI_FM_CALC_VALIDATE','/SMPL/PPPI_FM_INPUT_VALUE','/SMPL/PPPI_FM_OUTPUT_VALUE','/SMPL/PPPI_FM_SET_FLOAT_VALUE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'yc':('Yield Calculations', ['/SMPL/PPPI_FM_CALC_SETUP','/SMPL/PPPI_FM_CALC_VALIDATE','/SMPL/PPPI_FM_INPUT_VALUE','/SMPL/PPPI_FM_OUTPUT_VALUE','/SMPL/PPPI_FM_SET_FLOAT_VALUE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
 'tma':('Total Medium Addition', ['ZSMPL_FM_CUSTOM_INDEX','ZSMPL_FM_VALIDATE_QUANTITY','/SMPL/PPPI_FM_GET_DATE_TIME','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']),
}
REPLACE_DOCS={'tma'}
PATHS={
 'cm':'Phase 2 XSteps/SMPL- Conditioned Medium/SMPL_Conditioned Medium XStep Design Specification.docx',
 'fn':'Phase 2 XSteps/SMPL- Flask Number/SMPL_Flask Number XStep Design Specification.docx',
 'fr':'Phase 2 XSteps/SMPL- Flow Rate Determination/SMPL_Flow Rate Determination XStep Design Specification.docx',
 'hl':'Phase 2 XSteps/SMPL- Harvest Log/SMPL_Harvest Log XStep Design Specification.docx',
 'hsc':'Phase 2 XSteps/SMPL- Harvest Sampling Calculations/SMPL_Harvest Sampling Calculations XStep Design Specification.docx',
 'lcr':'Phase 2 XSteps/SMPL- Label Control and Reconciliation/SMPL_Label Control and Reconciliation XStep Design Specification.docx',
 'mc':'Phase 2 XSteps/SMPL- Material Consumption/SMPL_Material Consumption XStep Design Specification.docx',
 'pcv':'Phase 2 XSteps/SMPL- PCV Measurement/SMPL_PCV Measurement XStep Design Specification.docx',
 'rb':'Phase 2 XSteps/SMPL- Rocker Bag Daily Sample/SMPL_Rocker Bag Daily Sample XStep Design Specification.docx',
 'ss':'Phase 2 XSteps/SMPL- Solution Summary - Data Recording/SMPL_Solution Summary - Data Recording Var XStep Design Specification.docx',
 'tnv':'Phase 2 XSteps/SMPL- Theoretical No. of Vials/SMPL_Theoretical No. of Vials XStep Design Specification.docx',
 'tvc':'Phase 2 XSteps/SMPL- Three Variable Calc/SMPL_Three Variable Calc XStep Design Specification.docx',
 'yc':'Phase 2 XSteps/SMPL- Yield Calculations/SMPL_Yield Calculations XStep Design Specification.docx',
 'tma':'Phase 2 XSteps/SMPL- Total Medium Addition/SMPL_Total Medium Added XStep Design Specification.docx',
}
REMOVE_HEADINGS={'mc':['Functional Requirements']}

if __name__=='__main__':
    key=sys.argv[1]
    name,order=ORDERS[key]
    src=ROOT+'/'+PATHS[key]
    if key in REPLACE_DOCS:
        build_replace(src, src, order)
    else:
        build(src, src, order, remove_headings=REMOVE_HEADINGS.get(key))  # edit in place
