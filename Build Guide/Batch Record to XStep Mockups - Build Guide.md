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
- **Open the ACTIVE (Released) version — not just any version.** An item can carry many versions; the live one
  is the **Released** version, which is **not necessarily the highest-numbered** (real case: an item's active
  version was `0001`, with `0002`/`0003` as later drafts). The read tools resolve it via the picker (Released
  status wins, else highest 4-digit version name). An item with **no** Released version and non-numeric names
  is **ambiguous** — the recipe owner must designate one before you can trust which version's content to mirror
  (real case: *Material Consumption* was unresolvable until version `0002` was released).

### Step 4 — Define the XStep list (classify R / V / N)
- Map **every** batch-record section to one or more XSteps.
- Classify each with the **three-way tag** (not just reuse-vs-new) — this drives how the EBR renders it:
  - **R = Reuse** — an existing SMPL / DE1 100 library XStep used **as-is**. **No new mock-up** — it renders in the
    EBR as a **compact reuse card** (title + one-line description + a `Reuses: SMPL: …` pointer), because the real
    UI already exists in the library.
  - **V = Variant** — a **new mock-up** that is a parameterized/range-validated **variant of an existing** library
    XStep. Carries full mock-up content **and** names the reused base (`reuses=`).
  - **N = New** — genuinely new; full mock-up, no library base.
- **Only N and V get mock-ups.** R steps are folder-only + a reuse card. On a real reworked record this lands around
  **~40% R / ~20% V / ~40% N** — the majority of a record is reuse, and treating everything as "New" (a mock-up per
  step) is the most common early mistake. (AZ3 VI+C&D reworked to **15 R + 8 V + 15 N**.)
- The **N** ones cluster around the genuinely process-specific chemistry/biology (virus seed/MOI/infection + the BEI
  chain; low-pH titration; skid recipe; recovery/dilution). Most front-matter and utility blocks are **R**.
- **Name the reuse target explicitly** (`reuses="SMPL: …"`) and **verify it exists in DE1 100** (Step 3 / §6) — don't
  leave it "to be confirmed." A wrong-but-plausible reuse name is worse than an honest gap.
- Apply the **FM scoping rule**: only main-step FMs count. FMs that appear *only* inside the embedded
  **Conditional Header** or **Optional Signature** reference sub-steps are reference-only — don't document them.
  Exclude standard SAP FMs (e.g. `GET_SYSTEM_TIME_REMOTE`).

### Step 5 — Build the mock-ups (one per XStep) — see §3 for the formats
Each mock-up is a UI card showing how the XStep renders in the EBR. One folder per XStep, one `image.png`.

### Step 6 — Map coverage (the crosswalk)
- Build a **section-by-section coverage table**: every batch-record section → covering XStep(s).
- **Flag gaps** — any section with no XStep. Add blocks to close them (e.g. Merck needed
  *Pre-Inactivation/Thaw*; plus discrete *Gas-Flow Verification*, *Vessel Transfer*, *SAP/Excel Transaction*).
- **Do a deep-review sweep for the *hidden* recordables** — the misses aren't whole sections, they're fields
  buried in a table you already mapped. Re-walk every batch-record table and hunt specifically for: computed
  **totals / summary rows** (a "Total … (all cycles)" line under a per-cycle table); **cross-record write-backs**
  (a step that writes a value back into *another* MPR/section); **sub-tables** buried inside one attachment; and
  **sibling "results" tables** — **if one "results"/effluent table is customised into a variant, its siblings
  almost always need the same treatment.** (Real AZ3 finds: the *Total Load Volume (all cycles)* summary, the
  Strip 2 *Inlet 6 Totalizer* volume, and four effluent-results tables that all had to become the same variant.)
- Goal: 100% of the record covered, nothing dropped.
- **Make coverage provable with a Requirements Traceability Matrix (RTM).** The strongest proof is structural: map
  **every recordable section to exactly one XStep and render the *whole* section verbatim** beneath its card (a
  "New vs Old" panel — instruction + the exact fields captured, as chips). Then the coverage claim reduces to "is
  every section mapped?" — which is auditable, and any keyword/harvest heuristic used for reusable blocks becomes a
  *redundant* view that **cannot drop content**. Emit the RTM as a spreadsheet (one row per instruction group →
  fulfilling XStep, with a coverage status), plus a **streamlined-analysis reconciliation** sheet (each streamlined
  step → XStep, flagging Covered / Folded / Gap) and a **Goods-Issue & Labels** sheet (rule 12). Since a spreadsheet
  can't be viewed in Claude Code, also render the RTM to **PDF/HTML** via the same Chrome pipeline (§7). (AZ3 RTM:
  464 recordable lines, 100% mapped; the reconciliation surfaced the real gaps to resolve.)

### Step 7 — Assemble the EBR / PI Sheet (New vs Old comparison)
- String the XStep cards together **in process order, grouped by phase**.
- Add a **PI Sheet header** (Material/Product, Process Order, Batch #, Control Recipe, Master Recipe,
  Plant, License, Effective Date).
- Add an **Old ↔ New crosswalk** table (every XStep ↔ original batch-record section) and a
  **"Original BR: Section ___" chip** on each card.
- Recurring blocks are shown **once** and noted as re-used at each occurrence.
- Output as a **PDF** (page-comparable to the old PDF) and an **HTML** (interactive).

---

## 3. The four mock-up formats — and when to use each

> **Decision rule:** what does the step capture?

| Format | Use when the step… | Looks like |
|---|---|---|
| **Table** | captures a **list / repeating rows** (+ Add Row), **or** has **Start/End timer** buttons | Instructions panel → **Data Input table** (leftmost **`#` index column**, parameterized columns, ▶Start/▶End, **one data row shown**, + Add Row) → `Performed By` column → `Witness By` footer |
| **Form (non-table)** | captures **one fixed record** (no repeating rows, no timer) | Instructions panel → **right-aligned label/field pairs**; computed/auto fields **greyed (read-only)**; required fields red `*`; `Performed By *` last |
| **Long Text Instructions** | captures **no data here** — pure instruction + sign-off, **or** an instruction whose data is recorded in **another** step | A **rich/long instruction text** + **Performed By** and **Check By** signatures. **No table, no form fields.** |
| **Composite (gated blocks)** | is **one section with several conditional sub-sections** — a paper table like §8.4 "VI Treatment Vessel" (Bag *or* Tank, optional Vent Filter, required Product Filters, Tare Weight) | Instructions panel → a **sequence of blocks**, each a small table or form. A block may be **gated** by a `… Required?` **Yes/No dropdown** that activates/deactivates it; **tabular** blocks get a green section header (+ a **Goods Issue** badge if consumed); **non-tabular** blocks get **no title** (fields self-label). |

> **Composite = a last resort, not a default.** Only use it when the paper genuinely presents one numbered section
> as a set of mutually-exclusive / optional sub-tables (bag-vs-tank, if-applicable filters). Most steps are one of
> the first three formats. A composite is authored as an ordered list of blocks; each block is either a **table**
> (`cols`) or a **form** (`fields`), optionally preceded by a **gate** (`… Required?` dropdown) and marked **`gi`**
> when its rows are consumed (per-line Goods Issue). **Rule: green section header only on tabular blocks; drop the
> title entirely on non-tabular blocks** (the client asked for this — a green bar over three yes/no fields is noise).
> The gate is the visible face of the live **DEACTIVATE/ACTIVATE Setup-Function** pattern: the dropdown value drives
> whether the block's fields are active or N/A. (Real AZ3: *VI Treatment Vessel Setup* — Bag Required? → bag table
> (GI); mixer-bag attachment yes/no fields (no title); Tank Required? → tank form; Vent Filter Required? → 3-field
> table; always-required Product Filter table (per-line GI); Tare Weight form.)

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
   as its **default value** — so the operator confirms a system‑stamped time rather than keying one from scratch —
   and it is **editable/overridable** (they may legitimately need to correct the date/time). What makes it
   GxP‑sound is the **`Performed By` signature** on the line (attributable + audit‑trailed), **not** locking the
   field. Mechanism (real XStep convention): the FM writes a **default variable** (`LV_*_D` / `LV_*_T`) wired as
   the field's **Default Value** (`PPPI_DEFAULT_VARIABLE`), while the field captures into a separate value
   variable (`LV_DATE` / `LV_TIME`); set **Reason Required** on the field where a documented reason for change is
   wanted. So a "Start Time" column/field is really *two things*: the ▶ button **and** its stamped, editable
   field. **Placement follows the format:** in a
   **table**, the button sits **beside** the stamped field (adjacent cells) — and because start/stop timer
   steps live in table cells, those steps are **tables**; in a **non-tabular (Form)** step, the button sits
   **directly above** the field its output goes into, **not beside it**.
   **Record Date and Time as SEPARATE fields, not one "Date & Time" field.** There is no combined date-time
   primitive downstream — a timestamp is a Date field **and** a Time field (in the PI Sheet Sandbox: an
   `entry_date` + `entry_time`, or `output_date` + `output_time`; §13). The client prefers them split for
   visibility, so a stamped "Charge Date & Time" or a computed "Expiration Date & Time" renders as two adjacent
   fields sharing one ▶ button, not a single field. (Real AZ3 example: *WFI Container Setup* — Charge Date /
   Charge Time and the computed Expiration Date / Expiration Time are four separate fields.)
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
     set as the field's requested value (`PPPI_REQUESTED_VALUE`) — that limits the field to those values. So when a
     batch-record column can only hold a handful of set values (e.g. *Item* = Bag / Filter, a Pass/Fail/N-A result,
     a Yes/No), model it as a **dropdown**. **A mock-up dropdown ALWAYS becomes a real dropdown in the built XStep,
     and every dropdown requires its own CT04 characteristic (`ZSMPL_CHAR_*` — CABN + allowed CAWN/CAWNT values).**
     So each dropdown is *two* deliverables: the column **and** the characteristic behind it — always name the
     characteristic and list its allowed values (create a new one if none fits). **Never downgrade a dropdown to
     free text** (this client's workflow, confirmed 2026-07-15 — it overrides the generic "specs sometimes mean
     free text" caveat in the SAP builder guide). Example: `SMPL: Sample Submission Chart` → *DLIMS Test* column
     (`ZSMPL_CHAR_DLIMS_TEST`).
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
11. **Keep column / field labels short (≈30-char cap).** The live XStep stores an input column's label in
    `PPPI_INPUT_REQUEST`, which caps at **~30 characters** — an over-long header makes the table instruction fail
    to build (a bare `CX_CMX_TYPES_EXCEPTION`, no hint). Write mock-up column headers and field labels in the
    **abbreviated PI-sheet form** (units in parentheses, no sentence fragments): `Net Wt / Vol (kg=L)` not
    `Product Net Weight / Volume (kg = L)`; `Vol Loaded (L)` not `Actual Volume Loaded per Totalizer (L)`. Put the
    full description in the **instruction text**, not the header. (Output `PPPI_OUTPUT_TEXT` and instruction stext
    are more forgiving, but keep everything tight.) Parameter *variable* names are also capped at **10 chars** in
    SAP — not a mock-up concern, but it's why labels and variables stay terse.
12. **Sweep for Goods-Issue and Label points — they are load-bearing and easy to miss.** Do a dedicated pass over
    the record for two signals:
    - **Goods Issue** — every paper **"SAP Consumption Performed by/Date"** cell (and per-material variants like
      *"SAP Consumption of 8012555"*) is a material-consumption point. In the digital XStep this is **not** a manual
      field — it posts automatically via the **Goods Issue process message (`Z_PICONS`, movement type 261)**. Mark
      every consuming table/step (BOM, buffer/solution additions, filters, bags, resin, WFI, NaOH). Per-line GI on a
      table means the process message fires on each row's `Performed By`.
    - **Labels** — every **"label the vessel/sample/bag …"** instruction (usually **SOP-0107056**) is a label-print
      point. Note vessel labels (treatment vessel, retentate vessel + valves, intermediate/PFI vessels), sample
      labels, and product labels. (Open question to raise with the client: is a label **printed via a process
      message to a label printer**, or applied-and-recorded manually? It changes whether the XStep needs a
      control-function/process-message element.)
    Cross-check the sweep against your XStep list and **flag any consuming/labeling point not reflected in a step's
    design** — on real records ~half of these were initially missing. (AZ3: 17 GI points + 7 label points.)
13. **"Needs an XStep" vs "separate form" — one test.** Does the batch record contain the **fields to capture the
    measurement**, or does it only **name a sample / reference an external form**? If it only points outward (a
    sample designation tested per an SOP, a "record … from FORM-XXXX", a separate MPR/worksheet), it is **not** a
    new XStep — it's covered by the Sampling Record block or is genuinely out of scope. Build an XStep only where the
    record has capture fields. (Real AZ3: *SoloVPE / SOLO_A280* looked like a gap but is a **sample** (SOP-0107091);
    its concentration **result** *is* recorded, in the product-info table, so it's captured there — not a worksheet
    XStep. *VPro filter-integrity* belongs to a **separate record** (MABR-0027575 / PN 8012474); *Cassette Install*
    is **FORM-0071789**. All three: no new XStep.)
14. **Front-matter is recordable too — don't skip §1-6.** The equipment/materials **Bill of Materials**, **Additional
    Manufacturing Supplies** (extra filter/bag used mid-process), **Additional Solution Batches** (a solution-batch
    switch), and **Process Notes / global limits** are all recordable and need XSteps (Display BOM `R`; Additional
    Mfg Supplies `V`; Additional Solution Batches `V`; Process Notes `V`/Long-Text). Only the pure narrative
    (Process Summary, Flowchart, Referenced-Documents SOP list) and the revision history are non-recordable.
15. **Don't create a redundant block — check whether the data is captured at point-of-use first (the inverse of
    rule 10).** Before adding a "record all the X batches / all the Y IDs" consolidated front-matter table, ask
    *where is this actually recorded in the record?* If each value is captured **at its point of use** (the
    material batch/exp in the §10 acid table, the buffer in the skid-recipe step) and/or in the **§4 BOM**, a
    separate consolidated table is **redundant** — delete it. Map each section to the **fewest** XSteps that cover
    its genuine recordables. Tell for a redundant front-matter table: the section is largely a **reference /
    process-flow diagram** and its only *new* recordable is a small sub-table. (Real AZ3: §5 "Document Process
    Flow Sheet" — its only recordable is the *Additional Solution Batches* switch table; the solution batch/exp
    values live at point-of-use + BOM, so the extra "Solution/Buffer Batch Record" step was removed.) This is the
    counterweight to rule 10 — split when a section mixes concerns, **consolidate/drop** when a block duplicates
    capture that already happens elsewhere.
16. **Equipment is assigned once, then retrieved on use with a `Get [Type]` button.** The record assigns every
    instrument up front in a **Room & Equipment Assign** step (with the calibration check); each later step that
    *uses* a piece of equipment pulls it via a **`Get [Type]`** button that populates **`[Type] ID` + `[Type]
    Description`** (+ **`[Type] Cal Due`** for *calibrated* instruments — scale, pH/cond meter, thermometer — but
    **not** for mixer / stir plate / pump). **Substitute the actual equipment word** for "Equipment": *Get Scale /
    Balance*, *Get pH / Cond Meter*, *Get Thermometer*, *Get Mixer*, *Get Stir Plate*, *Get Pump*. Two rules of
    thumb: **(a)** a pH/conductivity meter and a thermometer are **distinct instruments** in the paper (separate
    IDs) → **two separate Gets**, not one; **(b)** the Get lives in the **reusable block** for that activity
    (weighing→Product Vessel Weigh, measuring→Product pH/Cond/Temp, mixing→Product Mixing) — a process step that
    weighs/measures **instantiates that block** rather than duplicating the button; add an *inline* Get only where
    an N-step embeds the weigh/measure/mix in its own table. To find every Get point, sweep the record for
    equipment-ID capture cells (`Scale/Balance ID`, `Meter ID`, `Thermometer ID`, `Mixer ID`, `Pump ID`,
    `Calibration Due Date`) and the equipment nouns; note that **not every BOM instrument is retrieved** — a Filter
    Integrity Tester assigned in the BOM may only be used on a *separate* form (rule 13). The reusable block behind
    every `Get [Type]` is **`SMPL: Equipment Select`** (DE1 100) — prefer it over `Record Text Value` even for
    meter / thermometer / Pendotech IDs, since those are calibrated. FM: the Get button is an equipment-lookup FM
    (`GET_ASSIGNED_EQUI_EBR` + `ELB_FM_GET_ASS_EQ_VALID`) resolving the assignment.
17. **Assemble a composite from a stack of existing blocks before building a New XStep — the "hidden Conditional
    Header" pattern.** A step that looks like one bespoke composite is usually **2–3 existing DE1 100 blocks
    stacked**. Every XStep template carries a **Conditional Header (SXS reference)** that can be *hidden*; stack the
    blocks and hide the header on the 2nd/3rd so the group renders as **one XStep in the EBR** while staying separate
    reusable references underneath. **Decompose before you build** — reserve **N** for logic no stack can express.
    Building-block vocabulary (all confirmed in DE1 100, §6):
    - `SMPL: Material Consumption` — one material line + goods issue; `SMPL: Component Goods Issue` — one GI step over
      several materials.
    - `SMPL: Record Text Value` / `SMPL: Record Numeric Value` — a single labelled value (ID, count, reading).
    - `SMPL: Equipment Select` — the equipment/instrument Get (rule 16).
    - `SMPL: Calc Three Columns` (2 inputs) · `SMPL: Three Variable Calc` (3 inputs) · `SMPL: Calc Range Values`
      (ranged result).
    - dynamic dropdowns (Yes/No etc.) · `SXS: Text Instructions with Sign-off` (Long Text Instructions).
    Worked examples (Jason, AZ POC): *Product Collection Vessel Setup* = `Equipment Select` (scale) + `Record Numeric
    Value` (tare) + `Material Consumption` (bag) + 3× dynamic dropdowns (attachments); *Pod Holder & Pressure Sensors*
    = `Record Text Value` (holder ID) + 2× `Material Consumption` (sensors) + `Equipment Select` w/ calibration
    (Pendotech). Same "gated blocks" shape as §3, but the blocks are **library references**, not bespoke mock-up
    sections. In the EBR crosswalk, an assembled step's `Reuses:` names the **stack** (e.g. "Equipment Select +
    Record Numeric Value + Material Consumption"), not "new".
18. **Near-match → ask the client (don't silently default, don't over-build).** When the reuse search (§6) turns up a
    block that matches **except a small field variant** — one or two fields different, same structure/purpose
    (canonical: `SMPL: Equipment Select` exists but lacks AZ's required **Calibration Due Date**) — do **not** quietly
    fall back to the generic block **or** immediately declare a new variant. Raise it and ask: *"`<block>` in DE1 100
    is a near-match but is missing `<field(s)>` — is there a step in a **client system** that already fulfils this
    variant?"* The answer (which system / no / not sure) decides reuse-the-client-variant / build-new / flag-open.
    **Client systems beyond DE1 100 may hold variants we can't see**, so a DE1 100 near-miss is not proof the variant
    doesn't exist. **Batch** these questions at the end of a decomposition pass; a structural / purpose difference is
    just "new", not a variant question.
19. **Goods issue with no batch field — source the upstream PN/batch, and confirm.** Some consuming steps have **no
    batch field** (conditioned medium, the column, incoming product) yet still must post an SAP goods issue. Don't
    assume — flag *how* the `Z_PICONS` (mvt 261) consumption is sourced; the usual answer is **consume the upstream
    MPR's PN / batch** (e.g. the Pod Harvest product). Note it on the card and raise it as an open config question for
    the functional spec.
20. **Collapsible blocks auto-collapse into one table when stacked — the dynamic-authoring mechanism (Jason Craig).**
    Certain building blocks are **collapsible**: each is a *single process instruction* — **`Material Consumption`,
    Dynamic Dropdown, `Record Text Value`, `Solution Summary - Data Recording`** (and similar single-instruction
    blocks). **Authoring 2+ of the same collapsible block in a row makes the EBR collapse them into one table.** This
    is *how* a stack of references renders as the clean multi-row table drawn in the mock-up — so **build a multi-row
    table by stacking N collapsible blocks, not by authoring a bespoke table XStep**, and express per-cycle / per-day /
    per-material repetition the same way (no custom step). It complements rule 17: **hide-the-header** makes a stack
    *look* like one XStep; **collapse** makes a stack of the **same** collapsible block *become* one table. Requirement:
    the grouping's objects must all sit in a **single process instruction** — mixed-instruction groupings don't
    collapse. Worked mappings (AZ3): product-filter / bag / vent-filter tables = N× `Material Consumption`; effluent /
    pH-cond-temp results tables = N× `Solution Summary - Data Recording`; the attachment Yes/No fields = N× Dynamic
    Dropdown; skid / CIPDS / cassette ID lists = N× `Record Text Value`.
21. **A dropdown that activates/deactivates a section must live in the SAME XStep as the section it gates — this can
    force a bespoke New XStep even when the fields are all reusable.** In PI-PCS, conditional activation is driven by a
    valuated characteristic (the dropdown) evaluated against **sibling/child steps in the same XStep tree**. You
    **cannot** author a standalone "dropdown XStep" and have it reach *down* and activate/deactivate a *separate* XStep
    below it in the recipe. Consequence for decomposition: rule 17's "hide-the-header stack" is fine for a *sequential*
    group of independent blocks, but the moment one block is a **gate** (Yes/No or a branch decision) that turns
    another block in the group on/off, the gate **and everything it gates must be built as one XStep** — so that group
    can no longer be modelled as independent sibling references; it becomes a **single (often New) XStep** whose mock-up
    shows the gate dropdown immediately above the section it controls. Test while decomposing: *"does this dropdown only
    record a value (→ collapsible reference, rule 20), or does its value switch another field/section on or off (→ must
    be co-located, this rule)?"* Worked example (AZ3 VI §8 **Treatment Vessel Setup**): the *Use-Affinity-vessel? / Bag?
    / Tank? / vent-filter / filters-attached* dropdowns each activate the section beneath them, so although every field
    maps to `Select Vessel Type & Tare Weight` + `Material Consumption`, it is built as **one New XStep** with all gates
    inline — not a stack of sibling reuse references. (The mock-up renderer models a gate with a `gate:(label,options)`
    block that prints an "activates/deactivates the section below" hint above the gated block.) Same test flags any
    decision-with-branches step (temperature decision tree, dilution-required?, cassette re-use?, continue-DF?): decide
    per step whether the branch is heavy enough to warrant a bespoke gated mock-up or is a simple in-line Yes/No that a
    single reused decision block covers.
    **How it is wired (confirmed from the live `SMPL: EFS Additional Staging` XStep):** the gate is *not* a function
    module. The dropdown is a restricted CT04 characteristic (`ZSMPL_CHAR_YES_NO` = Yes/No) captured to a local value
    `LV_DROP`; the gated section carries setup **Commands** — `TABLE.ACTIVATE` / `TABLE.DEACTIVATE` (and, at grouping
    level, `PROC_INSTR.ACTIVATE` / `PROC_INSTR.DEACTIVATE`, plus `LOCK` / `UNLOCK`) — each with a **Formula trigger**
    evaluating the gate value: DEACTIVATE on `( LV_ACTIVE <> 1 AND IV_ACT_FLP <> 1 ) OR ( LV_ACTIVE = 1 AND IV_ACT_FLP
    = 1 ) OR ( LV_DROP = 2 )`, ACTIVATE on the complement (`LV_DROP = 2` ⇒ No ⇒ deactivate). `/SMPL/PPPI_FM_INITIAL_ACTIVE`
    is present but only sets the *base* initial-active state — it is not the gate. Because these Commands act on
    sibling/child nodes in the same XStep tree, the gate and gated section must live in one XStep (the structural reason
    for this rule). The mock-up still just shows the gate dropdown above its section; document the Commands + trigger in
    the functional spec's Configuration section, not on the mock-up.
22. **Every table/block that triggers a process message needs its own Performed By — as the table's final column.** If
    a block *fires an SAP process message* when executed — most commonly a **Goods Issue** (`Z_PICONS`, mvt 261) for
    consumed components, but also any other posting/message trigger — it **must carry a Performed By**, because the
    message posts under the operator who executed it. Model it as the **last column of that table** (`… , PB]`), not a
    separate signature line below the table — the signature is per row, so it stays with the material line that posts.
    Any table with the green **SAP Goods Issue** badge (material / bag / filter / component consumption) gets the
    trailing `Performed By*` column; tables that only record equipment IDs or reference data and post nothing (e.g. the
    Tank Information setup table) do **not** need one. Worked example (AZ3 VI §8): the Bag, Vent Filter and Product
    Filter tables each post a Goods Issue → each ends with a Performed By column; the Tank table posts nothing → no
    Performed By.
23. **No multi-select — split a "mark all that apply" field into separate Yes/No dropdowns.** SiMPL XSteps do **not**
    support a multi-select control. Any paper-BR field that says *"mark the applicable …"* / *"check all that apply"*
    (attachments present, filters attached, lines connected, etc.) must be modelled as **one Yes/No dropdown per
    option**, not a single multi-value picker. Worked examples (AZ3 VI §8): *"Mark filters attached when tare
    obtained: Product filter / Vent filter / No filters (bag)"* → three dropdowns (**Product Filter attached?**,
    **Vent Filter attached?**, **No filters — vessel is a bag?**), each Yes/No; the mixer-bag attachments
    (mixer drive / top base / magnetic clamp) → three Yes/No dropdowns likewise.
24. **Still draw a representative PI Sheet visual for a block-stack reuse — don't leave it text-only in the
    comparison doc.** A block-stack step (rule 17) is a REUSE, not a New object, so it needs no bespoke build — but
    when you present it in the EBR / crosswalk *for comparison against the paper record*, a text summary of "what it
    reuses" is hard to check against the old form. Render the assembled stack as an inline mock-up **and keep the
    REUSE labelling**: show the badge, the `Reuses:` line naming the constituent blocks, a caption stating it is a
    block stack (no new object), then the visual. Label each constituent block in the visual so the reader can map it
    back — table blocks use the green section header, fields blocks use a per-block sub-label (`bsub` in the renderer)
    reading e.g. *"SMPL: Equipment Select — pH / Conductivity Meter"*. This keeps "what it looks like on the PI Sheet"
    and "what it's built from" visible together. (AZ3 VI+C&D: all 17 block-stack R steps carry a `blocks=` mock-up
    rendered inline in both EBR PDFs.)
25. **A limit/rule the block *validates against* is a PARAMETER, not a new XStep — check before you split or
    branch.** Many "fields" a paper record shows are not separate recordable objects but **parameters** or **built-in
    validators** already inside a reused block, so adding them changes **nothing** in the stack or XStep count — you
    populate a parameter on the one instance. Verified canonical case: an acceptance **range (min/max)** on a numeric
    value is the `IV_MIN` / `IV_MAX` parameters of the existing **`SMPL: Record Numeric Value`** plus its built-in
    `/SMPL/PPPI_FM_MIN_MAX` validator (confirmed in DE1 100, §11 catalogue). So a range-checked value **stays one
    reused `Record Numeric Value`** — do **not** add an XStep, do **not** split into separate min/target/max/actual
    steps, and do **not** add a decision dropdown for the in/out-of-range branch (the validator's error handling does
    the branch; see the VI Temperature Check). In the mock-up, **do not render `IV_MIN`/`IV_MAX` as fields** — they are
    configured parameters, not things the operator sees as cells; state the range in the **instructions** (so the MBR
    author knows what to set on the step) and rely on the validator's **error messaging** to tell the operator why an
    entry is rejected. The mock-up shows just the single entry field. (Exception: a block *built to display targets* —
    `SMPL: Solution Summary - Data Recording` — does carry Min/Max Target columns; that is its native layout, so there
    the targets are shown.)
    Same logic for other built-ins: Yes/No (`PPPI_FM_YES_NO_VALID`), within-expiry date (`CHECK_CHAR_DATE`), material
    PN/batch (`PPPI_FM_VALI_MAT`), and the per-row **Performed By** on a goods-issue table (the `SIG_ADD_DB_CB`
    callback fires per completing row — not a new step). Decomposition test: *"is this a value the operator records, or
    a limit/rule the block validates against?"* — the latter is a parameter/validator on an existing step; the stack is
    unchanged.

---

## 5. The common reusable building-block library

These recur in essentially every bioprocess batch record and should almost always be **reused** (validate fit first):

- **Signatures** (Performed By / Witness/Check By) — native to every step.
- **Room/Equipment Assign** — equipment, scales, tanks, probes, freezers, autoclave, with calibration/steril expiry.
- **Component / Material Addition** (+ SAP goods issue, batch, expiry) — incl. *Weight/Volumetric Component Measurements*.
- **Calc blocks — pick by input count.** **2 inputs → `SMPL: Calc Three Columns`** (`Value1 [op] Value2 = Result`
  — e.g. Net = Gross − Tare, the depth-filter A÷B=C calcs); **3 inputs → `SMPL: Three Variable Calc`** (or the
  4-Variable extension for 4 vars / mixed `×`+`+`); **a ranged result → `SMPL: Calc Range Values`** (e.g. flux
  500/600/700). **There is no "Two Variable Calc" object** — a two-input calc *is* `Calc Three Columns` (Jason's
  correction on the AZ POC crosswalk).
- **Long Text Instructions** (the shell in DE2 903) — any instruction-only / sign-off step (verifications, line
  connections, installs, general notes). One shell, content authored in MBR.
- **Record Text / Numeric Value** — capture a single labelled value (an equipment ID, a reading).
- **pH Probe Calibration / DO Probe Calibration / Probe Info**.
- **Record Daily Bioreactor Conditions** / Sampling / **Viable Cell Density** / **Sample Submission**.
- **Offline-meter / effluent results** — a **range-validated variant of *Solution Summary - Data Recording***
  for pH / conductivity / temperature readings taken off an offline meter (equilibration, strip, storage,
  product effluent). Shape: a **Get Equipment** button → read-only **Equipment ID / Description** (the offline
  meter), one **column per measurement** each with an **adjacent read-only UoM output** column (pH, mS/cm, °C),
  the accept ranges stated in the instruction text, and a per-cycle or per-day index. **Keep every sibling
  results table the same variant** — they only differ by which measurements/ranges apply.
- **Incoming / Load Product Information** — a variant of ***Solution Summary - Data Recording*** capturing a
  starting-material vessel/bag: **tare + net weight**, a **concentration result (g/L, e.g. SoloVPE)**, and the
  **DLIMS project / sample numbers** it's reported under, one row per vessel. (Covers a paper "Affinity/VF Product
  Information" table — AZD0543 VI §7.5 / C&D §7.4.)
- **Confirmed DE1 100 reuse targets / building blocks** (verified via `shaper_find`, §6): `SMPL: Solution Summary -
  Data Recording` (results / concentration / pH-cond-temp / hold-time / incoming-product variants), `SMPL: Calc
  Three Columns` (2-input), `SMPL: Three Variable Calc` (3-input), `SMPL: Calc Range Values` (ranged),
  `SMPL: Equipment Select`, `SMPL: Record Text Value`, `SMPL: Record Numeric Value`, `SMPL: Material Consumption`,
  `SMPL: Component Goods Issue`, `SMPL: Additional Assembly` (Z_PICONS Goods Issue), `SMPL: Room/Equipment Assign`,
  `SMPL: Sampling Record` + `SMPL: Sample Submission Chart`, `SMPL: Non-Routine Sampling Record`,
  `SMPL: Yield Calculations`, `SMPL: Solution Final Storage`, `SXS: Text Instructions with Sign-off`
  (DE2 903: Long Text Instructions), `SXS: Phase Comments` (there is **no** clean "SMPL: Comments"),
  Display BOM Material Table, `SMPL: Mixing Time` (Product Mixing), weight pattern (`SMPL: Record Scale Weight`).
- **Filter Integrity Test**, **Centrifugation / Harvest Log**, **Transfer (Solution/Media)**, **Mixing**,
  **Timer (Begin/End/Summary)**, **Label Control & Reconciliation**, **Cleaning / Sanitization**,
  **Storage / Dispense**.
- **pH Adjustment (Acid/Base)**, **SIP of Sample Port / SIP-CIP Confirm / Equip SIP Verify**, **Sterility Dates**.

Genuinely **new** blocks are the process-specific ones (for Merck: Virus Seed Identification, Cell Bank ID,
MOI Calculation, Virus Seed Inoculation, Waste Kill, BEI Cyclization, Viral Inactivation, Neutralization,
Formulation, Bulk Dispense, Cold Storage, Pre-Inactivation/Thaw, single-use bag setup).

---

## 6. Sourcing data from SAP (MCP)

- **XSteps:** `shaper_find` (locate by name), `shaper_folder_tree` / `shaper_get_folder_contents` (browse the
  library), `shaper_get_version` shape=`snapshot` (full content — FM calls live at `node.instr.rows`; reference
  sub-steps named *Conditional Header* / *Optional Signature* are reference-only).
  > **Tool rename:** the XStep tool group was renamed **`xs_*` → `shaper_*`** in an SapFractal build. If a call
  > errors with *"Tool xs_find not found"* while `list_connections` still works, the server was updated — switch to
  > `shaper_*` (git-pull the SapFractal project if the deferred-tool list is stale, then re-search).
  > **Case gotcha (DE1 100):** case-insensitive `shaper_find` hits *"The function UPPER is unknown"* on this system.
  > Pass **`case_sensitive: true`** with exact-case terms (e.g. `"SMPL: Solution Summary"`). Use it to **confirm
  > every `reuses=` target actually exists** before calling a step a Reuse.
- **Systems:** `list_connections`. Connection names use **underscores** — `DE1_100` (main XStep library),
  `DE2_903` (sandbox/dev, where `TR - Long Text Instructions` lives), `QE2_100` (QA). `list_connections` works even
  when the `shaper_*` group is unavailable — use it (or a `run_query` count) to confirm the server is reachable.
- **FMs / DDIC:** `find_objects` → `get_source` (ABAP body & signature), `get_xml` (domain fixed values).
- **Tables:** `get_table_data` / `run_query` (e.g. TOBJ/TACTZ for auth objects, TADIR for object inventory).

---

## 7. How the mock-ups & EBR were generated (tooling)

- Mock-ups: an HTML/CSS card template rendered **HTML → PNG via headless Chrome**
  (`chrome --headless=new --screenshot --window-size=W,H`). One `image.png` per XStep folder.
- EBR / PI Sheet: all cards assembled into one HTML, rendered **HTML → PDF**
  (`chrome --headless --print-to-pdf`, A3 landscape page).
- Driven by a small data file (one dict per XStep: title, instructions, and either `cols` for tables,
  `form` for forms, a long-text body, or a `blocks` list for a composite/gated XStep — each block a `gate`
  (`… Required?` dropdown) + `head`/`gi` + `fields` or `cols`) + a phase plan for the EBR + an Old↔New crosswalk map.
- **A shared mock-up construct must be styled in BOTH renderers, or it renders broken in the EBR.** The standalone
  mock-up template and the EBR card assembler use **different CSS class conventions** for the same thing (standalone
  styles plain `table` / `.form`; the EBR styles `table.di` / `.xform`). When you add a **new** construct (e.g. the
  composite `blocks`), emit it under a **scoping wrapper** (`.mk`) and add `.mk`-scoped styles to **both**
  stylesheets — otherwise the standalone PNG looks fine while the EBR card collapses to **unstyled raw text**
  (tables with no grid, form fields with no boxes). Symptom seen this build: the §8.4 composite rendered perfectly
  as a PNG but showed as plain text in the EBR until the EBR CSS got the matching `.mk` rules. Always re-check the
  new construct **in the assembled EBR**, not just the standalone mock-up.
- Re-running the generator rebuilds everything, so wording/column/format changes are one-line edits.
- **Keep the EBR PDF closed when you rebuild.** Chrome `--print-to-pdf` **silently no-ops on a locked file**
  (exits 0, writes nothing) — an open PDF viewer strands you on a stale export while the HTML keeps updating,
  which reads as "my change didn't take." Use an **absolute** output path (a relative `--print-to-pdf` path can
  also silently fail to write), and after a rebuild confirm the PDF's modified-time actually advanced.
- Published mock-ups also go to the **PI Sheet Sandbox** as JSON — see §13.

---

## 8. Quick checklist for a new batch record

- [ ] Read the full record; capture sections + attachments + header fields (incl. front-matter §1-6).
- [ ] List the recurring data-capture patterns.
- [ ] `shaper_find`-search the whole library per pattern (`case_sensitive: true`); check for an existing client folder.
- [ ] Build the XStep list; tag each **R / V / N** (rule: only N/V get mock-ups); apply the FM scoping rule.
- [ ] **Decompose composites into a stack of existing blocks first** (rule 17) — assemble from `Material Consumption` /
      `Component Goods Issue` / `Record Text-Numeric Value` / `Equipment Select` / `Calc Three Columns` / `Calc Range
      Values` / dynamic dropdowns / Long Text, stacked under a hidden Conditional Header; reserve **N** for what no stack covers.
- [ ] **Build multi-row tables by stacking collapsible blocks** (rule 20) — 2+ `Material Consumption` / Dynamic Dropdown /
      `Record Text Value` / `Solution Summary - Data Recording` in a row collapse into one table; don't author a bespoke table XStep.
- [ ] **Name + verify each reuse target** in `DE1_100` (`shaper_find`) — no "to-be-confirmed" reuses. Pick the calc
      block by input count (2→Calc Three Columns, 3→Three Variable Calc, ranged→Calc Range Values).
- [ ] **Near-match → ask the client** (rule 18): a block matching except 1–2 fields → ask if a client-system variant
      exists (which system / no / not sure); batch these questions.
- [ ] **GI with no batch field** (rule 19): flag how the goods issue is sourced (usually the upstream PN/batch).
- [ ] Pick a **format per step** (Table / Form / Long Text / Composite-gated-blocks) using the §3 decision rule.
- [ ] **Sweep for constants** — every fixed/standard value becomes a read-only **defaulted output**, not an entry field.
- [ ] **Sweep for Goods-Issue points** (SAP-Consumption cells → `Z_PICONS` mvt 261) and **Label points** (SOP-0107056);
      confirm each is reflected in a step (rule 12).
- [ ] **"Needs-XStep vs separate-form" test** on anything that only names a sample / references an external form (rule 13).
- [ ] Enforce **one signature per table line**; computed fields read-only; component tables get SAP+batch+expiry.
- [ ] Build one mock-up per **N/V** XStep (R = reuse card, no mock-up).
- [ ] Build the **coverage crosswalk**; close every gap. Front-matter (BOM / Add'l Supplies / Solution Batches /
      Process Notes) gets XSteps too (rule 14).
- [ ] Assemble the **EBR / PI Sheet** — **NEW** (POC-style: N/V/R badges + XStep↔MPR crosswalk) and **New vs Old**
      (same cards + verbatim old-BR panels); export PDF + HTML.
- [ ] Emit the **RTM** (Step 6): section→XStep trace + streamlined reconciliation + Goods-Issue/Labels sheets; render PDF/HTML too.
- [ ] Validate reuse candidates by **opening the real XStep** — the **active/Released** version, not just the name.
- [ ] **Deep-review sweep:** every total/summary row, cross-record write-back, attachment sub-table, and extra
      in-table measurement is on a card — and sibling **"results" tables use a consistent variant**.
- [ ] Publish to the **PI Sheet Sandbox** (§13): computed columns typed `output`, dropdowns carry `options`,
      date+time split; read the record back to verify.

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

> **Downstream:** these mock-ups (and the functional specs) are the input to the **SapFractal XStep builder**
> (`Build Guide/XSTEP_BUILD_GUIDE.md` + `XSTEP_TOOLS.md`) that constructs the real SAP XStep. It **clones the
> `SMPL: AZ Template XStep`**, which already ships the **Conditional Header** (title + instructions block) and the
> **Optional Signature** block (**Performed By** + **Witnessed By**) — so a mock-up's header, instructions and
> footer witness signature are **template-supplied**, not custom-built; the builder adds "only the spec-specific
> instructions, usually one table." Column labels → `PPPI_INPUT_REQUEST` (≤30 chars, rule 11); dropdowns → CT04
> characteristics (rule 9c); goods issue → `Z_PICONS` / mvt 261 (rule 5).

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
- **Captured results feed downstream systems, so type them — don't free-text them.** A numeric result is a
  `PPPI_MATERIAL_QUANTITY`, a Yes/No / pass-fail is a **CT04 characteristic**, a date is a date domain, a UoM is
  `PPPI_UNIT_OF_MEASURE`. The reason is downstream: these values flow to the SAP **Batch Release Hub** (Batch
  Record Review / deviation / usage-decision / serialization checks), the process order's **inspection lot /
  usage decision**, and **batch classification** — all of which auto-evaluate only on *typed* data, which is also
  what makes **review-by-exception** possible. Our developers already build this way; it's captured here as the
  context behind picking a field's type. (It does **not** change what a per-XStep functional spec documents — the
  spec stays scoped to the individual XStep as built in CMXSV; see the Functional Spec guide §5.)
- **The dependency engine = electronic conditional logic:** the paper record's *"if X, proceed / N/A the rest"*
  branching is enforced by **setup Commands with Formula triggers** — `TABLE.ACTIVATE`/`DEACTIVATE` and
  `PROC_INSTR.ACTIVATE`/`DEACTIVATE` (+`LOCK`/`UNLOCK`) whose trigger evaluates a gate dropdown's `LV_DROP` value
  (confirmed on `SMPL: EFS Additional Staging`); `INITIAL_ACTIVE` + `MBR_DEP_CHECK_ACTIVE` set the base active-state /
  perform-verify gating but are **not** the dropdown gate itself. See the Mockups guide rule 21.
- **Good-practice patterns to reuse:** dual-mode FMs (write vs read via a flag), ENQUEUE/DEQUEUE around writes,
  validators on every input, and a custom `ZTC_*` table layer for EBR-captured data (queryable/reportable).

**Verified FM catalogue — DE1_100 `SiMPL XStep Library - Process Manu.` (read the real blocks with `shaper_get_version shape:"snapshot"`; parse FUNC/IN/SIG rows for `PPPI_FUNCTION_NAME` / `PPPI_VALIDATION_FUNCTION` + `PPPI_EVENT`).** Namespaces: `/SMPL/PPPI_FM_*` (core), `/SMPL/ELB_FM_*` (equipment), `/SMPL/MBR_DEP_*` (deployment), `ZSMPL_FM_*` (AZ custom, FUGR `ZAI_XSTEP_FMG`). Every block also carries `PPPI_FM_INITIAL_ACTIVE` (activation) + `MBR_DEP_CHECK_ACTIVE` (save) + signature FMs — assume them, don't draw them.

| Building block | Validation FM (on column) | Key event-handler FM(s) | Mock-up implication |
|---|---|---|---|
| Record Numeric Value | `/SMPL/PPPI_FM_MIN_MAX` | `SET_FLOAT_VALUE` | Range-checked numeric = plain entry + Min/Max targets; the FM enforces range + error handling → **no decision dropdown for in/out-of-range** (this is why the VI Temperature Check dropped its dropdown). |
| Equipment Select | `/SMPL/ELB_FM_GET_ASS_EQ_VALID` | `ZSMPL_FM_GET_ASSIGNED_EQUI_EBR` (Get button) | "Get [Type]" button auto-fills ID / Description / **Calibration Due Date**. |
| Material Consumption / Component Goods Issue | `/SMPL/PPPI_FM_VALI_MAT` | `PPPI_FM_GI_SETUP` + `GI_SETUP_LINE` (`Z_PICONS`, mvt 261); `ZSMPL_FM_GET_MAT_ITEMS_EBR` | Green **SAP Goods Issue** badge + **Performed By** column (rule 22); PN/batch is validated, not free-text. |
| Calc Three Columns / Three Variable / Range Values | `/SMPL/PPPI_FM_CALC_VALIDATE` | `CALC_SETUP` / `RANGE_CALC_SETUP` / `INPUT_VALUE` / `OUTPUT_VALUE` | Inputs entered, result is a computed read-only cell (`=` prefix); ranges give Min/Target/Max. |
| Dropdown (Yes/No) Check & Val. | `/SMPL/PPPI_FM_YES_NO_VALID` | — | CT04-restricted dropdown; one dropdown per option (no multi-select, rule 23). |
| Timer (Begin/End/Summary, Start-End Process) | — | `GET_PROC_STRT_TM` / `STR_PROC_STRT_TM` / `GET_PROC_TM` / `CLEAR_PROC_TM` | Record buttons stamp start/end; duration is computed. |
| Date fields (expiry, storage) | `/SMPL/PPPI_FM_CHECK_CHAR_DATE` | — | Dates are validated (within-expiry) — a date domain, not free-text. |
| Any signed step | `/SMPL/PPPI_FM_SIG_VALIDATION`, `VALI_SUPE_SIG` | `SIG_ADD_DB_CB` / `SIG_POPULATE_CB` | Signature validated + persisted; supervisor sign-off is a distinct validator. |
| Vessel weigh / tables | `ZSMPL_FM_GET_MAT_ITEMS_EBR` | `ZSMPL_FM_WEIGHT_TRANSFER`, `SET_LINE_IDX` / `ZSMPL_FM_INCREMENT_TABLE_LINE` (`TABLE.LINE_ADDED`) | Net = Gross − Tare carried by an FM; table rows auto-index. |

Lifecycle events seen: `DOCUMENT.GENERATED` (instantiate), `PARAMETER_CHANGED` (recalc / re-activate), `DOCUMENT.SAVING` (dependency check), `PROC_INSTR.COMPLETING` (persist), `TABLE.LINE_ADDING/ADDED`, `TABLE_LINE.COMPLETING`, `TABLE_LINE.ACTIVATED`.

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

---

## 13. Publishing mock-ups to the PI Sheet Sandbox (the JSON target)

Once a mock-up is right, it's published to the **PI Sheet Sandbox** — a hosted PI-sheet representation at
`https://vantage.iss-i.ca/api/xsteps/`. This is a **concrete JSON form of the mock-up**, and the most literal
downstream target we have. (It is distinct from the SapFractal SAP builder in §11 / `XSTEP_BUILD_GUIDE.md`;
confirm with the team whether the Sandbox *feeds* that builder or is a parallel review surface.) One mock-up =
one Sandbox record.

### API contract

Auth is a bearer token: `Authorization: Bearer <api key>`.

| Verb | Endpoint | Purpose |
|---|---|---|
| `GET`   | `/api/xsteps/` | List every record — grab one as a live schema reference. |
| `GET`   | `/api/xsteps/{id}/` | Read one record. |
| `POST`  | `/api/xsteps/` | Create (returns `201` + the new `id`). |
| `PATCH` | `/api/xsteps/{id}/` | Update in place. **`PUT` is NOT supported (returns 404).** |

Always **read the record back** after a write — it confirms the structure persisted and that UTF-8 survived
(em dashes, °, ≤, etc. round-trip; a mangled character shows up immediately).

### Record shape

```jsonc
{
  "title", "description", "category": "custom", "tags": [],
  "instructions": [{ "id", "name", "color" }],   // instruction "groups" = the step's section(s)
  "parameters": [],
  "elements": [                                    // ordered UI elements
    { "id", "type", "label", "order", "config", "instrId", "instrName", "instrIndex" }
  ]
}
```

### Element types — what each mock-up construct becomes

| Mock-up construct | Sandbox element `type` |
|---|---|
| Instruction / conditional-header text | `output_long_text` (`config.content`) |
| Data-Input table | `ctrl_table` (`config.dynamic` = Add Row, `config.rows`, `config.columns[]`) |
| Standalone entry field | `entry_char_string` / `entry_numeric` / `entry_date` / `entry_time` |
| Standalone read-only / computed field | `output_char_string` / `output_numeric` / `output_date` / `output_time` |
| Performed / Witnessed signature | `entry_parameter` (or `entry_signature`) |
| FM / Get button (standalone) | `ctrl_function_call` |
| Goods issue | `ctrl_process_message` |
| Calculation | `ctrl_calculation` |

### Table column types (`ctrl_table.config.columns[i]`)

This is where the mock-up's column prefixes land — input / output / dropdown / FM button:

| Mock-up column | Sandbox column |
|---|---|
| Operator entry (plain) | `{ "type": "input", "header": "…" }` |
| Computed / read-only (`=`-prefixed) | `{ "type": "output", "header": "…" }` |
| Dropdown (`%`-prefixed) | `{ "type": "dropdown", "header": "…", "options": [ … ] }` |
| FM / Get button (`@BTN:` / `Get …`) | `{ "type": "function", "header": "…", "buttonLabel": "…" }` |
| No `type` given | **defaults to `input`** |

### Gotchas & conventions

- **Type your computed columns `output`.** An untyped column defaults to `input` and renders as an entry field —
  computed columns (Material Description, Exp. Date, expiry) must be explicitly `output`, or the operator is
  asked to type a value the system derives. (This is the Sandbox mirror of rule 9a and rule 4c — it bit us on
  the first upload.)
- **No combined date-time type** — a "Date & Time" is two elements (`*_date` + `*_time`); see rule 3.
- **Dropdowns carry their `options[]` inline** — the same value list you name for the CT04 characteristic
  (rule 9c).
- **The Sandbox is the source of truth once uploaded.** You can `GET` the record and **re-render the PNG
  mock-up from it**, keeping the mock-up folder and the Sandbox in sync — drive the renderer off the JSON
  (`output`/`dropdown` column types → read-only/dropdown styling; `output_*` elements → grey read-only fields).
