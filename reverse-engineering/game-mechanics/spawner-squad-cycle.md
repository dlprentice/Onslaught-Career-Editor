# Released spawner squad-cycle contract

Status: accepted static contract with a deterministic reconstruction boundary;
authored runtime reach remains open
Date: 2026-08-28
Verdict: `CSpawnerThng__DoSpawn` admits one squad-production cycle, not one
unit. A passing call can publish an empty squad, consumes its finite amount
slot even if squad allocation returns null, starts the first member wave
synchronously, and retries failed member waves through event 3000 until enough
members succeed.
Evidence: MEASURED — exact PC retail body hashes and instruction order were
reread from the pristine PE; Xbox mapped-body hashes were independently
reproduced; pinned source supplies named structures; and the PC demo, Xbox, and
PS2 closure was independently reconstructed before Core translation.
Specimen: PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
Xbox USA/Issue11 mapped images SHA-256
`665d34c581633e3cdc4c71b9a07dd9567e8e00703fe9f408a3c7930bbaab6a4d` /
`0f751ef1ef63e730716d2b2ab2a15176b385f56765d99efb5ed1c0985c738e43`.

## Exact PC closure

| Routine | Half-open range | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `CSpawnerThng__DoSpawn` | `[0x004E3C60,0x004E3F8B)` | 811 | `a21eb3fd7aad249edaca00b3dad1f9b42af222e5cb7b16251118130eb12316cc` |
| member wave | `[0x004E3F90,0x004E43BB)` | 1,067 | `b2783b8993c6fae83fc3989f3e2d581d29568d23013f9485d3e206b46885f4d7` |
| completion predicate | `[0x004E4430,0x004E4457)` | 39 | `6924a4d78a479ff95d511319fc08ec58f73ada86fe9096830bed31a12783a30c` |
| event-3000 callback | `[0x004E4460,0x004E4474)` | 20 | `05d36a344cd4c2a325aaf5c4ca474ff4f9c1d7bddb280df80e11b826f17452be` |

The pinned Stuart `InitThing.h` has SHA-256
`5a7132f3d0fe5f95a8696675c99ef19fa6ddcc941d9065c7efd3018beab82fef`.
Lines 410-425 name `CSpawnerInitThing`'s amount, squad size, member delay,
initial delay, squad delay, unit name, and spawn script. Lines 623-635 define
`CSquadInitThing`'s derived defaults as amount zero, empty unit name, and mode
zero. Retail writes those three defaults before squad initialization. Source
supplies these names and defaults; released field offsets and ordering below
come from the shipped bodies.

## Admission and synchronous start

PC retail admits a cycle only when all six conditions pass, in this order:

1. the spawner is enabled;
2. no member wave is already busy;
3. current time is strictly greater than the next-cycle time (equality and
   unordered/NaN fail);
4. finite amount is not exhausted, or infinite mode is enabled;
5. the spawned type has resolved and is not `-1`;
6. the released config pointer is non-null.

After admission, retail builds a temporary zero-member squad initializer,
resolves the authored transform and definition, requests a squad, and assigns
the returned reader. A non-null squad is flagged as building and initialized.
That initializer tail-publishes the still-empty squad into the world's ordered
squad set before the spawner commits any cycle fields.

Whether the squad result is non-null or null, retail then resets the successful
member count, sets busy, increments the admitted-cycle count once, and invokes
the first member wave synchronously. `DoSpawn` returns true after that wave
returns. Therefore true means that the cycle passed admission and began; it
does not prove that a squad or member exists. The amount slot is never rolled
back by a later allocation, initialization, clearance, or member failure.

A missing authored unit definition is not a clean rejection: PC reaches a null
definition and dereferences its type field. It remains an invariant/fault path,
not a false `DoSpawn` result.

## Member waves and completion

An event callback after busy has cleared is inert. While busy, each wave
resolves the current transform and clearance, then requests a member. Failed
clearance or a null member result leaves the ordinal, successful-member count,
squad reader, build flag, and busy latch unchanged and schedules event 3000 at
`now + CSpawnerDelay`.

On member success retail performs these observable phases:

1. increment the next transform ordinal;
2. initialize the member;
3. apply its seek/cooldown state;
4. attach it when a squad reader exists;
5. increment the successful-member count;
6. schedule another event-3000 wave when the count remains below squad size;
7. otherwise clear the squad build flag when present, release the squad reader,
   clear busy, and write `nextCycleTime = now + CSpawnerSquadDelay`.

Because the size comparison follows the increment, zero or negative squad size
still requires one successful member before completion. A null squad does not
block member construction, counting, or normal completion; its members remain
unattached through this path. Disabling a busy spawner blocks later admission
but does not cancel the current wave because the wave never rereads enabled.
A permanently failing member attempt can therefore retain busy and retry
without a proved ceiling.

## Released-family corroboration

The independently reconstructed PC demo has the same 811-byte start and
1,067-byte member-wave sizes. Xbox USA and Issue11 use the same transaction in
616-byte starts and 824-byte waves; their independently rehashed mapped bodies
are:

| Build/routine | Range | SHA-256 |
| --- | ---: | --- |
| Xbox USA start | `[0x000CE470,0x000CE6D8)` | `9a82f7c1b4c6167dbc46bb9c47022728974563f49452d71ab63f8d65e42abfde` |
| Xbox USA wave | `[0x000CE120,0x000CE458)` | `5dd472acc09fb41ffeb5cc12a149348187c43e738e43bfd5c622e7243fcbfe9f` |
| Xbox Issue11 start | `[0x000CE480,0x000CE6E8)` | `a6e3afecc7cc2c0a4aede0a9920a264c0b671b05f69dd95e588d508e497525e7` |
| Xbox Issue11 wave | `[0x000CE130,0x000CE468)` | `c2bbaa0cb0cb4c3c61328d67f7d93d9a371667a2da63581d99ba8ae02a898fad` |

The PS2 demo/EU/USA starts normalize to one body, as do their three member
waves, squad factories, and squad initializers. Field offsets differ by build
family, but admission, null-squad tolerance, empty publication, cycle commit,
member retry, and completion order agree. The sole observed semantic edge is
the all-position-components-zero fallback: PC's x87 equality path treats NaN
like equality, while Xbox and PS2 treat NaN as nonzero. No authored NaN input
has been established.

## Reconstruction boundary

[`RetailSpawnerCycleTransaction`](../../rebuild/OnslaughtRebuild.Core/RetailSpawnerCycleTransaction.cs)
now owns only the deterministic admission, counters, latches, due times, and
ordered adapter transcript. It preserves empty-squad publication before cycle
commit, amount consumption on null squad, immediate first wave, optional
attachment, retry without rollback, final release order, inactive late events,
and disable-during-busy behavior.

The runtime/Godot adapter still owns allocation, virtual initialization,
definition validity, reader/monitor lifetime, live ordered world-list mutation,
transform and clearance queries, member attachment, and event delivery. In
particular, a UnitAI scan must not snapshot the squad set: a squad appended by
the nested spawn helper can be the next node in that same scan.

## Cheapest remaining falsifier

On an app-owned copy, instrument one size-1 and one multi-member authored
spawner at the squad factory/initializer, world tail append, start-field writes,
member factory/attach, event-3000 scheduling, and completion/release sites.
Capture the prior tail's next link plus the spawner reader, admitted count,
member count, ordinal, busy latch, next-cycle time, and squad build flag. This
would test authored reach and event-manager behavior without weakening the
already closed static transaction. Forced null/failure arms require a bounded
copied-runtime harness; the pristine specimen remains read-only.
