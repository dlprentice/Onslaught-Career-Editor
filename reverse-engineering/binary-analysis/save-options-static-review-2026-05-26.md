# Save and options static contract

Status: active bounded contract for retail layout, serializer ownership, and product safety.

## Established surface

| Area | Current evidence | Boundary |
| --- | --- | --- |
| Save container | Retail files are `10004` bytes, start with version `0x4BD1`, and store `CCareer` from true-view base `0x0002`. `CCareer__Load`, `CCareer__Save`, and `CCareer__GetSaveSize` own the binary path. | Static ownership does not prove every frontend save-menu path. |
| Career data | The mapped body includes 100 nodes, 200 links, 300 Goodie slots with 233 displayable entries, five packed kill counters from `0x23F6`, and raw float ranks. | In-game presentation and unlock animation remain runtime behavior. |
| Options | Flags begin at `0x249E`, control entries at `0x24BE`, and the options tail is `0x56` bytes. `OptionsTail_Write`/`Read` and the binding helpers own this structure. | Hardware/input behavior needs focused runtime evidence when claimed. |
| Frontend persistence | `CFEPLoadGame__DoLoad`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, and `Platform__AsyncSaveCareer` connect frontend actions to serialization. | Static xrefs do not establish filesystem timing. |
| Product behavior | `BesFilePatcher` validates size/version, refuses in-place output, preserves unknown and reserved regions, supports scoped options copy, and blocks career writes to options-like files unless explicitly overridden. | These guarantees remain protected by focused AppCore/UI tests. |

## Canonical owners

- [Save format](../save-file/save-format.md)
- [Structure layout](../save-file/struct-layouts.md)
- [Career graph](../save-file/career-graph.md)
- [Grade system](../save-file/grade-system.md)
- [Goodies contract](../save-file/goodies-system.md)
- [Kill tracking](../save-file/kill-tracking.md)
- [`CCareer__Load`](functions/Career.cpp/CCareer__Load.md) and [`CCareer__Save`](functions/Career.cpp/CCareer__Save.md)
- [Control bindings](functions/Controller.cpp/ControlBindings.md)
- [`CFEPOptions__WriteDefaultOptionsFile`](functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md)
- [`CPauseMenu__ResumeGameAndPersistOptions`](functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md)
- [`BesFilePatcher.cs`](../../OnslaughtCareerEditor.AppCore/BesFilePatcher.cs)

## Open boundaries

- copied-profile runtime save/load and controller-remap behavior;
- exact source-layout identity for every object field;
- complete Goodies wall/model-viewer behavior;
- rebuild parity.

Contradictory controlled runtime evidence or a reviewed static correction may refine this contract. Historical queue completion and readiness artifacts are not independent authorities.
