# Ghidra IScript Lifecycle Review Wave926

Status: complete read-only static review
Date: 2026-05-27
Scope: `iscript-lifecycle-review-wave926`

Wave926 re-reviewed the compact IScript lifecycle pair selected from the Wave911 focused queue. The pass was read-only: no Ghidra mutation, no rename, no saved signature/comment/tag change, no function-boundary change, and no executable-byte change.

Targets:

| Address | Saved row | Static read-back evidence |
| --- | --- | --- |
| `0x005333b0` | `IScript__Constructor` | Called by `0x004f4230 CComplexThing__SetScript` at `0x004f42a8`; constructs the 0x3c-byte mission-script object, initializes the monitor/list state, installs vtable `0x005e4f08`, stores owner/script pointers, and writes the script back-pointer at `script_object_code+0x68`. |
| `0x00533450` | `IScript__Destructor` | Called by `0x00533430 IScript__ScalarDeletingDestructor` at `0x00533433`; restores vtable `0x005e4f08`, releases `this+0x0c`, walks the listener/state `CSPtrSet` at `this+0x28`, clears the set, and calls `CMonitor__Shutdown`. |

Read-back evidence:

- Metadata export: `2` rows, `2` OK.
- Tag export: `2` rows, `2` OK.
- Xref export: `2` rows.
- Instruction export: `95` function-body instruction rows.
- Decompile export: `2` rows, `2` OK.
- Focused Wave911 re-audit progress after Wave926: `98/1408 = 6.96%`.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-224500_post_wave926_iscript_lifecycle_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

Consult note:

- Cursor Composer 2.5 recommended the IScript constructor/destructor lifecycle pair as a compact low-risk Wave926 read-only check.
- A Codex read-only consult recommended a CUnit/active-reader targeting micro-cluster first, with CUnitAI deploy and PhysicsScript loader continuation as backups. That recommendation is carried forward as a likely Wave927 candidate rather than mixed into this IScript lifecycle wave.

What this proves:

- The two saved function rows still exist in the loaded Ghidra database with the expected names and signatures.
- The constructor xref still ties the row to `CComplexThing__SetScript`.
- The destructor xref still ties the row to `IScript__ScalarDeletingDestructor`.
- The old Wave578 IScript lifecycle correction boundary still holds under fresh read-back.

What remains unproven:

- Runtime mission-script startup behavior.
- Runtime mission-script teardown behavior.
- Exact IScript layout/source identity.
- Exact listener-node layout and runtime listener semantics.
- BEA patching behavior.
- Rebuild parity.
