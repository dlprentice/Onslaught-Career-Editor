# Ghidra MenuItem Base Comment Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back saved proof-boundary comments and tags for `5` already named MenuItem-family base-vfunc targets in the Steam `BEA.exe` Ghidra project. The pass preserves the existing names/signatures, distinguishes primary vtable `0x005db440` from sibling vtable `0x005dc520`, and tags the tranche as `menuitem-base-wave371`.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x00453a50` | `CMenuItem__ButtonPressed_NoOp` | Zero-body button-handler slot; instruction read-back is `RET 0x0c`, with vtable data including `0x005db440` slot `1`. |
| `0x00453a60` | `CMenuItem__IsEnabled` | Reads and returns `this+0x10`; vtable read-back includes `0x005db440` slot `3` and `0x005dc520` slot `3`. |
| `0x00453a70` | `CMenuItem__GetRowHeight` | Returns `0x14` or `0x28` based on `this+0x0c`; vtable read-back includes `0x005db440` slot `6` and `0x005dc520` slot `6`. |
| `0x00453a80` | `CMenuItem__DefaultFalseFlag` | Shared default-false virtual reused by flag-style slots `8`, `9`, and `10` in `0x005db440` and sibling menu-item vtables. |
| `0x00453a90` | `CMenuItem__scalar_deleting_dtor` | Installs vtable `0x005db440`, conditionally frees through `OID__FreeObject` when flags bit `0` is set, and returns `this`. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_menuitem_base_comment_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_menuitem_base_comment_probe.py tools\ghidra_menuitem_base_comment_probe_test.py` passed. |
| Expected red check | `cmd.exe /c npm run test:ghidra-menuitem-base-comment` failed before mutation because after-readback files and saved comments/tags were absent. |
| Headless apply | `ApplyMenuItemBaseCommentTranche.java` dry/apply both reported `targets=5 changed_or_would_change=5 failed=0`; apply printed `REPORT: Save succeeded`. |
| Read-back exports | Metadata `5`, decompile `5`, xrefs `119`, instruction rows `165`, tags `5`, primary vtable rows `12`, and sibling vtable rows `12`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-menuitem-base-comment` passed with targets `5`, primary vtable evidence hits `7`, sibling vtable evidence hits `5`, xref evidence hits `10`, instruction evidence hits `9`, stale token hits `0`, and overclaim hits `0`. |
| Whole-database queue | `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `6020` total functions, `1329` commented functions, `4691` commentless functions, `1939` undefined signatures, and `1980` `param_N` signatures. |
| Current proxies | Comment-backed `1329/6020 = 22.08%`; strict clean-signature `1267/6020 = 21.05%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_103746_post_wave371_menuitem_base_verified` with `19` files, `153422727` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra comment/tag refinement for already named MenuItem-family functions. It does not prove exact Stuart-source method identities, concrete MenuItem class layouts, per-slot semantic names beyond the recorded static evidence, runtime frontend input/layout behavior, BEA launch behavior, game patching, or rebuild parity.
