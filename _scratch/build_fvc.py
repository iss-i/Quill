# -*- coding: utf-8 -*-
"""Build the SMPL: Fill Volume Calculation XStep Design Specification (.docx) in the
AZ Phase 2 template. Clones the Three Variable Calc doc for the template shell (title
page, styles, live TOC), rebuilds the body with Fill Volume content, and reuses the
Phase-2 FM/pseudocode emitters for the 6 existing calc-engine / activation FMs."""
import sys, io, copy, os, shutil, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn
import build_phase2 as B
from p2lib import is_heading, heading_text

ROOT='..'
DONOR=ROOT+'/Phase 2 XSteps/SMPL- Three Variable Calc/SMPL_Three Variable Calc XStep Design Specification.docx'
OUTDIR=ROOT+'/Merck XStep Mock Ups/Fill Volume Calculation'
OUT=OUTDIR+'/SMPL_Fill Volume Calculation XStep Design Specification.docx'
FM_ORDER=['/SMPL/PPPI_FM_CALC_VALIDATE','/SMPL/PPPI_FM_CALC_EXECUTE','/SMPL/PPPI_FM_INPUT_VALUE',
          '/SMPL/PPPI_FM_OUTPUT_VALUE','/SMPL/PPPI_FM_INITIAL_ACTIVE','/SMPL/MBR_DEP_CHECK_ACTIVE']

os.makedirs(OUTDIR, exist_ok=True)
shutil.copy(DONOR, OUT)
doc=Document(OUT); body=doc.element.body
children=list(body)
sectPr=children[-1] if children[-1].tag==qn('w:sectPr') else None
purpose=next(el for el in children if el.tag==qn('w:p') and is_heading(el) and heading_text(el).strip()=='Purpose')
anchor=copy.deepcopy(purpose)
start=children.index(purpose); end=children.index(sectPr) if sectPr is not None else len(children)
for el in children[start:end]: body.remove(el)

bid=B.max_bookmark_id(body)+1
def add(el):
    if sectPr is not None: sectPr.addprevious(el)
    else: body.append(el)
def H(t):
    global bid
    add(B.make_heading_like(anchor,t,bid)); bid+=1
def P(t): add(B.mk_plain(t))
def Bul(t): add(B.mk_bullet(t))
def BL(): add(B.mk_blank())
def TBL(tmpl, headers, rows):
    t=B.mk_table(tmpl, rows); hdr=t.findall(qn('w:tr'))[0]; tcs=hdr.findall(qn('w:tc'))
    for i,h in enumerate(headers): B.set_cell_text(tcs[i], h)
    add(t)
def T3(headers, rows): TBL(B.T_PTABLE, headers, rows)
def T2(headers, rows): TBL(B.T_ETABLE, headers, rows)

# ---------------- content ----------------
H('Purpose')
P('The purpose of this document is to outline the design and configuration of the SMPL: Fill Volume '
  'Calculation XStep. This XStep calculates the volume required to fill the production bioreactor prior to '
  'seed addition, by subtracting the planned seed volume from the planned final batch volume, and records '
  'the result with the appropriate electronic signatures.')

H('Overview')
P('The SMPL: Fill Volume Calculation XStep provides the operator with a calculation step that determines '
  'the bioreactor Fill Volume before inoculation. The operator records the Planned Final Volume and the '
  'Seed Volume; the Fill Volume is then calculated automatically as:')
Bul('Fill Volume = Planned Final Volume − Seed Volume')
P('The calculation is performed by the generic SiMPL calculation engine. The entered values are converted '
  'and validated as numeric, the subtraction is executed, and the formatted result is written back to the '
  'Fill Volume field, which is read-only. The step is completed with a Performed-By signature and an '
  'optional Witness signature.')
P('All function modules used by this XStep already exist in DE1 100; no new development is required.')

H('Reasons for developing')
P('The SMPL: Fill Volume Calculation XStep was developed to automate and standardize the fill-volume '
  'calculation previously performed manually in the paper batch record (Manufacturing Directions, '
  'Section IV.C). Automating the calculation removes the risk of arithmetic error, enforces numeric input '
  'validation, ensures the result is captured consistently, and provides an electronic signature trail in '
  'line with data-integrity requirements.')

H('Authorization')
P('Access to the XStep and the ability to enter data and apply signatures is controlled by the standard '
  'SiMPL EBR security model. The operator must hold the PFCG role assigned to the relevant process order / '
  'control recipe. Performed-By and Witness signatures are captured using the SAP digital signature method '
  'configured for the EBR.')

H('Assumptions/ Dependencies')
Bul('The generic SiMPL calculation engine function modules (/SMPL/PPPI_FM_CALC_VALIDATE, '
    '/SMPL/PPPI_FM_CALC_EXECUTE, /SMPL/PPPI_FM_INPUT_VALUE, /SMPL/PPPI_FM_OUTPUT_VALUE) exist and are active '
    'in the target system.')
Bul('The standard activation and dependency function modules (/SMPL/PPPI_FM_INITIAL_ACTIVE, '
    '/SMPL/MBR_DEP_CHECK_ACTIVE) exist and are active.')
Bul('The Planned Final Volume and Seed Volume are entered in consistent units (e.g. kg / L).')
Bul('The Planned Final Volume is greater than or equal to the Seed Volume.')

H('Validation Checks')
P('The following validations are applied within the XStep:')
T3(['Field','Validation','Function Module'],
   [['Planned Final Volume','Must be numeric','/SMPL/PPPI_FM_INPUT_VALUE'],
    ['Seed Volume','Must be numeric','/SMPL/PPPI_FM_INPUT_VALUE'],
    ['Fill Volume','Calculated (read-only); optional min/max tolerance','/SMPL/PPPI_FM_CALC_VALIDATE']])
BL()

H('XStep Layout Design')
P('The XStep is rendered as a single calculation instruction. The operator enters the Planned Final Volume '
  'and Seed Volume; the Fill Volume is calculated and displayed as a read-only field. The step is signed '
  'with a Performed-By signature and an optional Witness signature. The fields are:')
Bul('Planned Final Volume – entry, numeric, required.')
Bul('Seed Volume – entry, numeric, required.')
Bul('Fill Volume – read-only, calculated (Planned Final Volume − Seed Volume).')
Bul('Performed By – signature, required.')
Bul('Witness By – signature, optional.')

H('Function Module(s)')
P('The following function modules are used by this XStep. All of them already exist in DE1 100 and are '
  'reused as-is; no new function module is required.')
for fm in FM_ORDER:
    for el in B.lib_fm_elems(fm): add(el)

H('Pseudocode')
for fm in FM_ORDER:
    for el in B.lib_pseudo_elems(fm): add(el)

H('Configuration Specifications')
P('The XStep is configured using the following parameters:')
T3(['Parameter','Value / Configuration','Description'],
   [['Header','Fill Volume Calculation','Header text displayed at the top of the step (configurable in SiMPL MBR).'],
    ['Instruction','(instruction text)','The instruction text displayed to the operator (configurable in SiMPL MBR).'],
    ['Calc Value 1','Planned Final Volume','First operand of the calculation.'],
    ['Calc Operation 1','Minus (−)','Operation applied between Value 1 and Value 2.'],
    ['Calc Value 2','Seed Volume','Second operand of the calculation.'],
    ['Calc Result','Fill Volume','Read-only field populated with the calculation result.'],
    ['Result UoM','kg / L','Unit of measure used to format the result.']])
BL()

H('Test Scenarios')
T3(['#','Scenario','Expected Result'],
   [['1','Enter Planned Final Volume = 2000 and Seed Volume = 200.','Fill Volume calculates to 1800.'],
    ['2','Enter a non-numeric value in Planned Final Volume.','Entry is rejected with a non-numeric error (INPUT_NOT_NUMERIC).'],
    ['3','Enter a Seed Volume greater than the Planned Final Volume.','Fill Volume calculates as a negative value; the configured tolerance check (if any) flags the result for review.'],
    ['4','Attempt to complete the step without a Performed-By signature.','The step cannot be completed; the Performed-By signature is mandatory.'],
    ['5','Re-open the completed step.','The recorded values, calculated Fill Volume and signatures are displayed and retained.']])
BL()

H('Document References')
T2(['Reference No.','Document Title'],
   [['1','Manufacturing Directions – Sample Virus in 2000L Single-Use Bioreactor (SUB)'],
    ['2','SiMPL XStep Library – Process Manufacturing (DE1 100)']])
BL()

H('Revision History')
T3(['Version No.','Description','Date'],
   [['1.0','Initial document','2026-06-30']])

# ---------------- fixes + save ----------------
B.neutralise_empty_headings(body)
B.set_update_fields(doc)
doc.save(OUT)

# title-canvas + header/footer text: rename the XStep
tmp=OUT+'.tmp'
with zipfile.ZipFile(OUT) as z: data={n:z.read(n) for n in z.namelist()}
for n in list(data):
    if re.match(r'word/(document|header\d+|footer\d+)\.xml$', n):
        x=data[n].decode('utf-8')
        x2=x.replace('Three Variable Calc','Fill Volume Calculation')
        if x2!=x: data[n]=x2.encode('utf-8')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in data.items(): z.writestr(n,b)
shutil.move(tmp,OUT)
print('built',OUT)
