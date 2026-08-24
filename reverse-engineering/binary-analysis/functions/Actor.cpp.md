# CActor__Init

> Address: `0x004011e0`

Status: active bounded static/runtime note — **RED for C2 promotion**
Last updated: 2026-08-24
Summary: exact retail `CActor__Init @ 0x004011e0` identity and two retained
caller-family write observations are reproduced, but every observed return
crosses a replay gap and the endpoint memory queries do not read back from the
requested return sequence. The Generation-32 grade therefore remains
`C1_CANDIDATE_PARTIAL` / `OPEN_EXECUTED`; this note makes no VERIFIED/C2 count
claim.
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

## Retained trace and caller-family census

Retained trace:
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

Cheapest named successor: a versioned entity-scoped successor to
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
