# Table Heuristics for Online Audit Parser (binary-analysis docs)

## Scope
Scan of markdown tables under `reverse-engineering/binary-analysis/**` to separate **function-entry mapping tables** from **callsite/xref/patch/other tables**. The goal is to avoid treating callsite tables as “expected function entries.”

## Observed Function-Mapping Table Patterns
These tables enumerate **function entry points** (address → function name), often in index or “key functions” sections.

- `reverse-engineering/binary-analysis/functions/_index.md:27`
  - Header: `| Address | Function | Notes |`
  - Section: `## Key Functions (Save/Cheat)`
- `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/_index.md:13`
  - Header: `| Address | Function | Status | Description |`
  - Section: `## Functions`
- `reverse-engineering/binary-analysis/functions/IScript.cpp.md:15` (table starts just above the excerpt)
  - Header: `| Address | Name | Purpose |`
  - Section: `## Functions (17 total)`
- `reverse-engineering/binary-analysis/functions/DXPalletizer.cpp.md:19`
  - Header: `| Address | Name | Size | Purpose |`
  - Section: `## Functions (9 total)`
- `reverse-engineering/binary-analysis/README.md:57`
  - Header: `| Address | Function | Purpose |`
  - Section: `## Key Discoveries`
- `reverse-engineering/binary-analysis/executable-analysis.md:39`
  - Header: `| Address | Function | Description |`
  - Section: `## Save/Load Function Map`

Common traits:
- Column set contains `Address` (or `VA`) plus `Function` or `Name`.
- Section header contains `Function`, `Functions`, `Function Map`, or `Function Index`.
- Optional columns: `Status`, `Notes`, `Description`, `Purpose`, `Size`.

## Observed Callsite/Xref Tables (Not Function-Entry Maps)
These list **callers/callees/xrefs** or **callsite addresses**, not function entry points.

- `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md:134`
  - Section: `## Called Functions`
  - Header: `| Address | Name | Purpose |` (call targets, not entries)
- `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md:159`
  - Section: `## Callers`
  - Header: `| Address | Function | Context |`
- `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md:74`
  - Section: `## Cross-References` → `### Called By`
  - Header: `| Address | Function | Context |`
- `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md:81`
  - Section: `### Calls`
  - Header: `| Address | Function | Purpose |`
- `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:187`
  - Section: `## Xrefs to Debug Path (0x0065211c)`
  - Header: `| Address | Function | Line# | Context |`

Strong indicators of callsite/xref tables:
- Section titles: `Callers`, `Called Functions`, `Called By`, `Calls`, `Cross-References`, `Xrefs`, `References`.
- Columns like `Context`, `Line`, `Line#`, `Read/Write`.

## Observed Patch/Byte Tables (Not Function-Entry Maps)
These list file patches or byte edits; they should never be treated as function maps.

- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:785`
  - Section: `## Known Binary Patches`
  - Headers include:
    - `| Region | File Offset | VA | Original | Patched | Purpose |`
    - `| File Offset | Original | Patched | Purpose |`
    - `| Address | Original | Patched | Purpose |`

## Observed Non-Function Tables (Not Function-Entry Maps)
Examples of tables that may still include `Address` but are not function entry maps:

- Vtable entries
  - `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md:31`
  - Header: `| Index | Address | Function |` under `### Vtable` (virtual slots, not entry list)
- Exception handlers
  - `reverse-engineering/binary-analysis/functions/Dropship.cpp/_index.md:16`
  - Header: `| Address | Name | Line | Purpose |` under `## Exception Handlers`
- Key addresses / globals / strings (not function entry lists)
  - `reverse-engineering/binary-analysis/windowed-mode-analysis.md:102` (not shown above): `| Address | Purpose |`

## Proposed Heuristics (Robust Against Callsite Tables)

### 1. Context/Heading Filters (Primary Guardrails)
If the nearest preceding heading (h2/h3/h4) or its parent contains any of:
- **Callsite/xref keywords**: `callers`, `called`, `calls`, `cross-references`, `xrefs`, `references`, `callsite`, `jump target`
- **Patch keywords**: `patch`, `patched`, `original`, `code cave`, `byte`, `file offset`
- **Non-function lists**: `vtable`, `class layout`, `members`, `offsets`, `globals`, `strings`, `cvars`, `exception`, `handlers`
Then classify as **non-function map** regardless of column names.

### 2. Header-Based Allowlist for Function Maps
Treat as **function-entry mapping** only if:
- Header contains `Address` (or `VA`) **and** `Function` **or** `Name`,
- AND header does **not** contain any of:
  - `Context`, `Line`, `Line#`, `Read/Write`, `Caller`, `Callee`, `Jump`, `Offset`, `Index`, `File Offset`, `Original`, `Patched`, `String`, `Usage`.

Allow optional columns: `Status`, `Notes`, `Description`, `Purpose`, `Size`, `Signature`.

### 3. Section-Title Positive Boost
If the section title includes:
- `Functions`, `Function Map`, `Function Mappings`, `Function Index`, `Key Functions`, `Function Addresses`
Then allow mapping even if the header is `Address | Name | Size | Purpose` (e.g. DXPalletizer).

### 4. File-Path Boost (Low-Risk)
If the file path matches:
- `reverse-engineering/binary-analysis/functions/_index.md`
- `reverse-engineering/binary-analysis/functions/**/_index.md`
Then a table under a `## Functions` section with `Address` + (`Function` or `Name`) is presumed to be a function map.

### 5. Tie-Breaker Scoring (Optional Implementation)
Score each table:
- +3: header includes `Address` and `Function`/`Name`
- +2: section title contains `Function`/`Functions`
- +2: file path is `functions/_index.md` or `functions/**/_index.md`
- -3: section title contains callsite/xref keywords
- -3: header includes `Context` or `Line#`
- -2: header includes `Offset` or `Index`
- -2: header includes `Original`/`Patched`

Classify as function map if score >= 4 and no hard-negative (callsite/xref/patch section).

## Edge Cases to Watch
- **Callsite tables with “Address | Function | Purpose”** (e.g., `### Calls` under cross-references) look like function maps at the header level. Context/heading checks are required to avoid misclassification.
- **Vtable tables** may include `Address | Function`, but are almost always under a `Vtable` heading and have an `Index` column.
- **Key Discoveries** or other summary sections may include function maps without “Function” in the heading (e.g., README). Header-based allowlist should accept those.

## Recommendation Summary
Use a **two-layer rule**: (1) reject tables under callsite/xref/patch headings, (2) accept only tables whose headers explicitly encode “address + function name” with no callsite/offset indicators. This avoids false positives while preserving the primary function-mapping tables across the binary-analysis docs.
