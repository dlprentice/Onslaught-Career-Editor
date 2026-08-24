# `CThing` / `CComplexThing` retail object layout

Status: active — static layout supported; `CThing__Init` runtime C2 remains RED
Last updated: 2026-08-24
Verdict: **SUPPORTED — exact PC retail envelopes and member intervals**
Evidence: MEASURED — pristine bytes, MSVC RTTI/COLs,
constructor/destructor dataflow, and five independently decoded PC-demo
witnesses; SOURCE — pinned GPL member order; MEASURED — retained runtime
preflight proves execution populations but not `CThing__Init` state transfer
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Non-retail inputs are the PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`,
and retained GPL source commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. The local analysis READY is
SHA-256 `e788ffde077c9c861d9163a7526964917cc1747c9c69f6287d9e919a1e399efa`;
its independent verification is
`cdf091efa7eceabf9df855db4e116b15760cfd0a53d9e796493a849438f07563`.

## Result

The released 32-bit PC layouts are:

- `CThing`: exactly `0x3c` bytes, ABI alignment 4.
- `CComplexThing`: exactly `0x7c` bytes including its `CThing` base, ABI
  alignment 4.

These are adjacent-boundary proofs, not allocator-size guesses. Retail
`CComplexThing` construction begins its first derived member at `this+0x3c`;
retail `CActor::Init` begins its first member at `this+0x7c`. Frozen source
member order and the intervening retail accesses fill both envelopes without
an unassigned gap.

Intervals below are half-open. Source names are used only where the retained
GPL declaration order and retail accesses agree.

### `CThing`

| Interval | Bytes | Recovered owner |
| --- | ---: | --- |
| `[0x00,0x04)` | 4 | primary vfptr for the offset-zero base/interface chain |
| `[0x04,0x08)` | 4 | base-chain storage; semantic name unknown |
| `[0x08,0x0c)` | 4 | `IRenderableThing` vfptr |
| `[0x0c,0x1c)` | 16 | `mMapWhoEntry` |
| `[0x1c,0x2c)` | 16 | `mPos` (`FVector`) |
| `[0x2c,0x2e)` | 2 | `mFlags` |
| `[0x2e,0x30)` | 2 | `mThingNumber` |
| `[0x30,0x34)` | 4 | `mRenderThing` |
| `[0x34,0x38)` | 4 | `mThingType` |
| `[0x38,0x3c)` | 4 | `mCollisionSeekingThing` |

### `CComplexThing`

| Interval | Bytes | Recovered owner |
| --- | ---: | --- |
| `[0x00,0x3c)` | 60 | inherited `CThing` |
| `[0x3c,0x6c)` | 48 | `mOrientation` (`FMatrix`) |
| `[0x6c,0x70)` | 4 | `mAnimation` |
| `[0x70,0x74)` | 4 | `mMotionController` |
| `[0x74,0x78)` | 4 | `mMissionScript` |
| `[0x78,0x7c)` | 4 | `mName` |

The allocator's 16-byte block rules do not change these C++ ABI alignments.
They concern heap block addresses and rounded allocation sizes; `CThing` itself
ends at `0x3c`, which is not a multiple of 16.

## Boundary proof

`CThing` ends at `0x3c`:

1. Strict RTTI places `CComplexThing` over `CThing` at complete-object offset
   zero.
2. `thing.h` makes `mOrientation` the first declared `CComplexThing` member.
3. At `0x004f3e70`, retail construction executes `8d 7b 3c`, then copies 12
   dwords into `[this+0x3c,this+0x6c)`.
4. The last `CThing` pointer occupies `[this+0x38,this+0x3c)`.

`CComplexThing` ends at `0x7c`:

1. Its final source-agreed pointer occupies `[this+0x78,this+0x7c)`.
2. Strict RTTI places `CActor` over `CComplexThing` at complete-object offset
   zero.
3. `actor.h` makes `mVelocity` the first declared `CActor` member.
4. Retail `CActor::Init` forms that address at `0x0040120e` with bytes
   `8d 53 7c`; the independently decoded demo witness does the same at
   `0x0040121e`.

## RTTI and lifecycle anchors

| Class/interface table | Vtable | COL | Complete-object offset |
| --- | ---: | ---: | ---: |
| `CThing` primary | `0x005df5c8` | `0x00616e28` | `0x00` |
| `CThing` render secondary | `0x005df550` | `0x00616de8` | `0x08` |
| `CComplexThing` primary | `0x005df784` | `0x00616f00` | `0x00` |
| `CComplexThing` render secondary | `0x005df70c` | `0x00616eb8` | `0x08` |

The strict RTTI graph reaches 63 `CThing` class names / 124 tables and 60
`CComplexThing` class names / 118 tables. `CSmallAirUnit` is the one reachable
class name without a corresponding strict table in this census.

The exact lifecycle bodies are `CThing` constructor `0x004f33e0`, `CThing`
destructor `0x004f3640`, `CComplexThing` constructor `0x004f3e10`, and
`CComplexThing` destructor `0x004f3f00`. They establish the vfptr transitions,
member initialization, and owned-pointer teardown. The `CComplexThing`
constructor copies exactly 12 dwords of identity-matrix storage and nulls all
four trailing pointers. Its destructor deletes `mMissionScript`, `mAnimation`,
and `mMotionController`; it performs no ownership action on `mName`, agreeing
with the retained source body.

Five selected retail/demo body pairs independently preserve the same affine
member offsets: the two constructors, the two destructors, and the
`CActor::Init` boundary witness. This is offset transfer only; it is not a
whole-body semantic-equivalence claim. Their exact entry pairs are
`0x004011e0 -> 0x004011f0`, `0x004f33e0 -> 0x004f3460`,
`0x004f3640 -> 0x004f36c0`, `0x004f3e10 -> 0x004f3e90`, and
`0x004f3f00 -> 0x004f3f80`. The five-row cross-build table has SHA-256
`4441e8c61541fe8339361cb3b2070cad736615406eb7ebb37a146633ad89f016`.

## Bounded access census

The local reproducer checked all 8,170 saved function owners and re-read
533,338 owned instruction rows / 1,770,927 bytes from the pristine image with
zero byte mismatches. It analyzed 3,603 accepted receiver contexts covering
1,030 functions and 2,016 scope/function pairs, emitting 4,216 access events:
3,688 strict and 528 explicitly name-assisted. Twenty-two events are derived
`REP` spans. No accepted context truncated; 52,879 unresolved observations
across duplicated analysis contexts were excluded rather than guessed.

Those counts are emitted lower bounds, not exhaustive cross-references. The
current local field/function aggregate is deliberately **not** promoted: five
field/function keys merged strict and name-assisted event details before
assigning a row tier. Strict membership and read/write totals were unaffected,
but the combined per-row address/offset lists are not tier-pure. A successor
must key by evidence tier or emit the two tiers separately.

## `CThing__Init` runtime state-transfer gate (2026-08-24)

Verdict: **RED — no C2 promotion.** The exact `0x004f34a0` body and this
layout identify the candidate receiver fields, but the retained runtime corpus
does not contain a target-specific call→entry→return envelope. The canonical
grade remains `C1_CANDIDATE_PARTIAL / OPEN_EXECUTED`; the complete RED contract
and witness matrix are in
[`CThing__Init__004f34a0.md`](../contracts/engine-world/CThing__Init__004f34a0.md).

The five-wave reuse preflight was:

| Wave | Disposition | Bounded result |
| --- | --- | --- |
| This layout and existing function owners | `REUSED` | The exact `CThing` intervals map the static stores at `this+0x1c`, `+0x2c`, and `+0x34`; no live value is inferred. |
| Current Generation-32 rows | `REUSED` | Exact range-set SHA-256 `639d6610c0906f371345f06e0bf3442d6bad31da53525b26844f9a48fa9a3ea8`, 301 bytes, `WORLD_SIM`, grade/open state unchanged. |
| Current and historical campaign reports | `EXTENDED` | Joined counts preserve the three observed caller families but expose no receiver/init or before/after state. |
| Three promoted G: routing inventories | `REUSED` | They route the retained corpus only; raw G: data was neither opened nor written. |
| Retained trace/TTD/CDB catalogs and call-context files | `NEW_MEASUREMENT` | 98 current `call-context.jsonl` files contain zero `0x4F34A0` target rows; positive control `0x4F9A90` appears in 11 files/rows. A poisoned expectation of one target file failed with exit 5. |

Retained call-count evidence is real but narrower: play-Level-100 has 1,579
calls partitioned into 1,481 trees, 68 Euler-branch complex things, zero
authored-basis complex things, and 30 waypoints; an independent damage-script
query has 1,578 calls. Those products do not carry per-call `this`, `init`, a
matching return, or receiver-field snapshots. The historical set-head walk is
also unusable as registration proof: its direct BSS read reported zero after an
access scan had already shown non-zero writes.

The missing runtime plate must bind two materially different caller families
to exact `this`/`init` continuity; record before/after `this+[0x0c,0x38)` while
separating base-body, callee, and derived writes; include a raw initialized/
default contrast; and fail wrong-receiver, swapped-init, wrong-field, and
cross-invocation controls. World insertion additionally needs a touched-memory
node readback whose element equals that same receiver. Until then, the static
layout remains supported and the runtime state-transfer claim remains open.

## Evidence boundary

This finding establishes static PC layouts, exact member intervals, selected
lifecycle behavior, and bounded receiver-flow observations. It does not prove
runtime values, ownership beyond the demonstrated teardown paths, complete
field cross-references, reconstruction parity, or original symbols absent from
the retained source. The detailed retail-derived event tables remain ignored
under `local-lab/pc-layout-thing-complexthing-20260813-v1/`.
