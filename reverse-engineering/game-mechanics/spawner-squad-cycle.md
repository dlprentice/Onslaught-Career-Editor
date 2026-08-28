# Released spawner squad-cycle contract

Status: accepted static contract with a deterministic reconstruction boundary;
authored definition reach closed, per-world/runtime invocation reach open
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

## Definition identity and concrete factories

The authored spawner field is a unit-definition **name**, not a concrete class
enum. Construction walks the ordered global definition registry, compares the
name at definition `+0xB0`, and caches the matching zero-based ordinal at PC
spawner `+0x3DC`. The definition separately stores a raw class selector at
`+0xE0`.

Those values have different released lifetimes. Each cycle start re-resolves
the current authored name, reads the current row's selector, and passes that
selector directly to `CWorldPhysicsManager__CreateSquad`. Each member wave
instead passes the constructor-cached ordinal to
`CWorldPhysicsManager__CreateThingByType`; that factory walks to the ordinal
and only then reads the row's selector. A missing name faults on the cycle-start
path, while a missing/negative ordinal returns a null member. A registry reorder
could therefore make squad and member selection diverge, although no released
registry mutation has yet been demonstrated.

The exact PC factory identities are:

| Routine | Half-open range | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| member factory | `[0x0050DF80,0x0050E7F4)` | 2,164 | `a30e5fb1fce83522dd93710391bbb624e126f983e1a4e527f858a2c2e914e548` |
| squad factory | `[0x0050F4B0,0x0050F5BC)` | 268 | `9130332099b72bd952b878d0e057bf16f01369b9a55bb2fa9bca642b604bbb3d` |
| authored-size predicate | `[0x0050F680,0x0050F6A4)` | 36 | `966275f62570df243aa01e4b27f363e8e1ee8fcfd3dab0e42e3db240ed0d535f` |

PC RTTI at each final primary vtable closes the member class labels below.
`Preserve size?` is the constructor's exact policy decision; it must not be
renamed to “can create a squad.”

| Selector | Member shell | Preserve size? | Squad shell |
| ---: | --- | :---: | --- |
| `0` | `CMech` | yes | `CRelaxedSquad` |
| `1` | `CPlane` | yes | `CNormalSquad` |
| `2` | `CGroundVehicle` | yes | `CNormalSquad` |
| `3` | `CInfantryUnit` | yes | `CRelaxedSquad` |
| `4` | `CCannon` | no | null |
| `5` | `CBoat` | no | null |
| `6` | `CCarrier` | no | null |
| `7` | `CBuilding` | no | null |
| `8` | `CPlane` | no | null |
| `9` | `CBomber` | no | null |
| `10` | `CGroundAttackAircraft` | no | null |
| `11` | null | no | null |
| `12` | `CDropship` | no | null |
| `13` | `CMine` | no | null |
| `14` | `CHiveBoss` | no | null |
| `15` | `CSubmarine` | no | null |
| `16` | `CDiveBomber` | no | null |
| `17` | `CThunderHead` | no | null |
| `18` | `CCarver` | no | null |
| `19` | `CGillM` | no | null |
| `20` | `CSentinel` | no | null |
| `21` | `CWarspite` | yes | `CNormalSquad` |
| `22` | `CFenrir` | no | null |
| `23` | `CWarspiteDome` | no | null |
| `24` | `CPod` | no | null |
| `25` | `CSimpleBuilding` | yes | null |
| outside unsigned `0..25` | null | yes | `CNormalSquad` |

Selectors `1` and `8` prove why the raw selector cannot be collapsed to the
member class: both construct `CPlane`, but only selector `1` preserves authored
squad size and constructs a normal squad. Selector `25` preserves size and can
construct multiple `CSimpleBuilding` members without a squad. Selector `11`
constructs neither class, is clamped to size one, and can leave an admitted
cycle retrying indefinitely if authored.

The exact 175,603-byte `default physics.dat`, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`,
closes authored definition reach. All 160 Unit records carry one serialized
behaviour type; the type-12 RTTI/slot-1 chain maps them to raw selectors. All 38
Spawner records then join without ambiguity through their field-1 Unit name:

| Raw selector | Spawner records | Released size/squad consequence |
| ---: | ---: | --- |
| `0` | 3 | preserve authored size; `CRelaxedSquad` |
| `2` | 16 | preserve authored size; `CNormalSquad` |
| `3` | 11 | preserve authored size; `CRelaxedSquad` |
| `8` | 6 | clamp size to one; no squad |
| `16` | 2 | clamp size to one; no squad |

Thus the six authored fighter spawners use selector `8`, not the legacy
selector-`1` plane route, and the two authored ground-attack spawners use
selector `16` / `CDiveBomber`; all eight discard their authored squad sizes at
construction. The serialized behaviour factory cannot produce selector `1` at
all. It can produce selector `11` only from serialized type `2`, but none of the
160 Unit records uses that type. Four Unit records do produce selector `25`,
but none of the 38 Spawner records names them. These three factory branches are
therefore dormant for the shipped default Spawner-definition corpus unless
another runtime writer mutates definition `+0xE0`; no such writer is currently
known. World placement and actual invocation of each of the 38 definitions
remain separate open questions. The exact serialized-type map and duplicate
record caveat are owned by
[`config-dat.md`](../asset-formats/config-dat.md#unit-behaviour-and-spawner-join).

Every valid PC and Xbox member/squad allocation tests the allocator result and
returns null on failure. The corresponding three PS2 factory families reproduce
the selector matrix, but pass each valid allocation directly to its constructor
without a local null test. PS2 allocation-null behavior is therefore a static
fault prediction, not an executed result. The factories return only constructed
shells; the member wave still owns definition initialization, cooldown, optional
squad attachment, and success-count mutation in that order.

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

## Event-3000 scheduler lifecycle

The one nonfinal scheduling tail passes the same logical tuple in PC retail and
demo, Xbox USA and Issue11, and the PS2 demo/EU/USA builds:

```text
event = 3000, listener = this spawner,
due = float32(current event-manager time + configured member delay),
priority = START_OF_FRAME, data = null, reuse record = null
```

PC retail calls the absolute-time overload at `0x0044B370`; it does not call
the manager's relative-time wrapper. The caller forms and stores the due
float32 before the call, so the manager does not add its clock a second time.
Passing a null reuse record makes every accepted successor a fresh pool object.
The manager does not search for another event number, listener, due time, or
matching tuple and therefore does not deduplicate. A rejected filing returns
no status to the spawner and rolls nothing back, so the busy cycle can remain
latched without a future callback after invalid-manager, excessive-time, or
pool-exhaustion rejection.

Outstanding-event counts need three distinct statements. In the ordinary
self-generated chain, a stable boundary after the immediate wave or after
callback cleanup contains at most one future event-3000 record. During a
nonfinal callback, the current due record and its fresh successor coexist until
the old record is recycled. The manager advances its insertion ring before it
flushes the due ring, so the successor cannot execute recursively in that same
flush. This is a producer invariant, not a scheduler guarantee: externally
filed duplicates are retained FIFO, can each advance a still-busy wave, and can
each schedule another successor. Once one callback completes the cycle, later
duplicates and already-filed successors remain queued but return inertly at the
busy gate.

Spawner destruction also is not event cancellation. Monitor shutdown zeros
the deletion-aware listener cell of every outstanding scheduled record but
does not remove the record from its ring or overflow list. The stale record
continues to occupy one live pool slot until due; `Flush` then observes a null
listener, skips the callback, still counts the record as processed, and
recycles it. A distant overflow record can therefore survive until its due
time or whole-manager shutdown. These ordering and lifetime laws are closed
statically across all seven examined builds; a spawner-specific causal runtime
capture of successor coexistence, deliberate duplication, and destruction
invalidation remains open.

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

That adapter must retain both the definition ordinal and raw class selector,
and derive member shell, authored-size policy, and squad shell independently.
It must not collapse selectors `1` and `8` merely because both return
`CPlane`. No unused parallel factory abstraction belongs in deterministic Core;
the selector table becomes executable when the adapter begins materializing
released actor scenes.

An adapter consuming `ScheduleEvent3000` must translate it exactly to a fresh
`AddEvent(3000, spawnerListener, due, StartOfFrame, data: 0, reuse: -1)` call.
Spawner teardown must clear that listener through the active-reader lifetime
boundary without removing the filed event. `RetailEventScheduler` already owns
the resulting no-dedup, advance-before-flush, null-listener accounting, and
recycling behavior; no parallel scheduler abstraction is needed.

## Cheapest remaining falsifier

On an app-owned copy, instrument one size-1 and one multi-member authored
spawner at the squad factory/initializer, world tail append, start-field writes,
member factory/attach, event-3000 scheduling, and completion/release sites.
Capture the prior tail's next link plus the spawner reader, admitted count,
member count, ordinal, busy latch, next-cycle time, and squad build flag. This
would test authored reach without weakening the already closed static
transaction. In a bounded optional arm, record the in-flight event handle and
the newly allocated successor during its callback, then destroy a spawner with
one event pending and observe listener zeroing, callback suppression, and later
pool return. Forced duplicate, null, and allocator-failure arms require a
copied-runtime harness; the pristine specimen remains read-only.
