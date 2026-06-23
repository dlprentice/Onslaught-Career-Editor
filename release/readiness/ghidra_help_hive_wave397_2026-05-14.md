# Ghidra HelpText / HiveBoss Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for six adjacent HelpText and HiveBoss targets. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x0047fab0` | `void * __thiscall CHelpTextDisplay__ctor(void * this)` | Corrected the constructor-like label to the HelpTextDisplay constructor. Static read-back shows two queued-message slots are cleared, the HelpTextDisplay vtable is installed, and `CGame` allocates this object during restart/init setup. |
| `0x0047fad0` | `void * __thiscall CHelpTextDisplay__scalar_deleting_dtor(void * this, byte flags)` | Created the adjacent missing scalar-deleting destructor function boundary. Static instruction/read-back evidence shows vtable restore and optional OID allocator free when the flag bit is set. |
| `0x0047fb00` | `void __thiscall CHelpTextDisplay__QueueMessageWithTimestamp(void * this, void * message)` | Corrected the older `CUnitAI` owner label. Static read-back shows a two-slot HelpText message queue with global timestamp stamping and an overflow console message. |
| `0x0047fb50` | `void __fastcall CHelpTextDisplay__RenderQueuedMessages(void * this)` | Corrected the older `CExplosionInitThing` owner label. Static read-back shows queued HelpText message age/fade handling, wrapping through `TextLayout__WrapWideTextToFixedLines`, font-state handling, draw dispatch, and old-slot expiry. |
| `0x0047fe30` | `void __thiscall CHiveBoss__Init(void * this, void * init_data)` | Corrected the undefined saved signature. Static read-back shows HiveBoss init-data flag setup, destructable-segment controller allocation, mesh-controller construction, `CUnit__Init`, `core2` segment lookup, guide creation, and seeded HiveBoss fields. |
| `0x004804c0` | `void __thiscall CHiveBoss__SetVar(void * this, void * name, void * data)` | Corrected the older `CExplosionInitThing` owner label to HiveBoss `SetVar` context. Static read-back shows `hb_*` config-name handling for guide velocities, rotation speeds, safe distance, and minimum ground-clearance style fields, then fallback to the base unknown-var path. |

## Validation

- `ApplyHelpHiveWave397.java` dry run: expected no mutation and reported the missing destructor boundary as a would-create item.
- `ApplyHelpHiveWave397.java` apply run: saved the project and reported six updated targets, one created function, and four renamed targets.
- Metadata/decompile/xref/tag/instruction read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_help_hive_wave397_probe.py --check`.
- Self-test: `tools/ghidra_help_hive_wave397_probe_test.py`.

## Claim Boundary

This tranche narrows static HelpText and HiveBoss ownership/signature evidence and saves those corrections in Ghidra. It does not prove runtime HelpText behavior, does not prove runtime HiveBoss behavior, does not prove exact source identity for every branch, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
