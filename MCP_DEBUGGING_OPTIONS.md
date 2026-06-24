# MCP Debugging Options (BEA RE)

Status: private maintainer/workstation note
Release posture: excluded from public/community release profiles
Last updated: 2026-05-01

This file compares local MCP/debugger options for private maintainer RE work. It is intentionally excluded from public/community release profiles because it records workstation paths, debugger setup assumptions, and local toolchain choices.

## Active Pathing (This Machine)

- Ghidra client: `D:\ghidra_12.0.3_PUBLIC_20260210\ghidra_12.0.3_PUBLIC`
- Ghidra project root: `C:\Users\david\Ghidra`
- Active GhydraMCP runtime bundle: `D:\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952`
- Repo-local `tools/GhydraMCP/` has been removed from this repo to avoid version drift confusion.

## Concise Install List (Recommended)

Order matters. This is the minimal stack that works best for BEA.exe RE with MCP access:

1. **Ghidra 12.x + GhydraMCP**
   Static analysis with MCP control (decompile, xrefs, data/struct edits). Install Ghidra, then install GhydraMCP plugin zip and run the MCP bridge. On this machine, the active bundle is `D:\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952`.
2. **x64dbg (x32dbg) + x64dbgMCP**
   Primary live debugger for the 32-bit BEA.exe. Install x64dbg, drop the plugin `.dp32` into the x32dbg plugins folder, then connect via MCP.
3. **Frida + frida-mcp**
   Runtime instrumentation and hooks when static + debugger aren’t enough. Install Frida, then `frida-mcp`.
4. **WinDbg + mcp-windbg** (optional but valuable)
   Crash dumps / deep Windows analysis. Install WinDbg or Debugging Tools for Windows, then `mcp-windbg`.

## Version/Cost Check (Verified 2026-02-10)

All recommended items are free. Latest-known versions at time of writing:
- Ghidra: `12.0.3` (active on this workstation).
- GhydraMCP: `v2.2.0-rc.2` (active working install, external bundle path above).
- x64dbg: GitHub snapshot release tag `2025.07.04` (use x32dbg for BEA.exe).
- x64dbgMCP: install/build from `Wasdubya/x64dbgMCP` (no formal release tags; use the repo’s `build/release/` artifacts).
- frida-mcp: PyPI `0.1.1` (2025-03-27).
- mcp-windbg: PyPI `0.12.2` (2025-12-15).

Note: GhydraMCP mutation reliability is affected by bridge request timeout. If renames/signature changes time out on `BEA.exe`, bump timeout aggressively (e.g., **300s+**) and restart the MCP server process. The stock `bridge_mcp_hydra.py` shipped in the bundle uses a hard-coded **10s** HTTP timeout; see `MCP_LIMITATIONS.md` for why this matters on `BEA.exe`.

## Two Access Modes (Important)

There are two independent layers:

1. **Codex MCP tools** (`mcp__ghydra__*`)
   This is the Codex client transport path to GhydraMCP.

2. **Direct HTTP to GhydraMCP plugin** (`http://<host>:8193/...`)
   This talks to the same Ghidra plugin API directly.

If Codex MCP transport fails (for example `Transport closed`), direct HTTP can still be healthy. This is not bypassing GhydraMCP; it is using the same backend API through a different client path.

**WSL networking caveat (this machine):** from WSL, use the Windows gateway IP (example: `http://172.26.112.1:8193`) rather than `127.0.0.1`, which is unreliable for the Windows-hosted Ghidra HTTP server.

## Save / Persistence Model (Do Not Skip)

- Mutation transaction success is required for edits to exist in the current open program state.
- The Ghidra `Save BEA.exe` action still matters for durable persistence and reliable reopen behavior.
- Recovery snapshots may recover work after crashes, but they are not a substitute for a clean save.
- Operational rule:
  1. Apply mutation.
  2. Read back by address immediately.
  3. If mismatch, record in `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`.
  4. After a meaningful batch, do explicit UI save when possible.

Appendix below contains the full catalog and setup notes.

## Appendix: Full Options and Notes

### Quick Recommendation (for BEA.exe)

1. **x64dbgMCP (x32dbg)** — best fit for live Windows x86 debugging (step, breakpoints, memory).
2. **frida-mcp** — best for live instrumentation/hooking without a traditional debugger UI.
3. **mcp-windbg** — best for crash dumps or WinDbg/CDB style workflows.
4. **LLDB MCP** — good cross-platform option if you prefer LLDB tooling.
5. **gdb-mcp / DAP-based (mcp-debugger, dap-mcp)** — good if you want DAP standardization.

### MCP Server Options (Validated)

| MCP Server | Debugger/Backend | Best For | Notes |
|------------|------------------|----------|-------|
| **x64dbgMCP** | x64dbg / x32dbg | Live Windows debugging | Plugin exposing 40+ x64dbg SDK tools; works with x64dbg/x32dbg. |
| **x64DbgMCPServer** | x64dbg / x32dbg | Live Windows debugging | C#/.NET Framework plugin template; HTTP/SSE MCP bridge. |
| **mcp-windbg** | WinDbg / CDB | Crash dumps + remote debug | Python MCP wrapper around CDB; supports dump analysis and live sessions. |
| **windbg-ext-mcp** | WinDbg extension + MCP | Kernel + user-mode debugging | Extension + MCP server; more setup (build extension). |
| **frida-mcp** | Frida | Live instrumentation, hooking | Inject JS, attach/spawn, inspect processes dynamically. |
| **LLDB MCP (official)** | LLDB | Cross-platform debugging | Built-in MCP server in LLDB. |
| **gdb-mcp** | GDB | Linux/Wine debugging | MCP wrapper around GDB for live sessions. |
| **mcp-debugger** | DAP (multi-language) | DAP-based workflows | MCP server for Debug Adapter Protocol; supports multiple languages. |
| **dap-mcp** | DAP | Python-first DAP workflows | MCP server designed for DAP sessions via config. |

### Setup Notes (Minimal)

#### x64dbgMCP
- Install the x64dbg plugin (`.dp32`/`.dp64`), then connect via MCP.
- Use x32dbg for BEA.exe (32-bit).
- The repo includes a Python client that can connect to the MCP port shown in x64dbg logs.

#### x64DbgMCPServer (AgentSmithers)
- C#/.NET Framework plugin template that exposes x64dbg via HTTP/SSE.
- Requires a stdio↔SSE bridge (e.g., MCPProxy-STDIO-to-SSE) for Claude Desktop.
- Default server URL in docs: `http://127.0.0.1:50300/sse`.

#### mcp-windbg
- Install WinDbg or Debugging Tools for Windows, then `pip install mcp-windbg`.
- Connect to crash dumps or remote targets via CDB.

#### windbg-ext-mcp
- Build the WinDbg extension and run the MCP server (requires VS Build Tools + Poetry).
- Designed with kernel debugging in mind but works for user-mode too.

#### frida-mcp
- `pip install frida-mcp` and run the MCP server.
- Attach/spawn the process and inject Frida scripts as needed.

#### LLDB MCP (official)
- Start the MCP server inside LLDB:
  ```
  (lldb) protocol-server start MCP listen://localhost:59999
  ```

#### gdb-mcp
- Install and run:
  ```
  gdb-mcp
  # or
  python -m gdb_mcp.server
  ```

#### mcp-debugger / dap-mcp
- Use if you prefer standardized Debug Adapter Protocol workflows.
- Configure with a DAP adapter (e.g., CodeLLDB, cppdbg) for native debugging.

### Recommended Stack for BEA.exe (Windows)

- **Primary**: x64dbgMCP (x32dbg) for stepping, breakpoints, memory inspection.
- **Secondary**: frida-mcp for runtime hooks, string interception, or fast probes.
- **Crash analysis**: mcp-windbg for post-mortem dumps and deeper Windows tooling.

### Additional / Experimental Options

These are promising for RE workflows but **not MCP-native** yet. They can be bridged with a lightweight MCP shim if needed.

- **Cheat Engine (CE) + MCP shim**
  Use CE for memory watches, pointer scans, and trainers. A small MCP server can read CE tables or expose a named‑pipe/HTTP bridge for watch values and simple write operations.
- **ReClass.NET + MCP shim**
  Great for struct layout discovery and live memory visualization. Export struct definitions or memory snapshots through a custom MCP wrapper.
- **RenderDoc / PIX (graphics capture)**
  Not directly MCP‑friendly, but useful for rendering pipeline insights and shader inspection; could be paired with a minimal MCP “session metadata” wrapper.
- **DynamoRIO / Intel Pin instrumentation**
  Advanced dynamic instrumentation. Not MCP‑ready, but can feed trace data to an MCP server for search/analysis.

If you want, I can draft a minimal “CE‑to‑MCP” or “ReClass‑to‑MCP” bridge spec in a follow‑up.

### Sources (checked Feb 12, 2026)

Ghidra releases: https://github.com/NationalSecurityAgency/ghidra/releases
GhydraMCP releases: https://github.com/starsong-consulting/GhydraMCP/releases
x64dbg releases: https://github.com/x64dbg/x64dbg/releases
LLDB MCP: https://lldb.llvm.org/use/mcp.html
x64dbgMCP: https://mcpservers.org/servers/Wasdubya/x64dbgMCP
x64dbgMCP (GitHub): https://github.com/wasdubya/x64dbgmcp
x64DbgMCPServer: https://github.com/AgentSmithers/x64DbgMCPServer
mcp-windbg: https://github.com/svnscha/mcp-windbg
mcp-windbg (PyPI): https://pypi.org/project/mcp-windbg/
windbg-ext-mcp: https://github.com/NadavLor/windbg-ext-mcp
frida-mcp: https://github.com/dnakov/frida-mcp
frida-mcp (PyPI): https://pypi.org/project/frida-mcp/
gdb-mcp: https://pypi.org/project/gdb-mcp/
mcp-debugger: https://github.com/debugmcpdev/mcp-debugger
dap-mcp: https://github.com/KashunCheng/dap_mcp
