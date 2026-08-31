# World 110 serialized initial-object seed admission

Status: accepted authored-data admission; runtime construction remains open
Date: 2026-08-30
Verdict: Core admits all 40 exact World-110 RLWD initial-object rows as one
immutable ordered seed projection with closed type-specific tails. These are
serialized constructor inputs, not 40 actors, a registry, or a session.
Evidence: MEASURED serialized data plus SOURCE-INFORMED field semantics — the
hash-pinned retail archive and RLWD reproduce every offset, record digest, raw
word, common field, and tail; pinned `InitThing` source names the version-50
field order and derived records. No runtime construction was observed.
Specimen: `data/resources/110_res_PC.aya`, 1,294,300 bytes, SHA-256
`4e041c758b9d41ba18311b1fadeacb95fc31af51320861480b97033bc24e3c2b`;
RLWD 76,600 bytes, SHA-256
`fb56249deac8faf0033f4d4b67688ff72e12d922291c880d75b10599fc739837`.

## Exact serialized envelope

The version-50 preamble is words `(3, 41, 110)`, one name `Aquila Prototype`,
trailing words `(0, 0, 0, 0, 1)`, and the 13 independently hash-pinned compiled
scripts. The initial-object header starts at RLWD offset 15,709 and is
`(2, 0, 40)`. Its first record starts at 15,719; the rows occupy exactly 2,608
bytes through offset 18,327. The following six bytes are the tree-group header
`(uint16 0, int32 2)`, independently closing the table boundary.

| Thing type | Rows | Closed retained tail |
| ---: | ---: | --- |
| 8 | 10 | `string8 definition; int32 trailer`, exact trailer `-1` |
| 15 | 1 | `int32 planeMode; int32 playerNumber` |
| 18 | 19 | explicit waypoint tail with no fields |
| 19 | 1 | amount, three raw delay words, squad size, unit, distinct spawner spawn script |
| 27 | 3 | explicit script-carrier tail with no fields |
| 28 | 5 | amount, mode, definition, exact trailer `-1` |
| 36 | 1 | raw finite radius word |

Every common and tail float remains its raw IEEE-754 word. All float words are
finite, and the serialized `active` and `attachScriptsToUnits` dwords are
required to be exactly zero or one. Object identity is derived only from exact
serialized order as `wres:rlwd:NNNN`; record offsets must remain contiguous,
and every record length and SHA-256 is retained.

## Load-bearing rows

The type-15 row is ordinal 1, 59 bytes, SHA-256
`850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc`.
Its position words are `(0x43846000, 0x43816800, 0x80000000)`, so authored Z
remains negative zero. Its orientation is `(0xbf04fd8b, 0, 0)`, plane mode is
zero, and player number is one. The new projection converts this row losslessly
to the separately accepted player-start owner; it does not replace that owner.

The five type-28 rows are ordinals `(14, 16, 17, 18, 19)`. Their amounts are
`(5, 5, 3, 5, 4)`, their modes are all zero, and the amount sum is 22. They
remain five squad seeds. The amount is multiplicity input, not a proved set of
22 member poses, actor identities, or publication order.

The sole type-19 row is ordinal 5 and is serialized inactive. Its amount is
three; delay and squad-delay bits are both `0x40a00000`; initial delay is zero;
squad size is one; and the unit is `Muspell Fighter`. Its common
`spawnScript` is `MuspellFighter2`, while its type-specific
`spawnerSpawnScript` is empty. Those fields are distinct. Cold seed admission
does not create the three configured fighters.

The sole type-36 radius word is `0x42480000` (50.0). It is retained as a raw
word, not interpreted as a collision volume or converted coordinate.

## Materializer and Core boundary

[`materialize_retail_assets.py`](../../rebuild/tools/materialize_retail_assets.py)
now retains all seven tail cases during its one table walk. A supported retail
materialization writes deterministic compact JSON to the ignored local path
`rebuild/OnslaughtRebuild.Core/Assets/Level110/level110-initial-object-seeds.json`.
The schema is `onslaught.world110-initial-object-seeds.v1`; the exact 21,651
output bytes have SHA-256
`51e51f5e1d3f7bce52ce99297711b1f299494271af3129828959e726aed04e5a`.
The payload remains user-local retail-derived evidence and is neither tracked
nor distributed.

[`RetailWorldInitialObjectSeedAdmission`](../../rebuild/OnslaughtRebuild.Core/RetailWorldInitialObjectSeedAdmission.cs)
loads only that embedded local payload. It verifies the output hash before JSON
interpretation, rejects unknown, duplicate, missing, null, reordered, or
unsupported shapes, validates the exact envelope and census, snapshots every
row, and exposes read-only typed views over the same row instances. There is no
public arbitrary-world or caller-supplied-row admission.

The 16 definition-bearing RLWD seeds join exactly to the existing RLWD subset
of `RetailWorld110LevelActors.AuthoredDefinitions`. Its 33 shared-BSWD
definitions remain separately owned and are not fabricated as rows in this
RLWD projection. Existing player-start, height-clamp, script/HFLD admission,
bounded session, and World-100 canonical-hash outputs remain unchanged.

## Falsifier and hard ceiling

A controlled production mutation swapped the decoded type-28 amount and mode.
The exact squad fact failed with expected amounts `(5, 5, 3, 5, 4)` and actual
`(0, 0, 0, 0, 0)`. Byte-for-byte restoration returned the same fact and the
adjacent 66-test World-110/start/height/session/hash gate to green.
The ignored machine-local receipt is
`local-lab/rebuild-world110-all40-initial-object-seed-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`fe300ff9fdfc13522922bdd81e860ecece1e54b521f719aeafec535d1b82e382`.

This admission does not establish coordinate conversion, physics or runtime
class enrichment, mesh/life/contact state, squad-member formation or poses,
spawner initialization, path construction, script startup, `CStart::Init`, a
Battle Engine or player, actor IDs, registry/world-list publication, nested
construction failure policy, state hashing, `Simulation`, `InteractiveSession`,
Godot ownership, or campaign 100-to-110 play. P7 remains open.
