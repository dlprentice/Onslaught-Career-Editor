# Ghidra Motion-Controller Constructor Review Wave1021

Status: complete static read-only evidence
Date: 2026-05-31
Scope: `motion-controller-constructor-review-wave1021`

Wave1021 re-read four motion-controller constructor rows with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x0049c3e0 CMCMine__Constructor` | Calls `CMotionController__ctor_base`, installs vtable `0x005dc3f4`, stores the mine owner pointer at `+0x08`, and returns with `RET 0x4`. Caller xrefs are `CMine__Init` at `0x004ba3d0` and `0x004ba3dc`. |
| `0x0049c5d0 CMCSentinel__Constructor` | Calls `CMotionController__ctor_base`, installs vtable `0x005dc420`, stores the sentinel owner pointer at `+0x08`, and seeds `+0x0c/+0x10` with `0xc479c000`. Caller xrefs are `CSentinel__Init` at `0x004deafd` and `0x004deb09`. |
| `0x0049cad0 CMCTentacle__Constructor` | Calls `CMotionController__ctor_base`, installs vtable `0x005dc450`, stores the tentacle owner pointer at `+0x08`, clears setup/cache pointer fields, and seeds `+0x28` with `0xbf800000`. Caller xref is `CTentacle__CreateTentacleGuide` at `0x004f07a9`. |
| `0x0049ef80 CMCWarspiteDome__Constructor` | Calls `CMotionController__ctor_base`, installs vtable `0x005dc484`, stores the dome owner pointer at `+0x08`, and returns with `RET 0x4`. Caller xrefs are `CWarspiteDome__Init` at `0x00504918` and `0x00504924`. |

Context exports covered `0x004bae30 CMotionController__ctor_base`, `0x004bae50 CMotionController__dtor_base`, the paired scalar-deleting destructors, and the paired destructor bodies for `CMCMine`, `CMCSentinel`, `CMCTentacle`, and `CMCWarspiteDome`. Vtable export covered `0x005dc3f4`, `0x005dc420`, `0x005dc450`, and `0x005dc484`.

Read-back evidence:

- Primary exports: 4 metadata rows, 4 tag rows, 7 xref rows, 51 body-instruction rows, and 4 decompile rows.
- Context exports: 10 metadata rows, 37 xref rows, 135 body-instruction rows, and 10 decompile rows.
- Vtable export: 48 rows across four motion-controller vtables.
- Export-contract function-quality closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress advances to `532/1408 = 37.78%`.
- Expanded static surface progress advances to `761/1493 = 50.97%`.
- Wave911 top-500 risk-ranked coverage advances to `460/500 = 92.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected saved constructor names, signatures, comments, vtable writes, caller xrefs, destructor context, and vtable slots remain coherent in the loaded Ghidra database.
- The old Wave434/Wave435 motion-controller constructor claims still match fresh static retail evidence and do not need another mutation.

What remains separate proof:

- Runtime mine motion behavior.
- Runtime sentinel motion behavior.
- Runtime tentacle motion behavior.
- Runtime dome motion behavior.
- Exact source-body identity.
- Concrete motion-controller, owner, and vtable layouts.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1021; motion-controller-constructor-review-wave1021; 0x0049c3e0 CMCMine__Constructor; 0x0049c5d0 CMCSentinel__Constructor; 0x0049cad0 CMCTentacle__Constructor; 0x0049ef80 CMCWarspiteDome__Constructor; 532/1408 = 37.78%; 761/1493 = 50.97%; 460/500 = 92.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified; no mutation.
