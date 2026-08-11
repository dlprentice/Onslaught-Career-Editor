# PC demo/retail FMV and startup lineage

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — five independently bounded function bodies in the exact
PC demo and pristine retail executable, mapped callsites, global reads/writes,
retained controller interfaces, and demo/retail file inventories; UNKNOWN —
live playback timing, codec/device behavior, and the meanings of four other
FMV backend flags.
Verdict: the demo and retail executables deliberately differ in startup policy.
The demo is compiled as playable-demo by default, contains an American-English
fallback probe, and carries a per-playback `can_skip` field through both FMV
input paths. Retail makes playable-demo an opt-in command-line state, removes
the `can_skip` field and both guards, and adds demo-aware loading-resource
selection around level entry.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable result is
[`pc-demo-retail-fmv-startup-lineage-2026-08-11.tsv`](pc-demo-retail-fmv-startup-lineage-2026-08-11.tsv).
It is 3,192 bytes with SHA-256
`ba3c995246cf556316d1b7d78ce529190100db550ac5862750a818382da9329d`.
The five retail bodies total 3,143 bytes / 935 instructions; their complete
demo bodies total 3,250 bytes / 958 instructions. Body SHA-256 values and both
exact extents are retained in the table. This independently closes five of the
65 address-mapped bodies that the first whole-executable census left changed or
incompletely bounded.

## The demo is compiled as playable-demo

Both parsers contain the exact `-playabledemo` comparison. What they write is
different:

| Build | Global | Initial storage | Parser behavior |
| --- | --- | --- | --- |
| Demo | `0x00633B1C` | file-backed `.data`, initial dword `1` | writes `1` again |
| Retail | `0x0083D448` | zero-initialized `.data` tail/BSS | writes `1` when the flag is present |

The surrounding cross-build references move together: frontend, game,
resource, and shell code reads demo `0x00633B1C` where the paired retail code
reads `0x0083D448`. The demo command-line branch is therefore not writing an
unrelated table entry; it reasserts a build state already initialized to one.
Retail turns the same mode into an opt-in launch state.

This is stronger than inferring edition from a filename. It is an executable
policy difference joined through the parser and its consumers.

## Demo-only American-English fallback

The first block in demo `CLIParams__ParseCommandLine @ 0x00423B60` attempts to
open `data\\language\\french.dat` with mode `rb`. Success closes the stream.
Failure writes `1` to demo global `0x0083EC50`. A second demo-only parser branch
does the same for `-us`.

The global's identity is independently fixed by paired consumers:

- demo `CText__Init @ 0x004F2270` reads `0x0083EC50`; retail
  `CText__Init @ 0x004F21F0` reads `g_UseAmericanEnglish @ 0x0083D990` at the
  corresponding instruction;
- demo shell initialization reads `0x0083EC50` before choosing language zero;
  retail reads `0x0083D990` in the same policy position;
- the retail `CText` implementation uses that state to substitute
  `data/LANGUAGE/american.DAT` for ordinary English.

Retail `CLIParams__ParseCommandLine @ 0x00423BC0` has neither the French-file
probe nor a `-us` comparison, and the bounded retail executable has no write to
`0x0083D990`. The demo thus carries a distribution-specific language fallback
that retail removed from its parser. This does not establish why a particular
demo package omitted or retained language files; it establishes the executable
fallback itself.

## `CFMV::ReceiveButtonAction` recovered

Retail `0x004656E0` was previously saved only as
`CFMV__VFunc_3_004656e0`. Its `RET 0x0C` and vtable position match the first
method added by retained `IController` after `CMonitor`:

```cpp
virtual void ReceiveButtonAction(CController* from_controller,
                                 int button,
                                 float ana_val) = 0;
```

The body then supplies semantic confirmation. In both builds:

- button `7` (`BUTTON_SKIP_CUTSCENE`) sets `CFMV+0x08 = 1` and clears the
  current playback/attract global;
- button `66` (`BUTTON_BREAK_ATTRACT_MODE`) does the same only when the
  loading/attract gate at `CFMV+0x0C` is nonzero;
- every other button returns without a write.

The source authority is `references/Onslaught/Controller.h`, SHA-256
`74fd5ad844b36fa9ccf470c591014e94b6306e80046a314a00215b6cc65f679f`.
The name is a semantic correction for the tracked ledger; this report does not
claim that the Ghidra project has already been renamed.

## Retail removed the per-playback skip gate

Three independently bounded bodies triangulate the same layout change.

| Role | Demo | Retail |
| --- | --- | --- |
| Wrapper | stores final explicit argument at `CFMV+0x10` | no store |
| Controller callback | returns immediately when `CFMV+0x10 == 0` | no leading guard |
| DirectX backend subobject | begins at `CFMV+0x14` | begins at `CFMV+0x10` |
| Backend controller polling | guarded by forwarded `can_skip` argument | unconditional |

The wrapper is demo `0x00465680` / retail `0x00465640`. The DirectX backend is
demo `0x0053F7A0` / retail `0x0053F190`. Apart from the three-instruction demo
guard and the four-byte subobject shift, the backend retains the same control
shape. It polls three controller state slots, requests stop when any is active,
and clears the same build-relative playback global.

This makes the wrapper's final explicit argument concrete: in the demo it is
`can_skip`, not an opaque backend flag. The demo copyright call at `0x004EFFE8`
passes zero as that final argument. Retail's corresponding copyright call at
`0x004EFE0B` also passes zero, but the retail wrapper and both retail input
paths ignore the former gate. Static consequence: retail accepts button 7
during that playback where the demo does not. Runtime input delivery and movie
duration remain unmeasured.

## Startup content and level-loading changes

The demo executable has four code references that push the exact `publisher`
FMV name (`0x004EFF3B`, `0x004EFFF8`, `0x004F0068`, and `0x004F04CC`) into the
mapped full-screen wrapper. The extracted demo also contains:

| Demo-only file | Bytes | SHA-256 |
| --- | ---: | --- |
| `BattleEngine/EXE/publisher.vid` | 1,432,996 | `c251f4be8ab7f2ac5d4f6b952ca44d0cf5aadd7552ad61725420009a6f0e79ba` |
| `BattleEngine/EXE/fe_publisher.tga` | 12,827 | `5a0a8f79a7a8ec45810fa98197be7f238395ec2b5af3d3f1ee59b42670d87cdb` |

Neither filename exists in the canonical retail extraction. The four
references are callsite facts; they do not imply that all four branches execute
in one launch.

Retail `CGame::RunLevel @ 0x0046E240` adds a different demo-mode adaptation
that demo `0x0046E120` lacks. When the retail playable-demo global is nonzero,
it sets `DAT_0066E8C0 = 1`, calls `CConsole::SetLoading`, then clears the byte.
Known consumers use the pair of flags to select the demo loading resource path
and use `DAT_0066E8C0` to select alternate loading text. This is a deliberately
short loading transaction, not a persistent game-mode flag.

## Boundary and next use

The recovered claims are object layout, branch policy, button identities,
global dataflow, and file/callsite presence. They do not prove DirectShow
filter selection, playback performance, controller sampling timing, rendered
frames, or that PE timestamps establish chronological order.

The practical RE value is larger than these five functions. The demo can now
refute interpretations of nearby startup and frontend bodies with known
distribution policy, and its initialized playable-demo global gives a data
anchor across many corresponding consumers. The next useful instrument is to
bound another coherent group among the remaining 60 changed bodies rather than
repeat normalized-signature searching over these resolved functions.
