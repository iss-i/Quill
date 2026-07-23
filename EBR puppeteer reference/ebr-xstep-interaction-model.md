---
name: ebr-xstep-interaction-model
description: "How to drive the SiMPL EBR recipe-sheet XStep forms (inputs, Enter-commit, validation popups)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 80737baf-30bf-45b8-b087-42737643f851
---

The EBR recipe sheet renders inside the iframe `iframe[id$="--piSheetFrame"]` (target it with `--frame piSheet`). It is legacy `_bfw_`-framework ABAP HTML, NOT clean SAPUI5, so:

- **Every input shares `id="_bfw_field_"`** with no name/aria-label/placeholder/`<label>`. Locate cells by GEOMETRY: find the header label's screen rect, then the editable input(s) beneath it (`findCellInput`). Form fields (Total Volume Added, Performed By, the Cryoprotectant Required? dropdown) are label-left / control-right — locate by the label leaf then the control to its right (strategy 5 in `findFieldByLabel`, `selectByLabel`).
- **Enter commits every input AND dropdown.** Without Enter the value does not register. A committed numeric reformats to 3 decimals ("2" → "2.000"); an un-reformatted value means it did not commit. `typeIntoHandle` presses Enter by default.
- **Validation state is the input's CSS class:** `...ContentWrapperWarning` / `...Error` / `...Success` (amber border = warning). No message-strip text.

**Out-of-range / invalid value triggers a TWO-popup dance (both must be handled):**
1. A SAPUI5 **"Properties"** dialog in the TOP document (Accept / Reject buttons, e.g. `#__button32`). Click **Reject** to discard an invalid value (Accept records it as a deviation — committed but flagged WARNING). It does NOT match `.sapMDialog`/`[role=dialog]`; find it by the Accept/Reject button text.
2. Then a **"Notifications"** `.sapMPopover` anchored to the bottom-left ⚠ icon ("Error — Value X was rejected") with an **X** close button (`aria-label="Close"`, icon-only — no text). Must be X'd off.

Real TMA-XStep labels (differ from the PDF/test JSON): **Amt. of Cryoprotectant Added** (not "Amount of..."), **Total Volume Added** (not "Total Volume of Cryoprotectant Added"), **UoM = ml** (lowercase), plus a required **Cryoprotectant Required?** dropdown (Select/Yes/No/N/A) and a Get Time / Time Cryoprotectant Added field. No "Maximum Qty" column on order 1005076. Total Volume Added stays empty until (likely) Save.

Setup note: on macOS `config.ts` only probes Windows browser paths and resolves `executablePath` eagerly even for probe/drive (which only attach to the running browser) — so `CHROME_PATH` must be set in `.env`. Related: [[ebr-puppeteer-tooling]]
