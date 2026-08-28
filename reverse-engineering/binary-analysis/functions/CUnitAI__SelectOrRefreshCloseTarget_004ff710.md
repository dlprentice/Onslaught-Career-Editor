# CUnitAI__SelectOrRefreshCloseTarget_004ff710

> Address: `0x004ff710`

Status: active multi-build static contract plus replicated bounded-runtime note
Last updated: 2026-08-28
Source File: none — no current source-crosswalk row | Binary: pristine
`BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: exact PC transaction/scoring law, corresponding PC-demo/Xbox/PS2
virtual-suite bodies, and replicated Level-521 call-context behavior. The
function ran 86 times on 50 receivers; 41 gap-free returns were heap-shaped
pointers, and every call was nested in
`CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` on the same receiver.
Evidence: MEASURED — independently decoded pristine instructions and console
bodies establish static branch/order correspondence; two serialized read-only
replays over the retained Level-521 take2 trace establish only the bounded
runtime call/return envelope.

## Static identity and ABI

- Canonical contract:
  [`../../contracts/unitai/CUnitAI__SelectOrRefreshCloseTarget_004ff710__004ff710.md`](../../contracts/unitai/CUnitAI__SelectOrRefreshCloseTarget_004ff710__004ff710.md).
- Body `[0x004ff710,0x004ffb57]`, 1,096 bytes; pristine-body SHA-256
  `e4f2106e542daa0af8b3f92409641169e35f6c7a573c73956693545756703d05`.
- ABI: `void * __thiscall (void * this)`. The static body has a bare `RET`;
  runtime carries the receiver in `ECX` and the return bits in `EAX`. The
  pointer is intentionally untyped; no concrete unit/reader class is inferred.
- Runtime caller site is uniquely `0x004ff702`, eight bytes before the recorded
  end of `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`.

## Exact transaction and scoring law

The receiver's `this+0x0C` cell is a deletion-aware active-reader reference.
The exact 52-byte `CGenericActiveReader::SetReader` body
`[0x00401000,0x00401034)` (SHA-256
`5540848cb8c7cd9fd46fc6a2d068b76527166c61510dd33c36b2c4dc1e41dca2`)
does same-target return, unlink-old, store-new, then register-new, matching
`references/Onslaught/activereader.cpp:8-21`. `this+0x10` is the distinct
runtime caller-supplied retained-target gate; its only proved nonzero producer
is the hierarchy-propagation path, which supplies literal `1`. `this+0x14` is a
construction-fixed fast-reuse gate: base initialization writes `1`, five PC
construction paths overwrite it with `0`, and no accepted post-construction
writer exists. It is not a mutable refresh latch. `this+0x18/+0x1C` receive two
raw helper results. B at `+0x1C` is behaviorally the ballistic-reach/line-
clearance prerequisite; A at `+0x18` is the final aim-angle/obstruction fire
acceptance. Those are bounded descriptions rather than recovered member/method
names; their stores and B-before-A order are instruction-proven.

Fast reuse requires a non-null current target, target virtual `+0x16C == 0.0`,
non-zero `this+0x14`, and a non-zero active/state helper. It preserves the
reader and `this+0x10`, performs support selection, stores helper B to `+0x1C`,
then either stores helper A to `+0x18` or explicitly zeros `+0x18` when B is
zero. Target slot `+0x16C` is source-backed `GetStealth()`. PC retail/demo test
only x87 status bit C3, so unordered/NaN passes this one gate alongside positive
and negative zero; Xbox's parity test and PS2's `c.eq.s` reject NaN and accept
only ordered zero.

Full refresh pre-clears `+0x18` then `+0x1C`, chooses the side-keyed list, and
walks it in retained order. A candidate must pass the active/state, side, and
linked-support gates, then this strict range test:

`distanceSquared < (((1 - candidatePercent * 0.01) * config[0x158]) ^ 2)`.

The seven profile cells are the exact array written by serialized
`CUnitAttackPriority` index `0..6`; defaults initialize all seven to `1.0f`.
Deterministic primary scoring is first-match in this exact flag order:

| Candidate bit | Exact shipped category | Priority index / cell |
| ---: | --- | ---: |
| `0x00020000` | `THING_TYPE_VEHICLE` | `1 / config[0x168]` |
| `0x00004000` | `THING_TYPE_INFANTRY` | `4 / config[0x174]` |
| `0x00000400` | `THING_TYPE_AIR_UNIT` | `5 / config[0x178]` |
| `0x00040000` | `THING_TYPE_EMPLACEMENT` | `0 / config[0x164]` |
| `0x00000100` | `THING_TYPE_BUILDING` | `2 / config[0x16C]` |
| `0x00008000` | `THING_TYPE_NAVAL` | `3 / config[0x170]` |

Candidate virtual-table displacement `+0x164` is slot 89, source-backed as
`CUnit::IsAThreat()`: the `CBattleEngine` primary vtable at `0x005D89C4`
points that slot to literal-true body `0x004014A0`, exactly matching
`BattleEngine.h:250`, while the `CUnit` primary vtable points it to
`0x004FD440`. Owner config `+0x138` is the normalized field written by shipped
property `CUnitIgnoreThreats` at `0x00432E50`; it is not a second candidate
field. When `IsAThreat()` is false and `CUnitIgnoreThreats` is zero, primary is
positive zero and the floor is skipped, but the candidate continues into the
ordinary primary/secondary comparison. Otherwise flag `0x00080000`
independently raises the selected primary to index-6 `config[0x17C]`
(`THING_TYPE_COMPONENT`) when it is lower.

`CUnitIndiscriminate` owns `config+0x128`; its serialized scalar is normalized
to zero/one. When nonzero, each candidate that already passed all three helper
gates and the strict range test consumes one shared gameplay-stream draw and
uses `(Random__NextLCGAbs() % 65536) / 8192` as primary. This arm bypasses the
`IsAThreat()` call and `CUnitIgnoreThreats` read, the category ladder, **and the
component floor** before joining the primary comparison. The PC retail/demo,
paired Xbox, and three PS2 bodies all carry that bypass and conversion. Their RNG bodies
also share multiplier `48271`, unusual modulus `214783647`, 32-bit wrapped
arithmetic, level-start seed `123456`, and the sign-normalized return; therefore
the remainder is always `0..65535`, including the `INT_MIN` corner mapping to
zero. The exact score domain is `[0, 65535/8192]`. The load-bearing bypass
edges are PC retail `0x004FF8F9→0x004FF9DD`, PC demo
`0x004FF9A9→0x004FFA8D`, Xbox USA/Issue 11
`0x00187AAE→0x00187B93` / `0x00187B1E→0x00187C03`, and PS2
demo/Europe/USA `0x002BFAA0→0x002BFBA0` /
`0x002BFB60→0x002BFC60` / `0x002C02C8→0x002C03C8` (with the
sample multiply in each MIPS delay slot).

Primary best starts at `-999999`; lower skips, greater resets secondary best to
zero, and equality enters the same secondary contest. Secondary starts at
`1000 - sqrt(distanceSquared)`, adds `1000000` inside the inclusive support
minimum/maximum band, or `10000` above the maximum after reaching the minimum.
Only a strictly greater secondary replaces the winner; equality preserves list
order. A greater-primary candidate whose secondary is non-positive can leave
the previous lower-primary pointer intact because retail does not clear that
local when it resets secondary.

A winner is committed with lifecycle-aware `SetReader`, followed by one support
update, a `this+0x10=0` write, a second support update on the now-current reader,
the active/state check, B-to-`+0x1C`, and conditional A-to-`+0x18`. The common
exit writes `+0x10=0` again. If the post-commit state or B check fails, the new
reader remains bound and the pre-cleared result cells remain zero; there is no
rollback. No winner still calls `SetReader(null)` before clearing `+0x10`.
`RetailUnitAITargetTransaction` carries this ordered plan into Core without
claiming monitor mutation or support/helper side effects.

## Cross-build correspondence

The PC demo bodies at `0x004FF5A0/0x004FF7C0` reproduce retail PC's transaction.
Xbox USA `0x00188A20/0x001878A0` and Issue 11
`0x00188A90/0x00187910` normalize identically within each virtual slot. PS2
demo `0x002BF548/0x002BF818`, Europe `0x002BF608/0x002BF8D8`, and USA
`0x002BFD70/0x002C0040` normalize identically within each slot; raw MIPS branch
inspection reproduces the same ladder, strict range, deterministic floor,
indiscriminate-floor bypass, draw conversion, and tie law. This closes
family-level branch correspondence and the per-draw integer law, not scenario
stream phase, period/frequency, or every floating-point knife edge.

## Replicated bounded-runtime contract

Scenario: retained `level521-native-20260802-0018-take2` combat trace,
full native replay window. Trace SHA-256
`F7A8F93F7E499C4C92E6CC8FF5C301BDBBF1A70C80B64185E7A71A9D3A59FD5C`;
runtime specimen SHA-256
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`.

- Corrected replay target 0: 86 calls / 86 entries / 41 raw returns; 41
  validated gap-free return envelopes; every exact-count expectation passed.
- All 86 calls occur inside an open ff4f0 invocation with equal `ECX`; the
  measured stack-depth delta is exactly 52 bytes on all 86.
- Receiver containment is `|r(ff710)|=50`, `|r(ff4f0)|=76`, and
  `r(ff710) ⊆ r(ff4f0)` with intersection size 50.
- All 41 validated return values are outside the module image and above the
  small-integer band: seven non-null heap-shaped values. This establishes a
  raw pointer-shaped return domain in this trace, not pointed-to RTTI or
  ownership.
- The positive rival `CWarspite__SetReaderAndRefreshSupportSelection` ran
  73/73/73 times only from the two formation-builder sites; its receiver set is
  disjoint from ff710. The exact dark `CWaypoint__RandomizeOffsetVectors` body
  stayed 0/0/0. Both preregistered controls survived.
- After excluding metadata and target rows, which encode the corrected table,
  all event/invocation rows for targets 0..2 match run-a byte-for-byte; both
  normalized streams SHA-256 to
  `AD623E03146985419C58F13B3364C1C12457034EFD53B2912B74AA7DAC0CDB0F`.

## Receipts and limits

- Corrected capture SHA-256
  `84DB81290B00CE15FBCEB579FD8BC8B4C793C3F947001544FA44918F4189D171`;
  wrapper receipt
  `A3D9E421EB12526405DF718C9142CE5BBE0AB829CAE6C9D614242BCE0138A96D`;
  manifest
  `9C3757B2670A67035FB25A093A8E36CFA0AA18BD44517E904BA410C1DA45999F`.
- Independent adjudication output SHA-256
  `2C4B7987EC08FBBFCC063C793196BD66BBF5093480B7D54899883F36AD6FF6A7`;
  promotion manifest:
  [`../unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv`](../unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv).
- The original run-a control design failed and remains preserved as a RED
  plate. Promotion rests on the later preregistered corrected replay, not on a
  post-hoc reinterpretation of that first control.
- The take2 recorder receipt is RECONSTRUCTED/PARTIAL: the trace bytes are
  hash-bound after lock release, but capture-time target hash was not
  independently bound. All claims here inherit that provenance limit and are
  bounded to this copied-runtime trace.
- No value watchpoint was collected. Exact per-invocation before/after dwords,
  pointed-to RTTI, helper side effects, scenario-specific shared-stream phase,
  RNG period/frequency, scoring-rounding knife edges, and other-level population
  remain open. The fast-reuse zero/NaN platform distinction is closed statically.
- `RetailUnitAITargetSelection` carries the finite-domain deterministic and
  indiscriminate transcript reducer into Core. `RetailUnitAITargetTransaction`
  consumes its optional winner and emits the exact ordered retained-refresh,
  fast-reuse, or full-selection plan. Both remain unwired from actor state;
  autonomous population, monitor execution, and helper side effects remain open.

## Cheapest falsifier

For the runtime envelope, replay the same corrected table and pinned v2
collector; any count/control/caller/receiver/hash mismatch falsifies that
bounded claim. For the static law, re-decode the exact bodies: a changed flag
order, non-strict range or secondary replacement, floor before the raw score
gate, random arm that reaches the component floor, different draw conversion
or `1000/10000/1000000` branch, or console body that does not carry the same
control-flow shape falsifies the promoted static contract.
