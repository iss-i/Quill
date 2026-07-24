# -*- coding: utf-8 -*-
"""Generate SiMPL EBR XStep UI mockups (image.png) per XStep, matching the
'Sample Mockup' (SMPL: Medium Addition) reference. Renders HTML via headless Chrome."""
import os, subprocess, html, sys

ROOT = r"c:\Users\carlo\Dev\TechSpecs\Merck XStep Mock Ups"
HTMLDIR = r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups\html"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
os.makedirs(HTMLDIR, exist_ok=True)

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<style>
 * {{ box-sizing:border-box; }}
 body {{ margin:0; font-family:Arial, Helvetica, sans-serif; background:#ffffff; }}
 .modalbar {{ background:#eef0f2; border-bottom:1px solid #d8dbdf; padding:13px 18px;
   font-size:15px; font-weight:bold; color:#1d1d1d; display:flex; justify-content:space-between; align-items:center; }}
 .modalbar .x {{ color:#7a7d82; font-weight:normal; font-size:16px; }}
 .strip {{ height:14px; background:#fbfbfc; border-bottom:1px solid #eef0f2; }}
 .card {{ margin:22px; border:1.5px solid #2f6d2f; border-radius:6px; overflow:hidden; }}
 .card-head {{ background:#eef4e2; color:#2f4d2f; font-weight:bold; font-size:14px; padding:13px 16px; }}
 .card-body {{ padding:16px; }}
 .sec-head {{ background:#f4f6f8; border:1px solid #e2e4e7; font-weight:bold; font-size:12px; color:#3a3d42; padding:9px 13px; }}
 .sec-body {{ border:1px solid #e2e4e7; border-top:none; padding:13px; font-size:12.5px; color:#2c7c9c; line-height:1.55; }}
 .sec-body .v {{ color:#1666c8; }}
 .di-label {{ font-weight:bold; font-size:12px; color:#3a3d42; margin:14px 0 6px; }}
 .hdrfields {{ margin:12px 0 4px; }}
 .hdrfield {{ margin:9px 0; font-size:13px; color:#3a3d42; }}
 .hdrfield .hlabel {{ display:inline-block; min-width:220px; }}
 .hdrfield .req {{ color:#d23b3b; }}
 .hdrfield .hinput {{ display:inline-block; width:230px; height:28px; border:1px solid #5a9bd4; border-radius:3px;
   vertical-align:middle; background:#fff; }}
 .hdrfield .hinput.ro {{ border-color:#cfcfcf; background:#f3f4f6; }}
 .hdrfield .fmbtn {{ display:inline-block; background:#fff; border:1px solid #b6bac0; border-radius:3px;
   padding:4px 11px 4px 8px; font-size:12px; color:#2a2d31; }}
 .hdrfield .fmbtn .tri {{ font-size:8px; margin-right:4px; }}
 table {{ width:100%; border-collapse:collapse; }}
 th {{ background:#f2f3f5; color:#3a3d42; font-weight:bold; font-size:11.5px; text-align:left;
   padding:8px 9px; border:1px solid #cace d2; border:1px solid #cacdd2; white-space:nowrap; }}
 td {{ background:#ffffff; border:1px solid #cacdd2; height:34px; padding:5px 9px; }}
 th.idxh, td.idxc {{ width:38px; text-align:center; color:#6b6f76; }}
 th.oph, td.opc {{ width:22px; text-align:center; }}
 td.opc {{ font-weight:bold; color:#3a3d42; background:#f7f8f9; font-size:13px; }}
 td .ddcell {{ display:block; position:relative; border:1px solid #b6bac0; border-radius:3px; padding:4px 22px 4px 8px; background:#fff; font-size:11px; color:#2a2d31; }}
 td .ddcell .ddchev {{ position:absolute; right:8px; top:6px; color:#6b6f76; font-size:8px; }}
 .req {{ color:#d23b3b; }}
 .btn {{ display:inline-block; background:#ffffff; border:1px solid #b6bac0; border-radius:3px;
   padding:4px 11px 4px 8px; font-size:11px; color:#2a2d31; }}
 .btn .tri {{ font-size:8px; vertical-align:middle; margin-right:4px; }}
 .addrow {{ color:#1666c8; font-size:12px; margin-top:9px; }}
 .witness {{ text-align:right; margin-top:14px; font-size:12px; color:#3a3d42; }}
 .witness .req {{ margin:0 3px; }}
 .witness input {{ width:160px; height:26px; border:1px solid #5a9bd4; border-radius:3px; vertical-align:middle; }}
 .form {{ padding:6px 0 2px; }}
 .frow {{ text-align:right; margin:9px 0; font-size:13px; color:#3a3d42; }}
 .frow .flabel {{ display:inline-block; margin-right:12px; }}
 .frow .req {{ color:#d23b3b; }}
 .frow .finput {{ display:inline-block; width:180px; height:28px; border:1px solid #5a9bd4; border-radius:3px;
   vertical-align:middle; background:#fff; color:#777; font-size:11.5px; padding:5px 7px; text-align:left; }}
 .frow .finput.ro {{ border-color:#cfcfcf; background:#f3f4f6; }}
 .frow .fdd {{ display:inline-block; width:180px; height:28px; border:1px solid #b6bac0; border-radius:3px;
   vertical-align:middle; background:#fff; font-size:11.5px; color:#2a2d31; padding:5px 22px 5px 7px;
   position:relative; text-align:left; }}
 .frow .fdd .fddchev {{ position:absolute; right:8px; top:9px; color:#6b6f76; font-size:8px; }}
 td.ro {{ background:#f3f4f6; }}
 td .fmclock {{ color:#9aa0a6; font-size:10px; margin-right:3px; }}
 td .fixed {{ color:#555; font-size:11px; }}
 .frow .fmbtn {{ display:inline-block; background:#fff; border:1px solid #b6bac0; border-radius:3px;
   padding:4px 10px 4px 7px; font-size:11px; color:#2a2d31; vertical-align:middle; margin-right:8px; }}
 .frow .fmbtn .tri {{ font-size:8px; margin-right:4px; }}
 .frow .fmstack {{ display:inline-block; vertical-align:middle; text-align:center; }}
 .frow .fmstack .fmbtn {{ display:block; margin:0 auto 4px; width:max-content; }}
 .frow .fmstack .finput {{ display:block; margin-bottom:5px; }}
 .sec-body ul {{ margin:8px 0 0; padding-left:20px; }}
 .sec-body li {{ margin:3px 0; }}
 .signoff {{ margin-top:18px; text-align:right; }}
 .sorow {{ margin:9px 0; font-size:13px; color:#3a3d42; }}
 .sorow .solabel {{ display:inline-block; margin-right:12px; }}
 .sorow .req {{ color:#d23b3b; }}
 .sorow .sofield {{ display:inline-block; width:185px; height:28px; border:1px solid #5a9bd4; border-radius:3px;
   vertical-align:middle; background:#fff; }}
 .gate {{ margin:15px 0 2px; font-size:13px; color:#3a3d42; }}
 .gate .glabel {{ display:inline-block; min-width:200px; font-weight:bold; }}
 .gate .req {{ color:#d23b3b; }}
 .gate .fdd {{ display:inline-block; width:150px; height:27px; border:1px solid #b6bac0; border-radius:3px;
   background:#fff; font-size:11.5px; color:#2a2d31; padding:5px 20px 5px 7px; position:relative; vertical-align:middle; }}
 .gate .fdd .fddchev {{ position:absolute; right:8px; top:8px; color:#6b6f76; font-size:8px; }}
 .gate .ghint {{ color:#8a8f96; font-style:italic; font-size:11px; margin-left:10px; }}
 .bhead {{ background:#eef4e2; border:1px solid #d5e0c2; font-weight:bold; font-size:12px; color:#2f4d2f;
   padding:7px 12px; margin:10px 0 0; }}
 .bsub {{ font-weight:bold; font-size:12px; color:#3a3d42; margin:14px 0 2px; padding-bottom:3px;
   border-bottom:1px solid #e2e4e7; }}
 .bnote {{ font-size:11px; color:#8a6d1f; font-style:italic; margin:4px 0 2px; }}
 .gibadge {{ font-size:9px; font-weight:bold; background:#1f7a1f; color:#fff; padding:1px 7px; border-radius:8px;
   margin-left:8px; vertical-align:middle; }}
</style></head><body>
 <div class="modalbar"><span>SMPL: {title}</span><span class="x">&times;</span></div>
 <div class="strip"></div>
 <div class="card">
   <div class="card-head">SMPL: {title}</div>
   <div class="card-body">{body}</div>
 </div>
</body></html>"""

BTN={'@START':'Start','@END':'End','@STAMP':'Record'}

def _hdr_label(c):
    """Strip cell-role prefixes (~ FM-stamp, = computed, %% dropdown) for the header label."""
    return c[1:] if c[:1] in ('~','=','%') else c

def th_cells(cols, idx_label='#'):
    # leftmost row-index column (label overridable; idx_label=None suppresses it, e.g. calc tables)
    out=[] if idx_label is None else [f'<th class="idxh">{html.escape(idx_label)}</th>']
    for c in cols:
        if c.startswith('@OP:'):
            out.append('<th class="oph"></th>')  # calc operator column (×, ÷, +, -, =); blank header
        elif c.startswith('@BTN:'):
            out.append('<th></th>')      # named action button; self-labels, blank header
        elif c in BTN:
            out.append('<th>'+('' if c=='@STAMP' else BTN[c])+'</th>')
        else:
            lbl=_hdr_label(c)
            label=html.escape(lbl.rstrip('*'))
            req='<span class="req"> *</span>' if lbl.endswith('*') else ''
            out.append(f'<th>{label}{req}</th>')
    return '<tr>'+''.join(out)+'</tr>'

def render_row(cols, data=None, idx=1, index=True):
    """Render one table row (prefixed with the standard '#' row-index cell unless index=False).
    `data` maps a column name to a pre-filled read-only value (setpoint / standard-amount
    defaults). Cell roles by prefix:
      @START/@END/@STAMP -> ▶ button;  @BTN:Label -> named ▶ action button;  @OP:x -> calc operator;
      ~Col -> FM-stamped read-only (clock);  =Col -> computed/output read-only;  %Col -> dropdown;
      a col present in `data` -> read-only default;  otherwise -> blank editable input."""
    out=[f'<td class="ro idxc">{idx}</td>'] if index else []
    for c in cols:
        if c.startswith('@OP:'):
            out.append(f'<td class="opc">{html.escape(c[4:])}</td>')
        elif c.startswith('@BTN:'):
            out.append(f'<td><span class="btn"><span class="tri">&#9654;</span>{html.escape(c[5:])}</span></td>')
        elif c in BTN:
            out.append(f'<td><span class="btn"><span class="tri">&#9654;</span>{BTN[c]}</span></td>')
        elif c[:1]=='~':
            val=html.escape((data or {}).get(c,''))
            out.append(f'<td class="ro"><span class="fmclock">&#9201;</span>{val}</td>')
        elif c[:1]=='=':
            val=html.escape((data or {}).get(c,''))
            out.append(f'<td class="ro">{val}</td>')
        elif c[:1]=='%':
            # dropdown restricted to a CT04 characteristic's values (e.g. ZSMPL_CHAR_*)
            val=html.escape((data or {}).get(c,''))
            out.append(f'<td><span class="ddcell">{val or "&nbsp;"}<span class="ddchev">&#9662;</span></span></td>')
        elif data and c in data:
            out.append(f'<td class="ro"><span class="fixed">{html.escape(data[c])}</span></td>')
        else:
            out.append('<td></td>')
    return '<tr>'+''.join(out)+'</tr>'

def form_rows(fields):
    out=[]
    for item in fields:
        label=item[0]; flag=item[1] if len(item)>1 else ''
        ph=item[2] if len(item)>2 else ''
        if flag=='dt':
            # 'dt' = date/time stamp: one ▶ Record button above SEPARATE, labelled Date then Time fields
            out.append('<div class="frow"><span class="flabel"></span>'
                       '<span class="fmbtn" style="margin-right:0"><span class="tri">&#9654;</span>Record</span></div>')
            out.append('<div class="frow"><span class="flabel">Date<span class="req"> *</span></span>'
                       '<span class="finput ro"></span></div>')
            out.append('<div class="frow"><span class="flabel">Time<span class="req"> *</span></span>'
                       '<span class="finput ro"></span></div>')
            continue
        if flag=='b':  # a ▶ Select/Get button (populates the read-only output fields that follow)
            out.append('<div class="frow"><span class="flabel"></span>'
                       f'<span class="fmbtn" style="margin-right:0"><span class="tri">&#9654;</span>{html.escape(label)}</span></div>')
            continue
        if flag=='d':  # dropdown field (restricted values via a CT04 characteristic, e.g. Yes/No)
            out.append(f'<div class="frow"><span class="flabel">{html.escape(label)}<span class="req"> *</span></span>'
                       f'<span class="fdd">{html.escape(ph)}<span class="fddchev">&#9662;</span></span></div>')
            continue
        ast='<span class="req"> *</span>' if flag in ('r','t') else ''
        cls='finput'+(' ro' if flag in ('o','t') else '')
        if flag=='t':
            # 't' = date/time stamp: a ▶ Record button ABOVE the read-only FM-filled field
            # (in non-tabular forms the button sits above its output field, not beside it)
            field=(f'<span class="fmstack"><span class="fmbtn"><span class="tri">&#9654;</span>Record</span>'
                   f'<span class="{cls}">{html.escape(ph)}</span></span>')
        else:
            field=f'<span class="{cls}">{html.escape(ph)}</span>'
        out.append(f'<div class="frow"><span class="flabel">{html.escape(label)}{ast}</span>{field}</div>')
    return ''.join(out)

def header_field_rows(fields):
    """Fields / buttons rendered above a Data Input table (left-aligned). Flags:
       'b' = ▶ Select/Get button;  'o' = read-only output;  'r'/'' = entry (required if 'r')."""
    out=[]
    for item in fields:
        label=item[0]; flag=item[1] if len(item)>1 else ''
        ph=item[2] if len(item)>2 else ''
        if flag=='b':
            out.append(f'<div class="hdrfield"><span class="fmbtn"><span class="tri">&#9654;</span>'
                       f'{html.escape(label)}</span></div>')
            continue
        ast='<span class="req"> *</span>' if flag in ('r','t') else ''
        cls='hinput'+(' ro' if flag=='o' else '')
        out.append(f'<div class="hdrfield"><span class="hlabel">{html.escape(label)}{ast}</span>'
                   f'<span class="{cls}">{html.escape(ph)}</span></div>')
    return '<div class="hdrfields">'+''.join(out)+'</div>'

def _instr(step):
    return f'<div class="sec-head">Instructions</div><div class="sec-body">{step["instructions"]}</div>' if step.get('instructions') else ''

def table_body(step):
    cols=step['cols']
    show_idx=step.get('index',True)
    thead=th_cells(cols, step.get('idx_label','#') if show_idx else None)
    # Build-guide rule: show exactly ONE data row per table mock-up (+ Add Row). For a
    # rowdata table, show the first pre-filled row as the representative example.
    if step.get('rowdata'):
        rows=render_row(cols, step['rowdata'][0], index=show_idx)
    else:
        rows=render_row(cols, index=show_idx)
    witness=''
    if step.get('witness',True):
        wl=html.escape(step.get('witness_label','Witness By'))
        witness=f'<div class="witness">{wl}<span class="req">*</span><input></div>'
    hdr=header_field_rows(step['header_fields']) if step.get('header_fields') else ''
    ftr=f'<div class="form">{form_rows(step["footer_fields"])}</div>' if step.get('footer_fields') else ''
    addrow='<div class="addrow">+ Add Row</div>' if step.get('add_row',True) else ''
    return (f'{_instr(step)}{hdr}<div class="di-label">Data Input</div>'
            f'<table>{thead}{rows}</table>{addrow}{ftr}{witness}')

def form_body(step):
    return f'{_instr(step)}<div class="form">{form_rows(step["form"])}</div>'

def signoff_rows(labels, cls='sorow', fcls='sofield'):
    return ''.join(f'<div class="{cls}"><span class="solabel">{html.escape(s)}<span class="req"> *</span></span>'
                   f'<span class="{fcls}"></span></div>' for s in labels)

def longtext_body(step):
    sos=step.get('signoffs',["Performed By","Check By"])
    return f'{_instr(step)}<div class="signoff">{signoff_rows(sos)}</div>'

def blocks_rows(blocks):
    """Render a composite XStep as a sequence of blocks. Each block dict may carry:
       'gate': (label, options)  -> a Yes/No dropdown that activates the section below
       'head': section title (green bar);  'gi': True -> SAP Goods Issue badge on the head
       'note': italic note;  'fields': form fields  OR  'cols'(+idx_label/rowdata/add_row/index): a table
       'witness': witness label -> right-aligned signature at the block end"""
    out=[]
    for b in blocks:
        if b.get('gate'):
            lbl,opts=b['gate']
            out.append(f'<div class="gate"><span class="glabel">{html.escape(lbl)}<span class="req"> *</span></span>'
                       f'<span class="fdd">{html.escape(opts)}<span class="fddchev">&#9662;</span></span>'
                       f'<span class="ghint">&mdash; activates / deactivates the section below</span></div>')
        # Optional per-block sub-label (names the reused library block behind this section);
        # opt-in via 'bsub' so existing mock-ups are unchanged.
        if b.get('bsub'):
            out.append(f'<div class="bsub">{html.escape(b["bsub"])}</div>')
        # Section header only on tabular blocks (green bar + optional GI badge).
        # Non-tabular process-instruction blocks carry no title — their fields self-label.
        if b.get('head') and 'cols' in b:
            badge=' <span class="gibadge">SAP Goods Issue &middot; Z_PICONS mvt 261</span>' if b.get('gi') else ''
            out.append(f'<div class="bhead">{html.escape(b["head"])}{badge}</div>')
        if b.get('note'):
            out.append(f'<div class="bnote">{html.escape(b["note"])}</div>')
        if 'fields' in b:
            out.append(f'<div class="form">{form_rows(b["fields"])}</div>')
        elif 'cols' in b:
            show_idx=b.get('index',True)
            thead=th_cells(b['cols'], b.get('idx_label','#') if show_idx else None)
            data=(b['rowdata'][0] if b.get('rowdata') else None)
            out.append(f'<table>{thead}{render_row(b["cols"], data, index=show_idx)}</table>')
            if b.get('add_row',True): out.append('<div class="addrow">+ Add Row</div>')
        if b.get('witness'):
            out.append(f'<div class="witness">{html.escape(b["witness"])}<span class="req">*</span><input></div>')
    return '<div class="mk">' + ''.join(out) + '</div>'

def blocks_body(step):
    return f'{_instr(step)}{blocks_rows(step["blocks"])}'

def build_html(step):
    if 'blocks' in step: body=blocks_body(step)
    elif 'form' in step: body=form_body(step)
    elif 'longtext' in step: body=longtext_body(step)
    else: body=table_body(step)
    return TEMPLATE.format(title=html.escape(step['title']), body=body)

def render(step):
    folder=os.path.join(ROOT, step['folder'])
    os.makedirs(folder, exist_ok=True)
    htmlpath=os.path.join(HTMLDIR, step['folder'].replace('/','_')+'.html')
    with open(htmlpath,'w',encoding='utf-8') as f:
        f.write(build_html(step))
    out=os.path.join(folder,'image.png')
    w=step.get('w',1740); h=step.get('h',760)
    url='file:///'+htmlpath.replace('\\','/')
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars',
        '--force-device-scale-factor=1', f'--window-size={w},{h}',
        f'--screenshot={out}', url], check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('rendered', step['folder'])

from steps import STEPS
if __name__=='__main__':
    sel=sys.argv[1:] if len(sys.argv)>1 else None
    for s in STEPS:
        if sel and s['folder'] not in sel: continue
        render(s)
    print('done', len([s for s in STEPS if not sel or s['folder'] in sel]),'mockups')
