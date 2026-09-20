# Save, options and startup compatibility contract

Status: active bounded contract; comprehensive compatibility recheck in progress
Last updated: 2026-09-19
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

## Rechecked static edges awaiting composed execution

Fresh inspection of `CCareer__Load` confirms that only the flag's low byte
selects its mode. Nonzero mode copies career data but restores the receiver's
previous volume words and skips entry/tail application. Zero mode takes its
audio values from absolute globals in canonical CAREER (`00660620`), a
precondition missing from an arbitrary-receiver interpretation.

The binding table is a sequence of 32-byte records terminated by ID `-1`.
Loading chooses each destination using its pre-copy active byte, then replaces
all 32 bytes without validating the incoming active flag or ID. File row IDs
do not select destinations. Altered metadata can affect later sizing/writing;
the ordinary initialized 16-active-row contract is not arbitrary-file validation.

Fresh instructions in frontend `00461e20` confirm that successful normal career
load can pass the **original entire read buffer** to the fixed-path writer at
`00461fe4`, conditional on byte `0082b5b0 == 0`. Thus immediate option skipping
does not exclude applying that save's options next boot. This complete menu
transaction has **not** been executed by the September 19 controls.

The PC save reader's documented double-close success edge is also present in
the rechecked `00515080` instructions. It checks the requested byte count, not
trailing EOF; open failure leaves `out_read` untouched. No new filesystem or
double-close runtime consequence is claimed. Its older demo-comparison results
remain inherited evidence, not comparisons rerun here.

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
