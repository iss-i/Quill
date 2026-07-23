# -*- coding: utf-8 -*-
"""Render the VI + C&D XStep mock-ups (POC model): one subfolder per XStep under 'XStep mockups';
render image.png only for NEW/VARIANT XSteps (REUSE steps are folder-only — no bespoke mock-up).
Removes stale subfolders no longer in the XStep set. Reuses the shared build_mockups renderer.
Usage: python build_vidf.py            # sync all folders + render N/V
       python build_vidf.py "VI - ..."  # re-render one folder by name"""
import os, sys, subprocess, re, shutil
sys.path.insert(0, r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups")
from build_mockups import build_html, CHROME
from steps_vidf import STEPS, BYF

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\AZ Phase 3 Virus Inactivation and filtration\XStep mockups"
HTMLDIR = os.path.dirname(os.path.abspath(__file__))

def render(s):
    folder = os.path.join(OUTDIR, s['folder']); os.makedirs(folder, exist_ok=True)
    if s['kind'] == 'R':
        return False  # reuse — no bespoke mock-up
    hp = os.path.join(HTMLDIR, 'mk_' + re.sub(r'[^A-Za-z0-9]+', '_', s['folder']) + '.html')
    open(hp, 'w', encoding='utf-8').write(build_html(s))
    out = os.path.join(folder, 'image.png')
    w = s.get('w', 1740); h = s.get('h', 760)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={w},{h}",
        f"--screenshot={out}", "file:///" + hp.replace("\\", "/")],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(hp)
    return True

def sync_folders():
    """Remove subfolders that are no longer in the XStep set (authorised rework cleanup)."""
    os.makedirs(OUTDIR, exist_ok=True)
    keep = {s['folder'] for s in STEPS}
    removed = []
    for name in os.listdir(OUTDIR):
        p = os.path.join(OUTDIR, name)
        if os.path.isdir(p) and name not in keep:
            shutil.rmtree(p); removed.append(name)
    return removed

if __name__ == '__main__':
    sel = sys.argv[1:]
    if sel:
        for f in sel:
            print('rendered:' if render(BYF[f]) else 'reuse (no mock-up):', f)
    else:
        removed = sync_folders()
        made = 0
        for s in STEPS:
            if render(s): made += 1
        print(f'done — {made} mock-up(s) rendered (N/V); {len(STEPS)} XSteps; {len(removed)} stale folder(s) removed')
        if removed:
            for r in removed: print('  removed:', r)
