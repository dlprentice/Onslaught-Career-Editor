# World 110 authored player-start admission

Status: accepted authored-data and bounded static construction contracts;
detached Start/engine/player shells implemented, complete initialization open
Last updated: 2026-09-06
Verdict: world 110 contains one exact authored type-15 start for player 1. Core
admits its serialized pre-initialization fields, the complete ordered-match
selection law, the released no-match fallback plan, and the exact
terrain-height prefix of `CStart::Init`. Separate deterministic owners carry
valid-object `CPlayer::AssignBattleEngine` order and invoke it once for every
ordered match over adapter-supplied, already-constructed engine/cell identities.
The production constructor now owns distinct Start, engine and player shells
and their reader storage, retaining supported initialization fields. It does
not complete their lifecycle, publish a world, or perform post-load assignment.
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

The retained ignored `local-lab/WORLD-DATA-2026-07-31.md` parser receipt
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
separate assignment owner remain outside this resolution owner; the bounded
sequence owner below consumes only caller-supplied identities.

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

No World-110 construction owner currently supplies a real engine identity, its
player-reader cell, or the player's engine-reader cell. The assignment contract
therefore closes one reusable function boundary without closing
`CStart::SpawnBattleEngine`, `GetPlayerObject`, live post-load integration, or
P7.

## Ordered authored-start assignment composition

[`RetailWorldPlayerAuthoredStartAssignmentSequence`](../../rebuild/OnslaughtRebuild.Core/RetailWorldPlayerAuthoredStartAssignmentSequence.cs)
joins `RetailWorldPlayerStartResolution.MatchingAuthoredStarts` to one
adapter-supplied binding per ordered match. Each binding names the matching
start identity, its already-constructed `GetPlayerObject` result, and that
engine's player-reader cell. The caller separately supplies the constructed
player identity, the player's engine-reader cell, and raw God word.

Before the first graph mutation, the owner snapshots the caller collection and
validates authored/final resolution consistency, exact count and ordinal start
identity, distinct player/engine reader roles, complete engine↔cell alias
consistency, every required cell, and each cell's current reverse membership.
A late invalid binding therefore cannot leave an earlier valid match half
applied. This is deterministic single-threaded preflight, not rollback against
concurrent mutation, resource exhaustion, invalid pointers, or arbitrary graph
corruption.

After preflight, every match invokes `RetailPlayerBattleEngineAssignment` in
list order. The player reader ends on the final match's engine; each earlier
engine reader remains aimed at the player, preserving the standalone stale-side
law. An exact repeated `(engine, cell)` tuple is permitted because current
evidence does not prove distinct `GetPlayerObject` values for duplicate matching
starts; the outer transcript still retains one assignment step per match even
when a nested same-target graph call has no actions. Nonzero God state emits the
two policy intents for every step.

The exact admitted World-110 player-1 resolution is exercised through
`wres:rlwd:0001`. Its adapter tokens are deterministic test identities, not a
claim that Core has constructed the retail objects. Synthetic two-match tests
are algorithmic discriminators for complete traversal and do not claim that the
shipped World-110 start list contains duplicate player-1 rows.

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
On this workstation it resides in canonical-checkout `local-lab/`. It is
ignored machine evidence, not content carried by a fresh clone or child
worktree. This mutation proves the
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

The ordered composition owner has a separate first-only/final-only receipt at
`local-lab/rebuild-world110-assignment-sequence-mutation-kill-20260831/RECEIPT.md`,
SHA-256
`bb600b6c439e24fc503a648c0203f8f6bf026a22d0d942d5cdadd922e1496c79`.
Stopping after ordinal zero and skipping every ordinal except the final one
each failed three ordered/per-match discriminators (8 passed / 3 failed).
Exact inverse-patch restoration returned the owner to SHA-256
`39aa59f8c87d62b23b5b4a86fcc3ade26af7ffcad5165b1d3c1a9b3ffde29118`
and the focused class to 11/11. This proves deterministic call composition and
ordering, not runtime object construction or virtual policy effects.

## Deliberate limits

The older admission, clamp and assignment helpers keep their original bounded
contracts. The detached construction owner below adds owned storage; neither
lane completes:

- Start's `CComplexThing::Init`/`CThing::Init` resource instantiation and world
  publication, including a proven class-15 resource-descriptor result;
- full Battle Engine constructor/Init dependencies, including Unit/base Init,
  parts, collision, resource objects, targeting and initial random events;
- the surrounding `CGame::LoadLevel` world/controller construction sequence;
- live post-load integration, God-policy execution, fallback Start execution,
  or earlier-match object lifetimes beyond the retained stale-link law;
- `CPlayer::Init` or the post-load state-pair writes;
- a complete World110 `Simulation`, `InteractiveSession`, Godot lifecycle or
  playable session.

The authored position and bounded final Z are therefore placement evidence,
not a claim that the rest of initialization leaves every coordinate,
orientation, object, or ownership field unchanged.

## Start, engine and player static construction boundary

On September 6 the named pristine specimen was hashed again, its PE section
mapping was decoded, and every selected instruction in the retained exports
was compared with the corresponding specimen bytes. Selected instruction
bytes matched with zero mismatches. Bounded GNU `objdump` disassembly was used
to independently read the Start suffix, spawn call/return boundary, player
constructor and relevant vtable targets. This is static evidence only; no
retail process, Ghidra project or desktop session was opened.

The retained exports are under
`local-lab/ghidra-fullpass-2026-07-23/exports/`. Paths in this table name
`decompile/` entries in their wave; `instructions.tsv` supplies the checked
instruction addresses and bytes. Export comments are fallible: in particular,
the old Start comment's “player-object globals” interpretation is incorrect.

| Owner/export | Half-open pristine range | Bytes | Raw SHA-256 |
| --- | --- | ---: | --- |
| W007 `004eacc0_CStart__Constructor.c` | `[0x004eacc0,0x004ead44)` | 132 | `e86928e2e14cf526b9ed2933e092f3ea68095930e9cdf0495fc4dcc0941f418e` |
| W007 `004eae10_CStart__Init.c` | `[0x004eae10,0x004eaf1a)` | 266 | `67ada0c7c363cd7f8ee3a059c198f568b687739f020a352b0ba6c2a37357934d` |
| Same Init, suffix after admitted sampler | `[0x004eae4c,0x004eaf1a)` | 206 | `1889a0910cbea5010703f7c6fefa1f00fc0128f7da9458be0d0d34a8a0edea44` |
| W007 `004eaf20_CStart__SpawnBattleEngine.c` | `[0x004eaf20,0x004eb12d)` | 525 | `b6bba0b576b156ae3e73ee11220eccb436b494002b746853bc1b9b0a0fe3f109` |
| W004 `0046d040_CGame__PostLoadProcess.c` | `[0x0046d040,0x0046d265)` | 549 | `0903b78f65a5e2807e9bee27ad83555063cc2dd62cbe49419193dae0d2ed1895` |
| W006 `004d2780_CPlayer__ctor.c` | `[0x004d2780,0x004d280f)` | 143 | `f35b657fe04e70f8f6459aba93d5437811748e0d29ca310975ebf8342238ed08` |
| W001 `00404dd0_CBattleEngine__Init.c` | `[0x00404dd0,0x004058fa)` | 2,858 | `44f563280d5c5748d2d09490113f4a5c27fa0d6c9e7d09a9abc8da0eece7dde0` |
| W001 `0040c650_CBattleEngine__UpdateConfiguration.c` | `[0x0040c650,0x0040c711)` | 193 | `c9b972544882212d5610222edf14c5b939cee9b1f24f98c46c03d025bc5a6cdd` |

The Start constructor calls the complex-thing base constructor, zeros its
engine reader at `+0x7c`, and constructs embedded init storage at `+0x84`.
It initializes the configuration and plane-mode words at `+0x444/+0x448` to
zero. These are init fields, not pointers to a player or engine.

The Init entry writes `-1` to the supplied init's `+0x70` and clears flag bit
2 at Start `+0x2c`. After the already-admitted height clamp it calls
`CComplexThing::Init` at `0x004eae4f`, then adds Start at the head of the global
start list at `0x004eae5a`. Its effective player number comes from init
`+0x3c0`; nonzero global `0x008a9bb4` swaps 1 and 2, leaving other values
unchanged. It copies clamped position, Euler words and allegiance into the
embedded engine initializer, then selects configuration ID `0x008a9bb8` for
effective player 1 or `0x008a9bbc` otherwise. These globals are
`CGame +0x11c/+0x120/+0x124`, corresponding to frontend settings in pinned
`references/Onslaught/game.h:63-73`. `CGame::CGame` at `0x0046c210` and
`game.cpp:216-224` initialize them to zero. That proves fresh-game defaults;
it does not prove the values after a frontend selection.

The engine initializer's configuration word is embedded `+0x3c0`, hence
Start `+0x444`. Its plane-mode word is embedded `+0x3c4`, hence Start
`+0x448`; Start copies this from authored Start init `+0x3bc`. The supported
XYZ/Euler projection does not assign meaning to the fourth FVector word or
otherwise pretend to reconstruct an entire native init buffer.

`SpawnBattleEngine(0)` calls the OID factory with type 3 at `0x004eaf43`,
publishes the returned engine through Start's reader at `0x004eaf51`, and only
then calls non-null engine Init with the embedded initializer at
`0x004eaf6a`. Its collision-template resets occur **after that call returns**,
at `0x004eaf77..0x004eafc5`. They must not be applied before initial engine
Init. The play-effect branch is skipped for this initial call. The factory
case is retained in W006 `004bf090_OID__CreateObject.c:28-66`; it allocates
`0x63c` bytes and zeros the engine's player reader at `+0x574`.

There are three separate reader cells:

| Cell | Initial target | Later operation |
| --- | --- | --- |
| Start `+0x7c` | null, then its allocated engine | SetReader before engine Init |
| Player `+0x1c` | null | PostLoadProcess → AssignBattleEngine |
| Engine `+0x574` | null | AssignBattleEngine → SetPlayer |

PostLoadProcess directly reads Start `+0x7c` at `0x0046d0d3`; the source's
`GetPlayerObject()` does not allocate another object there. The player ctor
stores its number, sets both view modes to 1, zeros seven stats and five kill
counts, and copies a complete God dword. The player-1 read at `0x004d27f3`
is runtime `0x00662ab4`, corresponding to the admitted career-container word
at `0x2496`; pinned `Player.cpp:24-34,247-265` supplies the source bridge.
This does not execute the later God-policy virtuals or `CPlayer::Init`'s
camera/host-time work.

## Configuration inputs and unfinished engine initialization

World110's exact RLWD name table contains **Aquila Prototype**. Its shared
BSWD contains Paladin Prototype, but that table is skipped: W008
`0050d4c0_CWorld__LoadWorldHeader.c` branches to configuration Load for the
non-base world and Skip for the base world. The byte-checked body is
`[0x0050d4c0,0x0050d577)`, 183 bytes, SHA-256
`a6518553f1f15ae04dff03db169812950b44704417dd7190c3dee3dec454eb16`.

The existing hash-gated `tools/battle_engine_config_decode.py` owns the
1,514-byte shipped configuration data, SHA-256
`58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a`.
The source loader and byte-checked retail loader at
`[0x0040f980,0x00410113)` read life/energy into configuration `+0x1c/+0x20`;
the 1,939-byte body hash is
`77e45d9fe461d98d44ad33d9bf3242e557b9fe42bf33cae8b761b35ee63d0742`.
The genuine Aquila record has life bits `0x41a00000` and energy bits
`0x41000000`. The existing Core configuration lookup owns the name-table
index clamp, case-sensitive search and fallback; no second selection law was
introduced for World110.

`UpdateConfiguration` writes life/energy and resets six stores. For each
store, overheat becomes zero, the raw heat word is copied, and current value
is capacity when the heat word is zero, otherwise zero. Engine Init repeats
those scalar/store writes, sets walker state 2 and shields equal to energy
for zero plane mode, or jet state 3 and zero shields otherwise. These are
supported initialization writes, not proof of final state after nested Init.

Review of the **complete** 2,858-byte engine Init and pinned
`references/Onslaught/BattleEngine.cpp:63-351` leaves these dependencies:

- walker/jet construction and weapon configuration; two render meshes, emitter
  enumeration and the LegMotion-dependent motion controller;
- `CUnit::Init` at call `0x004054c6`, base/AI/component construction, collision
  shape radius/height and world publication;
- cockpit and radar-warning receiver construction, equipment/readers and safe
  position/time state;
- the state-dependent part/mesh switch, Random call at `0x0040586e`, initial
  event `0x1772` scheduled at `0x004058b2`, and HandleAutoAim at `0x004058ba`.

Source-only defaults or top-level RNG counts do not discharge those nested
dependencies. Start's own base Init also calls resource-chain instantiation
for OID 15; its concrete descriptor result remains unadmitted. Consequently
the new constructor does not claim completed native Init, full call ordering,
post-load readiness or final engine position.

## Detached production construction and focused checks

[`RetailWorld110InitialConstruction.Create(career, settings)`](../../rebuild/OnslaughtRebuild.Core/RetailWorld110InitialConstruction.cs)
now owns a
[`RetailWorld110PlayerConstruction`](../../rebuild/OnslaughtRebuild.Core/RetailWorld110PlayerConstruction.cs).
The caller supplies validated career data and explicit frontend settings;
object and reader identities are allocated by the owner. Identities are local
Core tokens and make no claim about retail addresses or global thing-number
order. The Start reader targets its allocated engine; player/engine reciprocal
cells remain null. The supported Start/template and engine scalar/store fields
are constructed as a detached partial projection across unfinished Init
dependencies. Neither the Start template's post-Init reset nor post-load
assignment is exposed as completed work.

The production materializer emits the exact local
`level110-player-inputs.json` resource: 1,357 bytes, SHA-256
`3bcd5eac3bf17474f60e67d3f4aa135dd239de9a896d63f64f23c494fe339c7d`.
It carries World110's RLWD table and the admitted configuration fields from
the shipped data, with no restamped Level100 fixture or invented player row.

Focused checks live in
[`RetailWorld110PlayerConstructionTests.cs`](../../rebuild/OnslaughtRebuild.Core.Tests/RetailWorld110PlayerConstructionTests.cs)
and `World110InitialActorMaterializationTests` in
[`materialize_retail_assets_tests.py`](../../rebuild/tools/materialize_retail_assets_tests.py).
They distinguish all three reader cells, preserve raw God/settings words,
verify actual World110 configuration selection and stores, and assert that
post-load readers remain unassigned. They are deterministic construction
evidence, not retail runtime evidence.

## Cheapest falsifier

Rerun the exact world-110 parser against the named archive and require the
archive size/hash, RLWD header/census/tree boundary, record count, 59-byte row
digest, and every raw field above. Any mismatch rejects the admission rather
than being normalized.

The pure-list gate can be rerun by changing the complete walk to stop at the
first match; the exact ordered-match test must fail. The assignment gate can
be rerun by omitting its second `SetReader` operation; the exact fresh-bind fact
must fail. The composition gate can be rerun by processing only the first or
only the final binding; the ordered/per-match sequence facts must fail. The
cheapest runtime successor is a copied-game probe that records
World 110's start list after the
admitted height prefix and after the rest of `CStart::Init`, the value returned
by `GetPlayerObject`, and every `AssignBattleEngine` call during
`CGame::PostLoadProcess`. A duplicate matching start in a controlled copied
profile would test the runtime pointer/side-effect half that the deterministic
Core transcript deliberately omits. The pristine specimen remains read-only.
