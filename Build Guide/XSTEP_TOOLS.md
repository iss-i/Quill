# XStep MCP Tools

Reference for every `xs_*` tool exposed by the SapFractal MCP server. These are the tools an AI agent (Claude Code, Claude Desktop, etc.) calls to read and mutate cmxsvn xsteps. The same operations are also available over HTTP via `/api/xs/*` — see [XSTEP_API.md](XSTEP_API.md) for that surface.

Source of truth: [backend/src/mcp/tools/xs.ts](../../backend/src/mcp/tools/xs.ts). When this doc disagrees with the file, trust the file.

---

## Quick reference

**Discovery & read**

| Tool | Purpose |
|---|---|
| [`xs_folder_tree`](#xs_folder_tree) | Browse the cmxsvn folder hierarchy (CMX_XSR_DB_FOLD) |
| [`xs_find`](#xs_find) | Substring search by item stext |
| [`xs_get_metadata`](#xs_get_metadata) | Item row + version history |
| [`xs_get_version`](#xs_get_version) | Full content of one version (flat tree) |
| [`xs_get_snapshot`](#xs_get_snapshot) | GUI-shaped JSON snapshot (nested tree, typed rows) |
| [`xs_diff_snapshots`](#xs_diff_snapshots) | Structured diff between two snapshots |
| [`xs_get_folder_contents`](#xs_get_folder_contents) | Bulk read of every xstep under a folder |
| [`xs_list_children`](#xs_list_children) | Direct or deep children of a node |
| [`xs_list_parameters`](#xs_list_parameters) | Full parameter config on a T/S/R node |
| [`xs_get_instruction`](#xs_get_instruction) | Unified instruction reader — auto-detects table / process-message, falls back to raw |
| [`xs_search_instructions`](#xs_search_instructions) | Find instructions by (domain, value) anywhere in the repo |
| [`xs_check_semantic`](#xs_check_semantic) | Run the PI Interpreter's validator |

**Xstep lifecycle**

| Tool | Purpose |
|---|---|
| [`xs_clone_xstep`](#xs_clone_xstep) | Deep-copy an existing xstep |
| [`xs_delete_xstep`](#xs_delete_xstep) | Remove an xstep |
| [`xs_rename_xstep`](#xs_rename_xstep) | Rename — updates both folder browser title and inside-xstep titlebar |
| [`xs_rename_item`](#xs_rename_item) | Primitive: update folder browser title only (CMX_XSR_DB_ITEM.STEXT) |

**Tree-structure mutations**

| Tool | Purpose |
|---|---|
| [`xs_add_step`](#xs_add_step) | Add an S-node child |
| [`xs_add_reference`](#xs_add_reference) | Add an R-link child |
| [`xs_update_reference`](#xs_update_reference) | Repoint or open/close an R-link |
| [`xs_update_node_attrs`](#xs_update_node_attrs) | Flat attrs on T or S |
| [`xs_delete_node`](#xs_delete_node) | Remove a P / I / R node |

**Parameters**

| Tool | Purpose |
|---|---|
| [`xs_add_parameters`](#xs_add_parameters) | Batch attach/upsert N params on one owner |
| [`xs_update_parameter`](#xs_update_parameter) | Per-parameter partial update |

**Instructions (raw)**

| Tool | Purpose |
|---|---|
| [`xs_add_instruction`](#xs_add_instruction) | Add I-node with raw `fields[]` |
| [`xs_update_instruction`](#xs_update_instruction) | SET_CONTENT replace |

**Table instructions (typed)**

| Tool | Purpose |
|---|---|
| [`xs_add_table_instruction`](#xs_add_table_instruction) | Add a table from typed columns. `repeated: false` for a non-iterating grouping. |
| [`xs_update_table_instruction`](#xs_update_table_instruction) | Replace columns in place |
| [`xs_modify_rows`](#xs_modify_rows) | Edit rows of a table — insert / update / delete / reorder, batched in one read-write cycle |

**Process messages**

| Tool | Purpose |
|---|---|
| [`xs_add_process_message`](#xs_add_process_message) | PI_CONS / ZPICONS-style message instruction |
| [`xs_update_process_message`](#xs_update_process_message) | Replace content |
| [`xs_list_process_message_categories`](#xs_list_process_message_categories) | Discover valid PPPI_MESSAGE_CATEGORY values from O13C |
| [`xs_get_process_message_category_detail`](#xs_get_process_message_category_detail) | Full O13C contract for one category |

**Catalogs**

| Tool | Purpose |
|---|---|
| [`xs_instruction_recipes`](#xs_instruction_recipes) | Canonical field shapes per instruction kind |
| [`xs_list_parameter_types`](#xs_list_parameter_types) | Usage-ranked domain catalog |

**Classification (CABN)**

| Tool | Purpose |
|---|---|
| [`xs_add_characteristic`](#xs_add_characteristic) | Create CABN + CAWN/CAWNT values |
| [`xs_edit_characteristic_values`](#xs_edit_characteristic_values) | Add/remove values on existing CABN |

**Z function modules (whitelisted FUGR)**

| Tool | Purpose |
|---|---|
| [`xs_create_function_module`](#xs_create_function_module) | Create + activate a Z FM |
| [`xs_update_function_module`](#xs_update_function_module) | Delete + recreate to update |
| [`xs_get_function_module`](#xs_get_function_module) | Read FM interface + body |
| [`xs_delete_function_module`](#xs_delete_function_module) | Irreversible delete |

---

## Conventions

### Common inputs

- **`connection`** — required on every tool that touches SAP. The name of a profile in `connections.json` (e.g. `DE2_900`, `DE2_903`). Call `list_connections` if unsure.
- **`item_id`** — `CMX_XSR_DB_ITEM.ITEM_ID`. The xstep identity. Discoverable via `xs_folder_tree` or `xs_find`.
- **`root_nid`** — the live tree root, `CMX_XSR_DB_VERS.ROOT_ID`. **Not the same as `template_root_id`**. Many mutations need this; pass `item_id` to read tools instead and they resolve it for you.
- **`node_nid`** — NID of any node inside the tree. Returned by `xs_list_children`.

### NTYPE codes

```
T  root (the xstep itself)
S  step
I  instruction
R  reference (link to another xstep)
P  parameter
D  destination
G  grouping
X  internal grouping/repeating marker (read-only)
```

### Mutation scope

Mutating tools are folder-whitelisted on the SAP side. Currently only the **AI XA** folder (`fJVsUCCY7z6Ma4PXtWjXzG`) is accepted as a destination. Reads work against any folder.

### Response envelope

Most mutation tools wrap responses as:

```jsonc
// success
{ "ok": true, "result": { ... } }

// SAP-side failure
{ "ok": false, "error": "<message from ABAP>" }
```

Read tools usually return their payload directly (no envelope). Responses are hard-capped at `MCP_MAX_RESPONSE_BYTES` (default 2 MB) — large pages get a `… (truncated at N bytes)` suffix.

### Parameter naming

`CMX_XS_DB_PS.NAME` is `C(10)`. SAP truncates silently. Every tool that accepts a parameter name enforces `.max(10)` up front. PPPI_VARIABLE references inside instruction fields are also rejected over 10 chars.

### NID vs OID

- **NID** = stable slot identifier. Survives edits.
- **OID** = content version. Re-minted on every change.
- Parameter NIDs are *session-transient* — they can change between HTTP sessions even on the same xstep. Use `param_name` instead of `node_nid` for parameter deletes (see [`xs_delete_node`](#xs_delete_node)).

### Active version

For tools that accept either `item_id` or `version_id`, the server picks an "active" version when given an item:

1. Released status (`I8504`) wins
2. Otherwise the highest 4-digit numeric `VERS_NAME`
3. Otherwise an ambiguity error — pass `version_id` explicitly

---

# Discovery & read

## xs_folder_tree

Browse the cmxsvn folder structure (`CMX_XSR_DB_FOLD`). Read-only. Scoped to `namespace=SAP, repository=XSV`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `folder_id` | no | Subtree root. Omit for the entire repo. |
| `include_items` | no | Default `true`. Set `false` for folders-only — much smaller payload. |
| `max_depth` | no | Default 10, range 1–50. `1` = root only. |
| `max_results` | no | Total node budget across the response (folders + items). When exceeded, walk halts; `truncated_at[]` lists where to drill in. |

**Returns**

```jsonc
{
  total_folders: number,
  total_items:   number,
  roots:         FolderNode[],     // top-level subtree(s) from folder_id
  ancestors:     Ancestor[],       // parent chain when folder_id supplied
  truncated_at:  { folder_id, ... }[]
}
```

**Use it to** find `item_id`s before `xs_clone_xstep`, verify deletes, or peek at folder structure.

**Gotchas**

- Default cap is high — large repos can produce multi-MB JSON. Set `max_results` to bound.
- When drilling in via a `truncated_at` entry, pass its `folder_id` back as `folder_id` to expand that subtree.

---

## xs_find

Substring search against `CMX_XSR_DB_ITEM.STEXT`. One cheap SELECT vs walking the whole folder tree.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Case-sensitive. ABAP `%` wildcards honored; bare strings auto-wrap as `%name%`. |
| `folder_id` | no | Scope to one folder. **Does not recurse.** |
| `limit` | no | Default 50, max 200. |

**Returns**

```jsonc
{
  count: number,
  hits: [
    { item_id, stext, parent_folder_id, parent_folder_stext },
    ...
  ]
}
```

**Use it to** find xsteps by partial name when you don't want to walk a folder tree. Pass `item_id` from results to `xs_list_children` or `xs_get_metadata`.

---

## xs_get_metadata

Repository-level metadata for one item — identity, provenance, version history. Pure SQL against cmxsvn tables.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | yes | |

**Returns**

```jsonc
{
  item_id,
  stext,
  parent_folder_id,
  parent_folder_stext,
  template_root_id,   // NOT root_nid
  ref_indicator,      // "X" = reference/overlay item
  namespace,
  repository,
  language,
  created_by,
  created_at,
  versions: [
    { version_id, root_id, vers_name, date_from, date_to, status_obj_id, modified_by, modified_at },
    ...
  ]
}
```

**Use it to** see when an xstep was last edited, find all versions, or detect reference items (`ref_indicator='X'`).

**Gotchas**

- `template_root_id` is the OID-anchor of the original template, **not** a tree root NID. For tree walks use `versions[].root_id`.

---

## xs_get_version

Full content of one xstep version — layout, parameters, instruction fields — in one shot. Walks cmxsvn tables directly (NREL / NOBJ / ROOT / STEP / INSTR / REF / PS / VS).

**Inputs** — supply exactly one:

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | one-of | Server picks the active version. |
| `version_id` | one-of | Read a specific version. |

**Returns**

```jsonc
{
  version: { ... metadata },
  nodes: [
    {
      nid, parent_nid, idx, depth, ntype, stext,
      root?: { ... },      // T-nodes
      step?: { ... },      // S-nodes
      instr?: {            // I-nodes
        type, category,
        fields: [{ pos, domain, value, state, langu }, ...]
      },
      ref?: { ... },       // R-nodes
      parameters?: [       // T / S / R nodes that own parameters
        { name, domain, ptype, stext, value, is_table, state, pmode, is_live },
        ...
      ]
    },
    ...
  ]
}
```

**Use it to** export a complete picture of an xstep for diff/inspection. Works on any version including frozen historical ones.

**Gotchas**

- P-type nodes are excluded from `nodes[]` — they're carried inline as `parameters[]` on their owner.
- Ambiguous `item_id` (multiple Released versions, or none Released and multiple non-numeric VERS_NAMEs) returns `{ ok: false }` — retry with explicit `version_id`.
- Output can be very large (10-200K lines on complex xsteps). Use [`xs_get_snapshot`](#xs_get_snapshot) or paging tools when payload size matters.

---

## xs_get_snapshot

GUI-shaped JSON snapshot — same source data as `xs_get_version` but with `children[]` nested under each parent (not pointers) and I-nodes split into typed `rows[]` mirroring the cmxsvn `<Grouping>` view.

**Inputs** — supply exactly one of `item_id` / `version_id`:

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | one-of | Highest VERS_NAME picked. |
| `version_id` | one-of | |
| `include_metadata` | no | Default `true`. Set `false` to strip `idx`, `depth`, `pos`, `langu`, `start` for a more diff-friendly snapshot. |

**Returns**

```jsonc
{
  version: { ... },
  root: {
    nid, ntype, stext,
    root: { ... },
    parameters: [ ... ],
    children: [
      { ntype: "S", step: { ... }, parameters: [ ... ], children: [
        { ntype: "I", instr: { ... fields, rows: [
          { kind: "IN" | "OUT" | "BTN" | "FUNC" | "CMD" | "SIG" | "PMSG" | "HTML" | "OTHER", label, fields }
        ]} },
        ...
      ]},
      ...
    ]
  },
  totals: { nodes, instructions, references, steps, parameters }
}
```

**Use it to** hand off a complete xstep to another agent for inspection, or as a diff input. The nested shape is easier to read than `xs_get_version`'s flat `nodes[]` + `parent_nid`.

---

## xs_diff_snapshots

Structured diff between two xstep snapshots. NID-blind — nodes match by sibling position + ntype, parameters by NAME, instruction rows by position. Instruction-field NIDs that get re-minted on clone are suppressed by default.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `a_item_id` / `a_version_id` | one-of | Side A |
| `b_item_id` / `b_version_id` | one-of | Side B |
| `include_metadata` | no | Default `true`. |
| `ignore_nids` | no | Default `true`. Suppress 22-char framework NID diffs that come from cloning. Set `false` when debugging clone behavior. |

**Returns**

```jsonc
{
  identical: boolean,
  a: { item_id?, version_id, ... },
  b: { item_id?, version_id, ... },
  summary: {
    nodes_added, nodes_removed, nodes_changed,
    params_changed, instructions_changed,
    rows_changed, attrs_changed
  },
  changed_nodes: [
    {
      path: "T(Clone) → S(Main) → I(Setup Functions)",
      changes: [
        { kind: "attr"|"param"|"row"|"field"|"stext", field, old, new },
        ...
      ],
      children_added: [...],
      children_removed: [...]
    },
    ...
  ]
}
```

**Use it to** compare two xsteps (e.g. an iteration vs. its previous version) and produce a punch list of mutations. Designed so an LLM can read the diff and emit `xs_*` calls to bring one side to match the other.

---

## xs_get_folder_contents

Bulk read of every xstep under a folder (recursive), each with full active version content. Batched internally — ~O(max tree depth) NREL round-trips vs O(N×depth) of looping `xs_get_version`. Typical 50-200× speedup.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `folder_id` | yes | Recursive walk starts here. |
| `offset` | no | Default 0. Items sorted by `(parent_folder_stext, stext, item_id)` — pagination is stable. |
| `limit` | no | Default 50, max 500. Real gate is total payload size. |
| `include_attributes` | no | Default `true`. Set `false` for structure-only (nodes are `{nid, parent_nid, idx, depth, ntype}` only). |

**Returns**

```jsonc
{
  folder_id, folder_stext,
  total_items_in_folder,
  pagination: { offset, limit, returned, next_offset },
  items: [
    { item_id, stext, parent_folder_id, parent_folder_stext, version, node_count, nodes[] },
    ...
  ],
  skipped_no_version: [...],
  skipped_ambiguous_version: [...]
}
```

**Use it to** survey a whole folder in one call. Watch `items[].node_count` — deep trees can blow `MCP_MAX_RESPONSE_BYTES` at low item counts. If you see `(truncated at … bytes)`, drop `limit` and page.

---

## xs_list_children

List children of an xstep node — direct or recursive.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | one-of | Server resolves `root_nid` for you. |
| `root_nid` | one-of | `CMX_XSR_DB_VERS.ROOT_ID`. **Not `TEMPLATE_ROOT_ID`.** |
| `node_nid` | no | Walk a deeper node instead of the root. Must be reachable from `root_nid`. |
| `max_depth` | no | Default 1. For an entire xstep dump (root + step + instructions etc.) try `max_depth=3`. |

**Returns**

```jsonc
{
  root_nid,
  node_nid,    // the node walked under (== root_nid if not passed)
  children: [
    { nid, parent_nid, ntype, stext, depth },
    ...
  ]
}
```

**Use it to** get NIDs for subsequent `xs_*` mutation calls, or to confirm tree shape.

**Gotchas**

- Parameter `stext` here is just the name (e.g. `LT_BAGNO`) — call `xs_list_parameters` for full config.

---

## xs_list_parameters

Full parameter detail for one owner node (T, S, or R). Use this when `xs_list_children` showed parameters by name only and you need the actual config.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `node_nid` | yes | T / S / R NID. |

**Returns**

```jsonc
{
  node_nid,
  count,
  parameters: [
    { name, domain, ptype, stext, value, is_table, state, pmode, is_live },
    ...
  ]
}
```

`ptype` codes: `L` local, `I` input, `O` output, `E` exchange.

**Use it to** see actual parameter properties (e.g. `is_table=true` for tabular columns, `pmode=F` for fixed values) before editing.

---

## xs_get_instruction

Unified reader for any I-type instruction. Auto-detects table / process-message shapes and returns the typed spec; falls back to the raw flat fields[]. Subsumes the old `xs_get_table_instruction` and `xs_get_process_message` tools.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `instr_nid` | yes | I-type NID. Get from `xs_list_children` (filter `ntype="I"`). |
| `parse` | no | `"auto"` (default) / `"raw"` / `"table"` / `"process_message"`. See [parse modes](#parse-modes). |

**Returns**

```jsonc
{
  ok: true,
  result: {
    instr_nid,
    stext,
    ntype,
    kind: "raw" | "table" | "process_message",   // what the parser actually returned
    fields: [{ pos, domain, value }, ...],       // always present — raw flat view
    spec?:  TableInstructionSpec | ProcessMessageSpec   // present when kind != "raw"
  }
}
```

`spec` shape when `kind: "table"`:

```jsonc
{
  rows_min?, rows_max?, input_group?,
  columns: [
    { kind: "input"|"output"|"button"|"function_call"|"signature"|"conditional_rule"|"process_message"|"raw", ... },
    ...
  ]
}
```

`spec` shape when `kind: "process_message"`:

```jsonc
{
  category,
  tabular?,
  display_columns?: [{ label, variable }, ...],
  bindings:        [{ variable, field }, ...]
}
```

### Parse modes

| Mode | Behavior |
|---|---|
| `"auto"` (default) | Sniff: if any field carries `PPPI_MESSAGE_CATEGORY` → run process-message parser; else if `field[0]` is `PPPI_DATA_REQUEST_TYPE=REPEATED` → run table parser; else return raw. If the chosen parser errors, falls back to raw — auto mode never returns `ok: false`. |
| `"raw"` | Skip the typed parsers entirely. Returns `kind: "raw"` with `fields[]` only. |
| `"table"` | Force the table parser. Errors `NOT_A_TABLE` on a non-table instruction. |
| `"process_message"` | Force the process-message parser. Errors `NOT_A_PROCESS_MESSAGE` if `PPPI_MESSAGE_CATEGORY` is absent. |

**Use it for** read-modify-write cycles. `spec` matches the input shape of [`xs_update_table_instruction`](#xs_update_table_instruction) / [`xs_update_process_message`](#xs_update_process_message) — round-trips cleanly. `fields[]` is always present so an agent can fall back to raw editing via [`xs_update_instruction`](#xs_update_instruction).

**Gotchas**

- Unrecognized column shapes round-trip as `kind: "raw"` in the table parser's column list, so an agent can still edit the columns it understands.
- Validation FMs: parser auto-detects `PPPI_STRING_VARIABLE='X'` sentinel and fills `validation.validated_value_param`. `build(parse(fields))` round-trips.
- Tabular process messages (`REPEATED + PPPI_MESSAGE_CATEGORY`) resolve as `process_message` under auto-detect — `MESSAGE_CATEGORY` wins over `REPEATED`.
- **NID-shaped `PPPI_LONG_FORMULA` values are framework handles, not formula text.** When a `PPPI_LONG_FORMULA` value is a 22-char base64-like NID (e.g. `fJVsUCCY7z6Nskf8xa61zG`), it's a pointer to a separately-stored G-node holding the actual expression. The result envelope includes `formula_handles[]` (positions + values) plus `formula_handles_hint` whenever any are detected. **Do NOT pass those values back through `xs_update_instruction` / `xs_update_table_instruction` / `xs_modify_rows`** — the writers refuse NID-shaped values with `error: "NID_SHAPED_FORMULA_VALUES"`. Substitute the inline expression text first. Standard Setup Functions inlines: DEACTIVATE → `LV_ACTIVE <> 1`, ACTIVATE → `LV_ACTIVE = 1`, LOCK → `EV_LOCK = 1`, UNLOCK → `EV_LOCK <> 1`.

---

## xs_search_instructions

Find instructions across the repository whose field set contains a `(domain, value)` match.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `domain` | yes | Domain name to look for in `CMX_XS_DB_VS.DOMNAME` (e.g. `PPPI_BUTTON_TEXT`, `PPPI_FUNCTION_NAME`, `PPPI_EVENT`, `PPPI_LONG_FORMULA`). |
| `value_pattern` | no | SQL `LIKE` pattern on the matched value. Bare strings auto-wrap as `%pattern%`. |
| `limit` | no | Default 10, max 50. |

**Returns**

```jsonc
{
  count,
  matches: [
    {
      item_id, instr_nid, stext, ntype,
      fields: [{ pos, domain, value }, ...]   // ALL fields of the matching instruction, not just the matched one
    },
    ...
  ]
}
```

**Use cases**

- Find all buttons: `domain=PPPI_BUTTON_TEXT`
- FM calls to a specific function: `domain=PPPI_FUNCTION_NAME, value_pattern=ZSMPL_FM_*`
- Formulas using SUM aggregation: `domain=PPPI_LONG_FORMULA, value_pattern=[SUM]`
- Discover event handlers: `domain=PPPI_EVENT`

Each match includes the whole instruction's `fields[]`, so payloads grow fast — keep `limit` low.

---

## xs_check_semantic

Run the PI Interpreter's semantic validator on an xstep — same check cmxsvn's Simulate menu surfaces.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` / `root_nid` | one-of | |
| `step_nid` | no | Scope to a deeper S-step. Omit for the whole xstep from root. |
| `check_level` | no | `CMX_XS_CHECK_LEVEL` byte. Omit for framework default. |
| `include_symbols` | no | Default `false`. Returns the resolved symbol table — 50-200+ rows; enable only for debugging variable resolution. |

**Returns**

```jsonc
{
  root_nid, step_nid,
  message_count,
  messages: [
    { severity, msgid, msgno, msgv1, msgv2, msgv3, msgv4, message_text, nid? },
    ...
  ],
  symbols?: [ ... ]
}
```

**Catches**

- Dangling parameter refs
- Missing `PPPI_VARIABLE` values
- Invalid characteristic names
- FM signature mismatches
- Other editor-level errors

**Doesn't catch**

- Render-time issues (e.g. dropdown CAWN values incompatible with a validation FM's expected format)
- Runtime value-validation FM behaviour

`messages` is empty when the xstep is clean.

---

# Xstep lifecycle

## xs_clone_xstep

Clone an existing xstep into the destination folder. Deep-copies the tree via `IF_CMX_XS_CONVERTER` XML round-trip — the same path cmxsvn import uses.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `source_item_id` | yes | Any folder — only the destination is whitelisted. |
| `title` | yes | Max 40 chars. |
| `folder_id` | no | Defaults to the server-configured destination. |

**Returns** `{ item_id, version_id, root_id }`.

**Caveat:** R-children pointing at other library items are preserved **by reference** — they continue to point at the same external items, not freshly-copied versions. Use [`xs_update_reference`](#xs_update_reference) per child to repoint if needed.

---

## xs_delete_xstep

Remove an xstep from the destination folder. Folder-whitelisted on the SAP side.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | yes | Must live in a whitelisted folder. |

**Effects:** removes `CMX_XSR_DB_ITEM` + all `CMX_XSR_DB_VERS` rows; best-effort drops the underlying `CMX_XS` tree(s) via `IF_CMX_XS_LIBRARY->DELETE_TREE_BY_NID`.

**Use for** cleaning up xsteps that came out broken from earlier create/clone attempts.

---

## xs_rename_xstep

Rename an xstep — updates **both** `CMX_XSR_DB_ITEM.STEXT` (folder browser title) and `CMX_XS_DB_ROOT.STEXT` (inside-xstep titlebar) in one call. Composite over `xs_rename_item` + `xs_update_node_attrs(stext)`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | yes | Server resolves `root_nid` from `CMX_XSR_DB_VERS` automatically. |
| `new_stext` | yes | Max 40 chars. Applied to both fields. |

**Returns** on full success:
```jsonc
{ ok: true, result: { renamed: item_id, stext, item_updated: true, root_updated: true } }
```

**Not atomic.** The two SAP fields are independent transactions. Item update runs first; if it fails, nothing changed (full error envelope). If item update succeeds but root update fails, the response is **partial-success**:

```jsonc
{
  ok: false,
  result: { renamed: item_id, stext, item_updated: true, root_updated: false },
  error: "<sap message>",
  hint: "Folder browser title was updated, but the inside-xstep titlebar was not. Retry xs_update_node_attrs(root_nid=<same as node_nid>, stext=<new_stext>) directly to finish."
}
```

Same folder whitelist as [`xs_delete_xstep`](#xs_delete_xstep).

**Prefer this over the primitives.** Every fresh clone arrives with `ITEM.STEXT == ROOT.STEXT`; every rename has to maintain that. Using one primitive in isolation leaves the two out of sync — a footgun easy to miss because both still display normally, just labeled differently.

---

## xs_rename_item

**Primitive.** Updates `CMX_XSR_DB_ITEM.STEXT` (folder browser title) ONLY. Use [`xs_rename_xstep`](#xs_rename_xstep) for the standard "rename this xstep" case.

This primitive exists for niche cases where the two title fields should intentionally diverge.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `item_id` | yes | |
| `new_stext` | yes | Max 40 chars. |

Idempotent. Same folder whitelist as `xs_delete_xstep`.

---

# Tree-structure mutations

## xs_add_step

Append (or insert-after) a new S-type child step under `parent_nid`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | May equal `parent_nid` when attaching directly under the root. |
| `parent_nid` | yes | T or S. |
| `stext` | yes | |
| `after_nid` | no | Insert after this existing sibling NID. Otherwise appended. |

**Returns** `{ nid }`.

The new step is empty — caller mutates further via the returned NID.

---

## xs_add_reference

Insert a new R-type child (link to another xstep).

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `target_item_id` | yes | Namespace/repository resolved server-side from the items table. |
| `parent_nid` | no | Defaults to root (standard for header/signature refs). Pass T or S NID to nest deeper. |
| `after_nid` | no | Sibling position. Otherwise appended. |

**Returns** `{ nid }`.

---

## xs_update_reference

Update an R-type reference. Both inputs optional.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `ref_nid` | yes | |
| `target_item_id` | no | Repoint — namespace/repository resolved server-side. |
| `open_state` | no | `"open_final"` (CO_OPEN_FINAL='X', fully inlined), `"open_temp"` (CO_OPEN_TEMP='+'), or `"close"`. |

**Idempotent.** `open_final`↔`open_temp` goes via `close()→open()` internally.

**Use when** a sub-xstep gets a new released version and the parent should repoint. To remove the reference entirely, use [`xs_delete_node`](#xs_delete_node).

---

## xs_update_node_attrs

Update flat attrs on T (root) or S (step). Each field independent, applied if non-empty.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | May equal `node_nid` when updating the root itself. |
| `node_nid` | yes | T or S. Other ntypes rejected. |
| `stext` | no | Goes through framework setter. |
| `dst_namespace`, `dst_type`, `dst_location`, `dst_name` | no | Destination quartet. Framework `set_destination` via `create_node_destination(CMX_XS_W_DST_KEY)` — fires BAdIs / CLOG / cmxsvn-reader consistency. Read-modify-write: partial updates preserve other fields. |
| `gen_namespace`, `gen_name` | no | Generation. **STEP only.** Root has `GENERATION_MODE` instead, not yet exposed. Same framework path + read-modify-write as destination. Invalid (non-existent) generations are rejected by the framework master-data check. |
| `pred_mode` | no | Goes through `SET_PREDECESSOR_MODE`. |

**No clear primitives.** The framework rejects empty-key destinations/generations and exposes no `remove_destination` / `remove_generation` method — destinations and generations transition between values, not between "set" and "unset". Match SAP's design.

**Rename note.** Setting `stext` on a T-root updates the inside-xstep titlebar only — it does NOT touch the folder browser title (`CMX_XSR_DB_ITEM.STEXT`). For the standard "rename this xstep" case use [`xs_rename_xstep`](#xs_rename_xstep) which updates both.

---

## xs_delete_node

Remove a tree node by NID. Accepts P / I / R. T (whole xstep — use `xs_delete_xstep`) and S (would orphan children) are rejected.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `node_nid` | yes | P / I / R NID. **When `param_name` is set, this is reinterpreted as the OWNER NID** (see below). |
| `param_name` | no | For P deletes only. When set, `node_nid` is the owner (T/S/R) and the parameter is deleted by `(owner_nid, name)` without walking the framework tree. |

**Why `param_name` exists:** parameter NIDs aren't stable across HTTP sessions on a recently-edited xstep — by the time you call delete, the NID from a prior `xs_list_children` may be stale. The `(owner_nid, name)` pair IS stable.

**Rule of thumb:**
- P-deletes → always pass `param_name`
- I- and R-deletes → leave `param_name` unset

**Per-type caveats:**
- (P) Instructions whose `PPPI_VARIABLE` references the deleted name become dangling — cmxsvn shows "syntax error in process instruction" with an empty `<Grouping>`. Clean up or rebind referencing instructions first.
- (I) Parameters the instruction referenced become orphans (harmless — render as plain step parameters).
- (R) The referenced library item is untouched; only the link is removed.

---

# Parameters

## xs_add_parameters

Attach/upsert N parameters on **one** owner node in **one** edit session. Owner = T / S / R.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `owner_nid` | yes | T / S / R. All params target the same owner; for mixed owners, call once per owner. |
| `params[]` | yes | Ordered. Returned NIDs match this order. |
| `params[].name` | yes | Max 10 chars. Convention: `LV_` local, `IV_` input, `OV_` output. |
| `params[].domain` | yes | E.g. `PPPI_SHORT_TEXT`. Discover via [`xs_list_parameter_types`](#xs_list_parameter_types). |
| `params[].ptype` | no | Default `L` (local). Don't pair `I` with input-request — trips CMX_PII 006. |
| `params[].stext` | no | |
| `params[].value` | no | Default value. Converted to the param's domain on save. |
| `params[].is_table` | no | TRUE for params that back a table column. |

**Returns** `{ nids: [...] }` in the same order as `params`.

**Two-phase inside one session:**
1. Factory-create + set_parameter each spec
2. Re-lookup + `SET_VALUE` for each spec with a non-empty `value`

One save + one COMMIT.

**Why batch is the only path:** SAP wipes other text-domain inputs on the same node that aren't re-set in the same session. Single-param-per-call would silently destroy other inputs' values. **Always pass everything you want to keep.**

**Limitations** (vs. `xs_update_parameter`):

- `xs_add_parameters` can't preserve a parameter's existing `state` or `pmode` — those round-trip as defaults. For iteration patterns where you need to change one field without touching others, use [`xs_update_parameter`](#xs_update_parameter).

---

## xs_update_parameter

Per-parameter partial update — change one parameter's value/domain/state/pmode without touching any others on the same owner.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `owner_nid` | yes | T / S / R holding the parameter row. |
| `name` | yes | Max 10. |
| `domain` | no | New domain. Omit to keep. |
| `ptype` | no | New ptype. Omit to keep. |
| `stext` | no | |
| `value` | no | Empty string clears. |
| `state` | no | `'S'` set or `''` unvaluated. |
| `pmode` | no | `'F'` Fixed Value / `'A'` Auto / `'R'` Reference / `''` None. |
| `is_table` | no | |

**Returns** the merged spec that was persisted.

**Use for** iteration patterns like flipping `LV_UOM` "G" → "L" or setting `pmode="F"` on a default.

**Preserves `state` and `pmode`** through the round-trip — `xs_add_parameters` can't carry those.

---

# Instructions (raw)

## xs_add_instruction

Append/insert a process instruction under an S-step using raw `(domain, value)` fields.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `step_nid` | yes | S-type. |
| `stext` | yes | |
| `fields[]` | yes | At least one. |
| `fields[].domain` | yes | E.g. `PPPI_INPUT_REQUEST`. |
| `fields[].value` | yes | String; converted to the domain's wire type. |
| `type` | no | Defaults to `'0'`. Don't change unless you know why. |
| `after_nid` | no | Insert after this NID. Otherwise appended. |

**Returns** `{ nid }`.

**Input-request shape (most common):**

```jsonc
fields: [
  { domain: "PPPI_INPUT_REQUEST", value: "<label>" },
  { domain: "PPPI_VARIABLE",      value: "<param name>" },
  { domain: "PPPI_REQUESTED_VALUE", value: "<param domain>" }
]
```

**Important:** the `PPPI_VARIABLE` value MUST EXACTLY match a parameter's name as it lives in `CMX_XS_DB_PS`. Names are `C(10)` — anything over 10 chars is rejected up-front because the parameter it claims to reference can only exist with a name ≤ 10 chars. Call [`xs_add_parameters`](#xs_add_parameters) FIRST to create the param.

**For richer shapes, prefer the typed tools** ([`xs_add_table_instruction`](#xs_add_table_instruction) — also handles non-iterating groupings via `repeated: false`, [`xs_add_process_message`](#xs_add_process_message)).

---

## xs_update_instruction

Update an existing instruction. SET_CONTENT semantics — `fields` replaces the entire array, not a delta.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `instr_nid` | yes | I-type. |
| `stext` | no | Omit to keep existing. |
| `type` | no | Defaults `'0'`. |
| `fields[]` | no | Optional. If provided, REPLACES the entire existing field set. |

**Same C(10) guard on `PPPI_VARIABLE`** values as `xs_add_instruction`.

**Use for** fixing label typos, changing instruction kind (input_request → function_call by swapping fields), rebinding `PPPI_VARIABLE`. Omit `fields` for stext-only, omit `stext` for fields-only.

---

# Table instructions (typed)

## xs_add_table_instruction

Append a typed-columns instruction under an S-step. Two modes:

- **`repeated: true` (default)** — REPEATED table. Each `columns[i]` is a visible column populated per row; rows iterate. Server emits `header → column blocks → PPPI_INPUT_GROUP trailer`.
- **`repeated: false`** — non-iterating grouping. Each `columns[i]` renders ONCE as a stacked row under the instruction's stext. Use when the spec shows floating header fields above/beside a table, or any cluster of inputs/outputs that visually belong together but shouldn't iterate (e.g. Culture Weight's "Upper" section). Without this mode, callers fan out into N `xs_add_instruction` calls and cmxsvn renders N separate groupings — a common defect.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `step_nid` | yes | |
| `stext` | yes | |
| `repeated` | no | Default `true`. Set `false` for a non-iterating grouping. |
| `columns[]` | yes | Discriminated union — see below. In grouping mode (`repeated: false`), these are stacked rows. |
| `rows_min` | no | 3-digit string, default `"001"`. Ignored when `repeated: false`. |
| `rows_max` | no | 3-digit string, default `"999"`. Ignored when `repeated: false`. |
| `input_group` | no | Short name that visually bundles the columns. Conventionally the table's stext or a slug. |
| `after_nid` | no | |

**Returns** `{ nid, fields_count, fields }`.

**Backing params:** variable-owning columns need [`xs_add_parameters`](#xs_add_parameters) first. Use `is_table: true` in table mode (`repeated: true`), `is_table: false` in grouping mode (`repeated: false`).

### Column kinds

#### `input`

Operator-fillable cell.

```jsonc
{
  kind: "input",
  label: "Batch",                     // PPPI_INPUT_REQUEST
  variable: "LT_BATCH",               // PPPI_VARIABLE (≤10 chars; convention LT_ for tabular)
  domain: "PPPI_BATCH",               // PPPI_REQUESTED_VALUE
  default_from: "LV_PARTNO",          // optional, PPPI_DEFAULT_VARIABLE
  validation: { fm, bindings, validated_value_param? },
  text_for_invalid_node: "...",       // optional
  accept_invalid: "03",               // optional
  signature_strategy: "SAPPOCSS",     // rare, vestigial
  extra_fields: [...]                 // pass-through for unrecognized tails
}
```

#### `output`

Read-only display from a variable.

```jsonc
{ kind: "output", label: "Welder ID", variable: "LT_WELDID" }
```

Emits `PPPI_OUTPUT_TEXT` + `PPPI_OUTPUT_VARIABLE`.

#### `button` (legacy)

Click-only function call. Prefer `function_call`.

```jsonc
{
  kind: "button",
  label: "Get Welder",                // PPPI_BUTTON_TEXT
  fm: "ZSMPL_FM_GET_WELDER",          // PPPI_FUNCTION_NAME
  during_display: "0",                // optional, default "0"
  bindings: [ ... ]
}
```

#### `function_call` (unified)

Subsumes `button` and adds events + the `changing` direction. Use for row-sync FMs, signature commits, recalc handlers, or plain buttons.

```jsonc
{
  kind: "function_call",
  fm: "ZSMPL_FM_SET_LINE_INDEX",
  button_label: "Get Welder",         // optional — omit for invisible event-driven handler
  event: "TABLE.LINE_ADDED",          // optional — see event enum
  during_display: "0",
  bindings: [
    { direction: "in",       fm_param: "IM_ORDER",     variable: "LAV_ORDER" },
    { direction: "in",       fm_param: "IM_EQUIP_TYPE", constant: "M" },
    { direction: "out",      fm_param: "EX_EQUI",      variable: "LT_WELDID" },
    { direction: "changing", fm_param: "CT_INDEX",     variable: "LT_BAGNO" },
  ]
}
```

**Binding directions:**

- `in` → `PPPI_EXPORT_PARAMETER` (FM-side IMPORTING)
- `out` → `PPPI_IMPORT_PARAMETER` (FM-side EXPORTING)
- `changing` → `PPPI_CHANGING_PARAMETER` (bi-directional, FM reads AND writes)

**`var_kind`** on a binding controls the wire domain: `'string'` (default) → `PPPI_STRING_VARIABLE`, `'date'` → `PPPI_DATE_VARIABLE`, `'time'` → `PPPI_TIME_VARIABLE`, `'float'` → `PPPI_FLOAT_VARIABLE`.

**Event timing (SAP -ING vs -ED convention):**

- `-ING` fires BEFORE the action commits — use for cross-instruction lockstep mutations
- `-ED` fires AFTER the action commits — use for follow-up reads/displays

Most common decisions:
- `TABLE.LINE_ADDING` — master-side row-sync writing a shared counter that a follower reads
- `TABLE.LINE_ADDED` — in-table follow-up like populating a row-index variable
- `TABLE_LINE.COMPLETING` — per-row commit callbacks
- `PARAMETER_CHANGED` — recalc-on-edit (chatty if many params change)
- `PROC_INSTR.COMPLETING` — signature commit callbacks
- `DOCUMENT.GENERATED` — one-time init at xstep load

#### `conditional_rule`

`COMMAND + ACTION + (LONG_FORMULA | EVENT)` triplet evaluated by the framework to toggle visibility/activation.

```jsonc
// Formula-triggered (typical: pair with inverse)
{ kind: "conditional_rule", command: "TABLE_LINE.ACTIVATE",   formula: "LV_IND = 1" }
{ kind: "conditional_rule", command: "TABLE_LINE.DEACTIVATE", formula: "LV_IND <> 1" }

// Event-triggered (pre-allocate hidden row at xstep load)
{ kind: "conditional_rule", command: "TABLE.ADD_LINE", action: "HIDE", event: "DOCUMENT.GENERATED" }
```

`action` defaults to `"EXECUTE"`. Specify EITHER `formula` OR `event` — not both, not neither (enforced).

#### `signature`

```jsonc
{
  kind: "signature",
  label: "Performed By",
  variable: "LT_PERF1",              // ≤10 chars
  strategy: "SAPPOCSS",              // PPPI_SIGNATURE_STRATEGY
  validation: { fm: "ZEBR_XSTEP_SIG_VALIDATION", bindings: [...], validated_value_param: "IM_USERID" },
  text_for_invalid_node: "...",
  accept_invalid: "03"
}
```

#### `process_message`

Invisible row that fires a SAP message per-row over the LT_ variables the visible columns populate.

```jsonc
{
  kind: "process_message",
  category: "ZPICONS",               // discover via xs_list_process_message_categories
  bindings: [
    { variable: "LT_BAGNO", field: "PPPI_BATCH" },
    { variable: "LT_AMTADDE", field: "PPPI_MATERIAL_QUANTITY" }
  ]
}
```

Inherits the table's REPEATED firing — dispatches per row.

#### `raw`

Escape hatch for unrecognized column-block shapes. Round-trips verbatim through `xs_get/update_table_instruction` so other columns remain editable.

```jsonc
{ kind: "raw", fields: [{ domain: "...", value: "..." }, ...] }
```

### Companion setup

Each variable-owning column needs a matching parameter created via `xs_add_parameters` first. For table columns, set `is_table: true`. `button` / `function_call` / `process_message` / `conditional_rule` columns do NOT need their own param.

### Validation block

`input` and `signature` columns can carry a validation FM:

```jsonc
validation: {
  fm: "ZSMPL_FM_GET_EXPIRY_DATE",
  bindings: [
    { direction: "in",  fm_param: "IM_MATNR" },
    { direction: "out", fm_param: "EX_EXP_DATE", variable: "LT_EXPD", var_kind: "date" }
  ],
  validated_value_param: "IM_MATNR"
}
```

`validated_value_param` is the FM-side parameter that receives "the value being validated" (the column's own current value at validation time). When set, the builder substitutes `PPPI_STRING_VARIABLE='X'` for that binding — `'X'` is the framework sentinel and using a real variable name silently breaks validation.

---

## xs_update_table_instruction

Update an existing table instruction in place. Typed columns input, SET_CONTENT semantics.

**Inputs** — same as `xs_add_table_instruction` minus `step_nid`, plus `instr_nid`. `stext` is optional (omit to leave unchanged).

**Flow:** `xs_get_instruction(parse: "table")` → mutate `spec.columns` → `xs_update_table_instruction`. `instr_nid` stays stable.

**SET_CONTENT replaces FULL field set** — pass all columns you want to keep, not just changed ones.

---

## xs_modify_rows

Edit rows of a REPEATED table instruction in one read-modify-write cycle. `ops[]` applies sequentially against a single in-memory copy of `spec.columns[]`. Subsumes the old `xs_insert_row` / `xs_update_row` / `xs_delete_row` / `xs_reorder_rows`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `instr_nid` | yes | Must be a REPEATED table. |
| `ops[]` | yes | Discriminated union — at least one op. See [op kinds](#op-kinds). |

**Returns** `{ ops_applied, fields_count, columns }`.

### Op kinds

```jsonc
// insert — splice in. position -1 or omitted appends.
{ op: "insert", position?: number, column: TableColumn }

// update — replace by index.
{ op: "update", row_index: number, column: TableColumn }

// delete — remove by index. Subsequent rows shift up.
{ op: "delete", row_index: number }

// reorder — permute the whole array.
{ op: "reorder", new_order: number[] }
```

`column` for `insert`/`update` is the same typed shape as `xs_add_table_instruction.columns[i]` (input / output / button / function_call / signature / process_message / conditional_rule / raw).

`new_order` for `reorder` must have the same length as the current row count and contain every original index exactly once.

### Index shifting

`row_index` and `position` in later ops are evaluated against the **array state at that point**, not the original. After a `delete` or `insert`, downstream indices shift.

To delete multiple original rows in one call, **sort `row_index` descending** so earlier indices stay valid:

```jsonc
// Delete original rows 0 and 2 from a 3-row table:
ops: [
  { op: "delete", row_index: 2 },   // 3-row table → 2 rows; original [0,1,2] → [0,1]
  { op: "delete", row_index: 0 },   // 2-row table → 1 row;   was original row 1
]
```

The reverse order would delete original rows 0 and 3 (after the first delete shifted everything up).

### Examples

```jsonc
// Single insert (matches the old xs_insert_row):
ops: [{ op: "insert", column: { kind: "output", label: "Total", variable: "LV_TOT" } }]

// Append a row and immediately update what's now row 2 in one round-trip:
ops: [
  { op: "insert", column: {...} },
  { op: "update", row_index: 2, column: {...} },
]

// Swap rows 0 and 1 in a 3-row table:
ops: [{ op: "reorder", new_order: [1, 0, 2] }]
```

---

# Process messages

## xs_add_process_message

Append a process-message instruction to an S-step. Process messages post structured data to SAP (goods issue, quality result, control-recipe status, custom Z categories).

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `root_nid` | yes | |
| `step_nid` | yes | |
| `stext` | yes | Convention: `"Send Process Message"`. |
| `category` | yes | E.g. `PI_CONS`, `ZPICONS`. Discover via [`xs_list_process_message_categories`](#xs_list_process_message_categories). |
| `tabular` | no | Default `false`. Set `true` to prepend `PPPI_DATA_REQUEST_TYPE=REPEATED` — message fires once per row of LT_ vars in bindings. |
| `display_columns[]` | no | Optional `{ label, variable }` rows shown above the bindings. |
| `bindings[]` | yes | Ordered `{ variable, field }` pairs. Variable may be `""` (destination resolves at send time). |
| `after_nid` | no | |

**Returns** `{ nid, fields_count, fields }`.

**Distinct grammar** from `function_call`: uses `PPPI_DEFAULT_VARIABLE` + `PPPI_EXTERNAL_VALUE` pairs (no EXPORT/IMPORT triples). No `PPPI_EVENT` / `PPPI_OPTIONAL_PARAMETER` — messages fire on instruction completion; all bindings required.

**Before wiring:**

1. Call [`xs_list_process_message_categories`](#xs_list_process_message_categories) to find a valid category for the destination plant
2. Call [`xs_get_process_message_category_detail`](#xs_get_process_message_category_detail) to see which characteristics are mandatory (OBLKZ) vs optional, plus the dispatch FM

SAP-standard categories: `PI_CONS` (consumption / goods issue), `PI_GR` (goods receipt), `PI_PHST` (phase status), `PI_PHACT` (phase activity confirm), `PI_CRST` (control recipe status), `PI_QMSMR` (quality result). Customer Z-categories (e.g. `ZPICONS`) often shadow them.

**`tabular: true` typical use:** pair with a sibling table instruction that populates the same LT_ vars — message fires once per row.

---

## xs_update_process_message

Update a process-message instruction in place. SET_CONTENT.

**Inputs** — same as `xs_add_process_message` minus `step_nid` and `after_nid`, plus `instr_nid`. `stext` and `tabular` / `display_columns` optional.

**Flow:** `xs_get_instruction(parse: "process_message")` → mutate spec → `xs_update_process_message`. `instr_nid` stays stable. Pass ALL bindings/display_columns you want to keep — no partial updates.

---

## xs_list_process_message_categories

List process-message categories from O13C master (`TC50` + `TC50T`) — valid values for `PPPI_MESSAGE_CATEGORY`.

**Call before** picking a category for `xs_add_process_message` or `process_message` columns. Categories are per-plant; SAP-standard `PI_*` often have customer Z-equivalents (e.g. `ZPICONS` for a customer's GI message). Using a category not in the target plant's O13C silently fails at dispatch.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `plant` | no | 4-char WERKS to scope to one plant. Omit for all. |
| `category` | no | Wildcard against COSTR. `Z*`, `PI_CONS`, `*CONS*`. Bare strings auto-wrap as `%pattern%`. |
| `query` | no | Case-insensitive substring against code + description. Use when you don't know the exact code but know what it does. |
| `language` | no | SPRAS, default `"E"`. |
| `offset` | no | |
| `limit` | no | Default 100, max 500. |

**Returns**

```jsonc
{
  connection, total_matching, returned, offset, limit, next_offset,
  categories: [
    { plant, category, description, send_only_to_all },
    ...
  ]
}
```

---

## xs_get_process_message_category_detail

Full O13C dump for one category. Call AFTER `xs_list_process_message_categories` surfaces a candidate, BEFORE wiring.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `category` | yes | E.g. `"ZPICONS"`. |
| `plant` | no | Scope to one plant. Omit for per-plant view. |
| `language` | no | Default `"E"`. |

**Returns**

```jsonc
{
  ok: true,
  result: {
    category,
    per_plant: [
      {
        plant,
        description,
        send_only_to_all,
        destinations: [
          { destination, type, fm_name, fm_exists },   // fm_exists flags stale customizing
          ...
        ],
        characteristics: [
          {
            characteristic, oblkz,           // OBLKZ = mandatory flag
            atfor, length, description, default_value,
            per_destination_field: { [dest]: dspara }  // FM-side field name per destination
          },
          ...
        ]
      },
      ...
    ]
  }
}
```

**Errors `CATEGORY_NOT_FOUND`** if the (category, plant) tuple has no TC50 row — use `xs_list_process_message_categories` to discover valid values.

**Notes**

- Characteristics are independent of destinations. A category can have a full TC50C contract with ZERO destinations (record-only / audit categories). Empty destinations is not an error.
- Use `oblkz` to know which fields MUST be bound. Optional ones may be omitted.

---

# Catalogs

## xs_instruction_recipes

Catalog of canonical FIELD shapes for cmxsvn instruction kinds: `input_request`, `html_output`, `function_call`, `grouping`, `table`, `complex_table`, `calculation`, `process_message`, `row_sync`, `equipment_lookup`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `name` | no | Filter to one recipe. |
| `sandbox_kind` | no | Filter by sandbox JSON element type (e.g. `"entry_char_string"`, `"ctrl_table"`). |

**Returns**

```jsonc
{
  note: "...",
  total: number,
  recipes: [
    {
      name, description,
      field_template: [{ role, required, repeating, ... }, ...],
      example_payload: [{ domain, value }, ...],
      companion_setup: "...",
      sandbox_kinds: ["..."]
    },
    ...
  ]
}
```

**Key fact:** every instruction has `TYPE="0"`; what differentiates kinds is which DOMAINS appear in `fields[]`. Pass an `example_payload` (with your own labels/variable names/domains) to `xs_add_instruction`.

**No `connection` parameter** — purely static.

---

## xs_list_parameter_types

Static catalog of parameter-type domains in the customer's xstep system, ordered by usage frequency.

**Tiers**

- `S` = workhorses (>300K — `PPPI_SHORT_TEXT`, `PPPI_FRAGMENT_HTML`, `ZPPPI_NUMERIC_VALUE`, `PPPI_SIGNATURE`)
- `A` = common (100K–300K)
- `B` = specialty (10K–100K)
- `C` = rarer (1K–10K)

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `tier` | no | Filter by tier. |
| `query` | no | Case-insensitive substring against name + description. |

**Returns**

```jsonc
{
  note: "Catalog is static, refreshed manually from CMX_XS_DB_PS counts.",
  total: number,
  parameter_types: [
    { name, description, tier, usage_count },
    ...
  ]
}
```

**No `connection` parameter** — purely static. See `tool_types/xsteps/exploration/parameter_domains.md` for context. Defaults for ~85% of inputs: `PPPI_SHORT_TEXT` for text, `ZPPPI_NUMERIC_VALUE` for numbers.

---

# Classification (CABN)

## xs_add_characteristic

Create a classification characteristic (CABN) + optional allowed values (CAWN/CAWNT) for use as an xstep parameter domain.

**Call when** a spec needs a dropdown whose characteristic doesn't exist — verify absence first via `get_table_data(CABN, where="ATNAM = ...")` or `xs_list_parameter_types`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Max 30 chars. **Must start with `Z`** (customer namespace; SAP-standard `PPPI_*` and non-Z names rejected). Convention: `ZSMPL_CHAR_*` for sample-flow chars, `ZPPPI_*` for PI-sheet chars. |
| `description` | yes | Max 30 chars. Operator-facing label cmxsvn shows in dropdowns. |
| `data_type` | no | `CHAR` / `NUM` / `DATE` / `TIME` / `CURR`. Default `CHAR` — the only type currently supported for the `values` array. NUM/DATE/TIME/CURR characteristics can be created with no values; populate via SAP GUI for now. |
| `length` | no | Default 30. Max 70 (matches CAWN.ATWRT70). |
| `decimals` | no | NUM/CURR only. Default 0. |
| `case_sensitive` | no | Default `true`. |
| `values[]` | no | Empty array for a free-text characteristic. CHAR-only. Each `{ value, description }` becomes a CAWN row + an English CAWNT row. |

**Returns** `{ atinn, atnam, values_count }`. BAPI errors if the characteristic already exists.

**Backed by** `BAPI_CHARACT_CREATE` (package CT). Handles `ATINN` allocation, validation, change docs, value bookkeeping. Commits on success.

To edit values on an EXISTING characteristic, use [`xs_edit_characteristic_values`](#xs_edit_characteristic_values).

---

## xs_edit_characteristic_values

Edit the allowed-value list of an EXISTING characteristic — supports add and remove in one call.

**PREFER CREATING A NEW CHARACTERISTIC** over editing a shared one. Characteristics are shared classification artifacts — other xsteps, material classes, or AUSP rows may depend on this one. For isolated dropdown values, use [`xs_add_characteristic`](#xs_add_characteristic) to create a new one instead.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Must start with `Z`. Must already exist. |
| `add[]` | no | Each `{ value, description }`. Idempotent — already-present values skipped silently. |
| `remove[]` | no | Array of value keys (CAWN.ATWRT) to delete. Idempotent. |
| `confirm` | no | **Must be `true` to actually write.** Without it the tool returns a preview + queries to investigate dependents. |

At least one of `add` / `remove` must be non-empty.

**Safety gate:** without `confirm: true`, the tool returns:

```jsonc
{
  ok: false,
  status: "confirmation_required",
  message: "...",
  characteristic: name,
  values_that_would_be_added:   [...],
  values_that_would_be_removed: [...],
  how_to_investigate: {
    existing_values:      "run_query SELECT ... FROM cawn ...",
    existing_assignments: "run_query SELECT ... FROM ausp ...",
    class_memberships:    "run_query SELECT ... FROM ksml ...",
    orphans_check_for_removals: "..."  // when remove[] non-empty
  },
  safer_alternative: "...",
  to_proceed: "Re-call with confirm: true."
}
```

**REMOVAL HAZARD:** removing values does NOT clean up AUSP rows pinned to them. Those rows orphan (still reference the deleted key). The preview's `orphans_check_for_removals` surfaces the query to find them.

**Backed by** `BAPI_CHARACT_CHANGE` — diff-merge. Implementation reads current CAWN, submits `(existing − remove) ∪ add`.

CHAR-only in v1. Errors if characteristic doesn't exist (use `xs_add_characteristic`).

---

# Z function modules (whitelisted FUGR)

These tools write Z function modules in the whitelisted function group `ZAI_XSTEP_FMG`. They wrap ADT + SE37-equivalent APIs. **Name must start with `Z`** (defense-in-depth alongside the ABAP-side `check_fugr_allowed` whitelist).

## xs_create_function_module

Create + activate a new Z FM — interface and source body in one call.

**Wraps** `RS_FUNCTIONMODULE_INSERT_AIE` + `RS_FUNCTION_ACTIVATE`. On return, the FM is active and callable.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Max 30. Must start with `Z`. Convention: `Z<DOMAIN>_FM_<PURPOSE>`. |
| `function_group` | yes | Must be `ZAI_XSTEP_FMG` (only whitelisted group). Must already exist. |
| `short_text` | yes | Max 60. SE37 "Properties" description. |
| `importing[]` | no | Inputs. |
| `exporting[]` | no | Outputs. |
| `changing[]` | no | Bidirectional. Used by row-sync FMs. |
| `tables[]` | no | Legacy table-typed in/out. Prefer `changing` with table TYPE. |
| `exceptions[]` | no | Classic `RAISE <name>` exceptions. |
| `source_body` | yes | Body ONLY — between `FUNCTION ... ` and `ENDFUNCTION`. Do NOT include the FUNCTION/ENDFUNCTION lines or the `*"  IMPORTING` comment block. |
| `transport` | no | Open TR (e.g. `DE2K900123`). Omit for `suppress_corr_check` shortcut — fine on sandbox; next SE37 save will prompt for one. |

**Parameter spec shape** (`importing[i]`, `exporting[i]`, `changing[i]`, `tables[i]`):

```jsonc
{
  name: "IM_VALUE",                  // UPPER_SNAKE_CASE, max 30
  param_type: "ERFMG",               // type identifier; semantics depend on binding
  binding: "type",                   // optional: "type" (default) | "like" | "ref_to" | "table_of"
  optional: true,                    // SE37 "Optional" checkbox
  pass_value: false,                 // SE37 "Pass Value" checkbox
  default_value: "'X'"               // IMPORTING/CHANGING only; honored when caller omits
}
```

**Bindings:**

- `"type"` → `TYPE <param_type>` (default; most common)
- `"like"` → `LIKE <param_type>` (legacy; emits `dbfield`/`dbstruct`)
- `"ref_to"` → `TYPE REF TO <param_type>`
- `"table_of"` → `TYPE STANDARD TABLE OF <param_type>` (on IMPORTING/EXPORTING/CHANGING)

**Exception spec shape:**

```jsonc
{ name: "VALUE_NOT_FOUND", is_resumable: false }
```

`is_resumable` is for class-based exceptions (almost always false — leave unset for classic FMs).

**Returns** `{ funcname, function_include }`. Failures raise `XsEditorError` with the SAP error verbatim.

**Common pitfall:** including the `*"  IMPORTING` parameter comment block at the top of `source_body` causes "parameter comment blocks are not allowed" on activation. SE37 owns the comment block; you own the body.

---

## xs_update_function_module

Update an existing Z FM via delete + recreate.

**Inputs** — same shape as `xs_create_function_module` minus `function_group` (it's read off the existing FM and can't be changed). `short_text` and `source_body` required.

**Semantics:** replaces ALL parameter tables, short_text, exceptions, and body. Not a partial diff — pass the FULL desired interface + body.

**Caveats:**

- Brief unavailability window during the delete (~tens of ms).
- Deletes prior version history.
- Failure mid-recreate leaves the FM deleted — caller should retry the update with the same payload.

**To repoint to a different function group:** delete + create manually.

**Returns** `{ funcname, function_include }` — same shape as create.

---

## xs_get_function_module

Read an existing Z FM. Wraps `FUNCTION_EXISTS` + `RPY_FUNCTIONMODULE_READ_NEW`.

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Must start with `Z`. Must live in `ZAI_XSTEP_FMG`. |

**Returns**

```jsonc
{
  funcname, function_group, short_text, function_include,
  parameters: [
    { name, direction, binding, param_type, optional, pass_value, default_value },
    ...
  ],
  exceptions: [...],
  source_body                          // signature comment block + FUNCTION/ENDFUNCTION wrapper stripped
}
```

`source_body` is round-trippable as input to `xs_create_function_module`.

**Binding derivation:** binding is reconstructed from which RSIMP/RSEXP/RSCHA/RSTBL column carries a value (`table_of` > `ref_class` > `dbfield` > `typ`).

---

## xs_delete_function_module

Delete an existing Z FM via ADT (lock + DELETE).

**Inputs**

| Field | Required | Notes |
|---|---|---|
| `connection` | yes | |
| `name` | yes | Must start with `Z`. Must live in `ZAI_XSTEP_FMG`. |

**IRREVERSIBLE.** Removes the FM from `TFDIR`/`FUPARAREF`/`REPOSRC`. Use only for iterating on agent-generated FMs; never on production FMs.

**Returns** `{ ok, deleted }`. Errors include the SAP HTTP status + truncated response body.

---

# Typical workflows

## Reading a complete xstep for the first time

```
xs_folder_tree                       → find item_id by name
xs_get_metadata(item_id)             → see versions, ref_indicator
xs_get_version(item_id)              → full content
# OR
xs_get_snapshot(item_id)             → nested + typed rows[]
```

For ref-overlay items (`ref_indicator='X'`), `xs_list_children` errors but `xs_get_version` works (it walks cmxsvn directly).

## Cloning + editing

```
xs_clone_xstep(source_item_id, title)             → new item
xs_rename_item(new_item_id, new_stext)            → folder title
xs_update_node_attrs(root_nid, root_nid, stext)   → titlebar
xs_list_children(item_id=new_item_id, max_depth=3) → discover NIDs
```

## Adding a typed input to a step

```
xs_list_parameter_types(query="DECIMAL")          → find a domain
xs_add_parameters(root_nid, owner_nid=step_nid, params=[
  { name: "LV_VAL", domain: "ZPPPI_NUMERIC_VALUE_TWO_DEC", ptype: "L" }
])
xs_add_instruction(root_nid, step_nid, stext: "Volume", fields: [
  { domain: "PPPI_INPUT_REQUEST",   value: "Volume" },
  { domain: "PPPI_VARIABLE",        value: "LV_VAL" },
  { domain: "PPPI_REQUESTED_VALUE", value: "ZPPPI_NUMERIC_VALUE_TWO_DEC" }
])
```

## Building a table with a single-table row counter

```
# Parameters first (is_table: true for each LT_ column)
xs_add_parameters(root_nid, step_nid, params=[
  { name: "LT_INDEX",  domain: "ZSMPL_CHAR_GI_INITIALS", is_table: true, value: "1" },
  { name: "LT_BATCH",  domain: "PPPI_BATCH",  is_table: true },
  { name: "LT_PERF1",  domain: "PPPI_SIGNATURE", is_table: true }
])

# Table instruction with typed columns — invisible SET_LINE_INDEX FM keeps LT_INDEX in sync
xs_add_table_instruction(root_nid, step_nid, stext: "Bag Info", columns: [
  { kind: "function_call", fm: "/SMPL/PPPI_FM_SET_LINE_IDX",
    event: "TABLE.LINE_ADDED",
    bindings: [{ direction: "changing", fm_param: "CT_INDEX", variable: "LT_INDEX", var_kind: "float" }] },
  { kind: "output", label: "#",       variable: "LT_INDEX" },
  { kind: "input",  label: "Batch",   variable: "LT_BATCH", domain: "PPPI_BATCH" },
  { kind: "signature", label: "Performed By", variable: "LT_PERF1", strategy: "SAPPOCSS" }
])
```

For **cross-table** master/follower sync (two tables on the same step, follower mirrors master data per row), the canonical DE1 pattern uses `ZSMPL_FM_CUSTOM_INDEX` in Setup Functions + `ZSMPL_FM_INCREMENT_TABLE_LINE` on the master + `ZSMPL_FM_TRANSFER_LINE_ITEMS` × 4 events on the follower. See `XSTEP_BUILD_GUIDE.md` §5.1 for the full structural recipe.

## Iterating on a table

```
xs_get_instruction(instr_nid, parse: "table")     → typed spec
# mutate spec.columns in TS
xs_update_table_instruction(root_nid, instr_nid, columns: spec.columns)
```

For targeted row edits, use `xs_modify_rows` with an `ops[]` array of `insert` / `update` / `delete` / `reorder` operations — it batches the read-modify-write into a single round-trip and avoids hand-rebuilding `columns[]` on every change.

## Writing a process message

```
xs_list_process_message_categories(plant: "2910", query: "consumption")  → find ZPICONS
xs_get_process_message_category_detail(category: "ZPICONS", plant: "2910") → see characteristics + OBLKZ
xs_add_process_message(root_nid, step_nid, stext: "Send Process Message",
  category: "ZPICONS",
  tabular: true,                                  # fire per row of LT_* bindings
  bindings: [
    { variable: "LT_BAGNO",   field: "PPPI_BATCH" },
    { variable: "LT_AMTADDE", field: "PPPI_MATERIAL_QUANTITY" }
  ])
```

## Authoring a Z function module

```
xs_create_function_module(
  name: "ZSMPL_FM_RANGE_CLASSIFY",
  function_group: "ZAI_XSTEP_FMG",
  short_text: "Classify a numeric value into a range bucket",
  importing: [
    { name: "IM_VALUE",  param_type: "P", binding: "type" },
    { name: "IM_BUCKET", param_type: "STRING", binding: "type" }
  ],
  exporting: [
    { name: "EX_RESULT", param_type: "STRING", binding: "type" }
  ],
  source_body: `
    IF im_value > 100.
      ex_result = 'HIGH'.
    ELSEIF im_value > 0.
      ex_result = 'NORMAL'.
    ELSE.
      ex_result = 'LOW'.
    ENDIF.
  `
)
```

## Validating before save

```
xs_check_semantic(item_id)                         → catch dangling vars / missing PPPI_VARIABLE values
```

Empty `messages` = clean.

## Comparing two iterations

```
xs_diff_snapshots(a_item_id: "...", b_item_id: "...")
# → changed_nodes is a punch list
```

---

# Gotchas summary

- **Parameter names are `C(10)`.** SAP truncates silently. Every tool enforces it; references over 10 chars are rejected up-front.
- **Save-per-call.** Each xstep mutation is its own transaction. A failed second call leaves the first persisted.
- **NIDs are session-transient on recently-edited xsteps** for P-type nodes. For deletes, use `param_name` instead.
- **`PPPI_VARIABLE` must reference an existing parameter on the right owner.** Dangling refs render as "syntax error in process instruction" with an empty `<Grouping>`.
- **`xs_add_parameters` wipes sibling text-domain inputs** if you don't include them in the same call. Use `xs_update_parameter` for one-field changes.
- **Folder whitelist.** Mutations only accepted on items in the AI XA folder. To widen, edit `ZCL_SAPFRACTAL_XS_EDITOR`.
- **Reference items (`ref_indicator='X'`)** — `xs_list_children` errors with "internal error in XStep administration", but `xs_get_version` works because it walks cmxsvn tables directly.
- **`MCP_MAX_RESPONSE_BYTES` (default 2 MB)** caps every response. Watch for truncation markers on large xsteps and use paging / `include_attributes=false` to shrink.
