# CEventManager__AddEvent_AtTime

Status: active bounded contract — **C2 candidate; independent review required**
Last updated: 2026-08-24
Summary: specimen-bound static scheduler contract plus two retained Level-100
runtime queue envelopes. Two gap-free calls with distinct caller/payload
identities insert equal-time reused events into one priority-0 ring list in FIFO
order; a third gap-free call with a different requested time reaches a different
ring buffer. Generation 32 and shared counts remain unchanged pending review and
serialized integration.
Evidence: MEASURED — Generation-32 identity, pristine static body owners,
pinned source/body synthesis, retained TTD call/entry/return contexts, exact
queue/event write pairs, and injected wrong-payload/time/receiver/list controls.
Specimen: pristine `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/eventmanager.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044b370`

## Identity

- Body `[0x0044b370,0x0044b5b5)`, 581 bytes / 198 instructions; dated closure SHA-256 `038c8bd8c8886ccda9573fb3c7ea3b7bc2ef477c513c5c853ee8a9f5b1e56b48`.
  Generation-32 range-set SHA-256 is
  `2c53f758649589a9952f855029669e4a98538b69ef5a09afc317fe05d42465d2`;
  entity key is
  `CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:VA=0x0044b370:RANGES=2c53f758649589a9952f855029669e4a98538b69ef5a09afc317fe05d42465d2`.
- Generation-32 contract `C-9b3e8eb2538c212f`; question
  `Q-be6f270eb73c7034`. The frozen row is
  `C1_CANDIDATE_PARTIAL` / `CANDIDATE_NEEDS_REFUTER` / `OPEN_EXECUTED`.
  This file nominates bounded C2 evidence but does not mutate the frozen row.
- The retained runtime image's same 581-byte body hashes to
  `111aca6daabef73837e0740f27b1b15017c2778f67d8492337f23c564c7b4595`;
  that is a runtime-image pin, not a pristine-image equivalence claim.
- `RET 0x18` appears on each visible exit; the selected calls return through
  `0x0044b5b2` bytes `C2 18 00`. The exact trailing control
  `[0x0044b5b5,0x0044b5c0)` stayed unexecuted (`0/0/0`) in both full and
  selected replays.

## Calling convention

- `__thiscall`; manager receiver in `ECX`, followed by six explicit stack
  dwords. `RET 0x18` accounts for exactly those six dwords.
- All three selected contexts place manager `0x00672fc8` in `ECX` and preserve
  the stack return, event number, target/payload pointer, time-reference pointer,
  priority, data pointer, and reused-event pointer described below.

## Prototype and parameter semantics

```c
void __thiscall CEventManager__AddEvent_AtTime(
    void *this,
    int event_num,
    void *to_call,
    float *time,
    int start_or_end,
    void *data,
    void *re_use_event);
```

- `this` — event-manager receiver. The selected runtime value is
  `0x00672fc8`.
- `event_num` — only the low 16 bits are stored in the scheduled-event record.
  All selected/control rows use 3000; broader numeric semantics belong to each
  target class.
- `to_call` — required event target. Runtime paths A/B use `0x08090160` and
  `0x08015c60` respectively.
- `time` — readable pointer to the requested absolute-time float. Both equal-time
  paths point to stable `0xbf800000` (`-1.0f`) inputs; the different-time
  control carries `0x400338b3` (`2.050335645675659f`).
- `start_or_end` — ring priority index. The bounded paths use 0 only.
- `data` — optional event data target. The bounded paths use null only.
- `re_use_event` — optional existing 20-byte scheduled-event record. Paths A/B
  use `0x04094b4c` and `0x04094b74`; the different-time control uses
  `0x04094b38`. Allocation/free-list behavior is not part of this runtime
  proof.
- Nullability and invalid values beyond the statically visible guards are not
  generalized from these non-null selected inputs.

## Return value meaning

- Source and static signature are `void`; no scalar `EAX` contract is claimed.
- Paths A and B have validated gap-free returns at
  `0x17A1B5:0x24CB` → caller `0x0040477f` and
  `0x17A1B5:0x25C2` → caller `0x00401b46` respectively.
- The different-time control returns gap-free at `0x17A1B5:0x243E` →
  `0x004fef38`. No caller-visible status value is produced.

## Globals read/written

- The selected receiver is the global manager at `0x00672fc8`.
- Bounded manager fields observed directly are current time `+0x08`, current
  ring buffer `+0x10`, live event count `+0x18`, and the selected priority-0
  list header at `0x00673028`.
- Manager time stays `0x3d4ccccd` (`0.05f`) in both selected windows; current
  buffer stays 1. The live count advances `1713→1714→1715`.
- The manager `+0x20..+0x2f` block (events-processed, overflow cursor,
  free-list head, pool pointer on this mapped layout) is unchanged in both
  reused-event windows.
- A complete global read/write set, allocator/TLS/SEH state, and callback
  effects are outside this bounded runtime observation.

## Callees relied on / callers

- The exact static body directly reaches `CConsole__Printf @ 0x00441740`, the
  floor helper at `0x0055dfe7`, `CScheduledEvent__Set @ 0x004de1f0`,
  `CFlexArray__InsertAt @ 0x00424260`,
  `CGenericActiveReader__SetReader @ 0x00401000`, and the ring-list append
  helper at `0x004e5b20`.
- Selected path A is called at `0x0040477a` from
  `CAnimation__VFunc_0_00404750`; selected path B at `0x00401b41` from
  `CActor__HandleEvent`. These are distinct caller families and payloads.
- The different-time control is called at `0x004fef33` from
  `CUnitAI__VFunc_9_004fec60`.
- The full retained-trace target census records 12,973 call/entry pairs and raw
  returns; 11,325 returns are validated gap-free. That is a trace-bound census,
  not a whole-program caller census.

## Behavior summary

The exact static body and pinned source analog establish the broader branch
shape; the retained runtime proof consumes only the named arms:

1. reject an invalid manager or null `to_call`; reject requested times over
   1,000,000 on the later-time arm;
2. for a request at or before `mTime + 0.051f`, select the current ring buffer;
   if the request is negative, store `mTime + 0.0001f` as due time;
3. otherwise compute
   `floor((requested - mTime - 0.001f) * 20)`, then select a wrapped ring
   buffer unless the result reaches the overflow threshold;
4. reuse the supplied event record or pop/initialize a free record, store the
   low-word event number and due time, mark reuse, and conditionally set data;
5. append the record to the selected priority list and increment the live count.

For paths A/B, requested `-1.0f` plus manager time `0.05f` yields stored due
bits `0x3d4d35a9` (`0.05010000243782997f`) in both records. Both select current
buffer 1 / priority 0, whose 16-byte `GenericSPtrSet` header is
`0x00673028`.

### Selected queue envelopes

| path | call / entry / return | payload tuple | list before | list after / insertion |
| --- | --- | --- | --- | --- |
| A | `0x0040477a` / `0x17A1B5:0x2477` / `0x17A1B5:0x24CB` | event 3000, `to_call=0x08090160`, time `-1.0f`, priority 0, data null, reuse `0x04094b4c` | first `0x03f160d0`, last `0x03f184f8`, size 3 | first unchanged, last `0x03f18510`, size 4; node `0x03f18510` carries record A |
| B | `0x00401b41` / `0x17A1B5:0x256E` / `0x17A1B5:0x25C2` | event 3000, `to_call=0x08015c60`, time `-1.0f`, priority 0, data null, reuse `0x04094b74` | exact A final: first `0x03f160d0`, last `0x03f18510`, size 4 | first unchanged, last `0x03f18518`, size 5; node A next `0→0x03f18518`, so record B follows record A |

Every consumed list, live-count, input-time, manager-time, final event-record,
due-time, and node-link endpoint is a complete single-range observation with
matching source/observation sequence. All consumed write pairs share exact
Overwrite/Write boundary, PC, address, thread, and continuity epoch zero.
Envelope A contains 84 instructions, 12 write events / six pairs; envelope B
contains 84 instructions, 14 write events / seven pairs. Both have zero
nontrivial gaps and zero continuity breaks.

The B event record's *initial* 16-byte endpoint is split and sequence-invalid;
it is deliberately excluded. Its final record is complete and sequence-matched,
and its standalone due-time write, queue header, prior-node link, call tuple,
and return are valid. The proof therefore does not claim the B record's
pre-call contents.

### Different-time control

Invocation 1712 uses the same manager, event 3000, priority 0, and a distinct
reused record, but requests bits `0x400338b3` (`2.050335645675659f`). The
internal ring-join observation carries `EBX=40`, `ESI=0x00672fc8`, and
`EDI=0x04094b38`, selecting lane header `0x00673778`. The immediately following
A/B entries carry buffers `[1, 1]` and records
`[0x04094b4c, 0x04094b74]`. The passing narrow replay records exactly three
function entries/calls/returns, three ring-join entries, and zero padding hits.

## Error / edge behavior

- Static invalid-manager and free-pool exhaustion paths log and return; null
  target and time over 1,000,000 return without insertion. Negative requests
  normalize to `mTime + 0.0001f`.
- These runtime paths exercise valid manager, non-null targets, reuse records,
  priority 0, null data, current-ring insertion, and one later-time ring
  selection only.
- Allocation/free-list mutation, exhaustion, null/invalid targets, priorities
  1/2, nonnegative current-bucket requests, wraparound, overflow insertion,
  equal-time overflow ordering, callback execution, and concurrency are not
  established by the selected runtime arms.

## Runtime corroboration (TTD, bounded)

Trace: retained Level-100 opening, 6,199,181,312 bytes, SHA-256
`f3e677f7df5f5563ebb468f46ca6041756271f84dfc28ddf37b59210a4552b50`;
runtime image SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`.
The runtime image is pinned separately from the pristine static specimen.

Raw evidence SHA-256 pins:

- full call-context:
  `21be79e8eb954c805960f73b5bc7856443c589b4bf1ffb56b83718ac280434a7`;
- selected internal call/ring join:
  `256797a203816a8e82dc418a818e9e286e0a877a638b8f42d1db0af5fe451e43`;
- path-A queue/event writes:
  `8ed5cce0979476955b5ec72993fce1974ce9f8fffe2e07b2b15f252fc9af96f4`;
- path-B queue/event writes:
  `42139f887fd9722d9047366598d0003a50e6d54c376e39da6af9ee02c104fc40`.

The full/narrow call-context collector SHA-256 is
`bd13563bafdefaa88cfa2b893c5920cb2a68276d4989b0c9b242cc84a668ef47`;
the data-write collector is
`832e07e04b744ad55c00eda5b9b49240c5591a2576b4a4f792fb36f3e651038f`.
Both self-tests pass before use. TTD Replay/CPU hashes remain
`b705235016778648f2c194aa76b54669c19ae318d16d340019f8a6f6c86fabbc` /
`b2a9a06a3c292ef58df31df70ab35a9440dceb3ee36de9c2b08ff4507dd8ef93`.

## Evidence

- Generation-32 function/contract/question rows pin identity, body range,
  coverage, grade, and the open existing-trace falsifier.
- [`reverse-engineering/binary-analysis/event-manager-scheduler-semantics-2026-08-11.tsv`](../../binary-analysis/event-manager-scheduler-semantics-2026-08-11.tsv)
  pins the 581-byte / 198-instruction `SOURCE_BODY_DEMO_TWIN` mapping to
  `eventmanager.cpp:170`.
- [`reverse-engineering/binary-analysis/functions/CEventManager.cpp.md`](../../binary-analysis/functions/CEventManager.cpp.md)
  owns the broader function map, static failure/insertion laws, and this bounded
  runtime ledger summary.
- Pinned source hashes are eventmanager.cpp
  `613f4628471bbc3206f61dcfa9718dc6799f56e759fa7776a5fad204ba7af893`,
  eventmanager.h
  `57f39c8c9b3c413c16d0fc2b75237b1b045cd1754fd7245f871639b7518f5afc`,
  scheduledevent.h
  `1f568c7e1b71a4fbbf98e59a3c3ee55a71d60c0aa4313e1620426f3e52d0e4b1`,
  SPtrSet.cpp
  `49d40aa009dab4d0747560d30be27814fe6bc18a59b301860fa18a59a7644623`,
  and SPtrSet.h
  `2ab86140cd8df5ad035b297bbbab737e0c75fc5d88245873c8972b462e47d029`.
  Source names/layouts remain distinct from released-runtime proof.

## Can-fail verifier

Deterministic verifier SHA-256
`2fa0858488cb3c89bd95ff723709f1a1ad254bae9a237744e6a9260bd0d8e8f9`
pins all four raw inputs and checks the complete census, selected
call/entry/return tuples, manager receiver, request floats, internal ring
indices, event records, queue handoff, FIFO node link, due-time normalization,
live-count sequence, and every consumed write pair. Result SHA-256 is
`4f396d54169f191930b991cbabb5e3e7393ff17d783895c0882159373af7157b`.

Injected controls all fail as required:

- wrong A payload → `payload tuple differs for 1713`;
- different-time bits substituted for A → `requested time differs for 1713`;
- receiver shifted by four → `receiver differs for 1712`;
- selected list shifted by one priority-lane stride → `insertion list differs`.

The test was written first and failed with missing verifier module; after the
minimal verifier implementation it passes 1/1.

## C2 verdict: GREEN candidate

The selected evidence satisfies the bounded C2 falsifier:

- two independent caller/payload paths have exact manager, arguments,
  entry/return, reused record, queue before/after, insertion node, and live-count
  effects;
- equal requested times produce equal normalized due times in the same list,
  and the exact A-final/B-initial handoff plus prior-node update proves FIFO
  insertion order for those two records;
- a different requested time reaches a different measured buffer/list;
- wrong payload, time, receiver, and list expectations fail deterministically.

The candidate is bounded to these reused-event, priority-0 ring insertions. It
is not a universal scheduler, allocation, overflow, or callback contract.
Independent review is required before any integration owner promotes the
Generation-32 row or changes a VERIFIED/C2 count.

## Evidence boundary

This file and the paired function note are the only tracked writes. The lane
does not modify Generation 32, `EVIDENCE-REGISTER.tsv`, campaign TSVs,
`developer_state.json`, dashboards, Ghidra, executable bytes, traces, saves,
rebuild code, or shared counts. `G:\bea-ttd` was queried read-only; all generated
evidence lives in the dedicated worktree artifact bundle.

## Confidence

2 — exact static identity plus two gap-free queue/event/return envelopes and a
different-time ring control are measured. Confidence does not exceed 2 because
only reused-event, priority-0 ring arms are selected and the B record's initial
16-byte endpoint is intentionally excluded.

## Unresolved questions

- Fresh event allocation/free-list behavior and pool exhaustion.
- Null/invalid manager or target runtime effects beyond the static exits.
- Priorities 1/2, nonnegative current-bucket requests, wraparound, and
  overflow-list insertion/readback.
- Whether equal-time overflow events preserve the same order at runtime; only
  the selected ring-list FIFO law is promoted here.
- Data-bearing and non-reuse record ownership/lifetime.
- Callback dispatch effects, rescheduling interaction, concurrency, and full
  rebuild parity.
