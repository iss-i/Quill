# -*- coding: utf-8 -*-
"""Render the VI + C&D XStep mock-ups (POC model): one subfolder per XStep under 'XStep mockups',
sorted into two category subfolders — 'New XSteps' (bespoke N/V objects) and 'Reused XSteps' (R
block-stacks shown as a representative PI Sheet view). Pure reuse references with no mock-up data get
no folder. Removes stale folders (incl. the old flat layout). Reuses the shared build_mockups renderer.
Usage: python build_vidf.py            # sync folders + render all mock-ups
       python build_vidf.py "VI - ..."  # re-render one folder by name"""
import os, sys, subprocess, re, shutil
sys.path.insert(0, r"c:\Users\carlo\Dev\TechSpecs\_scratch\mockups")
from build_mockups import build_html, CHROME
from steps_vidf import STEPS, BYF

OUTDIR = r"c:\Users\carlo\Dev\TechSpecs\AZ Phase 3 Virus Inactivation and filtration\XStep mockups"
HTMLDIR = os.path.dirname(os.path.abspath(__file__))
NEW_DIR, REUSE_DIR = "New XSteps", "Reused XSteps"

def _has_mockup(s):
    return any(k in s for k in ('blocks', 'form', 'longtext', 'cols'))

def _subdir(s):
    """Category subfolder: bespoke N/V objects vs reused block-stacks."""
    return NEW_DIR if s['kind'] in ('N', 'V') else REUSE_DIR

def render(s):
    if s['kind'] == 'R' and not _has_mockup(s):
        return False  # pure reuse reference — no bespoke mock-up (sync_folders removes any stale one)
    folder = os.path.join(OUTDIR, _subdir(s), s['folder']); os.makedirs(folder, exist_ok=True)
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
    """Sort mock-up folders into the 'New XSteps' / 'Reused XSteps' category subfolders; remove any
    stale step folder (incl. leftovers from the old flat layout) that no longer holds a mock-up."""
    os.makedirs(OUTDIR, exist_ok=True)
    keep = {NEW_DIR: set(), REUSE_DIR: set()}
    for s in STEPS:
        if s['kind'] in ('N', 'V') or _has_mockup(s):
            keep[_subdir(s)].add(s['folder'])
    removed = []
    # 1) drop anything at the root that isn't one of the two category subfolders (old flat step folders)
    for name in os.listdir(OUTDIR):
        p = os.path.join(OUTDIR, name)
        if os.path.isdir(p) and name not in (NEW_DIR, REUSE_DIR):
            shutil.rmtree(p); removed.append(name)
    # 2) inside each category, drop step folders that no longer belong there
    for sub in (NEW_DIR, REUSE_DIR):
        subp = os.path.join(OUTDIR, sub)
        os.makedirs(subp, exist_ok=True)
        for name in os.listdir(subp):
            p = os.path.join(subp, name)
            if os.path.isdir(p) and name not in keep[sub]:
                shutil.rmtree(p); removed.append(f"{sub}/{name}")
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
        print(f'done — {made} mock-up(s) rendered into New XSteps/ + Reused XSteps/; '
              f'{len(STEPS)} XSteps; {len(removed)} stale folder(s) removed')
        if removed:
            for r in removed: print('  removed:', r)
