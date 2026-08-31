# CMech__VFunc_50_004a00a0

> Address: `0x004A00A0`

Status: active static function note
Last updated: 2026-08-23
Source File: none — `Mech.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the CWarspite/CGillM/CThunderHead/CMech slot-50 destruction override.
It always enters `CGroundUnit__MarkDestroyedAndResetState`, but the Unit-
definition `CUnitShatter` boolean at `+0x130` selects the continuation. A set
value performs the profile-drop call
and calls slot-14 `CComplexThing__AddShutdownEvent` immediately, even when the
shared transition returns 0, then returns that saved result. A null value gates
on a fresh transition, releases child units, and queues event `0x0fa4` for
`mTime+3.5f`.
All four receiver vtables route that delayed event through `CUnit__HandleEvent`
to the same profile-drop and shutdown-finalization chain.
Evidence: MEASURED — pristine identity, complete-body decode/hash, whole-`.text`
rel32 census, whole-image/direct-displacement field census, strict RTTI/vtable
readback, exact Unit-definition allocation/default/property/copy/attach/free
anchors, current 8,329-row name table, and the existing manager/Unit/
ComplexThing event laws. No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x004a00a0`–`0x004a0119` inclusive through the final plain `ret`,
**122 bytes / 46 instructions**, raw SHA-256
`949f82f92d813ddce68a84141f495e1a7b3528a27feb14052c5259b99c3ee007`.
It has **5 outbound direct `E8`, 0 outbound `E9`, and 1 indirect call**. All
branches remain inside the body. Signature shape is
`int __thiscall ...(CMech *mech)`: no stack arguments are read. EAX is the
saved ground-unit transition result on the live-`+0x130` arm, 0 on the
null-`+0x130` already-dying arm, and explicit 1 after the delayed event call.

The initial `push ecx` reserves the sole four-byte local. On the delayed arm the
FPU stores the computed due time into that local before the callee-clean
scheduler consumes its six arguments.

## Stage law (byte-exact)

1. **Profile split** (`0x004a00a4`–`0x004a00b2`): read
   `[mech+0x164]`, then dword `[profile+0x130]`. There is no local null check for
   the profile pointer. A nonzero `+0x130` value takes the immediate arm; zero
   takes the delayed arm. The profile is the shared Unit/definition record;
   strict RTTI recovers the authored property class `CUnitShatter`, but not the
   exact C++ member spelling. Its stored domain is exactly `{0,1}`.
2. **Live-`+0x130` immediate arm** (`0x004a00b4`–`0x004a00d1`): call
   [`CGroundUnit__MarkDestroyedAndResetState`](../GroundUnit.cpp/CGroundUnit__MarkDestroyedAndResetState.md)
   `0x0047ce80` and save its EAX result in EDI. Without testing that result, call
   `CUnit__SpawnProfileDropPickup 0x004fd230`, then receiver virtual byte offset
   `+0x38` (slot 14). Restore the saved result to EAX and return. This arm does
   not call `CUnit__ReleaseChildUnits` and does not queue event 4004.
3. **Null-`+0x130` one-shot gate** (`0x004a00d2`–`0x004a00df`): call the
   same ground-unit wrapper and test EAX. A 0 result returns immediately, with
   no child release, profile drop, slot-14 call, or event insertion.
4. **Null-`+0x130` fresh delayed arm** (`0x004a00e0`–`0x004a0119`): call
   `CUnit__ReleaseChildUnits 0x004fcfe0`, load manager time from
   `CEventManager::mTime 0x00672fd0`, and add the exact single-precision
   `3.5f` at `0x005dc4b8` (`00 00 60 40`). Schedule through
   `CEventManager__AddEvent_AtTime 0x0044b370` with the complete tuple
   `(event=4004, target=this, time=&local(mTime+3.5f), priority=0,
   data=null, reuse=null)`. Then return explicit 1 regardless of whether the
   source-void scheduler inserted an event.

`CGroundUnit__MarkDestroyedAndResetState` owns the inner
`CUnit__MarkDestroyedAndCleanupLinks` call and the fresh-only zero at
`[mech+0x25c]`. This wrapper owns the profile split and the two continuations
above; it does not duplicate the shared teardown contract.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004a00b7`, `0x004a00d4` | `CGroundUnit__MarkDestroyedAndResetState 0x0047ce80`; mutually exclusive sites |
| `0x004a00c0` | `CUnit__SpawnProfileDropPickup 0x004fd230` on the immediate arm |
| `0x004a00c9` | indirect receiver slot 14 (`vtable+0x38`) on the immediate arm |
| `0x004a00e2` | `CUnit__ReleaseChildUnits 0x004fcfe0` on the fresh delayed arm |
| `0x004a010d` | `CEventManager__AddEvent_AtTime 0x0044b370` |

The current saved name table owns those exact function names and boundaries.
The names do not supply the missing `Mech.cpp` field or event-enum spellings.

## References and receiver closure

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references. The
image-wide aligned-dword census finds exactly **four** copies of `0x004a00a0`,
all at byte offset `+0xc8` (slot 50). The strict pristine RTTI census resolves
them and their relevant dispatch slots as follows:

| Class | Vtable | Slot 0 | Slot 2 | Slot 14 | Slot 50 entry |
| --- | --- | --- | --- | --- | --- |
| CWarspite | `0x005e0684` | `CUnit__HandleEvent 0x004f9820` | `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0` | `CComplexThing__AddShutdownEvent 0x004f43d0` | `0x005e074c` |
| CGillM | `0x005e0b30` | `CUnit__HandleEvent 0x004f9820` | `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0` | `CComplexThing__AddShutdownEvent 0x004f43d0` | `0x005e0bf8` |
| CThunderHead | `0x005e0fe0` | `CUnit__HandleEvent 0x004f9820` | `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0` | `CComplexThing__AddShutdownEvent 0x004f43d0` | `0x005e10a8` |
| CMech | `0x005e3074` | `CUnit__HandleEvent 0x004f9820` | `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0` | `CComplexThing__AddShutdownEvent 0x004f43d0` | `0x005e313c` |

Thus the slot-50 producer is virtual for exactly these four proved classes, not
a direct rel32 call. The scheduled target is that same receiver, and every
proved receiver vtable has the same slot-0/slot-14/slot-2 chain needed below.
The dynamic handler identity is therefore closed for this static family rather
than inferred from the shared numeric event ID.

## Unit-definition `CUnitShatter` field closure

The same four strict receiver vtables also place
`CMech__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` in slot 71. That body
loads `[this+0x164]` and performs the only other receiver-side read of the field,
`cmp dword [profile+0x130],0` at `0x0049fddd`. Zero exits without entering its
`"Generic Mesh"` effect path; nonzero admits that per-mesh break-effects path.
Together, slot 71 and slot 50 are the complete direct consumer set for this
four-class family: the same definition value gates both mesh shatter effects
and the destruction continuation.

The writer/domain/lifecycle is byte-closed as follows:

| Stage | Exact owner and field action |
| --- | --- |
| allocate/register | `CUnitAI__CreateAndRegisterByName 0x0042ee90` allocates a `0x1ac`-byte Unit/definition record and appends it to `DAT_008553fc` |
| initialize | `CUnitAI__InitDefaults 0x0042efd0` writes zero to record `+0x130` at `0x0042f18a` |
| deserialize | type-2 Unit-value jump-table entry `0x00432a08` maps case `0x41` to block `0x00432342`, which constructs strict RTTI class `CUnitShatter` with vtable `0x005d9b34`; slot 3 `0x00434b60` reads exactly four payload bytes to `this+8` |
| apply | strict slot 1 `CUnitShatter__VFunc_1_00432dc0` tests that payload and writes exactly `1` at `0x00432dcb` for nonzero or `0` at `0x00432ddc` for zero |
| based-on copy | `CUnitBasedOn__VFunc_1 0x004332e0` loads `DAT_008553fc` at `0x004332eb` and calls helper `0x00433390` with null/matched source at `0x00433365/0x00433378`; that helper copies source `+0x130` at `0x00433b4d` to destination `+0x130` at `0x00433b53` |
| runtime attach | `CUnit__ctor_base 0x004f7e90` clears `[unit+0x164]`; `CUnit__Init 0x004f86d0` stores `[init+0x3bc]` there at `0x004f870d`, attaching the shared definition without copying this scalar |
| clear/free | `CWorldPhysicsManager__ClearAndFreeAllDefinitionLists 0x00510a90` removes each Unit-definition entry, calls deep teardown `0x005110f0`, frees the record, clears/frees the set, and zeros `DAT_008553fc`; the scalar has no separate destructor |

The serialized payload itself is an arbitrary four-byte value, but the
property apply helper collapses it into two equivalence classes (zero/nonzero)
and the definition stores only `0` or `1`. `CUnitShatter` is therefore the
narrowest retail-authentic property name; an exact source member spelling such
as `mShatter` would still be invented. This is a definition flag, not a loot ID
or pickup-table selector. Static bytes do not identify the visible debris asset
set or the profile-drop pickup selected downstream.

Adverse control: adjacent definition property `+0x128` has its own strict
`CUnitIndiscriminate` slot-1 writer `0x00432d90` and exact sites
`0x00432d9b/0x00432dac`. It is absent from both CMech consumer bodies and from
the seven-site `+0x130` lifecycle set; the census is selective rather than an
offset-neighborhood inference. Same-displacement uses are also kept separate:
for example `CUnit__ReturnField130PackedConst_00405d90` reads runtime
`[unit+0x130]` directly and has no `[unit+0x164]` definition-pointer derivation.
The verifier emits and exhaustively partitions all 116 decoded `+0x130`
instructions; each of the five target owner functions must equal its declared
site set, not merely contain it, and all 109 non-target sites remain visible by
address/function/operand for review.

## Reuse preflight and measurement disposition

- **REUSED = 6**: this note at predecessor hash
  `c3a7b4f233caf361cd0a1c184f2e9ec09cfd024c0be4972280879375c9afe71b`;
  current 8,329-row name table
  `ghidra-function-name-table-2026-08-17.tsv` hash `4590dff9…d3213`;
  `tools/re_rtti_vtables.py` hash `90071f25…17d1d`;
  `CPhysicsScriptStatements.cpp.md` pre-extension hash `4c0f581c…6ae05`;
  `function-c1-closure-2026-08-11.tsv` hash `cfe90af3…b8974`; and
  `pc-demo-retail-virtual-target-map-2026-08-11.tsv` hash `ba2db055…4c750`.
- **EXTENDED = 2**: this canonical Mech function note and the canonical
  `CPhysicsScriptStatements.cpp.md` writer/copy map; no new evidence root.
- **NEW_MEASUREMENT = 1**: focused read-only verifier
  [`tools/re_cmech_profile_field.py`](../../../../tools/re_cmech_profile_field.py),
  hash `9f1fb04f…e4fc`, plus eleven focused tests with eight can-fail mutations. It
  reproduces 156 raw little-endian `0x130` occurrences image-wide (155 `.text`, one `.data`), 116
  decoded current-function-range displacement uses, the seven owned lifecycle
  sites above, strict RTTI closure, body hashes, and the `+0x128` control.

## Delayed event and shutdown-finalization path

At fixed manager time, the exact 3.5-second due time maps under the existing
manager law to ring offset `floor((3.5-0.001)*20)=69` from the current insertion
bucket and fires after **70** fixed 0.05-second advances. When due:

```text
CEventManager__Flush
  -> receiver slot 0 = CUnit__HandleEvent
  -> event 4004 arm
  -> CUnit__SpawnProfileDropPickup
  -> receiver slot 14 = CComplexThing__AddShutdownEvent
  -> script event-id 3/delete when applicable, set TF_DECLARED_SHUTDOWN
  -> schedule thing-event 2000 (SHUTDOWN) at NEXT_FRAME
  -> CUnit -> CActor -> CComplexThing 2000 handler chain
  -> receiver slot 2 = CUnit__VFunc02_CleanupWorldLinksAndForward
```

This is the same delayed profile-drop plus shutdown-finalization semantics as
the component producer, with a 3.5-second rather than 7.0-second arm. Numeric
4004 is not treated as globally meaningful: the conclusion follows from all
four slot-0, slot-14, and slot-2 reads above. The immediate live-`+0x130` arm
joins the same drop-plus-slot-14 path without first queueing 4004.

## Manager boundary and failure behavior

The manager owns allocation, ring order, clock advancement, and slot-0
delivery. This producer owns only its fresh-null-profile tuple. Invalid-manager
and pool-exhaustion paths log and return; null-target and over-1,000,000-second
paths return without queueing. `AddEvent_AtTime` exposes no success status, so
this wrapper still returns 1 and does not roll back its already-completed child
release when insertion fails.

The delayed handler and its slot-14 callee are also source-void. Neither reports
whether the downstream event-2000 insertion succeeded.

## Open questions

- `CUnitShatter` is the retail-authentic property-class name and the stored
  domain is `{0,1}`, but `Mech.cpp` is absent, so the exact C++ member spelling
  at Unit-definition `+0x130` remains unavailable.
- `Unit.cpp` and its event enum are absent, so the authored spelling of 4004 is
  unknown. The receiver-specific retail effects are byte-closed without
  inventing that spelling.
- Static bytes prove that the live-`+0x130` arm performs the drop and slot-14
  call even when the saved transition result is 0. Runtime frequency and any
  repeated-call presentation were not measured.
- The exact visible debris/presentation selected by the shatter path, the
  profile-drop callee's concrete authored pickup table, runtime frequency, and
  rebuild parity remain outside this static function slice.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004a00a0`–`0x004a0119` is not
  `949f82f9…c3ee007`, the body is not 122 bytes / 46 instructions, or its final
  instruction stops being plain `ret`.
- The live-`+0x130` arm stops calling the ground-unit wrapper, profile-drop
  callee, and receiver slot 14 unconditionally before returning the saved
  wrapper result.
- The null-`+0x130` arm stops gating child release and event insertion on a
  nonzero wrapper result, or the tuple ceases to be
  `(4004, this, mTime+3.5f, 0, null, null)`.
- The reference census is not zero rel32 plus exactly the four strict slot-50
  entries above.
- Any definition-field lifecycle site differs: default `0x0042f18a`, truth
  writers `0x00432dcb/0x00432ddc`, copy `0x00433b4d/0x00433b53`, or consumer
  reads `0x0049fddd/0x004a00aa`; or strict `CUnitShatter` stops owning
  `0x00432dc0` in vtable `0x005d9b34` slot 1.
- Any of those four receiver vtables stops resolving slot 0 to
  `CUnit__HandleEvent`, slot 14 to `CComplexThing__AddShutdownEvent`, or slot 2
  to the named CUnit cleanup forwarder.

## Reproduction

Run read-only from the repository root after verifying the official specimen:

```bash
sha256sum ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup
python ./tools/re_cmech_profile_field.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup --out-json .artifacts/cmech-profile-field.json
python ./tools/re_cmech_profile_field_tests.py
python ./tools/disasm_va.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004a00a0 --count 46 --bytes
python ./tools/call_xref_scan.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004a00a0 0x0047ce80 0x004fcfe0 0x0044b370
python ./tools/operand_scan.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x00000fa4 0x004a00a0 0x004f9820 0x004f43d0 --window 8
python ./tools/pe_read_va.py ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x005dc4b8 --count 4 --as float
python ./tools/re_rtti_vtables.py --binary ./local-lab/safe-copy-bea-pristine/BEA.exe.original.backup --out-tsv .artifacts/mech-vtables.tsv
```

## Receipts

- 2026-08-23 — verified the exact Unit-definition lifecycle from allocation and
  zero default through strict `CUnitShatter` type `0x41`, zero/nonzero-to-boolean
  apply, based-on copy, runtime attachment, both four-receiver consumers, and
  registry teardown. Exact replays from ordinary-main and separate-worktree
  roots plus eleven focused tests (including cross-root JSON byte identity and
  target/control/factory/based-on/identity/table-drift attacks) are owned by the
  focused verifier. Both replays are 34,754 bytes with JSON SHA-256
  `32209c427a71fc1519e7096d8ec54dd950590533b1b69533f98a4fa45bffba15`;
  `nameTable.path` is the stable repository-relative identity, while its
  hash/8,329-row pins remain visible. Adjacent `CUnitIndiscriminate +0x128` is
  the adverse control.
  Exact source member spelling, presentation, loot-table identity, and rebuild
  parity remain open.
- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, five direct calls, one indirect call, zero
  inbound rel32 references, four strict slot-50 entries, exact profile split,
  immediate-arm ordering/result restoration, delayed tuple/constant/time
  formula, and every slot in the receiver dispatch/finalization path with
  read-only PE/capstone/RTTI probes.
- Related contracts:
  [`../GroundUnit.cpp/CGroundUnit__MarkDestroyedAndResetState.md`](../GroundUnit.cpp/CGroundUnit__MarkDestroyedAndResetState.md),
  [`../Unit.cpp/CUnit__HandleEvent.md`](../Unit.cpp/CUnit__HandleEvent.md), and
  [`../CEventManager.cpp.md`](../CEventManager.cpp.md).
