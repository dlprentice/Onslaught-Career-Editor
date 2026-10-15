# CPlayer__AssignBattleEngine

> Address: `0x004d3080`
>
> Source: `references/Onslaught/Player.cpp` / `references/Onslaught/Player.h`
>
> Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
> `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave472)
- **Verified vs Source:** Partial static source bridge plus bounded deterministic
  rebuild mapping; runtime player/BattleEngine behavior remains deferred

## Signature
```c
void __thiscall CPlayer__AssignBattleEngine(void * this, void * battle_engine);
```

## Exact boundary and released order

The pristine PC body is the 69-byte, 26-instruction half-open range
`[0x004d3080, 0x004d30c5)`, raw SHA-256
`17f1f2e24aa271c93f1a223b7ad871f34487e91d4e1e640c37056cb112593a10`.
It ends with `RET 0x4` at `0x004d30c2..0x004d30c4`; eleven NOP bytes separate
it from the next saved body at `0x004d30d0`.

For a valid concrete player and Battle Engine, the released order is:

1. Call `CGenericActiveReader__SetReader` on the player cell at `this +0x1c`
   with the one stack argument.
2. Reload that engine from the player reader, then call `SetReader` on the
   engine-side player cell at `battle_engine +0x574` with `this`.
3. Test the complete dword at player `+0x20`. Zero returns without a policy
   reset arm.
4. On any nonzero value, dispatch primary-vtable `+0xe0` with raw argument
   `0`, then `+0x154` with raw argument `1`.

Pinned `Player.cpp:254-266` names these operations `mBattleEngine.SetReader`,
`SetPlayer`, `SetVulnerable(FALSE)`, and `SetInfinateEnergy(TRUE)`. Four direct
callers remain: two in `CGame__PostLoadProcess` and two in
`CGame__RespawnPlayer`.

The shared reader body `[0x00401000, 0x00401034)` is 52 bytes, SHA-256
`5540848cb8c7cd9fd46fc6a2d068b76527166c61510dd33c36b2c4dc1e41dca2`.
It makes same-target calls no-ops; otherwise it detaches the old reverse
membership, publishes the new target, then attaches the new reverse
membership. This function does not clear the old engine's player reader or a
displaced player's engine reader. Reassignment can therefore leave both stale
reciprocal sides intact.

For the concrete primary `CBattleEngine` vtable, `+0xe0` resolves to
`0x00405e30` and stores raw zero at engine `+0x15c`. `+0x154` resolves to
`0x00405f20`, stores raw one at `+0x160`, then copies configuration `+0x20`
bits to engine `+0xfc`. These are static downstream effects, not a claim that
Core executes either virtual method.

## Failure boundary

There is no null guard. A null argument can first detach/publish null in the
player reader and then fault through the derived `0x574` receiver. A nonzero
God path can likewise complete both reader calls and earlier stores before a
null configuration dereference in the infinite-energy virtual. Retail has no
rollback. Allocator failure, malformed reader sets, pointer faults, and exact
runtime lifetime remain outside the current deterministic model.

## Rebuild mapping

[`RetailPlayerBattleEngineAssignment`](../../../../rebuild/OnslaughtRebuild.Core/RetailPlayerBattleEngineAssignment.cs)
composes the already accepted `RetailActiveReaderGraph` twice in the released
order. Its immutable outer transcript retains both reader-call boundaries even
when either nested action list is empty. Any nonzero raw God word then emits
the two policy-call intents with exact arguments `0` and `1`.

Both distinct reader-cell tokens must already exist. Preflight rejects only a
missing required cell or duplicate cell role before the host graph changes; it
is not a claim that retail is atomic or rolls pointer faults back. Integer
identities are adapter tokens, not retail addresses, and the adapter still must
prove that the supplied engine-side cell belongs to the supplied engine.

The owner intentionally does not execute the virtual policies, materialize
engine scalar state, allocate an object, derive a token from `+0x1c`/`+0x574`,
clear stale links, or connect serialized World-110 start identities to runtime
objects. `CStart::Init`, `CStart::SpawnBattleEngine`, `CBattleEngine::Init`,
`CPlayer::Init`, session wiring, and Godot ownership remain open.

## Measured reconstruction falsifier

In a disposable worktree, the production-only mutation omitted the second
engine-player `SetReader` call while retaining its outer transcript label. The
exact fresh-bind fact failed because the expected publish/attach actions were
empty. The owner was restored to SHA-256
`f8df01f2ad11d72061359487f625f0aeb68a6e34e291c0c59fb78c7e300cebce`;
the identical fact then passed 1/1 and the adjacent assignment/reader/start
gate passed 54/54.

The machine-local receipt is
`local-lab/rebuild-player-assign-battle-engine-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`63b97ad75ddb73a39c2f8a92a48c8471548c5c2fd93c1837e0788780aa9ca401`.
It proves the focused reconstruction discriminator, not a retail runtime-grade
promotion.

## Notes
- Wave472 removed the stale extra `param_2` from the saved Ghidra signature and replaced open-signature wording with stack-cleanup/caller evidence.
- The bounded Core owner adds deterministic function-order parity while leaving
  runtime pointer/fault/lifetime parity, object construction, BEA launch, game
  patching, and World-110 integration deferred.

## Related
- [CPlayer View Helpers](CPlayer__ViewHelpers.md)
- [CPlayer Snapshot Helpers](CPlayer__SnapshotHelpers.md)
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md)
- [CMonitor and active-reader lifecycle](../CMonitor.cpp.md)
