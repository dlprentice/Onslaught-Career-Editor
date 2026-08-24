# CMonitor__AddDeletionEvent

Status: active C1 contract; C2 runtime promotion RED
Last updated: 2026-08-24
Summary: specimen-bound static contract plus a retained-trace audit for `CMonitor__AddDeletionEvent` at `0x00401040`; two recordings cover the successful lazy-allocation body and common insertion/return bytes, but no retained target envelope exposes the receiver, reader cell, `monitor+0x04` transition, inserted payload, or return continuity required for C2.
Evidence: MEASURED — exact pristine body, current Generation-32 rows, two hash-bound execution-coverage products, and two hash-bound `CGenericActiveReader__SetReader` null-rebind control envelopes. No new replay, recording, native execution, or G: write was performed.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `Monitor.h` is absent from the pinned source drop; `activereader.h/.cpp` supplies architecture analogy only | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00401040`

## Promotion verdict

**RED — retain `C1_CANDIDATE_PARTIAL`; do not claim VERIFIED/C2.**

Generation 32 owns contract `C-72a0e9414f34c097`, question
`Q-cd61712a6052dfff`, semantic grade `C1_CANDIDATE_PARTIAL`, and campaign state
`OPEN_EXECUTED`. This file changes none of those canonical rows or any VERIFIED
count. The retained corpus proves that the successful lazy-allocation body and
the common insertion/return bytes executed in two recordings, but byte-union
coverage does not pair them to one invocation. It does not contain the
target-specific stateful call envelopes needed to establish the proposed
runtime contract.

## Five-wave reuse preflight

This preflight was completed and durably reported on task `t_e3fe26ad` before
any raw trace/debugger payload was opened. The counting unit is one unique
authority artifact, except Generation 32 where it is one target-specific row;
duplicate copies and search hits are excluded.

| Wave | REUSED | EXTENDED | NEW_MEASUREMENT | Exact authority |
| --- | ---: | ---: | ---: | --- |
| Tracked notes/contracts | 3 | 0 | 0 | `CMonitor.cpp.md` `72b257c8d648ea5608d10c8e30e368a75d7d76d62e961a2db59a1404985ea321`; `event-system.md` `5de00e66ea3c64f0e647bca35df004f2647151565fd394d162ac9362196b5b15`; `stuart-source-synthesis.md` `62c53e7e266b774c0d1ebe5c433203b9be08a972b911964ab3423fdbb86b417f` |
| Current Generation 32 target rows | 3 | 0 | 0 | `campaign-functions.tsv` `a63f42e331c265c94866ae944abc74e6a985dfb590f87419309c24932a951c63`; `campaign-contracts.tsv` `d4ddaa1054a4e27bfad0b4fbbbbdc817216c0329d580ae1419cdbcac5fa97409`; `campaign-questions.tsv` `0969bf5c5dcee73d9e046e37894db12f4becce65114d427de6329a0968a706ca` |
| Local-lab campaign reports | 4 | 0 | 0 | semantic shard report `712ea0715402f3e56ca9978aa9f0b75ad73d6b6ebd7fee53b6c1650f42f713bf`; primary report `bab5b7a599a2d3eed255da04bd4986502baccf54819aa7fdebcf2a640c94ebf3`; adversarial report `d2cdb6ce36df66cd8d1152c1d9df344014ce9fc658c44b72e4a2a107a62ce0ac`; CMonitor census `49e43479f4145746ce58633cec06c2e6f7d696247c3153805a741b28a321bf10` |
| G: routing inventories | 3 | 0 | 0 | `DRIVE-INVENTORY-2026-08-17.md` `3778443cecee5c342626edfe33262132a543be278acca2aa72ad6d3650df5fde`; `DRIVE-AUDIT-G-2026-08-17.md` `c43cdf1e16668a2d355cab02e20210716fe1d84bbd15a79b9c488a3537c4f458`; `g-drive-triage-2026-08-17.md` `c1c189f445fa7af7f443376c6a8600da35b5b2bcf14e815cc1a2c4a0fc8ee52d` |
| Retained TTD/CDB catalogs | 3 | 0 | 0 | TTD `REPORT.md` `9ff584135d237d56cee6d230d992d93520cfd577af7b944d47189a701f7559e1`; `sessions.tsv` `6ba813d8d1afb838e5a5bc1bc34a3eb22df5312a091357e72b033991c8b34a79`; `INDEX-CATALOG-2026-08-17.md` runtime/CDB route `8d50dc0d0fcfcae2fc1e64c77f20ee0c0bcc9be6cd4bb9f54065f2f543051040` |
| **Preflight total** | **16** | **0** | **0** | No new inventory, crosswalk, deep-mine, or output root. |

After that gate, four existing retained products were opened for a narrowly
targeted read (`NEW_MEASUREMENT 4`): two coverage JSONLs and two SetReader
call-context JSONLs. Thus this task's final disposition is `REUSED 16 /
EXTENDED 0 / NEW_MEASUREMENT 4`; none of the four measurements is a new replay
or capture.

## Identity and static contract

- Exact body: `[0x00401040,0x004010bd]`, one range, 126 bytes, 39 instructions,
  range-set SHA-256
  `209fb6083af63fd9265f4a1e90f21da8a2543c91539f98cdecc05f602c270606`.
- Raw body SHA-256:
  `b9d3c4afa0c93e5eccdcfbdfabc974da517d24c4172fde6f3a65628127701017`.
  The reviewed bundle disassembly is
  `139d20c0b80b2a80662fc31b3c9e77e98ebbbab2b7aa3aec48df62e895e068d4`.
- Prototype: `void __thiscall CMonitor__AddDeletionEvent(void * this, void * readerCell)`;
  `this` arrives in `ECX`, the one explicit argument is caller-stack dword
  `[entry ESP+4]`, and the body ends at `0x004010bb` with `RET 0x4`.
- Static null path: if `[this+4] == 0`, allocate `0x18` bytes through
  `CDXMemoryManager__Alloc` (`0x005490e0`; manager `0x009c3df0`, source-path
  string `Monitor.h`, line 94), call `CSPtrSet__Init` at `0x0040108a`, and
  store the resulting pointer to `[this+4]` at `0x00401093`.
- Static common path: load the argument at `0x0040109f`, load `[this+4]` at
  `0x004010a3`, and call `CSPtrSet__AddToHead` at `0x004010a7`.
  `AddToHead` stores the argument in the new wrapper's `+0` payload and links
  that wrapper as set head. This is exact static behavior, not a runtime
  identity/readback claim.
- Static allocation-failure path: `0x00401091 XOR ESI,ESI` reaches the same
  `[this+4]` store and common insertion call. Failure consequences inside
  `AddToHead` are not established here.
- Pinned-source analogy is deliberately weaker: the tracked synthesis says
  `CGenericActiveReader` removes the prior deletion event and adds one to the
  new monitor, while `ToReadDied()` describes pointer nulling. `Monitor.h` and
  the event-delivery implementation are absent, so source analogy cannot
  promote this retail function.

## Retained runtime evidence

### Two coverage recordings reach the successful lazy path

The following independent recordings are hash-bound to copied runtime
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`:

1. Level-512 opening trace, 6,031,409,152 bytes, SHA-256
   `3D3A118FE211EAD7B1E41055E4150DCFF576B6D0CC64879C52D1163BECA94808`.
   Recording receipt SHA-256
   `dec087c4445c67a1c83d94054329c6af3f07caff43696c8ff6775d9bcf19be23`;
   coverage JSONL SHA-256
   `e00382036da957b09007a3c5eba5e1b16c45c1e1aa2d09039453e859960099c8`.
2. Level-521 native take 4, 14,214,496,256 bytes, SHA-256
   `45AB04297F32BB27AC0C80E8ECB0B332E666A9955CAEA0763A83984AFFB74AC2`.
   Recording receipt SHA-256
   `c8e59da9db3f9fd4304d68dc667dc346e622d87c67fbff0fc17c4ec01fa86b98`;
   coverage JSONL SHA-256
   `26d0db3700590167abb26328520beecfdb145562fb9113bf46a48811d5b2ba66`.

Both coverage products contain exactly the same target ranges:
`[0x00401040,0x00401091)` and `[0x00401093,0x004010be)`, 81 + 43 = 124
executed bytes. Against the exact disassembly, that establishes execution in
each recording where the entry null check reaches the allocation body,
allocation returns non-null, `CSPtrSet__Init` executes, and the jump at
`0x0040108f` skips the failure XOR. It separately establishes execution of the
common insertion/return bytes. Byte-union coverage does not prove those bytes
belong to the same invocation. The only two body bytes not observed are
`[0x00401091,0x00401093)`, the allocation-failure `XOR ESI,ESI`.

Coverage is a byte-union, not a call envelope. It supplies no invocation count,
receiver, argument, branch association, before/after memory, inserted-node
payload, or return association. It cannot establish whether an initialized-set
invocation also occurred in either recording.

### Retained call-context controls do not target AddDeletionEvent

The retained call-context catalog reports 92 local-lab call-context products.
An exact target-row search for `entry_va:"0x401040"` finds zero; exact searches
also find no target row for `CMonitor__DeleteDeletionEvent @ 0x0042d9b0` or
`CSPtrSet__AddToHead @ 0x004e5a80`.

Two READY slices do target `CGenericActiveReader__SetReader @ 0x00401000` and
provide a useful can-fail control:

- Level 512: call-context SHA-256
  `6ae1206e2fd9c58b2178ed468e4366e8e5e57da2bb8e7400d0bd6a0e6b9b50d8`,
  receipt `c0968ff62894800623eddca81a1b3c6fd9bb27530ed59a4bac65a714fea4670c`.
  The one gap-free envelope calls from `0x004d8e2a`, enters with receiver
  `ECX=0x08228b38`, carries argument dword zero at `[ESP+4]`, and returns at
  `0x00401031` to `0x004d8e2f`.
- Level 521 take 4: call-context SHA-256
  `fd853be09bf7c8e1c5da358757d0484baaedf12bb635a4ff4abfef7a7bc0ec4e`,
  receipt `2c779a8431b255b657a345db7db6cc220836d82d8844b599602dd029a2631d17`.
  The one gap-free envelope has the same caller/return sites, receiver
  `ECX=0x07a0aa18`, and argument dword zero.

Those are two independent null-rebind envelopes. The static SetReader body
therefore skips its `AddDeletionEvent` call. The captures do not read the old
monitor/set or prove a successful removal, so they are a can-fail control for
registration only—not the requested DeleteDeletionEvent/removal readback.

## C2 falsifier matrix

| Required witness | Retained result | Disposition |
| --- | --- | --- |
| Two independent AddDeletionEvent call→entry→return envelopes | No target row in retained call-context products | **MISSING** |
| Exact `this` continuity through each target invocation | Coverage has no registers; SetReader receivers are not AddDeletionEvent envelopes | **MISSING** |
| Exact argument reader-cell identity | Coverage has no stack values; no AddDeletionEvent entry snapshot | **MISSING** |
| Null `monitor+0x04` before one call and non-null value after | Successful lazy route executes in two coverage products, but no pointed-memory readback exists | **MISSING** |
| Already-initialized insertion branch | Byte-union coverage cannot associate a later `JNZ` path with an invocation | **MISSING** |
| New set head payload equals the entry argument and survives through return | No `set+0`, `head+0`, or return-state readback | **MISSING** |
| Exact return identity at `0x004010bb` | No target return event | **MISSING** |
| Can-fail removal control using DeleteDeletionEvent or SetReader old-target removal | Two SetReader null-rebind envelopes exist, but neither captures old-set before/after state; DeleteDeletionEvent has no target row | **MISSING** |

Static source analogy, exact call sites, and the 124-byte runtime coverage remain
C1. They do not fill any missing stateful cell above.

## Cheapest sufficient instrument

Do not record or launch retail/native execution. Run one serialized, read-only
offline TTD replay plate over each already-pinned recording above, writing only
to an existing approved local-lab evidence owner. The plate must:

1. Target the exact AddDeletionEvent body and associate `call`, entry
   `0x00401040`, branch points `0x00401060`/`0x0040109f`, post-store
   `0x00401096`, post-insertion `0x004010ac`, and return `0x004010bb` per
   invocation.
2. At entry, snapshot `ECX`, `[ESP+4]`, and `[ECX+4]`. At post-store,
   post-insertion, and return, reuse the saved entry receiver and argument;
   snapshot `[receiver+4]`, `set+0` (head), `set+0x0c` (count), and `head+0`
   (payload).
3. Admit one envelope only when `[receiver+4]` is zero at entry, the lazy body
   executes, the post-store set is non-null, and the return head payload equals
   the exact entry argument. Admit the initialized envelope only when the entry
   set is already non-null, the lazy body is absent for that invocation, count
   advances consistently, and the return head payload equals the argument.
4. Target `CMonitor__DeleteDeletionEvent @ 0x0042d9b0` or the SetReader old-target
   remove site and capture the same set/head/count/payload fields before and
   after. A removal miss must remain observable as the can-fail arm.
5. Emit a deterministic verifier that rejects injected wrong receiver,
   wrong reader-cell/payload, and wrong return-PC mutations independently.
   It must also reject cross-invocation pairing, missing memory reads, and
   coverage-only substitution.

C2 becomes reviewable only if two independent trace receipts satisfy all of the
above and the two unique path scopes (lazy allocation and initialized insertion)
are both witnessed. If either recording lacks the initialized path, that is an
honest bounded corpus gap, not permission to infer it.

## Confidence and open boundary

Confidence remains **1 / C1**: exact identity, body bytes, ABI shape, static
allocation/insertion law, source analogy, and two successful-lazy coverage
routes are reconciled. Runtime receiver/cell continuity, concrete before/after
state, initialized insertion, removal behavior, allocation failure, duplicate
registration, whole-lifetime semantics, concurrency, and rebuild parity remain
open. The cheapest sufficient instrument above is the exact next step.
