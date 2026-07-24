# -*- coding: utf-8 -*-
"""Assemble the AZ Phase 3 VI + C&D EBR / PI Sheet on the POC model:
 - each XStep tagged N (new) / V (variant) / R (reuse); R renders a compact reuse card (no mock-up),
   N & V render the mock-up content inline; every card shows the original MPR section + reuse target.
Produces two documents:
 - "... - NEW"        : clean POC-style (badges + XStep<->MPR crosswalk)
 - "... - New vs Old" : same cards + the verbatim old-BR panels beneath each (the 'true comparison').
Reuses the shared renderer (build_mockups) and CSS (build_ebr)."""
import os, sys, html, subprocess
sys.path.insert(0, r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups")
from build_mockups import th_cells, render_row, form_rows, signoff_rows, header_field_rows, blocks_rows
from build_ebr import CSS as BASE_CSS
from steps_vidf import STEPS, PHASES, OLDREF, BYF
from old_full import full_for_folder, harvest_for_folder

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\AZ Phase 3 Virus Inactivation and filtration"
HTMLDIR = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
esc = html.escape
TAGNAME = {'VI': 'VIRUS INACTIVATION', 'CDF': 'CONC / DIAFILTRATION'}

EXTRA_CSS = """
 .badge{font-size:9px;font-weight:bold;padding:1px 6px;border-radius:8px;margin-left:8px;vertical-align:middle;}
 .b-new{background:#1f7a1f;color:#fff;} .b-var{background:#b8860b;color:#fff;}
 .b-reuse{background:#e2e6ea;color:#555;border:1px solid #cfd4d9;}
 .xcard.reuse{border-color:#c7cdd4;} .xcard.reuse .xhead{background:#f4f6f8;}
 .rdesc{font-size:11.5px;color:#3a3d42;line-height:1.5;}
 .reuses{font-size:10.5px;color:#2f6d2f;margin-top:6px;} .reuses b{color:#1f7a1f;}
 .reuses .tbd{color:#b26a00;}
 .mkcap{font-size:10.5px;color:#3a3d42;font-style:italic;margin:12px 0 2px;border-top:1px dashed #cfd4d9;padding-top:9px;}
 .mkcap b{color:#2f6d2f;font-style:normal;}
 .kban{font-size:11px;color:#555;margin:6px 0 16px;} .kban b{color:#2f4d2f;}
 .gate{margin:15px 0 2px;font-size:13px;color:#3a3d42;}
 .gate .glabel{display:inline-block;min-width:200px;font-weight:bold;} .gate .req{color:#d23b3b;}
 .gate .fdd{display:inline-block;width:150px;height:27px;border:1px solid #b6bac0;border-radius:3px;background:#fff;font-size:11.5px;color:#2a2d31;padding:5px 20px 5px 7px;position:relative;vertical-align:middle;}
 .gate .fdd .fddchev{position:absolute;right:8px;top:8px;color:#6b6f76;font-size:8px;}
 .gate .ghint{color:#8a8f96;font-style:italic;font-size:11px;margin-left:10px;}
 .bhead{background:#eef4e2;border:1px solid #d5e0c2;font-weight:bold;font-size:12px;color:#2f4d2f;padding:7px 12px;margin:10px 0 0;}
 .bsub{font-weight:bold;font-size:11.5px;color:#3a3d42;margin:13px 0 2px;padding-bottom:3px;border-bottom:1px solid #e2e4e7;}
 .bnote{font-size:11px;color:#8a6d1f;font-style:italic;margin:4px 0 2px;}
 .gibadge{font-size:9px;font-weight:bold;background:#1f7a1f;color:#fff;padding:1px 7px;border-radius:8px;margin-left:8px;vertical-align:middle;}
 .mk table{width:100%;border-collapse:collapse;table-layout:fixed;margin-top:2px;}
 .mk th{background:#f2f3f5;color:#3a3d42;font-weight:bold;font-size:10px;text-align:left;padding:6px 6px;border:1px solid #cacdd2;word-wrap:break-word;}
 .mk td{background:#fff;border:1px solid #cacdd2;height:26px;padding:4px 6px;font-size:10px;}
 .mk th.idxh,.mk td.idxc{width:26px;text-align:center;color:#6b6f76;}
 .mk td.ro{background:#f3f4f6;}
 .mk td .ddcell{display:block;position:relative;border:1px solid #b6bac0;border-radius:3px;padding:3px 17px 3px 6px;background:#fff;font-size:9.5px;color:#2a2d31;}
 .mk td .ddcell .ddchev{position:absolute;right:6px;top:4px;color:#6b6f76;font-size:7px;}
 .mk td .fmclock{color:#9aa0a6;font-size:9px;margin-right:2px;} .mk td .fixed{color:#555;font-size:9.5px;}
 .mk .btn{display:inline-block;background:#fff;border:1px solid #b6bac0;border-radius:3px;padding:2px 7px;font-size:9.5px;} .mk .btn .tri{font-size:7px;margin-right:3px;}
 .mk .addrow{color:#1666c8;font-size:11px;margin-top:6px;}
 .mk .form{padding:4px 0;}
 .mk .frow{text-align:right;margin:6px 0;font-size:11.5px;color:#3a3d42;} .mk .flabel{display:inline-block;margin-right:10px;}
 .mk .finput{display:inline-block;width:190px;height:22px;border:1px solid #5a9bd4;border-radius:3px;vertical-align:middle;background:#fff;color:#777;font-size:10px;padding:3px 6px;text-align:left;}
 .mk .finput.ro{border-color:#cfcfcf;background:#f3f4f6;}
 .mk .fdd{display:inline-block;width:190px;height:22px;border:1px solid #b6bac0;border-radius:3px;vertical-align:middle;background:#fff;font-size:10px;color:#2a2d31;padding:3px 17px 3px 6px;position:relative;text-align:left;}
 .mk .fdd .fddchev{position:absolute;right:6px;top:5px;color:#6b6f76;font-size:7px;}
 .mk .fmbtn{display:inline-block;background:#fff;border:1px solid #b6bac0;border-radius:3px;padding:2px 8px 2px 6px;font-size:10px;color:#2a2d31;vertical-align:middle;margin-right:7px;} .mk .fmbtn .tri{font-size:7px;margin-right:3px;}
 .mk .fmstack{display:inline-block;vertical-align:middle;text-align:center;} .mk .fmstack .fmbtn{display:block;margin:0 auto 3px;width:max-content;} .mk .fmstack .finput{display:block;margin:0 0 4px;}
 .mk .witness{text-align:right;margin-top:10px;font-size:11px;color:#3a3d42;} .mk .witness input{width:150px;height:22px;border:1px solid #5a9bd4;border-radius:3px;vertical-align:middle;}
 .oldbr{margin:14px 0 2px;border:1px solid #d9c98f;border-top:3px solid #c9a227;background:#fbf7e9;border-radius:4px;padding:9px 12px;page-break-inside:avoid;}
 .oldbr .oh{font-weight:bold;font-size:10.5px;letter-spacing:.4px;color:#7a5c00;margin-bottom:6px;text-transform:uppercase;}
 .oldbr .osec{font-weight:bold;font-size:10.5px;color:#5f4a00;margin:11px 0 5px;border-bottom:1px solid #e7dcb4;padding-bottom:3px;}
 .oldbr .otag{font-weight:600;font-size:8px;background:#e9dfb6;color:#6b5300;padding:1px 6px;border-radius:8px;margin-left:7px;vertical-align:middle;letter-spacing:.3px;}
 .oldbr .oi{font-size:10px;color:#2f3237;margin:6px 0 2px;line-height:1.42;}
 .oldbr .oi:before{content:"\\25B8\\A0";color:#b58a00;font-weight:bold;}
 .oldbr .ofl{margin:1px 0 3px 13px;}
 .oldbr .ofield{display:inline-block;font-size:8.7px;color:#54575c;background:#fff;border:1px solid #e2d9b6;border-radius:3px;padding:1px 6px;margin:2px 3px 0 0;line-height:1.5;}
 .oldbr .note{font-size:9px;color:#8a6d1f;font-style:italic;margin-top:6px;}
"""
CSS = BASE_CSS + EXTRA_CSS

def badge(kind):
    m = {'N': ('NEW', 'b-new'), 'V': ('VARIANT', 'b-var'), 'R': ('REUSE', 'b-reuse')}
    t, c = m[kind]; return f'<span class="badge {c}">{t}</span>'

# ---------- verbatim old-BR panels (only used when show_old=True) ----------
def _render_sections(secs):
    parts, ng = [], 0
    for tag, sec_no, title, groups in secs:
        parts.append(f'<div class="osec">&sect;{sec_no} &nbsp;{esc(title)}'
                     f'<span class="otag">{TAGNAME[tag]}</span></div>')
        for g in groups:
            ng += 1
            parts.append(f'<div class="oi">{esc(g["instr"])}</div>')
            if g['fields']:
                chips = ''.join(f'<span class="ofield">{esc(f)}</span>' for f in g['fields'])
                parts.append(f'<div class="ofl">{chips}</div>')
    return ''.join(parts), ng

def old_block(folder):
    secs = full_for_folder(folder)
    if secs:
        body, ng = _render_sections(secs)
        return (f'<div class="oldbr"><div class="oh">&#9660; Old paper batch record &mdash; '
                f'verbatim requirement this XStep must fulfill ({len(secs)} section(s), {ng} group(s)):</div>'
                f'{body}<div class="note">Instructions shown with the exact fields the operator records '
                f'(chips), in document order under their real section number.</div></div>')
    secs = harvest_for_folder(folder)
    if secs:
        body, ng = _render_sections(secs)
        return (f'<div class="oldbr"><div class="oh">&#9660; Old paper batch record &mdash; verbatim text '
                f'this reusable XStep must fulfill, harvested from every section that records it '
                f'({len(secs)} section(s), {ng} group(s)):</div>{body}'
                f'<div class="note">Instantiated wherever the process needs it, so the text is collected '
                f'from across both records (deduped); the same lines also appear under their unit-op card.</div></div>')
    return ''

# ---------- cards ----------
def _reuses_line(step):
    if step.get('reuses'):
        return f'<div class="reuses">Reuses: <b>{esc(step["reuses"])}</b></div>'
    if step['kind'] in ('R', 'V'):
        return '<div class="reuses"><span class="tbd">Reuse target: to be confirmed in DE1 100</span></div>'
    return ''

def _has_mockup(step):
    return any(k in step for k in ('blocks', 'form', 'longtext', 'cols'))

def _mockup_inner(step):
    """Render the inline PI-Sheet visual for a step from its mock-up data (blocks / form / longtext / table)."""
    if 'blocks' in step:
        return blocks_rows(step['blocks'])
    if 'form' in step:
        return f'<div class="xform">{form_rows(step["form"])}</div>'
    if 'longtext' in step:
        return f'<div class="xsignoff">{signoff_rows(step.get("signoffs",["Performed By","Witnessed By"]))}</div>'
    show_idx = step.get('index', True)
    thead = th_cells(step['cols'], step.get('idx_label', '#') if show_idx else None)
    rows = (render_row(step['cols'], step['rowdata'][0], index=show_idx) if step.get('rowdata')
            else render_row(step['cols'], index=show_idx))
    wl = esc(step.get('witness_label', 'Witness By'))
    hdr = header_field_rows(step['header_fields']) if step.get('header_fields') else ''
    ftr = f'<div class="xform">{form_rows(step["footer_fields"])}</div>' if step.get('footer_fields') else ''
    witness = (f'<div class="witness">{wl}<span class="req"> *</span> <span class="b"></span></div>'
               if step.get('witness', True) else '')
    addrow = '<div class="addrow">+ Add Row</div>' if step.get('add_row', True) else ''
    return (hdr + '<div class="di-label">Data Input</div>'
            f'<table class="di">{thead}{rows}</table>{addrow}{ftr}{witness}')

def card(step, show_old=True):
    ref = OLDREF.get(step['folder'], '')
    head = (f'<div class="xhead"><span class="xtitle">SMPL: {esc(step["title"])}{badge(step["kind"])}</span>'
            f'<span class="xref">Original BR: {esc(ref)}</span></div>')
    old = old_block(step['folder']) if show_old else ''
    if step['kind'] == 'R':
        body = f'<div class="rdesc">{esc(step.get("desc", ""))}</div>{_reuses_line(step)}'
        if _has_mockup(step):
            body += ('<div class="mkcap">&#9660; Representative <b>PI Sheet view</b> &mdash; this is a '
                     '<b>block stack</b> (no new object), assembled from the reused DE1&nbsp;100 blocks named above; '
                     'each labelled section / table below is one of those blocks as it renders in the EBR:</div>'
                     f'{_mockup_inner(step)}')
        return f'<div class="xcard reuse">{head}<div class="xbody">{body}{old}</div></div>'
    instr = (f'<div class="sec-head">Instructions</div><div class="sec-body">{step.get("instructions","")}</div>'
             + _reuses_line(step))
    inner = instr + _mockup_inner(step)
    return f'<div class="xcard">{head}<div class="xbody">{inner}{old}</div></div>'

def cover(show_old=True):
    nN = sum(1 for s in STEPS if s['kind'] == 'N'); nV = sum(1 for s in STEPS if s['kind'] == 'V')
    nR = sum(1 for s in STEPS if s['kind'] == 'R')
    fields = [("Material / Product", "AZD0543 — Antibody-Drug Conjugate (DSP, Process 1, GPF, 2000 L)"),
              ("Records covered", "PN 8012441 Virus Inactivation (Low pH) &nbsp;+&nbsp; PN 8012475 Concentration &amp; Diafiltration (Large Skid UF/DF)"),
              ("MABR / MPR", "MABR-0027570 (VI) &nbsp;|&nbsp; PN 8012475 (C&amp;D)"),
              ("Process Order No.", "____________"), ("Batch #", "____________"),
              ("Plant / Facility", "GPF"), ("Effective Date", "____________")]
    rows = ''.join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k, v in fields)
    mode = "New vs Old" if show_old else "NEW (XStep-based EBR)"
    if show_old:
        detail = ("<b>Beneath each XStep card is the verbatim full text of the old paper section(s) it must "
                  "fulfill</b> &mdash; every instruction with the exact fields the operator recorded &mdash; so you "
                  "can confirm, line by line, that the XStep covers the requirement.")
    else:
        detail = ("For the full line-by-line comparison (verbatim old text beneath each card) see the companion "
                  "<b>&ldquo;New vs Old&rdquo;</b> PDF; traceability is in the RTM.")
    return f"""<div class="cover">
      <div class="pi-title">SiMPL Electronic Batch Record &mdash; PI Sheet &nbsp;|&nbsp; <b>{mode}</b></div>
      <div class="pi-sub">AZD0543 &mdash; Virus Inactivation + Concentration &amp; Diafiltration (2000 L, Process 1)</div>
      <table class="pi-fields">{rows}</table>
      <div class="legend"><b>How to read this:</b> the digital EBR is assembled from XStep building blocks.
      Each card shows the original MPR section it replaces ("Original BR: &sect;___") and is tagged
      {badge('N')} (built new), {badge('V')} (a new variant of an existing SMPL XStep), or {badge('R')}
      (reuses an existing DE1&nbsp;100 SMPL XStep as-is &mdash; shown as a summary, no new mock-up). {detail}</div>
      <div class="kban"><b>{nN}</b> new &nbsp;+&nbsp; <b>{nV}</b> variant &nbsp;+&nbsp; <b>{nR}</b> reuse
      &nbsp;=&nbsp; <b>{len(STEPS)}</b> XSteps for both records.</div>
    </div>"""

def crosswalk():
    out = ['<h2>XStep &harr; Original MPR Crosswalk</h2><table class="xwalk">'
           '<tr><th>EBR Phase</th><th>XStep</th><th>Type</th><th>Original MPR Section</th></tr>']
    for ph, folders in PHASES:
        first = True
        for f in folders:
            s = BYF[f]
            phcell = f'<td class="ph" rowspan="{len(folders)}">{esc(ph)}</td>' if first else ''
            out.append(f'<tr>{phcell}<td>SMPL: {esc(s["title"])}</td><td>{s["kind"]}</td>'
                       f'<td>{esc(OLDREF.get(f, ""))}</td></tr>')
            first = False
    out.append('</table>')
    return ''.join(out)

def build(show_old=True, out_base="AZ Phase 3 VI + CDF EBR (PI Sheet) - New vs Old", html_name="vidf_ebr.html"):
    body = [cover(show_old), crosswalk()]
    for ph, folders in PHASES:
        body.append(f'<div class="phase">{esc(ph)}</div>')
        for f in folders:
            body.append(card(BYF[f], show_old=show_old))
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
           f"<body><div class='doc'>{''.join(body)}</div></body></html>")
    hp = os.path.join(HTMLDIR, html_name); open(hp, 'w', encoding='utf-8').write(doc)
    open(os.path.join(OUTDIR, out_base + ".html"), 'w', encoding='utf-8').write(doc)
    pdf = os.path.join(OUTDIR, out_base + ".pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}", "file:///" + os.path.abspath(hp).replace("\\", "/")],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("XSteps:", len(STEPS), "| EBR PDF:", pdf)

if __name__ == '__main__':
    build(show_old=False, out_base="AZ Phase 3 VI + CDF EBR (PI Sheet) - NEW", html_name="vidf_ebr_new.html")
    build(show_old=True, out_base="AZ Phase 3 VI + CDF EBR (PI Sheet) - New vs Old", html_name="vidf_ebr.html")
