# XStep Build Guide

The single source-of-truth for building SAP PI-PCS xsteps with the SapFractal MCP toolkit. Read top to bottom. Pair this guide with:
- `XSTEP_TOOLS.md` — per-tool reference (parameter shapes, examples)
- `XSTEP_API.md` — HTTP API reference for `/api/xs/*` endpoints
- the functional spec for the xstep you're building

Companion sources in the repo (not required reading, but worth knowing they exist):
- `xstepBuilder/xsteps/*/build_plan.md` — completed build plans
- `tool_types/xsteps/exploration/` — the deep-dives this guide condenses

---

## 1. Mental model

An xstep is a hierarchical tree of nodes stored in SAP's cmxsvn repository. The PI-PCS framework renders it into a PI sheet at runtime; an operator fills it in; the framework collects signatures, fires process messages, and writes back to MES / goods movements.

**Nodes have NIDs** — opaque 22-char base64-like identifiers (`fJVsUCCY7z6...`). Key NIDs you track:

- `item_id` — repository handle for the xstep (CMX_XSR_DB_ITEM.ITEM_ID)
- `version_id` — the editable version
- `root_nid` — root T-node of the tree (CMX_XSR_DB_VERS.ROOT_ID)
- `step_nid` — inner S-step you're attaching things to
- `instr_nid` — instruction node (for updates)

**NIDs are session-transient** — they only match within one SAP session. After any save, re-fetch via `xs_list_children`.

**Node types (ntype):**
- `T` — root
- `S` — step
- `R` — reference (to another xstep — Conditional Header, Optional Signature, etc.)
- `I` — instruction
- `P` — parameter
- `D` — destination
- `G` — generation hook

**Parameters live at scopes:**
- `ptype="L"` — local (step scope, most common)
- `ptype="I"` — input (MBR-fed)
- `ptype="O"` — output
- `ptype="E"` — exchange

Each parameter has a `domain` (e.g. `PPPI_MATERIAL`), an `is_table` flag (column vector vs single value), `state` (`S`=set, blank=unvaluated), `pmode` (`F`=fixed, `A`=auto, blank=none), and an optional `value`.

**Instructions** are children of steps. Most common kinds:
- Input requests (single field)
- Tables (multi-column repeated input) — most complex; see Pattern 1
- Process messages
- Function calls
- Conditional rules
- Calculations
- Groupings (header sections)

**Table columns are typed primitives**: `input`, `output`, `function_call`, `signature`, `conditional_rule`, `process_message`, `button`, `raw`. Order matters — framework events fire in column position.

---

## 2. Cardinal rules

1. **Look up, never guess.** Any time you'd type a domain name, characteristic name, EQTYP code, FM parameter name, or any other SAP identifier from memory — run the appropriate `xs_*` or `find_objects` / `get_table_data` lookup first. Wrong codes usually produce silent incorrect behavior, not errors.
2. **Never pattern-match on short SAP codes.** EQTYP=`W` is NOT "Welder" — it's "Workstation". Single-character SAP codes are rarely mnemonic. Always query the text table.
3. **Check folder paths before copying from a reference.** "Inactive XSteps" / "Archived" / "Old" folders contain drift. When two references disagree, the active-folder one is canonical.
4. **Flag conflicting search results.** When `xs_search_instructions` returns two shapes for the same FM/pattern, surface the discrepancy to the user.
5. **Read `xs_instruction_recipes` before building.** Hard-won patterns can't be reconstructed from search alone.
6. **Safe edit zone is the main step S subtree.** NEVER touch T-root params, the Conditional Header R, or the Optional Signature R. They are template + MBR territory.
7. **Don't touch `Setup Functions` or `Activate` instructions.** Load-bearing for cmxsvn's frame setup; deleting them breaks Simulate.

If you only remember rule #1, you'll prevent the majority of mistakes.

---

## 3. The build flow (20 lines)

1. **Clone** a template via `xs_clone_xstep`. The current iSSi canonical template is `SMPL: AZ Template XStep` (item `fJVsUCCY7z6KzR4szUfXzG` on DE2_903 in Max Parker XA Folder). Supersedes the older `SMPLXA: XStep Template`.
2. **Get NIDs** with `xs_list_children(item_id)` — captures `root_nid` (T) and the main step S NID (the S child directly under T, between the two R-references).
3. **Rename** the cloned step: `xs_rename_item` (folder label) + `xs_update_node_attrs` on root_nid (xstep title) + `xs_update_node_attrs` on main step S (step title). Easy to miss — the cloned step retains the template's literal `<XStep Name>` text and that propagates into operator-visible labels.
4. **Add params first** via `xs_add_parameters` — ONE batched call per owner (cross-param wipe makes batching mandatory; see §6). `is_table:true` for every column-backing var. Names ≤10 chars (SAP truncates silently).
5. **Set defaults inline** during param creation: `value:"..."` AND `state:"S"` AND `pmode:"F"`. All three or the param renders as "None" in the Valuation tab and runtime treats it as unvaluated.
6. **Use typed domains.** `PPPI_UNIT_OF_MEASURE` (not `PPPI_SHORT_TEXT`) for UoMs. `PPPI_MATERIAL_QUANTITY` for quantities. See domain swap table §7.
7. **Tables** via `xs_add_table_instruction` with typed columns.
8. **Multi-row header sections** also via `xs_add_table_instruction(repeated:false)` — NOT N separate `xs_add_instruction` calls.
9. **Apply canonical patterns** for row-sync, signature, validation FMs, equipment lookup — see §5.
10. **Apply iteration patterns** appropriate to the spec — typed domains, Z_PICONS, sig-carries-PMSG, sign-and-persist triplet, LAV_DEST — see §7.
11. **Verify** with `xs_check_semantic(item_id)` — should return 0 errors. A single info message reporting `visit=N pii=M` is normal.
12. **Manual cmxsvn test** — Simulate from the root must work.

**Inheritance writeback tip (for steps 9–10).** When you need to modify a template-inherited instruction (most often `Setup Functions` — prepending a `ZSMPL_FM_CUSTOM_INDEX` call, for example), the writer takes a full field array via SET_CONTENT. Don't naively concatenate your new fields with the array `xs_get_instruction` returned: if the read result includes `formula_handles[]`, those positions carry 22-char CMX NIDs that point to G-node formula expressions, not formula text. Round-tripping them as literals corrupts the formula. Substitute inline expressions before writing — for Setup Functions: DEACTIVATE → `LV_ACTIVE <> 1`, ACTIVATE → `LV_ACTIVE = 1`, LOCK → `EV_LOCK = 1`, UNLOCK → `EV_LOCK <> 1`. The write tools refuse NID-shaped values up front (since 2026-06-02) with `error: "NID_SHAPED_FORMULA_VALUES"`, but it's faster to substitute proactively when you see `formula_handles[]` in the read.

That's it. Patterns and pitfalls below.

---

## 3.5 Decision defaults

Questions the user has answered the same way across enough builds that they should now be defaults, not questions. **Apply silently** unless the spec or an existing artifact explicitly contradicts. Surface only the contradiction.

1. **Rename the cloned step to `SMPL: <Title>` (colon-space form).** Use `xs_rename_item` (folder label) + `xs_update_node_attrs` on root_nid (xstep title) + `xs_update_node_attrs` on main step S (step title). Idempotent. Don't ask.

2. **Never configure the wrapping Optional Signature R or its inner Witnessed By S step.** Template + MBR overlay own them. This includes `IV_HEADER`, `IV_SIGN`, `IV_LOCK`, `IV_TAR_*` on those nodes. See [[template_signature_handoff]] memory. Skip silently.

3. **Always include the full TABLE.DEACTIVATE / TABLE.ACTIVATE / TABLE.LOCK / TABLE.UNLOCK quartet on signed tables.** Do NOT drop any of them. Earlier builds (Total Medium Addition, EFS Exhaust Filter Info) emitted only DEACTIVATE or only DEACT+ACT — that was wrong; the quartet is load-bearing. Standard inline formulas: DEACTIVATE `LV_ACTIVE <> 1`, ACTIVATE `LV_ACTIVE = 1`, LOCK `EV_LOCK = 1`, UNLOCK `EV_LOCK <> 1`. Same shape as the PROC_INSTR-level quartet in Setup Functions.

4. **Hardcode the PI_CONS / Z_PICONS qty when the spec gives a literal value** (e.g. "always 1 EA"). No backing variable. Don't ask whether to add `LV_QTY` for it.

5. **Substitute the nearest existing CABN characteristic when a spec-named one doesn't exist.** Common examples: `ZSMPL_CHAR_POS_NEG` → `ZSMPL_CHAR_PASSED_NOT_PASSED`; `ZSMPL_CHAR_PASS_FAIL` → same; `ZSMPL_CHAR_YES_NO_DROPDOWN` → `ZSMPL_AZ_CHAR_YES_NO`. Flag the substitution in the build plan; do **not** pause the build unless the spec needs a wholly novel enumeration with no near-neighbor.

6. **Match the existing skeleton's variable prefix; do not rename mid-build.** If the template's `Activate` instruction already binds `LV_ACTIVE`, keep the LV_*; don't promote to LT_* even when adding new tabular columns. New columns get the right prefix per §4 (`LT_*` for `is_table=true`); existing wiring stays.

7. **Confirm cross-table master/follower direction from the spec wording, not from layout order.** "First record A, then submit B for review" means A is the master regardless of which appears on top of the PNG.

8. **Before asking a binding/event/FM-choice question — `xs_search_instructions` first.** Specifically:
   - "Which row-sync FM should I use?" → search `PPPI_FUNCTION_NAME` for the candidates against a production two-table xstep.
   - "Which equipment type code (`Q` vs `M` etc.)?" → grep one existing button binding on a similar xstep.
   - "Which event should this FM fire on?" → search the FM's name; copy the production event.
   - "Which characteristic should I use for X?" → check the AZ Template's existing usage first.

   The high-frequency anti-pattern in this repo's build plans is asking the user when the answer is one search call away.

These defaults supersede earlier sections where they conflict. If you find yourself drafting a clarifying question to the user, run the relevant rule above mentally first.

---

## 4. Naming conventions

Verified against ~3M live params on DE2_903:

| Prefix | Use | Production count |
|---|---|---|
| `LV_*` | local **scalar** (`is_table=false`) | 2.1M scalar / 250K tabular |
| `LT_*` | local **tabular** (`is_table=true`) | 640K tabular / 20K scalar |
| `LAV_*` | local accessible (cross-phase, framework-supplied: LAV_ORDER, LAV_PHASE, LAV_CRID, LAV_PLANT, LAV_DEST) | — |
| `IV_*` | MBR-fed inputs (`ptype:"I"`) | — |
| `OV_*` | outputs back to MBR (`ptype:"O"`) | — |

**Rule of thumb:** `is_table=true` → use `LT_`; `is_table=false` → use `LV_`. The minority crossover (`LV_*` + `is_table=true`) is functional but confuses reviewers.

**Spec-vs-production naming**: Specs occasionally write `LAC_CRID`, `LAC_BATCH` — these are typos. Production uses `LAV_*`. Match production; flag the discrepancy.

---

## 5. Canonical patterns

### 5.1 Cross-table row sync (master / follower) — canonical DE1 pattern

Two tables on the same step where the operator adds rows to a master table and the follower table's data columns track the master per-row. This is the pattern used by DE1's `SMPL: Bag Replacement Weight` (`AZ Phase 2` folder) — the canonical reference for this family of xsteps.

The pattern uses **three** building blocks, distributed across **three** locations:

1. **`ZSMPL_FM_CUSTOM_INDEX`** in Setup Functions (step-level) — keeps both tables' line counters synchronized.
2. **`ZSMPL_FM_INCREMENT_TABLE_LINE`** on the master table — advances the master's line counter as rows are added.
3. **`ZSMPL_FM_TRANSFER_LINE_ITEMS`** on the follower table, fired on **four events** — pulls master row data into the follower and assigns the follower's row index.

**Setup Functions (step-level, NOT inside any table):**

```
function_call ZSMPL_FM_CUSTOM_INDEX
  event: PARAMETER_CHANGED
  bindings:
    - changing CH_INDEX1 ↔ LV_LINENO1 (optional)
    - changing CH_INDEX2 ↔ LV_LINENO2 (optional)
```

Setup Functions is a non-table grouping (no `PPPI_DATA_REQUEST_TYPE` header). One CUSTOM_INDEX call covers BOTH tables' counters — don't duplicate this per-table.

**Master table — columns in structural order:**

```
function_call ZSMPL_FM_INCREMENT_TABLE_LINE
  event: TABLE.LINE_ADDING          ← before-commit, so the follower can react in lockstep
  bindings:
    - in IV_FLAG = "X" (optional)
    - in IV_ORDER ← LAV_ORDER
    - in IV_CRID ← LAV_CRID
    - in IV_PHASE ← LAV_PHASE
    - in IV_STEP_INDEX ← STEP_INDEX (float)
    - in IV_KEYWORD = "<sync_group_name>"     ← constant; scope key
    - in IV_INDEX ← LV_LINENO1 (optional)      ← INPUT only, not an EV output

output "#"
  variable: LV_LINENO1

[ ... data columns ... ]
```

The master FM treats IV_INDEX as an **input** — the counter advances on its own; you don't read an EV output here.

**Follower table — columns in structural order:**

```
function_call ZSMPL_FM_TRANSFER_LINE_ITEMS   ← fires FOUR times with identical bindings
  event: DOCUMENT.GENERATED                   ← (1) initial population at load
  bindings: <see below>

function_call ZSMPL_FM_TRANSFER_LINE_ITEMS
  event: TABLE.LINE_ADDED                     ← (2) populate per new follower row
  bindings: <same>

function_call ZSMPL_FM_TRANSFER_LINE_ITEMS
  event: PARAMETER_CHANGED                    ← (3) re-sync when master values change
  bindings: <same>

function_call ZSMPL_FM_TRANSFER_LINE_ITEMS
  event: TABLE_LINE.COMPLETING                ← (4) finalize on row commit
  bindings: <same>

conditional_rule
  command: TABLE.ADD_LINE
  action: HIDE
  event: DOCUMENT.GENERATED                   ← pre-allocates one hidden row

output "#"
  variable: LV_LINENO2                        ← populated by TRANSFER's EX_PLANT output (see binding)

[ ... data columns sourced from LT_TR_* via TRANSFER outputs ... ]
```

Each TRANSFER_LINE_ITEMS row has the same binding set — the four instances differ only in `PPPI_EVENT`:

```
bindings:
  - in IM_BATCH ← LV_BATCH
  - in IM_MATERIAL ← LV_PARTNO
  - in IM_DATE ← LV_DATE (date)
  - in IM_TIME ← LV_TIME (time)
  - in IM_PHASE ← LAV_PHASE
  - in IM_QTY ← LV_QTY (float, optional)
  - out EX_PROCESS_ORDER → LT_TR_ORD
  - out EX_MATERIAL → LT_TR_MAT
  - out EX_BATCH → LT_TR_BAT
  - out EX_UOM → LT_TR_UOM
  - out EX_QTY → LT_TR_QTY (float)
  - out EX_PHASE → LT_TR_PHA
  - out EX_DATE → LT_TR_DAT (date)
  - out EX_TIME → LT_TR_TIM (time)
  - in IM_PROCESS_ORDER ← LAV_ORDER
  - in IM_UOM ← LV_UOM1
  - out EX_PLANT → LV_LINENO2                 ← naming is misleading — this is the row-index slot
```

**Critical**:
- CUSTOM_INDEX lives in **Setup Functions** at the step level, NOT inside either table. It synchronizes both line-counter variables (LV_LINENO1, LV_LINENO2) on `PARAMETER_CHANGED`.
- `EX_PLANT` is the customer FM's row-index output despite the misleading name. Bind it to the follower's `#` variable — that's how the follower's row number gets assigned.
- Fire TRANSFER on **all four events** — each one covers a different lifecycle phase. Missing one leaves stale data in the follower under that phase.
- `IV_KEYWORD` is the cross-xstep counter scope key. Don't reuse across xsteps that could run on the same plant+order+phase — counter collisions.

**Drift pattern you may see in DE2 prod (avoid for new builds):** Some DE2-evolved versions use `ZSMPL_FM_SET_LINE_INDEX` + `ZSMPL_FM_INCREMENT_TABLE_LINE` with `EV_INDEX_T1` / `EV_INDEX_T2` outputs, distributing the row-index logic across both tables instead of consolidating in Setup Functions. This is drift introduced during DE2 cloning — DE1's `AZ Phase 2` xsteps don't use it. When verifying a build or rebuilding from a DE2 copy, **compare against the DE1 original** before assuming the DE2 shape is correct (see also: `de1-canonical-for-az-phase2` memory).

### 5.2 Per-row signature with audit

```
[ ... data columns ... ]

[ invisible function_call SET_LINE_INDEX / INCREMENT_TABLE_LINE rows if any ]

signature                                         ← ALWAYS LAST column in the row
  variable: LV_PERFORMED_BY
  strategy: "SAPPOCSS"  (or "SS000201" for "Done By")
  label: "Performed By"
  validation:
    fm: ZEBR_XSTEP_SIG_VALIDATION
    validated_value_param: IM_USERID
    bindings: [step-context: IV_HEADER, STEP_INDEX, LAV_CRID, LAV_PHASE, LAV_ORDER, SIMPL_UUID, LAV_PLANT]
```

**Critical**:
- Signature column **must always be last** in the table row, even after invisible function-call columns. FMs that fire on `TABLE_LINE.COMPLETING` belong on the SIG row itself (via `bindings`), not in trailing columns. A function-call after SIG breaks runtime ordering.
- The signature column inside a table can bind to step-scoped scalars (`IV_HEADER`, `LAV_*`, etc.) — they don't need to be `is_table=true`.
- For sign-and-persist, the SIG row also carries the process-message bindings + sign-time FM triplet — see §7.3 & §7.4.

### 5.3 Equipment picker (Get Welder / Get Sealer / Get Filter Tester)

```
function_call /SMPL/ELB_FM_GET_ASSIGNED_EQUI
  button_label: "Get <equipment_name>"
  bindings:
    - in IM_ORDER ← LAV_ORDER
    - in IM_EQUIP_TYPE = "<EQTYP>"   ← M for welders/sealers, Q for testers
    - out EX_EQUI → LV_<EQ>_ID
    - out EX_EQUI_TXT → LV_<EQ>_DESC

output "<Equipment> ID"        variable: LV_<EQ>_ID
output "<Equipment> Descr"     variable: LV_<EQ>_DESC
```

**EQTYP codes** (T370U master): A=Additional, B=Scales/Balances, D=Printers, F=Fridges/Freezers, G=GG, L=Lab, **M=Machines** (welders/sealers), P=PRT, **Q=Test/measurement** (filter testers), R=Rooms, S=Customer, W=Workstation, X=Equipment Services. There is no welder/sealer/tester-specific category — pick the broadest fitting standard.

### 5.4 Material / batch validation (Part No. + Batch input columns)

```
input "Part No"
  variable: LV_PARTNO   domain: PPPI_SHORT_TEXT
  validation:
    fm: ZSMPL_FM_GET_MAT_DETAIL
    validated_value_param: IM_MATNR
    bindings:
      - in IM_MATNR ← LV_PARTNO   ← framework substitutes 'X' sentinel automatically
      - out EX_MAT_DESC → LV_PARTDESC

output "Description"   variable: LV_PARTDESC

input "Batch"
  variable: LV_BATCH    domain: PPPI_SHORT_TEXT
  validation:
    fm: ZSMPL_FM_GET_EXPIRY_DATE
    validated_value_param: IM_BATCH
    bindings:
      - in IM_BATCH ← LV_BATCH
      - in IM_MATNR ← LV_PARTNO   ← required: validates batch belongs to the entered material
      - out EX_EXP_DATE → LV_EXPDT (var_kind: "date")

output "Expiry Date"   variable: LV_EXPDT
```

### 5.5 Get current date/time button

```
function_call /SMPL/PPPI_FM_GET_DATE_TIME
  button_label: "Get Date" (or "Get Time")
  bindings:
    - out EV_DATE_DEFAULT → LV_DATE (var_kind: "date")
    - out EV_TIME → LV_TIME (var_kind: "time")
```

Alternative: `GET_SYSTEM_TIME_REMOTE` (uses `L_DATE` / `L_TIME` outputs).

### 5.6 Goods Issue process message

The customer renamed `ZPICONS` → **`Z_PICONS`** (underscore). Use the new name on new builds.

Every goods-movement message needs **`ZSMPL_CHAR_MOVEMENT_TYPE`**:
- `261` — goods issue for order
- `262` — reverse GI for order
- `311` — transfer posting

In v3+ builds, the PMSG is **folded into the SIG row** (see §7.3), not a separate process_message row.

### 5.7 Conditional table activation/deactivation

Signed tables get the **full four-CMD state machine**, same shape as the PROC_INSTR quartet in Setup Functions. Don't drop any of them — earlier builds did and that's why some old build plans look incomplete.

```
conditional_rule
  command: TABLE.DEACTIVATE
  formula: LV_ACTIVE <> 1       ← UNQUOTED literal (see §6 formula syntax)

conditional_rule
  command: TABLE.ACTIVATE
  formula: LV_ACTIVE = 1

conditional_rule
  command: TABLE.LOCK
  formula: EV_LOCK = 1

conditional_rule
  command: TABLE.UNLOCK
  formula: EV_LOCK <> 1
```

These pair on the **table instruction itself** (NOT its columns). Place them inside the table's `columns[]` array alongside the SIG row.

Driver-variable substitutions:
- `LV_ACTIVE` is the standard activation gate; swap in your specific dropdown variable (e.g. `LV_TUBREQ`, `LV_ACTIVE2`) when the activation is driven by a spec-defined dropdown. The activate/deactivate inverse pair stays.
- `EV_LOCK` is the lock state from the surrounding step's lock machinery — usually inherited from the AZ template. Don't rebind it unless a different lock source is in scope.

### 5.8 Range validation formula (`PPPI_LONG_FORMULA`)

The `PPPI_LONG_FORMULA` field on an input column holds a single-statement expression evaluated by the cmxsvn framework. Two roles:
- **Validation** on an input column — formula must evaluate true for the input to be accepted. False fires a deviation popup.
- **Calculation** on an output column — formula computes the value displayed in the output cell from other column / xstep variables.

**Syntax:**
- Infix math: `+ - * /`. Infix compare: `< > = <= >= <>` (use `=` for equality, not `==`).
- Logical: `AND`, `OR` (uppercase, plain word — not symbols).
- `X` = the current parameter being validated/calculated. References to other params use their plain names (e.g. `IV_TMP_MIN`, `LT_VCD`).
- String literals are not commonly supported — use a numeric-coded characteristic for Yes/No outputs and let the characteristic's description render the human label.

**Canonical range-validation pattern** (in-table numeric column bounded by MBR-fed min/max):

```
PPPI_INPUT_REQUEST   = "Temp (°C)"
PPPI_VARIABLE        = LT_TEMP
PPPI_REQUESTED_VALUE = ZSMPL_CHAR_NUMERIC
PPPI_LONG_FORMULA    = IV_TMP_MAX > X AND X > IV_TMP_MIN     ← strict (exact bounds rejected)
```

Strict inequalities — values exactly at the bound are rejected. Use `>=` / `<=` for inclusive. Pair with two `PTYPE='I'` parameters (`IV_<COL>_MIN`, `IV_<COL>_MAX`) on the owning step; the MBR overlay sets the recipe-specific bounds. Names cap at 10 chars — 3-char abbreviation + `_MIN`/`_MAX` fits.

**Critical**: any IV param referenced by a formula needs to exist at BOTH the outer T-root AND the inner S-step with `PMODE='R'` on the inner copy. Without it the formula reads `IV_TMP_MIN`/`IV_TMP_MAX` as empty even when MBR populates the outer. See §7.10.

**Calculation pattern for Yes/No outputs** — use `ZSMPL_CHAR_YES_NO` (1=Yes, 2=No) and compute the numeric code via boolean-arithmetic:

```
PPPI_OUTPUT_TEXT     = "Is Transfer Req?"
PPPI_OUTPUT_VARIABLE = LT_TRANS
PPPI_LONG_FORMULA    = (LT_VCD >= 3.1) * 1 + (LT_VCD < 3.1) * 2
```

If the formula path silently fails or the column doesn't update at runtime, fall back to an FM call bound to `PPPI_EVENT = PARAMETER_CHANGED` on the input column that drives the output.

### 5.9 In-table row index parameter (`#` column)

For a `1, 2, 3, …` row counter in a single REPEATED table (no cross-table sync — that's §5.1):

1. **Backing parameter** — declare `is_table=true`, `PTYPE='L'`, **`domain="ZSMPL_CHAR_GI_INITIALS"`** (NOT `PPPI_MATERIAL_QUANTITY` — see gotcha in §6), `value="1"` default.
2. **Row-sync FM call** on `TABLE.LINE_ADDED` — invisible (`button_label` omitted), `changing` binding from the FM's index param to the LT_ variable.
3. **Output column** rendering the var: `PPPI_OUTPUT_TEXT="#"` + `PPPI_OUTPUT_VARIABLE=LT_INDEX1`.

```json
// param
{ "name": "LT_INDEX1", "domain": "ZSMPL_CHAR_GI_INITIALS",
  "ptype": "L", "is_table": true, "value": "1", "stext": "Row #" }

// function_call column (no button_label = invisible)
{ "kind": "function_call", "fm": "/SMPL/PPPI_FM_SET_LINE_IDX",
  "event": "TABLE.LINE_ADDED",
  "bindings": [{ "direction": "changing", "fm_param": "CT_INDEX",
                 "variable": "LT_INDEX1", "var_kind": "float" }] }
```

**Two distinct uses — don't conflate them:**

| Use case | FM | Where it lives | Binding |
|---|---|---|---|
| Single table, in-table counter | `/SMPL/PPPI_FM_SET_LINE_IDX` (or `ZSMPL_FM_SET_LINE_INDEX`) | inside the table | `changing CT_INDEX ↔ LT_<col>` |
| Cross-table, step-level sync of two counters | `ZSMPL_FM_CUSTOM_INDEX` | Setup Functions (NOT in a table) | `changing CH_INDEX1 ↔ LV_LINENO1`, `changing CH_INDEX2 ↔ LV_LINENO2` |

For the cross-table case (master + follower), don't add a per-table SET_LINE_INDEX — use the canonical CUSTOM_INDEX-in-Setup-Functions + TRANSFER_LINE_ITEMS pattern in §5.1. Look up an active DE1 reference if uncertain.

---

## 6. Critical gotchas

| Gotcha | Detail |
|---|---|
| **Cross-param wipe** | Calling `xs_add_parameters` re-sends text-domain inputs on the same owner. Any params NOT in the batch get wiped. Always batch all params for one owner in one call. |
| **10-char parameter limit** | `CMX_XS_DB_PS.NAME` is C(10). Names over 10 chars get silently truncated. `LV_PARTDESC` (11) becomes `LV_PARTDES`. Shorten before sending. |
| **NIDs transient across sessions** | NIDs from `xs_list_children` only match within the current SAP session. Re-fetch after a save or restart. |
| **Formula literal syntax** | `PPPI_LONG_FORMULA` literals are **UNQUOTED**: `LV_X = 1`, NOT `LV_X = '1'`. The quoted form silently no-ops or shows up as "valid parameter name" errors. |
| **Signature column LAST** | The signature column must be the last column in any table row, even after invisible function-call columns. |
| **Conditional rule pairs** | Activate/deactivate (or LOCK/UNLOCK) typically deploy as a PAIR (the formula + its inverse) on the table itself. |
| **Default value triplet** | A working default needs all three of `value`, `state="S"`, `pmode="F"` on the param. Missing any → renders as "None" in Valuation tab. |
| **PPPI_STRING_VARIABLE='X' sentinel** | On validation FM bindings, the framework substitutes `'X'` as the value-being-validated. Don't try to pass a real variable for that binding — use `validated_value_param` in the builder and it does the substitution. |
| **Save per call** | Every xstep mutation is save-per-call — no transaction wrapper. A failed second call leaves the first change persisted. |
| **EV_INDEX_T1/T2 outputs are drift** | If you see follower-side `INCREMENT_TABLE_LINE` with `out EV_INDEX_T1` / `out EV_INDEX_T2` bindings, that's the DE2-drift pattern (§5.1 alt). Canonical DE1 doesn't read those — it uses `TRANSFER_LINE_ITEMS` `out EX_PLANT → LV_LINENO2` for the follower's index instead. Don't introduce EV_INDEX_T1/T2 in new builds. |
| **xs_check_semantic info message** | A single info message `CMX_PII 998 visit=N pii=M` is normal (walk statistics), not an error. |
| **NID-shaped PPPI_LONG_FORMULA values are handles, not text** | When `xs_get_instruction` returns a `PPPI_LONG_FORMULA` value that is a 22-char base64-like NID (e.g. `fJVsUCCY7z6Nskf8xa61zG`), that's a pointer to a separately-stored G-node holding the actual formula expression. Writing it back as-is via `xs_update_instruction` stores the NID as a literal string; simulate then fails with "specify a valid parameter reference; parameter does not exist." The tooling gates this — `xs_update_instruction` / `xs_add_instruction` / `xs_add_table_instruction` / `xs_update_table_instruction` / `xs_modify_rows` refuse NID-shaped values; `xs_get_instruction` annotates them with `formula_handles[]`. **Replace each NID with the actual inline expression** before writing. Standard Setup Functions inlines: DEACTIVATE → `LV_ACTIVE <> 1`, ACTIVATE → `LV_ACTIVE = 1`, LOCK → `EV_LOCK = 1`, UNLOCK → `EV_LOCK <> 1`. |
| **PPPI_INPUT_REQUEST has a ~30-char limit** | `xs_add_table_instruction` / `xs_update_table_instruction` fail with a generic `CX_CMX_TYPES_EXCEPTION` when an input column's `label` is over ~30 chars. PPPI_OUTPUT_TEXT and instruction stext fields are more forgiving. Shorten labels (PDF wireframes are usually already abbreviated — match those instead of PNG hover-text). The exception message gives no hint at the cause; symptom is "add fails on an instruction with all-other-fields-valid input." |
| **IV params need TWO-level scope** | An IV input parameter (`PTYPE='I'`) referenced by a validation formula, calculation formula, or FM-call binding on the **inner main S step** must also be declared at the **outer T-root**. The inner copy gets `PMODE='R'` (reference); the outer stays at `''` or `'F'`. The framework resolves the inner step's value at runtime by name-lookup against outer scope. Without the inner reference, validations / calculations / FM-call bindings on the inner step see undefined params even though MBR is correctly populating the outer wrapper. See §7.10 for build flow. |
| **Row index domain MUST be `ZSMPL_CHAR_GI_INITIALS`** | Not `PPPI_MATERIAL_QUANTITY`. Even though row indices are integers, the customer convention separates them — quantity-domain values are subject to ALPHA conversion + quantity-aware framework handling that breaks counter behavior. Use `ZSMPL_CHAR_GI_INITIALS` + `value:"1"` for sequential row counters; keep `PPPI_MATERIAL_QUANTITY` for actual measured quantities (weights, volumes, sensor readings). |

---

## 7. Iteration patterns (what evolves v1 → v3+)

Patterns extracted from diff analysis of `Max Parker XA Folder - BU` archive (Bag Replacement Volumetric/Weight series). The base build from §3 is a **first draft**; these are the deltas that mature xsteps add.

### 7.1 Typed domain swaps

| v1 default | Mature replacement |
|---|---|
| `PPPI_SHORT_TEXT` (for UoM) | **`PPPI_UNIT_OF_MEASURE`** |
| `ZPPPI_NUMERIC_VALUE` (for quantity) | **`PPPI_MATERIAL_QUANTITY`** |
| `PPPI_SHORT_TEXT` (for HTML instructions) | **`PPPI_FRAGMENT_HTML`** |

Typed domains give cmxsvn its dropdown / unit-validation / formatted-display behavior for free.

### 7.2 Param consolidation

Delete duplicate scalars (e.g. `LV_UOM` + `LV_QTYUOM` doing the same job). Upgrade the survivor's domain (see 7.1). Set defaults inline with the triplet.

### 7.3 Sign-and-persist: SIG row carries the PMSG

**v2 pattern (deprecated):** separate `kind:"process_message"` row + separate `kind:"signature"` row.

**v3+ pattern:** `kind:"signature"` row owns the strategy AND the full `(variable, PPPI_field)` binding set AND the movement type. One row, not two.

```json
{
  "kind": "signature",
  "strategy": "SAPPOCSS",
  "process_message_category": "Z_PICONS",
  "bindings": [
    ["LT_PARTNO",  "PPPI_MATERIAL"],
    ["LT_BATCH",   "PPPI_BATCH"],
    ["LT_QTY",     "PPPI_MATERIAL_CONSUMED"],
    ["LT_UOM",     "PPPI_UNIT_OF_MEASURE"],
    ["LAV_ORDER",  "PPPI_PROCESS_ORDER"],
    ["LAV_PHASE",  "PPPI_PHASE"],
    ["LT_DATE",    "PPPI_EVENT_DATE"],
    ["LT_TIME",    "PPPI_EVENT_TIME"]
  ],
  "movement_type": "261"
}
```

### 7.4 Sign-and-persist requires THREE FMs on `TABLE_LINE.COMPLETING`

v1 typically has zero or one; v3+ has all three:

**(a) Signature validation** (on the SIG input column):

| Slot | Value |
|---|---|
| FM | `/SMPL/PPPI_FM_VALI_SUPE_SIG` |
| `IM_STEP_NAME` ← | `IV_HEADER` |
| `IM_STEP_INDEX` ← | `STEP_INDEX` |
| `IM_CONTROL_RECIPE` ← | `LAV_CRID` |
| `IM_PHASE` ← | `LAV_PHASE` |
| `IM_PO_NR` ← | `LAV_ORDER` (opt) |
| `IM_USERID` ← | `'X'` (sentinel) |
| `IM_STEP_UUID` ← | `SIMPL_UUID` |
| `IM_PLANT` ← | `LAV_PLANT` |
| `PPPI_TEXT_FOR_INVALID_INPUT` | fragment node |
| `PPPI_ACCEPT_INVALID_INPUT` | `03` (reject) |

**(b) Signature DB callback** (function_call row, event `TABLE_LINE.COMPLETING`):

| Slot | Value |
|---|---|
| FM | `/SMPL/PPPI_FM_SIG_ADD_DB_CB` |
| `IM_CONTROL_RECIPE` ← | `LAV_CRID` |
| `IM_PHASE` ← | `LAV_PHASE` |
| `IM_STEP_IDX` ← | `STEP_INDEX` |
| `IM_STEP_UUID` ← | `SIMPL_UUID` (opt) |
| `IM_STEP` ← | `IV_HEADER` (opt) |
| `IM_USERID` ← | `LV_PERFORM` |

**(c) MBR dependency add perform** (function_call row, event `TABLE_LINE.COMPLETING`):

| Slot | Value |
|---|---|
| FM | `/SMPL/MBR_DEP_ADD_PERFORM` |
| `IM_CONTROL_RECIPE` ← | `LAV_CRID` |
| `IM_AUFNR` ← | `LAV_ORDER` (opt) |
| `IM_STEP_UUID` ← | `SIMPL_UUID` |
| `IM_DEST_NAME` ← | `LAV_DEST` |
| `IM_USERID` ← | `LV_PERFORM` |

All three need `LAV_*` context vars + `SIMPL_UUID` + `LV_PERFORM`. The dependency FM additionally requires **`LAV_DEST`** — v1 builds commonly miss this. Add it as a param when adding `/SMPL/MBR_DEP_ADD_PERFORM`:

```json
{
  "name": "LAV_DEST",
  "domain": "PPPI_CONTROL_RECIPE_DEST",
  "ptype": "L",
  "pmode": "A"   // framework fills it; don't set state/value
}
```

### 7.5 Runtime-filled params: never `pmode=F`

These get computed by FMs or entered by the operator mid-execution. Locking them with Fixed conflicts with the runtime write:

- Weight/quantity outputs: `LV_GROSS`, `LV_NET`, `LV_TARE`, `LV_QTY`, `LV_VOLUME`
- Anything bound to a button or FM `EX_*` export

**Do** set `pmode=F` on:
- Static UoM defaults (`LV_UOM`, `LV_UOM1`)
- Static title/header strings (`IV_TITLE1`)
- Booleans (`IV_ACTIVE`, `IV_ACT_FLP`) carrying their Yes/No char value
- Line counters (`LV_LINENO1`, `LV_LINENO2`) — see 7.6

### 7.6 Line counter defaults

Despite being incremented at runtime by `ZSMPL_FM_INCREMENT_TABLE_LINE`, line counters get `value=1, state=S, pmode=F`. The framework overwrites the value when the FM fires; the default is for the pre-first-row render only.

### 7.7 UoM uppercase

Customer convention is **uppercase** UoM codes. Older xsteps have lowercase (`"g"`) — those flipped to uppercase (`"G"`) between v3 and v5 of Weight. Refactor lowercase to uppercase on touch.

Per-recipe defaults:

| Recipe family | `LV_UOM` default | Quantity domain |
|---|---|---|
| Bag Replacement Volumetric | `"L"` | `PPPI_MATERIAL_QUANTITY` |
| Bag Replacement Weight | `"G"` | `PPPI_MATERIAL_QUANTITY` |
| Culture Weight | `"G"` | `PPPI_MATERIAL_QUANTITY` |
| Viral Sample Submission | `"EA"` | `PPPI_MATERIAL_QUANTITY` |

### 7.8 Row ordering: CMD before FUNC

In v1 builds, FUNC rows often appear before CMD rows (e.g. row-sync FM before `TABLE.ADD_LINE / HIDE`). Customer convention is **CMD first, then FUNC**.

### 7.9 Row-scope copy params (conditional)

Sometimes per-row bindings need to be stable against framework re-evaluation of `LAV_*`. The fix:

- Add a row-scope copy param: `LV_RORDER` (domain `PPPI_PROCESS_ORDER`), etc.
- Add a "Set Row Order" instruction that copies `LAV_ORDER` → `LV_RORDER` on `TABLE.LINE_ADDED`
- Repoint bindings from `LAV_ORDER` → `LV_RORDER`

Only needed when binding stability matters (e.g. row needs to outlive a re-eval of `LAV_*`). Not all xsteps need this. Volumetric used it; Weight did not.

### 7.10 IV-parameter two-level scope (PMODE='R')

**Critical for any xstep that adds new IV params.** XStep input parameters (`PTYPE='I'` — the values MBR overlays at runtime per recipe) must be declared at **two levels**:

1. **Outer wrapper (the T-root)** — source-of-truth declaration with a hardcoded default. `PMODE='F'` (Fixed Value), `state='S'`, `value=<default>`. MBR overlays the recipe-specific value at runtime.
2. **Inner main S step** — a *reference* copy. `PMODE='R'`, `ref=<same name>`. Same NAME, same DOMAIN, same `PTYPE='I'`, `value=''`, `state=''`. The framework resolves it by name lookup against outer scope.

Without the inner reference, validations / calculations / FM-call bindings on the inner step read the param as empty even when MBR is correctly populating the outer wrapper.

**Don't touch template-owned IV params.** These already exist at BOTH levels in the AZ Template (the template ships them with the correct outer-F + inner-R wiring); your job is to leave them alone, NOT to re-declare them:

| Template-owned IV (skip) | Domain | Outer default |
|---|---|---|
| `IV_HEADER` | `PPPI_SHORT_TEXT` | (recipe-driven) |
| `IV_INSTR` | `PPPI_FRAGMENT_HTML` | (recipe-driven) |
| `IV_PL_TXT` | `PPPI_FRAGMENT_HTML` | (recipe-driven) |
| `IV_PRINT` | `PPPI_SHORT_TEXT` | (recipe-driven) |
| `IV_SIGN` | `ZSMPL_CHAR_SIGNATURE_STRAT` | (recipe-driven) |
| `IV_ACTIVE` | `ZSMPL_CHAR_YES_NO` | (recipe-driven) |
| `IV_ACT_FLP` | `ZSMPL_CHAR_YES_NO` | (recipe-driven) |
| `IV_TITLE1` | `PPPI_SHORT_TEXT` | (recipe-driven) |

Only add a new IV param at both levels when the spec explicitly calls for one (e.g. a configurable Min/Max value, a recipe-driven label/flag, etc.). Don't re-add the template IVs above — they're already there.

**Canonical exemplar — DE1 `SMPL: Feed Addition Set Up` (item `fJVsUCCY7z6LX7XXHJP1zG`, AZ Phase 2 folder).** This xstep adds two custom IV params (`IV_DMAX` "Prod Days Max" and `IV_DMIN` "Prod Days Min", domain `ZSMPL_CHAR_INT3`). The verbatim CMX_XS_DB_PS rows:

**Outer T-root** (hardcoded default — MBR overlays at runtime):
```jsonc
{ "name": "IV_DMAX", "domain": "ZSMPL_CHAR_INT3", "ptype": "I", "stext": "Prod Days Max",
  "value": "13", "state": "S", "pmode": "F", "ref": "", "is_table": false }
{ "name": "IV_DMIN", "domain": "ZSMPL_CHAR_INT3", "ptype": "I", "stext": "Prod Days Min",
  "value": "2",  "state": "S", "pmode": "F", "ref": "", "is_table": false }
```

**Inner main S step** (reference back to outer scope):
```jsonc
{ "name": "IV_DMAX", "domain": "ZSMPL_CHAR_INT3", "ptype": "I", "stext": "Prod Days Max",
  "value": "", "state": "", "pmode": "R", "ref": "IV_DMAX", "is_table": false }
{ "name": "IV_DMIN", "domain": "ZSMPL_CHAR_INT3", "ptype": "I", "stext": "Prod Days Min",
  "value": "", "state": "", "pmode": "R", "ref": "IV_DMIN", "is_table": false }
```

Note: `ref` on the inner copy is the same NAME as the param — that's how it walks back to outer scope.

**Build flow** — `xs_add_parameters` supports `pmode` (and `ref_target` for PMODE='R') at create time, and the editor's edit-zone guard allows BOTH T-root and main-step ownership. Two batched calls do it:

1. `xs_add_parameters` on the **outer T-root** (`owner_nid = root_nid`) — one spec per new IV param: `ptype='I'`, `pmode='F'`, `value=<default>`. Don't include any template-owned IVs — they already exist.
2. `xs_add_parameters` on the **inner main S step** — same NAME, same DOMAIN, same `PTYPE='I'`. Set `pmode='R'` and `ref_target=<same name>`. Don't include template-owned IVs here either.

No separate `xs_update_parameter` step needed — `pmode` + `ref_target` are settable at create time. If you do need to flip an existing param's mode after the fact, `xs_update_parameter` accepts T-root owners now too.

The wiring is **encoded in `PMODE`, not in the `VALUE` field** — the inner level keeps `VALUE` empty. The `VALUE` column on the OUTER side holds the static default; MBR overrides it per recipe at runtime.

**Caveat on T-root edits:** ADDING new IV params at T-root is the recommended §7.10 path and is fully supported. AVOID updating the existing template-owned T-root params listed above — those are MBR-driven and overwriting them fights the overlay. The tooling does not block these updates anymore; the responsibility for not editing them is on the builder.

**Diagnosing it later:** cmxsvn renders both rows in the parameter list, so the editor UI doesn't make the scope link obvious. The only way to see the wiring is to query `CMX_XS_DB_PS` and look at PMODE per OID — same NAME at both OIDs, one `F`/`''`, one `R`.

---

## 8. Skip list — what NOT to add by default

| Pattern | Why skip |
|---|---|
| **`LV_VAL1` placeholder triplet** in Setup Functions | Sometimes added (Weight v2→v3), sometimes removed (Weight v3→v4 reversed it). Add ONLY if cmxsvn raises "Internal error in plug-in [Work Instructions/PI Sheet]" specifically about LV_VAL1 / IV_TITLE1. Not a default-add. |
| **Row-scope copy params** (LV_RORDER etc.) | Only when bindings need to outlive a re-evaluation of `LAV_*`. Optional. |
| **Deleting Setup Functions / Activate** | Load-bearing for cmxsvn frame setup. Deleting them breaks Simulate. |

---

## 9. Customer conventions (iSSi on DE2_903)

Not documented in SAP. Treat as defaults; if in doubt, ask.

| Topic | Convention |
|---|---|
| Canonical template | `SMPL: AZ Template XStep` (item `fJVsUCCY7z6KzR4szUfXzG`, Max Parker XA Folder) |
| Folder whitelist for new builds | Max Parker XA Folder (`fJVsUCCY7z6DxdXgpau1zG`) or Dennis Kim XA Folder (`fJVsUCCY7z6DxEAfEw}1zG`) |
| Table index var domain | `ZSMPL_CHAR_GI_INITIALS` with default `"1"` |
| Welder / Sealer EQTYP | `M` (Machines) |
| Filter tester EQTYP | `Q` (Test/measurement equipment) |
| Signature strategy | `SAPPOCSS` (supervisor) or `SS000201` (Done By) |
| Signature validation FM | `ZEBR_XSTEP_SIG_VALIDATION` (alt: `/SMPL/PPPI_FM_VALI_SUPE_SIG` for v3+ supervisor sigs) |
| Signature audit commit FM | `ZEBR_XSTEP_SIG_ADD_DB_CB` (alt: `/SMPL/PPPI_FM_SIG_ADD_DB_CB`) on `PROC_INSTR.COMPLETING` |
| Date/time fetch | `/SMPL/PPPI_FM_GET_DATE_TIME` (use `EV_DATE_DEFAULT` for date) |
| Material lookup + description | `ZSMPL_FM_GET_MAT_DETAIL`, `validated_value_param: IM_MATNR` |
| Batch lookup + expiry | `ZSMPL_FM_GET_EXPIRY_DATE`, `validated_value_param: IM_BATCH`, requires `IM_MATNR` |
| Row sync index FM | Cross-table sync: `ZSMPL_FM_CUSTOM_INDEX` in Setup Functions (CH_INDEX1/2 ↔ LV_LINENO1/2) + `ZSMPL_FM_INCREMENT_TABLE_LINE` on master + `ZSMPL_FM_TRANSFER_LINE_ITEMS` × 4 events on follower (see §5.1). Single-table only: `/SMPL/PPPI_FM_SET_LINE_IDX` (CT_INDEX changing) |
| Equipment fetch | `/SMPL/ELB_FM_GET_ASSIGNED_EQUI` |
| Goods Issue process message category | **`Z_PICONS`** (underscore — replaces older `ZPICONS`) |
| Logbook update | `/SMPL/ELB_FM_UPDATE_LOGB` on `PROC_INSTR.COMPLETING` with `IV_EQUIPMENT ← LV_ROOM_ID` |
| Numeric quantity domain | `PPPI_MATERIAL_QUANTITY` (not `ZPPPI_NUMERIC_VALUE`) |

When adding a new pattern, search for an existing iSSi xstep that does the same thing first. Convention is a stronger signal than first-principles design.

---

## 10. Common mistakes

1. **Pattern-matching on EQTYP letters.** `W` is not Welder — it's Workstation. Use `M` for welders/sealers.
2. **Typing process message field names from memory.** `PPPI_MATERIAL_QUANTITY` vs `PPPI_MATERIAL_CONSUMED`, `PPPI_UNIT_OF_MEASURE` vs `PPPI_UNIT_OF_MEASUREMENT`. Always copy from `xs_get_process_message_category_detail`.
3. **Reaching for SET_LINE_INDEX + EV_INDEX_T1/T2 for cross-table sync.** That's DE2 drift. Canonical DE1 cross-table sync uses CUSTOM_INDEX in Setup Functions + INCREMENT_TABLE_LINE on master (TABLE.LINE_ADDING) + TRANSFER_LINE_ITEMS × 4 events on follower — see §5.1. SET_LINE_INDEX is single-table only.
4. **Copying from a drifted reference.** Always check folder paths. Active-folder references are canonical.
5. **Guessing index var domain.** Use `ZSMPL_CHAR_GI_INITIALS` per customer convention.
6. **Confusing T370T with text table.** T370T is the master config; T370U is the text table. Other T370 families follow the normal `_T` suffix convention — don't generalize.
7. **Dropping to raw `set_content` when the typed builder lacks a feature.** Stop and flag the gap. Raw is a last resort.
8. **Quoting formula literals.** `LV_X = '1'` silently breaks. Use `LV_X = 1`.
9. **Forgetting to rename the cloned step.** The cloned step retains `<XStep Name>` literal text. Update via `xs_update_node_attrs(stext: ...)`.
10. **Single-call `xs_add_parameters`.** Cross-param wipe destroys other text-domain inputs. Batch all params per owner.
11. **Reusing `IV_KEYWORD` across xsteps.** Counter collisions when they run on the same plant+order+phase. Pick distinct keywords.
12. **`LV_PARTDESC` (11 chars).** Truncated to `LV_PARTDES`. Use `LV_PARTDS` (9 chars) instead.

---

## 11. When something breaks

| Symptom | Likely cause |
|---|---|
| `"Internal error in plug-in [Work Instructions/PI Sheet]"` in cmxsvn | Check `LV_VAL1` exists on main step and Setup Functions placeholder triplet (`&IV_TITLE1&` / `LV_VAL1` / `PPPI_SHORT_TEXT`) is intact. Or the xstep has a structural issue. |
| `xs_check_semantic` reports dangling vars | An instruction references a param that doesn't exist (or has the wrong name). Names are C(10) max. |
| Render returns empty XML | The destination key on the xstep doesn't match the iterator filter. The iterator only walks nodes assigned to the same destination key. |
| "Enter a valid parameter name, use letters and underscores" | Formula literal quoting (see §6) — `LV_X = '1'` instead of `LV_X = 1`. |
| `xs_list_children` returns "An internal error has occurred in XStep administration" on a target xstep | The target xstep itself is structurally invalid (mid-build or corrupt). Try the same call on a known-good xstep to confirm the tool works. |
| Cross-table sync row appears one row late | Master is using `TABLE.LINE_ADDED` instead of `TABLE.LINE_ADDING` — switch. |
| Param default shows "None" in Valuation tab | Missing one of the triplet — needs `value` AND `state="S"` AND `pmode="F"`. |
| Process message silently doesn't fire | Wrong category name (`ZPICONS` vs `Z_PICONS`); missing `ZSMPL_CHAR_MOVEMENT_TYPE`; or destination FM doesn't exist (`fm_exists: false`). |
| `"Specify a valid parameter reference; parameter does not exist"` at simulate (no param name quoted), but `xs_check_semantic` is clean | The classic NID-formula round-trip: you read an instruction with `xs_get_instruction`, included its `PPPI_LONG_FORMULA` NID values verbatim in your `xs_update_instruction` field array, and the writer stored the 22-char NID as a literal formula expression. Simulate parses the NID-as-text and fails. Check the instruction with `xs_get_instruction` — if the response includes `formula_handles[]`, those positions need inline substitution. Standard Setup Functions inlines: DEACTIVATE → `LV_ACTIVE <> 1`, ACTIVATE → `LV_ACTIVE = 1`, LOCK → `EV_LOCK = 1`, UNLOCK → `EV_LOCK <> 1`. The write tools now refuse NID-shaped values up-front; if you see `error: "NID_SHAPED_FORMULA_VALUES"` the gate caught it. |
| `CX_CMX_TYPES_EXCEPTION` from `xs_add_table_instruction` with all fields apparently valid | Most common cause: an input column's `label` exceeds ~30 chars (`PPPI_INPUT_REQUEST` width). Shorten the label. Reproduces deterministically — bisect by removing columns one at a time until the add succeeds, then check the surviving column's label length. |
| **IV param reads empty in a validation formula / FM binding even though MBR overlay sets it** | The inner main S step is missing the `PMODE='R'` reference copy of the IV param. The outer T-root declaration alone isn't enough — formulas/FM bindings on the inner step resolve names against the inner scope. Add an inner copy via `xs_add_parameters` (same name/domain/PTYPE='I'), then `xs_update_parameter` to flip `pmode='R'`. See §7.10. |
| **Row `#` column renders blank or `0` on the first row** | The `LT_INDEX*` row-index param is missing its `value="1"` default. `/SMPL/PPPI_FM_SET_LINE_IDX` (or sibling FMs) increments *from* the default on each `TABLE.LINE_ADDED`; without a `"1"` seed the first render shows empty/zero. Also check the param's domain is `ZSMPL_CHAR_GI_INITIALS`, not `PPPI_MATERIAL_QUANTITY` — wrong domain changes the framework's handling of the counter. |

---

## 12. When to ask the user vs proceed

**Proceed without asking when:**
- Documented customer convention covers it
- A canonical pattern in `xs_instruction_recipes` matches
- It's a structural lookup (read instruction, query table, list children)
- Verifying a write just made
- Spec is vague but convention is clear (e.g. spec says "numeric field" → `PPPI_MATERIAL_QUANTITY` per convention)

**Ask before proceeding when:**
- Inventing a new identifier (sync group keyword, variable name in a new domain)
- A search returns conflicting results for the same FM/pattern
- A reference xstep is in an inactive folder and the active alternative looks different
- Customer convention doesn't cover the case
- Destination FM reports `fm_exists: false`
- Spec is internally inconsistent (wireframe label vs body text disagree)
- The action is irreversible (delete operations on master data)
- Spec mentions an FM but the wireframe has no UI surface to feed/display its inputs/outputs

Lean toward proceeding once you have either a convention or a recipe. Lean toward asking on boundary-crossing situations.

---

## 13. Workflow checklist for a new build

When the user asks you to build an xstep:

1. **Read the spec** end to end. Understand the wireframe.
2. **Locate or clone a template.** `xs_find` for similar existing xsteps; `xs_clone_xstep` from the AZ template if starting fresh.
3. **Read the active reference for similar patterns.** Check folder paths — avoid Inactive folders.
4. **Read `xs_instruction_recipes`** for any pattern you'll use.
5. **Look up domains and characteristics.** For each table column, verify domain via `xs_list_parameter_types`. For each process message, verify characteristics via `xs_get_process_message_category_detail`.
6. **Look up FM signatures.** Verify parameter names, directions, required flags before binding. Use `xs_search_instructions(domain=PPPI_FUNCTION_NAME, value_pattern=<FM>)` for the fastest binding-shape discovery — it returns full bindings from a known-good call site.
7. **Write a build plan** (markdown file in `xstepBuilder/xsteps/<name>/build_plan.md`) before executing. Confirm with the user.
8. **Build incrementally**, reading after writes. Use `xs_get_instruction(parse:"table")` to verify table writes.
9. **Verify destination FMs exist** via `find_objects(query=<fm_name>)` — `total_matching: 0` means the FM is missing.
10. **Run `xs_check_semantic`** — 0 errors required (info message OK).
11. **Manual cmxsvn Simulate test** — must work.
12. **Rename** the item / root / step to the spec title.

---

## 14. Tool families (brief)

For full per-tool reference see [XSTEP_TOOLS.md](./XSTEP_TOOLS.md). Quick orientation:

- **Repository navigation**: `xs_find`, `xs_folder_tree`, `xs_list_children`, `xs_get_metadata`, `xs_get_version`
- **Instruction authoring**: `xs_add_table_instruction` / `xs_update_table_instruction`, `xs_add_instruction`, `xs_add_grouping_instruction`, `xs_add_table_instruction(repeated:false)`, `xs_get_instruction`
- **Parameter authoring**: `xs_add_parameters` (batched), `xs_update_parameter`, `xs_list_parameters`, `xs_list_parameter_types`
- **Node mutation**: `xs_update_node_attrs`, `xs_rename_item`, `xs_delete_node`, `xs_insert_row`, `xs_update_row`, `xs_delete_row`, `xs_reorder_rows`
- **Lifecycle**: `xs_clone_xstep`, `xs_create_blank_xstep`, `xs_delete_xstep`
- **References**: `xs_add_reference`, `xs_update_reference`
- **Function modules**: `xs_create_function_module`, `xs_update_function_module`, `xs_get_function_module`, `xs_delete_function_module`
- **Characteristics**: `xs_add_characteristic`, `xs_edit_characteristic_values`
- **Validation**: `xs_check_semantic`, `xs_diff_snapshots`, `xs_get_snapshot`
- **Process messages**: `xs_add_process_message`, `xs_update_process_message`, `xs_list_process_message_categories`, `xs_get_process_message_category_detail`
- **Search**: `xs_search_instructions`, `xs_instruction_recipes`
- **SAP data layer**: `find_objects`, `get_source`, `get_table_data`, `get_xml`, `get_usages`, `run_query`

Tools are deferred — they don't appear in your tool list at session start. Call `ToolSearch` with intent keywords (e.g. `"xstep table builder"`, `"parameter domain"`, `"process message category"`) before assuming a capability is missing.

---

## Appendix: AZ Template structure

`SMPL: AZ Template XStep` (item `fJVsUCCY7z6KzR4szUfXzG`) contains:

- **T-root** + 12 input/header parameters: `IV_ACTIVE`, `IV_ACT_FLP`, `IV_HEADER`, `IV_INSTR`, `IV_PL_TXT`, `IV_PRINT`, `IV_SIGN`, `IV_TITLE1`, `LV_LOCK`, `OV_VAL`, `SIMPL_UUID`, `STEP_INDEX`.
- **`Conditional Header` R-reference** — renders the title bar and instructions block. Nested step inside.
- **`<XStep Name>` S-step** (depth 1) — your main step. Pre-wired with:
  - Framework params: `EV_LOCK`, `IV_*` (mirroring root), `LAV_CRID`, `LAV_ORDER`, `LAV_PHASE`, `LAV_PLANT`, `LV_ACTIVE`, `LV_SIGC`, `LV_SIGD`, `LV_VAL1`, `SIMPL_UUID`, `STEP_INDEX`
  - `Setup Functions` instruction — load-bearing, don't touch
  - `Activate` instruction — load-bearing, don't touch
  - `Hide in Print Mode` generation hook
- **`Optional Signature` R-reference** — contains nested signature step with two sub-steps (Performed By + Witnessed By). Adds target-value param family at the ref level: `IV_TAR_MN` (target min), `IV_TAR_MX` (target max), `IV_TAR_VL` (target value), `IV_TAR_MT` (target type), `IV_LOCK` (lock control). Use these for any spec that needs operator entries scored against a target range (pH, temperature, weight tolerance, etc.).

For most specs, the workflow is: clone → rename the inner step → add only the spec-specific instructions (typically one table). The Optional Signature ref usually already satisfies "Verified By" / "Witness By" specs — check it before building a custom step-level signature.

**Spec "dropdown selection" doesn't always mean a real dropdown.** Specs frequently describe columns as "dropdown" when the production xstep uses `PPPI_SHORT_TEXT` (free text). Before creating Z-characteristics with enumerated values, check the active reference's column type.

---

## Appendix: Lessons that didn't fit elsewhere

### "Production-pattern lookup" is the fastest FM-binding discovery

When wiring a new FM, the fastest path is NOT reading FM source — it's:

```
xs_search_instructions(domain="PPPI_FUNCTION_NAME",       value_pattern="<FM>")  // event callbacks
xs_search_instructions(domain="PPPI_VALIDATION_FUNCTION", value_pattern="<FM>")  // column validators
```

Returns full bindings from a known-good call site — FM-side param names, directions, optional flags, var_kind, AND the xstep-side variables conventionally fed in. Beats reading FM source because you get the customer's binding pattern, not just the FM signature.

### `xs_get_instruction` round-trips the `X` sentinel correctly

The typed parser auto-detects `PPPI_STRING_VARIABLE="X"` on a validation binding and back-fills `validated_value_param: "<fm_param>"` on the parsed spec. So `build(parse(fields))` produces the same field array — read-modify-write is safe.

### Parallel parameter creation works

Multiple `xs_add_parameters` calls + an `xs_update_node_attrs` call batch fine in a single parallel response. Persistence is save-per-call but wall-clock is one round-trip. NOTE: instructions that reference a param still need the param to exist first — parallelism is fine within a "layer" (all params; all instructions) but not across.
