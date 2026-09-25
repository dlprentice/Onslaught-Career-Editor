# CCareer__UpdateGoodieStates

Status: mixed — reset-time execution rechecked; broader unlock claims retain their dated evidence
Last updated: 2026-09-20
Summary: original reset produces nine instruction states; canonical progression reads and separate pending/count bookkeeping matter.
Source File: `references/Onslaught/Career.cpp` (partial-source comparison) | Binary: pristine `BEA.exe.original.backup`; selected instructions and original reset execution are linked below.

> Address: 0x0041c470 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** inherited partial-source comparison; the September 20 original-code reset check below does not certify all unlock rules.

## Purpose
Complex goodie unlock logic. This is the master function that evaluates all goodie unlock conditions including kill thresholds, level completion, grade milestones, and special conditions.

## Signature
```c
void CCareer::UpdateGoodieStates(void);
```

## Unlock Conditions (from FEPGoodies.cpp)
- Kill count thresholds (aircraft, vehicles, etc.)
- Level completion (specific missions)
- Grade requirements (A-rank on level X, S-rank on level Y)
- Cumulative grades (10 S-ranks total, etc.)
- Episode completion

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Called after mission completion and kill count updates
- In memory, `CGoodie::mState` values are normal ints `0/1/2/3` (GS_UNKNOWN/INSTRUCTIONS/NEW/OLD). In the repo's historical aligned file view they appear as `value << 16` because CCareer bytes are copied from `source + 2`.
- Don’t patch goodies using legacy 4-byte aligned offsets; patch using the true dword view offsets (`file_off = 0x0002 + career_off`).
- **Historical confusion**: Earlier docs claimed Goodie 228 overlapped mCareerInProgress. In the true view, Goodie 228 is at `0x22D6` and `mCareerInProgress` is at `0x248A`. The legacy aligned view placed “goodie 228” at `0x22D4`. Do NOT write to `0x22D4` as if it were mCareerInProgress.
- Kill totals are compared as `kills_payload = (kill_dword & 0x00FFFFFF)` (see `reverse-engineering/save-file/kill-tracking.md`). The “shift-16” appearance in some hex views is an alignment artifact, not what the binary compares.

## Evidence routing
- Earlier unlock tables, subject to recheck: `reverse-engineering/save-file/goodies-system.md`
- Source logic: `references/Onslaught/Career.cpp` (`CCareer::UpdateGoodieStates()`) and `references/Onslaught/FEPGoodies.cpp` (goodies[] data)
- Binary: `CCareer__UpdateGoodieStates` at `0x0041c470` (uses `& 0x00FFFFFF` masks before threshold compares)
- Supporting helpers now source-mapped:
  - `CGrade__ctor_char` (`0x00420ab0`) from `CGrade(char g)`
  - `CGrade__operator_gte` (`0x00420ac0`) from `CGrade::operator >=`
  - `CCareer__GetNode` (`0x00420af0`) from inline `CCareer::GetNode(int)`
  - `CCareer__NodeArrayAt` (`0x00421970`) compiler-emitted `node_base + index*0x40` helper used in one unlock branch

## September 20 original reset execution

The [startup composition](../../save-options-static-review-2026-05-26.md#original-startup-reset-including-goodies)
executes this unchanged body `[0041c470,00420aa9)`, SHA-256
`76401a9804734cdd9b9bb6c0aaeaa24feb23ea53b8f760aea18354f2476343d7`,
from the pristine specimen identified in that contract. It retains original
descriptor initialization and grade/episode/index helpers. All 17 reset cases
leave exactly slots `0, 1, 8, 14, 33, 36, 41, 42, 43` at state `1`, with the
remaining 291 slots and both bookkeeping globals zero. This establishes the
canonical reset result, not the entire 17,977-byte routine's semantics.

Fresh instructions at `00420230–0042026c` distinguish pending extra Goodies at
receiver `+0`, accumulated count at `00662b20`, and first-Goodie flag at
`00662b24`. Recompute adds pending extras and the unlocked-count delta, then
clears receiver `+0`. The old `new_goodie_count` name for that object field was
misleading. Partial source agrees at `Career.cpp:81–83,897–902` in the pinned
reference; these addresses were independently read from the executable.

World, grade and kill predicates read canonical CAREER `00660620`, while slot
updates use the supplied receiver. Original `0045ac30` initializes descriptor
thresholds used by those predicates; mapping zero BSS alone is invalid. The
controls use the canonical receiver, valid graph and reset rankings. They trap
unexpected entry into positive-ranking CRT conversion and do not exercise
malformed graphs, every unlock condition, actual file/device services or UI.

## 2026-05-07 Headless Read-Back

A read-only Ghidra headless export rechecked this function and seven supporting helpers:

- `CCareer__UpdateGoodieStates` (`0x0041c470`)
- `TOTAL_S_GRADES` (`0x0041c240`)
- `CCareer__GetAndResetGoodieNewCount` (`0x00421550`)
- `CCareer__GetAndResetFirstGoodie` (`0x00421560`)
- `CGrade__ctor_char` (`0x00420ab0`)
- `CGrade__operator_gte` (`0x00420ac0`)
- `CCareer__GetNode` (`0x00420af0`)
- `CCareer__NodeArrayAt` (`0x00421970`)

Result: `targets=8 dumped=8 missing=0 failed=0`.

Public-safe observations from the read-back:

- `CCareer__UpdateGoodieStates` still calls `CCareer__CountGoodies`, `TOTAL_S_GRADES`, the `CGrade` constructor/comparison helpers, `CCareer__GetNode`, and `CCareer__NodeArrayAt`.
- The four `TOTAL_S_GRADES` callsites line up with developer-item Goodies `74..77`.
- Source inspection confirms Goodies `71..73` are explicitly marked new when `COMPLETE_LEVEL_OR_EVO(741)` is true; the related episode-instruction logic marks 71 in episode 7 and 72/73 in episode 8, even though the normal Goodies wall coordinate mapping still skips from 70 to 74.
- Kill-threshold branches mask packed kill counters with `0xffffff`, matching the current true-view save docs.
- The function updates the aggregate new-goodie counter global consumed by `CCareer__GetAndResetGoodieNewCount`.
- The function updates the first-goodie flag global consumed by `CCareer__GetAndResetFirstGoodie`.
- No game launch, rename map, signature edit, or executable patch was performed for this read-back.

## Level 100 (training is not exempt)

MEASURED 2026-08-19 against official specimen `74154bfa…7750`. Training
skips **kill accumulation** (`CCareer__UpdateThingsKilled` `cmp eax, 0x64`
at `0x0041c188`) but this body still runs. World `100` is not a special
early-out.

| Goodie | Retail site | Predicate |
| --- | --- | --- |
| 0 | walk `0x00660634` `cmp [edx], 0x64` / hit `0x0041c527` → `cmp [node+4], 1` then `[this+0x1f44] = 2` if state `<= 1` | complete world 100 |
| 8 | same walk at `0x0041c7f2` / hit `0x0041c84f` → `[this+0x1f64] = 2` | complete world 100 |
| 78 | `0x0041de68` `push 0x43` (`'C'`) `CGrade__ctor_char`; `push 0x64`; `CCareer_T3_0041c330`; `CGrade__operator_gte`; `CCareer__GetGoodiePtr(0x4e)` store `2` | `GRADE(100) >= C` |
| 121 | `0x0041ea4f` `push 0x42` (`'B'`); same helpers; `GetGoodiePtr(0x79)` | `GRADE(100) >= B` |
| 164 | `0x0041f70e` `push 0x41` (`'A'`); same helpers; `GetGoodiePtr(0xa4)` | `GRADE(100) >= A` |

`CGrade::operator>=` treats `'S'` as above every other grade
(`Career.h:35`). A FillOut ranking of `1.0f` that survives the
score-time arm therefore unlocks 0, 8, 78, 121, and 164 together.
`0x0041e4a7` `push 0x64` is `GetGoodiePtr(100)` (concept-art band), not
world 100.

Cheapest falsifier: `0x0001c4c7` is not `83 3a 64`, **or** `0x0001de68`
is not `6a 43` (next insn is `lea ecx,[esp+0x16]` at `0x0001de6a`),
**or** `0x0001ea4f` is not `6a 42` (the preceding byte is `00`), **or**
`0x0001f70e` is not `6a 41`.

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Calls this after mission updates
- [CCareer__UpdateThingsKilled](CCareer__UpdateThingsKilled.md) - Kill counts affect unlocks
- [TOTAL_S_GRADES](TOTAL_S_GRADES.md) - S-rank milestone checks
- [CCareer__GetAndResetGoodieNewCount](CCareer__GetAndResetGoodieNewCount.md) - Debriefing new-goodie count consume/reset
- [CCareer__GetAndResetFirstGoodie](CCareer__GetAndResetFirstGoodie.md) - Debriefing first-goodie consume/reset gate
