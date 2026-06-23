# Goodies Hidden Path Static Refresh - 2026-05-08

Status: GREEN static reachability refresh; hidden runtime reachability remains open

## Objective

Rerun the read-only source, script, packed-resource, xref, and existing Ghidra-export probes after the focused Goodies input-observer runtime proof. This narrows the remaining Goodies 71-73 question without launching BEA, mutating the installed game, mutating Ghidra, or committing private runtime evidence.

## Public-Safe Result

The refresh keeps the current model intact:

- Goodies 71, 72, and 73 are real shipped texture-only rows with resource, source data-table, texture-helper, unlock, and instruction support.
- The normal wall-coordinate path still has no known coordinate that maps to 71, 72, or 73.
- The focused copied-profile runtime observer already proved ordinary right-navigation returns `66, 67, 68, 69, 70, 74` with no hidden 71/72/73 returns on that path.
- Source Goodie API calls, current `CCareer__GetGoodiePtr` xrefs, current direct data xrefs, checked loose mission scripts, and checked packed top-level resource text scans still do not expose a direct Goodies 71-73 request path.

This is not an impossibility proof. It leaves indirect binary-only paths, developer/debug paths, cheat paths, non-wall runtime branches, and runtime-generated script behavior as separate follow-ups.

## Commands Run

| Command | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `py -3 tools\goodies_source_topology_probe.py --check` | PASS | `goodieFiles=11 directState71to73=0 directArray71to73=0 mapperReturns71to73=0` | Source topology still has 71-73 data/resource support but no source-level direct state or coordinate return path. |
| `py -3 tools\goodies_source_access_probe.py --check` | PASS | `set=3 get=3 direct71to73=0` | Source `GetGoodieState` / `SetGoodieState` callers remain bounded and do not directly target 71-73. |
| `py -3 tools\goodies_getgoodieptr_xref_probe.py --check` | PASS | `GetGoodiePtr rows: 423; callers: CCareer__UpdateGoodieStates=423`; direct data references `0` | Existing Ghidra xref exports still show `GetGoodiePtr` as unlock recomputation support, not a frontend direct-selection path. |
| `py -3 tools\goodies_ghidra_readback_probe.py --check` | PASS | Functions `6/6`, instruction contexts `8/8`, unlock read-back PASS, field map PASS, selection constants PASS `hits=0` | Existing Goodies Ghidra exports still show selected-coordinate handlers using the mapper and no direct `0x47`/`0x48`/`0x49` target constants in those handlers. |
| `py -3 tools\goodies_iscript_readback_probe.py --check` | PASS | IScript Goodie handlers set/get/index PASS | Retail mission-script handlers remain a real indexed state surface to track, even though checked corpora do not target 71-73. |
| `py -3 tools\goodies_script_corpus_probe.py --script-root "<install>\data\MissionScripts" --resource-root "<install>\data\Resources" --scan-packed-resources --require-root --check --out <ignored-output>` | PASS | Loose scripts: `files=733 calls=32 indices=51,53,68,69,70,71 target72to74=0`; packed resources: `archives=301 inflateErrors=0 tokenFiles=0 calls=0 target72to74=0` | The checked installed loose scripts and top-level inflated packed resources have no literal Goodie state calls for script indices 72-74, the one-based indices corresponding to save Goodies 71-73. |

Raw generated summaries remain ignored under `subagents/`.

Follow-up scalar scan: `release/readiness/goodies_scalar_reference_scan_2026-05-08.md` adds a broader read-only Ghidra instruction-scalar search for `0x47`, `0x48`, and `0x49`. The broad search is noisy, but it narrows the next static review queue to focused frontend/script/career-adjacent literal candidates without proving a hidden selector.

## Updated Classification

Goodies 71-73 are best classified as shipped, source-recognized, texture-only Goodies with no proven normal wall-coordinate path and no currently proven direct source/script/xref selector.

The remaining question is no longer missing assets or ordinary wall navigation. It is hidden or indirect runtime reachability.

## Not Claimed

- This does not prove 71-73 are unreachable in all runtime states.
- This does not inspect every compiled binary indirect array access.
- This does not prove or disprove developer/debug direct-selection paths.
- This does not launch BEA, attach CDB, mutate Ghidra, patch saves, or patch executables.
- This does not make extracted private assets public-safe for redistribution.
