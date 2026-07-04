# Wave1118 Particle/Message Current-Risk Review

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1118-particle-message-current-risk-review`

Wave1118 accounts for `13 rows` from the Wave1108 current focused denominator as the score-26 particle/message current-risk head, moving current focused accounting to `100/1179 = 8.48%` of current focused candidates: 1179. The wave used a fresh read-only Ghidra export and no mutation.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x004729d0 CGameInterface__ctor_base` | Constructor-style base body for the global GameInterface object; initializes the base monitor/control field at `this+0x04` and installs the `0x005dbc2c` vtable. |
| `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` | DATA xref from `0x005dbcf8`; vtable slot 3 dispatches base update context, selects support/escort target context, builds the aim transform, and calls `CUnit__ForwardAimTransformAndAttachTargetReader`. |
| `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags` | DATA xref from `0x005dbcfc`; vtable slot 4 updates two ballistic firing-readiness flags through `CUnit__CanFireAtTarget_BallisticArcB/A`. |
| `0x004b6e50 CMessage__ctor_base` | Mission-script sound and unit damage/effect xrefs; `RET 0x1c` confirms seven stack arguments after `this`, with `message_text`, `active_reader_target`, and `queue_sort_key` preserved in the queued message. |
| `0x004cae50 CParticle__Destroy` | Particle manager/game/frontend/CDXEngine shutdown xrefs; frees the observed `+0x88` resource block after the particle-set vfunc `+0x38` guard and unlinks the active-list/owner handle at `+0x58`. |
| `0x004cb0e0 CParticleManager__Init` | Allocates the `0x200` entry particle pool, constructs `0xd8` byte nodes, links the free list through `+0x68`, inserts into `DAT_009c63f4`, and increments `DAT_0082b3ec`. |
| `0x004cb1b0 CParticleManager__Shutdown` | Destroys the `0xd8` byte particle array, frees the backing allocation, recursively releases the next manager pointer, and decrements `DAT_0082b3ec`. |
| `0x004cb210 CParticleManager__Update` | Frontend process and CDXEngine render xrefs; clamps/stores delta time, updates active particles, dispatches render-node callbacks, prunes dead particles, and calls `CParticleManager__CleanupHandles`. |
| `0x004cb5c0 CParticleManager__AllocateParticle` | Create-effect and descriptor-update xrefs; allocates/recycles from the free list, creates another manager pool when allowed, applies effect-type LOD skip thresholds, and dispatches particle-set vfunc `+0x24`. |
| `0x004cbca0 CParticleManager__UpdateParticles` | Called by `CParticleManager__Update`; walks active particles, dispatches handle-state vfunc `+0x54`, decrements lifetime, integrates position by global delta, and observes `DAT_009c63fc`. |
| `0x004cbe30 CParticleManager__PruneDeadParticles` | Called by `CParticleManager__Update`; recounts live particles at manager `+0x1c`, unlinks death-flagged particles, calls `CParticle__Destroy`, and recycles nodes to manager `+0x8`. |
| `0x004cc870 CParticleSet__dtor_base` | Scalar-deleting destructor and unwind xrefs; restores base vtable pointer `PTR_LAB_005ddad4` before return/free paths. |
| `0x004cd7f0 CParticleSet__LoadFromArchive` | `CParticleSet__LoadParticleSetFile` xref; destroys the current list, allocates a `0x1388c` archive workspace, validates token ids `0/1/2/3/4`, dispatches created-set vfunc `+0x18`, resolves references, and returns success/failure. |

Fresh export evidence:

- Metadata: `13` rows, `targets=13 found=13 missing=0`.
- Tags: `13` rows, `missing=0`.
- Xrefs: `34` rows.
- Instructions: `1521` rows, `targets=13 missing=0`.
- Decompile: `13` rows, `targets=13 dumped=13 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified`.

Boundary:

This is static read-only Ghidra/source-reference evidence. It does not prove runtime particle behavior, runtime message behavior, runtime targeting behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
