# Unit Test Script Build Guide — From Functional Spec to Unit Test Script

A repeatable method for turning an XStep **functional spec** (+ its mock-up) into an executable **Unit Test
Script** (`.docx`) in the standardized **AZ Test Script Template**. The UT script proves the *built* XStep behaves
as the spec says — it is the execution evidence for the DE1 / ARS unit-test phase.

Companion to *Functional Spec Build Guide.md* (that gets you the design spec) and *Batch Record to XStep Mockups -
Build Guide.md* (the mock-up). Captured from the AZ Phase 1 (Component Goods Issue) and Phase 2 (EFS Exhaust Filter
Info, Harvest Sampling Calculations) test scripts.

**Reference files** live in the record's `UT Scripts/` folder: `AZ Test Script Template (2).docx` (the empty
template — clone this) and the accepted examples (`Phase 1 - SMPL_ Component Goods Issue`, `Phase 2 - SMPL_EFS
Exhaust Filter Info`, `Harvest Sampling Calculations`). Mirror the closest example for step style.

---

## 1. What the UT script is

- **One script per XStep**, a Word doc uploaded for review then executed by a tester who records Actual Result +
  Pass/Fail against each step. GxP: the Actual Result **must** be documented per step; evidence (screenshots) is
  collected where the script calls for it.
- It is **built from the functional spec** — every control the spec documents (inputs, validations, dropdowns/gates,
  buttons, calcs, goods issue, signatures) becomes one or more test steps with an Expected Result.
- **Author-time vs execution-time.** The builder fills the *design-time* fields (approval author, version, referenced
  docs, test header, pre-requisites/set-up, system/environment) and writes the steps. The tester fills the
  *execution-time* fields at run: Actual Result, Pass/Fail, tester name/signature, date commenced, run #, and the
  pre-requisites-satisfied Yes/No.

---

## 2. The template — fixed structure (clone it; don't rebuild from scratch)

Clone `AZ Test Script Template (2).docx` and fill it — it carries the approved front matter, disclaimer, borders and
signature blocks. Its parts, in order (with the python-docx **table index**):

```
Title page:  <Project Name> / "Test Script" / Template Version Number
Instructions for the Tester   (bullet list — leave as-is)
table 0  Document Approval / Review   (Author / Reviewed / Approved  ×  Name&Role / Signature / Date)
table 1  Version Control              (Version / Date / Description of Changes / Author)
table 2  Referenced Documents         (No. / Document Title and ID / Version / Location)
table 3  Disclaimer                   (leave as-is)
table 4  Test Script header           (Test Script ID & Version # | Test Phase ; Test Name ; Test Objective ; Requirements Tested)
table 5  Pre-requisites / Set-Up      (Pre-requisites ; Set Up Steps | Data Requirements)
table 6  System / Environment / Tester(System Name & Version # ; Environment ; Tester Name / Date / Run #)
table 7  Test Steps                   (Step No. / Action / Description / Expected Result / Actual Result / Pass-Fail-TIL#)
table 8  Test Script Summary Result   (leave as-is — completed at execution)
```

Several header cells are **horizontally merged** (e.g. the value cell in table 4 spans columns 1-3; table 5's
pre-requisite row spans both columns). Set the **first** cell of a merged group — python-docx writes through the
shared `<w:tc>`.

---

## 3. The toolchain (`_scratch/build_<key>_ut.py`)

One small python-docx script per XStep. Shape (see `build_tvs_ut.py`):

```python
from docx import Document
from docx.oxml.ns import qn
from docx.shared import RGBColor
BLACK = RGBColor(0,0,0)
doc = Document(TEMPLATE)                       # clone the empty template

def setc(cell, text):                          # replace a cell's text, multi-line on \n, in BLACK
    for p in cell.paragraphs[1:]: p._p.getparent().remove(p._p)
    p = cell.paragraphs[0]
    for r in list(p.runs): r._r.getparent().remove(r._r)
    for i, ln in enumerate(str(text).split('\n')):
        para = p if i == 0 else cell.add_paragraph()
        run = para.add_run(ln); run.font.color.rgb = BLACK

# fill tables 0,1,2,4,5,6 by (row, cell) index ; then the step table:
t7 = doc.tables[7]
row_tmpl = copy.deepcopy(t7.rows[1]._tr)        # a BORDERED data row to clone
for r in list(t7.rows[1:]): r._tr.getparent().remove(r._tr)   # drop the blank template rows
for i,(action,expected) in enumerate(STEPS, 1):
    nt = copy.deepcopy(row_tmpl); t7._tbl.append(nt); row = t7.rows[-1]
    setc(row.cells[0], str(i)); setc(row.cells[1], action); setc(row.cells[2], expected)
    setc(row.cells[3], ''); setc(row.cells[4], '')

# GLOBAL: force every coloured run to black (see §5) ; then doc.save(OUT)
```

- **Clone a bordered data row** (`t7.rows[1]`) for each new step — `table.add_row()` can drop the per-cell borders;
  a deep-copied `<w:tr>` keeps them.
- Output to the record's `UT Scripts/` folder as `SMPL_<XStep name> Unit Test Script.docx`.

---

## 4. Designing the steps from the functional spec

Walk the spec's **XStep Layout Design** + **Validation Checks** + **Configuration** and turn each behaviour into
steps. The canonical AZ flow (all three examples follow it):

1. **Create and release a Process Order** containing the XStep (pre-configured master recipe). → PO created/released.
2. **Open the EBR** for the order / control recipe and **navigate to the XStep**. → EBR opens without error, XStep visible.
3. **Verify `IV_HEADER` / `IV_INSTR`** (and any `IV_LABEL*` / `IV_TAB_TIT*` / `IV_TITLE*`) display as authored in MBR.
4. **Exercise every control**, positive **and** negative, in layout order:
   - **Input + validation** → do the *negative* first the way the examples do (`enter a Part No. that does not exist`
     → *error popup* → `Discard popup`), then the *positive* (`enter one that exists`). Same for batch-not-for-material,
     expired batch, bad date format, non-numeric.
   - **Populated output** (Description, Exp. Date, computed result) → verify it auto-fills read-only; for a calc,
     **compare against an independently calculated expected value**.
   - **Gate dropdown** → test **both ways**: set No (section deactivates) then Yes (section activates). State the
     mechanism (`TABLE.ACTIVATE`/`DEACTIVATE` on `LV_DROP`) in the Expected Result.
   - **Get-equipment / Get-date buttons** → the assigned equipment / date-time is retrieved and stamped.
   - **Add Row** → a new row is added and auto-numbered; **Deactivate/remove line** if the block supports it.
5. **Goods issue** → after signing a consumed line, **navigate to CO54** and confirm the `Z_PICONS` process message
   exists with the right material / batch / quantity / movement type (261).
6. **Signatures** → try an *incorrect* username/password (rejected), then the valid Performed By (per row) and the
   step-level Witness / Recorded By; confirm the step **cannot complete** without the mandatory signatures.
7. **Re-open the completed XStep** → recorded values, outputs, stamps and signatures are retained.

Keep each Action terse and imperative and each Expected Result checkable (name the driving FM / command / message
where it clarifies, as the spec does). Granularity: match the sibling example — EFS Exhaust Filter (a gated
filter-info table like most of ours) runs ~30 steps; a single-table step runs ~8-12.

---

## 5. Formatting & fill rules

- **No blue text anywhere.** The template's instructional placeholders are blue; any run you add inherits that blue
  from the paragraph mark. Two defences: (a) set `run.font.color.rgb = BLACK` on every run you write; (b) a **global
  pass** before save that blacks out every remaining coloured run —
  `for col in doc.element.body.iter(qn('w:color')): col.set(qn('w:val'),'000000')` (also drop any `themeColor`/
  `themeTint`/`themeShade` so `val` wins). Verify: the only run colour left in `document.xml` is `000000`.
- **Fill the whole top section** (design-time): **Document Approval** author (Name & Role + Date), **Version Control**
  `1.0 / <date> / Initial Document / <author>`, **Referenced Documents** (the functional spec + version, the
  Manufacturing Directions, the DE1 100 SiMPL library, the mock-up), **Test Script header** (`Test Script ID &
  Version # = "<XStep name> V1.0"`, `Test Phase = "Unit Test"`, Test Name, Objective, Requirements Tested),
  **Pre-requisites / Set-Up / Data Requirements**, and **System / Environment** (e.g. `DE1 V1` / `DE1`).
- **Leave execution-time fields blank**: Actual Result, Pass/Fail column, Tester Name, Date Test Commenced, Run #,
  the "all pre-requisites satisfied?" Yes/No, and the Summary Result table.
- **Conventions from the examples**: dates as **DDMONYYYY** (e.g. `23JUL2026`); Test Phase = **Unit Test**; Test
  Script ID = **`<XStep name> V1.0`**; the author is whoever builds it.

---

## 6. Verification checklist (run after every build)

- [ ] Document **opens** and `word/document.xml` **parses** as XML.
- [ ] **No non-black run colour** anywhere (`grep` distinct `w:color w:val` = `{000000}` only).
- [ ] Top section fully filled (Approval author+date, Version 1.0/Initial, Referenced Docs, Test header ID/Phase/
      Name/Objective/Requirements, System/Environment); execution-time fields left blank.
- [ ] Step table = header + N numbered steps, **sequential**, each with an Action and an Expected Result; Actual/
      Pass-Fail blank.
- [ ] Steps cover: create/open/navigate, header display, **every control positive + negative**, each **gate both
      ways**, Add Row, goods-issue **CO54** check, mandatory-signature block, re-open persistence.
- [ ] All template tables (approval, version, refs, disclaimer, header, pre-reqs, system, steps, summary) still present.

---

## 7. Gotchas

- **Blue text** — the single most common defect (see §5). Always run the global black-out pass and verify.
- **Cloned-row borders** — clone an existing bordered `<w:tr>`; `add_row()` may produce borderless rows.
- **Merged header cells** — write the first cell of the merge; `.text` on a later cell of the same `<w:tc>` is a no-op.
- **Table indices shift** if the template is re-versioned — detect a table by its header text (row 0 / first cell)
  rather than trusting a hard index, or re-dump the template before building.
- **Don't invent execution data** — pre-requisites/data-requirements describe *what the tester must have* (a valid PO,
  test materials, an expired batch for the negative test, an assigned scale); they are not filled-in results.

---

## 8. Worked example — VI Treatment Vessel Setup (`build_tvs_ut.py`)

Gated composite (the EFS Exhaust Filter archetype). 25 steps: create/open/navigate → header → the four gate dropdowns
(Use-Affinity deactivates the whole step; Bag Required No→deactivate / Yes→activate via `TABLE.ACTIVATE`/`DEACTIVATE`
on `LV_DROP`) → Bag / Vent Filter / Product Filter lines (Part→Description, Batch→Exp. Date, autoclave date validation
incl. invalid-month + "N/A", per-row Performed By) → Tank section (IDs + `Get Pressure Date/Time` stamp) → Get Scale/
Balance → tare weight → filters-attached dropdowns → Add Row auto-index → expired-batch + missing-signature negatives
→ Recorded By signature → **CO54** `Z_PICONS` check → re-open persistence. Top section filled; all text black.
Referenced docs: the `SMPL_VI Treatment Vessel Setup XStep Design Specification` (v1.0), VI MPR (PN 8012441), the DE1
100 library, and the EBR mock-up.
