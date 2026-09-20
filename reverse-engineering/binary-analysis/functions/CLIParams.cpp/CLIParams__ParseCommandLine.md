# CLIParams__ParseCommandLine

Status: active — complete parser static audit; isolated initializer controls
Last updated: 2026-09-19
Summary: startup defaults, the 25 retail option comparisons, argument ordering and bounded side effects.
Evidence: MEASURED — pristine instructions and four executions of the unchanged initializer on controlled memory; no new retail launch or full parser execution.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: 0x00423bc0 | Source: `references/Onslaught/CLIParams.cpp` (`CCLIParams::GetParams(char *text)` parser shape)
Source File: `references/Onslaught/CLIParams.cpp` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`; Binary: `BEA.exe.original.backup` (`74154bfa…7750`).

## Identity and evidence

The saved signature remains
`void __thiscall CLIParams__ParseCommandLine(void * this, char * commandLine)`.
The complete retail body is `[00423bc0,004241a0)`, 1,504 bytes / 465 instructions,
SHA-256 `7e9869f8c52f40b3b9ac5d85e48d40389b1de09ad8c829b94be121f774b75ec6`.
`CLTShell__WinMain` supplies receiver `00662db8` at call `0051229d`.

Pinned source `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`,
[`CLIParams.cpp`](../../../../references/Onslaught/CLIParams.cpp):18–87,
corroborates the constructor/parser relationship. Its field set and option set
differ from retail; source declarations are not a recovered retail class layout.

Private evidence is under `local-data/test-runs/cli-startup-20260919/`:
`selected-bodies.json`, the complete body disassemblies, `parser-static.json`,
and `initializer-run-48y5v5ma/cli_defaults.*`. The latter contains the exact
driver, linked original bytes, inputs and complete outputs. Four initializer
cases passed; this is not a count of parser tests or retail acceptance runs.

## Startup defaults ownership

`CLIParams__InitDefaults` at `004239f0` initializes this same command-line
object. The old Unit AI attribution was wrong. Startup table slot `006220f0`
points to the already recovered wrapper `FUN_004239c0`; its call at `004239c5`
supplies `ECX=00662db8`. The complete wrapper is 22 bytes, SHA-256
`0b26668dbb326c122f227da7bed3d4e097124a037d37948ad3b342b3be96d87e`.

The initializer is `[004239f0,00423bbb)`, 459 bytes, SHA-256
`f7880354d98dbec574e79e988905adc3b588d76dcdc63e04ac4d5520f2ca1188`.
Among its defaults it:

- clears dword `+18` (global `00662dd0` on the startup receiver), the byte
  `+186` windowed guard, and trace-request dwords `+2a8/+2b0`;
- copies the autoconfig-directory literal at `00624488` to `+44`, and the
  dot literal at `00624484` to `+2d4`;
- samples byte `0066e94e` at `00423b7e`, setting `+318` to `120000` for nonzero
  or `-1` for zero; it also sets `+31c` to `-1`.

The four isolated original-code cases cover zeroed/poisoned object memory with
the `0066e94e` byte set to `0/1`. Each checks all 864 bytes of the object and
surrounding guards, the returned receiver, preserved nonvolatile registers and
stack, and the unchanged external byte. The function has no calls. The existing
`void * __fastcall(void * this)` signature/storage remain unchanged by the
[one-row metadata correction](../../../../tools/cohort-specs/cli-initializer-ownership.manifest.tsv).

The later parser `-e3` branch sets `0066e94e` but neither reruns initialization
nor recomputes `+318`. Do not translate that option into an automatic `120000`
timeout on the constructor-before-parser route. `-timeout` is a separate write.
These findings do not establish every later writer or actual startup state.

## Argument ordering

The former `if / else if` pseudocode was inaccurate. The retail body performs
independent comparisons in the order below. An option that consumes a value
advances the token pointer, and subsequent comparisons in that same iteration
inspect the consumed token. For example, the instruction path for
`-level -nomusic` attempts an integer scan and then reaches the later
music-off comparison. `-level -testeur` does not revisit the earlier testeur
comparison. These examples are static paths, not newly executed parser tests.

Tokenization tests ASCII space, not tabs or quoting syntax. It skips repeated
spaces; a trailing space can leave an empty final token. Unknown tokens fall
through without a parser diagnostic. Numeric scan results are ignored.
`-timeout`, `-soundbuffers` and `-res` check remaining-token counts;
`-level` and `-defaultoptionsname` do not. The nominal 30 slots of 256 bytes
must not be described as safely bounded: some stores precede the length/count
checks. Malformed-input behavior was not executed in this audit.

## Complete retail option map

Offsets are hexadecimal and receiver-relative unless an absolute address is
shown. The table records parser actions; an option name alone does not prove
that its downstream audio, graphics or gameplay effect works.

| Option | Comparison call | Direct action |
| --- | --- | --- |
| `-testeur` | `00423c71` | Set byte `+186=1` at `00423c7d`. |
| `-getversion` | `00423c8a` | Format version at `00423caf`, then call imported `ExitProcess` at `00423cdb`; status is `(major*100+minor)*100+patch`. |
| `-e3` | `00423ce7` | Set byte global `0066e94e=1` at `00423cf3`. |
| `-defaultoptionsname VALUE` | `00423d00` | Consume one token and scan `%s` into global `0063db18` at `00423d2d`. |
| `-level N` | `00423d42` | Consume one token and scan `%d` into `+10` at `00423d69`. |
| `-cardid` | `00423d77` | Set byte `+181=1` at `00423d83`. |
| `-backbuffer2` | `00423d90` | Set dword `+0=2` at `00423d9c`. |
| `-findgoodwater` | `00423da8` | Set byte `+182=1` at `00423db4`. |
| `-timeout N` | `00423dc1` | Consume an available token and scan `%d` into `+318` at `00423df4`. |
| `-findbadwater` | `00423e02` | Set byte `+183=1` at `00423e0e`. |
| `-playabledemo` | `00423e1b` | Set dword global `0083d448=1` at `00423e2c`. |
| `-res W H` | `00423e38` | Consume two available tokens into `+164/+168`; if either signed value is below `640×480`, reset both to `640×480`; call `0052c730` at `00423ed7`. |
| `-32bittextures` | `00423eeb` | Set dword `+2ac=0` at `00423ef7`. |
| `-dxtntextures` | `00423f03` | Set dword `+2ac=1` at `00423f0f`. |
| `-traceconsole` | `00423f1b` | Set dword `+2b0=1` at `00423f27`. |
| `-landscape0` | `00423f33` | Call `00527d00` on `008aa920` with float `0` at `00423f45`. |
| `-landscape1` | `00423f50` | Same helper/receiver with float `1` at `00423f66`. |
| `-landscape2` | `00423f71` | Same helper/receiver with float `2` at `00423f87`. |
| `-autoconfigtest [PATH]` | `00423f92` | Set dword `+3c=1`; process the optional directory and logger filename as described below. |
| `-nomusic` | `004240b4` | Set dword `+14=0` at `004240c0`. |
| `-soundbuffers N` | `004240c9` | Consume an available token and scan `%d` into `+2d0` at `00424100`. |
| `-showdebugtrace` | `0042410e` | Set dword `+2a8=1` at `0042411a`. |
| `-nosound` | `00424126` | Set dword `+188=0` at `00424132`. |
| `-skipfmv` | `0042413e` | Set dword `+298=1` at `0042414a`. |
| `-forcewindowed` | `0042415f` | If absolute guard byte `00662f3e` is nonzero, set dword `+38=1` at `0042416b`. |

The entire 23-byte resolution helper stores width/height at its receiver's
`+330bc/+330c0`; it does not create or resize a window itself. The entire
31-byte landscape helper converts the float argument to an integer, stores
it at `+0c`, and writes `1` to `+10`. Their hashes and complete bytes are
bound in `parser-static.json`; renderer acceptance remains separate.

## Windowed guard and logger boundaries

On this specimen, absolute `00662f3e` equals startup receiver `00662db8+186`.
It is BSS, with no file-backed byte, and the initializer explicitly clears it.
`-testeur` sets receiver-relative `+186`; `-forcewindowed` reads the absolute
global at `00424150`. The normal startup receiver therefore admits
`-testeur -forcewindowed` in that order; reversing them does not revisit the
first token. A different receiver must not silently be treated as the global.

The July 28 correction in
[windowed-mode-analysis.md](../../windowed-mode-analysis.md) remains valid:
patching file offset `0x262f3e` would change a resource, not this guard.
The old footer here claiming a pristine default of `1` contradicted that
correction and has been removed. The
[July retail capture](../../retail-capture-provenance-2026-07-25.md) is inherited
runtime evidence; it was not rerun for this audit. No claim about every binary
variant is made.

Both trace options are real retail comparisons, but their stores are distinct
from developer selector `+18` and either `CDebugLog` output-enable field.
The complete parser has no deliberate store to those fields. This excludes
neither malformed-input effects nor later startup writers. Pinned source
`CLIParams.cpp`:278–279 calls `CONSOLE.SetTrace(TRUE)` for `-traceconsole`;
retail instead stores the request field. Follow its actual consumers before
claiming that it enables the [reviewed logger](../string-helpers.md#debug-log-ownership-and-history--september-19).

## Autoconfig path side effects

An available next token whose first byte is not `'-'` is consumed as the
directory, copied into `+44`, and given a trailing backslash if necessary.
Otherwise the existing directory is used. The parser copies that directory
into `00662cb0`, appends `setuphistory.txt`, and calls `004d2600(path,1)` at
`00424091`. That complete helper iterates directory prefixes and reaches
imported `CreateDirectoryA` through `0055f347`. These are directory creation
attempts; their success is not checked here.

At `004240a0`, it calls `StoreField04_00441730` with setup-history logger
receiver `0066eb90` and filename pointer `00662cb0`. The complete ten-byte
setter changes only receiver `+4`. This path does not itself open/write the
log, reset its first-attempt flag, or enable either logger. A future isolated
parser experiment must intercept these filesystem calls before execution.

## Source differences and remaining work

This complete parser has no comparison for `-configuration`, `-norumble`,
`-nostaticshadows`, `-hidetail`, `-textureramlimit`, `-devmode` or `-GOD`;
the verified PE also lacks matching case-insensitive NUL-terminated ASCII
literals. In particular, source `CLIParams.cpp`:269–270 supplies a developer
option absent from these retail branches. This does not prove the absence of
other development mechanisms or later writes to the selector.

Trace-request consumers, startup initializer order beyond the demonstrated
caller chain, later developer-selector writes, complete parser execution,
and downstream presentation/audio behavior remain open. The next useful
checks are reference-backed consumer analysis and isolated parser cases with
explicit filesystem/exit interception. Full startup-to-Level-100 parity is
not established by this note.
