# GxP Compliance Guide — Overarching Rules for Building XSteps

The **compliance overlay** for every XStep we build. Where the companion guides tell you *how* to build:

- **Batch Record to XStep Mockups - Build Guide.md** — batch record → mock-up (formats, fields, patterns).
- **Functional Spec Build Guide.md** — mock-up → XStep Design Specification (FMs, params, layout).

…this guide tells you *what must be true* for the result to be GxP-compliant. It is the shared reference for the
**overarching rules we hold every XStep to**. It does **not** repeat the build mechanics — it points at them.

> **Scope & status.** Working reference for authoring XSteps in the cmxsvn editor (CMXSV) and their specs — **not**
> a validation deliverable and not a substitute for the site Validation Master Plan or the controlling regulation
> text. Deeper background and the SAP source material live in the **`GxP Compliance Documentation/`** folder
> (regulated-environment whitepapers, Batch Release Hub, the Manufacturing course, and the GxP Compliance
> Reference PDF).

---

## 1. Why these rules exist — the regulatory basis (in one paragraph)

An EBR is a GxP record. Four instruments govern it: **FDA 21 CFR Part 11** (electronic records & signatures —
attributable e-signatures, secure time-stamped audit trails), **EU GMP Annex 11** (computerised systems —
validation, data integrity, access & change control), **EU GMP Chapter 4** (controlled, versioned documentation),
and **GAMP 5** (risk-based validation; SAP is a configurable product, so validation concentrates on our
configuration, not delivered standard functionality). The data-integrity yardstick is **ALCOA+** (Attributable,
Legible, Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring, Available). Every rule below is one
of these principles made concrete for an XStep.

---

## 2. The overarching rules (every XStep is checked against these)

| # | Rule | Driver | Satisfied in the XStep by |
|---|---|---|---|
| **G1** | **Every recordable action carries an attributable e-signature.** One `Performed By` per table line; a second sign-off (`Witnessed`/`Verified`/`Checked By`) is a **step-level footer**, never a second column. | 21 CFR 11; ALCOA-Attributable | Signature column + Optional-Signature block; `SAPPOCSS` strategy + validation FMs. See Mockups rule 1–2. |
| **G2** | **Timestamps are system-stamped as an editable default — not hand-keyed from scratch.** A ▶ button/FM stamps the current date/time into the field's **default** (via a `LV_*_D`/`LV_*_T` default variable → `PPPI_DEFAULT_VARIABLE`); the field captures into a separate `LV_DATE`/`LV_TIME`. The operator **may override** it (they can legitimately need to correct a date/time) — what makes it GxP-sound is the **`Performed By` e-signature** on the line (attributable + audit-trailed), **not** locking the field. Date and Time are **separate** fields; set **Reason Required** where a documented reason for change is wanted. | 21 CFR 11 audit trail; ALCOA-Contemporaneous | Date/time & timer FMs (`GET_DATE_TIME`; `STR_PROC_STRT_TM`/`GET_PROC_TM`/`CLEAR_PROC_TM`) → default variable. See Mockups rule 3 / Func Spec §5. |
| **G3** | **Only true operator measurements are entry fields.** Computed outputs and standard constants are **read-only (greyed)** — never blank inputs the operator re-keys. | ALCOA-Accurate; error reduction | Computed columns typed `output`; constants pre-filled read-only. See Mockups rule 4. |
| **G4** | **Measured values with limits are validated in-line; out-of-spec is a captured deviation.** | Annex 11; review-by-exception | Range/tolerance FMs (`/SMPL/PPPI_FM_MIN_MAX`, `CALC_TOLERANCE`) with MBR-fed `IV_*` min/max; out-of-spec triggers a deviation/escalation, not a silent accept. |
| **G5** | **Results are typed, machine-readable characteristics — not free text.** Quantity → `PPPI_MATERIAL_QUANTITY`; Yes/No, pass/fail, disposition → a **CT04 characteristic**; date → a date domain; UoM → `PPPI_UNIT_OF_MEASURE`. | Data integrity; downstream auto-evaluation | Correct domain per field. This is *why* typing matters: values flow to the **inspection lot / usage decision**, **batch classification**, and the **Batch Release Hub** — which auto-evaluate only on typed data (and that is what makes review-by-exception possible). |
| **G6** | **Fixed value lists are controlled vocabularies, never free text.** | Data integrity / consistency | Dropdown backed by a **CT04 characteristic** (`ZSMPL_CHAR_*`, CABN + allowed values). See Mockups rule 9c. |
| **G7** | **Material identity & consumption are traceable.** Part No. → Material Description and Batch No. → Exp. Date validated; goods issue posted by a **process message** (`Z_PICONS`, movement type 261), **one line per material**. | Batch genealogy; GMP | Input-validation FMs + goods-issue process message. See Mockups rule 5. |
| **G8** | **Capture each datum once, in the step that owns it.** Other steps carry it forward **read-only** — never re-transcribe or duplicate. | ALCOA-Original; error reduction | Carry-forward read-only fields; instruction-only steps where data lives elsewhere. See Mockups §3 "data lives elsewhere". |
| **G9** | **No silent gaps.** Every batch-record recordable is covered — including totals/summary rows, cross-record write-backs, attachment sub-tables — and sibling "results" tables use a **consistent** variant. | ALCOA-Complete/Consistent | Coverage crosswalk + deep-review sweep. See Mockups §2 Step 6. |
| **G10** | **Version & change control.** Build against the **approved recipe**; the **Released** XStep version is the validated one (not necessarily the highest-numbered); changes go through SAP transport/ChaRM; the design spec is the change-control artifact. | Annex 11; GMP Ch. 4; ECM | Released-version discipline; versioned specs. See Mockups Step 3 / Func Spec §4. |
| **G11** | **Records endure and are retrievable independently.** EBR data persists to SAP (standard docs / `ZTC_*` tables) and is retained per the record-retention policy — **do not** rely on a platform audit log (e.g. a 90-day default) as the GxP record. | 21 CFR 11; ALCOA-Enduring/Available | Persistence FMs; process messages posting to SAP. |
| **G12** | **Reuse the validated library first; flag new development as new validation scope.** Every reused standard XStep/FM is functionality we don't re-validate; a genuinely new Z FM (e.g. in `ZAI_XSTEP_FMG`) is net-new scope the spec must call out. | GAMP 5 risk-based; clean-core | Reuse-first rule; "author new only when nothing fits." See Func Spec §5 ⭐. |

---

## 3. ALCOA+ quick map

| Principle | The rule(s) that carry it |
|---|---|
| Attributable | G1 |
| Legible | short standardised labels (Mockups rule 11) |
| Contemporaneous | G2 |
| Original | G8 |
| Accurate | G3, G4 |
| Complete / Consistent | G9 |
| Enduring / Available | G11 |

---

## 4. Scope boundary — what these rules are, and are NOT

- **They apply at XStep-build time** (authoring in CMXSV and writing the spec). Satisfy them **per XStep**.
- **They are not per-spec content to transcribe.** The functional spec stays scoped to the individual XStep as
  built in CMXSV — its FMs, parameters, columns, validations, signatures, process messages, and layout. The
  **downstream** picture (SAP Batch Release Hub release checks, batch disposition, the CSV/validation programme,
  audit-log retention, requirement-traceability matrices) is **compliance-programme material** — it lives in the
  `GxP Compliance Documentation/` folder, **not** in each XStep spec. G5/G7/G11 tell you *why* to type and post
  data correctly; they don't tell you to document the downstream contract in every spec.
- **Shared responsibility.** SAP qualifies the platform (IQ); our XSteps + specs support the **customer's** OQ/PQ
  against their URS (the paper MABR + requirements). Reuse and clean-core keep that validation scope small.

---

## 5. Pre-flight checklist (run against every XStep)

- [ ] **G1** e-signature present; one per line; second sign-off in the footer.
- [ ] **G2** every date/time is **system-stamped as the field default** (editable/overridable), Date and Time separate, and covered by a `Performed By` signature (+ Reason Required if overrides need a reason).
- [ ] **G3** computed/constant fields read-only; only measurements are entry fields.
- [ ] **G4** measured inputs with limits carry a range/tolerance validator; out-of-spec captured.
- [ ] **G5** each result has the correct typed domain (quantity/Yes-No/date/UoM) — no free text.
- [ ] **G6** fixed-list fields are CT04-backed dropdowns (column **+** characteristic named).
- [ ] **G7** Part/Batch/Exp validated; goods issue via `Z_PICONS` (261), one line per material.
- [ ] **G8** each datum captured once; carry-forwards read-only.
- [ ] **G9** coverage crosswalk complete — no dropped section, total, cross-record, or sub-table.
- [ ] **G10** built on the approved recipe; mirroring the **Released** version; change under control.
- [ ] **G11** records persist to SAP and are independently retained.
- [ ] **G12** reused from the validated library where possible; any new Z development flagged.

---

## 6. Where to go next

| Need | Guide |
|---|---|
| Turn a batch record into a mock-up (formats, fields, patterns) | *Batch Record to XStep Mockups - Build Guide.md* |
| Turn a mock-up into an XStep Design Specification | *Functional Spec Build Guide.md* |
| The SAP builder mechanics (cmxsvn tools) | *XSTEP_BUILD_GUIDE.md* / *XSTEP_TOOLS.md* |
| Regulatory background, SAP source material, mapping detail | `GxP Compliance Documentation/` (whitepapers, Batch Release Hub, Manufacturing course, GxP Compliance Reference PDF) |

> Regulatory specifics summarised here are for orientation; confirm against the controlling regulation text and
> the site Validation Master Plan before formal use.
