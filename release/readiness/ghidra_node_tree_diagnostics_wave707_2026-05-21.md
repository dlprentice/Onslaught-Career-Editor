# Ghidra Node-Tree Diagnostics Wave707 Readiness

Status: passed
Date: 2026-05-21

Wave707 node-tree diagnostics saved three adjacent CFastVB diagnostic wrapper rows with the `node-tree-diagnostics-wave707` and `wave707-readback-verified` tags.

## Targets

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00599a74` | `void __cdecl CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag(void * match_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a 0x100 local buffer, appends via `CTexture__AppendDiagnosticMessage`, and sets `match_context +0x40`. |
| `0x00599ac8` | `void __cdecl CFastVB__SelectBestNodeTreeMatch_ReportWarning(void * match_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a 0x100 local buffer and appends via `CTexture__AppendDiagnosticMessageDedup` without a local flag write. |
| `0x00599b13` | `void __cdecl CFastVB__SetParseErrorAndMarkStateDirty(void * parser_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a 0x100 local buffer, appends via `CTexture__AppendDiagnosticMessage`, and sets `parser_context +0x40/+0x44`. |

## Evidence

- Accepted dry/apply/final dry:
  - `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`
  - `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`
  - `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `3` metadata rows, `3` tag rows, `9` xref rows, `267` instruction rows, and `3` clean decompile rows.
- Queue after Wave707: `6098` total, `4107` commented, `1991` commentless, `1216` exact-undefined signatures, `228` `param_N`, comment-backed proxy `4107/6098 = 67.35%`, strict clean-signature proxy `4053/6098 = 66.46%`.
- Raw commentless head remains `0x0042f220 CSPtrSet__Clear`.
- High-signal head moved to `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-204613_post_wave707_node_tree_diagnostics_verified`, `19` files, `165448583` bytes, `DiffCount=0`.

## Boundaries

This is static Ghidra metadata/read-back evidence only. Exact context layout, varargs ABI, diagnostic id semantics, dedup key semantics, flag meanings, runtime parser behavior, source identity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave707 node-tree diagnostics`, `node-tree-diagnostics-wave707`, `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`, `0x00599b13 CFastVB__SetParseErrorAndMarkStateDirty`, `0x0042f220 CSPtrSet__Clear`, `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`.
