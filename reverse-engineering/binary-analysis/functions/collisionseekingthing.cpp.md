# collisionseekingthing.cpp Functions

Status: active bounded static and isolated-code contracts
Last updated: 2026-09-19 (selected initialization, speed providers and readiness queue)
Summary: collision-component ownership, initial-scan readiness, selected masks
and callback ordering; real world scanning and full projectile behavior remain open.

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **2026-08-12 live promotion closeout:** the five bounded implementation
> identities at `0x004263f0`, `0x004264a0`, `0x004269b0`, `0x00426a00`, and
> `0x00426a20` were reproduced in isolated Ghidra projects, rollback-tested,
> promoted into the PRE-backed-up live project, separately read back, copied to
> a verified POST backup, and refreshed into the byte-identical tracked
> snapshot. See the
> [collision-component identity correction](../collision-component-identity-correction-2026-08-12.md).
> This closes shared base implementation identity only; folded derived aliases,
> exact runtime behavior, layouts, and rebuild parity remain open.

> Source File: collisionseekingthing.cpp | Binary: BEA.exe
> Debug Path: 0x006246d8 (`[maintainer-local-source-export-root]\collisionseekingthing.cpp`)

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x00425a10` | `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` | same class; suffix re-read |
| `0x004261be` | `CCollisionSeekingRound__Init` | `CCollisionSeekingThing__Init` | class prefix moved; suffix unchanged |
| `0x0042627a` | `CCollisionSeekingRound__Init` | `CCollisionSeekingThing__Init` | class prefix moved; suffix unchanged |
| `0x004264a0` | `CCollisionSeekingRound__ResolveRoundCollisionResponse` | `CCollisionSeekingThing__ResolveCollisionResponse` | shared base owner and non-round-specific response recovered |
| `0x00426920` | `CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance` | class prefix moved; suffix unchanged |
| `0x00426ad3` | `CCollisionSeekingRound__CreateEffect` | `CCSRay__CreateEffect` | class prefix moved; suffix unchanged |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

The 2026-08-11 round/explosion collision join supersedes the active meaning of
that row and additionally identifies `0x00426900` as
`CCSPersistentThing__CheckCollisionFlags` and `0x004269b0` as
`CCSPersistentThing__Init`. Strict RTTI fixes their slots; the pinned
`CThing::InitCollisionSeekingThing` source fixes the persistent owner; and the
retail bodies recover immediate neighbor scanning and shared owner-`Hit`
dispatch. Historical Wave1059 labels below remain a record of what that older
pass saved, not the current semantic boundary.

## Persistent hierarchy and lifecycle — 2026-08-11

The strict retail RTTI hierarchy removes the old owner ambiguity:

```text
CCollisionSeekingRound ----------> CCSPersistentThing
CCollisionSeekingInfantryBloke --> CCSPersistentThing
CCSPersistentThing --------------> CCollisionSeekingThing
CCollisionSeekingThing ----------> CMonitor -> IListener
```

That hierarchy, exact vtable slots, and the retail bodies establish this
bounded lifecycle:

| Address | Current name | Exact static contract |
| --- | --- | --- |
| `0x00426370` | `CCollisionSeekingThing__ReplacePrimarySeekerAndRefreshOffset` | Deletes the previous primary helper, installs the replacement, and stores its owner-relative centre offset. |
| `0x004263f0` | `CCollisionSeekingThing__dtor_base` | Resets the base vtable, deletes helper pointers at `+0x14/+0x18`, then shuts down the inherited monitor. |
| `0x00426460` | `CCollisionSeekingThing__ScalarDeletingDestructor` | Calls the base destructor, conditionally frees `this` when delete bit 0 is set, and returns `this`. |
| `0x00426920` | `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance` | Scales unequal MapWho depths to a common level and returns `max(abs(dx), abs(dy))`. |
| `0x004269b0` | `CCSPersistentThing__Init` | Copies the `CInitCSThing` state, optionally arms event 3000, then performs the initial neighbor scan. |
| `0x00426a00` | `CCSPersistentThing__ProcessMapWhoCollisionSweep` | Slot 5 forwards the previous/current sector pair to the embedded detector at `this+0x24`. |
| `0x00426a20` | `CCSPersistentThing__HandleEvent` | Slot 0 accepts event number 3000 and sets collision-ready bit `0x400`; other event numbers are ignored. |
| `0x00480db0` | `CHLCollisionDetector__DispatchFilteredCollisionPair` | Rejects null/self and either failed mutual slot-8 filter, then dispatches the surviving pair. |
| `0x00480e10` | `CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions` | Recurses through four quad children and applies the same candidate/filter/dispatch path to every MapWho entry. |
| `0x00481060` | `CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Scans only newly entered 3x3 cells across descending MapWho layers, using quad traversal at the current top layer. |
| `0x004812d0` | `CHLCollisionDetector__HandleScheduledCollisionEvent` | Event 2000 re-enters collision handling with its retained peer component and then clears scheduled state. |
| `0x004f3a50/0x004f3a70` | `CCSPersistentThing` destructors | Shut down the embedded detector monitor at `+0x24`, chain through the collision-seeking base destructor, and conditionally free the object. |

`CInitCSThing::mStartCollideOnNextFrame` is the dword at initializer offset
`+0x20`, not a sound/config flag. When it is true,
`CCSPersistentThing::Init` clears ready bit `0x400` and schedules event number
3000 after `mTimeBeforeStart` at `+0x2c`; the source default is `NEXT_FRAME`
(`-1.0f`). The initial scan still runs, but the shared response body cannot
complete owner `Hit` dispatch until readiness is restored. When the flag is
false, the ready bit survives and an existing overlap may be handled
synchronously during initialization, which is the path used by the small
tutorial explosion.

This is a static C1 contract. It does not establish exact runtime event cadence,
the meaning of every detector field, collision geometry beyond the named
filters, or rebuild parity.

## Selected round initialization — 2026-09-19

Fresh pristine-byte inspection and **20 isolated original-code controls** now
bound the ordinary Forseti Missile/Blaster initialization path. The executable
is `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The selected Steam `data/default physics.dat` is 175,603 bytes, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
Inputs, original-body pins and results are in
[validation](../../../VALIDATION.md#round-collision-initialization--september-19).
The experiment executes the collision component, with controlled dependencies;
the surrounding firing/Round/Actor path below is separately established statically.

Records 163/189 omit Radius, Beam, BasedOn, Missile, Torpedo, Mesh and Length.
Native defaults therefore select the zero-radius ordinary Round path. At
`004d8611..004d867b`, it allocates a `0x3c` collision component, installs primary
vtable `005de950` and calls Actor Init. The common Thing wrapper reuses that
component and dispatches its `+0c` to `00425b50`; it does not allocate a plain
persistent component in its place. The wrapper receives `P = CInitThing+68`.

### Selected collision configuration and nested values

The firing caller invokes `CInitThing__ctor` at `00506ac9`. Its start-next-frame
and delay defaults survive the selected caller/Round prefix. At collision Init:

| `P` offset | Value or role |
| --- | --- |
| `+00` | Round receiver, written by the common wrapper |
| `+04` | Null ignored-owner pointer on this selected zero-radius path |
| `+08` | Forseti Missile `0x01000004`; Blaster `0x03000004` |
| `+0c` | Initially null; `00425b50` replaces it with its new line helper |
| `+10/+14/+18/+1c` | Desired/minimum/maximum collision levels and response: `2/1/1/1` |
| `+20` | Start next frame: `1` |
| `+24/+28/+30` | Zero |
| `+2c` | Delay bits `bf800000`, or `-1.0f` |
| `+34` | Round length: zero |

Blaster's field `0x23` contains `03000000`, a **nested type ID**, not the
runtime TreeCollision value 3. Loader `00439aa0` calls factory `0043e540`;
its case 3 installs `005dace8`. That table's `+4` points to `004059c0`, which
returns **2**. Apply `00439a8f` writes the result to RoundData `+a4`.
Consequently `004d84f0` adds exclusion bit `02000000` to Blaster's mask.
Literal-payload decoding would lose that branch.

The complete three-case factory maps type IDs `1/2/3` to getter values
`0/1/2`. Its byte-resolved RTTI labels are `COnStateType`, `COnfStateType`
and `COffStateType` respectively; `COnfStateType` preserves the binary's spelling.
This is a factory/getter mapping, not a general numeric-enum rule.

The selected null `P+04` must not be replaced by a fabricated shooter pointer.
The concrete Round filter independently rejects the shooter through the
comparison against Round `+ec` at `00425c7c..00425c88`. The mask experiment
executes the shared persistent predicate `00426900`; it does not replace the
concrete Round filter's additional shooter and trajectory logic.

### Readiness and callback order

`00426150` first constructs component flags `0x456`. With `P+20 != 0`,
`004269b0` clears ready bit `0x400`, then requests **event number 3000** with
the delay pointer `P+2c`. It always calls the initial scanner afterward.
The scanner boundary therefore sees `0x56` on the selected path.
At `004264af..004264b2`, the shared response rejects this unready component
before reading its peer or invoking shape, movement, geometry or owner-Hit
callbacks. This is not a 3000-millisecond delay or a sound event.

The original-code controls distinguish the relevant alternatives:

| Controlled change | Observed consequence |
| --- | --- |
| Selected start-next-frame value 1, or another nonzero value 2 | Event request precedes scan; no response callbacks during scan |
| Start-next-frame value 0 | No event request; successful geometry reaches both Hits inside the scan |
| Deliver event 2999, then attempt response | Still blocked before geometry |
| Deliver event 3000, then attempt response | Ready bit restored; geometry and Hits become reachable |
| High event bits set, low word 3000 | Same readiness restoration; handler reads the low 16-bit ID |
| Ready response, geometry reports no collision | Geometry executes; neither Hit executes |
| Either ignored-owner direction, or either owner's dead bit `0x10` | Ready response is rejected before geometry |
| Peer type `02000000` in the native persistent predicate | Forseti mask admits it; Blaster mask rejects it |
| Peer type zero / peer type 4 | Both masks admit / both masks reject |

Successful controlled geometry yields first `Round.Hit(peer, report)`, then
`peer.Hit(Round, report)`, with the **same report pointer** and `report+0=1`.
The geometry/Hit bodies themselves are recording stubs. Component shape
getters and owner slot `+64` are also controlled; that owner slot represents
movement delta, not the separate `+6c` velocity getter.

The initial scan receives the radius established by owner `+44`. With the
default-registry renderer result [already bounded](Actor.cpp.md#selected-round-renderer-admission),
the static Round route reaches `004f3940 → 004d8ac0`, calculating authored
radius plus `speed × float32(0.05) × 0.5`. Only **after the scan returns** does
`00425c42..00425c4e` store `float32(GetMaxVelocity() × float32(0.05) + length)`
in component `+1c`. In the experiment, controlled inputs make this visible as
`1.75` during the scan and `4.0` afterward, or `6.5` with length `2.5`.
These are synthetic distinguishing values, not shipping measurements.

Helper padding at `+10/+20/+30` is unspecified: the native code copies
uninitialized stack words there. Checks cover meaningful fields and preserved
surrounding storage without inventing zero-valued padding.

This closes the selected component's ordinary initial-scan Hit path before
Actor's random draw at `0040135d`. It does not establish actual neighbor
enumeration, scheduler cadence, collision geometry, allocator behavior or an
exhaustive shot RNG count. No retail game, desktop session, complete Round/Actor
initializer or Ghidra database was run for this experiment.

### Static candidate-filter boundary

A separate pristine RTTI census finds exactly five primary tables in the
`CCollisionSeekingThing` hierarchy, each at complete-object offset zero:

| Class | Primary vtable | Candidate filter at `+20` |
| --- | --- | --- |
| `CCollisionSeekingThing` | `005d9608` | `00426900` |
| `CCollisionSeekingInfantryBloke` | `005dbf48` | `00425a10` |
| `CCollisionSeekingRound` | `005de950` | `00425c60` |
| `CCSRay` | `005de980` | `00426900` |
| `CCSPersistentThing` | `005df6d8` | `00426900` |

For the candidate-side call, the argument is the initializing ordinary Round,
whose concrete type setter supplies `80000007`. All three filter bodies have
a bounded call path for that argument:

- `00426900` is a call-free mask test.
- `00425a10` cannot enter its apparent allegiance branch: it compares
  `(type & 00020000)` with 1 at `00425a24..00425a2d`. It reaches the same mask
  test instead; neither possible masked value equals 1.
- `00425c60` calls the mask test, can reject shooter identity, and conditionally
  checks Round configuration. Its centre/velocity providers require the other
  owner's type to contain `20` or `4000`. The selected argument `80000007`
  contains neither, so those calls are unreachable in this direction.

Thus unknown neighbor identity does not introduce a gameplay/CRT RNG call or
unresolved virtual call **inside this candidate-side filter set** for valid
retail components receiving the selected ordinary Round. This is static
instruction reasoning, not an additional native or retail execution result.
The actual scanner preserves the argument direction at `00480b83/00480b92`,
`00480c3c/00480c4b` and quad traversal `00480e7a/00480e89`.

All five tables also use the call-free map-cell-distance body `00426920` at
`+28` and shared response `004264a0` at `+18`. Overlap handling at `00480d87`
dispatches only the initiating component's response. It does not separately
call the candidate's response. The selected unready gate consequently blocks
both owner Hits on this ordinary path.

Blaster's **own** filter can ask a qualifying neighbor for its centre;
surviving pair processing asks both centres and, for a positive gap, both
maximum speeds. Neighbor centres reach the renderer getters below through
`004f3ac0`. Our Round's maximum-speed route is
`004d82a0 → +b4 → 004db600` (Gravity), not the nearby BounceFactor leaf at
`004d82d0`; both selected definitions have zero gravity. Queue insertion via
`0044b370` can still occur after an unready response returns. Those production
maximum-speed providers and queue operations are separate from the recording
stubs; their later bounded analysis follows below.

### Static renderer centre boundary

Pinned source `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`, `thing.h:246`,
types `Thing+30` as `CRenderThing* mRenderThing`; `thing.cpp` identifies its
centre-provider call as `GetBoundingBox()`. This is the renderer object returned
by the registry, distinct from the `IRenderableThing` owner interface at
`Thing+8` passed into renderer Init.

Pristine RTTI resolves five compatible primary tables. Each has complete-object
offset zero and `CRenderThing` base displacement `(0,-1,0)`:

| Renderer | Vtable | Bounding-box getter `+10` |
| --- | --- | --- |
| `CRenderThing` | `005deaac` | `00405930`: return null |
| `CRTCutscene` | `005dea38` | `00405930`: return null |
| `CRTMesh` | `005deb1c` | `004de060`: read `[this+14]`, then `[resource+150]` |
| `CRTTree` | `005deb9c` | Same `004de060` body |
| `CRTBuilding` | `005de9c0` | `004dba20`: call `+24`, null-check, then read `[result+150]` |

Building's `+24` binds exactly to `004de070`, which returns `[this+14]`.
These four complete bodies contain no RNG, allocation, resource loading or
object/global writes. Cutscene's separate animated-mesh getter is not reached
from its null-returning bounding-box slot. The calls at `004f3b20`,
`004f3b76` and `004f3b99` therefore leave no unresolved renderer callback for
valid objects in this hierarchy. `004f3ac0` computes into the supplied output;
the collision callers supply stack-local buffers.

This static closure includes the centre-provider dependency in Blaster's own
trajectory filter. It does not validate bounding-box contents, lifetimes,
runtime neighbor selection or modified vtables. Mesh/tree require a valid
resource pointer at `+14`; only the Building body checks it for null.
Neighbor maximum-speed dispatch and event queue insertion are bounded below.

### Static maximum-speed providers and linked parents

Pinned `thing.h:118` identifies primary slot `+3c` as `GetMaxVelocity`: a
movement bound, not current velocity. Pair scheduling calls the candidate's
getter at `00480f82`, stores its result as float32, then calls the initiating
owner at `00480f8d` and adds that stored candidate result.

Strict pristine RTTI admits **62 primary CThing-compatible tables** with base
displacement `(0,-1,0)`. The 62 secondary renderer-interface tables at object
offset eight are excluded. Fourteen distinct speed getters cover this set:

| Getter | Result / compatible owners |
| --- | --- |
| `00405e60` | 2.0; InfantryUnit |
| `00405ef0` | 35.0; BattleEngine |
| `004bfc50` | 10.0; EscapePod, Rocket, Pod |
| `004bfc60` | zero; 29 tables including Thing, Actor, Building and Tree |
| `004de700` | 1.0; Feature |
| `004df510` | 18.0; Shell |
| `004f84b0` | stored float32 0.2; Unit, GroundUnit |
| `0050e860` | 13.0; eight aircraft/boss classes |
| `0050e8b0` | 15.0; Carver, DiveBomber, Plane |
| `0050e9a0` | stored float32 5.8; Warspite, GillM, ThunderHead, Mech |
| `0050eaf0` | 3.5; Mine, Boat, GroundVehicle |
| `0050eb90` | `float32[[this+164]+b4]`; Submarine |
| `004d82a0` | gravity-dependent 160.0 or configuration speed; Round, Missile |
| `0050fcd0` | null parent gives 13.0; otherwise forwards parent `+3c`; Component, Tentacle, GillMHead |

The eleven constant bodies are exactly `FLD dword [constant]; RET`.
Submarine's body only reads configuration. Round and Missile both bind
gravity slot `+b4` to `004db600`, which has no calls: active torpedo state
returns zero, otherwise it multiplies configuration gravity by stored `0.025f`.
These thirteen targets introduce no RNG or further unresolved callback.

The remaining getter reads Component `+26c`. A null link uses its constant;
a non-null link tail-dispatches the parent's primary slot. The actual parent
assignment at `00428b50` is reached from Unit Init call `004f8d7c`: ECX is the
freshly initialized child, while the first argument is the original parent's
primary `this`. Factory `0050fa40` creates Component/Tentacle/GillMHead with
Unit, Thing and Monitor bases at offset zero. No renderer-interface adjustment
occurs. Constructors/Init clear the link; parent monitor shutdown clears the
registered reader cell. Destructors unregister it without promising to zero
the dying object's storage. The exact `CActiveReader<T>` specialization is
absent from the partial source; generic storage is `CMonitor*`.

This closes the forwarding **type** edge on normal fresh-child construction.
A finite, acyclic chain through these valid primary objects introduces no RNG.
The setter has no cycle guard: fresh allocation supports ordinary tree
construction, but unidentified alias writes, reinitialization and corrupt or
cyclic links are not covered. A type census alone cannot establish termination.
The current descriptive setter name has a Unit prefix; its observed receiver
here is Component-family. No source declaration or Ghidra rename is claimed.

The independent [readiness queue composition](CEventManager.cpp.md#projectile-readiness-queue--september-19)
now executes actual insertion and later delivery, keeping the selected
component unready during submission. It also identifies a precision-dependent
bucket boundary and an overflow-capacity failure. This does not execute the
pair scanner or its event-2000 receiver, and allocator/diagnostic and live-state
limits remain explicit. Full-shot RNG is still not established.

The private static receipt and complete 62-table mapping are pinned in
[validation](../../../VALIDATION.md#projectile-readiness-queue-and-speed-dependencies--september-19).

---

## Current Status

Wave 322 (2026-05-11) superseded the earlier stub wording. Later hierarchy,
source, cross-build, and retail-body work now bounds the shared base lifecycle;
it still does not constitute a complete standalone mapping of every function
historically built from `collisionseekingthing.cpp`.

Wave1059 (`collision-seeking-round-tail-review-wave1059`, `wave1059-readback-verified`) saved function-tag normalization for the collision-seeking round tail and context rows after fresh read-back. Its historical owner labels for `0x004263f0`, `0x00426a00`, and `0x00426a20` are superseded by the hierarchy-backed lifecycle above. The pass saved `131` tags across fourteen rows with no rename, signature, comment, boundary, or executable-byte change. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `812/1408 = 57.67%`; expanded static surface progress advances to `1140/1509 = 75.55%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`, `19` files, `174689159` bytes, `DiffCount=0`, `HashDiffCount=0`.

The later sections above add bounded instruction and isolated-code contracts
to this historical allocation/ownership record. They do not recover exact
source text or establish complete runtime collision behavior or rebuild parity.

## Observed Allocation Contexts

| From address | Current saved owner | Alloc size / line | Observed role |
|--------------|---------------------|-------------------|---------------|
| 0x004261be | `CCollisionSeekingThing__Init` | `0x1c`, line `0x28` | Primary CLine-style seeker/helper setup context. |
| 0x0042627a | `CCollisionSeekingThing__Init` | `0x28`, line `0x39` | Secondary CMeshCollisionVolume-style helper setup context. |
| 0x00426ad3 | `CCSRay__CreateEffect` | `0x34`, line `0x13a` | Effect/trace helper allocation context. |

The allocator callsites pass the `collisionseekingthing.cpp` debug path for provenance. The exact source helper class names and layouts are still bounded because the current retail evidence comes from debug-path strings, allocation sizes, vtable assignments, and the surrounding `CCollisionSeekingRound` decompile/read-back context.

## Wave416 Adjacent Lifecycle Helpers

Wave416 saved static Ghidra corrections for adjacent collision-seeking helper lifecycle targets:

| Address | Current saved owner | Observed role |
| --- | --- | --- |
| `0x00488e80` | `CCollisionSeekingInfantryBloke__scalar_deleting_dtor` | Scalar-deleting destructor wrapper with delete-flag check and optional object free. |
| `0x00488ea0` | `CCollisionSeekingInfantryBloke__dtor_body_00488ea0` | Destructor body that shuts down monitor state and chains to `CCollisionSeekingThing` base cleanup. |
| `0x00488ef0` | `CCollisionSeekingThing__ctor_base` | Constructor-base helper that clears field `+0x04` and installs shared collision-seeking vtable context. |

This is saved static Ghidra metadata/read-back evidence only. It does not prove runtime collision-seeking behavior or complete helper layouts.

## Related CollisionSeekingRound State

The `CollisionSeekingRound.cpp` page now records the saved Wave 322 names/signatures/comments for the surrounding cluster, including the recovered boundaries at:

- `0x00425b50` `CCollisionSeekingRound__InitCollisionLineAndSound`
- `0x00425c60` `CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`
- `0x00425e30` `CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`
- `0x00426370` `CCollisionSeekingThing__ReplacePrimarySeekerAndRefreshOffset`
- `0x004264a0` `CCollisionSeekingThing__ResolveCollisionResponse`
- `0x00426920` `CCollisionSeekingThing__ComputeScaledMapCellChebyshevDistance`
- `0x00426a00` `CCSPersistentThing__ProcessMapWhoCollisionSweep`
- `0x00426a20` `CCSPersistentThing__HandleEvent`

## Remaining Work

- Resolve the remaining helper allocations and `CCSRay`-specific overrides; the persistent/round/infantry hierarchy itself is now exact.
- Add concrete structure types and local-variable names only after stronger layout evidence; add further tags only after fresh read-back justifies them.
- Keep runtime projectile/collision behavior separate from static saved-Ghidra evidence until copied-profile runtime proof exists.
