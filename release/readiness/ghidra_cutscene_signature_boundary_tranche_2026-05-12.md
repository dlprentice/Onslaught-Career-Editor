# Ghidra Cutscene Signature / Boundary Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 345 continued the saved-Ghidra static re-audit at the adjacent `CCutscene` cluster around `0x0043e8e0`. It saved names, signatures, comments, and tags for fourteen cutscene targets after fresh metadata, decompile, xref, instruction, tag, and vtable-slot review.

The pass recovered two missing function boundaries, corrected stale destructor/init/animation-node labels, and recorded the current vtable context without claiming complete class-layout recovery.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043e8e0` / `0x0043ea90` | `CCutscene__dtor_base` / `CCutscene__scalar_deleting_dtor` | Corrects the stale scalar-deleting destructor label on the body and records the wrapper/body split. |
| `0x0043eab0` | `CCutscene__Init` | Corrects the stale vfunc label to the init body that copies init-name context, calls load, and delegates base init work. |
| `0x0043eca0` | `CCutscene__ClearAnimationsAndStop` | Recovered missing boundary from vtable/xref context; clears animation-slot lists and calls the stop slot. |
| `0x0043ed20` | `CCutsceneAnimNode__DestroyRecursive` | Narrows the old cutscene-wide destroy label to the animation-node recursive cleanup body. |
| `0x0043ed80` / `0x0043f210` | `CCutscene__Load` / `CCutscene__AddAnimation` | Keeps the loader and add-animation labels with explicit proof-boundary signatures/comments. |
| `0x0043f340` / `0x0043f420` / `0x0043f510` / `0x0043f690` / `0x0043fa70` / `0x0043fcd0` | start/stop/init/update/prepare/force-end helpers | Hardened existing names with saved signatures, comments, and tags. |
| `0x0043fcb0` | `CCutscene__EventDispatchUpdate` | Recovered missing event-dispatch boundary; handles event code `3000` by calling update and otherwise delegates to the base event handler. |

## Evidence

- Initial read-only exports covered `12` starting targets and found two missing boundaries through vtable/xref context.
- `tools/ApplyCutsceneSignatureBoundaryTranche.java` dry/apply reported `targets=14`, `changed_or_would_change=14`, `failed=0`; apply printed `REPORT: Save succeeded`.
- Final read-back verified `14/14` metadata rows, `14/14` decompile exports, `16` xref rows, `1694` instruction rows, `14/14` tag rows, and `128` vtable-slot rows.
- Vtable-slot evidence included `0x005dad88` slots `0`, `1`, `2`, and `9`, plus `0x005dae00` slot `4` and `0x005dae80` slot `2` for the checked cutscene context.
- `py -3 tools\ghidra_cutscene_signature_boundary_tranche_probe_test.py` passed `2/2`; `py -3 -m py_compile tools\ghidra_cutscene_signature_boundary_tranche_probe.py tools\ghidra_cutscene_signature_boundary_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-cutscene-signature-boundary-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database baseline reports `5974` functions and `0` weak functions. The refreshed quality queue reports `1089` commented functions, `4885` commentless functions, `1961` undefined signatures, and `2115` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_175825_post_wave345_cutscene_verified` with `19` files, `152701831` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current CCutscene labels and boundary coverage, but it does not prove runtime cutscene playback, exact source identities beyond the recorded static evidence, concrete `CCutscene` or animation-node layouts, `.cut` format completeness, local variable recovery, structure typing, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/cutscene-wave345/current/`.
