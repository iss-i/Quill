# Build Guide — From Master Recipe to Work Instructions

A practical, repeatable method for turning a **master recipe** (the ordered tree of XSteps that
templates the EBR) into an operator-facing **Work Instruction (WI)** — the step-by-step,
screenshot-driven document that walks a user end-to-end through executing the process order and
filling out every XStep in SiMPL EBR.

Captured from the **AZ Phase 1 SiMPL EBR Work Instructions** (Buffer, Calculation & Sampling, IBC,
Media / Nutrient Feed A — *Pangaea Life Science Solutions*) and their **Input Data Shortlist**.

> **Where this sits.** The other two guides build the *authoring* side — the
> [Batch Record → XStep Mock-ups guide] turns a paper MBR into reusable XStep mock-ups, and the
> [Functional Spec guide] documents each XStep's FMs/config. **This guide builds the *execution* side:**
> once the master recipe exists (its XSteps assigned and its production version customized), the WI
> tells the operator how to run it. **One Work Instruction = one master recipe.**

---

## 1. What a Work Instruction is

A WI is **not** a spec and **not** a mock-up. It is the operator's runbook: "open this process order,
put the EBR in Change mode, and here is exactly what to click and type in each XStep, in order, with a
screenshot of each." It replaces the manual, hand-written step-by-step instructions the functional team
otherwise writes from the process orders — the single biggest manual effort in the delivery.

Key facts (from the Phase 1 set):
- **Scope = one master recipe** (e.g. *50 mM Sodium Acetate Buffer*, *FPCHO Nutrient Feed A*, *IBC*).
- **Audience = the shop-floor operator + reviewing supervisor**, non-SAP.
- **Content = actions, not design** — "Enter the Measured Amount and press Enter", "Sign Performed By",
  not FM names or characteristics.
- **Every XStep gets its own numbered sub-section + screenshots.**
- Produced as a controlled `.docx`/PDF with a title page, ToC, and a Revision History.

---

## 2. Source inputs (what you need to generate one)

| Input | Where it comes from | Drives |
|---|---|---|
| **Master recipe XStep tree** (phases → ordered XSteps) | SAP master recipe / production version (`cr_*` / `shaper` tools), or the mock-up **EBR phase plan** as a proxy | The ToC + section structure (§3) |
| **Each XStep's element/field list** (in order) | our XStep data model (`steps_vidf.py`), or live via `shaper_get_version` | The per-XStep numbered steps (§5) |
| **A screenshot per XStep** | executed EBR (final) or the **mock-up `image.png`** (draft) | The visual under each sub-section |
| **Input Data Shortlist** (`XStep → Field → value`) | the test-data workbook | Example values / filled screenshots (§8) |
| **Client-specific variants** | the client's actual document + the RTM (Mock-up guide §4) | Which *variant* of a block to document (§9) |

**The recipe's XStep order is the backbone** — get it first. Everything else hangs off it.

---

## 3. Anatomy of a Work Instruction (fixed structure)

Every Phase 1 WI is the **same shape** — only the recipe-specific middle changes:

```
Title page
Table of Contents
1  Purpose            ← boilerplate (swap recipe name)
2  Overview           ← boilerplate (what SiMPL EBR is)
3  Navigation         ← boilerplate (Fiori Launchpad, plant access, pick the PO)
4  Master Recipe EBR  ← boilerplate (open PO, Display/Change mode, Expand/Collapse phases)
   4.1  Phase 0020: PO Info
        4.1.1  Display Order Details
        4.1.2  BOM Details
        4.1.3  Batch Record Signature Table
        4.1.4  Room & Equipment Assign
        4.1.5  Component Goods Issue
        …                                   ← one sub-section per XStep, grouped by phase
   4.2  Phase 0030: Weigh
   4.3  Phase 0040: Prep
   4.4  Phase 0050: Transfer
   4.5  Phase 0060: Summary
   4.x  Phase 0180 / 0070: Room & Equipment Cleaning / Area Clearance
5  Revision History
```

- **§1–§4 are ~identical across every recipe** — treat them as a fixed template with the recipe name
  and plant (e.g. "G20") substituted. Do not re-author them per recipe.
- **§4.x = the master recipe, phase by phase.** The phase names/numbers (0020 PO Info, 0030 Weigh,
  0040 Prep, 0050 Transfer, 0060 Summary, cleanup) come straight from the recipe.
- **Each XStep = one numbered sub-section** (`4.1.4 Room & Equipment Assign`) containing a short numbered
  action list and one or more screenshots.

---

## 4. The boilerplate front matter (template it, don't rewrite it)

Lift these verbatim and parameterize only the **{recipe name}** and **{plant}**:

- **Purpose** — "…provide step-by-step guidance for executing the **{recipe}** process steps within the
  SiMPL EBR application in **{plant}**…"
- **Overview** — the standard "SiMPL EBR is a web-based application… integrates with SAP ECC via the Fiori
  Launchpad…" paragraph.
- **Navigation** — access via Fiori Launchpad; process orders show only for the user's plant; select the
  relevant PO on the Process Order List page.
- **Master Recipe EBR** — the fixed open/execute flow:
  1. Search the process order, press Enter; select it to launch the EBR.
  2. Order details appear in the header.
  3. **Display vs Change** — Display to view only; **Change to execute**.
  4. Click the control-recipe row to open the EBR.
  5. **Expand All** / **Collapse All** to show/hide phases; **Change↔Display** toggle.

---

## 5. Per-XStep execution steps — the element→sentence engine (the core)

This is what makes a WI **auto-generable.** The numbered steps under each XStep are a *deterministic
function of that XStep's ordered UI elements*, using a fixed set of verb templates. Walk the XStep's
elements top-to-bottom and emit one instruction per element:

| XStep element (mock-up) | Generated Work-Instruction sentence |
|---|---|
| **Get [Type] button** (Get Equipment / Scale / pH Meter …) | "Click the **Get [Type]** button to select the assigned [Type]. The **[Type] ID** and **[Type] Description** are retrieved and populated." (+ "…and **Calibration Due Date**" when the variant has it — see §9) |
| **Entry field** (text/number) | "Enter the **[field]** and press Enter." |
| **Entry field feeding a calc** | "Enter the **[field]**; the **Result** is calculated and populated automatically." |
| **Output / computed field** | "The **[field]** is populated automatically." |
| **Dropdown** | "Select an option from the **[field]** dropdown." |
| **Date/Time stamp button** | "Press **[Record / Get Date/Time]** to stamp the **[field]** (Date and Time)." |
| **Table (Add Row)** | "Complete each row of the **[table]**: [per-column sentences]. Use **+ Add Row** for each additional [item]." |
| **Goods Issue** | (no operator field) — "On signing, the material is consumed into SAP (goods issue) automatically." |
| **Performed By** | "Once the entries are reviewed and complete, sign the **Performed By** field." |
| **Witnessed By / Verified By** | "The supervisor signs the **Witnessed By** field — **must be a different user** than Performed By. Once signed, the step is **complete and locked** (no further edits)." |

Real examples this reproduces exactly:
- *Calculation*: "Enter the Measured Amount → the Result is calculated → sign Performed By → Witnessed By (different user)."
- *FIO / Investigational Samples*: "Click Get Equipment → Equip ID/Description populate → select the Sample Pulled dropdown → enter Storage Location → sign Performed By."
- *DLIMS Samples*: "Press Get # of Vessels → enter DLIMS Project & Sample Number → sign Sampled By → Witnessed By → step locked."

> **Rule of thumb:** the WI step order **follows the mock-up element order**, and every interactive element
> becomes exactly one numbered instruction. If you can't write the sentence from the element, the mock-up is
> under-specified — fix the mock-up, don't invent the step.

---

## 6. Signature & completion conventions (GxP)

Apply on every data XStep:
- **Performed By** signed by the executing operator after entries are complete.
- **Witnessed By / Verified By** signed by a **different** user (supervisor).
- After the witness signature the step is **locked** — state this explicitly ("no further modifications
  can be made"). This is the operator-facing expression of the same dual-signature control the specs
  document at the FM level.

---

## 7. Screenshots

- **One (or a few) screenshots per XStep**, placed directly under its numbered steps, captioned
  "Steps X–Y: [context]".
- **Draft/spec stage:** use the mock-up `image.png` (shows the layout and fields).
- **Final operator WI:** use screenshots of the **executed EBR** filled with the Input-Data-Shortlist
  values, so the operator sees a realistic filled example.
- Keep the screenshot immediately adjacent to the steps it illustrates; never batch them at the end.

---

## 8. Input Data Shortlist integration

The shortlist maps **`XStep Name → Field Name → Input value`** for the recipe (plus the test **PO
numbers** per operator). Use it two ways:
- To **fill example screenshots** (the realistic filled EBR).
- As an optional **data appendix / inline callout** ("For this order, enter Room # = 1418; Equipment =
  30003581, 30009530, …").
Keep the field names in the shortlist **identical** to the XStep field labels so the mapping is 1:1 and
machine-joinable.

---

## 9. Client-specific variants — document the variant, not the generic block

The generic library block is often **not** what the client uses. The Phase 1 *FIO Samples* step shows the
**generic** "Get Equipment → Equip ID + Description" with **no Calibration Due Date** — but AZ requires Cal
Due. The WI must render the **client's variant** (the fields that are actually on their XStep), not the
stock block. Source the field list from the client's mock-up / the RTM coverage check, and let the
element→sentence engine (§5) pick up the extra field automatically. **If the mock-up carries the client
field, the WI step falls out for free; if it doesn't, that's a gap to fix upstream first.**

---

## 10. Consolidation / dynamic steps — document each XStep once

A heavily-repeated activity (component addition, weighing, equipment select, a chromatography cycle) is
**one scalable XStep referenced many times**, not many steps. The WI documents it **once**, and the
repetition is expressed as **"+ Add Row"** / "repeat per cycle/day". Do not emit a sub-section per
repetition — mirror the recipe's reuse. (This is the operator-facing side of the dynamic-authoring /
exploded-reference pattern in the Mock-up guide.)

---

## 11. Formatting & style conventions

- **Voice:** imperative, second person, present tense — "Enter…", "Click…", "Select…", "Sign…".
- **Numbered lists** for the action sequence; **bold** the field/button names exactly as they appear on
  screen.
- **No SAP internals** — no FM names, characteristics, NIDs, or config. Those live in the Functional Spec.
- Consistent per-XStep heading numbering that matches the phase (`4.<phase>.<step>`).
- Standard footer (copyright / page number) and a **Revision History** table (Version / Description /
  Author / Date).
- Keep each XStep sub-section short (a handful of steps) — one screen of actions + its screenshot.

---

## 12. Generation workflow (how to build one)

1. **Get the recipe's ordered XStep tree** (phases → XSteps) — SAP recipe or the EBR phase plan.
2. **Emit the boilerplate front matter** (§4) with the recipe name / plant substituted.
3. **For each phase, for each XStep in order:** emit a numbered sub-section; run the **element→sentence
   engine** (§5) over the XStep's ordered elements to produce the steps; insert the screenshot (§7).
4. **Apply the client variant** (§9) and **consolidate repeats** (§10).
5. **Add Revision History**; build the ToC.
6. Output `.docx` (controlled format) — and, if useful for review, a PDF via the shared HTML→PDF pipeline.
7. **Verify against a real Phase 1 WI** as the golden reference (regenerate *Calculation & Sampling* and
   diff the step wording) before pointing the generator at a new recipe.

The engine is deterministic: same XStep definitions + same recipe order → same WI. Wording changes are
one edit to the §5 templates, not a per-document rewrite.

---

## 13. Quick checklist for a new Work Instruction

- [ ] Obtain the **master recipe XStep order** (phases → XSteps).
- [ ] Reuse the **boilerplate** Purpose / Overview / Navigation / Master Recipe EBR (swap recipe + plant).
- [ ] One **numbered sub-section per XStep**, grouped by phase, in recipe order.
- [ ] Generate steps via the **element→sentence engine** — one instruction per interactive element, in order.
- [ ] Use the **client variant** of each block (e.g. AZ Calibration Due Date), not the generic one.
- [ ] Document repeated activities **once** (Add Row / per-cycle), not per repetition.
- [ ] **Performed By** → **Witnessed By (different user)** → step locked, on every data step.
- [ ] Screenshot per XStep (mock-up PNG for draft; filled executed-EBR for final).
- [ ] Merge **Input Data Shortlist** values for realistic examples.
- [ ] Revision History + ToC.
- [ ] **Diff against a real Phase 1 WI** to validate wording before scaling.
