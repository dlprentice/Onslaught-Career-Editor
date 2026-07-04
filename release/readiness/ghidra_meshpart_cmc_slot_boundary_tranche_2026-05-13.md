# Ghidra MeshPart / CMC Slot Boundary Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra boundary evidence.

This wave continued the saved-Ghidra static re-audit in the MeshPart / motion-controller neighborhood. It recovered four adjacent vtable-slot function starts that had been queued after the MeshPart / CMC existing-signature tranche, then saved conservative names, signatures, comments, and tags after serialized dry/apply/read-back.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00495770` | `CMCComponent__VFunc_08_CheckOwnerRangeWindow` | Recovered `CMCComponent` slot-8 boundary; reads owner through `this+0x08`, compares owner range/window float context at `+0xe0/+0xe4` and `+0xe8/+0xf0` against component cached fields, and returns `bool`. |
| `0x004959a0` | `CMCComponent__VFunc_04_UpdateTurretBarrelTransform` | Recovered `CMCComponent` slot-4 boundary; handles `turret` / `barrel` MeshPart token paths, vector/matrix helper calls, output-style arguments, and `RET 0x10`. |
| `0x00496100` | `CMCDropship__VFunc_05_UpdateDoorAnimationValue` | Recovered `CMCDropship` slot-5 boundary; filters MeshPart names by the `door` token, selects `dooropening` / `doorclosing` animation rows from owner-state context, writes a door animation output, and `RET 0x8`. |
| `0x00496200` | `CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow` | Recovered `CMCDropship` slot-8 boundary; reads owner through `this+0x08`, compares owner state `+0x27c` and time/window fields `+0x2a4/+0x2a8` against cached fields, and returns `bool`. |

Evidence:

- `tools/ApplyMeshPartCmcSlotBoundaryTranche.java` dry/apply passed with `targets=4 changed_or_would_change=4 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `4` metadata rows, `4` decompile exports, `7` xref rows, `1380` instruction rows, `4` tag rows, `40` vtable-slot rows, `4` focused xref evidence hits, `11` focused instruction evidence hits, `4` vtable evidence hits, and `5` string-token checks (`barrel`, `turret`, `door`, `dooropening`, `doorclosing`).
- Focused validation passed: `py -3 tools\ghidra_meshpart_cmc_slot_boundary_probe_test.py`, `py -3 -m py_compile tools\ghidra_meshpart_cmc_slot_boundary_probe.py tools\ghidra_meshpart_cmc_slot_boundary_probe_test.py`, and `cmd.exe /c npm run test:ghidra-meshpart-cmc-slot-boundary`.
- The refreshed all-functions baseline reports `6008` total functions, `0` legacy weak names, `1951` undefined signatures, and `2056` `param_N` signatures.
- The refreshed quality queue reports `6008` functions, `1197` commented functions, `4811` commentless functions, `1951` undefined signatures, and `2056` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1197/6008 = 19.92%`, strict clean-signature `1131/6008 = 18.82%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_010345_post_wave357_meshpart_cmc_slot_verified` with `19` files, `152963975` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/meshpart-cmc-slot-wave357/current/`.

Claim boundary: this is static retail Ghidra evidence only. It recovers and labels four MeshPart/CMC-adjacent vtable-slot function starts, but it does not prove exact source virtual names, concrete class layouts, local/type recovery, runtime component or dropship behavior, BEA launch, game patching, or rebuild parity.
