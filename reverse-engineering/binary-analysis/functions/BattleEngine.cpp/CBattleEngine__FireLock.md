# CBattleEngine__FireLock

Status: active static function note; historical 2026-08-23 runtime refuter RED,
`C1_CANDIDATE_PARTIAL` preserved; revalidated 2026-08-30
Last updated: 2026-08-30
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is the 2026-08-04 target-lock promotion label, not this proof.
This wake does **not** redo `FUN_00598c85` (`8002c949`) or rewrite
`CBattleEngine__AddProjectile.md` / `CBattleEngine__HandleLocks`.
Did not adopt a C1 rename. Operator 2026-08-19 closed the unlabeled
first-gates mill for this root. Cycle 89 accepted the DisplayLock
and GetCurrentTarget byte notes. This follow-on names rebuild
owners only; it does not redo the body.

The historical runtime refuter below was revalidated from retained receipt
bytes on 2026-08-30. It adds no new TTD replay, runtime capture, Ghidra
mutation, campaign generation, or rebuild claim.

> Address: `0x00407060`

## Contract

Incoming-ECX `thiscall`. First insn `push ebx`. Three `ret 0x4`
exits (`0x004070c4`, `0x00407120`, `0x0040713c`). Body
`0x00407060`–`0x0040713e` is 223 bytes, SHA-256
`59141a0e0053ed2011e834d07badaa6c68252700e2c6adea0c30c2f7c8f8e54e`.
Four `E8`, zero `E9`. Neighbour table `CBattleEngine__LockHit`
starts at `0x00407140` and is not claimed. Preceding table
`CBattleEngine__StartLock` ends at `0x0040705a` and is not rewritten.

The body, with `ebx = [esp+8]` after the `push ebx`:

1. `test ebx, ebx` / `mov edi, ecx`. Null arg jumps to the shared
   epilogue at `0x00407139`.
2. Walk the set at `this+0x294` (`lea ecx, [edi+0x294]`). For each
   live node `esi`: `fld [esi+8]` / `fcomp dword [0x00672fd0]` /
   `fnstsw ax` / `test ah, 1`. That is CF after compare, so the
   taken path is `[esi+8] < [0x00672fd0]`. Then `cmp [esi], ebx`.
   Both true → `push esi` / `E8` `CSPtrSet__Remove` `0x004e5bd0`.
3. Walk the set at `this+0x2a4`. If some node has `[node]==ebx`,
   `ecx=esi` / `E8` `CGenericActiveReader__dtor` `0x0044b1d0` then
   `push esi` / `mov ecx, 0x009c3df0` / `E8` `CDXMemoryManager__Free`
   `0x00549220`.
4. Else `push esi` / `E8` `CSPtrSet__AddToHead` `0x004e5a80`, then
   `fld [0x00672fd0]` / `fst [esi+4]` / `fadd dword [0x005d85ec]` /
   `fstp [esi+8]`. File `0x001d85ec` is `00 00 00 3f` = `0.5f`.
   `0x00672fd0` is BSS (not in the 2,506,752-byte image); the
   campaign already closed it as `CEventManager` `mTime`.

Those field names, `ToRead`, `Add` versus `AddToHead`, and the
callee bodies are **not** this proof.

One inbound `.text` `E8`/`E9`: `CALL` at `0x005074c9` inside table
`ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0`–`0x005078ab`.
The site is `push esi` / `E8` after `DisplayLock` `0x00407310`
returns nonzero and `mov ecx, [esp+0x10]`. Zero encodings of imm
`60 70 40 00` in the image.

Source architecture (not proof): `CBattleEngine::FireLock`
`references/Onslaught/BattleEngine.cpp:842-866` and inlined
`CLockInfo::Fired` at `:3153-3157` (`mStart=GetTime();
mFinish=mStart+0.5f`). `HandleLocks` does not call `FireLock`.
Retail inlines the already-fired walk and the `Fired` stores.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00007060` is not `53`, **or**
`0x0000713c` is not `c2 04 00`, **or** `0x000070c8` is not
`e8 03 eb 0d 00`, **or** `0x00007106` is not `e8 75 e9 0d 00`,
**or** `0x00007129` is not `e8 a2 40 04 00`, **or** `0x00007134`
is not `e8 e7 20 14 00`, **or** body SHA-256 is not
`59141a0e…e54e`, **or** `tools/call_xref_scan.py` on
`0x00407060` is not exactly one `CALL` at `0x005074c9`, **or**
`0x001d85ec` is not `00 00 00 3f`, **or** a second `.text`
`E8`/`E9` to this entry exists.

## Historical runtime refuter — 2026-08-23 RED; revalidated 2026-08-30

At the dated measurement and at this revalidation, contract
`C-ad6551a6e68e8140` remains `C1_CANDIDATE_PARTIAL`, question
`Q-627e8b2d6a55ae8b` remains `CANDIDATE_NEEDS_REFUTER` and open, and no
campaign authority owner changed. Future readers must select current campaign
authority through `developer_state.json` → `current_re_authority`, not from a
generation number frozen in this historical note.

The public-safe receipt
[`CBattleEngine__FireLock__runtime-refuter-2026-08-23.tsv`](CBattleEngine__FireLock__runtime-refuter-2026-08-23.tsv)
records the input identities and branch census. The original normalized set is
exactly 139 rows: 58 support inputs plus 81 execution-coverage files, SHA-256
`1df43b51b428da9f11a9e2acdb16ca3241431e92cec631e0a24bfd0b2822b765`.
That historical identity and its range-only census were reproduced on Linux
with a read-only path adapter, candidate-parent Git blobs, and the preserved
Windows path-display and ordering rules. The digest must not be recomputed from
newer tracked files.

The 81 historical coverage files comprise 66 campaign receipts, three Level
521 receipts, and 12 exact legacy local-lab receipts. The corrected current
indexer accepts the selected 66+3 Archive B receipts and the full 72-receipt
Archive B corpus, while rejecting all 12 legacy local receipts. The indexer is
`tools/ttd_coverage_index.py`, SHA-256
`23b7c9ab05c93eeb406d99f3f6dafc0f8a4696500e97218eacf873ade922a8a2`,
Git blob `d01682cf3ab72f3cfe82a92ae96005d9d9e31e5c`, introduced after the
candidate by `8d2b72a6b1e2cfba5cc47701f3f021bc6d4cab91`.

| Current-tool corpus | Receipts | Portable receipt-set SHA-256 | Linux-root-bound index-content SHA-256 |
| --- | ---: | --- | --- |
| Selected campaign root | 66 | `4570f7ee938519373619e6a6b0e5f82c688814c37f6f26ed21b30144d6aca581` | `7c560044fd19a7d9f36421884727f4727f0d18d4524ec12cb88267e308e1b8f8` |
| Selected Level 521 root | 3 | `6e9e3b4a899e5405bdd68bfa2c71d589a844f3c62de0a1f11badbc729e0e098d` | `85ec09f11aa4cbad29b6ca36c72d7f497a642eac959dbae62c10667db48544af` |
| Full Archive B root | 72 | `926b6ec66befc8e0060d49efc6c00d485ab6a6ed563b55c79d86bf829b7d5c39` | `d57d872c6f265539839697f6894dab390152e4ec03975660d83f16459740d454` |

The legacy subset manifest is SHA-256
`938bdc9237f7d853e7c221c85249349b82cc2c45d13a4c272e224db113adfe51`
over byte-sorted `local-lab/<relative-path><TAB><file-sha256><LF>` rows. Its
bytes remain exact historical inputs, but current admission fails closed: five
receipts use the unsupported complete `Position` terminal class, two contain a
failed assertion, and five predate the required `counters_quarantined` field.
They are not current-valid coverage receipts.

The two call-context replicas, SHA-256
`05d45bd7d0dcfb7b4e647efcc532c5171dd1164dd7059f7891b955aed6e135ce`
and `c496431e684e3b565bc37354c2244f9f019d9093fdd4dfa3d5da0065dcab51ef`,
each contain 14 gap-free FireLock call/entry/return envelopes from callsite
`0x005074c9` inside `ProjectileBurst__SpawnFromCurrentPreset`: six non-null
arguments followed by eight null arguments; `StartLock` has zero calls. They
are deterministic replicas of one gameplay trace, not independent gameplay.
The older data-write replicas, SHA-256
`2f8941ecff8bcc1070148256dd27c3979783c4f9961263c4ff407e146b9a3b2b`
and `9c87ffed902dbf173afe5d2cd477e2ecfb8fc21d103f2874b2d86c7286059ef3`,
support positive callback chronology only; endpoint and zero-write promotion
remain superseded. Coverage at `0x0040707f` alone does not prove a container
value. The bounded join with that positive chronology supports only the
empty-active-list observation recorded here.

The reproduced historical census is:

| PC or branch group | Receipt hits |
| --- | ---: |
| FireLock entry `0x00407060` | 3 |
| StartLock entry `0x00406fc0` | 0 |
| active iterator `0x0040707f` | 1 |
| active compare/absent return/remove `0x004070a4/0x004070c4/0x004070c8` | 0 |
| fired iterator/compare/add `0x004070db/0x004070ea/0x00407106` | 0 |
| stamp stores `0x00407112/0x0040711b` | 0 |
| duplicate destructor/free `0x00407129/0x00407134` | 0 |
| shared return `0x0040713c` | 3 |

The three entry sessions are Level 521 takes 1, 2, and 4, with receipt
SHA-256 values
`e7e966ef592a9f9e5771d34e75bc4d7eb4a501fd6e2ab0f65a5df4dd266fefaa`,
`4da8c41fae2a6ca768769646e152a40947db3d4bf3a393b03a2f727d4788c3a4`,
and `26d0db3700590167abb26328520beecfdb145562fb9113bf46a48811d5b2ba66`.
Only take 4 reaches the active iterator. The strict-valid 69 selected receipts
and, independently, the strict-valid 72-receipt corpus produce the same
decisive 3/0/1/zero-positive-arm result.

This attempt is RED for the proposed C2 promotion. It does not negate the
extant C1 authority's `INDEPENDENT_REFUTATION_SURVIVED` evidence state;
`RED_C1_PRESERVED` means the requested transfer, timestamp, and destruction
runtime witnesses were absent. Static bytes and pinned source still do not
promote those candidate arms to runtime causality.

The dated next-instrument proposal is a read-only, serialized Windows TTD
branch screen followed, only if warranted, by bounded v3 write replays against
the retained logical trace `damage-script-level100-20260802-a` (25,769,803,776
bytes; SHA-256
`994a6aa99444176ec4b8985d03bd95549a07f9eead6e41492a24c4567c9befcd`).
That trace was not among the 139 inputs; its size was checked but its bytes were
not rehashed on 2026-08-30. It must be copied into a separately authorized
Windows TTD environment. Archive B is never a writable execution root.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `59141a0e…e54e`. `call_xref_scan` still one `CALL`
at `0x005074c9`. Cycle 89 accepted the DisplayLock /
GetCurrentTarget byte notes. Did not open Ghidra. Did not edit
`rebuild/**`.

Retail entity: player `CBattleEngine` lock-set move at projectile
spawn, after `DisplayLock` returns nonzero. Stuart architecture
(not proof): `BattleEngine.cpp:842-866`.

Nearest reconstruction owner (absent lock-set type):
`rebuild/OnslaughtRebuild.Core/Simulation.cs` `TryFire` /
`LaunchWalkerRound` / `EmitWeaponFireEvent`. That is the player
spawn of the same `ProjectileBurst__SpawnFromCurrentPreset`
body. Core has no `+0x294` / `+0x2a4` occupancy and does not
call this function.

Not the owner: `Level100ActorWeaponRuntime.LaunchActorRound`
models that spawn for **scatter only**.
`ActorRoundState.Locked` is the round seek/homing flag, not
this transition.

Godot: none. HUD target-lock layers stay absent
(`rebuild/OnslaughtRebuild.Godot/Assets/Hud/README.md`).

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this
mapping until that lane names the arm.

Siblings: `CBattleEngine__DisplayLock` /
`CBattleEngine__GetCurrentTarget` in this folder.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00407060` | `CBattleEngine__FireLock` | `53 8b5c2408 5657 85db … e803eb0d00 … e875e90d00 … e8a2400400 … e8e7201400 … c20400` (223 B) | incoming-ECX thiscall; ret 0x4 ×3; 223 B; 4 E8 `CSPtrSet__Remove` + `CSPtrSet__AddToHead` + `CGenericActiveReader__dtor` + `CDXMemoryManager__Free` / 0 E9; 1 inbound `ProjectileBurst__SpawnFromCurrentPreset` `0x005074c9`. HIGH on ABI, set occupancy `+0x294`/`+0x2a4`, `0.5f` add, unique inbound. Mapping `PARTIAL_CONTRACT` onto `Simulation.TryFire`. **Not** on field names, `FiredAt` as a retail body, or rebuild parity. |
