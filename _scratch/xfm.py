import json, sys

STD = {'GET_SYSTEM_TIME_REMOTE','CMX_TOOLS_FM_SET_VALUE','CMX_TOOLS_FM_SET_DATE_TIME',
       'CMX_TOOLS_FM_SET_DATE','CMX_TOOLS_FM_SET_ATT_FOR_EBR','COPF_CALL_TRANSACTION',
       'CMX_TOOLS_FM_SET_ATT_FOR_PI'}

def is_std(fm):
    f=fm.upper()
    if f in STD: return True
    if f.startswith('Z') or f.startswith('/SMPL/') or f.startswith('ELB_'): return False
    return True

def walk(node, refchain, out):
    stext = node.get('stext','') or ''
    low = stext.lower()
    isref = refchain or ('conditional header' in low) or ('optional signature' in low)
    instr = node.get('instr')
    if isinstance(instr,dict):
        for r in (instr.get('rows') or []):
            for f in (r.get('fields') or []):
                dom = f.get('domain') or ''
                val = (f.get('value') or '').strip()
                if not val: continue
                if dom=='PPPI_FUNCTION_NAME': out.append((val,'FUNC',isref,stext,r.get('label','')))
                elif dom=='PPPI_VALIDATION_FUNCTION': out.append((val,'VALID',isref,stext,r.get('label','')))
    for ch in (node.get('children') or []):
        walk(ch, isref, out)

def main(path):
    data=json.load(open(path,encoding='utf-8'))
    if 'result' in data: data=data['result']
    root=data.get('root') or data
    out=[]; walk(root, False, out)
    main_fms={}; ref_fms={}
    for val,kind,isref,stext,label in out:
        target = ref_fms if isref else main_fms
        target.setdefault(val,{'kind':set(),'steps':set()})
        target[val]['kind'].add(kind); target[val]['steps'].add(stext)
    print("=== MAIN-STEP FMs (document these) ===")
    for k in sorted(main_fms):
        d=main_fms[k]; tag='[STD-EXCLUDE]' if is_std(k) else ''
        print(f"  {k} {tag} kinds={sorted(d['kind'])}  instr={sorted(s for s in d['steps'] if s)}")
    print("=== REFERENCE-ONLY FMs (skip per scoping rule) ===")
    for k in sorted(ref_fms):
        if k in main_fms: continue
        d=ref_fms[k]; tag='[STD]' if is_std(k) else ''
        print(f"  {k} {tag} kinds={sorted(d['kind'])}")

if __name__=='__main__':
    main(sys.argv[1])
