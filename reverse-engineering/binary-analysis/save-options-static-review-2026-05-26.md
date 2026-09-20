# Save, options and startup compatibility contract

Status: active bounded contract; comprehensive compatibility recheck in progress
Last updated: 2026-09-20
Summary: independently rechecked startup/serialization behavior and explicit remaining save/settings compatibility boundaries.
Evidence: MEASURED — selected pristine instructions and the isolated execution below; inherited subsystem summaries remain subject to recheck.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## September 19 independent recheck

The private `local-data/test-runs/save-startup-20260919/` owner contains selected
complete-body disassembly and `startup_control.py`. The accepted
`startup-run-o3zcj6ov/startup` receipt is
`9639d263d59a96532c7f182d1e0b209f20b4faa90bc9e4acc519c8dd938a45f7`.
Seventeen scenarios execute unchanged original startup, parser, career load,
career reset, binding initialization and options-tail reader bodies. After
startup returns through an intercepted graphics-create failure, the driver
**separately invokes** original Save, SaveWithFlag and the small default-options
writer. Those later calls do not imply that startup itself saves a file.

The input is the real tracked `gold_career_save.bin`, SHA-256
`0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`;
negative controls modify only private in-memory derivatives. Original fixture
and executable identities are checked before and after execution. Complete
10,004-byte serializer outputs, their guards, selected before/after state and
source-buffer immutability are compared. This is independent execution of retail
code, not a reconstruction serializer testing itself.

| Question | Rechecked result | Evidence boundary |
| --- | --- | --- |
| Which settings file boots? | WinMain reads the CLI-writable name at `0063db18`; `-defaultoptionsname profiles/test.cfg` changes that read. The small writer independently opens the fixed `defaultoptions.bea` literal at `0063fc74`. | Original parser/WinMain/writer executed; file operations intercepted. |
| What rejects a file? | WinMain calls Load only after the requested byte count is read. Load checks the low 16 bits of `[00623e24] + 0x4bc0`; the pristine global is 17, yielding `0x4bd1`. It has no length argument or checksum check. | Missing, empty, short and wrong-version startup cases executed. No claim that the raw loader safely admits arbitrary buffers. |
| Does boot restore a campaign? | WinMain calls Load with flag zero, then calls Blank regardless of open/read/load success. Blank resets authored campaign nodes and progression while preserving volumes and control options. It does not erase the whole career record. | Complete direct reset state compared; final Goodie recomputation intercepted. |
| Are settings copied unchanged? | The tail reader copies some raw dwords, converts six signed integers through float32/x87, normalizes its final two bytes to booleans, and calls preset/language and audio actions. | Actual reader, packed-mode helper and numeric setter executed; downstream actions recorded but intercepted. |
| Is tail `+28` a device ordinal? | No: it packs width, height and a pixel-format class. Matching-current, matching-second, unavailable and empty mode-list cases have distinct results. A nonempty changed-mode lookup clears the packed key's low 16 bits after selecting a match or fallback. | Original lookup executed with explicitly authored mode capabilities, not host GPU enumeration. |
| Does Save only copy bytes? | Save appends the current active binding rows and current tail globals. The tail writer also refreshes packed-mode global `0066061c`. SaveWithFlag first changes live career `+2488` to one. | Both complete outputs compared in all 17 scenarios; no file publication. |
| Does writer return imply durable success? | The small writer ignores both `fwrite` and `fclose` results. Only open failure reaches its logger. | Success, open failure, short-write and close-error return values supplied to unchanged writer code. Actual filesystem effects untested. |

All system, allocator and graphics calls are intercepted. Audio, preset,
language, diagnostics and final Goodie actions remain explicit boundaries.
The Linux child admits only read/write/exit syscalls; a forbidden-call negative
control terminates with SIGSYS. These controls establish neither real desktop
startup nor full save compatibility. Exact commands and intermediate failures
are in [VALIDATION.md](../../VALIDATION.md#original-save-and-startup-controls--september-19).

## Original menu load and next-startup composition

`menu_control.py` in the same private owner passed 20 cases through unchanged
`CFEPLoadGame__DoLoad`, PC storage-info/read, name-conversion, career Load and
default-options writer bodies. Accepted stem `menu-run-47t_hlhy/menu`, receipt
`720608d9374496a1341259191136537c6a903c725a468e1eafb60c8092159211`.
This replaces the earlier static-only status of the normal load/publication edge.

The live career receives the file's data with its two packed counter bytes
normalized, but retains its previous volumes; bindings and selected tail
globals stay unchanged. If the post-page-call low byte at `0082b5b0` is zero,
the original writer receives **every byte of the original read buffer**.
Nonzero higher bytes alone do not suppress the write. File open/write/close
failures do not change the menu caller's success path. Actual page behavior,
latest-world selection, text/audio services and filesystem effects remain
intercepted rather than validated.

`menu_to_startup.py` then feeds the successful case's captured payload unchanged
to the existing original WinMain executable. Receipt
`533c72da0958207b18b1eb5ea20ec378598226a3c0ca5065451d71906f2f3639`,
stem `menu-boot-qssmorvv/chain`. Menu-live volumes remain `0.25/0.75`, whereas
the next startup reads the fixture's `0.6/0.4` bits, applies its bindings and
sensitivity, and resets campaign progress. The handoff assumes successful
storage; it does not prove durable publication, real process restart or audio
playback. The startup driver's later separately invoked serializers/writer are
outside this chain claim.

The PC reader controls also reproduce name narrowing to low bytes, filename
aliasing/truncation for authored wide strings, name-based identity despite
changed device/slot, one close on a short read and two closes on a complete
read. Supplied close errors do not alter full-read success. Upstream keyboard
admission and the actual CRT consequences remain open.

## Control preset recheck

Twenty separate original-code preset controls pass with original table
initialization and authored detected-count/enable flags. The existing
[binding contract](functions/Controller.cpp/ControlBindings.md#independently-rechecked-preset-behavior--september-19)
now replaces the ambiguous "scheme layers" description: the initialized image
has one 16-row preset group plus a joystick fallback table. Scheme 1 copies
matching rows; higher schemes may substitute the first two enabled devices.
With only one enabled device on that path, secondary-slot field0 is cleared
across all 47 runtime rows, including the 31 normally omitted from saves.

Those direct controls are now complemented by the composed loader experiment
below. Missing/duplicate/inactive/early-sentinel controls bound table lookup
behavior, not arbitrary malformed-save admission.

## Original loader, mutable bindings and later serialization

`load_preset_control.py` passed 19 cases through unchanged Load, TailRead,
ApplyPreset and their actual table helpers, followed by original Save/TailWrite.
Accepted stem `load-preset-run-k8m1uqgd/load`, receipt
`2235a9b50f4d537e1ec45c5fabc2c491ca6c73450d59d0608496e2c2fcab8610`.
The driver measures the actual tail-end ESI at the language-call boundary and
compares complete selected state, serializer output and guards.

Only the flag's low byte selects its mode: `0x100` applies bindings and tail;
`1` and `0x101` preserve receiver volumes and skip them. A separate receiver
control confirms that zero-mode audio calls still use canonical CAREER's
absolute volume globals, rather than the selected receiver's copied values.

The binding table is a sequence of 32-byte records terminated by ID `-1`.
Loading chooses each destination using its pre-copy active byte, then replaces
all 32 bytes without validating the incoming active flag or ID. File row IDs
do not select destinations. Altered metadata can affect later sizing/writing;
the ordinary initialized 16-active-row contract is not arbitrary-file validation.

| Private input change | Observed direct same-process result |
| --- | --- |
| First saved row becomes inactive, custom scheme | Size changes `10004 → 9972 → 9940` across two loads of the same input. The second tail starts at `0x269e`, 32 bytes earlier than `0x26be`. |
| First saved ID becomes `-1` | The first load still consumes the ordinary 16 rows. Later table walks stop at the new first sentinel: size becomes 9492 and the next load reads its tail at `0x24be`. |
| First saved row becomes inactive, scheme 1 | Actual preset application restores that row; both loads retain size 10004 and tail start `0x26be`. |
| First saved ID duplicates the next row | Both loads retain the ordinary size and tail start in this tested custom-scheme case. This does not make duplicate IDs equivalent under later preset lookup. |

These are deliberately changed private derivatives of the real fixture.
Repeated direct calls do **not** establish drift across fresh startups, which
run the binding initializer again. Final Save consumes the resulting live table;
it is not fed back into Load in this experiment. Language/audio/latest-world
actions remain intercepted here. No arbitrary malformed-file safety is claimed.

## Original language application and persistence

`language_control.py` then replaces the language hook with original
`CFrontEnd__SetLanguage`, cleanup and `CText__CopyFrom`, keeping the real
Load/TailRead/preset/Save chain. Sixteen cases pass; accepted stem
`language-run-n__ph8sw/language`, receipt
`016b415f9846f13e02fc2c290e5c96c52e01f1af9cc245d30d119cf507fde5dd`.
The five cache slots and one adjacent-state negative control use explicitly
authored headers/buffers. They are not actual loaded language files.

TailRead's unsigned 16-bit selector chooses a cached object through unchecked
`frontend + 0xbf40 + selector * 0x30` arithmetic. The copy frees a nonnull
destination buffer, copies selected header fields, allocates/copies exactly the
source byte count, and rebases two pointers. Destination `+20..+2f` survives;
the old claim that every object field is copied was incorrect. Reapplying the
same selector repeats the free/allocation/copy. Sizes 0, 1, 3, 4, 7 and 17
exercise the dword and trailing-byte copy paths. See the precise
[copy contract](functions/text.cpp/CText__CopyFrom.md).

The active language field is copied from the source header's `+1c`; only after
that operation returns does TailRead store the input selector to `0066305c`.
Save writes the **low word of active header `0083d97c`**, not that mirror.
An authored selector 2/header-language 4 case therefore saves 4; a full header
value `0x12345678` saves `0x5678`. These controls distinguish the two owners,
not legitimate localization configurations. Index 5 and out-of-buffer pointer
controls expose missing bounds checks without establishing supported inputs.

The original cleanup's null-object path executes; nonnull destruction remains
unresolved. Allocator/free and audio services are intercepted. Fresh static
inspection of `CText__Init` confirms that it sets the language field before
opening or parsing the file, and that its American override/invalid-selector
fallback can select a different filename without changing that field. Thus
neither the input mirror nor header language proves which text actually loaded.
Real language-file initialization and localized menu acceptance remain open.

The subsequent [initializer inspection](functions/text.cpp/CText__Init.md)
also corrects the failure boundary: an Open failure reaches the fatal helper
before the apparent cleanup tail. Its call chain ends at the confirmed
`ExitProcess(1)` import. Successful Open does not prove a complete read: Init
ignores the actual copied count, and an unknown tagged format has a path that
sets the loaded flag after a returning diagnostic/Close. Those are fresh static
findings, not executed failure results. Six preserved language files have been
read and identified for the next controlled original-parser experiment.

## Rechecked static edges awaiting further execution

The PC save reader checks the requested byte count, not trailing EOF; open
failure leaves `out_read` untouched. Its older demo-comparison results remain
inherited evidence, not comparisons rerun here.

## Implementation-consumer findings

The retained `BesFilePatcher.ApplyOptionsTailOverrides` clamps mouse sensitivity
to `0.1..5.0`. Fresh bytes place the image default at `7.0`, and the retail menu
setter at `004cefe0` writes `(index + 1) * 3.0`; the construction bounds yield
`3, 6, ..., 63`. The tail reader preserves the raw sensitivity dword. Therefore
that editor's range is a narrower application policy, not the retail range.
The `OptionsD3DDeviceIndex`/`D3DDeviceIndex` consumer names similarly misdescribe
the packed display-mode key. No companion/rebuild code was changed in this RE pass.

## Inherited surface and routing

The table below routes earlier work. Items outside the recheck above are not
newly verified merely because they remain documented here.

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
