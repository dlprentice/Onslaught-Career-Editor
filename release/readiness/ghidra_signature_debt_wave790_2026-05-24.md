# Ghidra Signature Debt Wave790 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave790`

Wave790 signature debt saved Ghidra comments, tags, and parameter-hardened signatures for three existing function rows. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Target rows:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x00505c30 NamedEntryList__FindNearestChildByNameAndPosition` | `int __cdecl NamedEntryList__FindNearestChildByNameAndPosition(char * entry_name, float * position_xyz)` | Body walks `DAT_00854fc0`/`DAT_00854fc8`, compares entry names with `stricmp(entry_name)`, scans the matched child list, and returns the child with the smallest squared 3D distance from `position_xyz`. |
| `0x0050b010 CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk` | `void __stdcall CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk(void * unit)` | Thin body forwards `unit` to `CWorld__AddUnitToOccupancyGridAndRebuildShadows`; callers include UnitAI, Feature, WarspiteDome, NamedMesh, Cannon, and Sentinel init/add-to-world contexts. |
| `0x0050b020 CWorld__RemoveUnitFromOccupancyGrid_Thunk` | `void __stdcall CWorld__RemoveUnitFromOccupancyGrid_Thunk(void * unit)` | Thin body forwards `unit` to `CWorld__RemoveUnitFromOccupancyGrid`; callers include Building, BuildingNamedMesh, NamedMesh, Cannon, Dropship, UnitAI, Feature, and Hazard cleanup/remove contexts. |

Read-back evidence:

- `ApplySignatureDebtWave790.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave790.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave790.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 20 xref rows, 315 instruction rows, and 3 decompile rows.
- Queue after Wave790: 6098 total, 5544 commented, 554 commentless, 31 exact-undefined signatures, 19 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5494/6098 = 90.10%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-023043_post_wave790_signature_debt_verified`, 19 files, 171215751 bytes, `DiffCount=0`.

What this proves:

- The three target rows exist in the saved Ghidra project.
- The saved signatures replace prior `param_N` names with bounded names supported by static caller/decompile evidence.
- The saved comments and tags include `signature-debt-wave790` and `wave790-readback-verified`.
- The observed behavior is static retail Ghidra evidence tied to read-back metadata, decompile, instruction, xref, and queue exports.

What remains unproven:

- Exact source identity.
- Concrete list, child, unit, or world layouts.
- Runtime behavior.
- BEA patching behavior.
- Rebuild parity.
