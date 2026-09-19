# Companion protected file bridge

Status: active — bounded native file I/O exception, Linux checks executed
Last updated: 2026-09-19
Summary: preserves existing file identity and publication protections while the standard Godot companion owns presentation and save-format behavior in GDScript.

The companion uses an explicitly disclosed C# helper because standard Godot cannot
express the existing protected-file transaction. The helper opens a bounded
snapshot or publishes caller-prepared bytes to a new path. It does not parse
career fields, calculate edits, launch the game, manage profiles or patch retail
files. Those unused AppCore profile routes throw `NotSupportedException`.
`Compatibility.cs` supplies only their compile-time stubs and the existing
10,004-byte payload bound; it is not another save implementation.

The production project links the unchanged MIT
[`SaveLabFileTransaction.cs`](../../OnslaughtCareerEditor.AppCore/SaveLabFileTransaction.cs)
and [`FileMutationSafety.cs`](../../OnslaughtCareerEditor.AppCore/FileMutationSafety.cs).
It has no reference to the AppCore assembly, `SaveLabService`, the C# save codec,
GPL rebuild code, Godot .NET or third-party NuGet libraries. A self-contained
package includes Microsoft's .NET runtime; users do not need a separate runtime
installation. This is a production C# dependency, confined to this stated boundary.

The measured standard editor is `4.8.dev6.official.8898c2b3d`. The following review
pins upstream source to full commit `8898c2b3db32adf6f92c694ffb6dac19af672e5f`:

| Required protection | Standard Godot API evidence |
|---|---|
| Open without following links; compare physical file identity and hard-link count | The bound `FileAccess` methods expose no descriptor, file identity, link count or no-follow flag. [Bound methods](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/core/io/file_access.cpp#L1015-L1119). Unix opens through `stat` then `fopen`; Windows uses `_wfsopen`. [Unix](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/unix/file_access_unix.cpp#L64-L190), [Windows](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/windows/file_access_windows.cpp#L101-L234). |
| Atomically publish only to a vacant destination | Unix `rename` can replace an entry and falls back to copy/remove across devices. Windows removes an existing file before moving. [Unix rename](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/unix/dir_access_unix.cpp#L401-L430), [Windows rename](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/windows/dir_access_windows.cpp#L313-L355). |
| Protected staging and cleanup | `FileAccess.create_temp` chooses a timestamp path, performs an ordinary write open, closes and reopens it; later cleanup removes by pathname. It does not expose exclusive creation or protected publication. [Temporary-file implementation](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/core/io/file_access.cpp#L83-L153). |
| Flush staged bytes and the destination directory to storage | `FileAccess.flush` calls `fflush`, without `fsync` or `FlushFileBuffers`; no directory-sync binding is exposed. [Unix flush](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/unix/file_access_unix.cpp#L329-L332), [Windows flush](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/windows/file_access_windows.cpp#L375-L382). |

An exclusively created directory does reserve its name: Godot calls `mkdir` or
`CreateDirectoryW`. It does not retain a protected directory handle for child
operations, establish source identity, or add no-clobber publication. The Unix
requested directory mode is `0775` before the process umask. Making a random
directory and checking links before an ordinary write therefore does not satisfy
the transaction. [Unix directory creation](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/unix/dir_access_unix.cpp#L320-L341),
[Windows directory creation](https://github.com/godotengine/godot/blob/8898c2b3db32adf6f92c694ffb6dac19af672e5f/drivers/windows/dir_access_windows.cpp#L232-L259).

These are source-level API findings. They do not claim exhaustive operating-system
acceptance. A later official Godot version needs its own review before removing
the bridge or changing the guarantee.

The bridge consumes one UTF-8 JSON line on stdin and emits one JSON line on stdout.
Save bytes travel as base64 through the pipe, never command-line arguments or
temporary request files. Requests have a 64 KiB bound and reject duplicate or
unknown fields. Both paths must be absolute `.bes` paths. The existing output
directory must already exist; the destination must be vacant.

| Operation | Request fields after `protocol: 1` | Successful response |
|---|---|---|
| `open` | `op`, `input` | `ok`, `message`, `input`, physical `identity`, `sha256`, `size`, `bytes` |
| `publish` | `op`, `input`, opened `identity`, opened `sha256`, `output`, prepared `bytes` | `ok`, `message`, `input`, `identity`, `output`, `sha256`, `size`, reopened `bytes`, `original_verified`, `verified` |

Publishing reacquires protected source and directory handles, compares the opened
identity and source hash, stages the complete supplied bytes, verifies them, and
uses the existing no-overwrite transaction. It reopens the result and verifies the
source again. GDScript must independently validate the save, the selected edit
ranges and the returned bytes before presenting success. The helper intentionally
accepts unchanged bytes for a preservation copy and does not judge format fields.

Exit codes are `0` for success, `1` for an I/O refusal, and `2` for malformed
requests. The caller must parse the response even when the process exits nonzero.
Failures return `ok: false`, `message` and `may_have_output`. Once publication may
have begun, `may_have_output: true` and `output` identify the path for inspection;
the application must not automatically delete, retry over, or announce success
for that path. An absent helper or unsupported platform makes protected operations
unavailable; there is no ordinary `FileAccess` write fallback.

`global.json` pins the existing installed SDK to `8.0.424`, and both projects pin
the runtime to `8.0.30`. Run `dotnet` with this directory as its working directory
so the SDK pin applies. Build with `dotnet publish OnslaughtToolkit.FileBridge.csproj
-c Release -r linux-x64 --self-contained true` or the corresponding `win-x64`
RID, supplying `--output`, `BaseIntermediateOutputPath` and `BaseOutputPath` beneath
a unique ignored `local-data/` run directory. Ship the whole publish directory.
The standard Godot launcher supplies the helper through `ONSLAUGHT_FILE_BRIDGE`
for development or as a `file-bridge` sibling in a package.

[`test_file_bridge.py`](../tests/test_file_bridge.py) uses owned copies of the
tracked real fixture for exact round trips, independent literal intended-edit
diffs, malformed requests, changed source bytes and identities, alias conflicts,
existing destinations and game-tree refusal. Supply `--bridge` with the executable
and an ignored `--output-root`. Build the separate
`OnslaughtToolkit.FileBridge.TransactionTests.csproj` with its own intermediate and
output directories, then pass its executable as `--race-harness`. The harness
exercises six Linux publication/failure cases through existing internal hooks.
Those hooks are absent from the production protocol. Test copies remain in the
reported ignored run directory; the tracked fixture is hash-checked unchanged.

The executed Linux checks cover the linked descriptor-relative no-follow source
opens, unnamed staging, last-moment destination conflicts, directory replacement,
source changes during staging and unnamed-stage cleanup. They do not prove power
loss behavior. Windows remains pending actual Windows execution. Its retained
implementation locks ancestors and verifies file identity, but releases staging
quarantine and closes the handle before its path-based move, then verifies the
published identity; this existing handoff is not claimed as Linux-equivalent
runtime evidence. Cross-exporting or inspecting a Windows package does not resolve
that acceptance requirement.
