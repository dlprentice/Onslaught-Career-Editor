# Career.cpp Function Mappings

> Functions from Career.cpp mapped to BEA.exe binary
> Source: references/Onslaught/Career.cpp (Stuart's code)

## Overview
- **Functions Mapped:** 37
- **Status:** MIGRATED from ghidra-analysis.md
- **Classes:** CCareer, CCareerNode

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x0041b6a0 | CCareer__StaticInitDefaults | VERIFIED | [View](CCareer__StaticInitDefaults.md) |
| 0x0041b740 | CCareerNode__Blank | VERIFIED | [View](CCareerNode__Blank.md) |
| 0x0041b770 | CCareerNode__SetBaseThingExistTo | VERIFIED | [View](CCareerNode__SetBaseThingExistTo.md) |
| 0x0041b7b0 | CCareer__GetLevelStructure | VERIFIED | [View](CCareer__GetLevelStructure.md) |
| 0x0041b7c0 | CCareer__Blank | VERIFIED | [View](CCareer__Blank.md) |
| 0x0041b8f0 | CCareer__GetNodeFromWorld | VERIFIED | [View](CCareer__GetNodeFromWorld.md) |
| 0x0041b940 | CCareerNode__GetChildLinks | VERIFIED | [View](CCareerNode__GetChildLinks.md) |
| 0x0041b9f0 | CCareerNode__GetParentLinks | VERIFIED | [View](CCareerNode__GetParentLinks.md) |
| 0x0041bb20 | CCareer__DoesBaseThingExist | VERIFIED | [View](CCareer__DoesBaseThingExist.md) |
| 0x0041bbb0 | CCareer__IsWorldLater | VERIFIED | [View](CCareer__IsWorldLater.md) |
| 0x0041bc60 | CCareer__Later | VERIFIED | [View](CCareer__Later.md) |
| 0x0041bd00 | CCareer__Update | VERIFIED | [View](CCareer__Update.md) |
| 0x0041bdf0 | CCareer__ReCalcLinks | VERIFIED | [View](CCareer__ReCalcLinks.md) |
| 0x004496e0 | CCareer__AreSecondaryObjectivesComplete | VERIFIED | Behavior-verified helper used by `CCareer__ReCalcLinks`, `CGame__FillOutEndLevelData`, and `CGame__RunOutroFMV` |
| 0x0041c180 | CCareer__UpdateThingsKilled | VERIFIED | [View](CCareer__UpdateThingsKilled.md) |
| 0x0041c240 | TOTAL_S_GRADES | VERIFIED | [View](TOTAL_S_GRADES.md) |
| 0x0041c330 | CCareer__GetGradeForWorld | VERIFIED | [View](CCareer__GetGradeForWorld.md) |
| 0x0041c450 | CCareer__CountGoodies | VERIFIED | [View](CCareer__CountGoodies.md) |
| 0x0041c470 | CCareer__UpdateGoodieStates | VERIFIED | [View](CCareer__UpdateGoodieStates.md) |
| 0x00420ab0 | CGrade__ctor_char | VERIFIED | [View](CGrade__ctor_char.md) |
| 0x00420ac0 | CGrade__operator_gte | VERIFIED | [View](CGrade__operator_gte.md) |
| 0x00420af0 | CCareer__GetNode | VERIFIED | [View](CCareer__GetNode.md) |
| 0x00421200 | CCareer__Load | NAMED | [View](CCareer__Load.md) |
| 0x00421350 | CCareer__Save | NAMED | [View](CCareer__Save.md) |
| 0x004213c0 | CCareer__SaveWithFlag | NAMED | [View](CCareer__SaveWithFlag.md) |
| 0x00421430 | CCareer__GetSaveSize | NAMED | [View](CCareer__GetSaveSize.md) |
| 0x00421470 | CCareer__GetGradeFromRanking | VERIFIED | [View](CCareer__GetGradeFromRanking.md) |
| 0x004214e0 | CCareer__SetSlot | VERIFIED | [View](CCareer__SetSlot.md) |
| 0x00421550 | CCareer__GetAndResetGoodieNewCount | VERIFIED | [View](CCareer__GetAndResetGoodieNewCount.md) |
| 0x00421560 | CCareer__GetAndResetFirstGoodie | VERIFIED | [View](CCareer__GetAndResetFirstGoodie.md) |
| 0x00421570 | CCareer__IsEpisodeAvailable | VERIFIED | [View](CCareer__IsEpisodeAvailable.md) |
| 0x004218f0 | CCareer__GetKillCounterTopByte_23F4 | VERIFIED | [View](CCareer__GetKillCounterTopByte_23F4.md) |
| 0x00421900 | CCareer__GetKillCounterTopByte_23F8 | VERIFIED | [View](CCareer__GetKillCounterTopByte_23F8.md) |
| 0x00421910 | CCareer__SetKillCounterTopByte_23F4 | VERIFIED | [View](CCareer__SetKillCounterTopByte_23F4.md) |
| 0x00421940 | CCareer__SetKillCounterTopByte_23F8 | VERIFIED | [View](CCareer__SetKillCounterTopByte_23F8.md) |
| 0x00421970 | CCareer__NodeArrayAt | VERIFIED | [View](CCareer__NodeArrayAt.md) |
| 0x00421980 | CCareer__GetGoodiePtr | VERIFIED | [View](CCareer__GetGoodiePtr.md) |

## Related
- Source: `references/Onslaught/Career.cpp`
- Header: `references/Onslaught/Career.h`
- Parent: [../README.md](../README.md)
