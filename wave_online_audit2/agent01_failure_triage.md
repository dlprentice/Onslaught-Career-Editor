# Semantic audit failure triage (online pass 2026-02-12)

Scope: 66 failing file entries from `reverse-engineering/binary-analysis/semantic-audit-online-pass-2026-02-12.json`. Classification based on mismatch type plus repo-doc cues only (no MCP/Ghidra).

## Bucket counts
- (1) False positive (callsite/non-entry): 0
- (2) Name-style mismatch only (`Class::` vs `Class__`): 2
- (3) Wrong address mapping in doc: 14
- (4) Missing function object (manual UI create likely): 44
- (5) Other: 6

## Top actionable fixes
1. Missing function objects: manual UI create at addresses listed under bucket (4), then re-run audit. Start with the most central docs so they stop polluting rollups (examples below).
2. Wrong address mappings: update doc tables to the actual names already in the program (bucket 3). These are likely stale or mis-mapped entries (examples below).
3. Name-style mismatches: normalize `Class::` -> `Class__` (or vice versa) in display-settings docs (bucket 2).
4. Unnamed functions (FUN_*) in bucket (5): rename in Ghidra to expected names (function objects exist).

### Examples
- Missing function object: `0x004f7a80` expected `CScriptObjectCode__Run`; actual is missing
- Wrong address mapping: `0x004213c0` expected `CCareer::SaveToFile` but actual is `CCareer__SaveWithFlag`
- Wrong address mapping: `0x00421200` expected `CCareer::LoadFromFile` but actual is `CCareer__Load`
- Wrong address mapping: `0x00421430` expected `CCareer::GetSaveSize` but actual is `CCareer__GetSaveSize`
- Name-style mismatch: `0x00528f80` expected `CD3DApplication::Init` but actual is `CD3DApplication__Init`
- Name-style mismatch: `0x005290a0` expected `CD3DApplication::Create` but actual is `CD3DApplication__Create`
- Unnamed function (rename only): `0x00404960` expected `CAtmospheric__Unlink` but actual is `FUN_00404960`
- Unnamed function (rename only): `0x00404920` expected `CAtmospheric__Link` but actual is `FUN_00404920`

## Bucket (1) False positive due to callsite/non-entry
- (none)

## Bucket (2) Name-style mismatch only
- `lore-book/reverse-engineering/binary-analysis/functions/display-settings.md`
- `reverse-engineering/binary-analysis/functions/display-settings.md`

## Bucket (3) Wrong address mapping in doc
- `lore-book/reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `lore-book/reverse-engineering/binary-analysis/executable-analysis.md`
- `lore-book/reverse-engineering/binary-analysis/functions/DXBattleLine.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/IScript.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
- `reverse-engineering/binary-analysis/executable-analysis.md`
- `reverse-engineering/binary-analysis/functions/DXBattleLine.cpp.md`
- `reverse-engineering/binary-analysis/functions/DXFrontEndVideo.cpp.md`
- `reverse-engineering/binary-analysis/functions/IScript.cpp.md`
- `reverse-engineering/binary-analysis/functions/Submarine.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/landscapeib.cpp/_index.md`

## Bucket (4) Missing function object / needs manual UI create
- `lore-book/reverse-engineering/binary-analysis/README.md`
- `lore-book/reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/Cannon.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `lore-book/reverse-engineering/binary-analysis/functions/GroundAttackAircraft.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__InitColorGradient.md`
- `lore-book/reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `lore-book/reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/Sentinel.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/gcgamut.cpp.md`
- `lore-book/reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`
- `reverse-engineering/binary-analysis/README.md`
- `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/Cannon.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md`
- `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`
- `reverse-engineering/binary-analysis/functions/DataType.cpp.md`
- `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md`
- `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`
- `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md`
- `reverse-engineering/binary-analysis/functions/GroundAttackAircraft.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__InitColorGradient.md`
- `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md`
- `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md`
- `reverse-engineering/binary-analysis/functions/Sentinel.cpp.md`
- `reverse-engineering/binary-analysis/functions/gcgamut.cpp.md`
- `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md`

## Bucket (5) Other (function exists but unnamed or ambiguous)
- `lore-book/reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/Atmospherics.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/MemoryManager.cpp/_index.md`
- `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/_index.md`
