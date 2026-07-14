import json, sys, re

STD = {'GET_SYSTEM_TIME_REMOTE','CMX_TOOLS_FM_SET_VALUE','CMX_TOOLS_FM_SET_DATE_TIME',
       'CMX_TOOLS_FM_SET_DATE','CMX_TOOLS_FM_SET_ATT_FOR_EBR','COPF_CALL_TRANSACTION',
       'CMX_TOOLS_FM_SET_ATT_FOR_PI'}

def is_std(fm):
    f=fm.upper()
    if f in STD: return True
    if f.startswith('Z') or f.startswith('/SMPL/') or f.startswith('ELB_'): return False
    return True  # other bare SAP std

def load(path):
    txt=open(path,encoding='utf-8').read()
    return json.loads(txt)

def walk(node, refchain, out):
    # node: dict. Determine if this node is a reference/step that is Conditional Header / Optional Signature
    stext = node.get('stext') or node.get('step',{}).get('stext') if isinstance(node.get('step'),dict) else node.get('stext')
    stext = node.get('stext','') or ''
    low = stext.lower()
    isref = ('conditional header' in low) or ('optional signature' in low)
    newchain = refchain or isref
    # collect FM fields from this node's instruction rows
    rows = node.get('rows') or []
    fields = node.get('fields') or []
    def scan_fields(flist, label):
        for f in flist:
            dom = f.get('domain') or f.get('domname') or ''
            val = (f.get('value') or '').strip()
            if not val: continue
            if dom=='PPPI_FUNCTION_NAME':
                out.append((val,'FUNC',newchain,stext,label))
            elif dom=='PPPI_VALIDATION_FUNCTION':
                out.append((val,'VALID',newchain,stext,label))
    for r in rows:
        scan_fields(r.get('fields') or [], r.get('label',''))
    scan_fields(fields,'')
    for ch in (node.get('children') or []):
        walk(ch, newchain, out)

def main(path):
    data=load(path)
    root=data.get('root') or data
    out=[]
    walk(root, False, out)
    # dedupe
    main_fms={}
    ref_fms={}
    for val,kind,isref,stext,label in out:
        if is_std(val):
            tgt='STD'
        target = ref_fms if isref else main_fms
        key=val
        target.setdefault(key,{'kind':set(),'steps':set(),'std':is_std(val)})
        target[key]['kind'].add(kind)
        target[key]['steps'].add(stext)
    print("=== MAIN-STEP FMs ===")
    for k in sorted(main_fms):
        d=main_fms[k]
        tag='[STD]' if d['std'] else ''
        print(f"  {k} {tag} kinds={sorted(d['kind'])}")
    print("=== REFERENCE-ONLY FMs (Conditional Header / Optional Signature) ===")
    for k in sorted(ref_fms):
        if k in main_fms: continue
        d=ref_fms[k]
        tag='[STD]' if d['std'] else ''
        print(f"  {k} {tag} kinds={sorted(d['kind'])}")

if __name__=='__main__':
    main(sys.argv[1])
