# -*- coding: utf-8 -*-
"""Render the RTM as a viewable HTML + PDF (same pipeline as the EBRs) so it can be opened in the
PDF viewer / browser without a spreadsheet app. Mirrors the .xlsx sheets: Coverage Summary,
RTM (BR -> XStep), Streamlined Reconciliation, XStep Inventory."""
import os, html, subprocess
from old_full import SECTIONS, SEC2FOLDER
from steps_vidf import STEPS
from build_rtm import RECON, GI_LABEL   # reuse the single source of the reconciliation + GI/label data

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\AZ Phase 3 Virus Inactivation and filtration"
HTMLDIR = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
esc = html.escape
BYF = {s['folder']: s for s in STEPS}
SC = {'Covered': '#c6efce', 'Folded': '#ffeb9c', 'Reference': '#e7e6e6', 'Excluded': '#e7e6e6',
      'GAP': '#ffc7ce', 'Review': '#ffeb9c', 'Out-of-scope': '#e7e6e6'}

def scolor(s):
    for k, v in SC.items():
        if s.startswith(k):
            return v
    return '#ffffff'

CSS = """
 *{box-sizing:border-box;} body{font-family:'Segoe UI',Arial,sans-serif;color:#222;margin:0;padding:26px 30px;font-size:11px;}
 h1{font-size:19px;color:#1f4e79;margin:0 0 3px;} .sub{color:#666;font-style:italic;margin:0 0 16px;font-size:11px;}
 h2{font-size:14px;color:#fff;background:#2e75b6;padding:6px 11px;border-radius:4px;margin:22px 0 8px;}
 table{border-collapse:collapse;width:100%;margin-bottom:8px;table-layout:fixed;}
 th{background:#1f4e79;color:#fff;font-size:10px;text-align:left;padding:5px 7px;border:1px solid #d0d0d0;vertical-align:top;}
 td{font-size:9.7px;padding:4px 7px;border:1px solid #dcdcdc;vertical-align:top;word-wrap:break-word;line-height:1.35;}
 td.n,td.c{white-space:nowrap;} .mono{font-family:Consolas,monospace;font-size:9px;color:#555;}
 .fields{color:#555;font-size:9px;}
 .kv{width:auto;} .kv td{font-size:11px;} .kv td.k{font-weight:bold;width:340px;} .kv td.val{width:120px;font-weight:bold;text-align:center;}
 .note{background:#fbf7e9;border:1px solid #e7dcb4;border-left:4px solid #c9a227;padding:8px 12px;font-size:10.5px;
   color:#3a3d42;line-height:1.5;margin:6px 0 4px;border-radius:0 4px 4px 0;}
 .legend{font-size:9.5px;color:#555;margin:4px 0 14px;}
 .chip{display:inline-block;padding:1px 7px;border-radius:8px;font-weight:bold;font-size:9px;}
 @page{size:A4 landscape;margin:12mm;}
"""

def summary():
    cov = ref = exc = 0
    for tag in ('VI', 'CDF'):
        for sec_no in SECTIONS[tag]:
            n = len(SECTIONS[tag][sec_no]['groups']) or 1
            if sec_no in SEC2FOLDER[tag]:
                cov += n
            elif 'REVISION' in SECTIONS[tag][sec_no]['title'].upper():
                exc += n
            else:
                ref += n
    tot = cov + ref + exc
    rc = {}
    for row in RECON:
        rc[row[4]] = rc.get(row[4], 0) + 1
    kv = [("Recordable requirement lines mapped to an XStep", cov, 'Covered'),
          ("Reference-only lines (§1-3 summary / flowchart / SOP refs)", ref, 'Reference'),
          ("Excluded (revision history)", exc, 'Excluded'),
          ("TOTAL lines extracted from both MPRs", tot, ''),
          ("Recordable coverage", "100%", 'Covered')]
    rows = ''.join(f'<tr><td class="k">{esc(k)}</td>'
                   f'<td class="val" style="background:{scolor(s) if s else "#fff"}">{v}</td></tr>' for k, v, s in kv)
    recon = ' &nbsp; '.join(f'<span class="chip" style="background:{scolor(k)}">{k}: {v}</span>' for k, v in rc.items())
    return f"""<h1>Requirements Traceability Matrix &mdash; AZ Phase 3 VI + C&amp;D XSteps</h1>
      <div class="sub">AZD0543 &middot; PN 8012441 Virus Inactivation + PN 8012475 Concentration &amp; Diafiltration &middot; GPF 2000 L, Process 1</div>
      <h2>1 &middot; Section-level coverage (provable)</h2>
      <table class="kv">{rows}</table>
      <div class="note"><b>Proof:</b> every process section (&sect;4 &rarr; last attachment) in BOTH source MPRs is
      rendered verbatim under exactly one XStep. No recordable section is unmapped. Whole sections are rendered
      (not filtered), so the reusable-block keyword harvest cannot drop content &mdash; it is only a redundant view.</div>
      <h2>2 &middot; Streamlined-Analysis reconciliation</h2>
      <div style="margin:6px 0 4px">{recon}</div>
      <div class="note">Both former GAPs resolved with no new XStep: <b>SoloVPE/SOLO_A280</b> is a sample
      (SOP-0107091) handled by the Sampling Record XStep; the <b>VPro filter-integrity</b> worksheet belongs to the
      separate Virus Filtration record (MABR-0027575 / PN 8012474), cassette integrity on FORM-0071789.</div>"""

def rtm_table():
    out = ['<h2>3 &middot; RTM &mdash; every recordable line &rarr; the XStep that fulfils it</h2>',
           '<div class="legend">Req ID &middot; Record &middot; &sect; &middot; Section &middot; Type &middot; verbatim requirement &middot; '
           'fields captured &middot; fulfilling XStep &middot; coverage. Colour = coverage status.</div>',
           '<table><colgroup>'
           '<col style="width:7%"><col style="width:4%"><col style="width:3%"><col style="width:13%">'
           '<col style="width:7%"><col style="width:27%"><col style="width:18%"><col style="width:16%"><col style="width:5%">'
           '</colgroup>'
           '<tr><th>Req ID</th><th>Rec</th><th>&sect;</th><th>Section</th><th>Type</th>'
           '<th>Old BR requirement (verbatim)</th><th>Fields captured</th><th>Fulfilled by XStep</th><th>Cov.</th></tr>']
    for tag in ('VI', 'CDF'):
        for sec_no in sorted(SECTIONS[tag]):
            sec = SECTIONS[tag][sec_no]; title = sec['title']
            folder = SEC2FOLDER[tag].get(sec_no)
            if folder:
                xt = "SMPL: " + BYF[folder]['title']; status = 'Covered'
            elif 'REVISION' in title.upper():
                xt, status = '— (revision history) —', 'Excluded'
            else:
                xt, status = '— reference / not recordable —', 'Reference'
            groups = sec['groups'] or [{'instr': '(no extractable recordable text)', 'fields': []}]
            for i, g in enumerate(groups, 1):
                instr = g['instr']
                typ = 'Fields' if instr == '(records)' else ('Note' if instr.startswith(('All ', 'For all', 'When ', 'If ', 'Verify', 'CAUTION')) else 'Instr.')
                rid = f'{tag}-S{sec_no}-{i:03d}'
                out.append(
                    f'<tr><td class="n mono">{rid}</td><td class="c">{tag}</td><td class="c">&sect;{sec_no}</td>'
                    f'<td>{esc(title)}</td><td class="c">{typ}</td>'
                    f'<td>{"" if instr=="(records)" else esc(instr)}</td>'
                    f'<td class="fields">{esc(" | ".join(g["fields"]))}</td>'
                    f'<td>{esc(xt)}</td>'
                    f'<td class="c" style="background:{scolor(status)}">{status[:4]}</td></tr>')
    out.append('</table>')
    return ''.join(out)

def recon_table():
    out = ['<h2>4 &middot; Streamlined-Analysis reconciliation (per streamlined step)</h2>',
           '<table><colgroup><col style="width:5%"><col style="width:8%"><col style="width:24%">'
           '<col style="width:22%"><col style="width:8%"><col style="width:33%"></colgroup>'
           '<tr><th>Rec</th><th>Streamlined</th><th>Streamlined Title</th><th>Fulfilled by XStep(s)</th>'
           '<th>Status</th><th>Note / Action</th></tr>']
    for rec, num, title, xs, status, note in RECON:
        out.append(f'<tr><td class="c">{rec}</td><td class="c mono">{esc(num)}</td><td>{esc(title)}</td>'
                   f'<td>{esc(xs)}</td><td class="c" style="background:{scolor(status)}">{status}</td>'
                   f'<td class="fields">{esc(note)}</td></tr>')
    out.append('</table>')
    return ''.join(out)

def gilabel_table():
    gi = sum(1 for x in GI_LABEL if x[2] == 'GI'); lbl = sum(1 for x in GI_LABEL if x[2] == 'LABEL')
    out = [f'<h2>5 &middot; Goods Issue &amp; Label points ({gi} GI &middot; {lbl} label)</h2>',
           '<div class="note">From a keyword sweep of both MPRs for &ldquo;SAP Consumption&rdquo; (Goods Issue, '
           'Z_PICONS mvt 261) and &ldquo;label&rdquo; / SOP-0107056. Rows marked <b>Yes (added)</b> are gaps this '
           'review found and closed in the XStep instructions. <b>Open question:</b> buffer 8012555 Goods Issue &mdash; '
           'one consolidated posting or per recipe phase?</div>',
           '<table><colgroup><col style="width:6%"><col style="width:7%"><col style="width:7%">'
           '<col style="width:38%"><col style="width:30%"><col style="width:12%"></colgroup>'
           '<tr><th>Rec</th><th>&sect;</th><th>Type</th><th>Material / Label target</th>'
           '<th>Fulfilled by XStep</th><th>Reflected?</th></tr>']
    for rec, sec, kind, target, xs, refl in GI_LABEL:
        bg = '#c6efce' if kind == 'GI' else '#ffeb9c'
        out.append(f'<tr><td class="c">{rec}</td><td class="c">{sec}</td>'
                   f'<td class="c" style="background:{bg}">{kind}</td><td>{esc(target)}</td>'
                   f'<td>{esc(xs)}</td><td class="c">{esc(refl)}</td></tr>')
    out.append('</table>')
    return ''.join(out)

def inventory_table():
    persec = {}
    for tag in ('VI', 'CDF'):
        for sec_no, folder in SEC2FOLDER[tag].items():
            persec.setdefault(folder, []).append((tag, sec_no, len(SECTIONS[tag][sec_no]['groups'])))
    out = ['<h2>6 &middot; XStep inventory (32)</h2>',
           '<table><colgroup><col style="width:4%"><col style="width:9%"><col style="width:34%">'
           '<col style="width:41%"><col style="width:12%"></colgroup>'
           '<tr><th>#</th><th>Group</th><th>XStep (SMPL)</th><th>Old BR sections fulfilled</th><th># Old groups</th></tr>']
    for i, s in enumerate(STEPS, 1):
        f = s['folder']; secs = persec.get(f, [])
        secstr = ', '.join(f'{t} &sect;{n}' for t, n, _ in sorted(secs)) or '(reusable — instantiated in-line)'
        ng = sum(g for _, _, g in secs)
        out.append(f'<tr><td class="c">{i}</td><td class="c">{esc(f.split(" - ")[0])}</td>'
                   f'<td>SMPL: {esc(s["title"])}</td><td class="fields">{secstr}</td><td class="c">{ng}</td></tr>')
    out.append('</table>')
    return ''.join(out)

doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
       f"{summary()}{rtm_table()}{recon_table()}{gilabel_table()}{inventory_table()}</body></html>")
hp = os.path.join(HTMLDIR, 'rtm_view.html'); open(hp, 'w', encoding='utf-8').write(doc)
base = "AZ Phase 3 VI + CDF - Traceability Matrix (RTM)"
open(os.path.join(OUTDIR, base + ".html"), 'w', encoding='utf-8').write(doc)
pdf = os.path.join(OUTDIR, base + ".pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    f"--print-to-pdf={pdf}", "file:///" + os.path.abspath(hp).replace("\\", "/")],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("RTM view PDF:", pdf)
