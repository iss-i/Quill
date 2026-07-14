# -*- coding: utf-8 -*-
import json, sys
KEYS={'PPPI_FUNCTION_NAME':'FUNC','PPPI_VALIDATION_FUNCTION':'VALID','PPPI_EVENT':'EVENT',
      'PPPI_BUTTON_TEXT':'BUTTON','PPPI_COMMAND':'CMD','PPPI_COLUMN_NAME':'COL','PPPI_FIELD_NAME':'FLD'}
def walk(n, path, out):
    st=n.get('stext','') or ''
    instr=n.get('instr')
    if isinstance(instr,dict):
        for r in (instr.get('rows') or []):
            kind=r.get('kind'); label=(r.get('label') or '')
            fields={}
            for f in (r.get('fields') or []):
                dom=f.get('domain'); val=(f.get('value') or '').strip()
                if dom in KEYS and val: fields.setdefault(KEYS[dom],[]).append(val)
            if fields:
                out.append((path+' / '+st, kind, label, fields))
    for ch in (n.get('children') or []):
        walk(ch, path+' / '+st if st else path, out)
d=json.load(open(sys.argv[1],encoding='utf-8'))
if 'result' in d: d=d['result']
root=d.get('root') or d
out=[]; walk(root,'',out)
for path,kind,label,fields in out:
    # only show rows with FUNC/VALID/EVENT/BUTTON
    if any(k in fields for k in ('FUNC','VALID','EVENT','BUTTON')):
        ev=','.join(fields.get('EVENT',[]))
        bt=','.join(fields.get('BUTTON',[]))
        fn=','.join(fields.get('FUNC',[]))
        vl=','.join(fields.get('VALID',[]))
        col=','.join(fields.get('COL',[])+fields.get('FLD',[]))
        seg=path.split(' / ')[-2:]
        print(f"[{kind}] {' / '.join(s for s in seg if s)} | {label[:34]}")
        if ev: print(f"      event: {ev}")
        if bt: print(f"      button: {bt}")
        if col: print(f"      column/field: {col}")
        if fn: print(f"      FUNC: {fn}")
        if vl: print(f"      VALIDATOR: {vl}")
