# Ghidra Controller Base Comment Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back hardened signatures, comments, and tags for `3` already named CController base helpers in the Steam `BEA.exe` Ghidra project. The pass keeps the current names, corrects the static reset helper to `__cdecl`, corrects `CController__Flush` and `CController__DoMappings` to `__thiscall`, and records the source/reference boundary for controller inactivity timing, button flush, and mapping-dispatch behavior.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x0042d7a0` | `void __cdecl CController__ResetInactivityTimerConditional(void)` | Source-parity inactivity timer reset helper with a retail non-interactive-section guard. |
| `0x0042d9d0` | `void __thiscall CController__Flush(void * this)` | Copies current button bitfields into old-button fields, clears current fields, then tail-dispatches `DoMappings` through vtable `+0x3c`. |
| `0x0042db40` | `void __thiscall CController__DoMappings(void * this)` | Main virtual-controller mapping engine: mapping-table scan, push-type dispatch, repeat timing, playback/record hooks, platform input cases, and `CController__SendButtonAction`. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_controller_base_comment_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_controller_base_comment_probe.py tools\ghidra_controller_base_comment_probe_test.py` passed. |
| Expected red check | `cmd.exe /c npm run test:ghidra-controller-base-comment` failed before expectation adjustment because the saved comment used the less-overclaiming phrase `platform mouse/keyboard` instead of probe wording `retail-only mouse/keyboard`; the probe was corrected and rerun. |
| Headless apply | `ApplyControllerBaseSignatureCommentTranche.java` dry reported `updated=0 skipped=3 renamed=0 missing=0 bad=0`; apply reported `updated=3 skipped=0 renamed=0 missing=0 bad=0` and `REPORT: Save succeeded`. |
| Read-back exports | Metadata `3`, decompile `3`, xrefs `5`, instruction rows `1365`, and tags `3`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-controller-base-comment` passed with targets `3`, xref evidence hits `5`, instruction evidence hits `13`, stale signature hits `0`, and overclaim hits `0`. |
| Whole-database queue | Refreshed headless `ExportFunctionQualitySnapshot.java` plus `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `6020` total functions, `1332` commented functions, `4688` commentless functions, `1939` undefined signatures, and `1980` `param_N` signatures. |
| Current proxies | Comment-backed `1332/6020 = 22.13%`; strict clean-signature `1270/6020 = 21.10%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `G:\GhidraBackups\BEA_20260513_113130_post_wave373_controller_base_verified` with `19` files, `153455495` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra signature/comment/tag refinement for already named CController base helpers. It does not prove runtime input behavior, exact class layout, exact Stuart-source method identity for every retail branch, concrete local variable types, BEA launch behavior, game patching, or rebuild parity.
