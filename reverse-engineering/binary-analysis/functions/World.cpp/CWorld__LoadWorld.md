# CWorld__LoadWorld

> Address: 0x0050b9c0 | Source: World.cpp

Status: active bounded static contract
Last updated: 2026-09-07
Summary: three-argument world loader; allocation, explicit-tree initialization,
ordinary-object initialization and base-world skip order are byte-checked.
Source File: none — World.cpp is absent from the pinned references/Onslaught snapshot | Binary: BEA.exe pristine specimen (identity below).
Evidence: pristine executable bytes and exact World110 BSWD/RLWD inputs; no
new retail execution, Ghidra mutation or complete runtime-construction claim.
Specimen: local-lab/safe-copy-bea-pristine/BEA.exe.original.backup,
2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Identity and ABI

The half-open body `[0x0050b9c0,0x0050d4b2)` is 6,898 bytes, SHA-256
`8deeac85f88c5a505f4b65dc2ff05b2c485aea78cd93523558949c0de3f96e5d`.
All 2,023 retained own-function instruction rows in
`local-lab/ghidra-fullpass-2026-07-23/exports/W008/instructions.tsv` matched
pristine bytes on September 7. Bounded independent `objdump` readback also
confirmed the explicit-tree branch.

Entry ECX is the receiver. The three stack arguments are the memory-buffer
read receiver, the base-world flag, and the initial world-state setup flag.
The final `RET 0xc` confirms three explicit arguments. The boolean return
interpretation and prototype are inherited from the
[July 13 ABI correction](../../ghidra-full-reaudit-closeout-2026-07-13.md);
this pass did not reopen the database or promote new metadata.

```c
bool __thiscall CWorld__LoadWorld(
    void * this,
    void * mem_buffer,
    int is_base_world,
    int initialize_world_state);
```

The input is a world buffer, not established as a whole AYA archive by this
body. The World110 materializer separately identifies the enclosing chunks.

## Allocation and initialization order

1. Header/script loading and the recursive base-world load precede the outer
   world's ordinary objects. The recursive call is at `0x0050bbf5`.
2. Ordinary-object records allocate their objects before the explicit-tree
   loop. Allocation is distinct from virtual Init and world publication.
3. The explicit-tree loop consumes groups and records in serialized order.
   Its eligible records call OID 7 creation at `0x0050cec4` and virtual Init
   at `0x0050ced8`.
4. Influence-map load/skip follows at `[0x0050cf11,0x0050cf3d)`. The ordinary
   Init loop then resolves target references and applies the career-existence
   gate before each eligible virtual Init at `0x0050cfc8`.
5. Waypoint/occupancy work follows. Only the non-base path can reach
   `CWorld__SpawnInitialThings` at `0x0050d431`, after ordinary initialization;
   the base flag at `0x0050d417` skips to `0x0050d48e`.

Thus explicit base-world trees precede ordinary base-world Init. The base load
finishes before World110's RLWD Init, whose first landing craft is ordinal 8.
Later squad records may have allocated objects but their Init has not run at
that point. Saved career bits can omit ordinary-object Init; a serialized
row count is not a claim that every corresponding object was published.

## Explicit trees: repeated data is not repeated creation

Each record reads float X, float Y and signed variant before deciding whether
to instantiate it. The reads occur at `0x0050cde1`, `0x0050cdf2` and
`0x0050ce00`. The gate `[0x0050ce05,0x0050ce1b)` admits a base-world load;
for a non-base load it skips allocation when the base-world id is not `-1`.
Its 22 bytes have SHA-256
`7eb2326beb6bcd9f166d66adbf0258df2779979a6de3eb2b444654c7fcbafde2`.

For admitted records, four-character comparisons at `0x0050ce99` and
`0x0050ceb4` bypass allocation for names beginning with `fern` or `bush`.
The literals were read at `0x00633a74` and `0x00633a6c`. These are loader
branches, not a general rule that vegetation data is disposable.

World110's base tree region `[2709,29549)` and level tree region
`[18327,45167)` are byte-identical 26,840-byte tables, SHA-256
`26d874c61ed827db550feb27e57e3c076440d58b432ad0788e2a379b08db82a9`.
Each contains 753 ferns and 1,481 pines. Only the base-world pine records call
Tree Init; all level-world records are read past because a base is present.
This conclusion follows the branch and each table's role, rather than
content deduplication. Both serialized tables remain preserved.
Exact source identities, group offsets and the connected Core input boundary
are in the [World110 owner](../../../game-mechanics/world-110-initial-constructor-seeds.md).

## Existing score-time finding

The August 19 L100 receipt reported the final outer RLWD score-time stores to
`CGame+0x108/+0x10c` at `0x0050d2e0/0x0050d2ed`, with payload words at
`+0x147ba/+0x147be` equal to 300.0f and 500.0f. This is an inherited bounded
measurement, not a September 7 reread of those L100 values. It does not name
the other tail words or establish runtime score behavior by itself.

## Implementation and evidence boundary

The shared explicit-tree parser now preserves group/record order, raw XY
words, variants and exact offsets. World110 retains the two tables in its
existing initial actor/input asset and marks the measured Tree Init branch.
Level100's existing pine/shadow projection and waypoint parser use that same
reader. No second tree artifact, render path or live world has been created.

Tree terrain/yaw/resource initialization, complete ordinary class Init,
reader/world/MapWho publication, shared event/random order and post-load
player assignment still require concrete owners. Static loop closure does not
establish a playable World110 or campaign transition. The older wave queue
percentages, generic memory claims and level-number classifications do not
serve as current evidence for this body.

Cheapest falsifier: compare the exact body and the base/name skip branches
above, then reproduce both admitted tree regions from the pinned World110
archive. Controlled runtime validation remains separate.
