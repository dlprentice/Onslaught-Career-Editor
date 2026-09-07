# CActor__Init

> Address: `0x004011e0`

Status: active bounded static/runtime note — **RED for C2 promotion**
Last updated: 2026-09-07
Summary: exact retail `CActor__Init @ 0x004011e0` identity and two retained
caller-family write observations are reproduced, but every observed return
crosses a replay gap and the endpoint memory queries do not read back from the
requested return sequence. The Generation-32 grade therefore remains
`C1_CANDIDATE_PARTIAL` / `OPEN_EXECUTED`; this note makes no VERIFIED/C2 count
claim. The September 7 extension below resolves the complete static Actor
body and ordered base-call boundary for World110 construction; it adds no
runtime observation or campaign promotion.
Evidence: MEASURED — Generation 32, pristine-body/static owners, retained
Level-100 TTD trace, target-filtered call/entry/raw-return events, same-boundary
Overwrite/Write pairs, and four injected verifier controls. Source names and
member intent are SOURCE analog evidence only.
Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Runtime image: copied windowed target `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`.
Source File: `references/Onslaught/actor.cpp` | Binary: `BEA.exe`

## Identity and static boundary

- Exact body: `[0x004011e0,0x004013c4]`, 485 bytes, 148 instructions;
  `RET 0x4` is at `0x004013c2` and proves one explicit stack dword after
  `ECX`.
- Raw pristine body SHA-256:
  `434f5fd6f9e3a04274452dbdbf4cc04f21bc514f25cdeab76e03eff3f6875ad4`.
  Generation-32 range-set SHA-256:
  `0b1c5e7dedd1d8b4a059ac056bac6be6d0afe5436b615a80f4b5db7f921a6011`.
  The dated closure range digest is
  `74768a5019003baf53f959a0c8e81f29b723fcaf2ba1282aeb3c6318c9c7e2f9`;
  these digests use different documented encodings and are not interchangeable.
- The exact trailing `[0x004013c5,0x004013d0)` residual is Generation-32
  terminal padding. It was also used as a `0/0/0` runtime control and did not
  fire.
- Static direct callees are `CComplexThing__Init @ 0x004f3fd0`,
  `Random__NextLCGAbs @ 0x004de8d0`, and
  `CEventManager__AddEvent_AtTime @ 0x0044b370`.
- [`../cthing-ccomplexthing-layout-2026-08-13.md`](../cthing-ccomplexthing-layout-2026-08-13.md)
  proves that inherited `CComplexThing` storage ends at `this+0x7c`; the first
  `CActor` member begins exactly there.

## Prototype

```c
void __thiscall CActor__Init(void *this, void *init);
```

The names are the current bounded analysis vocabulary. Concrete dynamic type,
nullability, ownership, and the complete `CInitThing` retail layout remain open.

## Pinned-source analog boundary

Pinned `actor.cpp:15-40` initializes three contact timestamps, last-move time,
velocity, old position, old orientation, then calls the superclass initializer,
seeds the full-move counter, and schedules the first move event. The source files are SHA-256
`72ff886915a2cb7ef82e5992538214027f5d13a45be804606e7031ba9ecb9d82`
(`actor.cpp`) and
`0af427656cfb9dbbc1afb9a207d0ac6c1deea944e44b05019bfad30315e3f2cf`
(`actor.h`). This establishes developer naming, member order, and intended
shape for that lineage; it does not prove Steam behavior by itself.

The runtime joins below are limited to watched destination dwords and exact
writer boundaries. They do not promote unwatched source branches or source
semantics.

## Complete static initialization boundary (2026-09-07)

This is a normal-return, valid-input contract for the pristine specimen named
above. The retained exports are under
`local-lab/ghidra-fullpass-2026-07-23/exports/`; their instruction bytes were
compared directly with the PE-mapped specimen, without opening Ghidra. All
362 instruction rows in the three bodies matched. Bounds below are half-open;
the name table's upper addresses are inclusive and must be incremented.

| Owner / retained decompile | Body / bytes | Raw body SHA-256 |
| --- | --- | --- |
| `W001/decompile/004011e0_CActor__Init.c` | `[0x004011e0,0x004013c5)`, 485 | `434f5fd6f9e3a04274452dbdbf4cc04f21bc514f25cdeab76e03eff3f6875ad4` |
| `W007/decompile/004f3fd0_CComplexThing__Init.c` | `[0x004f3fd0,0x004f4111)`, 321 | `7b0bc6bcc32ae9a36fe53e86c7d93e3fea3423896bec0aa0dba740c04a3d1212` |
| `W007/decompile/004f34a0_CThing__Init.c` | `[0x004f34a0,0x004f35cd)`, 301 | `b54ff4165a998127328eafd4e63175249216437d2cfc3996f74beb2a388d35d4` |

The three export-file hashes, in table order, are
`a3f996b22faccaf2ae2df66c38355517f4b646c837f55744863c954b69fd0438`,
`8b6b744b54f7ac0259e71a8a9455d1ffb9d3238a1fed0a6ab694d936937224f0`,
and `981970a1f60fc2f83ae8b2a9f6eb38f489c97eb64e4bf1f68e2502fc5947beec`.
Source bridges are pinned commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`, `actor.cpp:15-40,213-226`,
`actor.h:7-10,58-65`, `thing.cpp:40-85,591-610,613-632,651-667`, and
`thing.h:41-51,131-136`. The Actor source hashes remain those above;
`thing.cpp` is `e930244e01fbad5fe7e15c2595ce595282fb4c982a469cf604e5b9e0de09727e`
and `thing.h` is `cf0c15e24869d57ab354251f465aee6dc1780c6f7c557fec27d081d71a46e8fe`.

### Ordered Actor-owned operations

1. `0x004011ed..0x00401204` writes `0xc2c80000` (`-100.0f`) to
   `this+0xcc/+0xd0/+0xd4`, then copies the current event-time dword at
   `0x00672fd0` to `this+0xd8`. This does not reset the event clock.
2. `0x00401217..0x00401247` copies all four dwords of velocity
   `init+[0x50,0x60)` to `this+[0x7c,0x8c)`, then all four position
   dwords `init+[0x04,0x14)` to old position `this+[0x8c,0x9c)`.
   These writes precede collision/render initialization, whose callbacks can
   read velocity and old position.
3. Discriminator `init+0x60 == 0` builds old orientation from yaw/pitch/roll
   at `+0x44/+0x48/+0x4c`; `== 1` copies 12 dwords from `init+0x14`;
   other values leave old orientation untouched. The Euler arm uses x87
   `FSIN`/`FCOS` and staged float stores, then copies 12 dwords to `this+0x9c`
   at `0x0040133e`. Only nine matrix components are calculated: the fourth
   dword of each row is copied stack padding, not a demonstrated zero.
4. Call `CComplexThing__Init(this, init)` at `0x00401343`. The original
   initializer pointer is forwarded. Actor performs no later pose recopy;
   base/virtual effects below can therefore change the final old/current pose.
5. After the base returns, call receiver virtual `+0x60` at `0x0040134c`.
   `FISTP qword` followed by a low-dword load produces divisor `r`. The
   body does not set the x87 control word; generic fractional/invalid values
   cannot be replaced with an assumed C# truncation law.
6. Call `Random__NextLCGAbs` at `0x0040135d`, passing the seed pointer stored
   at `0x008a9d9c`. This is exactly one direct draw, even when shutdown is
   declared or `r == 1`. Signed `IDIV r` supplies remainder `q`, written to
   `this+0xdc` at `0x00401369`. There is no zero-divisor guard.
7. If `this+0x2c & 1` is set, return with counter `q` and no movement request.
   This is `TF_DECLARED_SHUTDOWN`, **not** inactive/deactivated state. Otherwise
   store `q - 1`. A positive result requests `LF_MOVE` (`3001`); a zero or
   negative result calls virtual `+0x60` a second time at `0x0040138c`, performs
   the same conversion, resets the counter to that result, and requests
   `MOVE` (`3000`). At `0x004013b7` the request is
   `AddEvent_AtTime(manager=0x00672fc8, event, this, &-1.0f, 0, null, null)`.
   This is an enqueue attempt; manager validity/capacity can make it fail.

The shared RNG is already implemented by `Level100ReleasedRandom`, using the
shipped multiplier 48271 and modulus **214783647**, with wrapping signed
arithmetic. Its byte-checked body `[0x004de8d0,0x004de95a)` hashes to
`f33a7592cf35d9e67f07ffd18af33d0b44c76ae0698c2f783d007a296a5abc93`.
No seed at a particular World110 actor boundary is inferred here: earlier
constructors, scripts' allocation dependencies and collision callbacks retain
their own possible effects. Reuse the existing
[event-manager owner](CEventManager.cpp.md) and `RetailEventScheduler` for
admission and FIFO ordering; `NEXT_FRAME` is a negative-time request, not a
direct call to `Move` or an instruction to invent a separate timer.

### Ordered inherited effects and mutable initializer

`CComplexThing__Init` first dispatches `+0xa8(init+0x1ac)` at `0x004f3fe9`,
then calls `CComplexThing__SetScript(this, init+0xac)` at `0x004f3ff8`.
Only then does it initialize current orientation at `this+0x3c`, with the
same mode-0 Euler / mode-1 12-dword-copy / other-mode-no-write distinction,
and call `CThing__Init` at `0x004f40de` or `0x004f4102`.

For the World110 tables below, `+0xa8` resolves to `CComplexThing__SetName`:
it removes/frees an existing name, and for a nonempty new name allocates and
copies the string before adding this receiver at the **head** of named set
`0x00855130`. SetScript deletes an existing `this+0x74`, looks up/clones
nonempty script code, constructs its interface and writes `+0x74`, then
requests `INIT_SCRIPT` (`2001`, time `-1.0f`, lane 0, null data/reuse) if code
was found. It does **not** execute the script's Init or Ready inline. The
enqueue follows the allocation branch even if allocation returned null.

`CThing__Init` then performs these operations in order:

| Site | Supported operation / dependency |
| --- | --- |
| `0x004f34b5` | If `this+0x30` is null, virtual `+0x88(init)` initializes the render chain. The common `0x004f35d0` asks virtual `+0x20` for OID, calls `0x005164b0` with render interface `this+8`, and stores the result at `+0x30`. Descriptor objects run their own Init before this call returns; presentation work cannot be treated as absent constructor effects. |
| `0x004f34c2` | Virtual `+0x98(0)` establishes the complete concrete type word at `+0x34`. For Unit-derived targets it depends on Unit profile pointer `+0x164` and profile `+0x104`; it is not merely the Actor lineage mask. |
| `0x004f34d2..0x004f34e5` | Copy all four authored position dwords to `this+[0x1c,0x2c)`. |
| `0x004f34ea..0x004f3534` | If virtual `+0xb0` permits ground clipping, sample `0x0047eb80` with map `0x006fadc8`; for finite height below current Z, dispatch `+0x50` with a copied position whose Z is that height. There is no radius/COfG subtraction in this base clamp. |
| `0x004f353f..0x004f3559` | If virtual `+0xc4` is zero, clamp finite Z above water dword `0x006fbdfc` by a **direct current-Z store**. It does not teleport or synchronize old Z. |
| `0x004f3560..0x004f3594` | If flag `0x2` is set, initialize MapWho with current position, receiver and `init+0xa8` force radius. If signed layer `this+0x18 < 3`, append receiver to big set `0x00855170` and OR flag `0x40`. Then dispatch collision Init `+0x8c(init+0x68)`. |
| `0x004f35a2..0x004f35c0` | OR type bit `0x800000` if a render object exists; call `+0x5c` only for raw `init+0x3ac == 0`; finally add receiver at the **head** of world set `0x00855090`. Active nonzero does not cause an Activate call. |

None of these three bodies resets the complete flag word or assigns a thing
number. Those are constructor/derived-owner responsibilities. The common
Actor teleport `0x00401910` copies the clamped four-dword position to old
position, calls `CThing__Teleport` (`0x004f3ce0`, itself dispatching `+0x4c`),
then updates/notifies MapWho/collision if a prior sector exists. Consequently,
ground teleport can synchronize old/current Z, while the subsequent water
clamp can separate them again. The watched Unit lane below corroborates one
transitive old-Z overwrite, not every World110 pose outcome.

MapWho helper `0x00492ba0` calls owner `+0x40` for radius and secondary/render
`+0x54` for a box; a box replaces the radius with its XY enclosing extent,
then a nonnegative `init+0xa8` overrides it. Thus even an explicit radius does
not skip the earlier virtual calls. Layer selection, sector conversion and
MapWho insertion finish before the big-set/collision steps above.

Collision Init is not read-only on the initializer. Common helper
`0x004f39c0` does nothing when signed `init+0x70 == -1`; otherwise it lazily
allocates a `0x38`-byte persistent component, changes `init+0x80` from 2 to 1
if no render object exists, writes receiver to `init+0x68`, and invokes the
component's `+0x0c` Init. Ground-vehicle override `0x0047c8e0` first allocates
a `0x1c`-byte shape into `init+0x74` when null, using virtual `+0x44` bounding
radius multiplied by stored `0.8f`; it then always calls the common helper.
The persistent component Init at `0x004269b0` calls its base, conditionally
clears ready bit `0x400` and requests component event `3000` using
`AddEvent_TimeFromNow(init+0x94)` when `init+0x88 != 0`, then always performs
an initial neighbor scan. Existing
[collision evidence](collisionseekingthing.cpp.md#persistent-hierarchy-and-lifecycle--2026-08-11)
owns the downstream filters and possible synchronous owner-Hit path. Such
callbacks precede final world insertion and the Actor RNG draw.

### World110 concrete virtual dependencies

Direct specimen dword reads bind the table slots below. The admitted selector
factory at `[0x0050df80,0x0050e7f4)` installs the three concrete tables;
all 549 retained W008 instruction rows matched, raw body SHA-256
`a30e5fb1fce83522dd93710391bbb624e126f983e1a4e527f858a2c2e914e548`.
The class Init slot `+0x24` supplies an independent identity check.

| Receiver | Primary table | Init `+0x24` | Multiplier `+0x60` | Ground `+0xb0` | Collision `+0x8c` | Type `+0x98` |
| --- | --- | --- | --- | --- | --- | --- |
| Squad LightTank/Sabre, selector 2 | `0x005e297c` | `0x0047cfd0` | `0x0050e940`: 4.0f | `0x004014a0`: true | `0x0047c8e0` | `0x0050e970` |
| Fighter/LightFighter, selector 8 | `0x005e1930` | `0x004d19d0` | `0x004de700`: 1.0f | `0x004014a0`: true | `0x004f39c0` | `0x0050e870` |
| Lander, selector 12 | `0x005e1dd8` | `0x00446d70` | `0x004de700`: 1.0f | `0x004dfcb0`: `!(flags & 4)` | `0x004f39c0` | `0x0050eab0` |

All three use `+0x50 = 0x00401910`, `+0x88 = 0x004f35d0`,
`+0xa8 = 0x004f4120`, `+0xc4 = 0x00405930` (false), and
`+0x5c = 0x004fd700`. The latter clears active field `+0x214` and deactivates
the linked target/children when previously active; it does not set shutdown
bit 1. `CBattleEngine` table `0x005d89c4` likewise uses multiplier 1, but
has its own type/deactivation targets `0x00405f00` / `0x00406020`.

For multiplier 1, the direct draw remains mandatory: absent shutdown the
initial counter becomes 1 and MOVE is requested. For multiplier 4 and a
nonnegative RNG return, remainders 0/1 reset counter to 4 and request MOVE;
remainders 2/3 leave counters 1/2 and request LF_MOVE. Preserve the signed
instruction law for unusual RNG states rather than turning this example into
an unsigned implementation.

Additional byte-checked helper body identities (half-open ranges) are:

| Helper | Range | Raw body SHA-256 |
| --- | --- | --- |
| SetName | `[0x004f4120,0x004f41a3)` | `32e2883d2d54b3ee117b11753fef53973dac018b51f11c7debf597aa31830e71` |
| SetScript | `[0x004f4230,0x004f42f2)` | `0e1bc17c5a4823132172adba2e691c128845f90f3788d3009d6b9f52e497ec32` |
| Actor teleport | `[0x00401910,0x004019a1)` | `eeb8009bb817d8662f1dcc461cab29d3ee05b4df5e36c214bd270bc5315e0039` |
| MapWho Init | `[0x00492ba0,0x00492c58)` | `1f4a1f596520e4f7d5e42e5bac52cb848cde7c91a42e5a5bbf8450a5779ce7ec` |
| Ground collision wrapper | `[0x0047c8e0,0x0047c964)` | `555aa25b26f25bf13d9f563aa6362576330a6b077f0b152c6550b11429db0304` |
| Common collision wrapper | `[0x004f39c0,0x004f3a49)` | `9894aeccb95717d2ebf26951a4ec4bc370a5cebaa498da244405beec8494c9ad` |
| Persistent collision Init | `[0x004269b0,0x004269f6)` | `bd4cf3f803c5d5a661b2d81ef96d1c2753a6ba4be722a4d1c6673ea96dedddd4` |
| Render-chain instantiation | `[0x005164b0,0x00516578)` | `582ec79455f2915a91620f946c9f80e7267e1d46b8d10a5ee81653c4626dc29b` |

### Construction and proof limits

The complete direct Actor control flow is resolved; its transitive dynamic
effects are not all closed. A genuine World110 Init executor needs initialized
resource/profile state, mutable Init storage, concrete virtual dispatch,
MapWho/named/big/world collections, collision components and callbacks, and a
shared scheduler/RNG whose ordering includes earlier objects. The current
constructor-enriched actor registry and detached Start/engine/player shells
do not satisfy that boundary. In particular, script names as data, authored
poses and zero pending events must not be described as post-Init state.

A focused Core seam can expose only the first-move decision after that base
boundary: caller-owned shared RNG, resolved multiplier and post-base shutdown
flag produce the counter and optional existing-scheduler request. Do not draw
early, introduce a new random stream, move world publication after that draw,
or silently initialize all actors with the multiplier-1 path. Existing
`ThingActorBaseState` already owns contacts/poses/velocity; it has no
last-move-time or full-move-counter field and is not a full Init executor.

Cheapest static falsifiers are the three fully byte-compared bodies, selected
concrete table slots and constant loads (`0x005d8568 = 1.0f`,
`0x005d85bc = 4.0f`). Focused future Core tests should distinguish shutdown
from inactive, verify one draw for multiplier 1, all four multiplier-4
remainders, script/collision/MOVE request order, and ground-teleport versus
water-only old-pose changes. Runtime return continuity, constructor-global
seed/time, allocation/callback effects and final state still require a
controlled copied-runtime witness when the desktop is available. No such
runtime was run for this extension, and no C2/complete-RE grade changes.

## Retained trace and caller-family census

Historical recording identity (the raw recording was retired on September 5;
the retained extracts cannot replay it):
`G:\bea-ttd\level-opening-3m-v1-level100\level-opening-3m-v1-level100.run`,
6,199,181,312 bytes, SHA-256
`f3e677f7df5f5563ebb468f46ca6041756271f84dfc28ddf37b59210a4552b50`.
Its producer receipt binds the runtime image above.

A complete target-filtered replay produced 40 calls, 40 entries, and 40 raw
returns:

| caller site | current containing owner | calls | fallthrough |
| --- | --- | ---: | --- |
| `0x004f8b38` | `CUnit__Init [0x004f86d0,0x004f91f1]` | 34 | `0x004f8b3d` |
| `0x0044cb18` | `CFeature__Init [0x0044ca30,0x0044cbd6]` | 6 | `0x0044cb1d` |

These are two materially different caller families in one hash-bound world-load
trace. No `CRound__Init` caller was observed, so this result satisfies the
broader two-family falsifier but not its preferred CRound/CUnit pairing.

Selected envelopes:

| family | entry position | receiver | init pointer | raw return position/target |
| --- | --- | --- | --- | --- |
| `CUnit__Init` | `0x16A336:0x6D` | `0x08015610` | `0x08015890` | `0x16A3C0:0x8F` → `0x004f8b3d` |
| `CFeature__Init` | `0x16A67C:0x25` | `0x04989910` | `0x08016f50` | `0x16A691:0x8F` → `0x0044cb1d` |

At both calls, call-event `ECX` equals entry-event `ECX`; stack dword zero equals
the exact caller fallthrough and stack dword one is the listed init pointer. The
raw return is at `0x004013c2`, decodes `C2 04 00`, and targets that same
fallthrough.

**Limit:** all 40 invocations are `CALL_ENTRY`, not `CALL_ENTRY_RETURN`.
Every raw return follows a recorded nontrivial gap, so the collector reports
zero validated/gap-free returns and does not attach a return event to an
invocation. The table above is an ordered raw-return witness, not a gap-free
association.

## Watched direct writes

The two receiver plates watch 14 `CActor` dwords and one representative dword
from each inherited owner. Every row below is a same-boundary structural pair:
its Overwrite and Write callbacks share PC, position, thread, access address,
and a memory query whose source sequence equals the observation sequence.

| destination | direct writer(s) | bounded observation |
| --- | --- | --- |
| `this+0xcc/+0xd0/+0xd4` | `0x004011ed/11f3/11f9` | each selected lane stores bytes `0000C8C2` (`-100.0f` bits); before values differ by lane |
| `this+0xd8` | `0x00401204` | selected Unit `00000000→00000000`; selected Feature `F0FF9C04→00000000`; only exact bits are claimed |
| `this+0x7c/+0x80/+0x84/+0x88` | `0x00401217/121c/1222/1228` | four dwords written; Unit remains all zero, Feature overwrites four nonzero prior dwords with zero |
| `this+0x8c/+0x90/+0x94/+0x98` | `0x00401236/123b/1241/1247` | Unit direct post bytes `E5B28943 70DA7843 8F8B42BF 907D1A00`; Feature `00007743 00000A43 00000080 00000000` |
| first watched dword at `this+0x9c` | `0x0040133e` | both lanes write `0000803F`; the callback has `EAX=init`, destination `EDI=this+0x9c`, and count `ECX=12`, but only dword zero was watched |
| `this+0xdc` | `0x00401369/137b/1397` | selected lanes write three stages ending `00000001`: seed `0`, temporary `-1`, then `1` |

For all direct velocity/old-position writers, `EBX` equals the exact selected
receiver and `EAX` equals the exact entry init pointer. That register continuity,
the static init-source loads, and the exact destination pairs establish only the
watched transfer boundary. The selected Unit init-source plate separately watched
ten init position/orientation/velocity/type dwords and observed zero write
callbacks; it does not establish their endpoint values because of the readback
limit below.

## Inherited versus Actor-owned effects

The destination-owner boundary is explicit:

- `this+0x1c` is inherited `CThing::mPos`; `CThing__Init` writer
  `0x004f34d2` stores the watched dword in both lanes.
- `this+0x3c` is inherited `CComplexThing::mOrientation`; writer
  `0x004f40da` stores the watched dword in both lanes.
- Actor-owned storage begins at `this+0x7c`; the direct writers in the table
  above are inside `CActor__Init`.
- The selected Unit lane's inherited `CThing__Init` path invokes
  `CActor__CopyTransformAndNotify_00401910`; writers
  `0x0040194f/1954/195a/1960` re-write Actor-owned old-position dwords. This is
  a transitive base-initialization consequence, not a second direct
  `CActor__Init` copy. In the watched Unit lane, dword two changes
  `8F8B42BF→269919C1`; the other three transitive writes preserve their values.
  The selected Feature lane did not take that watched transitive path.

## Deterministic refuter

The ignored verifier pins the four raw JSONLs before parsing, rechecks the exact
caller/entry/raw-return shape, every writer/address/register relation, the
inherited/Actor destination partition, and the gap ledgers. Verifier SHA-256 is
`b9c1eb7d1c828789ae1aa6079d4b0bc9424999b8fe469dae89d79860f32eeae4`;
its result SHA-256 is
`077f51f252715541ab59ab3c5a2826d7c30aa2cf531410cef431611a80c3e40c`.

Four injected controls fail before a candidate verdict can be emitted:

1. wrong receiver → `unit receiver address differs`;
2. Unit data evaluated with the Feature init pointer → init continuity fails at
   `0x00401217`;
3. first Actor destination labeled inherited → boundary check fails;
4. first watched field address shifted by four → target-definition check fails.

## RED C2 disposition

This measurement does **not** advance the function to C2. Two independent
requirements remain missing:

1. **Validated return association.** All 40 returns cross replay gaps; the
   call-context output has 40 raw returns but zero validated/gap-free envelopes.
2. **Return-sequence readback.** Data-write callbacks produce exact
   before/after pairs, but the endpoint memory queries frequently report a
   source sequence different from the requested return sequence. The receiver
   plates therefore end `targetEvidence=fail`, `collectorChecks=fail`; only the
   same-boundary write pairs are consumed.

The following was the August 24 successor prescription, before retirement of
the raw recording. It documents the missing witness, but is no longer an
executable retained-trace route; new return evidence now needs a separately
controlled copied runtime when available.

Historical cheapest named successor: a versioned entity-scoped successor to
`tools/Invoke-TtdDataWrites.ps1` / `ttd_exec_coverage` that captures the selected
receiver bytes directly inside the matching raw-return callback, carries the
entry receiver/init/fallthrough into that callback, permits only ledgered gaps
with `continuity_break_crossed=false`, rejects nesting or a mismatched return
target, and runs exact plus swapped-init/wrong-field controls over this same
retained trace. No new native recording is justified until that retained-trace
instrument either succeeds or proves the required readback impossible.

## Evidence identities

- Call-context JSONL: 141,493 bytes, SHA-256
  `8d91a1104006459d652b31afb8b97255e80e6363024c11a29d31f72baf6b7786`.
- Unit receiver writes: SHA-256
  `a6705d97cfb9be297b7f98f03a71ed15b7053cd0f4793722c6ce49600ac89287`;
  24 structural pairs, 58 nontrivial gaps, 16 continuity breaks.
- Feature receiver writes: SHA-256
  `9449a3f484bc1faea6304149b36e1f0b5810d8bdcaa24ecaed1166887bd4addb`;
  18 structural pairs, 10 nontrivial gaps, 16 continuity breaks.
- Unit init-source zero-write control: SHA-256
  `9d1f7c59baedd7fd524b4d6ae53cb3704c1c33729de0239c220ac925d74aad39`.
- Call collector SHA-256
  `bd13563bafdefaa88cfa2b893c5920cb2a68276d4989b0c9b242cc84a668ef47`;
  data-write collector SHA-256
  `832e07e04b744ad55c00eda5b9b49240c5591a2576b4a4f792fb36f3e651038f`;
  data-write wrapper SHA-256
  `15181c819a0a61be73d91ace40f7c36860c51f4ea1606347f6c3e931200dffa4`.
- Generation-32 contract `C-eeae7f7364612d01`, question
  `Q-92f9d3b76cc0c226`, static receipt SHA-256
  `3e9031b3fe71928c866e986cc7625603d5d91dbcd75df9a1a324f0eb4f4b796c`.

No pristine executable, runtime target, trace, Ghidra project, save, shared
campaign ledger, grade count, or reconstruction owner was written.
