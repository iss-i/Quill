# -*- coding: utf-8 -*-
"""Build AZ Phase 3 (AZD8630 Affinity / CaptureSelect CH1-XL) XStep mock-ups + EBR.
Creates a folder for every XStep; renders image.png for the NEW/VARIANT ones;
assembles the EBR PI-sheet PDF cross-referenced to the original MPR (PN 8010457)."""
import os, sys, subprocess, html
sys.path.insert(0, r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups")  # shared renderers
from build_mockups import th_cells, render_row, form_rows, signoff_rows, build_html, header_field_rows
from build_ebr import CSS as BASE_CSS
from steps_az3 import STEPS, PHASES, OLDREF, BYF

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\AZ Phase 3 XStep Mock Ups (POC)"
HTMLDIR = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
esc = html.escape

EXTRA_CSS = """
 .badge { font-size:9px; font-weight:bold; padding:1px 6px; border-radius:8px; margin-left:8px; vertical-align:middle; }
 .b-new { background:#1f7a1f; color:#fff; }
 .b-var { background:#b8860b; color:#fff; }
 .b-reuse { background:#e2e6ea; color:#555; border:1px solid #cfd4d9; }
 .xcard.reuse { border-color:#c7cdd4; }
 .xcard.reuse .xhead { background:#f4f6f8; }
 .rdesc { font-size:11.5px; color:#3a3d42; line-height:1.5; }
 .reuses { font-size:10.5px; color:#2f6d2f; margin-top:6px; }
 .reuses b { color:#1f7a1f; }
 .reuses .tbd { color:#b26a00; }
 .kban { font-size:11px; color:#555; margin:6px 0 16px; }
 .kban b { color:#2f4d2f; }
"""
CSS = BASE_CSS + EXTRA_CSS

def badge(kind):
    m={'N':('NEW','b-new'),'V':('VARIANT','b-var'),'R':('REUSE','b-reuse')}
    t,c=m[kind]; return f'<span class="badge {c}">{t}</span>'

def card(step):
    ref=OLDREF.get(step['folder'],'')
    head=(f'<div class="xhead"><span class="xtitle">SMPL: {esc(step["title"])}{badge(step["kind"])}</span>'
          f'<span class="xref">Original BR: {esc(ref)}</span></div>')
    if step.get('reuses'):
        reuses=f'<div class="reuses">Reuses: <b>{esc(step["reuses"])}</b></div>'
    elif step['kind'] in ('R','V'):
        reuses='<div class="reuses"><span class="tbd">Reuse target: to be confirmed in DE1 100</span></div>'
    else:
        reuses=''
    if step['kind']=='R':
        body=f'<div class="rdesc">{esc(step.get("desc",""))}</div>{reuses}'
        return f'<div class="xcard reuse">{head}<div class="xbody">{body}</div></div>'
    instr=f'<div class="sec-head">Instructions</div><div class="sec-body">{step.get("instructions","")}</div>'+reuses
    if 'form' in step:
        inner=instr+f'<div class="xform">{form_rows(step["form"])}</div>'
    elif 'longtext' in step:
        inner=instr+f'<div class="xsignoff">{signoff_rows(step.get("signoffs",["Performed By","Witnessed By"]))}</div>'
    else:
        show_idx=step.get('index',True)
        thead=th_cells(step['cols'], step.get('idx_label','#') if show_idx else None)
        rows=(render_row(step['cols'], step['rowdata'][0], index=show_idx) if step.get('rowdata')
              else render_row(step['cols'], index=show_idx))
        wl=esc(step.get('witness_label','Witness By'))
        hdr=header_field_rows(step['header_fields']) if step.get('header_fields') else ''
        ftr=f'<div class="xform">{form_rows(step["footer_fields"])}</div>' if step.get('footer_fields') else ''
        witness=(f'<div class="witness">{wl}<span class="req"> *</span> <span class="b"></span></div>'
                 if step.get('witness',True) else '')
        addrow='<div class="addrow">+ Add Row</div>' if step.get('add_row',True) else ''
        inner=(instr+hdr+'<div class="di-label">Data Input</div>'
               f'<table class="di">{thead}{rows}</table>{addrow}{ftr}{witness}')
    return f'<div class="xcard">{head}<div class="xbody">{inner}</div></div>'

def cover():
    fields=[("Material / Product","8010457 / AZD8630 Affinity (CaptureSelect CH1-XL, GPFN, 500 L)"),
            ("MABR / MPR","MABR-0023643"),("General Supplies PO No.","____________"),
            ("MPR Process Order No.","____________"),("Batch #","____________"),
            ("Plant / Facility","GPF-North"),("Process","Process 1 — DSP Step 2 of 8 (Affinity Capture)"),
            ("Effective Date","____________")]
    rows=''.join(f'<tr><td class="k">{k}</td><td>{val}</td></tr>' for k,val in fields)
    nN=sum(1 for s in STEPS if s['kind']=='N'); nV=sum(1 for s in STEPS if s['kind']=='V'); nR=sum(1 for s in STEPS if s['kind']=='R')
    return f"""<div class="cover">
      <div class="pi-title">SiMPL Electronic Batch Record &mdash; Process Instruction (PI) Sheet</div>
      <div class="pi-sub">AZD8630 &mdash; Affinity Chromatography (CaptureSelect CH1-XL, GPF-N, 500 L) &nbsp;|&nbsp; <b>NEW (XStep-based EBR)</b></div>
      <table class="pi-fields">{rows}</table>
      <div class="legend"><b>How to read this:</b> this is the NEW digital EBR assembled from XStep building blocks for the
      AZD8630 Affinity capture step. Each card shows the original MPR section it replaces ("Original BR: Section ___")
      so it compares directly against <i>MABR-0023643 / PN 8010457</i>. Cards are tagged
      {badge('N')} (built new), {badge('V')} (a new variant of an existing XStep), or {badge('R')} (reuses an existing
      DE1&nbsp;100 SMPL XStep as-is &mdash; shown as a summary, no new mock-up needed).</div>
      <div class="kban"><b>{nN}</b> new &nbsp;+&nbsp; <b>{nV}</b> variant &nbsp;+&nbsp; <b>{nR}</b> reuse &nbsp;=&nbsp; <b>{len(STEPS)}</b> XSteps total.</div>
    </div>"""

def crosswalk():
    out=['<h2>XStep &harr; Original MPR Crosswalk</h2><table class="xwalk">'
         '<tr><th>EBR Phase</th><th>XStep</th><th>Type</th><th>Original MPR Section</th></tr>']
    for ph,folders in PHASES:
        first=True
        for f in folders:
            s=BYF[f]
            phcell=f'<td class="ph" rowspan="{len(folders)}">{esc(ph)}</td>' if first else ''
            out.append(f'<tr>{phcell}<td>SMPL: {esc(s["title"])}</td><td>{s["kind"]}</td>'
                       f'<td>{esc(OLDREF.get(f,""))}</td></tr>')
            first=False
    out.append('</table>')
    return ''.join(out)

def render_mockup(step):
    folder=os.path.join(OUTDIR, step['folder'])
    htmlpath=os.path.join(HTMLDIR, 'mk_'+step['folder'].replace(' ','_')+'.html')
    open(htmlpath,'w',encoding='utf-8').write(build_html(step))
    out=os.path.join(folder,'image.png')
    w=step.get('w',1740); h=step.get('h',760)
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',
        f'--window-size={w},{h}',f'--screenshot={out}','file:///'+htmlpath.replace('\\','/')],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(htmlpath)

def build():
    # 1) create a folder for every XStep
    for s in STEPS:
        os.makedirs(os.path.join(OUTDIR, s['folder']), exist_ok=True)
    # 2) render mock-ups for NEW + VARIANT only
    made=[]
    for s in STEPS:
        if s['kind'] in ('N','V'):
            render_mockup(s); made.append(s['folder'])
    # 3) assemble the EBR
    body=[cover(), crosswalk()]
    for ph,folders in PHASES:
        body.append(f'<div class="phase">{esc(ph)}</div>')
        for f in folders:
            body.append(card(BYF[f]))
    doc=f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='doc'>{''.join(body)}</div></body></html>"
    hp=os.path.join(HTMLDIR,'az3_ebr.html'); open(hp,'w',encoding='utf-8').write(doc)
    open(os.path.join(OUTDIR,'AZ Phase 3 EBR (PI Sheet) - NEW.html'),'w',encoding='utf-8').write(doc)
    pdf=os.path.join(OUTDIR,'AZ Phase 3 EBR (PI Sheet) - NEW.pdf')
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--no-pdf-header-footer',
        f'--print-to-pdf={pdf}','file:///'+hp.replace('\\','/')],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('folders:',len(STEPS),'| mock-ups rendered (N+V):',len(made))
    print('EBR PDF:',pdf)

if __name__=='__main__':
    sel=sys.argv[1:]
    if sel:
        # re-render only the named mock-up folder(s); do NOT touch the EBR
        for f in sel:
            for s in STEPS:
                os.makedirs(os.path.join(OUTDIR, s['folder']), exist_ok=True)
            render_mockup(BYF[f]); print('rendered mock-up:', f)
    else:
        build()
