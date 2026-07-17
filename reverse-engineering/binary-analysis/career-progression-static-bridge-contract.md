# Career progression static bridge

This page connects source-side career vocabulary to the retail save and static
function evidence without claiming runtime persistence or source identity.

| Concern | Canonical evidence |
| --- | --- |
| Retail file layout and byte preservation | [`../save-file/save-format.md`](../save-file/save-format.md) |
| Campaign nodes and links | [`../save-file/career-graph.md`](../save-file/career-graph.md) and [`../save-file/career-links.md`](../save-file/career-links.md) |
| Source architecture | [`../source-code/gameplay/career-system.md`](../source-code/gameplay/career-system.md) and [`../source-code/gameplay/game-system.md`](../source-code/gameplay/game-system.md) |
| Career update/recalculation | [`functions/Career.cpp/CCareer__Update.md`](functions/Career.cpp/CCareer__Update.md) and [`functions/Career.cpp/CCareer__ReCalcLinks.md`](functions/Career.cpp/CCareer__ReCalcLinks.md) |
| Mission result handoff | [`functions/game.cpp/CGame__FillOutEndLevelData.md`](functions/game.cpp/CGame__FillOutEndLevelData.md), [`functions/game.cpp/CGame__DeclareLevelWon.md`](functions/game.cpp/CGame__DeclareLevelWon.md), and [`functions/game.cpp/CGame__DeclareLevelLost.md`](functions/game.cpp/CGame__DeclareLevelLost.md) |
| Secondary-objective predicate | [`functions/EndLevelData.cpp/CEndLevelData__IsAllSecondaryObjectivesComplete.md`](functions/EndLevelData.cpp/CEndLevelData__IsAllSecondaryObjectivesComplete.md) |

`level_structure`, `CCareer`, `CGame`, and `CEndLevelData` are safe bridge
vocabulary for implementation planning. This evidence does not prove runtime
save/load behavior, mission outcome persistence, campaign-map UI behavior,
Goodie recomputation, exact source-to-retail layout identity, or rebuild parity.
