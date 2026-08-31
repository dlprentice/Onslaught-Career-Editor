# World 110 authored player-start admission

Status: accepted authored-data admission, ordered list resolution, bounded
height clamp, and standalone player/engine assignment; runtime construction
remains open
Date: 2026-08-30
Verdict: world 110 contains one exact authored type-15 start for player 1. Core
admits its serialized pre-initialization fields, the complete ordered-match
selection law, the released no-match fallback plan, and the exact
terrain-height prefix of `CStart::Init`. A separate deterministic owner now
carries valid-object `CPlayer::AssignBattleEngine` order, but no path composes
the serialized start with a constructed `CStart`, Battle Engine, player, or
playable World-110 session.
Evidence: MEASURED — the exact record was reread from the hash-pinned retail
archive; the retained 66-level round-trip census independently corroborates the
type-15 tail grammar; pinned source owns the serialized fields and post-load
algorithm; pristine PC bytes fix the released list-walk, fallback behavior, and
37-byte height-clamp prefix, plus the exact 69-byte assignment order; the hash-
pinned HFLD fixes the exact World-110 sample and final Z.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
authored-record source `data/resources/110_res_PC.aya`, 1,294,300 bytes,
SHA-256 `4e041c758b9d41ba18311b1fadeacb95fc31af51320861480b97033bc24e3c2b`.

## Exact serialized record

The admitted archive inflates to 3,666,589 bytes. Its world-110 RLWD is 76,600
bytes and carries actor header `(2, 0, 40)`. All 40 initial-object records walk
to the expected tree header with this type census:

| Thing type | Rows |
| ---: | ---: |
| 8 | 10 |
| 15 | 1 |
| 18 | 19 |
| 19 | 1 |
| 27 | 3 |
| 28 | 5 |
| 36 | 1 |

RLWD ordinal 1 is the one type-15 row. Its exact admitted projection is:

| Field | Exact value |
| --- | --- |
| object identity | `wres:rlwd:0001` |
| serialized record | 59 bytes, SHA-256 `850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc` |
| position bits `(x, y, z)` | `(0x43846000, 0x43816800, 0x80000000)` |
| decoded `x, y` | `(264.75, 258.8125)` |
| orientation bits `(yaw, pitch, roll)` | `(0xbf04fd8b, 0x00000000, 0x00000000)` |
| plane mode | `0` |
| player number | `1` |

The raw IEEE-754 words are the authority. In particular, position Z is
authored negative zero; converting the row to ordinary decimal values before
admission would erase evidence. The complete 59-byte digest also binds the
common fields not projected individually by Core.

## Field ownership and corpus corroboration

Pinned `references/Onslaught/InitThing.h:112-130` names the common
`CInitThing` position, Euler-orientation, script/name, target, allegiance, and
active fields. Its version-greater-than-45 loader at lines 318-356 fixes their
serialized order for this version-50 world. `InitThing.h:791-830` then names
the derived `CStartInitThing` tail and loads `mPlaneMode` followed by
`mPlayerNumber`; its constructor defaults are plane mode false and player 1.

The retained external `local-lab/WORLD-DATA-2026-07-31.md` parser receipt
round-tripped all 115 BSWD/RLWD payloads byte-for-byte (7,664,606 bytes). Its
independent 66-level cross-check found 83 type-15 rows: one player-1 row in all
66 levels and exactly one player-2 row in each of worlds 850 through 866. That
corroborates the two-dword tail grammar without selecting world 110 specially;
the archive identity and exact 59-byte row above remain the world-110
measurement.

## Load and post-load ownership are separate

[`CGame__LoadLevel`](../binary-analysis/functions/game.cpp/CGame__LoadLevel.md)
loads the world and constructs fresh `CPlayer` and `CController` shells for the
attempt. It does not inspect the start list or assign a Battle Engine.

[`CGame__PostLoadProcess`](../binary-analysis/functions/game.cpp/CGame__PostLoadProcess.md)
owns that later step. Pinned `references/Onslaught/game.cpp:781-822` and the
pristine body at `0x0046d040` agree on this order for each player:

1. Walk the complete world-owned start list.
2. For every row whose player number matches, call `AssignBattleEngine` with
   that row's `GetPlayerObject()` result.
3. Continue walking after a match. Multiple matching rows therefore reassign
   in list order; the final matching row supplies the retained assignment.
4. Only when no row matched, create type 15 at `(256, 256, 0)`, copy the
   current player number, initialize it, and assign its player object.
5. Call `CPlayer::Init` after either path.

The byte discriminator is the unconditional list advance at
`0x0046d0e7` after the match arm's assignment at `0x0046d0dc`; the loop returns
to `0x0046d0c6` while another node exists. The found flag is tested only after
the list is exhausted at `0x0046d102`. The earlier statement that retail
stopped at the first match was false.

## Reconstruction admission

[`RetailWorldPlayerStartAdmission`](../../rebuild/OnslaughtRebuild.Core/RetailWorldPlayerStartAdmission.cs)
accepts only world 110, the exact archive identity, and the exact ordered start
record above. Object identity, type, length, record digest, all six raw float
words, plane mode, player number, count, and null shape fail closed.
Commit `4e3d472c` gives the real materializer the matching fail-closed
actor-header/census/tree-boundary and exact-start parser, so a supported retail
materialization verifies the same row before writing generated assets.
`RetailWorld110LevelActors.AuthoredPlayerStarts` keeps this row separate from
the 49 definition-bearing identities because a start is placement/lifecycle
input, not a Battle Engine definition.

The accepted projection is immutable and deterministic. Resolution now walks
the stored start rows completely, retains every match in order through
`MatchingAuthoredStarts`, and exposes the final matching row through
`AuthoredStart` and the effective projected fields. World 110's admitted data
still resolves player 1 to its one exact authored row. Unmatched player 2
returns an empty match list plus only the released pre-init fallback fields:
type 15, `(256, 256, 0)`, plane mode 0, and player number 2. Unsupported player
numbers are rejected. Rejected admission does not mutate the adjacent bounded
world-110 mission instrument.

## Bounded post-load list resolution

Commit `7491346f` carries only the deterministic selection part of
`CGame::PostLoadProcess`. The selected pristine byte range is
`[0x0046d0a9,0x0046d10a)`, 97 bytes, SHA-256
`6a3af1eb13df39a7fd5eeb2996f8ef26c09ad7b2f23988d8b0f4c93e9e35cb22`.
It contains the start/player number comparison, every-match assignment call,
unconditional list advance, and post-exhaustion found test; the surrounding
accepted function owns the unchanged fallback fields.

An internal synthetic projection distinguishes `[player1-first, player2,
player1-final]` without weakening public admission. Its result preserves both
matching rows in order, takes all effective serialized fields from the final
row, and cannot be changed by append or indexed replacement. This is a
serialized resolution transcript, not a transcript of runtime pointers or
completed player assignments. `GetPlayerObject` and composition with the
separate assignment owner remain outside this owner.

## Standalone `CPlayer::AssignBattleEngine` boundary

The pristine function is `[0x004d3080, 0x004d30c5)`, 69 bytes, SHA-256
`17f1f2e24aa271c93f1a223b7ad871f34487e91d4e1e640c37056cb112593a10`.
For valid objects it first rebinds the player's Battle Engine reader, then the
engine's player reader. If the complete player God dword is nonzero, it calls
the source-correlated vulnerability policy with raw `0`, then infinite energy
with raw `1`. There is no non-God reset arm.

[`RetailPlayerBattleEngineAssignment`](../../rebuild/OnslaughtRebuild.Core/RetailPlayerBattleEngineAssignment.cs)
composes those two calls over `RetailActiveReaderGraph` and returns a deeply
immutable outer call transcript. Empty generic-reader action lists do not erase
same-target function-call boundaries. Rebinding player P from engine A to B
does not clear A's reader back to P; displacing player P2 from B likewise does
not clear P2's reader forward to B. Those stale sides are released behavior,
not cleanup omissions in the deterministic owner.

The adapter supplies stable object/cell tokens and must pre-create both
distinct reader cells. Null graph, duplicate reader-cell roles, and missing
required cells are rejected before mutation; the adapter still guarantees that
the engine-side cell belongs to the supplied engine. This does not claim retail
rollback: the retail null-engine path can clear the player's old reader before
faulting, and configuration/allocator failures remain outside Core. The two
policy transcript entries are call intents, not executed Battle Engine scalar
state.

No World-110 owner currently supplies a constructed engine identity, its
player-reader cell, or the player's engine-reader cell. The assignment contract
therefore closes one reusable function boundary without closing
`CStart::SpawnBattleEngine`, `GetPlayerObject`, post-load integration, or P7.

## Bounded `CStart::Init` terrain clamp

[`CStart__Init`](../binary-analysis/functions/game.cpp/CStart__Init.md) bounds
the full pristine body but admits only the 37-byte half-open prefix
`[0x004eae27, 0x004eae4c)`, SHA-256
`f4efe7633c1f4ea75ca937ec0479eb1c72cd273812c15c31100991cd0844fe6a`.
Retail samples the heightfield once, compares that result strictly below
serialized Z, and only on that arm samples again and stores the second result.
The contract stops before the next-call setup at `0x004eae4c` and
`CComplexThing__Init` at `0x004eae4f`.

`RetailWorldPlayerStartHeightClamp` composes that prefix with an already
admitted resolution and only `Level100Terrain.World110`. For the exact authored
row, XY converts to 24.8 fixed `(67,776, 66,256)`. The pinned world-110 HFLD
returns `-10,485` units on both calls; scale bits `0x3a7003c0` produce final Z
bits `0xc1199926` (`-9.599889755249023`). This is strictly below authored
negative zero, so the second result is retained. The immutable result preserves
the serialized Z and authored orientation separately from that final value.

The released fallback position is also bounded through the same prefix. This
does not make either resolution a constructed runtime object: no base
initializer, Battle Engine, player assignment, session mutation, or Godot
owner is introduced.

## Measured mutation receipts

The independent row gate was exercised against canonical commit `4e3d472c` in
a disposable worktree. The controlled production mutation changed only
`RetailWorld110LevelActors.PlayerStartPlayerNumber` from `1` to `2`.
`RetailWorldPlayerStartAdmissionTests.Admit_ExactWorld110StartPreservesRawBitsAndDeterministicIdentity`
then failed with Expected 1 / Actual 2. After restoring the production owner,
the same exact filtered test passed; the receipt also binds the restored owner
and test SHA-256 values.

The receipt's logical machine-local path is
`local-lab/rebuild-world110-player-start-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`900f22187dea14262846d968a229e7a324ec1a292302c3214ddf656ec7e56b3d`.
On this workstation it resolves below `~/ProjectData/Onslaught/`. It is external
lab evidence, not content carried by a fresh clone. This mutation proves the
exact player-number assertion is live; it does not prove runtime construction.

The bounded clamp has a separate controlled production mutation at
`local-lab/rebuild-world110-player-start-height-clamp-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`9acb79d7a5e092725c1767358eb1d574853531b6caea0aa5ef30a752c6e03c40`.
Changing only `firstHeight < serializedZ` to `firstHeight >= serializedZ`
failed four of seven focused tests: the authored and fallback rows retained
their serialized Z, the distinct second-sample case did not clamp, and equality
incorrectly did. After byte-verified restoration, all seven tests passed. This
proves the strict branch is live; the internal distinct-result seam separately
proves two calls and storage of the second sample.

The ordered resolution has its own controlled first-match mutation at
`local-lab/rebuild-world110-player-start-postload-order-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`fce701a0ee95a2d91a351e8082076b70280b3c2abd95e41baad4e38738291c46`.
Adding one `break` after the first retained match reduced the ordered result
from two rows to one and failed the exact discriminator. After byte-verified
restoration, that fact passed 1/1 and the adjacent World-110/player-start gate
passed 44/44. Distinct first/final projected fields separately prevent a
first-row payload from passing through the final-row identity.

The standalone assignment owner has a separate reciprocal-call mutation at
`local-lab/rebuild-player-assign-battle-engine-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`63b97ad75ddb73a39c2f8a92a48c8471548c5c2fd93c1837e0788780aa9ca401`.
Omitting the second graph mutation while retaining its outer transcript label
failed the exact fresh-bind fact. After byte-for-byte production restoration,
the same fact passed 1/1 and the adjacent assignment/active-reader/start gate
passed 54/54. This makes the focused Core reciprocal mutation test-observable;
it does not prove runtime object construction or policy execution.

## Deliberate limits

This seam does **not** establish or implement:

- the remainder of `CStart::Init` from `0x004eae4c` onward, including
  `CComplexThing::Init`;
- `CStart::GetPlayerObject` or any Battle Engine allocation/initialization;
- `CGame::LoadLevel` player/controller construction;
- the runtime `GetPlayerObject` values, composition of repeated
  `CPlayer::AssignBattleEngine` calls with constructed engines, policy-method
  execution, or earlier-match lifetimes beyond the standalone stale-link law;
- `CPlayer::Init` or the post-load state-pair writes;
- a construction-ready world-110 actor definition set, actor registry,
  `InteractiveSession`, Godot lifecycle, or playable world 110.

The authored position and bounded final Z are therefore placement evidence,
not a claim that the rest of initialization leaves every coordinate,
orientation, object, or ownership field unchanged.

## Cheapest falsifier

Rerun the exact world-110 parser against the named archive and require the
archive size/hash, RLWD header/census/tree boundary, record count, 59-byte row
digest, and every raw field above. Any mismatch rejects the admission rather
than being normalized.

The pure-list gate can be rerun by changing the complete walk to stop at the
first match; the exact ordered-match test must fail. The assignment gate can
be rerun by omitting its second `SetReader` operation; the exact fresh-bind fact
must fail. The cheapest runtime successor is a copied-game probe that records
World 110's start list after the
admitted height prefix and after the rest of `CStart::Init`, the value returned
by `GetPlayerObject`, and every `AssignBattleEngine` call during
`CGame::PostLoadProcess`. A duplicate matching start in a controlled copied
profile would test the runtime pointer/side-effect half that the deterministic
Core transcript deliberately omits. The pristine specimen remains read-only.
