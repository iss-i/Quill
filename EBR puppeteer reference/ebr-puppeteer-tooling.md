---
name: ebr-puppeteer-tooling
description: "The probe/drive/eval tooling for exploring and driving the EBR app, and what it can/can't do"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 80737baf-30bf-45b8-b087-42737643f851
---

EBRPuppeteer drives the SiMPL EBR Fiori app via puppeteer-core. Two entry points:
- `npm start -- <order> [recipeAddress]` launches Chrome, logs in, navigates to the recipe, stays open. Writes the CDP endpoint to `.browser-endpoint`.
- `npm run drive -- <cmd>` and `npm run eval -- <expr|file>` ATTACH to that running browser via the endpoint.

Key exploration tool: **`npm run eval -- --frame piSheet "<expr>"`** runs arbitrary JS in the recipe iframe and returns JSON — this is the workhorse for inspecting/measuring the sheet. Everything was discoverable this way; screenshots are optional (only for visual ambiguity).

`drive` verbs (all take `--frame piSheet` to target the sheet): click, clickText, typeInto, read, setCell <col> <row> <val>, getCell, setSelect <label> <val>, plus the high-level sign/gotoRecipe/etc. Locators live in `src/locators.ts`, frame resolution in `src/frames.ts`.

Known tooling gaps still open (as of this work): `setCell` does not yet auto-handle the two validation popups; `clickText`/`findByText` only match visible text, not `aria-label`/`title` (so icon-only buttons like the Notifications Close X need a CSS selector); the `.sapMDialog` popup detectors miss the "Properties"/"Notifications" popups. See [[ebr-xstep-interaction-model]] for the popup flow and the legacy-ABAP field details.
