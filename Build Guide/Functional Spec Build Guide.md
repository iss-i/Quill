# Functional Spec Build Guide — From Mock-up to XStep Design Specification

A practical, repeatable method for turning an XStep **mock-up** (or a batch-record section) into a complete
**XStep Design Specification** (`.docx`) in the standardized template — including the two technical sections
(**Function Module(s)** and **Pseudocode**) that the client documents almost always lack.

Companion to *Batch Record to XStep Mockups - Build Guide.md* (that guide gets you to the mock-up; this one
gets you from the mock-up to the signed-off design spec). Captured from the AZ Phase 1/Phase 2 and Merck 2000L
SUB engagements.

**Downstream:** the finished spec + mock-up feed the **SapFractal XStep builder** (`XSTEP_BUILD_GUIDE.md` +
`XSTEP_TOOLS.md`), which constructs the real SAP XStep in cmxsvn (clone AZ template → add params → typed table
columns → wire FMs / process messages / signatures → `xs_check_semantic` → Simulate). Write the spec so it drops
straight into that build — the FM names, bindings, dropdown characteristics and labels you document are wired
verbatim. See the ⭐ convention table in §5. The mock-up is **also** published to the **PI Sheet Sandbox** (a
JSON PI-sheet — see the Mockups Build Guide §13); the spec's field roles map 1:1 to its element/column types
(**entry → `input`, computed → `output`, dropdown → `dropdown`, FM button → `function`**), so the roles you
assign each field carry all the way through.

---

## 1. What the spec is (and the two build modes)

Each XStep gets one **XStep Design Specification** — a Word doc uploaded to **Google Docs** for review, so
headings, the Table of Contents, and table styling must survive that round-trip. Every spec has the **same 13
sections in the same order** (see §2).

There are two ways you'll ever build one:

| Mode | When | What you author |
|---|---|---|
| **Augment** | The client provided a spec that already has the functional sections but is **missing Function Module(s) + Pseudocode** (the AZ Phase 1/2 case) | Author only those two sections and insert them in the right place; leave everything else intact. |
| **From scratch** | Only a **mock-up** exists (the Merck case) — no client doc | Clone a good donor spec for the *shell* (title page, styles, live TOC), delete the body from `Purpose` onward, and rebuild all 13 sections. |

Both modes reuse the **same emitters** for the FM/Pseudocode content, so the technical sections come out
byte-consistent regardless of mode.

---

## 2. The template — 13 sections, fixed order

```
1  Purpose
2  Overview
3  Reasons for developing
4  Authorization
5  Assumptions/ Dependencies
6  Validation Checks
7  XStep Layout Design
8  Function Module(s)        ← technical
9  Pseudocode                ← technical
10 Configuration Specification(s)
11 Test Scenarios
12 Document References
13 Revision History
```

**The golden rule of placement:** *Function Module(s)* + *Pseudocode* go **right after "XStep Layout Design"
and immediately BEFORE "Configuration Specification(s)"** — never before Test Scenarios.

**Per-doc variation — detect, don't assume.** Client docs are individually authored and differ:
- Some have **no** "XStep Layout Design" heading (e.g. calibration/probe/harvest-calc docs) → the technical
  sections sit right after *Validation Checks*, still immediately before Config Spec.
- Some spell it **"Configuration Specification"** (singular), some **"Configuration Specifications"** (plural).
- Some are missing the "Assumptions/ Dependencies" and/or "Configuration Specifications" headings entirely
  (e.g. Yield Calculations) → **flag it, don't fabricate** the missing sections; anchor the insert to
  "Test Scenarios" instead.
- Heading numbering (`numId`) and heading level (Heading 1 vs Heading 2) vary per doc → the build **clones the
  existing "Configuration Specification(s)" heading's `pPr`** so new headings auto-adopt the right numbering.

---

## 3. The toolchain (`_scratch/`)

Everything runs on **python-docx** with a small, persistent toolkit in the repo `_scratch/` folder:

| File | Role |
|---|---|
| `p2lib.py` | `extract_sections(docx)` → `{fm_name: {fm:[elements], pseudo:[elements]}}`, splitting the FM/Pseudocode sections on the bold `Function: <name>` paragraphs. Plus `is_heading`, `heading_text`, `ptext`, `pstyle`. |
| `build_phase2.py` (imported as `B`) | The engine. Holds the cloned table/label/bullet **templates**, the FM/Pseudocode **emitters** (`lib_fm_elems`, `lib_pseudo_elems`), the heading+bookmark cloner, and all the doc-wide fixes (TOC, pgNumType, empty-headings, header shading, updateFields). |
| `fmdata.py` | `FMDATA` = hand-authored FM dicts (interface + pseudocode) for **new/custom** FMs that aren't transplantable from an existing golden doc. |
| `build_<key>.py` | One per doc (or a batch driver). Defines the content and the FM order, then drives `B`. `build_fvc.py` / `build_crt.py` / `build_do.py` are the from-scratch Merck exemplars. |

### The FM library — three sources, reuse-first

`B.lib_fm_elems(name)` / `B.lib_pseudo_elems(name)` resolve an FM in priority order:

1. **GOLDEN** = *Additional pH Monitoring* — signature/activation/validation FMs
   (`SIG_ADD_DB_CB`, `SIG_POPULATE_CB`, `SIG_VALIDATION`, `VALI_SUPE_SIG`, `INITIAL_ACTIVE`,
   `MBR_DEP_ADD_PERFORM`, `MBR_DEP_CHECK_ACTIVE`, `COND_AVG`, `RANGE_CLASSIFY`, `ENTRY_VALIDATION1`).
2. **BIOSAMP** = *Bioreactor Sampling* — the daily-sampling archetype set
   (`GET_ASSIGNED_EQUI_EBR`, `ELB_FM_GET_ASS_EQ_VALID`, `STORE_DAILY_SAMPLE`, `OPS`, `CALC_EXECUTE`,
   `MIN_MAX`, `GET_DATE_TIME`, + the sig/activation FMs).
3. **FMDATA** = authored dicts (`CUSTOM_INDEX`, `CALC_VALIDATE`, `INPUT_VALUE`, `OUTPUT_VALUE`,
   `SET_LINE_IDX`, `CHECK_CHAR_DATE`, `VALIDATE_FLOW`, `GET_FLASKS`, …).

**Transplanted** (1 & 2) come out as raw deep-copied XML from an accepted Google-origin doc → they already
match the accepted style exactly. **Authored** (3) are built from `FMDATA` via templates cloned from the
golden doc → same look.

**Adding an FM the library doesn't have yet:** either add it to `fmdata.py`, or inject it at runtime from the
build script (no need to edit the big file):
```python
B.FMDATA['ZSMPL_FM_CHECK_CHAR_DATE'] = { 'name': ..., 'imports': [...], 'exceptions': [...], 'pseudo': [...] }
```
`imports/exports/changing` = list of `(NAME, TYPE, 'Short text')`; `exceptions` = list of `(NAME, 'Short text')`;
`pseudo` = list of `(kind, text)` where `kind='b'` renders a bullet and anything else renders a plain line.

### The from-scratch build shape (the `build_fvc/crt/do.py` pattern)

```python
import build_phase2 as B
from p2lib import is_heading, heading_text

DONOR = '.../Three Variable Calc .../....docx'   # proven-good shell (clean title canvas, live TOC)
shutil.copy(DONOR, OUT)
doc = Document(OUT); body = doc.element.body
# find sectPr + the 'Purpose' heading; snapshot a deep copy of it as the heading template ('anchor')
# delete every element from 'Purpose' up to (not incl.) sectPr → empty body, front matter + TOC kept
# helpers: H(text)=cloned heading, P/Bul/BL=plain/bullet/blank, T3/T2=3-/2-col tables
# ... author all 13 sections ...
for fm in FM_ORDER:
    for el in B.lib_fm_elems(fm): add(el)      # under 'Function Module(s)'
for fm in FM_ORDER:
    for el in B.lib_pseudo_elems(fm): add(el)  # under 'Pseudocode'
B.neutralise_empty_headings(body); B.set_update_fields(doc); doc.save(OUT)
# finally: raw-zip text-replace the donor XStep name in word/{document,header*,footer*}.xml
```

Donor tip: reuse a **known-clean title canvas** (13 `txbxContent` / 78 `wps:` shapes). *Three Variable Calc*
is the proven donor for the Merck from-scratch builds. The FM/Pseudocode content is independent of the donor,
so any accepted Phase-2 doc works as a shell.

---

## 4. Sourcing function modules from SAP (DE1 100)

**All FMs live in DE1 100** (MCP connection `DE1_100`). Resolve by name prefix:

- **`/SMPL/…`** → DE1 100. `find_objects` (query without the namespace slashes, e.g. `CHECK_CHAR_DATE`) →
  `get_source` on the returned ADT URI. The signature comment block gives the interface; the body drives the
  pseudocode.
- **`ZSMPL…`** (custom Z) → also in DE1 100; a local `Function Modules/` folder holds many as `.abap` files
  (filenames replace `/` with `_`). Prefer the local folder, fall back to `DE1_100`.
- **Naming traps are real:** `GET_EXPIRY` ≠ `GET_EXPIRY_DATE` ≠ `GET_EXP_DATE`; the real object may be
  `ZSMPL_FM_CHECK_CHAR_DATE`, **not** `/SMPL/PPPI_FM_CHECK_CHAR_DATE`. **Always confirm the exact object** the
  XStep calls before documenting it.

### Which FMs an XStep actually calls

If the XStep exists in SAP: `shaper_get_version` (shape=`snapshot`) on the item, then grep the snapshot for
`PPPI_FUNCTION_NAME` (buttons / event handlers / main FM) **and** `PPPI_VALIDATION_FUNCTION` (column /
signature **validators**). Capture **both** — validators are real FMs. If it's a mock-up only (no XStep yet),
you're *designing* the FM set — pick it from the archetype (§5) and the mock-up's controls.

> **Tool rename + case gotcha:** the XStep MCP tool group was renamed **`xs_*` → `shaper_*`** in an SapFractal
> build (`shaper_find`, `shaper_get_version`, `shaper_folder_tree`, `shaper_search_instructions`, …). If a call
> errors *"Tool xs_find not found"* while `list_connections` works, git-pull SapFractal and use the `shaper_*`
> names. On DE1 100, `shaper_find` case-insensitive search fails with *"The function UPPER is unknown"* — pass
> **`case_sensitive: true`** with exact-case terms. Use `shaper_find` to **confirm a reuse-target XStep exists**
> before a functional spec references it as the base.

**Read the ACTIVE (Released) version.** `xs_get_version` resolves the active version via the picker — Released
status wins, else the highest 4-digit `VERS_NAME`. The active version is **not always the highest-numbered**
(a live item's active version was `0001`, with `0002`/`0003` as later drafts). If an item has **no** Released
version and non-numeric names the picker is **ambiguous** — pass an explicit `version_id` and confirm which one
is live. Document the FMs and parameters from the version that's actually released, not whichever sorts last.

### The scoping rule (what to document)

- Document an FM **only if it's used in a MAIN step**. FMs used only inside the embedded **Conditional
  Header** or **Optional Signature** reference sub-steps are reference-only → **do not document**.
- Document **validators**, not just function buttons.
- **Exclude standard SAP FMs** (`GET_SYSTEM_TIME_REMOTE`, `CMX_TOOLS_FM_*`, `COPF_CALL_TRANSACTION`, …).
- Reuse the **exact wording** of an FM already documented in a sibling spec, for consistency.

---

## 5. Design the FM set from the mock-up (archetype → FMs)

Pattern-match the mock-up to an archetype, then take that archetype's characteristic FMs (from the Mockups
Build Guide §9 catalog). The recurring building blocks:

| Control on the mock-up | FM(s) |
|---|---|
| **▶ Record / ▶Start / ▶End button** stamping a date/time | `/SMPL/PPPI_FM_GET_DATE_TIME`, or a timer family (`STR_PROC_STRT_TM` / `GET_PROC_TM` / `CLEAR_PROC_TM`). Stamps a **default variable** (`LV_*_D`/`LV_*_T`) wired as the field's **Default Value** (`PPPI_DEFAULT_VARIABLE`); the field captures into a separate `LV_DATE`/`LV_TIME` and stays **editable** — the `Performed By` signature is the GxP control, not read-only. |
| **Numeric field with a range** `(min–max)` | `/SMPL/PPPI_FM_MIN_MAX` (or a tolerance validator) |
| **Date field** (expiry, calibration due) | `ZSMPL_FM_CHECK_CHAR_DATE` (format yyyy.mm.dd / "N/A" / not-in-past) |
| **Equipment / probe / vessel** with lot + expiry | `GET_ASSIGNED_EQUI_EBR` + `ELB_FM_GET_ASS_EQ_VALID` |
| **A = B − C** style calc, single record | simplest first: `ZSMPL_FM_BASIC_CALCULATIONS`, or `CALC_EXECUTE` / the CALC_VALIDATE→INPUT/OUTPUT chain |
| **Component / material table** with a **SAP** column | `GET_MAT_ITEMS` / BOM reader + `VALIDATE_QUANTITY` + a goods-issue **process message** |
| **Repeating table (+ Add Row)** | a row-indexer: `ZSMPL_FM_CUSTOM_INDEX` or `/SMPL/PPPI_FM_SET_LINE_IDX` (this drives the mock-up's standard leftmost `#` index column) |
| **Performed By** signature (one per row) | `SIG_ADD_DB_CB` (+ `SIG_VALIDATION`), often with `MBR_DEP_ADD_PERFORM` |
| **Witness By / Check By** footer signature | `VALI_SUPE_SIG` |
| **Conditional "if X, proceed / N/A the rest"** | `INITIAL_ACTIVE` + `MBR_DEP_CHECK_ACTIVE` (on nearly every step) |
| **Gated sub-section** (a `… Required?` Yes/No dropdown that activates/deactivates a block — composite XSteps) | **Not an FM — setup Commands with Formula triggers** (confirmed on live `SMPL: EFS Additional Staging`). The dropdown is a CT04 char (`ZSMPL_CHAR_YES_NO`) → local `LV_DROP`; the block carries `TABLE.ACTIVATE`/`TABLE.DEACTIVATE` (and grouping-level `PROC_INSTR.ACTIVATE`/`DEACTIVATE`, `LOCK`/`UNLOCK`), each with a Formula trigger on the gate value — DEACTIVATE = `(LV_ACTIVE<>1 AND IV_ACT_FLP<>1) OR (LV_ACTIVE=1 AND IV_ACT_FLP=1) OR (LV_DROP=2)`, ACTIVATE = complement (`LV_DROP=2`⇒No⇒deactivate). Document these Commands + the trigger formula in **Configuration**, one gate per conditional block. `INITIAL_ACTIVE` is present but only sets the base initial-active state — it is **not** the gate. |
| **Consumed material** (paper "SAP Consumption Performed by/Date"; per-line on a table) | **Goods Issue process message `Z_PICONS`, movement type 261** — automatic, not a manual field. Fires per row on the line's `Performed By` |
| **"Label the vessel/sample …" (SOP-0107056)** | a **label-print control function / process message to the label printer** *(confirm with client — may instead be applied-and-recorded manually, i.e. instruction-only)* |

Signature plumbing **varies per doc** — mirror the closest accepted sibling. E.g. *Harvest Log* uses
`SIG_ADD_DB_CB` + `VALI_SUPE_SIG` + `MBR_DEP_ADD_PERFORM`; *Bioreactor Sampling* uses the sig callbacks
without `MBR_DEP_ADD_PERFORM`. Pick the sibling that matches the mock-up's signature layout.

### ⭐ The most important lesson — validate that the FM's interface FITS

**A name match — or an archetype match — is a candidate, not a fit.** Before you reuse an FM, open its real
interface (`get_source`) and check its parameters against the step's actual columns.

> **Worked example (Daily Observations).** The archetype ("daily sampling") points at
> `ZSMPL_FM_STORE_DAILY_SAMPLE`. But its interface is **fixed** to Seed/Production parameters —
> `IV_GLUCOSE / IV_BRX_WT / IV_VCD / IV_VIAB` — and the **viral** Daily Observations step records Temperature,
> RPM, pH, DO, O₂, **CPE %**, and live/dead cell counts. The FM does **not** fit. The right call was to
> **exclude it**, document the FMs that do fit (`OPS` for probe-vs-external pH, `MIN_MAX`, `GET_DATE_TIME`,
> equipment + signature FMs), and **flag** that persisting the viral parameters would need a new store FM.
> Documenting the mis-fit FM would have put glucose/VCD parameters in a viral-observations spec.

**Prefer the simplest existing FM** (a single subtraction is `BASIC_CALCULATIONS`, not the full calc chain).
**"Use an existing DE1 100 FM first; author a new one only when nothing fits"** — and when nothing fits, say
so explicitly in the spec rather than forcing a bad match.

### ⭐ Canonical FM / domain conventions (validated against the SAP XStep builder)

The spec you write is the **input to the SapFractal XStep builder** (`Build Guide/XSTEP_BUILD_GUIDE.md` +
`XSTEP_TOOLS.md`), which wires exactly the FMs and bindings you document. Its convention tables confirm the FM
set we've been using — pick from these first (they're what the builder expects):

| Control on the mock-up | FM / domain the builder wires |
|---|---|
| Part No. → Material Description | `ZSMPL_FM_GET_MAT_DETAIL`, `validated_value_param: IM_MATNR` (out `EX_MAT_DESC`) |
| Batch No. → Exp. Date | `ZSMPL_FM_GET_EXPIRY_DATE`, validates `IM_BATCH` **and requires `IM_MATNR`** (out `EX_EXP_DATE`, date) |
| Goods issue / SAP consumption | process message **`Z_PICONS`** (underscore) + `ZSMPL_CHAR_MOVEMENT_TYPE = 261` (order consumption) |
| ▶ Record date/time | `/SMPL/PPPI_FM_GET_DATE_TIME` — outputs **`EV_DATE_DEFAULT`** / `EV_TIME` into a **default variable** (`LV_*_D`/`LV_*_T`) set as the field's `PPPI_DEFAULT_VARIABLE`; the field itself captures `LV_DATE`/`LV_TIME` and stays **editable** (operator may correct it — the `Performed By` signature is the control) |
| Per-row Performed By | `/SMPL/PPPI_FM_SIG_ADD_DB_CB`, strategy `SAPPOCSS`; validator `/SMPL/PPPI_FM_VALI_SUPE_SIG` |
| Get Equipment / scale / probe | `/SMPL/ELB_FM_GET_ASSIGNED_EQUI`, **EQTYP** `B`=scales/balances, `M`=welders/sealers, `Q`=testers |
| Leftmost `#` row index | `ZSMPL_FM_CUSTOM_INDEX` / `/SMPL/PPPI_FM_SET_LINE_IDX`, domain **`ZSMPL_CHAR_GI_INITIALS`** default `"1"` |
| Numeric quantity column | domain `PPPI_MATERIAL_QUANTITY` |
| Offline-meter results (pH / conductivity / temperature, with accept ranges) | **Get Equipment** `/SMPL/ELB_FM_GET_ASSIGNED_EQUI` (offline meter, EQTYP `Q`) + per-measurement range validation `/SMPL/PPPI_FM_MIN_MAX` or `ZSMPL_FM_CALC_TOLERANCE`. A generic tolerance/min-max FM may expose **more targets than the step uses** (e.g. CALC_TOLERANCE takes 3; a 2-measurement step feeds 2) — that's fine, document only the fed ones. |

**The AZ template already provides the header + both signatures.** The builder clones `SMPL: AZ Template XStep`,
which ships a **Conditional Header** (title + instruction block) and an **Optional Signature** block (**Performed
By** + **Witnessed By**). So the header/instructions and the Verified/Witnessed-By footer are **template-supplied**
— the builder just "adds the spec-specific instructions, usually one table." Keep documenting the activation /
signature FMs (they're what the step *uses*), but know they come from the template, not custom wiring.

**Dropdowns are real and each needs a CT04 characteristic.** In this client's workflow a spec/mock-up dropdown
**always** becomes a real dropdown, and every dropdown requires a **`ZSMPL_CHAR_*` CT04 characteristic** (CABN +
allowed values). Treat each dropdown column as *two* deliverables — see §6 (name the characteristic + its values
in Configuration Specification and Assumptions).

**The builder can author new Z FMs** (`xs_create_function_module` in FUGR `ZAI_XSTEP_FMG`). So a spec that flags
genuine new development (§5 ⭐) is buildable — reuse-first just keeps it simpler.

**All `IV_*` params are spec-worthy — document the full MBR-authorable input set.** The `IV_*` parameters are
the step's MBR/recipe-authorable interface, so **document every one of them**, including the standard template
inputs `IV_ACTIVE`, `IV_ACT_FLP`, `IV_HEADER`, `IV_INSTR`, `IV_PL_TXT`, `IV_PRINT`, `IV_SIGN` (and `IV_TITLE1`).
It's still worth **noting which are template-supplied** — inherited from the AZ template, so the builder does
**not** re-create them (XSTEP_BUILD_GUIDE §7.10) — versus **new step-specific** `IV_*` (a target amount, a
min/max bound, a recipe-driven label/flag) that the builder adds with the two-level scope it expects: an
**outer T-root** declaration (`PMODE='F'`, default value) **and** an **inner main-step reference** (`PMODE='R'`).
Call out that pairing for each new IV so the builder wires it correctly.

**A validated limit/rule is a PARAMETER on the existing step — not a new XStep or extra columns.** An acceptance
**range (min/max)** on a numeric value is the `IV_MIN` / `IV_MAX` parameters of the existing `SMPL: Record Numeric
Value` + its built-in `/SMPL/PPPI_FM_MIN_MAX` validator (verified in DE1 100 — `IV_MIN` "Minimum Range" / `IV_MAX`
"Maximum Range", blank until the recipe sets them). So a range-checked value **is documented as the existing
`Record Numeric Value` with `IV_MIN`/`IV_MAX` populated + the `MIN_MAX` validator** — do **not** spec a new/variant
object, separate min/target/max steps, or an in/out-of-range **decision dropdown** (the validator's error handling
is the branch). Same for other built-in validators (`YES_NO_VALID`, `CHECK_CHAR_DATE`, `PPPI_FM_VALI_MAT`) and the
per-row `Performed By` (`SIG_ADD_DB_CB` fires per completing row). The Mockups Build Guide §11 carries the
**verified FM catalogue** (block → validation FM / event FM / parameters) confirmed against the live library —
mirror it when documenting the FM set, and keep the spec scoped to the one XStep as built in CMXSV.

**"Authored in MBR" is a claim to VERIFY, not to trust.** Client specs routinely say a target / tolerance / UoM
is "authored in SiMPL MBR" when the live XStep actually **hardcodes** it — e.g. a tolerance baked into an FM
call (`ZSMPL_FM_CALC_TOLERANCE`, `IM_PERCENT = 5`) or a UoM held as a fixed local param (`LT_UOM = KG`), neither
of which the recipe overlays. The real per-recipe values (e.g. `IV_TAR_A = 3.15`, `IV_TAR_B = 51.975`) live on
the **T-root `IV_*` parameters / the recipe**, not in the spec. When documenting Configuration, run
`xs_list_parameters` on the live XStep and distinguish **true `IV_*` (recipe-overlaid)** from **hardcoded**
values — and **flag any spec claim that doesn't match what the XStep actually does** (a spec that says
"tolerance authored in MBR" when it's a hardcoded `IM_PERCENT` is a real defect worth surfacing).

**Capture results as typed, machine-readable characteristics — it's *why* the domain choice matters.** Every
recorded value carries a real domain, never free text: quantities → `PPPI_MATERIAL_QUANTITY`; Yes/No / pass-fail /
disposition → a **CT04 characteristic** (`ZSMPL_CHAR_*`, e.g. Yes/No or pass-fail); dates → a date domain; UoM →
`PPPI_UNIT_OF_MEASURE`. Our developers already do this at the XStep build level — the point for spec-authoring is
that **the reason is downstream**: these values flow to the SAP **Batch Release Hub** release checks (Batch Record
Review, deviation, usage decision, serialization), to the process order's **inspection lot / usage decision**, and
to **batch classification characteristics**, all of which auto-evaluate only if the value is *typed data, not
prose*. So when you assign a field's domain in the spec, pick the type that lets the value be read as data. **This
is background knowledge for choosing the domain — do NOT write the downstream batch-release contract into each
XStep spec.** The spec stays scoped to the individual XStep as built in CMXSV (its FMs, params, columns,
validations, signatures, process messages, layout).

---

## 6. Writing the sections (content guide)

- **Purpose** — one paragraph: what the XStep does and what it captures.
- **Overview** — how it renders and behaves: the controls, what's stamped vs entered vs computed, validation,
  signatures. End with *"All function modules used by this XStep already exist in DE1 100; no new development
  is required."* (or the honest exception — see the Daily Observations note above).
- **Reasons for developing** — why it replaces the paper step (removes transcription/arithmetic error, enforces
  validation, electronic signature trail, one reusable block vs a table reprinted per occurrence).
- **Authorization** — standard SiMPL EBR security model + PFCG role + SAP digital signature.
- **Assumptions/ Dependencies** — bullets: the FMs exist/active; master-data prerequisites; units; ranges;
  any out-of-scope item flagged. **For every dropdown column, list the required CT04 characteristic**
  (`ZSMPL_CHAR_*`) and its allowed values as a prerequisite — it's a build deliverable (create it if it doesn't
  exist). E.g. WFI Container Setup assumes `ZSMPL_CHAR_WFI_ITEM` = { Bag, Filter }.
- **Validation Checks** — 3-col table (Field / Validation / Function Module). **Name an FM only where it truly
  drives that check.** (Don't repeat a signature-validation FM on every range row — describe the behavior in
  words and cite the range FM only. The FM's proper home is the field it actually validates + its own
  FM/Pseudocode section.)
- **XStep Layout Design** — the instruction text (quote the mock-up) + a bullet per field with its role
  (entry / read-only stamped / computed / signature). Note **Add Row** and the footer signature.
  **End the section by embedding the mock-up image** (`image.png` from the XStep's mock-up folder), centred,
  ~6.5″ wide. Add the image **on its own — no caption/intro line** (per client preference, keep just the
  image). Developers use it as the **look-and-feel reference**, so every spec must carry it. (Helper in the
  build script:
  `IMG(path)` → `doc.add_paragraph()` + `add_run().add_picture(path, width=Inches(6.5))`, centre-aligned, then
  detach `para._p` and insert it via the normal `add()` so it lands right before the *Function Module(s)*
  heading. The image survives the later raw-zip title rename, which preserves every package entry.)
- **Function Module(s)** — intro line, then the emitted interface blocks (see §7).
- **Pseudocode** — the emitted pseudocode blocks (see §7).
- **Configuration Specification(s)** — 3-col table (Parameter / Value / Description): header text, instruction,
  each button/field/validator, ranges/setpoints, Add Row. **Give each dropdown column a row naming its CT04
  characteristic** (`ZSMPL_CHAR_*`) and allowed values (e.g. `Item | Dropdown (CT04) | ZSMPL_CHAR_WFI_ITEM =
  Bag / Filter`). Keep column **labels ≤ ~30 chars** (they become `PPPI_INPUT_REQUEST`, which caps there) and
  remember backing **variable names cap at 10 chars** — favour terse labels; the long description lives in the
  instruction, not the header. **Document all `IV_*` params** — they're the MBR-authorable interface (§5); mark
  which are template-supplied vs new step-specific, and give each new one its outer-`F` / inner-`R` two-level pairing.
- **Test Scenarios** — 3-col (# / Scenario / Expected Result): a happy path per control, each validation
  failure (with the exception name), Add Row, the mandatory-signature block, and re-open persistence.
- **Document References** — the Manufacturing Directions, the SiMPL library, and the reference archetype spec.
- **Revision History** — 3-col; **1.0 / Initial document / <date>**. Initial versions are **not** sent to the
  client → do **not** bump the revision on later edits to an unreleased doc.

---

## 7. Formatting & style (Google-Docs-safe)

Docs use **Google-Docs-origin styles**: `normal` (lowercase) + `Heading 1/2`; **no** `List Paragraph` style.

- **FM section labels** — `Function: X`, `Import Parameters:`, `Export Parameters:`, `Changing Parameters:`,
  `Exceptions:` are `normal` style, **bold** run.
- **Parameter tables** — 3 columns (*Parameter Name / Associated Type / Short Text*); header row shaded
  `CCCCCC` + **bold**; **single black borders** `sz=8` all sides incl. `insideH/insideV`. (The chosen reference
  is *Room/Equipment Assign V1.3* — its FM tables are bordered. Do **not** copy borderless-table docs.)
- **Exception tables** — 2 columns (*Exception / Short Text*), same header style.
- **Pseudocode** — plain `normal` (not bold): numbered sections (`1. Purpose`, `2. Input Parameters`,
  `3. Processing Logic`), lettered sub-steps (`a.`/`b.`), bullets, then trailing **Additional Notes /
  Error Handling: / Dependencies: / Assumptions:**. Bullets render as a literal `•  ` prefix in a `normal`
  paragraph (indent ~360) so they're portable (no `numId` dependency).

---

## 8. Doc-wide fixes (apply to EVERY build — `build_phase2.py` does these)

These all exist because the doc is round-tripped through Google Docs:

1. **Live TOC** — the client docs ship a *static* Google TOC (baked page numbers in a `w:sdt`). Replace the
   `sdtContent` with a live Word field `TOC \h \u \z \t "Heading 1,1,…,Heading 6,6"` (`fldChar dirty=true`).
   (`fix_toc`) On a from-scratch build the donor already has the live field — just keep it.
2. **`updateFields`** — add `<w:updateFields w:val="true"/>` to `settings.xml` so Word/Google rebuilds the TOC
   on open. (`set_update_fields`)
3. **Neutralise empty headings** — strip `pStyle`+`numPr` from blank `Heading` paragraphs, else they show as
   empty TOC lines. (`neutralise_empty_headings`)
4. **Remove `pgNumType`** — delete `<w:pgNumType w:start="1"/>` from every `sectPr`, else the TOC's trailing
   sections show page "1" in Google Docs. (`remove_pgnumtype`)
5. **Strip header `w:shd`** — some docs have a pale-blue shading behind the logo that renders as an ugly band;
   remove it. (`strip_header_shd`)
6. **Heading bookmarks** — every new heading needs a unique `_heading=h.<hash>` bookmark wrapping it, or its
   TOC entry links to an empty anchor (jumps to top). The heading cloner adds this. (`make_heading_like`)

---

## 9. Gotchas (learned the hard way)

- **Ampersand in the XStep name.** The raw-zip title/header/footer text-replace writes into XML — use the
  **escaped** form (`Cell Receipt &amp; Transfer`), or `document.xml` won't parse. In python-docx **body**
  content pass the literal `&` (python-docx escapes it for you). Verify with an XML parse after building.
- **`addprevious` inserts immediately before the anchor** → insert a list of elements with **forward**
  iteration (`for el in els: anchor.addprevious(el)`), not reversed, or the block comes out scrambled
  (Function line at the bottom). `addnext` is the opposite (use reversed).
- **Bullet-heading docs.** A few source docs define only bullet-format `numId`s, so section headings render as
  ● bullets in body + TOC. Detect via the heading `numId`'s `ilvl0 numFmt=bullet`; create a decimal numbering
  def and reassign every heading's `numPr` to it.
- **Grey borders.** One doc had `w:color="aaaaaa"` table borders (faded grid) → replace with `000000`.
- **Malformed title canvas.** Some docs have a title drawing-canvas with too few shapes → a visible gap.
  Transplant a good doc's `paragraph[0]` (deepcopy), remap the 2 title-image `r:embed` ids, swap the
  XStep-name `<w:t>`. Good canvas = 13 `txbxContent` / 78 `wps:` shapes.
- **Refreshing the TOC for real** (page numbers) needs MS Word via COM
  (`Word.Application` → `TablesOfContents.Update()`); python-docx can't repaginate. `set_update_fields` is
  usually enough (Word/Google rebuilds on open).
- **Attribute FMs precisely.** Don't repeat an FM name across many rows where it isn't the actual driver
  (e.g. a supervisor-signature FM cited on every range row). State the behavior in words; cite the FM once, at
  its real home. (Direct client feedback.)
- **Disk space.** The Windows box has run to **0 bytes free** mid-build; a `.docx` build needs ~2.5 MB of
  headroom (1.2 MB doc + a temp copy during the zip rewrite). Clear `%TEMP%` if a write fails with
  "No space left on device", and flag the full disk to the user.

---

## 10. Verification checklist (run after every build)

- [ ] All **13 headings** present, in order (or the doc's known variant).
- [ ] `Function:` line count = **2 × N** FMs (N under *Function Module(s)*, N under *Pseudocode*).
- [ ] `document.xml` **parses** as XML (catches ampersand/escaping bugs).
- [ ] **No donor-name leftovers** (`grep` the old XStep name across `word/*.xml` = 0).
- [ ] Every FM param/exception table is **populated** (no empty template rows).
- [ ] The **mock-up image** is embedded at the **end of XStep Layout Design** (one inline shape, before the
      *Function Module(s)* heading).
- [ ] TOC is a **live field** + `updateFields` set; no empty heading lines; no `pgNumType`.
- [ ] The FM set matches the mock-up's controls, each FM's **interface fits**, and any non-fit / new-dev item
      is **flagged**, not hidden.

---

## 11. Worked examples (Merck, from scratch)

- **Cell Receipt & Transfer** (`build_crt.py`) — Table archetype. ▶Record buttons stamp Date/Time Received +
  Transfer Time; Cell Tank # entry; Sterilization Exp. Date; Performed By column + Witness By footer; Add Row.
  **8 FMs, all in DE1 100:** `CUSTOM_INDEX`, `GET_DATE_TIME`, `CHECK_CHAR_DATE` (sourced from DE1 100 and
  injected via `B.FMDATA`), `SIG_ADD_DB_CB`, `VALI_SUPE_SIG`, `INITIAL_ACTIVE`, `MBR_DEP_ADD_PERFORM`,
  `MBR_DEP_CHECK_ACTIVE`. Title name contains `&` → escaped in the raw-XML rename.
- **Daily Observations** (`build_do.py`) — the **viral variant** of Bioreactor Sampling (adds CPE %, Cell
  Count Live/Dead, O₂). **11 FMs transplanted verbatim from the BIOSAMP library** (no new dev):
  `GET_ASSIGNED_EQUI_EBR`, `ELB_FM_GET_ASS_EQ_VALID`, `OPS`, `MIN_MAX`, `GET_DATE_TIME`, `SIG_ADD_DB_CB`,
  `SIG_POPULATE_CB`, `SIG_VALIDATION`, `VALI_SUPE_SIG`, `INITIAL_ACTIVE`, `MBR_DEP_CHECK_ACTIVE`.
  **Deliberately excluded** `STORE_DAILY_SAMPLE` (glucose/VCD interface doesn't fit the viral params — see the
  ⭐ lesson in §5) and `CALC_EXECUTE` (no computed column). The persistence gap was flagged to the user.

---

## 12. Quick procedure

1. Read the mock-up (+ the batch-record section it covers). Note the archetype, every field's role
   (entry / stamped / computed / signature), specs/ranges, and signatures.
2. Design the **FM set** from the controls (§5). For each candidate FM, `find_objects`→`get_source` in
   DE1 100 and **confirm the interface fits**. Reuse first; author only what's missing; flag non-fits.
3. Pick the **mode** (§1) and a **donor** (from-scratch) or the client doc (augment).
4. Write the build script: content for the 13 sections + `FM_ORDER`; emit FM/Pseudocode via `B.lib_*_elems`;
   inject any new FM via `B.FMDATA`.
5. Run the **doc-wide fixes** (§8) and the **rename** (from-scratch).
6. **Verify** (§10). Flag any assumption or new-development item to the user.
