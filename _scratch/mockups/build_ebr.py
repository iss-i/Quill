# -*- coding: utf-8 -*-
"""Assemble the individual XStep mockups into one mock EBR / PI Sheet for the
Merck 2000L SUB process, cross-referenced to the original MABR sections, so the
NEW (XStep-based) EBR can be compared against the OLD paper batch record.
Outputs an HTML and a PDF."""
import os, subprocess, html
from steps import STEPS
from build_mockups import th_cells, render_row, form_rows, signoff_rows, header_field_rows

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\Merck XStep Mock Ups"
HTMLDIR = r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BYF = {s['folder']: s for s in STEPS}

# original MABR section each XStep maps to (for the comparison chip + crosswalk)
OLDREF = {
 "Virus Seed Identification":"I",
 "Cell Identification":"II",
 "Vessel and Single-Use Bag Setup":"III.A–B",
 "Equipment Sterilization Verification":"III.A + Equip. Steril. Record",
 "Probe Identification":"III.C",
 "pH Probe Calibration":"III.A, IV.G",
 "Assembly and Line Connections":"III.D–H, V.I",
 "Controller and Gas Flow Verification":"IV.A",
 "Fill Volume Calculation":"IV.C",
 "Component Addition":"IV.B–C, IV.F",
 "Medium Addition":"IV.B (media fill)",
 "Controller Setpoint and Alarm Configuration":"IV.D, V.J, VI.A/F",
 "DO Probe Calibration":"IV.E",
 "LAF Sanitization":"IV.F, VI.J",
 "Antifoam Addition":"IV.F",
 "Cell Receipt and Transfer":"V.A–C",
 "Daily Observations":"V.D/M, VI (table)",
 "Virus Seed Inoculation":"V.D",
 "Weighted-Average Titer":"V.E",
 "MOI Calculation":"V.F",
 "Thaw and Add Virus Seed":"V.G",
 "Actual MOI":"V.H",
 "Transfer Line Clip-Off":"V.I",
 "Inoculation Finish Time and SUB Label":"V.K",
 "Waste Inactivation":"V.L",
 "Sample Submission":"VI.K, XI.E/H/L",
 "Harvest - Unifuge Centrifugation":"VI.B–I",
 "Harvest Controller Shutdown":"VI.F",
 "Vessel Transfer":"VI.I, X, XI.C",
 "Cold Storage":"VI.L",
 "SUB Filter Decontamination":"VII.A",
 "Filter Integrity Test":"VII.B–C",
 "Pre-Inactivation Thaw":"VIII.A–B",
 "BEI Cyclization":"IX.A–E",
 "BEI Cyclization Hold":"IX.C–D",
 "Viral Inactivation":"X.A–I",
 "BEI Waste Neutralization":"X.J",
 "pH Adjustment":"IX.E, X.F, XI.G",
 "Neutralization":"XI.A",
 "Neutralization Hold":"XI.B",
 "Formulation":"XI.D, XI.F",
 "Bulk Dispense and Disposition":"XI.C, I–J",
 "Label Control and Reconciliation":"VI.K, XI.K",
 "SAP and Excel Transaction Record":"XI.M",
 "Comments":"Comments",
}

PHASES = [
 ("Batch Identification", ["Virus Seed Identification","Cell Identification"]),
 ("Phase 1 — Production Vessel Preparation",
   ["Vessel and Single-Use Bag Setup","Equipment Sterilization Verification","Probe Identification",
    "pH Probe Calibration","Assembly and Line Connections"]),
 ("Phase 2 — Media Preparation",
   ["Controller and Gas Flow Verification","Fill Volume Calculation","Component Addition","Medium Addition",
    "Controller Setpoint and Alarm Configuration","DO Probe Calibration","LAF Sanitization","Antifoam Addition"]),
 ("Phase 3 — Plant / Infection",
   ["Cell Receipt and Transfer","Daily Observations","Virus Seed Inoculation","Weighted-Average Titer",
    "MOI Calculation","Thaw and Add Virus Seed","Actual MOI","Transfer Line Clip-Off",
    "Inoculation Finish Time and SUB Label","Waste Inactivation"]),
 ("Phase 4 — Culture & Harvest",
   ["Sample Submission","Harvest - Unifuge Centrifugation","Harvest Controller Shutdown","Vessel Transfer",
    "Cold Storage"]),
 ("Phase 5 — SUB Filter Decontamination & Integrity",
   ["SUB Filter Decontamination","Filter Integrity Test"]),
 ("Phase 6 — Pre-Inactivation", ["Pre-Inactivation Thaw"]),
 ("Phase 7 — Cyclization & Inactivation",
   ["BEI Cyclization","BEI Cyclization Hold","Viral Inactivation","BEI Waste Neutralization","pH Adjustment"]),
 ("Phase 8 — Neutralization, Formulation & Dispense",
   ["Neutralization","Neutralization Hold","Formulation","Bulk Dispense and Disposition",
    "Label Control and Reconciliation"]),
 ("Phase 9 — Closeout", ["SAP and Excel Transaction Record","Comments"]),
]

CSS = """
 @page { size: 420mm 297mm; margin: 12mm; }
 * { box-sizing:border-box; }
 body { margin:0; font-family:Arial,Helvetica,sans-serif; color:#222; }
 .doc { max-width:1500px; margin:0 auto; }
 .cover { border:2px solid #2f6d2f; border-radius:6px; padding:22px 26px; margin-bottom:18px; }
 .pi-title { font-size:22px; font-weight:bold; color:#2f4d2f; }
 .pi-sub { font-size:15px; color:#444; margin:4px 0 16px; }
 .pi-fields { border-collapse:collapse; width:100%; font-size:12.5px; }
 .pi-fields td { border:1px solid #ccc; padding:7px 10px; }
 .pi-fields td.k { background:#f3f5f1; font-weight:bold; width:170px; }
 .legend { margin-top:14px; font-size:12px; color:#555; background:#f7f9f4; border:1px solid #dfe6d6; padding:9px 12px; border-radius:4px; }
 h2 { font-size:16px; color:#2f4d2f; margin:22px 0 8px; }
 .xwalk { border-collapse:collapse; width:100%; font-size:11.5px; }
 .xwalk th { background:#2f4d2f; color:#fff; text-align:left; padding:6px 9px; border:1px solid #2f4d2f; }
 .xwalk td { border:1px solid #ccc; padding:5px 9px; }
 .xwalk td.ph { background:#eef4e2; font-weight:bold; }
 .phase { background:#2f4d2f; color:#fff; font-size:15px; font-weight:bold; padding:10px 14px; border-radius:4px;
   margin:20px 0 12px; page-break-before:always; page-break-after:avoid; }
 .xcard { border:1.5px solid #2f6d2f; border-radius:6px; overflow:hidden; margin:0 0 14px; page-break-inside:avoid; }
 .xhead { background:#eef4e2; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; }
 .xtitle { font-weight:bold; font-size:13.5px; color:#2f4d2f; }
 .xref { font-size:10.5px; color:#5a6b5a; background:#dfeacb; border:1px solid #c4d3a8; border-radius:10px; padding:2px 10px; }
 .xbody { padding:13px; }
 .sec-head { background:#f4f6f8; border:1px solid #e2e4e7; font-weight:bold; font-size:11px; color:#3a3d42; padding:7px 11px; }
 .sec-body { border:1px solid #e2e4e7; border-top:none; padding:10px 11px; font-size:11.5px; color:#2c7c9c; line-height:1.5; }
 .sec-body .v { color:#1666c8; }
 .di-label { font-weight:bold; font-size:11px; color:#3a3d42; margin:11px 0 5px; }
 .hdrfields { margin:9px 0 4px; }
 .hdrfield { margin:6px 0; font-size:11.5px; color:#3a3d42; }
 .hdrfield .hlabel { display:inline-block; min-width:200px; }
 .hdrfield .req { color:#d23b3b; }
 .hdrfield .hinput { display:inline-block; width:210px; height:22px; border:1px solid #5a9bd4; border-radius:3px;
   vertical-align:middle; background:#fff; }
 .hdrfield .hinput.ro { border-color:#cfcfcf; background:#f3f4f6; }
 .hdrfield .fmbtn { display:inline-block; background:#fff; border:1px solid #b6bac0; border-radius:3px;
   padding:2px 9px 2px 6px; font-size:11px; color:#2a2d31; }
 .hdrfield .fmbtn .tri { font-size:8px; margin-right:3px; }
 table.di { width:100%; border-collapse:collapse; table-layout:fixed; }
 table.di th { background:#f2f3f5; color:#3a3d42; font-weight:bold; font-size:10px; text-align:left; padding:6px 6px; border:1px solid #cacdd2; word-wrap:break-word; }
 table.di td { background:#fff; border:1px solid #cacdd2; height:26px; padding:4px 6px; font-size:10px; }
 table.di th.idxh, table.di td.idxc { width:26px; text-align:center; color:#6b6f76; }
 table.di th.oph, table.di td.opc { width:16px; text-align:center; }
 table.di td.opc { font-weight:bold; color:#3a3d42; background:#f7f8f9; }
 table.di td .ddcell { display:block; position:relative; border:1px solid #b6bac0; border-radius:3px; padding:3px 17px 3px 6px; background:#fff; font-size:9.5px; color:#2a2d31; }
 table.di td .ddcell .ddchev { position:absolute; right:6px; top:4px; color:#6b6f76; font-size:7px; }
 table.di td.ro { background:#f3f4f6; }
 table.di td .fmclock { color:#9aa0a6; font-size:9px; margin-right:2px; }
 table.di td .fixed { color:#555; font-size:9.5px; }
 .req { color:#d23b3b; }
 .btn { display:inline-block; background:#fff; border:1px solid #b6bac0; border-radius:3px; padding:2px 7px; font-size:9.5px; }
 .btn .tri { font-size:7px; margin-right:3px; }
 .xform .fmbtn { display:inline-block; background:#fff; border:1px solid #b6bac0; border-radius:3px;
   padding:2px 8px 2px 6px; font-size:10px; color:#2a2d31; vertical-align:middle; margin-right:7px; }
 .xform .fmbtn .tri { font-size:7px; margin-right:3px; }
 .xform .fmstack { display:inline-block; vertical-align:middle; text-align:center; }
 .xform .fmstack .fmbtn { display:block; margin:0 auto 3px; width:max-content; }
 .xform .fmstack .finput { display:block; margin:0 0 4px; }
 .addrow { color:#1666c8; font-size:11px; margin-top:7px; }
 .witness { text-align:right; margin-top:10px; font-size:11px; color:#3a3d42; }
 .witness .b { display:inline-block; width:150px; height:22px; border:1px solid #5a9bd4; border-radius:3px; vertical-align:middle; }
 .xform { padding:4px 0; }
 .xform .frow { text-align:right; margin:6px 0; font-size:11.5px; color:#3a3d42; }
 .xform .flabel { display:inline-block; margin-right:10px; }
 .xform .req { color:#d23b3b; }
 .xform .finput { display:inline-block; width:170px; height:22px; border:1px solid #5a9bd4; border-radius:3px;
   vertical-align:middle; background:#fff; color:#777; font-size:10px; padding:3px 6px; text-align:left; }
 .xform .finput.ro { border-color:#cfcfcf; background:#f3f4f6; }
 .xform .fdd { display:inline-block; width:170px; height:22px; border:1px solid #b6bac0; border-radius:3px;
   vertical-align:middle; background:#fff; font-size:10px; color:#2a2d31; padding:3px 17px 3px 6px;
   position:relative; text-align:left; }
 .xform .fdd .fddchev { position:absolute; right:6px; top:5px; color:#6b6f76; font-size:7px; }
 .xbody .sec-body ul { margin:6px 0 0; padding-left:18px; }
 .xbody .sec-body li { margin:2px 0; }
 .xsignoff { margin-top:12px; text-align:right; }
 .xsignoff .sorow { margin:6px 0; font-size:11.5px; color:#3a3d42; }
 .xsignoff .solabel { display:inline-block; margin-right:10px; }
 .xsignoff .req { color:#d23b3b; }
 .xsignoff .sofield { display:inline-block; width:170px; height:22px; border:1px solid #5a9bd4; border-radius:3px; vertical-align:middle; background:#fff; }
"""

def card(step):
    ref = OLDREF.get(step['folder'],'')
    head = (f'<div class="xhead"><span class="xtitle">SMPL: {html.escape(step["title"])}</span>'
            f'<span class="xref">Original BR: Section {html.escape(ref)}</span></div>')
    instr = f'<div class="sec-head">Instructions</div><div class="sec-body">{step["instructions"]}</div>'
    if 'form' in step:
        inner = instr + f'<div class="xform">{form_rows(step["form"])}</div>'
    elif 'longtext' in step:
        inner = instr + f'<div class="xsignoff">{signoff_rows(step.get("signoffs",["Performed By","Check By"]))}</div>'
    else:
        thead = th_cells(step['cols'])
        # Build-guide rule: one data row per table (+ Add Row). rowdata → first pre-filled row.
        if step.get('rowdata'):
            rows = render_row(step['cols'], step['rowdata'][0])
        else:
            rows = render_row(step['cols'])
        wl = html.escape(step.get('witness_label','Witness By'))
        hdr = header_field_rows(step['header_fields']) if step.get('header_fields') else ''
        inner = (instr + hdr + '<div class="di-label">Data Input</div>'
                 f'<table class="di">{thead}{rows}</table><div class="addrow">+ Add Row</div>'
                 f'<div class="witness">{wl}<span class="req"> *</span> <span class="b"></span></div>')
    return f'<div class="xcard">{head}<div class="xbody">{inner}</div></div>'

def crosswalk():
    out=['<h2>Old &harr; New Crosswalk</h2><table class="xwalk"><tr><th>EBR Phase</th><th>New XStep</th><th>Original MABR Section</th></tr>']
    for ph,folders in PHASES:
        first=True
        for f in folders:
            s=BYF[f]
            phcell=f'<td class="ph" rowspan="{len(folders)}">{html.escape(ph)}</td>' if first else ''
            out.append(f'<tr>{phcell}<td>SMPL: {html.escape(s["title"])}</td><td>{html.escape(OLDREF.get(f,""))}</td></tr>')
            first=False
    out.append('</table>')
    return ''.join(out)

def cover():
    fields=[("Material / Product","8012xxx&nbsp;/&nbsp;Sample Virus in 2000L SUB"),
            ("Process Order","____________"),("Batch #","____________"),
            ("Control Recipe","____________"),("Master Recipe","____________"),
            ("Plant / Bldg-Rm","____________"),("USDA License","XXXX BP MFG US 2000L SUB"),
            ("Effective Date","____________")]
    rows=''.join(f'<tr><td class="k">{k}</td><td>{val}</td></tr>' for k,val in fields)
    return f"""<div class="cover">
      <div class="pi-title">SiMPL Electronic Batch Record &mdash; Process Instruction (PI) Sheet</div>
      <div class="pi-sub">Sample Virus in 2000L Single-Use Bioreactor (SUB) &mdash; U.S. Use &nbsp;|&nbsp; <b>NEW (XStep-based EBR)</b></div>
      <table class="pi-fields">{rows}</table>
      <div class="legend"><b>How to read this:</b> this is the NEW digital EBR assembled from reusable XStep building blocks.
      Each step shows the original paper batch-record section it replaces ("Original BR: Section ___"), so it can be
      compared directly against <i>MABR &mdash; 100/2000L SUB Manufacturing Directions</i>. Recurring blocks (e.g. Daily
      Observations, Sample Submission, pH Adjustment, LAF Sanitization, Vessel Transfer) are shown once and re-used at each
      occurrence in the live recipe.</div>
    </div>"""

def build():
    body=[cover(), crosswalk()]
    for ph,folders in PHASES:
        body.append(f'<div class="phase">{html.escape(ph)}</div>')
        for f in folders:
            body.append(card(BYF[f]))
    doc=f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='doc'>{''.join(body)}</div></body></html>"
    hp=os.path.join(HTMLDIR,'merck_ebr.html')
    open(hp,'w',encoding='utf-8').write(doc)
    # also a viewing copy in the deliverable folder
    open(os.path.join(OUTDIR,'Merck EBR (PI Sheet) - NEW.html'),'w',encoding='utf-8').write(doc)
    pdf=os.path.join(OUTDIR,'Merck EBR (PI Sheet) - NEW.pdf')
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--no-pdf-header-footer',
        f'--print-to-pdf={pdf}','file:///'+hp.replace('\\','/')],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # preview png of the top (cover + crosswalk start)
    prev=os.path.join(HTMLDIR,'ebr_preview.png')
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',
        '--window-size=1560,1500',f'--screenshot={prev}','file:///'+hp.replace('\\','/')],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('built PDF:',pdf)
    print('preview:',prev)

if __name__=='__main__':
    build()
