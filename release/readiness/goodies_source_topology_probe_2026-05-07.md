# Goodies Source Topology Probe - 2026-05-07

Status: public-safe read-only source evidence

## Scope

This note records a read-only source-topology probe for Goodies 71-73. It checks how Stuart's source represents those rows across the frontend data table, texture helper, unlock logic, normal coordinate mapper, selected-load path, and unlock-all save-name cheat.

This pass does not launch BEA, read or write `BEA.exe`, mutate Ghidra, patch the installed game, write saves, or commit raw generated JSON. Source remains architecture/name evidence; Steam retail binary read-back and copied-profile runtime proof remain the authority for shipping behavior.

Raw generated JSON stayed under ignored `subagents/`.

## Command

| Command | Result | Important Output | What It Proves |
| --- | --- | --- | --- |
| `py -3 tools\goodies_source_topology_probe.py --check` | PASS | `goodieFiles=11 directState71to73=0 directArray71to73=0 mapperReturns71to73=0` | Source topology still has 71-73 asset/unlock support, while normal source-level frontend coordinate mapping and direct state access do not expose 71-73. |

## Public-Safe Findings

| Check | Finding |
| --- | --- |
| Source files scanned | 106 source/reference files under `references/Onslaught/` |
| Files with Goodies tokens | 11 |
| Goodies token lines | 1092 |
| Data-table entries for 71-73 | Present |
| Career unlock entries for 71-73 | Present |
| Career instruction entries for 71-73 | Present |
| Texture helper cases for 71-73 | Present |
| Mesh helper cases for 71-73 | Absent |
| Background helper cases for 71-73 | Absent |
| Normal `get_goodie_number` returns for 71-73 | Absent |
| Direct source `GetGoodieState` / `SetGoodieState` calls targeting 71-73 | 0 |
| Direct source `mGoodies[71..73]` array hits | 0 |

## Interpretation

- Goodies 71-73 are source-real rows: they have frontend data-table entries, texture helper cases, and Career unlock/instruction support.
- The normal selected-load path still derives the selected row from `get_goodie_number(mCX, mCY)` before loading `goodie_<n>_res_PC.aya`.
- The source unlock-all save-name cheat is a display-state override after coordinate mapping. It makes mapped slots appear old/unlocked, but it is not proof that skipped indices have visible wall coordinates.
- This aligns with existing copied-profile wall replay evidence: normal wall navigation skips from 70 to 74 even though 71-73 exist as shipped texture-only rows.

## Not Claimed

- This is not Steam retail runtime proof.
- This does not inspect packed/runtime script divergence.
- This does not rule out indirect binary-only, developer/debug, or hidden direct-selection paths.
- This does not prove hidden/non-grid reachability or unreachability for Goodies 71-73.
