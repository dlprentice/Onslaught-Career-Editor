# Wave1202 Cannon Motion-Controller Residual Current-Risk Review

Status: complete read-only static evidence validated, committed, and pushed
Date: 2026-06-07
Tag: `wave1202-cannon-motion-controller-residual-current-risk-review`

Wave1202 re-read `13 cannon/motion-controller current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Codex read-only consults used: one consult recommended a console cluster, and the adversarial consult preferred this coherent cannon/motion-controller cluster over a heterogeneous score-17 sweep; Codex root made the final selection.

Representative anchors:

| Address | Name | Evidence |
| --- | --- | --- |
| `0x0041b450` | `CCannon__VFuncSlot_02_RemoveFromWorldAndForward` | Slot-2 owner-corrected CCannon/CWarspiteDome cleanup/world-link forwarding evidence remains bounded. |
| `0x0041b590` | `CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` | Slot-50 mark-destroyed/reset-deploy-graph behavior remains bounded; old CanFire-style implication stays inactive. |
| `0x00493020` | `CMCBuggy__CMCBuggy` | Constructor stores owner/model pointer and initializes buggy motion-controller fields. |
| `0x00495280` | `CMCCannon__Dtor` | Destructor resets the CMCCannon vtable, clears owner field `+0x08`, and forwards to the CMotionController base destructor body. |
| `0x00495930` | `CMCComponent__Ctor` | Constructor initializes base controller state, owner field `+0x08`, vtable `0x005dc2d8`, and scalar fields `+0x0c/+0x10`. |
| `0x00496090` | `CMCDropship__Ctor` | Constructor initializes base controller state, owner field `+0x08`, vtable `0x005dc304`, scalar `+0x10`, and sentinel `+0x0c`. |
| `0x0049cad0` | `CMCTentacle__Constructor` | Constructor installs vtable `0x005dc450`, stores owner pointer, clears tentacle cache/array fields, and seeds `+0x28` with `-1.0f`. |
| `0x0049ef80` | `CMCWarspiteDome__Constructor` | Constructor installs vtable `0x005dc484` and stores the owner-dome pointer at `+0x08`. |

Fresh Ghidra export evidence:

- `13` metadata rows.
- `13` tag rows.
- `20 xref rows`.
- `140 instruction rows`.
- `13 decompile rows`.
- Verified backup: `G:\GhidraBackups\BEA_20260607-003050_post_wave1202_cannon_motion_controller_residual_current_risk_review_verified`.

Mutation status: read-only review. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Corrected active current-risk progress is `1055/1179 = 89.48%`.
- Remaining active focused work: `124`.
- Current risk candidates: `6166`.
- Current focused candidates: `1141`.
- Live regenerated current focused candidates: `1141`.
- The legacy additive counter is deprecated (`1086/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- Active target remains `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Boundary: this proves fresh static Ghidra metadata/tag/xref/instruction/decompile read-back for the listed cannon/motion-controller rows only. Runtime cannon behavior, runtime motion-controller behavior, exact layouts, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1202; wave1202-cannon-motion-controller-residual-current-risk-review; 13 cannon/motion-controller current-risk rows; 1055/1179 = 89.48%; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 124; current risk candidates: 6166; fresh Ghidra export; read-only review; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; CCannon__VFuncSlot_02_RemoveFromWorldAndForward; CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph; CMCBuggy__CMCBuggy; CMCCannon__Dtor; CMCComponent__Ctor; CMCDropship__Ctor; CMCTentacle__Constructor; CMCWarspiteDome__Constructor; 0 / 0 / 0; 6411/6411 = 100.00%; 20 xref rows; 140 instruction rows; 13 decompile rows; G:\GhidraBackups\BEA_20260607-003050_post_wave1202_cannon_motion_controller_residual_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
