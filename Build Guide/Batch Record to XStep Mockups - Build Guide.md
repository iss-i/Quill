# Build Guide — From Batch Record to Full XStep Mock-ups

A practical, repeatable method for turning a client's paper/Word/PDF batch record
(MABR / Manufacturing Directions) into a streamlined digital **EBR** built from reusable
**XStep** building blocks, and for producing the **mock-ups** and the assembled **EBR / PI
Sheet** used to review and compare "New vs Old".

Captured from the AZ Bioreactor (MABR-0027688) and Merck 2000L SUB engagements.

---

## 1. The big picture — what the transformation actually is

A paper batch record is a long, **repetitive**, sign-on-paper document. The same data-capture
patterns (sampling, additions, signatures, equipment selection, calculations, readings) repeat
dozens of times across phases.

The XStep approach:

1. **Decompose** the record into its recurring data-capture *patterns* — do **not** transcribe it page-by-page.
2. **Factor each pattern into ONE parameterized XStep "building block"** — with native e-signatures
   (replacing By/Check By columns), FM-backed calculations & range validation (replacing manual math
   and "(X.XX)" annotations), SAP master-data integration (equipment + calibration checks, materials,
   batches), and conditional branching.
3. **Store them as a library**, organized by scope: cross-process blocks + product/area-specific blocks.
   In SAP these are reusable **references** (cmxsvn `ref_indicator = "X"`).
4. **Reassemble** the batch record as a *tree of references* to those blocks (the master/control recipe →
   the operator-facing **PI Sheet**). Recurring blocks (e.g. Daily Sampling) are **instantiated many times**
   with different parameters instead of being copied as static pages.

**Payoff:** a 100+ page static record collapses into ~30–50 reusable, validated blocks + a recipe that
references them. Edit a block once → every occurrence updates. Calculations/ranges enforced by FMs.
Signatures and equipment/material data electronic and tied to SAP. The same library is reused across the
whole product family and future products.

---

## 2. The workflow (step by step)

### Step 1 — Read & understand the batch record
- Read the whole record. Capture the **section structure** (numbered/lettered steps) and the **attachments**
  (non-routine, event-driven actions).
- Note the **header/identification** block (product, batch #, order, USDA/license, plant).
- Note GxP context: every step has **By / Check By** (Performed/Witnessed) sign-offs.

### Step 2 — Identify the recurring patterns (the building blocks)
Look for the patterns that repeat. The common ones in any bioprocess record:
- **Signatures** (Performed By / Witnessed/Checked By) — on nearly every step.
- **Equipment / probe / vessel identification** with **calibration / sterilization expiry**.
- **Component / material addition tables** — Component, Manufacturer, Amount, Batch #, Exp Date,
  Amount Added, **SAP** (goods issue).
- **Calculations** — fill volume, MOI, weighted-average titer, BEI/neutralizer volumes, etc.
- **Daily sampling / observations** — the single biggest reuse win (one table reprinted per day, per phase).
- **Sample submission** to QC (retention/sterility/etc.).
- **pH adjustment / probe calibration**, **filter integrity**, **centrifuge/harvest**, **transfers**,
  **mixing**, **timers (start/stop)**, **labeling**, **cleaning/sanitization**, **dispense/storage**.

### Step 3 — Cross-check the existing XStep library (don't rebuild what exists)
- Search the **whole** XStep repository by concept, not just one folder
  (`xs_find` by keyword: e.g. *Inactivation, Neutral, Seed, Centrifug, Harvest, Sterili, Probe,
  Dispense, Transfer, Mixing, Component, Timer, Daily, pH Adjust*).
- **Check whether a client folder already exists** (e.g. a "Merck" folder may already be started).
- Use the **canonical library** (e.g. `Bioreactor`, `Solution Buffer`) for generic blocks —
  these are the clean reusable versions.
- **Match by name, then VALIDATE by opening the XStep** (`xs_get_version`) — a name match isn't a fit;
  e.g. *Record Daily Bioreactor Conditions* may need a viral CPE%/Live-Dead variant.

### Step 4 — Define the XStep list (reuse vs new)
- Map **every** batch-record section to one or more XSteps.
- Classify each as **Reuse** (from library) or **New build**.
- The **new** ones cluster around the genuinely process-specific chemistry/biology
  (e.g. for Merck: virus seed/MOI/infection + the BEI inactivation chain). Most utility blocks are reuse.
- Apply the **FM scoping rule**: only main-step FMs count. FMs that appear *only* inside the embedded
  **Conditional Header** or **Optional Signature** reference sub-steps are reference-only — don't document them.
  Exclude standard SAP FMs (e.g. `GET_SYSTEM_TIME_REMOTE`).

### Step 5 — Build the mock-ups (one per XStep) — see §3 for the formats
Each mock-up is a UI card showing how the XStep renders in the EBR. One folder per XStep, one `image.png`.

### Step 6 — Map coverage (the crosswalk)
- Build a **section-by-section coverage table**: every batch-record section → covering XStep(s).
- **Flag gaps** — any section with no XStep. Add blocks to close them (e.g. Merck needed
  *Pre-Inactivation/Thaw*; plus discrete *Gas-Flow Verification*, *Vessel Transfer*, *SAP/Excel Transaction*).
- Goal: 100% of the record covered, nothing dropped.

### Step 7 — Assemble the EBR / PI Sheet (New vs Old comparison)
- String the XStep cards together **in process order, grouped by phase**.
- Add a **PI Sheet header** (Material/Product, Process Order, Batch #, Control Recipe, Master Recipe,
  Plant, License, Effective Date).
- Add an **Old ↔ New crosswalk** table (every XStep ↔ original batch-record section) and a
  **"Original BR: Section ___" chip** on each card.
- Recurring blocks are shown **once** and noted as re-used at each occurrence.
- Output as a **PDF** (page-comparable to the old PDF) and an **HTML** (interactive).

---

## 3. The three mock-up formats — and when to use each

> **Decision rule:** what does the step capture?

| Format | Use when the step… | Looks like |
|---|---|---|
| **Table** | captures a **list / repeating rows** (+ Add Row), **or** has **Start/End timer** buttons | Instructions panel → **Data Input table** (leftmost **`#` index column**, parameterized columns, ▶Start/▶End, **one data row shown**, + Add Row) → `Performed By` column → `Witness By` footer |
| **Form (non-table)** | captures **one fixed record** (no repeating rows, no timer) | Instructions panel → **right-aligned label/field pairs**; computed/auto fields **greyed (read-only)**; required fields red `*`; `Performed By *` last |
| **Long Text Instructions** | captures **no data here** — pure instruction + sign-off, **or** an instruction whose data is recorded in **another** step | A **rich/long instruction text** + **Performed By** and **Check By** signatures. **No table, no form fields.** |

### Format details

**Table** — e.g. Component Addition (5 components), Daily Observations (per-day), Sample Submission,
Probe Identification (5 probes), and *every timer step* (Medium Addition, Harvest, Inoculation,
Inactivation, Neutralization, Cyclization, Transfers).

> **Render exactly ONE data row per table mock-up** (plus the header row), even when the real step captures
> many entries (5 components, N probes, one row per day, etc.). The single row shows the operator what one
> entry looks like; the **+ Add Row** control is kept **wherever the step is genuinely repeating** so the
> intent — "add another" — is still clear. Do **not** pad the mock-up with 3–5 empty rows; one row + Add Row
> communicates the same thing and keeps every card compact and consistent. (Omit Add Row **only** when the
> table is capped at a single row — i.e. one row is the maximum. There is no such thing as a "fixed-count"
> multi-row table: if a table can hold more than one row, it gets Add Row.)

> **Not everything belongs *in* the table.** A table step can carry **single-record** fields that don't repeat
> per row — a scale/valve ID, a charge date-time, a Select/Get button, an overall Recorded/Verified By. Put those
> **above** the table (a header block) or **below** it (a footer block), and keep only the genuinely **per-row**
> fields (Part No, Batch, result, `Performed By`) as columns. (Example: *WFI Container Setup* — Bag + Filter are
> table rows each with their own `Performed By`, but the WFI valve ID / charge time / Recorded+Verified By sit
> below the table.)

> **Calculations render two ways.** A one-input calc with a computed output (e.g. *Fill Volume = Planned − Seed*)
> is a **Form** — entries + a greyed computed result. A **multi-variable** calc — the reusable
> **Three-/N-Variable Calc** XStep — is a **horizontal calc *table*:** the variables sit in a row separated by
> narrow **operator cells** (`×` `÷` `+` `−` `=`), ending in a greyed **result** cell, with **no `#` index column
> and no + Add Row** (a calc is one computation, not a list). In the formula, **fixed constants** (a standard
> factor like `1.10`, `2.3 CV/cycle`) show as **greyed defaults** and **carried-forward** values (from another
> step) are greyed/entered — only true measurements are open entries. (Example: *Estimated VI Product Volume* =
> Bed Volume × Est. Product Volume × Cycles × VI Additions.) **Pick the calc XStep by variable count / operators:**
> 2–3 variables using the calc's two operator slots → **Three Variable Calc**; **4 variables, or a formula the
> 3-var can't express (e.g. mixed `×` then `+`)** → the **4 Variable Calc** (a new extension of Three Variable
> Calc). Same calc that runs each processing day is **one instance per day** (see rule 8), not a multi-row table.

**Form (non-table)** — e.g. Cell Identification, Vessel & Single-Use Bag Setup, pH Probe Calibration,
Fill Volume Calculation, MOI Calculation, LAF Sanitization, SUB Filter Decontamination, pH Adjustment.
(Calculation outputs like *Fill Volume*, *Amount Seed Needed*, *Actual MOI* are read-only/greyed;
fixed values like *Vessel Type = 2000L SUB* are read-only.)

**Long Text Instructions** — e.g. Assembly & Line Connections, Controller & Gas Flow Verification,
Antifoam Addition. Built from the reusable XStep (`SMPLXA: TR - Long Text Instructions` in DE2 903; DE1 100
equivalents: `SXS: Text Instructions with Sign-off`, `SMPL: Dyn. Instructions &/or Signature`). Structure: a
**Conditional Header** display of parameters `IV_HEADER` / `IV_INSTR` / `IV_PL_TXT` (rich/long text authored in
SiMPL MBR), the standard **Activate** wiring, and an **Optional Signature** block with separate **Performed by**
+ **Witnessed by** instructions.

> **Watch out — "data lives elsewhere":** a step can *look* like a data step (even its name may say so) but
> actually be **instruction-only** when the values it references are recorded in a **different** step. Example:
> *Antifoam Addition* (batch record §IV.F.1) reads "*add L-Glutamine, Gentamycin and antifoam **according to the
> component table***" — the amounts/batches live in the **Component Addition** step (§IV.C), so this step captures
> **nothing** and is **Long Text**, not a form. The tell is an instruction that points at data elsewhere:
> *"according to the component table / per the table above / as recorded in Section X / previously recorded."*
> Contrast with the *other half* of the same section, **LAF Sanitization** (§IV.F), which **does** capture new
> data (Room / LAF / Disinfectant Batch / Exp) — so it correctly stays a form. **Split a batch-record section
> into separate XSteps when one part records data and another is instruction-only.**

---

## 4. Key rules & constraints (learned the hard way)

1. **One signature per table line.** A Data-Input table may have **at most one** signature column
   (`Performed By`). A second signature must be a **step-level footer signature** (`Witness By` / `Checked By` /
   `Verified By`) — **not** a second column. Fix any table with two signature columns by moving the second to the footer.
2. **Instruction-only steps sidestep the signature limit.** If a step captures no data, use **Long Text
   Instructions**: By + Check By are separate signature *instructions* (not table-bound), so both work freely.
   Don't force a no-data step into an (empty) table.
3. **Time / date fields = a button + an FM-filled field beside it (never a typed field).** Whenever a step
   records a **start time, end / finish time, or date**, render a **▶ button** (▶Start / ▶End / ▶Date) with the
   timestamp **field(s) directly beside it**. The field is **populated by a function module** (a system-time FM)
   when the operator presses the button — it is **read-only**, never hand-keyed. So a "Start Time" column/field
   is really *two things*: the ▶ button **and** its stamped field. **Placement follows the format:** in a
   **table**, the button sits **beside** the stamped field (adjacent cells) — and because start/stop timer
   steps live in table cells, those steps are **tables**; in a **non-tabular (Form)** step, the button sits
   **directly above** the field its output goes into, **not beside it**.
4. **Three field roles in a calc/record step — only one is an entry field.** Triage every field before
   drawing it: **(a) Operator inputs** = batch-specific measurements → editable, usually required (red `*`).
   **(b) Standard-constant defaults** = fixed process parameters (e.g. Cell Density `1.0×10⁶ cells/mL`,
   MOI `0.2×`, a target concentration) → **pre-filled and read-only**, *not* blank entry fields, *no* `*`.
   **(c) Computed outputs** = calculation results, master-data descriptions, auto expiry dates → **read-only
   (greyed)**. Only (a) is typed. Rendering a defaulted constant (b) or a computed output (c) as a blank
   required input is a common mis-read — the operator would be asked to "enter" a value the process fixes or
   the system derives.
5. **Component/material tables: Batch # + Exp. Date are columns; SAP consumption is a PROCESS MESSAGE, not a
   column.** Record **Batch #** and **Exp. Date** as columns (with batch-expiry validation, and Exp. Date usually
   a validation output from the Batch No — rule 9). The SAP goods issue / consumption is posted by a **Goods Issue
   process message** attached to the step — e.g. `Z_PICONS`, SAP **movement type 261** (order consumption), keyed
   by the line's batch/qty. When the paper shows a **"SAP Consumption by/Date"** column, that is the process
   message's automatic posting record — **do NOT draw it as a data column or field.** (Confirmed on
   `SMPL: Additional Assembly` / `SMPL: Bag Replacement Volumetric`.)
   **One table row per consumed material.** When a step consumes **more than one material** (e.g. a bag *and* a
   WFI filter), give **each material its own table row** — so each line carries its own **Performed By** signature
   *and* its own goods-issue posting (one Z_PICONS per line). Do **not** render several consumables as separate
   *form* fields — a form is a single record and can't sign or consume per material. Put the per-material fields
   (Part No, Batch No, Exp. Date, Performed By) in the **table**, and keep any **single-record** fields that aren't
   per-material (a valve ID, charge date/time, vessel tare weight, an overall Recorded/Verified By) **outside** the
   table — above it (`header_fields`) or below it (`footer_fields`). (Real example: AZ3 *WFI Container Setup &
   Charge* — Bag + WFI Filter are two table lines; WFI Valve ID / charge date-time / expiry / Recorded+Verified By
   sit below the table.)
6. **Recurring blocks are reused, not duplicated.** The same block (Daily Observations, Sample Submission,
   pH Adjustment, LAF Sanitization, Vessel Transfer, Controller Config) is instantiated at each occurrence.
7. **One data row per table mock-up.** Every table card shows a single data row (plus the header), regardless of
   how many entries the real step captures. Keep the **+ Add Row** control wherever the step is genuinely
   repeating so the "add another" intent stays visible; drop it only when the table is capped at a single row
   (one row max). Never pad a mock-up with multiple blank rows.
8. **Every table has a leftmost `#` index column.** All Data Input tables start with a read-only, auto-numbered
   `#` column (1, 2, 3 …) as the very first column — a standard on every table step. It is rendered
   automatically; do **not** add it to the step's column list by hand. It mirrors the row-index function module
   (CUSTOM_INDEX / SET_LINE_IDX) wired into the live XStep. **Relabel it when the row index *is* the entity
   number** — one row per bag / day / cycle — to e.g. `Bag No.` or `Day #` rather than adding a redundant column;
   the auto-numbering then reads as the bag/day number. (Omit the index column entirely only for a **calc table**
   — see §3.) **Or run the step as one instance per day/cycle** instead of a multi-row table: when the batch
   record shows Day 1 / Day 2 (or per-cycle) rows for the *same* calc/record, model **one single-instance card**
   (no Day column, no Add Row) that the live recipe instantiates each day — don't draw the Day rows. (Real AZ3
   example: the per-day depth-filter calcs §11.1–11.8.)
9. **Lookup outputs come from an input validation on a field (the usual case) — or a Select/Get button (equipment/time).**
   A read-only field is often auto-filled from a value the operator types into a *different* field. Two distinct
   mechanisms — don't default to a button:
   - **(a) Input validation on an entry field — NO button.** The **default for material / batch lookups.** The
     entry field carries a `PPPI_VALIDATION_FUNCTION` that fires on entry and populates a linked read-only OUTPUT
     field. Real AZ example (`SMPL: Bag Replacement Volumetric`): **Part No** → `ZSMPL_FM_GET_MAT_DETAIL` →
     **Material Description**; **Batch No** → `ZSMPL_FM_GET_EXPIRY_DATE` → **Exp. Date**. You just *type the Part
     No / Batch No*; the derived field fills and renders greyed/read-only. There is **no** "Get Material" button.
   - **(b) Select/Get button** — for **equipment / probes / scales / time**: `Get Welder` / `Equipment Select`
     (→ `ZSMPL_FM_GET_ASSIGNED_EQUI_EBR`; opens a picker, may enforce a calibration / weight-check), `Get Time`
     (→ `GET_DATE_TIME`). The button populates its output fields.
   - **(c) Selection fields** — dropdown / radio / checkbox — for a fixed option set (Yes/No, a specific equipment
     ID, Optical-vs-Conventional, a preset amount): **chosen, not typed.** A dropdown restricted to a fixed value
     list is backed by a **characteristic created in CT04** (e.g. `ZSMPL_CHAR_DLIMS_TEST`, `ZSMPL_CHAR_YES_NO`)
     set as the field's requested value — that limits the field to those values. So when a batch-record column can
     only hold a handful of set values (e.g. *Item* = Bag / Filter, a Pass/Fail/N-A result, a Yes/No), model it as
     a **dropdown** and note the CT04 characteristic; if a needed value list doesn't exist yet, it's a new CT04
     characteristic to create. Example: `SMPL: Sample Submission Chart` → *DLIMS Test* column.
   All three differ from the three entry roles in rule 4: a **validation/lookup output** is read-only like a
   computed value; a **selection** is chosen. Tell for a validation output: the paper shows a value *derived from*
   another field the operator **enters** (Description from Part No, Exp. Date from Batch) — model it as a greyed
   output, not an entry field, and **not** behind a button. Some fields have no derivation source in the client's
   SAP tables (e.g. Autoclave Assembly ID / Exp. Date, SAP-Consumption-by) — those stay plain **entry** fields.
10. **Split a large or product-varying section into smaller, combinable XSteps.** When a batch-record attachment
    is big, mixes concerns, or differs across products (part numbers), don't build one giant mock-up — split it
    into several small XSteps that **combine as needed** and **reuse across products**. Real AZ examples:
    *Exhaust Filter Staging* → four XSteps (Exhaust Filter Info / Bioreactor Assembly Info / Sterilization Info /
    Additional Staging); *Antifoam Addition* → Pre-Automated / Post-Automated; *Bag Replacement* → two–three
    tables "to save screen space." Harmonize product variants by making **headers, instructions and column titles
    MBR-configurable** so one XStep serves many part numbers. Same instinct as rule 6 (reuse) and the §3
    data-vs-instruction split: smaller pieces reuse better and fit the screen.

---

## 5. The common reusable building-block library

These recur in essentially every bioprocess batch record and should almost always be **reused** (validate fit first):

- **Signatures** (Performed By / Witness/Check By) — native to every step.
- **Room/Equipment Assign** — equipment, scales, tanks, probes, freezers, autoclave, with calibration/steril expiry.
- **Component / Material Addition** (+ SAP goods issue, batch, expiry) — incl. *Weight/Volumetric Component Measurements*.
- **2-/3-/4-Variable Calc** — volume, MOI, formulation, tolerance, depth-filter sizing. The **4 Variable Calc** is
  a newer extension of *Three Variable Calc* for 4 variables or mixed `×`/`+` formulas.
- **Long Text Instructions** (the shell in DE2 903) — any instruction-only / sign-off step (verifications, line
  connections, installs, general notes). One shell, content authored in MBR.
- **Record Text / Numeric Value** — capture a single labelled value (an equipment ID, a reading).
- **pH Probe Calibration / DO Probe Calibration / Probe Info**.
- **Record Daily Bioreactor Conditions** / Sampling / **Viable Cell Density** / **Sample Submission**.
- **Filter Integrity Test**, **Centrifugation / Harvest Log**, **Transfer (Solution/Media)**, **Mixing**,
  **Timer (Begin/End/Summary)**, **Label Control & Reconciliation**, **Cleaning / Sanitization**,
  **Storage / Dispense**.
- **pH Adjustment (Acid/Base)**, **SIP of Sample Port / SIP-CIP Confirm / Equip SIP Verify**, **Sterility Dates**.

Genuinely **new** blocks are the process-specific ones (for Merck: Virus Seed Identification, Cell Bank ID,
MOI Calculation, Virus Seed Inoculation, Waste Kill, BEI Cyclization, Viral Inactivation, Neutralization,
Formulation, Bulk Dispense, Cold Storage, Pre-Inactivation/Thaw, single-use bag setup).

---

## 6. Sourcing data from SAP (MCP)

- **XSteps:** `xs_find` (locate by name), `xs_folder_tree` / `xs_get_folder_contents` (browse the library),
  `xs_get_version` shape=`snapshot` (full content — FM calls live at `node.instr.rows`; reference sub-steps
  named *Conditional Header* / *Optional Signature* are reference-only).
- **Systems:** `list_connections`. DE1 100 = main XStep library; DE2 903 = sandbox/dev (where `TR - Long Text
  Instructions` lives); QE2 100 = QA.
- **FMs / DDIC:** `find_objects` → `get_source` (ABAP body & signature), `get_xml` (domain fixed values).
- **Tables:** `get_table_data` / `run_query` (e.g. TOBJ/TACTZ for auth objects, TADIR for object inventory).

---

## 7. How the mock-ups & EBR were generated (tooling)

- Mock-ups: an HTML/CSS card template rendered **HTML → PNG via headless Chrome**
  (`chrome --headless=new --screenshot --window-size=W,H`). One `image.png` per XStep folder.
- EBR / PI Sheet: all cards assembled into one HTML, rendered **HTML → PDF**
  (`chrome --headless --print-to-pdf`, A3 landscape page).
- Driven by a small data file (one dict per XStep: title, instructions, and either `cols` for tables,
  `form` for forms, or a long-text body) + a phase plan for the EBR + an Old↔New crosswalk map.
- Re-running the generator rebuilds everything, so wording/column/format changes are one-line edits.

---

## 8. Quick checklist for a new batch record

- [ ] Read the full record; capture sections + attachments + header fields.
- [ ] List the recurring data-capture patterns.
- [ ] `xs_find`-search the whole library per pattern; check for an existing client folder.
- [ ] Build the XStep list; mark **Reuse vs New**; apply the FM scoping rule.
- [ ] Pick a **format per step** (Table / Form / Long Text Instructions) using the §3 decision rule.
- [ ] **Sweep for constants** — every fixed/standard value becomes a read-only **defaulted output**, not an entry field.
- [ ] Enforce **one signature per table line**; computed fields read-only; component tables get SAP+batch+expiry.
- [ ] Build one mock-up per XStep.
- [ ] Build the **coverage crosswalk**; close every gap.
- [ ] Assemble the **EBR / PI Sheet** (phase order + header + crosswalk + per-card BR-section chips); export PDF + HTML.
- [ ] Validate reuse candidates by **opening the real XStep**, not just the name.

---

## 9. XStep Archetype Catalog

The single most useful scanning aid: the ~46 AZ Phase 2 XSteps (and the 51 `ZSMPL_AZP2` FMs) collapse into
about **12 recognizable archetypes**. Pattern-match each batch-record step to an archetype instead of
treating it as bespoke — the archetype tells you the likely **format** and **FMs**.

| Archetype | Phase 2 examples | Default format | Characteristic FMs |
|---|---|---|---|
| **Instruction + sign-off** | Long Text Instructions | Long-text | none (activate + signatures) |
| **Signature** | Signature Table, Optional Signature | embedded | SIG_ADD_DB_CB, SIG_VALIDATION, VALI_SUPE_SIG |
| **Equipment / probe / consumable ID** | Room/Equipment Assign, Optical pH / pO2 Probe Info, EFS Assembly/Exhaust Info, Additional Assembly | Form / Table | GET_ASSIGNED_EQUI_EBR, ELB_GET_ASS_EQ_VALID, GET_EXPIRY |
| **Bag / filter / vessel swap** | Bag Replacement (Vol/Wt), TFF Swap, CM Bag, EFS Additional Staging | Table | GET_FILTER_BOM, INCREMENT / SET_LINE_IDX |
| **Calibration** | pH Probe Calibration | Form | CHECK_CHAR_DATE, MIN_MAX |
| **Material / component addition** | Medium / Total Medium, Glucose / Nutrient Feed, Feed Set Up, Antifoam (+K Setpoint), Material Consumption, Conditioned Medium | Table | GET_MAT_ITEMS/BOM, VALIDATE_QUANTITY, LOAD_MAT_DESC, **goods-issue process message** |
| **Calculation** | Bioreactor pH Calc, Three Variable Calc, Yield, Theoretical Vials, Harvest Sampling Calc, Flow Rate | Form / Table | **BASIC_CALCULATIONS** (simple) or CALC_VALIDATE / CALC_EXECUTE (multi-step); MIN_MAX / CALC_TOLERANCE |
| **Daily sampling / observations** | Bioreactor Sampling, Sampling Record, Rocker Bag Daily Sample, Medium Hold Time Readings | Table | STORE_DAILY_SAMPLE (persist), GET_PH_VALUES / OPS, MIN_MAX, equipment "Get" buttons |
| **Analytics recording** | Viable Cell Density, Cell Count Log, PCV Measurement | Table / Form | INSERT / LOAD_FLASK_DETAILS, RANGE_CLASSIFY |
| **Sample submission (LIMS)** | Sampling Submission Chart, Non-Routine Sampling, Viral Sample Submission | Table | GET_DLIMS_INFO, GET_SAMPLE_PARAMS |
| **Timer / elapsed time** | Timer Begin/End/Summary, Hold Time, Flow Rate | Table | EXC_TIME_*, ELAPSED_TIME_TYPES |
| **Cleaning / steril / labeling / harvest** | Cleaning Cycle, EFS Sterilization, Label Control & Reconciliation, Harvest Log, Centrifuge Run Sheet, Solution Summary, Filter Integrity | Table / Form | SIP-CIP confirm, STARTING_LABELS, CALCULATE_TOTAL |

**Invisible helper FMs** (not operator steps — table/row plumbing and async posting): `CUSTOM_INDEX`,
`SET_LINE_IDX`, `ALTERNATE_ROWS`, `SET_ROW_ORDER`, `CHANGE_TO_NA`, `SET_ORDER_STAT_ASYNC`, `DISCARD_*`.

---

## 10. Batch-Record Scanning Playbook

> ### ⭐ Hunt for the constants — the highest-value pass
>
> **When you see a constant in the original batch record, identify it and put it in the XStep as a read-only
> output (a defaulted field), not an entry field.** This is the single biggest win of the scan. Any value the
> **process** fixes — rather than the **operator** measuring it — is a constant that should be pre-populated,
> greyed, no `*`, so the operator *confirms* it instead of re-typing it, and every calculation/validation uses
> the one governed value on every batch.
>
> **What counts as a constant:** standard cell density (`1.0×10⁶ cells/mL`), standard MOI (`0.2×`), target
> pH / temperature / DO setpoints, nominal fill / working volumes, fixed dilution or conversion factors,
> standard air-pressure limits, "no warmer than `2x°C`", per-SOP hold times — anything printed as a set value.
>
> **How to spot one:** a value **printed beside the field** (`X 1.0x10⁶`, `0.2x`), an inline `X` / `÷`
> operator carrying the value, or wording like *standard / nominal / target / set / fixed / per SOP / do not
> exceed*. Do a **dedicated sweep** for these — they hide inside instruction prose and calc formulas, not just
> in obvious "spec" fields.
>
> **Payoff:** removes a whole class of transcription error, and makes the standard **visible and
> change-controlled in one place** (change the default once, every occurrence updates) instead of being
> re-keyed by hand every batch.

### Recognition cues (what you read → what it is)

| In the batch record | → maps to |
|---|---|
| "By / Check By" with **no data** | Instruction + sign-off (Long Text) |
| "…**according to the component table / per the table above / as recorded in Section X**" + By/Check By | Instruction-only (Long Text) — the data is captured in **another** step; don't duplicate it |
| A **single fixed record** of fields | Form archetype |
| A **repeating table** (+ Add Row) | Table archetype |
| Equipment ID + **calibration / sterilization / lot + expiry** | Equipment / Consumable ID |
| Component table (Material / Batch / Exp) with a **"SAP Consumption by/Date"** column | Material Addition → **Goods Issue process message** (`Z_PICONS`, mvt 261). The SAP-consumption column is the message's auto-record — **not** a drawn field |
| **Several materials** each recorded with Part/Batch/Exp/By + consumption | **One table row per material** (per-line `Performed By` + its own Z_PICONS goods issue). Single-record non-material fields go **outside** the table (header/footer fields) |
| "**Calculate** A = B − C" | Calculation → **simplest FM first** (BASIC_CALCULATIONS) |
| A value **printed beside the field** (`X 1.0x10⁶`, `0.2x standard MOI`) | Standard constant → **read-only default**, not an entry field |
| Inline **`X` / `÷`** glyphs between fields (`Cell Density: X … ÷ Inv. Log Titer`) | The **formula** *and* which operands are fixed (after `X`) vs entered (blank after `÷`) |
| A calc that **aggregates over a repeating set** (per seed batch, + Add Row) | **Table**, not Form — even though the final output is one value |
| Several **lettered sub-steps** each with its **own By/Check By** | **Separate XSteps** — one sign-off pair = one XStep |
| An input labeled "**(from step X)**" | A **carry-forward** field — sourced from another step's output, not a fresh entry |
| **Material Description** next to a **Part No**, or **Exp. Date** next to a **Batch No** | **Validation output** — the entry field (Part No / Batch No) has a `PPPI_VALIDATION_FUNCTION` (`ZSMPL_FM_GET_MAT_DETAIL` / `ZSMPL_FM_GET_EXPIRY_DATE`) that fills the greyed output on entry. **No button.** |
| Batch/Exp/Description next to an **Equipment / probe / welder / scale** | **Select/Get button** output (`Get Welder` → `ZSMPL_FM_GET_ASSIGNED_EQUI_EBR`) — a picker, may enforce a calibration/weight-check |
| A **checkbox / radio / "☐ option A ☐ option B"** or a fixed option list | **Selection field** (dropdown / radio / checkbox) — chosen, not typed |
| The **same section repeated across product PNs** with small differences, or one **oversized** attachment | **Split into smaller combinable XSteps**; make headers/columns MBR-configurable to serve all variants |
| A numeric field with "**(min – max)**" | attach a range validator (MIN_MAX / tolerance) |
| "Sample **daily** / record conditions" | Daily Sampling → persist (STORE_DAILY_SAMPLE) |
| "Submit to QC / retention / cooler" | Sample Submission (LIMS) |
| "Start / Stop time, hold time, elapsed" | Timer |
| A **start / end time or date** field to record | A **▶ button + an FM-filled read-only field** (system-time FM stamps it; not typed) — button **beside** the field in a table, **above** the field in a form |
| "**if X, proceed to step Y / N/A** the rest" | Conditional activation (INITIAL_ACTIVE + MBR_DEP_CHECK_ACTIVE) |
| **Attachment / non-routine** event | Standalone reusable block, invoked on demand |
| **Same table repeated** per day / phase | ONE reusable block instantiated N times (dedupe!) |

### The functional / data dimension (capture per step)

Don't just note the UI — note the **data operations** (this is what the FM wiring reveals). For each step ask:
does it **read** master data (equipment / BOM / batch), **validate** (range / tolerance / equipment),
**calculate**, **persist** to a `ZTC_*` table (*and who reads it back?*), or **post a real SAP transaction**
via a process message (goods issue / receipt / status)? Also note the **event** it should fire on.

### The two passes

1. **Structural pass** — sections, attachments, header fields, and **where blocks repeat**.
2. **Per-step classification pass** — archetype + exact fields/units + specs/ranges + signatures + SAP
   touchpoints + conditionals.
3. **Constant sweep** (see the ⭐ callout above) — mark every fixed/standard value and tag it as a read-only
   **default output**, distinguishing it from the batch-specific measurements the operator actually enters.

Then: library-match each archetype (**validate by opening**), pick the **minimal** FM set, choose the format
(Table / Form / Long Text), **dedupe** recurring blocks (note reuse count), build the **coverage crosswalk**,
and close gaps.

---

## 11. Function Module patterns (how FMs are wired in XSteps)

Observed in the AZ Bioreactor XSteps — reuse these mental models when designing new steps.

- **FMs fire on XStep lifecycle events**, not just buttons:
  `DOCUMENT.GENERATED` → INITIAL_ACTIVE (set active/inactive); `PARAMETER_CHANGED` → recalc/re-validate;
  `DOCUMENT.SAVING` → MBR_DEP_CHECK_ACTIVE (re-check prerequisites); `PROC_INSTR.COMPLETING` → **persist to SAP**.
- **Three call-sites in one XStep:** **buttons** (e.g. "Get Equipment" → read master data), **column validators**
  (`PPPI_VALIDATION_FUNCTION` — range / equipment / calc as-you-type), and **event/function calls**.
- **Full CRUD against SAP:** e.g. `STORE_DAILY_SAMPLE` `ENQUEUE`-locks → `INSERT INTO ztc_daily_sample` → `DEQUEUE`
  on completion, and the *same FM* reads it back via a retrieve flag (cross-step / cross-day data). Others
  **update** batch shelf-life (SLED/DOM) or upsert custom `ZTC_*` tables.
- **Real SAP transactions via process messages:** the "SAP" column on a component table is a **goods movement**
  (e.g. `CREATE_PROC_MSG`, movement 261) — not a checkbox.
- **The dependency engine = electronic conditional logic:** INITIAL_ACTIVE + MBR_DEP_CHECK_ACTIVE turn the paper
  record's *"if X, proceed / N/A the rest"* branching into enforced perform/verify-before-start gating.
- **Good-practice patterns to reuse:** dual-mode FMs (write vs read via a flag), ENQUEUE/DEQUEUE around writes,
  validators on every input, and a custom `ZTC_*` table layer for EBR-captured data (queryable/reportable).

---

## 12. Lessons & gotchas banked from these engagements

- **Prefer the simplest existing FM.** A single subtraction is `ZSMPL_FM_BASIC_CALCULATIONS`
  (`IM_QTY`, `IM_QTY_2`, `IM_OPERAND` ADD/SUB/MUL/DIV → `EX_RESULT`), **not** the generic
  CALC_VALIDATE → CALC_EXECUTE → INPUT_VALUE → OUTPUT_VALUE chain.
- **One signature per table line** — a second signature goes to the step-level footer, or the step becomes a
  Long Text Instructions step (which carries By + Check By natively, no table).
- **Numeric `ERFMG` fields need no char-conversion FM** (INPUT_VALUE is only for TEXT30 basic-XStep entries).
- **Validate reuse by opening the XStep** — a name match is a candidate, not a fit (e.g. viral Daily
  Observations needs CPE% / Live-Dead that the generic bioreactor conditions block lacks).
- **Naming traps:** e.g. `GET_EXPIRY` vs `GET_EXPIRY_DATE` vs `GET_EXP_DATE` are different FMs; confirm the one
  the XStep actually calls. **Skip OBSOLETE** library items.
- **Computed fields are read-only (greyed);** component/material tables always carry **SAP + Batch + Expiry**.
- **Don't duplicate data across steps.** A step that only *instructs* an action against data recorded elsewhere
  (e.g. "add … according to the component table") is **Long Text**, not a data step — capture each value **once**,
  in the step that owns it. Watch for step **names that overstate** what's captured (a step called "Antifoam
  Addition" that records nothing).
- **One batch-record section can be several XSteps.** Split it where one part records data and another is
  instruction-only — e.g. §IV.F becomes *LAF Sanitization* (form, records Room/LAF/Batch/Exp) **+** an aseptic
  addition instruction (Long Text). Conversely, **dedupe** the same table repeated across phases into one reused block.
- **Split calcs by signature ownership — the sign-off pair is the boundary.** When one section (e.g. §V) has
  several lettered sub-steps that each carry their **own** *Calculations By / Check By* — Weighted-Average Titer
  (§V.E), planned MOI / seed amount (§V.F), Actual MOI (§V.H) — make each its **own XStep**. Don't merge related
  calcs into one form just because they share a topic; **one By/Check-By pair = one XStep**. (This is broader than
  "data vs instruction": here *all three are calcs* and still split.)
- **Format follows the input, not the label.** A calc is a **Form** when it's a single record (Fill Volume,
  planned MOI) but a **Table** when it aggregates over a repeating set (Weighted-Average Titer across N seed
  batches, + Add Row) — even though its final output is a single value. Ask "does the input repeat?", not
  "is it a calculation?".
- **Standard process constants are read-only defaults, not inputs.** In a calc, fixed standards like Cell
  Density (`1.0×10⁶ cells/mL`) and MOI (`0.2×`) are pre-populated read-only; only batch-specific measurements
  are entry fields. The tell is the batch record **printing the value beside the field** (`X 1.0x10⁶`), often
  with "*standard … for infection*". Read the inline **`X` / `÷`** operators too — they encode the formula and
  flag which operands are fixed (constant after `X`) vs entered (blank after `÷`).
- **Calc outputs carry forward.** One step's computed output becomes the next step's input — Weighted-Average
  Titer's *Final Inv. Log of Titer* feeds MOI Calculation's *Inv. Log Titer*. Mark such inputs as sourced-from-
  step-X (read-only / defaulted from the upstream result), not as fresh operator entries.
