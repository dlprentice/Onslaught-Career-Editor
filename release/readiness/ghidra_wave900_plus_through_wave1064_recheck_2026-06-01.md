# Ghidra Wave900-Wave1064 Static Re-Audit Recheck

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00535560` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: validation passed after `test:ghidra-wave900-plus-through-wave1064-recheck`
Date: 2026-06-01
Scope: Wave900 through Wave1064 static evidence gate

This note extends the Wave900+ structural recheck through Wave1064 after `iscript-setthing-command-bridge-wave1064`.

Expected current anchors:

- Latest wave note: `release/readiness/ghidra_iscript_setthing_command_bridge_wave1064_2026-06-01.md`
- Focused probe: `tools/ghidra_iscript_setthing_command_bridge_wave1064_probe.py`
- Package script: `test:ghidra-iscript-setthing-command-bridge-wave1064`
- Aggregate script: `test:ghidra-wave900-plus-through-wave1064-recheck`
- Queue closure: `6246/6246 = 100.00%`
- Wave911 focused progress: `812/1408 = 57.67%`
- Expanded static surface progress: `1199/1560 = 76.86%`
- Wave911 top-500 coverage: `500/500 = 100.00%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified`

Validation boundary: this gate checks static read-back evidence, release notes, package wiring, backup references, and queue closure. It does not prove runtime mission-script dispatch behavior, complete mission-script corpus coverage, exact source/layout identity, BEA patching, gameplay outcomes, or rebuild parity.

Observed validation result:

- Readiness notes: `167`
- Covered waves: `165`
- Package probe scripts: `163`
- Evidence bases: `163`
- Backup references: `165`
- Apply scripts: `52`
- Wave982-Wave1064 direct probes: `83` results, `1` direct pass, `82` allowed stale-current failures, `0` disallowed failures
- Current queue: `6246` total, `0` commentless, `0` undefined signatures, `0` `param_N`, `PASS`

Probe token anchor: Wave1064; iscript-setthing-command-bridge-wave1064; 0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg; 0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg; 0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg; 0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg; 0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg; 0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg; 0x004fd830 CUnit__SetFactionForHierarchy; 0x004fe390 CEngine__EnableThingByNameFlag; 0x004fe3f0 CEngine__DisableThingByNameFlag; 812/1408 = 57.67%; 1199/1560 = 76.86%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified; no mutation.
