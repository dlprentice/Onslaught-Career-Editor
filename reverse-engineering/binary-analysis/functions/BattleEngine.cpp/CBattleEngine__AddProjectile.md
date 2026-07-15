# CBattleEngine__AddProjectile

> Address: `0x00406fc0` | Source family: `references/Onslaught/BattleEngine.cpp`
> The filename and saved Ghidra symbol are retained so historical links and
> exports remain resolvable.

## Status

- Saved Ghidra name: `CBattleEngine__AddProjectile`
- Current static semantic role: lock-entry creation, not projectile spawning
- Source candidate: `CBattleEngine::StartLock`
- Source candidate status: `hypothesis-only`; no reviewed retail rename was applied
- Runtime behavior proof: not established

## Saved Signature

```c
void __thiscall CBattleEngine__AddProjectile(
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
