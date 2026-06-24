# Ghidra MeshPart / CMC Existing Signature Tranche - 2026-05-13

Status: GREEN public-safe static Ghidra correction evidence.

This wave continued the saved-Ghidra static re-audit in the MeshPart / motion-controller neighborhood immediately after the CMCCannon tranche. It hardened twelve existing function objects with corrected names, signatures, comments, and tags after serialized dry/apply/read-back. It did not create new function boundaries; the adjacent no-function vtable-slot bodies at `0x00495770`, `0x004959a0`, `0x00496100`, and `0x00496200` remain queued for a later boundary-recovery tranche.

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x004956a0` | `Mat34__Add` | Matrix helper with `this`, `outMatrix`, and `rhsMatrix` arguments; instruction read-back confirms `RET 0x8`. |
| `0x004957d0` | `CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel` | Child/subpart walker over `+0x15c/+0x160`; checks exact `turret` and starts-with `barrel` name tokens. |
| `0x00495930` | `CMCComponent__Ctor` | Constructor-style body that initializes `CMotionController`, sets vtable `0x005dc2d8`, stores field `+0x08`, and initializes `+0x0c/+0x10`. |
| `0x00495960` | `CMCComponent__ScalarDeletingDestructor` | Scalar-deleting destructor wrapper with `flags` argument; calls `CMCComponent__Dtor` and conditionally frees `this`. |
| `0x00495980` | `CMCComponent__Dtor` | Destructor body that resets vtable `0x005dc2d8`, clears field `+0x08`, and tail-calls the base destructor body. |
| `0x00495e00` | `Mat34__Subtract` | Matrix subtract helper with `this`, `outMatrix`, and `rhsMatrix` arguments; instruction read-back confirms `RET 0x8`. |
| `0x00495ed0` | `Mat34__ScaleByScalar` | Owner-neutral correction from the older `CMCMech` label; scales a matrix into `outMatrix` with a `float scalar` stack argument. |
| `0x00496090` | `CMCDropship__Ctor` | Constructor-style body that initializes `CMotionController`, sets vtable `0x005dc304`, stores field `+0x08`, initializes `+0x10`, and sets `+0x0c` to `-1`. |
| `0x004960c0` | `CMCDropship__ScalarDeletingDestructor` | Scalar-deleting destructor wrapper with `flags` argument; calls `CMCDropship__Dtor` and conditionally frees `this`. |
| `0x004960e0` | `CMCDropship__Dtor` | Destructor body that resets vtable `0x005dc304`, clears field `+0x08`, and tail-calls the base destructor body. |
| `0x00496250` | `CMeshPart__NameDoesNotStartWithDoor` | Negated four-character `Door` prefix predicate against the MeshPart name field. |
| `0x00496270` | `CMeshPart__HasDoorOpeningOrClosingAnimation` | Animation-token predicate checking `DoorOpening` and `DoorClosing` through `FindAnimationIndex`. |

Evidence:

- `tools/ApplyMeshPartCmcExistingSignatureTranche.java` dry/apply passed with `targets=12 changed_or_would_change=12 failed=0`; the apply reported `REPORT: Save succeeded`.
- Read-back verified `12` metadata rows, `12` decompile exports, `42` xref rows, `1164` instruction rows, `12` tag rows, `36` vtable-slot rows, `13` focused xref evidence hits, `14` focused instruction evidence hits, `2` vtable evidence hits, and `4` string-token checks (`turret`, `Door`, `DoorClosing`, `DoorOpening`).
- Focused validation passed: `py -3 tools\ghidra_meshpart_cmc_existing_signature_probe_test.py`, `py -3 -m py_compile tools\ghidra_meshpart_cmc_existing_signature_probe.py tools\ghidra_meshpart_cmc_existing_signature_probe_test.py`, and `cmd.exe /c npm run test:ghidra-meshpart-cmc-existing-signature`.
- The refreshed all-functions baseline reports `6004` total functions, `0` legacy weak names, `1951` undefined signatures, and `2056` `param_N` signatures.
- The refreshed quality queue reports `6004` functions, `1193` commented functions, `4811` commentless functions, `1951` undefined signatures, and `2056` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1193/6004 = 19.87%`, strict clean-signature `1127/6004 = 18.77%`. The `20%` value is not a milestone or acceptance gate.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_003011_post_wave356_meshpart_cmc_verified` with `19` files, `152963975` bytes, and `HashDiffCount=0`.

Raw proof remains ignored under `subagents/ghidra-static-reaudit/meshpart-cmc-wave356/current/`.

Claim boundary: this is static retail Ghidra evidence only. It corrects saved names, signatures, comments, and tags for twelve MeshPart/CMC-adjacent targets, but it does not prove exact source virtual names, concrete class layouts, local/type recovery, runtime MeshPart optimization, component/cannon/dropship behavior, BEA launch, game patching, or rebuild parity.
