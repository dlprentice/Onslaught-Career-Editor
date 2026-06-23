# Goodies RE Coverage Map Evidence - 2026-05-07

## Scope

This pass updated the public-safe Goodies RE map after the WinUI Goodies catalog/save-state work. It is documentation/static planning only. It does not run BEA, mutate `BEA.exe`, patch the installed game, mutate a Ghidra project, or commit private assets.

## What Changed

- `reverse-engineering/save-file/goodies-system.md` now records the current three-layer Goodies coverage:
  - catalog identity from PC resources, video inventory, and extracted language titles;
  - save state from true-view `CGoodie[300]` analysis;
  - WinUI display from the explicit `.bes` save-state loader.
- The docs now separate proven catalog/save/UI behavior, source/static unlock recomputation, and remaining unproven runtime trigger/selection behavior.
- The next static/runtime RE targets are listed by bounded target area:
  - `CCareer__UpdateGoodieStates` (`0x0041c470`);
  - `CGame__RunIntroFMV` (`0x0046d890`);
  - `CGame__RunOutroFMV` (`0x0046d9f0`);
  - `IScript__GetGoodieState` / `IScript__SetGoodieState`;
  - frontend Goodies display/cheat override paths.

## What This Proves

- The repo now has a current, public-safe handoff from WinUI Goodies product work back into static/runtime RE planning.
- The Goodies browser claims are bounded: identity, save-state decoding, and native display are proven; source/static unlock recomputation now has read-back coverage, while live runtime trigger and hidden/non-grid selection behavior remain separate RE tasks.
- Follow-up evidence in `release/readiness/goodies_getgoodieptr_xref_readback_2026-05-07.md` shows `CCareer__GetGoodiePtr` xrefs currently resolve only to `CCareer__UpdateGoodieStates`, and direct data xrefs to the concrete 71-73 state addresses are not reported in the current Ghidra project. This narrows the Goodies 71-73 direct-path question without closing runtime reachability.
- Follow-up evidence in `release/readiness/goodies_source_access_probe_2026-05-07.md` shows source-level `CAREER.GetGoodieState` / `CAREER.SetGoodieState` callers are bounded to FEPGoodies coordinate wrapping and gameplay FMV unlock checks, with no direct source API call to Goodies 71-73.
- Follow-up evidence in `release/readiness/goodies_iscript_readback_2026-05-07.md` confirms the retail mission-script `SetGoodieState` / `GetGoodieState` handlers read/write Goodie state by script index, which keeps mission-script use as a real indirect access surface to investigate.
- Follow-up evidence in `release/readiness/goodies_script_corpus_probe_2026-05-07.md` checked both the repo-local and installed Steam mission-script corpora and found Goodie state calls for script indices `51`, `53`, and `68-71`, but none for `72-74` (the 1-based indices corresponding to save Goodies 71-73).

## Commands Run

```powershell
npm run test:md-links
npm run test:doc-commands
py -3 tools/docsync_check.py
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools/release_curated_manifest.py --check
py -3 tools/release_profile_snapshot.py --check
```

Result: pass.

## Fresh Read-Only Probe Refresh

After the WinUI Goodies filter/status work, these read-only probes were rerun without launching BEA, mutating `BEA.exe`, or mutating a Ghidra project:

| Probe | Result | Public-safe output summary |
| --- | --- | --- |
| `py -3 tools/goodies_runtime_readback_probe.py --check` | PASS | `15/15` source/runtime-static token groups passing. |
| `py -3 tools/goodies_source_access_probe.py --check` | PASS | Source Goodie API lines: `set=3`, `get=3`, direct `71-73=0`. |
| `py -3 tools/goodies_script_corpus_probe.py --script-root "<install>\\data\\MissionScripts" --require-root --check` | PASS | Installed corpus: `733` scripts, `32` Goodie calls, indices `51,53,68,69,70,71`, target `72-74=0`. |
| `py -3 tools/goodies_ghidra_readback_probe.py --check` | PASS | Existing Ghidra exports: functions `6/6`, instruction contexts `8/8`, unlock read-back PASS, field map PASS. |
| `tasklist.exe /FI "IMAGENAME eq BEA.exe"` | PASS | No running `BEA.exe` process after the read-only probes. |

This refresh strengthens the static RE baseline. It still does not prove live runtime reachability for hidden/non-grid Goodies.

## Not Proven Yet

- Runtime proof of every Goodie unlock trigger.
- Hidden/non-grid runtime selection proof for Goodies 71-73.
- Ghidra read-back of every target listed above in this pass beyond the currently covered unlock/frontend subset.
- Full textured/animated in-app Goodies model viewer.
- Public redistribution of extracted Goodies assets.
