# Goodies Static Baseline Refresh - 2026-05-07

Status: public-safe read-only RE evidence

Source branch: `wip/sandbox`
Source commit under validation: `b18bdb16`

## Scope

Refresh the Goodies static/read-back baseline before any further hidden/non-grid Goodies runtime work or richer Goodies Browser work. This pass is read-only and public-safe: it does not launch BEA, mutate the installed game, patch `BEA.exe`, mutate Ghidra, write saves, or commit private proof JSON.

Raw generated JSON stayed under ignored `subagents/` paths.

## Commands

| Command | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `py -3 tools/goodies_runtime_readback_probe.py --check` | PASS | `groups: 15/15 passing` | Existing source/runtime-static token groups still support the current Goodies evidence map. |
| `py -3 tools/goodies_source_access_probe.py --check` | PASS | `source Goodie API lines: set=3 get=3 direct71to73=0` | Source-level Goodie state access remains bounded and does not directly target Goodies 71-73. |
| `py -3 tools/goodies_script_corpus_probe.py --script-root <installed MissionScripts> --require-root --check --out <ignored-output>` | PASS | `files=733 calls=32 indices=51,53,68,69,70,71 target72to74=0` | The installed MissionScripts corpus still has no script calls for the 1-based indices that would correspond to save Goodies 71-73. |
| `py -3 tools/goodies_ghidra_readback_probe.py --check` | PASS | Functions `6/6`, instruction contexts `8/8`, unlock read-back PASS, field map PASS. | Existing Ghidra read-back exports still support the known frontend/unlock/static table interpretation. |
| `py -3 tools/goodies_getgoodieptr_xref_probe.py --check` | PASS | `GetGoodiePtr rows: 423; callers: CCareer__UpdateGoodieStates=423`; direct data refs for Goodies 71-73: `0`. | Current Ghidra xref exports still show `GetGoodiePtr` as an unlock recomputation helper and no direct data xrefs to the concrete 71-73 state addresses. |
| `py -3 tools/goodies_iscript_readback_probe.py --check` | PASS | IScript Goodie handlers: set PASS, get PASS, index PASS. | Retail mission-script Goodie get/set handlers remain proven as an indirect state surface, even though the checked installed scripts do not target 71-73. |
| `tasklist.exe /FI "IMAGENAME eq BEA.exe"` | PASS | No matching task running. | Confirms this refresh did not leave a BEA process running. |

## Current Baseline

- Goodies 71-73 are shipped texture-only resource rows with extracted preview coverage.
- The known frontend wall coordinate mapper does not expose 71-73 through normal wall coordinates.
- Existing copied-profile wall replay evidence already shows normal visible wall navigation jumps from 70 to 74.
- The source Goodie API callers do not directly target 71-73.
- The checked installed MissionScripts corpus does not call script indices 72-74.
- Ghidra xrefs to `CCareer__GetGoodiePtr` resolve to `CCareer__UpdateGoodieStates`, and current direct data-xref exports do not report direct references to the concrete 71-73 state slots.
- IScript Goodie get/set handlers are real and remain a possible indirect runtime surface in principle.

## Still Not Proven

- Hidden/non-grid runtime reachability or unreachability of Goodies 71-73.
- Packed/runtime script divergence outside the checked installed MissionScripts corpus.
- Hidden/developer/cheat/direct-selection paths that bypass the known wall coordinate mapper.
- Textured/animated native Goodies model viewing.
