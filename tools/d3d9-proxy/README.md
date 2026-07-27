# bea-d3d9-proxy

A passive Direct3D 9 draw-call recorder for a **copied** Battle Engine Aquila
build. It records, per frame and in draw order, every draw call with the render
state in force and **the vertex data** — which for this title means literal
screen coordinates.

## Why this exists

There is no HUD element *position* table anywhere in the shipped data. Sizes are
authored; positions are computed in code, in subsystems that have no counterpart
in the GPL drop. Every HUD coordinate in the reconstruction has therefore been
recovered by fitting pixels, which is slow, and which has produced at least one
conclusion that had to be withdrawn.

RenderDoc cannot help: its `renderdoc.dll` ships one D3D9 source file against 27
for D3D11, and carries the literal string
`Trying to get IDirect3DDevice9 - not supported.` Its log was byte-identical
before and after the game presented hundreds of frames, so it never wrapped a
device.

`d3d9` is **not** in `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs`,
so a `d3d9.dll` in the application directory wins the load. `BEA.exe` imports
`d3d9.dll!Direct3DCreate9` statically, so the proxy is in the chain from process
start. No executable is modified.

## Use

```powershell
./build.ps1                                   # -> build/d3d9.dll (PE32, i386)
./Test-Proxy.ps1                              # self-test, does not touch the game
./Run-D3D9Capture.ps1 -Seconds 25 -MaxFrames 120
./Run-D3D9Capture.ps1 -NoLog                  # proxy present but inert
```

`Run-D3D9Capture.ps1` copies the DLL in, runs the game, and removes it again in a
`finally` block, so the canonical capture target stays byte-identical between
runs and existing parity captures stay valid. It refuses to run against anything
that looks like an installed game, refuses to overwrite an existing `d3d9.dll`,
and reports the `BEA.exe` hash before and after.

The game is closed by posting `WM_CLOSE` to its own `HWND`. No global synthetic
input is ever sent — see `AGENTS.md`.

## Configuration

The DLL is **completely inert** unless one of these is set. With neither, it
forwards every call and wraps nothing.

| Variable | Default | Meaning |
|---|---|---|
| `BEA_D3D9_LOG` | — | Log file path. Setting this enables capture. |
| `BEA_D3D9_CAPTURE` | — | Any non-zero value enables capture to `G:\bea-d3d9-capture\d3d9-<stamp>-<pid>.log`. |
| `BEA_D3D9_FIRSTFRAME` | `0` | First frame to record. |
| `BEA_D3D9_MAXFRAMES` | `300` | Frames to record, then the log closes itself. |
| `BEA_D3D9_MAXVERTS` | `64` | Draws with more vertices than this are refused with `too-many-verts nv=… cap=…` rather than dumped. **In-level mesh draws will exceed 64 constantly** — raise it, or expect a log of refusals. |
| `BEA_D3D9_NOVERTS` | `0` | Record draws and state but no vertex data. Each draw still gets a `noverts-configured` refusal line. |
| `BEA_D3D9_STRICTCOV` | `0` | `1` turns a provisional-coverage warning into a refusal, so nothing whose written extent was inferred is ever decoded. |
| `BEA_D3D9_FAULT_NOCLEARBIND` | `0` | **Fault injection, self-test only.** Stops a dying buffer wrapper retracting itself from the devices holding it, to prove the generation check refuses a dangling binding. Any log produced with it set is stamped `# FAULT-INJECTION`. |

If the log cannot be opened the proxy falls back silently to pure pass-through.
It never creates a window, dialog, console, thread or socket, and never takes
focus.

## Log format

One record per line.

```
D <frame> <draw> <kind> prim=… primc=… verts=… fvf=… s0=(vb=…,off=…,stride=…)
          tex0=<ptr>:<w>x<h>:fmt<n>:lv<n> tex1=… ab=… sb=… db=… bop=… at=… aref=…
          afunc=… z=… zw=… zf=… cull=… lit=… fog=… tfactor=… s0.cop=op/arg1,arg2 …
V <frame> <draw> <i> xyzrhw=(x,y,z,rhw) diff=0xAARRGGBB t0=(u,v)
V <frame> <draw> - none <reason> [detail]   nothing recorded, and exactly why
V <frame> <draw> - warn <reason> [detail]   recorded, but qualified
I <frame> <draw> idx=…                 index run for an indexed draw
I <frame> <draw> - none <reason> …     same refusal grammar for the index run
L VB|IB wrap=… off=… size=… mapped=… flags=0x…   Lock
U VB|IB wrap=… cov=[lo,hi),[lo,hi)?    Unlock, and the resulting range list
VB|IB create <real> wrap=… gen=… …     buffer created through the proxy
VB|IB retire wrap=… real=… gen=… …     wrapper destroyed; STILL-BOUND if bound
P <frame> draws=<n>                    Present
S <frame> begin|end                    BeginScene / EndScene
C <frame> …                            Clear
! <frame> …                            state-block events, shadow invalidation
# refusals total=<n> warnings=<n>      tally by reason, at window close and detach
```

A `DIP` record carries `basevtx=`, `startidx=` **and** `minvtx=`. All three are
needed: the vertex run starts at `basevtx + minvtx`, while the values on the `I`
line are relative to `basevtx` alone. Without `minvtx` the `I` and `V` lines are
in different coordinate systems and nothing in the log reconciles them.

`s0=(vb=released,…)` means the bound buffer's wrapper was destroyed while still
bound; `s0=(vb=stale,…)` means the stored pointer no longer resolves to the
wrapper it was recorded against. Neither is ever decoded.

For `D3DFVF_XYZRHW` — which is every draw this title issues in the front end —
the `x` and `y` in a `V` line **are** back-buffer pixel coordinates.

### How the state values are obtained, and how to read them

The game creates its device with `D3DCREATE_PUREDEVICE`, and a pure device
refuses every `Get*` state query. Render state, texture-stage state, FVF, stream
bindings and the viewport are therefore **shadowed** from the game's own `Set*`
calls. Each value carries its provenance:

- `ab=1` — observed: the game set this value.
- `bop=1~` — the Direct3D default; the game never set it.
- `zf=?` — unknown; a state block `Apply` invalidated the shadow.

Values recorded while a state block is being recorded (`BeginStateBlock` ..
`EndStateBlock`) are not applied to the shadow, because they are not applied to
the device either. If `!` lines never appear in a log, no state block was used
and the shadow is exact for that run.

### How the vertex data is obtained

The game's vertex and index buffers are created `D3DUSAGE_WRITEONLY`, which may
not legally be read back. Rather than lock them anyway and hope, the proxy wraps
the buffers and captures the bytes **on the way in**: whatever the game writes
between `Lock` and `Unlock` is copied into a private shadow, and draws are
decoded from that shadow. No Direct3D resource is ever read, and the game's own
bytes are never altered.

Bound buffers are held **weakly**. `SetStreamSource`/`SetIndices` deliberately do
not `AddRef` the wrapper: the device references the *real* buffer, and holding a
reference of our own to a `D3DPOOL_DEFAULT` resource would make `Reset` fail with
`D3DERR_INVALIDCALL` on every mode change. Instead the wrapper retracts itself
from every device that has it bound as it is destroyed, and each binding records
a process-unique generation number so a heap block the allocator recycles into a
*different* wrapper cannot impersonate the original. A draw through a binding
that lost its buffer is refused (`stream0-released-while-bound`,
`vb-wrapper-stale`), never decoded. This matters because the one buffer this
title draws from is `D3DPOOL_DEFAULT`, which the application **must** release
before `Reset` — so a resolution change or a level transition destroys it while
it is the bound stream.

### What the coverage check actually guarantees — and what it does not

Read this before treating a coordinate as measured.

Direct3D reports what the game **mapped** for writing. It never reports what the
game **wrote**, and there is no legal way to find out: the buffers are
`D3DUSAGE_WRITEONLY`, and poisoning a mapping to detect writes would change what
the game renders. So each mapped range is recorded with its provenance:

- A **sized** `Lock(off, size, …)` records `[off, off+size)` as an exact mapped
  extent.
- A **size-0** `Lock(off, 0, …)` means "to the end of the buffer" — the standard
  dynamic-ring idiom `Lock(0, 0, D3DLOCK_DISCARD)`. The game almost certainly
  wrote less, and after a discard the untouched tail is fresh uninitialised
  memory. That range is recorded as **provisional**.
- `D3DLOCK_DISCARD` voids the whole buffer's previous ranges, not just the
  locked one.

Ranges are kept as a **list, not a hull**: two disjoint locks do not claim the
gap between them. A draw reading that gap is refused.

The guarantee is therefore exactly this, and no more:

> **A draw that reads bytes the game never mapped for writing is refused. A draw
> that depends on a range whose extent was inferred rather than measured is
> marked `- warn vb-provisional-coverage` (or refused under
> `BEA_D3D9_STRICTCOV=1`).**

It is **not** a guarantee that every decoded byte was written by the game. Within
a mapped range the proxy cannot tell a written vertex from an unwritten one. Set
`BEA_D3D9_STRICTCOV=1` when that distinction matters more than coverage of the
capture. `L` and `U` records are in every log so the check can be audited from
the capture itself rather than taken on trust.

**Every refusal states its reason**, so an absent vertex dump can never be
mistaken for "the game drew nothing there", and every refusal and warning is
tallied by reason in the `# refusals` block at the end of the log.

## How the code is kept honest

- **No vtable slot is counted by hand.** `gen_wrappers.py` parses the same
  `d3d9.h` the compiler uses and emits the pass-through bodies and the vtable
  initialisers for all 119 `IDirect3DDevice9` slots (and the 17/6/14/14 of the
  other four interfaces). A wrong signature is a compile error, not a crash.
- **The export table is verified against the live system DLL** on every build.
  All 23 ordinals — including the six `NONAME` internals — are re-exported at
  their original ordinals. A missing forward is a crash at startup, so
  `build.ps1` fails rather than emit one.
- The real DLL is loaded from `GetSystemDirectoryW()` by absolute path, never by
  bare name, which would find this DLL again and recurse into itself. It is
  loaded lazily, never under the loader lock in `DllMain`.
- `Test-Proxy.ps1` drives the proxy through a real device with
  `D3DDEVTYPE_NULLREF` and a window that is never shown, then asserts the log
  contains the exact screen coordinates that were issued, on both the `…UP` path
  and the write-only buffer path.
- **The refusal paths are tested, not just the success paths.** The self-test's
  frame 3 releases a buffer while it is still the bound stream and allocates a
  new one straight afterwards, draws across the gap between two disjoint locked
  ranges, and draws from a `Lock(0, 0, D3DLOCK_DISCARD)` ring. Each must produce
  a named refusal or warning and **no** decoded vertex; the log is also asserted
  never to contain either doomed buffer's coordinates. Section `[5]` re-runs it
  with `BEA_D3D9_FAULT_NOCLEARBIND=1`, which leaves the binding genuinely
  dangling, so the generation check is proven to refuse rather than assumed to.

## Known limits

- An `IDirect3D9Ex` device would not be wrapped. This title never asks for one;
  if it ever did, the log says `D3D9EX create … -- NOT WRAPPED` rather than
  silently recording nothing.
- `QueryInterface` to an interface other than the one wrapped returns the real
  object unwrapped, and logs `qi-unwrapped`.
- Textures are not wrapped, so texture *contents* are not recorded — only
  identity, dimensions, format and level count.

## Back-buffer grab

`PrintWindow` with `PW_RENDERFULLCONTENT` returns the window chrome and a blank
white client area for this title, because the Direct3D back buffer is never
composited into the window DC (measured 2026-07-27; same note in
`rebuild/tools/Capture-Retail.ps1`). So the frame is taken from inside the
process instead, at `Present`, **before** the real call — with
`D3DSWAPEFFECT_DISCARD` the back buffer is undefined the moment `Present`
returns. It needs no foreground window, no focus and no synthetic input, and
nothing on the desktop can get in front of it.

```powershell
./Test-Shot.ps1                                        # prove it against known colours
./Run-FrontendPageCapture.ps1 -Route frontend-options   # drive to a page and capture it
```

| Variable | Default | Meaning |
|---|---|---|
| `BEA_D3D9_SHOT` | — | `all`, `change`, or a frame list: `1,3`, `40-90`, `0-600/30`. Setting it arms the grab; **nothing else does**, and with it unset no directory is created. |
| `BEA_D3D9_SHOTDIR` | `G:\bea-d3d9-shots` | Output root. A `<stamp>-<pid>` run directory is created under it. |
| `BEA_D3D9_SHOTEVERY` | `15` | `change` mode: sample every N frames. The VRAM read-back is the expensive part, and this title's frame timing is a measured quantity. |
| `BEA_D3D9_SHOTMAX` | `64` | Hard cap on images written. |
| `BEA_D3D9_SHOTTHRESH` | `6` | `change` mode: per-cell channel delta (4x4 grid) that counts as a change. |

Each run writes `manifest.csv` — one row per **sampled** frame, whether or not an
image was written, carrying the full-frame mean. The back buffer *is* the client
area, so that mean is directly comparable to the measured retail screen
signatures, and the manifest works as a signature oracle without any screenshot.

PNG is emitted with **stored (uncompressed) deflate blocks**. That is a
conformant zlib stream and needs no compression library, so a DLL injected into
a retail game gains no dependency. Files are large; the capture volume is bounded
by `BEA_D3D9_SHOTMAX` and the default output drive is chosen for having the room.

`Test-Shot.ps1` clears four frames of a real HAL device — on an off-screen window
that is never shown — to exact colours, two of them the measured retail
signatures `35,37,60` and `73,79,94`, and asserts the manifest mean **and** the
PNG's decoded pixels are those colours. The PNG is parsed independently in
Python (chunk CRCs, zlib, IHDR, filter bytes), which is what proves the channel
order and the hand-rolled encoder rather than assuming them.

Two behaviours worth knowing:

- `GetRenderTargetData` **fails** against this game's device with
  `D3DERR_INVALIDCALL`, though it succeeds against a plain HAL device. The grab
  falls back to `StretchRect` into a single-sampled `CreateRenderTarget`
  intermediate and reads back from that. The direct HRESULT and the fact that
  the fallback was taken are both recorded, so it is never silent.
- The cached `D3DPOOL_SYSTEMMEM` surface is **deliberately leaked** at
  `DLL_PROCESS_DETACH`: releasing it there is a call into the real `d3d9.dll`
  under the loader lock, at a point where that DLL may already be gone, and it
  crashed the self-test host at exit. The `D3DPOOL_DEFAULT` resolve target is
  released in a **pre**-`Reset` hook, because holding one across `Reset` makes
  `Reset` fail.

