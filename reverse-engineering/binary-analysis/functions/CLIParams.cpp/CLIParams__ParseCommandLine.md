# CLIParams__ParseCommandLine

Status: active — complete parser static audit; bounded original-code execution
Last updated: 2026-09-19
Summary: startup defaults, the 25 retail option comparisons, argument ordering and bounded side effects.
Evidence: MEASURED — pristine instructions, four initializer controls and 47 isolated parser cases; no retail startup or gameplay acceptance.
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
cases passed. The separate parser experiment below adds 47 cases with explicit
OS/printf interception; neither count describes retail acceptance runs.

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
comparison. Both cases now pass with the unchanged parser and original scanner
in the isolated experiment below.

Tokenization tests ASCII space, not tabs or quoting syntax. It skips repeated
spaces; a trailing space can leave an empty final token. Unknown tokens fall
through without a parser diagnostic. Numeric scan results are ignored.
`-timeout`, `-soundbuffers` and `-res` check remaining-token counts;
`-level` and `-defaultoptionsname` do not. The nominal 30 slots of 256 bytes
must not be described as safely bounded: some stores precede the length/count
checks. Overlong tokens and excess-token memory behavior were not executed.

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
retail instead stores the request field. The bounded consumer review below
identified no path from either request to the
[reviewed logger](../string-helpers.md#debug-log-ownership-and-history--september-19).

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
log, reset its first-attempt flag, or enable either logger. The isolated
experiment intercepts the filesystem boundary and confirms the prefix order,
filename store and logger preservation for its selected cases.

## Isolated parser execution — September 19

`python local-data/test-runs/cli-startup-20260919/parser_control.py` passed
**47 bounded cases**. Accepted stem:
`parser-run-m20ei0zy/cli_parser` under that same private owner. Receipt SHA-256:
`e6dca9f618862716ac0c129f151335938b3d81e8e72e441146a4a499173a1296`;
ELF SHA-256:
`9d785de30b3e49cb1a24ad7b38b2fa5f40474a9d894ae23336a151497f5104cf`.

The complete initializer and parser, stack probe, case-insensitive comparison,
numeric/string scanner and required helpers execute unchanged at their original
addresses. All 21 admitted code envelopes match pristine bytes: 6,017 named
body bytes plus the 11 alignment bytes inside the two-range `strchr` envelope.
Original character tables and default locale data are retained. Numeric scanning
is original retail code, not an authored approximation of `sscanf`.

Each case compares 8,400 captured bytes before and after parsing: both settings
objects and their guards, both complete logger extents, command input, filenames,
selected globals and the resolution/landscape helper outputs. Forty-six cases
also check normal-return stack/nonvolatile registers. The version case deliberately
leaves through an intercepted nonreturning `ExitProcess` boundary.

Consequential controls establish:

- Mixed-case options match; tabs do not split tokens and quotes are literal.
- Reversing `-testeur -forcewindowed` changes admission. An alternate receiver's
  `+186` cannot substitute for the separately read global guard.
- `-e3` sets its global byte without changing the initialized timeout;
  `-timeout 42` separately changes that timeout.
- Failed `%d` conversion preserves the destination but still consumes the token.
  Thus `-level -nomusic` disables music, while `-level -testeur` does not enable
  the earlier option. `-defaultoptionsname -level 110` handles both consuming
  branches in one iteration.
- For `-res 800 -showdebugtrace`, failed height conversion preserves the authored
  preloaded height of 720, and the later trace comparison still runs. This does
  not make 720 a retail startup default. A width below 640 instead resets both
  dimensions to 640/480.
- Autoconfig records each directory prefix in order, keeps a following option
  separate from the optional path, and stores the composed filename without
  enabling logging. `-getversion -nosound` exits before the sound option.

`printf`, `CreateDirectoryA`, `GetLastError` and `ExitProcess` are authored
recording boundaries. No actual formatting, directories or Windows exit behavior
are claimed. The false-directory-result control supplies last error zero; it
does not cover ordinary nonzero Win32 errors or errno translation. The child
admits only Linux read/write/exit syscalls; a separate forbidden-`getpid` control
terminates with SIGSYS. No omitted locale/heap/file helper was needed by the
accepted bounded cases. Snapshot preservation covers the recorded regions,
not all process memory. Independent review checked the saved ELF and all outputs
without rerunning them. Earlier harness failures and the narrower 45-case run
remain separate from this accepted receipt.

## Developer selector and trace consumers — September 19

`00662dd0` is the settings object's `+18` developer selector, not frontend state
or a demo/intro flag. Its initializer clears it at `00423a25`. Static retail
branches correspond to `CLIPARAMS.mDeveloperMode` in pinned source
`actor.cpp`:87–109, `BattleEngine.cpp`:1259–1262, `eventmanager.cpp`:400–409,
`FrontEnd.cpp`:188–203 and `game.cpp`:2672,2710,3360,3593.

All ten occurrences of this absolute address in the specimen decode as reads:

| Read instruction | Bounded consumer behavior |
| --- | --- |
| `0040164f` | Zero skips actor velocity diagnostics. |
| `00408195` | Nonzero, together with zero receiver vulnerability, bypasses the water-death virtual call after the altitude gate. |
| `00441715` | Exactly one enables the logger during history reset; other values preserve enablement. |
| `0044b7e0` | Exactly one admits scheduler overflow-order diagnostics. |
| `00466775` | Nonzero changes the first-run frontend branch. |
| `0046f945` | Exactly one admits the developer win-level branch. |
| `0046fa39` | Exactly one, with game state at least three, admits the developer lose-level branch. |
| `00470687` | Zero skips developer diagnostic rendering. |
| `00471614` | Zero skips additional debug output. |
| `004bbda0` | Exactly one admits this function body; its full semantics were not re-audited here. |

`trace_consumers.py` preserves complete enclosing-body envelopes, decoded reads
and startup calls in `trace-consumers.json`, SHA-256
`db29480702a78a37d3242498124dbb13050860afb7838610eb271aaa8fb46451`.
The PE contains no absolute address-dword occurrence for `00663060` (`+2a8`),
`00663068` (`+2b0`) or their interior bytes. The base address `00662db8`
occurs only as initializer/parser receiver and a read of its first dword.
No consumer of either trace request, or later deliberate writer of `+18`, was
identified. This bounded absence claim excludes neither computed pointers,
bulk writes, malformed-input effects nor external changes.

Initializer table slots `006220f0/0062218c/00622190` point to the CLI, debug-log
and setup-history initializers. Debug enable starts at zero; history enable
starts at one. WinMain's parser call at `0051229d` precedes its `004efb10` call
at `005123c3`. In that latter body, calls at `004efb58/004efb65/004efb6f`
initialize the pointer pool, reset the debug logger and reset setup history,
respectively. With selector zero, both resets preserve their prior enable flags.
These are static call relationships plus the earlier isolated logger controls,
not a new whole-startup observation or a proof of logger state at every warning.

Two neighboring fields must remain separate from this developer selector:
`+3c` (`00662df4`) is the autoconfig-test flag and also causes
[`IsCheatActive`](../FEPSaveGame.cpp/IsCheatActive.md#autoconfig-identity-correction--september-19)
to return true early. `+294` (`0066304c`) is a distinct frontend startup
override, initialized to `-1`; it is not the parser's `-level` destination at
`+10` (`00662dc8`). The latter is read at `004f034a` and forwarded to the game
call at `004f036e`. `selector-neighbors.json` binds the additional complete
bodies, SHA-256 `142ba92383897d598d11086bac0894d6d9bff568c1d016dee512a437d12113e2`.

## Source differences and remaining work

This complete parser has no comparison for `-configuration`, `-norumble`,
`-nostaticshadows`, `-hidetail`, `-textureramlimit`, `-devmode` or `-GOD`;
the verified PE also lacks matching case-insensitive NUL-terminated ASCII
literals. In particular, source `CLIParams.cpp`:269–270 supplies a developer
option absent from these retail branches. This does not prove the absence of
other development mechanisms or later writes to the selector.

No active trace-request consumer or later developer-selector writer has been
identified. Full startup ordering and actual warning/logger state, nondefault
locale and nonzero Windows error paths, and downstream presentation/audio
behavior remain open. The startup path supplies the next evidence for the
pointer-pool warning and complete-shot RNG investigation; the isolated parser
cases do not establish full startup-to-Level-100 parity.
