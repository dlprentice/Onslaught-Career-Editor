# CPauseMenu__ResumeGameAndPersistOptions

> Address: 0x004d06e0 | Source: PauseMenu.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (read-back verified in mutation snapshots)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Pause-menu resume/exit helper that serializes current `CAREER` state and persists options/defaultoptions side effects before returning gameplay control to the frontend/game loop.

## Signature
```c
// Live read-back signature (wave217 snapshot)
void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * param_1);
```

## High-Confidence Behavior Contract

1. Triggered from pause-menu dispatch flow (resume/exit path).
2. Participates in the save/persist chain documented in `CCareer__Save` side-effect notes:
   - `CCareer__Save` buffer serialization.
   - Conditional `PCPlatform__WriteSaveFile` slot write.
   - `CFEPOptions__WriteDefaultOptionsFile` (`defaultoptions.bea`) update.
3. Returns control to frontend/game state transition path after persistence branch handling.

## Evidence

- `scratch/deep_semantic_tail_2026-02-27/all_after_wave217.tsv` line 1820:
  - `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * param_1)`
- Caller anchors in pause-menu cluster:
  - `scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave22_prep/xrefs.tsv` lines 35-36.
- Save/defaultoptions side-effect chain references:
  - `../Career.cpp/CCareer__Save.md`
  - `../../high-impact-call-chain-appendix.md`

## Related

- [PauseMenu__Init](./PauseMenu__Init.md)
- [CCareer__Save](../Career.cpp/CCareer__Save.md)
- [CFEPOptions__WriteDefaultOptionsFile](../FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md)
