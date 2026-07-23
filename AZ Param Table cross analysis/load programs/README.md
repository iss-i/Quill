# PPTable load programs (DE1 100 · package ZSMPL_AZP2)

One ABAP load report per parameter table. Each reads a **delimited text file —
comma (`.csv`) or tab (`.txt`), auto-detected — as UTF-8** and upserts it into
the table. Columns are matched to table fields **by header name (row 1)**, so
column order doesn't matter and extra columns are ignored. Excel `"quoted"`
fields are handled, so values containing a comma (e.g. `AZDXXXX, INT-XXX`)
survive — you can `Save As → CSV UTF-8` **or** `Text (Tab delimited)`.

Modeled on the proven `ZCPPR_PARAM_TABLE_DATA_LOAD` (comma split, codepage
4110), extended with header-name mapping + quoted-field handling.

| Program | Target table | Description |
|---|---|---|
| `ZSMPL_PP_LOAD_UOP`   | `ZTC_PP_UOP`   | Unit Operation master |
| `ZSMPL_PP_LOAD_RES`   | `ZTC_PP_RES`   | Resource master |
| `ZSMPL_PP_LOAD_PARAM` | `ZTC_PP_PARAM` | Parameter catalog |
| `ZSMPL_PP_LOAD_PVAL`  | `ZTC_PP_PVAL`  | Parameter values (versioned) |
| `ZSMPL_PP_DELETE_DATA` | all four | **Deletes** data — clears the tables so a load can be re-run |

## Deleting (ZSMPL_PP_DELETE_DATA)
Clears loaded rows from all four tables (current client). Safety:
- **`p_test` defaults ON** — simulates and reports how many rows *would* go.
- Actual deletion needs `p_test` **off** *and* `p_conf` (Confirm deletion) **on**.
- Per-table checkboxes; optional `s_uop` scope (leave empty = every row).
- Deletes in dependency order **PVAL → PARAM → RES → UOP**, then commits.

Run it in test mode first and check the counts match what you expect.

## How to create them in SAP
These are source files only — I don't have tooling to create Z reports in
DE1 100. To install each:
1. `SE38` → program name (e.g. `ZSMPL_PP_LOAD_UOP`) → **Create** → type
   *Executable program*, **package `ZSMPL_AZP2`**, assign a transport.
2. Paste the corresponding `.abap` file contents, **Save**, **Activate**.
   (Or create via ADT / `abapGit`.)

## Selection screen (all four)
- **p_file** — the tab-delimited file (F4 file picker provided).
- **p_head** — leading rows to skip; row 1 must be the header (default `1`).
- **p_del**  — delete ALL existing rows before load (update mode only).
- **p_test** — **default ON**; simulates and prints a count without writing.
  Untick to commit.

Output is a short log: rows read / new / existing / errors.

## Field handling
- Upsert via `MODIFY` keyed by each table's primary key.
- `MANDT` is set by the system; `CREATED_BY/ON` + `CHANGED_BY/ON`
  (PARAM/PVAL) are stamped by the program — CREATED_ is preserved on updates.
- Dates (`VALID_FROM`, `VALID_TO`) accept `YYYY-MM-DD` or `YYYYMMDD`.
- `MATNR` runs through the MATN1 input conversion; `*` (scope wildcard) is
  kept verbatim.
- `IS_CALC` / `TOOL_READY` accept `X`/`Y`/`Yes`/`True`/`1` → `X`, else blank.

## Loading the converted Phase-2 data
The workbook `../Phase2 Parameters in PPTable_v2 Format.xlsx` already has
`ZPP_PARAM` and `ZPP_PVAL` sheets in these tables' field names — save each
sheet as tab-delimited text and run the matching loader.

### Caveats to resolve before a real load
- **PARAM_ID is CHAR30** in the table (the design/retrieval spec said CHAR40).
  A few converted PARAM_IDs exceed 30 chars (e.g.
  `BIO_ANTIFOAM_4102604_MANUAL_REQ_QTY` = 35) and will be **truncated** —
  shorten those identifiers first.
- **`UOP_ID`** in the converted data is a placeholder (`INOCULUM` / `BIOREACTOR`).
  Confirm the real unit-op codes (and that they exist in `ZTC_PP_UOP`) before
  loading `ZTC_PP_PARAM` / `ZTC_PP_PVAL`.
- Load order (referential sanity): `UOP` → `RES` → `PARAM` → `PVAL`.
