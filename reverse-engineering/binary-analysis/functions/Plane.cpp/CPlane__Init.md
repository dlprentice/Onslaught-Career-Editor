# CPlane__Init

Status: active static function note
Last updated: 2026-09-08
Summary: Plane initialization, selected training-aircraft animation ownership,
and the script-spawn collision-delay boundary; runtime parity remains open.

> Source File: Plane.cpp absent from the pinned partial source | Binary: BEA.exe
> Evidence: specimen-bound static instructions and the selected aircraft mesh; no new runtime observation.

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d19d0` | `CPlane__Init` | `void __thiscall CPlane__Init(void * this, void * init_thing)` |

## Wave483 Read-Back

Wave483 hardened the saved Ghidra signature/comment/tags for the retail plane init entry. The function uses `ECX` as `this`, reads one stack argument at `[ESP+0x54]`, and returns with `RET 0x4`, so the current saved model is a `__thiscall` init with one explicit `init_thing` argument.

Important instruction evidence:

| Address | Evidence |
| --- | --- |
| `0x004d19e9` | Reads the stack argument into `EBX`. |
| `0x004d19f0` | Copies `ECX` into `ESI` as `this`. |
| `0x004d19f3` | Writes `1` to `[EBX+0x80]`, meaning `init_thing+0x80`. |
| `0x004d19fd` | Calls `CAirUnit__Init`. |
| `0x004d1a28` | Calls `CAirGuide__ctor`. |
| `0x004d1a49` | Stores the guide pointer at `this+0x208`. |
| `0x004d1a6a` | Calls `CWarspite__Init`. |
| `0x004d1a82` | Stores the CWarspite-like pointer at `this+0x13c`. |
| `0x004d1a9c` | Pushes launch string pointer `0x006243f8`. |
| `0x004d1b1e` | Pushes Engine string pointer `0x00622cec`. |
| `0x004d1b9d` | Calls `CSPtrSet__AddToTail` for the `this+0x1d4` list. |
| `0x004d1bae` | Calls `Random__NextLCGAbs`. |
| `0x004d1bdc` | Writes roll bits `0x3f4ccccd` (`+0.8`) to `this+0x284`. |
| `0x004d1be8` | Writes roll bits `0xbf4ccccd` (`-0.8`) to `this+0x284`. |
| `0x004d1c04` | Returns with `RET 0x4`. |

## Behavior Summary

- Marks `init_thing+0x80` before delegating to `CAirUnit__Init(this, init_thing)`.
- Allocates a `0x30` guide component, initializes it through `CAirGuide__ctor`, and stores it at `this+0x208`.
- Allocates a `0x64` CWarspite-like component, initializes it through `CWarspite__Init(this, init_thing)`, writes vtable pointer `0x005de73c`, and stores it at `this+0x13c`.
- Looks up the `launch` animation through `CMesh__FindAnimationIndexByName` and updates launch state/timer fields at `this+0x27c` and `this+0x280`.
- Enumerates `Engine` hardpoints, allocates 8-byte nodes, links them through `CWorldPhysicsManager__PushNodeGlobalList`, and appends them to the list at `this+0x1d4`.
- Randomly writes `+0.8` or `-0.8` into `this+0x284`.

## Xrefs And Source Boundary

The only current xref into `0x004d19d0` is a `DATA` reference from `0x005e1954`, consistent with a table/vtable-style reference rather than a normal direct caller.

The retail binary carries debug string `[maintainer-local-source-export-root]\Plane.cpp` at `0x00631630`, but the current Stuart source snapshot does not contain `Plane.cpp`, `CPlane`, or `CWarspite` source bodies. Treat the function name and behavior as retail static evidence, not source-body parity.

## Validation

- `ApplyPlaneInitWave483.java` final dry/apply/verify logs saved successfully.
- The initial comment pass exposed and corrected a stale human claim that the `0x80` write was on `this`; final read-back and probe require `init_thing+0x80`.
- The retired focused probe and queue check passed; their implementations remain
  available in Git history.

## Deferred

Exact `CPlane` layout, exact `init_thing` field meaning, `CWarspite` semantics/signature, runtime flight/launch behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Selected training aircraft, September 8

Fresh static reads use pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The shared Air Trainer/Target Drone mesh `m_FA_F24_training.msh.aya` is
26,677 bytes, SHA-256
`48876552ae836750221241719f333fb9b5221f78f1ab8bc03d5950cdbf4e6ec5`:
12 parts, 11 CEMT bindings and no CAMD animation modes.

Missing `launch` mode does not eliminate animation construction. Plane Init
passes the lookup result `-1` to virtual `+0xf0`. The setter at `0x004f44a0`
allocates an animation owner when `this+0x6c` is null; its constructor queues
event 3000 for NEXT_FRAME (`-1.0f`). The subsequent mode setter retains mode
index `-1`, resets frame to zero, enables looping, and substitutes increment
`1.0f` for the missing mode's zero result. This event is admitted before the
Plane-specific spin draw. Absence of visible animation is not absence of an
event owner.

Script `SpawnThing` constructs a fresh initializer at `0x00536d54`, retaining
constructor `+0x88 = 1`. At `0x00536fa8`, after two argument pushes, it writes
`1.5f` (`0x3fc00000`) to initializer `+0x94`. Plane changes `+0x80` to one,
not either delay field. Persistent collision initialization clears readiness
bit `0x400` and schedules its event 3000 relative to that delay. The initial
neighbor scan still occurs with readiness clear. This is the script-spawn
route, not proof of the world-authored Trainer's collision delay.

The same initializer keeps orientation type zero: the emitter branch supplies
yaw and pitch derived from the owner's current emitter forward, zero roll and
zero velocity. An all-zero emitter position selects the owner-position and
owner-basis-to-Euler fallback. The rebuild's precomputed spawn pose does not
yet reproduce this creation transaction.

Re-read body identities use half-open ranges:

| Body | Range | SHA-256 |
| --- | --- | --- |
| Plane Init | `0x004d19d0..0x004d1c07` | `f297eb3687986960d06f2ed1b03e45b137a9ca2fd34a56472e390b36ee302a2a` |
| Script SpawnThing | `0x00536cd0..0x005371e0` | `cd7c8f28d7c21ce976f405baffde1f7eb9727d6822f3e1c38536eb92a798eb5e` |
| InitThing constructor | `0x0048dcf0..0x0048ddd0` | `7c9cb28a5a8f66ea786f9943ce904e982a41581e5a433de3754ee9b9996c59ef` |
| Persistent collision Init | `0x004269b0..0x004269f6` | `bd4cf3f803c5d5a661b2d81ef96d1c2753a6ba4be722a4d1c6673ea96dedddd4` |
| Animation allocation/setter | `0x004f44a0..0x004f4528` | `ebebf118cf20136f6ef013d2e2592771c9a6f4b13174bd766acb9033388ddab1` |
| Animation constructor | `0x004046d0..0x0040474d` | `e3cd9b697b3fe781735a31d3a2d806ac323f83b333445367a4e6669253dd2c64` |
| Animation mode setter | `0x00404860..0x004048ba` | `e643d3cc227058c6ae6a12af074b84a832da215fa2454b763a42dd2deb8019d7` |
| Mesh mode increment lookup | `0x004aa7e0..0x004aa81f` | `7152c64d81cf5a035f0cb54729e9664d6e0e6794eaf24ae71bd1e7b3c703eec9` |

No complete constructor RNG count is established. The inspected local
renderer/animation helpers add no shared draw, but resource preload, cache
residency and transitive loader work remain open. These are static contracts;
no new live play, writable Ghidra session or metadata promotion was performed.
