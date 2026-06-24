# Capture/Menu Behavior Analysis

> Scope: explain the windowed-app menu entries (`File`, `Capture`) observed during runtime and why they often appear to do nothing.
> Date: 2026-03-01

## Executive Summary

The `File`/`Capture` menu commands are consistent with the legacy DirectX framework-style app shell used by this build lineage. Source parity indicates menu dispatch wiring exists, but capture implementation files (`Capture.cpp`/`Capture.h`) are absent from the current Stuart source drop. In retail behavior, this can present as visible menu options with weak/no observable action.

## Menu Command Routing (Source Anchors)

From `references/Onslaught/d3dapp.cpp`:

- `WM_COMMAND` dispatch block: `references/Onslaught/d3dapp.cpp:768-833`
- Capture command IDs and handlers:
  - `IDM_CAPTUREOPTIONS -> CCAPTURE::ShowCaptureOptions(hWnd)` (`references/Onslaught/d3dapp.cpp:820-822`)
  - `IDM_CAPTURESTART -> CCAPTURE::StartCapture()` (`references/Onslaught/d3dapp.cpp:824-826`)
  - `IDM_STOPCAPTURE -> CCAPTURE::StopCapture()` (`references/Onslaught/d3dapp.cpp:828-830`)
- Other relevant menu paths:
  - `IDM_CHANGEDEVICE` (`references/Onslaught/d3dapp.cpp:788-799`)
  - `IDM_TOGGLEFULLSCREEN` (`references/Onslaught/d3dapp.cpp:801-811`)
  - `IDM_EXIT` (`references/Onslaught/d3dapp.cpp:813-816`)

Editor parity exists in `references/Onslaught/EditorD3DApp.cpp:758-803` with the same capture command mapping.

### Visible Menu Command Map (Observed UI)

| Menu Command | Source Mapping | Status | Evidence |
|---|---|---|---|
| `File > Go/stop` | `IDM_GO` case exists but is commented out | Visible, no active handler | `references/Onslaught/d3dapp.cpp:772`, `references/Onslaught/EditorD3DApp.cpp:742` |
| `File > Single step` | `IDM_SINGLESTEP` case exists but is commented out | Visible, no active handler | `references/Onslaught/d3dapp.cpp:778`, `references/Onslaught/EditorD3DApp.cpp:748` |
| `File > About...` | `IDM_HELP_ABOUT` handled in shell path | Explicit no-op/defer behavior in this source drop | `references/Onslaught/ltshell.cpp:1012`, `references/Onslaught/ltshell.cpp:1070` |
| `File > Change device...` | `IDM_CHANGEDEVICE` | Active handler path | `references/Onslaught/d3dapp.cpp:788-799` |
| `File > Exit` | `IDM_EXIT` | Active handler path | `references/Onslaught/d3dapp.cpp:813-816` |
| `Capture > Options` | `IDM_CAPTUREOPTIONS -> CCAPTURE::ShowCaptureOptions` | Routed, implementation source missing | `references/Onslaught/d3dapp.cpp:820-822` |
| `Capture > Start` | `IDM_CAPTURESTART -> CCAPTURE::StartCapture` | Routed, implementation source missing | `references/Onslaught/d3dapp.cpp:824-826` |
| `Capture > Stop` | `IDM_STOPCAPTURE -> CCAPTURE::StopCapture` | Routed, implementation source missing | `references/Onslaught/d3dapp.cpp:828-830` |

## Binary-Side Evidence

- `AVIFIL32.dll` is imported by `BEA.exe`.
- `AVIStreamWrite` import is present in `BEA.exe` import table.
- Existing RE symbol evidence includes `CDXEngine__CaptureAviFrame` (`0x005140e0`) and `AVIStreamWrite` references in exported function snapshots under `reverse-engineering/binary-analysis/scratch/**/all-after-*.tsv`.

These anchors support that at least part of AVI capture plumbing exists in the retail binary.

## Why Menus Can Appear No-Op

High-confidence contributors:

1. **Framework shell behavior**: DX sample-framework menu surface is visible regardless of whether all capture prerequisites are active.
2. **Missing source implementation in provided drop**: no `Capture.cpp`/`Capture.h` available in current `references/Onslaught` tree, limiting source parity and suggesting optional/conditional capture code paths.
3. **Runtime preconditions**: capture start/options typically require valid compressor/configuration/output state; if unmet, commands may return without visible UI side effects.

## External Corroboration (Stuart / desimbr)

Operator-supplied Discord notes from 2026-02-25 align with the binary/source evidence:

- The window menu structure looks like default DirectX 8 framework menu wiring.
- Capture behavior likely relied on Win32 AVI APIs (specifically `AVIMakeCompressedStream` was recalled).
- Source parity gap remains expected: retail `.map/.pdb` were not available, and current source drop is `.cpp/.h` only.

These statements are treated as corroborating context, not sole proof; command routing and import evidence above remain the primary anchors.

## Confidence and Open Questions

- Command dispatch mapping: **high**.
- AVI pipeline presence in binary: **high**.
- Exact retail runtime failure/no-op condition for each capture command: **medium** (needs deeper behavior-level tracing in binary call chains).

Open questions for next pass:

1. Resolve exact function-level chain from WM_COMMAND IDs to `CDXEngine__CaptureAviFrame` and any gate flags.
2. Determine whether options dialog path is disabled by build flags, runtime checks, or missing codec/compressor path.
3. Identify if capture commands are compiled as stubs in this retail variant.

## Related

- `reverse-engineering/binary-analysis/widescreen-patch-analysis.md`
- `reverse-engineering/binary-analysis/windowed-mode-analysis.md`
- `references/Onslaught/d3dapp.cpp`
- `references/Onslaught/EditorD3DApp.cpp`
