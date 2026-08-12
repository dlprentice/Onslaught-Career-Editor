# CBattleEngine__StartLock

> Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x00406fc0`
> Status: source identity promoted in Ghidra 2026-08-04
> Last updated: 2026-08-12
> The **filename** is retained at the withdrawn name so historical links and
> exports remain resolvable. A filename here is a research label, not a claim.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | 2026-07-28 intermediate label (historical) | Correction |
| --- | --- | --- | --- |
| `0x00406fc0` | `CBattleEngine__AddProjectile` | `CBattleEngine__AddTrackedActiveReader` | same class; suffix re-read |

## Source-identity promotion — 2026-08-04

The later backed-up, scratch-reproduced, independently refuted and separately
read-back target-lock promotion supersedes the July descriptive label with
`CBattleEngine__StartLock`, without changing this function's range. Its live
promotion READY is
`local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json`,
SHA-256
`77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945`.
This proves the bounded source-method identity and saved metadata, not all-path
runtime behavior or rebuild parity.

Three places carried the withdrawn label until 2026-07-28: the H1, the
`Saved Ghidra name` line below, and the function name inside the saved-signature
block. All three now read the current name. **Nothing else changed** — the
lock-entry interpretation, the argument shape, the boundaries and the contract
link were already written against the lock reading and are unaffected by the
rename.

### The rename and this note's source candidate do not conflict — and neither is settled

Recorded rather than smoothed over, because a reader could otherwise take the new
Ghidra label as having displaced the source candidate.

- **MEASURED (database):** the current 2026-08-12 export names `0x00406fc0`
  `CBattleEngine__StartLock`.
- **SOURCE:** `references/Onslaught/BattleEngine.h:142` declares
  `void CBattleEngine::StartLock(CUnit*, float, BOOL=FALSE)` and
  `references/Onslaught/BattleEngine.cpp:801` defines it. Its body, at
  `BattleEngine.cpp:806-824`, performs the five steps this note's
  "Current Static Interpretation" already lists, in the same order: reject a
  dying unit, scan `mLocks` for a duplicate, `new CLockInfo()`, store
  start/finish/direct-lock, `mLocks.Append(info)`. The declared argument list
  matches the saved signature below argument for argument. The Ghidra label
  describes the same act — the appended `CLockInfo` holds a reader set by
  `SetReader` — in different words.
- **MEASURED:** the later target-lock proof completed the bounded byte,
  call-graph, source, scratch, refuter, and promotion join for this identity.

---

## Status

- Saved Ghidra name: `CBattleEngine__StartLock` (after the intermediate July
  label `CBattleEngine__AddTrackedActiveReader`)
- Current static semantic role: lock-entry creation, not projectile spawning
- Source identity: `CBattleEngine::StartLock`
- Source identity status: bounded and promoted; complete runtime behavior remains open
- Runtime behavior proof: not established

## Saved Signature

```c
void __thiscall CBattleEngine__StartLock(
    void * this,
    void * target,
    float lockTime,
    int directLockFlag);
```

The parameter names above describe the current address-bound call shape. They
do not accept the stronger source method identity.

## Current Static Interpretation

The reviewed `CBattleEngine__HandleLocks` body calls `0x00406fc0` four times
with a candidate target, a lock-time value, and a direct-lock flag. The helper
then:

1. rejects a candidate carrying the checked inactive/dying-style flag;
2. scans the tracked set at BattleEngine `+0x294` to avoid duplicates;
3. allocates one `0x14`-byte entry when no duplicate exists;
4. stores current and finish-time values plus the direct-lock flag; and
5. appends the entry to the tracked set.

This structure aligns with pinned-source `CBattleEngine::StartLock`. The old
projectile interpretation resulted from the superseded
`CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` name at `0x00406560`.
Neither the caller nor this helper is current evidence of projectile emission.

## Contract

The bounded machine-readable contract is
[`battleengine-target-acquisition-static-contract-v1`](../../../game-mechanics/battleengine-target-acquisition-static-contract-v1.md).
It records `0x00406fc0` as a saved dependent name whose lock-entry role is
statically supported while the exact source name remains hypothesis-only.

## Boundaries

- No Ghidra rename or mutation is performed by this note.
- Exact `CLockInfo`, `CUnit`, BattleEngine, timestamp, flag, and set layouts are
  not established.
- The checked flag is not promoted to an exact retail field name.
- Lock timing, target choice, projectile emission, weapon firing, gameplay
  effects, and rebuild behavior remain unproven.
- No BEA launch, executable mutation, debugger action, or runtime observation
  occurred.
