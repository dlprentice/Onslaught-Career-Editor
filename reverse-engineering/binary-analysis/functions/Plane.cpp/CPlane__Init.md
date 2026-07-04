# CPlane__Init

Address: `0x004d19d0`

Saved signature: `void __thiscall CPlane__Init(void * this, void * init_thing)`

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
- `py -3 tools\ghidra_plane_init_wave483_probe_test.py`
- `cmd.exe /c npm run test:ghidra-plane-init-wave483`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`

## Deferred

Exact `CPlane` layout, exact `init_thing` field meaning, `CWarspite` semantics/signature, runtime flight/launch behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
