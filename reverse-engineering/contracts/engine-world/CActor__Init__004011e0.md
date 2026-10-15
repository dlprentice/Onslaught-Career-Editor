# CActor__Init

Status: active bounded contract — **RED for C2 promotion; C1 retained**
Last updated: 2026-08-24
Summary: specimen-bound `CActor__Init @ 0x004011e0` static contract plus two
retained caller-family runtime write observations. Exact call/entry receiver and
init pointers, direct and inherited write pairs, and raw returns are measured;
validated return association and return-sequence readback are absent, so the
Generation-32 grade remains `C1_CANDIDATE_PARTIAL` / `OPEN_EXECUTED`.
Evidence: MEASURED — Generation-32 identity, pristine static body owners,
retained Level-100 TTD replay, same-boundary write pairs, gap ledgers, and
injected wrong-receiver/init/owner/field controls. SOURCE analog evidence is
kept separate.
Specimen: pristine `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/actor.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004011e0`

## Identity

- Body `[0x004011e0,0x004013c4]`, 485 bytes, 148 instructions; raw pristine-body SHA-256 `434f5fd6f9e3a04274452dbdbf4cc04f21bc514f25cdeab76e03eff3f6875ad4`.
- Generation-32 range-set SHA-256
  `0b1c5e7dedd1d8b4a059ac056bac6be6d0afe5436b615a80f4b5db7f921a6011`;
  entity key
  `CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:VA=0x004011e0:RANGES=0b1c5e7dedd1d8b4a059ac056bac6be6d0afe5436b615a80f4b5db7f921a6011`.
- Contract `C-eeae7f7364612d01`; question `Q-92f9d3b76cc0c226`.
- `RET 0x4` at `0x004013c2`; exact trailing
  `[0x004013c5,0x004013d0)` terminal-padding control stayed `0/0/0` at runtime.
- Current grade is unchanged: `C1_CANDIDATE_PARTIAL`, contract state
  `CANDIDATE_NEEDS_REFUTER`, execution state `OPEN_EXECUTED`. This card changes
  no campaign TSV, register, count, or current-authority pointer.

## Calling convention

- `__thiscall`; the exact body receives `this` in `ECX` and ends in `RET 0x4`,
  accounting for one explicit stack dword. The two selected runtime observations
  reproduce that receiver/argument placement.
- Additional register or stack parameters are not_determinable from the promoted
  evidence and are not claimed.

## Prototype and parameter semantics

```c
void __thiscall CActor__Init(void *this, void *init)
```

- `this`: exact entry receiver in `ECX` for the two selected observations.
- `init`: exact entry stack dword one. The runtime writer events preserve its
  value in `EAX` across the watched direct velocity/old-position/orientation
  writes.
- Nullability, aliasing, concrete dynamic types, invalid orientation modes,
  allocator failure, scheduler failure, and zero/negative move multipliers are
  unresolved.

## Return value meaning

- The signature declares `void`; no scalar `EAX` return contract is claimed.
- Caller-visible post-return state is not_determinable: the retained trace has
  raw returns but zero validated gap-free invocation returns and no accepted
  return-sequence receiver readback.

## Globals read/written

- Exact global storage identities and a complete global read/write set are
  not_determinable from the promoted evidence.
- The bounded static body reads the event-clock value and visible shutdown gate
  used by the sequence below. Global effects inside the random/event callees are
  not promoted here.

## Callees relied on / callers

- Static direct callees are `CComplexThing__Init @ 0x004f3fd0`,
  `Random__NextLCGAbs @ 0x004de8d0`, and
  `CEventManager__AddEvent_AtTime @ 0x0044b370`; the first reaches inherited
  `CThing__Init @ 0x004f34a0`.
- The complete target-filtered retained-trace census observes 34 calls from
  `CUnit__Init @ 0x004f8b38` and six from
  `CFeature__Init @ 0x0044cb18`. Broader caller populations are unknown.

## Behavior summary

The exact retail body, bounded static predecessor, and source analog agree on
this visible order without making a whole-source equivalence claim:

1. store `-100.0f` bits to Actor-owned `this+0xcc/+0xd0/+0xd4`;
2. store the observed event-clock value to `this+0xd8`;
3. transfer four watched velocity dwords to `this+0x7c..+0x88`;
4. transfer four watched old-position dwords to `this+0x8c..+0x98`;
5. build or copy old orientation and copy 12 dwords to
   `this+0x9c..+0xcb`;
6. call `CComplexThing__Init @ 0x004f3fd0`, which reaches inherited
   `CThing__Init @ 0x004f34a0`;
7. obtain the virtual move multiplier, call
   `Random__NextLCGAbs @ 0x004de8d0`, seed/update `this+0xdc`, and call
   `CEventManager__AddEvent_AtTime @ 0x0044b370` unless the visible shutdown
   gate suppresses scheduling.

Pinned `actor.cpp:15-40` is source analog evidence for names/order only.
`actor.cpp` SHA-256 is
`72ff886915a2cb7ef82e5992538214027f5d13a45be804606e7031ba9ecb9d82`;
`actor.h` is
`0af427656cfb9dbbc1afb9a207d0ac6c1deea944e44b05019bfad30315e3f2cf`.
The exact inherited/Actor destination boundary comes from
[`../../binary-analysis/cthing-ccomplexthing-layout-2026-08-13.md`](../../binary-analysis/cthing-ccomplexthing-layout-2026-08-13.md):
`CComplexThing` ends and `CActor` begins at `this+0x7c`.

## Error / edge behavior

- The visible shutdown gate suppresses event scheduling on its guarded path.
- Null/aliased pointers, invalid orientation modes, allocator or scheduler
  failure, and zero/negative move multipliers have no accepted bounded witness;
  their behavior is unknown rather than inferred from the source analog.
- No caller-visible error code is claimed for this `void` contract.

## Runtime corroboration (TTD, bounded)

Trace: retained Level-100 opening, 6,199,181,312 bytes, SHA-256
`f3e677f7df5f5563ebb468f46ca6041756271f84dfc28ddf37b59210a4552b50`;
runtime image SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`.

Complete target census: 40 call/entry pairs and 40 raw returns, partitioned
exactly as `CUnit__Init` caller `0x004f8b38` ×34 and `CFeature__Init` caller
`0x0044cb18` ×6.

| selected family | call/entry | receiver | init | raw return/target |
| --- | --- | --- | --- | --- |
| `CUnit__Init` | `0x004f8b38` / `0x16A336:0x6D` | `0x08015610` | `0x08015890` | `0x16A3C0:0x8F` / `0x004f8b3d` |
| `CFeature__Init` | `0x0044cb18` / `0x16A67C:0x25` | `0x04989910` | `0x08016f50` | `0x16A691:0x8F` / `0x0044cb1d` |

In both rows, call/entry `ECX`, stack return, and init-pointer extraction agree;
the raw return is `0x004013c2` bytes `C2 04 00` and targets the exact caller
fallthrough. Both returns cross nontrivial replay gaps and are therefore raw,
not validated invocation returns.

### Watched Actor-owned writes

The two selected receiver plates produce 24 structural pairs (Unit) and 18
(Feature). Every consumed pair has matching Overwrite/Write boundary, thread,
PC, address, and observation-sequence memory source.

| field boundary | exact direct writer PCs | selected results |
| --- | --- | --- |
| contact timestamps `+0xcc/+0xd0/+0xd4` | `0x004011ed/11f3/11f9` | both lanes write `0000C8C2` to each dword |
| last-move time `+0xd8` | `0x00401204` | Unit `00000000→00000000`; Feature `F0FF9C04→00000000` |
| velocity `+0x7c..+0x88` | `0x00401217/121c/1222/1228` | Unit four zero writes; Feature four nonzero-to-zero writes |
| old position `+0x8c..+0x98` | `0x00401236/123b/1241/1247` | Unit post `E5B28943 70DA7843 8F8B42BF 907D1A00`; Feature post `00007743 00000A43 00000080 00000000` |
| watched old-orientation dword zero `+0x9c` | `0x0040133e` | both lanes write `0000803F`; only dword zero is claimed |
| full-move count `+0xdc` | `0x00401369/137b/1397` | three observed stages end at `00000001` in both lanes |

The direct velocity/old-position callbacks carry `EBX=this` and `EAX=init`.
The orientation-copy callback carries `EAX=init`, `EDI=this+0x9c`, `ECX=12`.
This is exact runtime register continuity for the watched stores, not proof of
unwatched input fields or complete source semantics.

### Inherited/transitive partition

- Inherited `CThing` destination `this+0x1c`: writer `0x004f34d2` in both
  lanes; selected Unit `00000000→E5B28943`, Feature
  `50FA9C04→00007743`.
- Inherited `CComplexThing` destination `this+0x3c`: writer
  `0x004f40da`; watched dword remains `0000803F` in both lanes.
- Selected Unit only: the inherited base-init path invokes
  `CActor__CopyTransformAndNotify_00401910`, whose
  `0x0040194f/1954/195a/1960` writers re-write Actor-owned old-position
  dwords. Dword two changes `8F8B42BF→269919C1`; this is explicitly transitive,
  not a direct `CActor__Init` transfer.
- Unit init-source zero-write control: ten selected init
  position/orientation/velocity/type dwords produced zero write callbacks in
  the exact selected window.

The exhaustive per-pair ledger, not repeated here, is summarized in
[`../../binary-analysis/functions/Actor.cpp.md`](../../binary-analysis/functions/Actor.cpp.md).

## Evidence

- The exact static range, instruction count, and raw pristine-body digest are
  independently carried by
  `reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv`.
- The detailed runtime ledger, caller census, write-pair matrix, controls, and
  missing-witness boundary are retained in
  `reverse-engineering/binary-analysis/functions/Actor.cpp.md`; the owner split
  is supported by
  `reverse-engineering/binary-analysis/cthing-ccomplexthing-layout-2026-08-13.md`.
- Source analog inputs are `references/Onslaught/actor.cpp` and
  `references/Onslaught/actor.h`; their hashes are pinned above and remain
  separate from retail/runtime proof.
- The trace, runtime image, verifier result, and four raw-input SHA-256 pins in
  this contract bind the ignored retained evidence without turning it into a
  tracked payload or a canonical-grade change.

## Can-fail verifier

Deterministic verifier SHA-256
`b9c1eb7d1c828789ae1aa6079d4b0bc9424999b8fe469dae89d79860f32eeae4`
pins the raw evidence and checks the call/entry/raw-return shape, every consumed
write pair, owner boundary, receiver, init continuity, and gap ledger. Result
SHA-256:
`077f51f252715541ab59ab3c5a2826d7c30aa2cf531410cef431611a80c3e40c`.

Injected controls all fail as required:

- wrong receiver → address mismatch;
- Unit write stream with Feature init pointer → fails at `0x00401217`;
- first Actor field relabeled inherited → `this+0x7c` boundary failure;
- first target shifted by four → target-definition failure.

Raw input SHA-256 pins:

- call-context `8d91a1104006459d652b31afb8b97255e80e6363024c11a29d31f72baf6b7786`;
- Unit receiver writes `a6705d97cfb9be297b7f98f03a71ed15b7053cd0f4793722c6ce49600ac89287`;
- Feature receiver writes `9449a3f484bc1faea6304149b36e1f0b5810d8bdcaa24ecaed1166887bd4addb`;
- Unit init-source zero-write control `9d1f7c59baedd7fd524b4d6ae53cb3704c1c33729de0239c220ac925d74aad39`.

## C2 verdict: RED

No C2 promotion is made. The exact blockers are:

1. all 40 observed returns are separated from entry by replay gaps, yielding
   zero `CALL_ENTRY_RETURN` / gap-free envelopes;
2. endpoint receiver/init memory queries do not consistently report
   `source_sequence_matches_observation=true` at the requested return, so both
   receiver plates end `targetEvidence=fail`, `collectorChecks=fail` despite
   complete, untruncated replay and valid same-boundary write pairs.

The existing trace therefore proves bounded writes but not a receiver
write/readback envelope attached to a validated return. `void` ABI, complete
write set, invalid input behavior, scheduler outcome, allocation/lifetime,
post-return state, and broader caller populations remain open.

Cheapest falsifier/instrument: a versioned entity-scoped successor to
`tools/Invoke-TtdDataWrites.ps1` / `ttd_exec_coverage` that records watched
receiver bytes inside the matching raw-return callback, carries the exact entry
receiver/init/fallthrough into that callback, accepts only ledgered gaps with no
continuity break, rejects nesting or mismatched return targets, and runs exact
plus swapped-init/wrong-field expectations over this same retained trace. Do
not record a new native trace unless that retained-trace successor fails for a
named technical reason.

## Evidence boundary

This file advances documentation and a RED falsifier only. It does not modify
Generation 32, `EVIDENCE-REGISTER.tsv`, Ghidra, pristine/runtime binaries,
traces, saves, rebuild code, canonical grades, or VERIFIED/C2 counts.
Independent review is required before any later integration owner changes the
canonical campaign state.

## Confidence

2 - Exact static identity and the two bounded caller-family write observations
are measured and independently reviewed, while validated invocation returns,
return-sequence readback, complete semantics, and C2 promotion remain absent.

## Unresolved questions

- All 40 observed returns remain separated from entry by replay gaps, so the
  validated gap-free return count is zero.
- Both receiver plates still fail the return-endpoint sequence match; accepted
  post-return receiver/init readback is absent.
- Complete unwatched inputs/writes, invalid-input and failure behavior,
  allocation/lifetime, scheduler outcome, post-return state, and broader caller
  populations remain unknown.
- The cheapest falsifier remains the retained-trace return-callback readback
  successor described in the RED verdict; no new native trace is warranted
  unless that instrument fails for a named technical reason.
