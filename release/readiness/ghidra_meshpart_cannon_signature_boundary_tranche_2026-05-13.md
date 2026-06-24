# Ghidra MeshPart / CMCCannon Signature Boundary Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra correction evidence.

This wave continued the saved-Ghidra static re-audit around `CMeshPart` optimization helpers and the adjacent `CMCCannon` motion-controller vtable. It hardened six existing function signatures/comments/tags and recovered two previously missing function starts after serialized dry/apply/read-back. The CMCCannon vtable-slot names are behavior-bounded retail labels, not exact source virtual-method closure.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00495030` | `CMeshPart__PassesBuggyCoreStateForStrictOptimize` | Hardened to one `meshPart` argument; rejects `CORE`/`x1` name contexts and gates one mesh-kind/triangle-count case below `0x15` for the stricter optimize path. |
| `0x00495090` | `CMeshPart__PassesBuggyCoreStateForMergeOptimize` | Hardened to one `meshPart` argument; records the merge-pass form of the same `CORE`/`x1` and triangle-count optimization gate. |
| `0x004950f0` | `CMeshPart__AnySubPartNameStartsWithCore` | Renamed from the older token-address label; walks the child/subpart pointer array at `+0x15c/+0x160` and checks child names at `+0xdc` for the `CORE` token. |
| `0x00495230` | `CMCCannon__Ctor` | Corrected constructor-style signature to one explicit owner/field pointer argument; sets the `CMCCannon` vtable, stores field `+0x08`, and initializes `+0x0c/+0x10` with `0xc479c000`. |
| `0x00495260` | `CMCCannon__ScalarDeletingDestructor` | Corrected scalar-deleting destructor wrapper with a `flags` argument; calls `CMCCannon__Dtor` and conditionally frees `this`. |
| `0x00495280` | `CMCCannon__Dtor` | Corrected destructor body; resets the vtable, clears field `+0x08`, and tail-calls the `CMotionController` base destructor body. |
| `0x004bae60` | `SharedMotionController__VFunc_NoOpFourArgs_004bae60` | Recovered one-instruction no-op vtable target used by `CMCCannon` slots `3` and `14`; returns with `0x10` bytes of caller arguments removed. |
| `0x004952a0` | `CMCCannon__VFunc_04_UpdateTurretBarrelTransform` | Recovered `CMCCannon` slot `4` boundary; static evidence includes owner pointer `+0x08`, `turret` / `barrel` token checks, vector/matrix helper calls, transform/offset-style output writes, and `RET 0x10`. |

Evidence:

- `tools/ApplyMeshPartCannonSignatureBoundaryTranche.java` dry/apply passed with `targets=8 changed_or_would_change=8 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `8` metadata rows, `8` decompile exports, `11` xref rows, `10` instruction anchors, `8` tag rows, `4` vtable-slot evidence hits, `1` `CMCCannon` vtable-owner row, and `4` string-token checks (`CORE`, `x1`, `barrel`, `turret`).
- Focused validation passed: `py -3 tools\ghidra_meshpart_cannon_signature_boundary_probe_test.py`, `py -3 -m py_compile tools\ghidra_meshpart_cannon_signature_boundary_probe.py tools\ghidra_meshpart_cannon_signature_boundary_probe_test.py`, and `cmd.exe /c npm run test:ghidra-meshpart-cannon-signature-boundary`.
- The refreshed all-functions baseline reports `6004` total functions, `0` legacy weak names, `1951` undefined signatures, and `2067` `param_N` signatures.
- The refreshed quality queue reports `6004` functions, `1181` commented functions, `4823` commentless functions, `1951` undefined signatures, and `2067` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1181/6004 = 19.67%`, strict clean-signature `1118/6004 = 18.62%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260512_235146_post_wave355_meshpart_cannon_verified` with `19` files, `152931207` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/meshpart-cannon-wave355/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects saved function boundaries, names, signatures, comments, and tags for eight MeshPart/CMCCannon targets, but it does not prove exact source virtual names, concrete class layouts, local/type recovery, runtime mesh optimization or turret/cannon behavior, BEA launch, game patching, or rebuild parity.
