# WebGPU / WASM / Netcode Feasibility Dossier

Status: historical feasibility dossier; product-lane references below are superseded by the WinUI/AppCore lane
Last updated: 2026-05-01
Scope: public-safe planning artifact for the Ralph-loop agentic RE goal

## Strategic call

WASM, WebGPU, and browser netcode are future runtime and rebuild concerns. They are not replacements for the current WinUI/AppCore product lane, and this goal must not implement a WebGPU renderer, WASM runtime, browser game port, or netcode layer.

Historical note: when this dossier was written, the near-term product was still framed around Electron/React. That lane is now archived/reference. Current active product work uses WinUI 3 plus AppCore, while Electron remains provenance/reference material.

The historical near-term product framing was:

- Electron main process and TypeScript CLI for local filesystem, copied-profile mutation, app-owned artifacts, Ghidra, CDB, VLC-backed media preparation, process lifecycle, Win32 capture, and scoped input.
- React/Vite renderer for browser-testable UI and fixture proof.
- Typed preload/job contracts so the renderer never receives raw Node, shell, debugger, Ghidra, filesystem, desktop-capture, process-launch, or input privileges.

The future web-runtime question is narrower: which clean-room, portable pieces can eventually run in Node, Electron, or browser contexts, and what must be proven before any rebuilt renderer, runtime, or networked mode is credible.

## Source register

Public platform sources checked for this dossier:

- MDN WebAssembly: <https://developer.mozilla.org/docs/WebAssembly>. MDN describes WebAssembly as a low-level, compact binary format for modern browsers that interoperates with JavaScript and is a compilation target for languages such as C/C++ and Rust.
- MDN WebGPU API: <https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API>. MDN describes WebGPU as a modern GPU API reached through `navigator.gpu`, adapter/device selection, canvas configuration, buffers, textures, pipelines, command encoders, and WGSL shaders. MDN currently marks it as not Baseline because it does not work in some widely used browsers, and the API is secure-context constrained.
- GPUWeb implementation status: <https://github.com/gpuweb/gpuweb/wiki/Implementation-Status>. The cross-browser status is moving but still platform-specific enough that prototypes need feature detection and pre-release/stable browser checks.
- Emscripten porting index: <https://emscripten.org/docs/porting/index.html>. Emscripten names the relevant porting surfaces: portability limits, runtime environment, C++/JavaScript integration, filesystems, graphics, audio, debugging, pthreads, networking, SIMD, exceptions, setjmp/longjmp, async code, and builds.
- Emscripten file systems: <https://emscripten.org/docs/porting/files/file_systems_overview.html>. Browser builds use virtual filesystems and cannot directly access arbitrary host files; persistence requires explicit browser-backed storage such as IndexedDB or user-mediated import/export.
- Emscripten pthreads: <https://emscripten.org/docs/porting/pthreads.html> and MDN SharedArrayBuffer: <https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer>. Browser pthread-style shared memory depends on `SharedArrayBuffer`, secure contexts, and cross-origin isolation headers.
- Emscripten networking: <https://emscripten.org/docs/porting/networking.html>. Browsers do not expose raw TCP/UDP sockets; Emscripten routes to WebSockets/proxies or JavaScript APIs, and does not provide C/C++ APIs for WebRTC or WebTransport.
- MDN WebTransport: <https://developer.mozilla.org/en-US/docs/Web/API/WebTransport_API> and MDN RTCDataChannel ordering: <https://developer.mozilla.org/en-US/docs/Web/API/RTCDataChannel/ordered>. These are candidate future transports, not design decisions.
- Emscripten audio/debug/SIMD docs: <https://emscripten.org/docs/porting/Audio.html>, <https://emscripten.org/docs/porting/Debugging.html>, <https://emscripten.org/docs/porting/simd.html>. Audio, debug information, and vectorization all need browser-specific proof rather than native assumptions.

Repo sources used:

- `roadmap/goals/2026-05-01-ralph-loop-agentic-re-master-goal.md`
- `roadmap/electron-workbench-migration.md`
- `roadmap/status-current.md`
- `roadmap/repo-structure-and-archive-map.md`
- `reverse-engineering/game-assets/extraction-pipeline.md`
- `reverse-engineering/quick-reference/aya-resource-chunks.md`
- `reverse-engineering/quick-reference/aya-tags.md`
- `reverse-engineering/quick-reference/source-hierarchy.md`

## Decision summary

| Question | Current answer |
| --- | --- |
| Can WASM/WebGPU replace the Electron backend now? | No. Browser sandboxes do not provide the native capabilities the workbench needs. |
| Can browser UI remain useful now? | Yes. Browser preview-mode fixtures and Browser Use are valuable for renderer workflows, but they are not native runtime proof. |
| Can WebAssembly help soon? | Yes, for portable parsers, validators, diff engines, asset loaders, and isolated clean-room simulation kernels with golden fixtures. |
| Can WebGPU help soon? | Possibly, for asset viewers or small clean-room scenes after asset loaders and intermediate render data are stable. |
| Can the original game be directly ported? | Not as a near-term task. The Steam binary, DirectX-era renderer, native dependencies, private assets, and undocumented runtime semantics make a direct browser port the wrong objective. |
| Can netcode start now? | No. Netcode is downstream of deterministic or server-authoritative clean-room runtime slices, stable state serialization, and a legal asset/content posture. |

## Historical native-workbench needs

The current WinUI/AppCore/tools lane has native responsibilities that a normal browser app must not perform:

- select and validate local game folders and copied profiles;
- prepare app-owned artifact roots and copied mutation targets;
- verify and mutate copied `BEA.exe` files through byte-checked patch catalog jobs;
- inspect, copy, plan, preview, apply, and restore save/options files without synthesizing baselines;
- launch and stop managed local processes;
- capture a Win32 game window and send separately armed scoped input;
- run Ghidra, CDB, PowerShell helpers, and VLC-backed media preparation;
- keep raw runtime evidence, private game files, media, saves, and screenshots out of public release surfaces.

Those workflows should stay behind WinUI/AppCore/C# CLI/tools boundaries with copied artifact roots. The archived Electron job model remains useful provenance, but it is not the active product backend. A browser-only runtime would either lose these capabilities or recreate them unsafely through local helper services, which would defeat the current native-boundary architecture.

## Near-term portable possibilities

Near-term web-runtime work should mean portable libraries, not a game port:

- save/options parsers and validators with true-view offsets, byte-preservation tests, and golden fixtures;
- patch catalog validators and byte-plan/diff engines that never patch original installs;
- AYA/resource archive chunk readers and dependency graph builders;
- texture/mesh metadata loaders that produce public-safe intermediate structures;
- browser-safe viewers for user-provided or sanitized fixtures;
- isolated simulation kernels for one documented mechanic at a time, such as rank calculation, energy/shield behavior, input mapping, or mission-script parsing after evidence exists.

The first viable shared target is TypeScript/Node/Electron parity. WASM becomes useful only when a bounded module has a stable API, measurable performance need, or a need to share logic across native-like and browser contexts.

## Long-term rebuild ambition

A long-term browser runtime must be a clean-room rebuild, not a wrapper around the retail executable. It would need:

- public-safe or user-provided assets;
- clean-room loaders for saves, resources, textures, meshes, language rows, audio, and video manifests;
- documented render semantics and material behavior;
- deterministic or intentionally server-authoritative runtime semantics;
- replayable input/state traces;
- explicit browser support and fallback policy;
- clear legal boundaries around original assets, source references, and extracted outputs.

The practical order is parser/loader first, viewer second, isolated simulation third, renderer fourth, runtime fifth, netcode last.

## DX8-era renderer constraints

The source hierarchy records a PC renderer chain through `CEngine -> CDXEngine (DirectX 8) -> CPCEngine`. That is useful architecture evidence, but the Steam retail binary remains the shipping-behavior authority.

WebGPU is not a DirectX 8 compatibility layer:

- Fixed-function or FVF-era assumptions need explicit translation into modern vertex layouts, bind groups, pipelines, textures, samplers, and WGSL shaders.
- D3D render state, texture stages, fog, alpha test/blend behavior, lighting, matrix usage, and viewport/camera behavior need semantic documentation before visual parity can be claimed.
- Shaders must be rewritten or reconstructed. The original PC path predates WebGPU's WGSL model.
- WebGPU device limits, adapter features, texture formats, compressed texture support, device loss, and browser/driver variance must be part of the proof matrix.
- Renderer proof must distinguish "asset appears in a viewer" from "game scene parity." A rotating model viewer is not a rebuilt game renderer.

Near-term WebGPU work should be limited to a browser-safe asset or scene viewer after loader outputs are stable. WebGL or CPU/2D fallbacks may still be needed for unsupported browsers or test environments.

## Native dependency constraints

The current preservation work relies on native tooling and OS integration:

- `BEA.exe` launch/stop and copied-profile setup;
- Win32 window capture and bounded scoped input;
- Ghidra/headless jobs and mutation-gated rename maps;
- CDB/WinDbg helpers;
- VLC-backed Bink `.vid` preparation into app-owned MP4 cache;
- legacy AYAResourceExtractor-related x86/C++/CLI constraints;
- local artifact roots and private evidence retention.

WASM does not grant these authorities. In a browser, WebAssembly still runs inside the browser security model and reaches browser APIs through JavaScript bindings or Emscripten glue. Any web prototype must treat native jobs as out of scope or consume public-safe exported summaries.

## Asset and media constraints

The asset surface is feasible but not trivial:

- Resource archives are chunked `*_res_PC.aya` files, commonly under `data\Resources\`, with 4-byte chunk IDs and size-prefixed payloads.
- Known top-level chunks include `LVLR`, `TARG`, `AYAD`, `TEXT`, `MESH`, `ERES`, `WRES`, `IMPS`, `SURF`, `SSHD`, `PLAT`, `PMIB`, `DMKR`, and `GDIE`.
- Mesh data includes hierarchy, bounding, bone, animation, material, index-buffer, vertex-buffer, and texture-reference chunks.
- Vertex buffers are documented as 36-byte standard vertices or 48-byte skinned variants, with D3D-era FVF flags and triangle-strip primitive data.
- Texture payloads can involve zlib-compressed DDS content. Browser upload paths require decoded or browser-supported texture formats, plus explicit handling for compression and color/alpha behavior.
- `REFR` chunks can share geometry from another part, and `BBOX` can appear twice intentionally. A viewer must preserve these quirks rather than normalizing them away.
- Bink `.vid` playback is not solved by WebGPU. The current app uses VLC as backend infrastructure to prepare an app-owned MP4 cache where available.

Public-safe posture is bring-your-own-game-files or sanitized fixtures. Do not bundle raw game assets, private media, raw saves, screenshots with private imagery, or copied executable bytes into public releases.

## WebAssembly constraints

WebAssembly is plausible for bounded modules, but the browser environment changes the work:

- Filesystem access is sandboxed and user-mediated. Emscripten virtual filesystems can simulate synchronous native file APIs, but browser builds do not have arbitrary path access.
- Persistent browser storage needs explicit IndexedDB or export/import flows; in-memory `MEMFS` state is lost on reload.
- C++/JavaScript boundaries must be designed. Every exported parser or simulation function needs stable binary/JSON contracts.
- Pthreads require `SharedArrayBuffer` and cross-origin isolation headers in deployed browsers.
- SIMD can help math-heavy or decode-heavy modules, but needs feature detection, scalar fallback, and parity tests.
- Exceptions, setjmp/longjmp, undefined behavior, float/integer edge cases, memory growth, and async loading need review before compiling source-derived clean-room code.
- Browser debugging uses Emscripten/browser tooling such as DWARF, name sections, source maps, assertions, sanitizers, and DevTools. It is not a replacement for Ghidra/CDB evidence.

Good first WASM candidates are parsers and pure validators. Poor first candidates are the renderer, process launcher, debugger adapter, media transcoder, and whole-game runtime.

## WebGPU constraints

WebGPU is promising for a future renderer target, but each prototype must be gated:

- Feature-detect `navigator.gpu`, adapter availability, required limits, and required optional features.
- Run only from secure contexts or trusted local origins.
- Include fallback behavior for no adapter, rejected device requests, device loss, unsupported texture formats, and browser-specific gaps.
- Keep input assets public-safe or user-provided.
- Build a deterministic fixture scene before attempting gameplay scenes.
- Record screenshots/artifacts as proof, but do not treat visual similarity as semantic parity.

The browser support matrix should be updated at prototype time, not frozen in this dossier. As of this dossier, MDN and GPUWeb status still justify cautious, feature-detected WebGPU planning rather than a hard dependency in the default workbench.

## Deterministic simulation constraints

Netcode and runtime replay depend on simulation discipline. Before any multiplayer design, a clean-room runtime slice must define:

- fixed tick rate or explicit variable-step rules;
- input sampling and serialization format;
- deterministic PRNG behavior;
- state snapshot format;
- floating-point tolerance policy across engines and architectures;
- mission script/event ordering;
- AI and physics update order;
- collision and damage semantics;
- replay comparison artifacts.

For Battle Engine behavior, source names and architecture are hints, while retail binary evidence, real saves, Ghidra, and runtime probes remain authority. A simulation slice should start small: one mechanic, one fixture, one replay, one acceptance test.

## Netcode constraints

Browser transports are not the hard part until the simulation model exists.

Potential future transport families:

- WebRTC data channels for peer-to-peer or relay-assisted low-latency data, including ordered/unordered channel choices.
- WebTransport for client/server streams and datagrams where browser/server support is available.
- WebSockets for tooling, lobby, relay, or server-authoritative prototypes where reliability and deployability matter more than UDP-like behavior.

Design questions that must precede transport selection:

- Is the game deterministic enough for lockstep or rollback?
- If not, what is server-authoritative and what is predicted locally?
- What is the state delta format?
- How are mission scripts, AI, projectiles, transform state, energy, shields, damage, and cutscene/camera events replicated?
- What latency and packet-loss behavior is acceptable for walker/jet movement and weapon firing?
- How are user-provided assets/content versioned and verified?
- What anti-cheat or trust model is realistic for a preservation project?

Do not start netcode until clean-room runtime slices can replay deterministically or a server-authoritative model is deliberately chosen.

## Legal and release posture

This dossier is public-safe and intentionally contains no raw assets, executable bytes, save contents, private screenshots, or secrets.

Any future web runtime must keep these release rules:

- Use bring-your-own-game-files for copyrighted retail assets unless a sanitized subset is explicitly cleared.
- Keep `game/**`, private `media/**`, `save-attempts/**`, raw `subagents/**`
  proof output, private runtime evidence, and operator directives out of
  app ZIPs, generated package/source exports, and web/community runtime
  bundles. Compact non-secret state batons may be tracked in public-primary
  source.
- Do not ship copied `BEA.exe` bytes, extracted private media, raw Bink video, raw screenshots, or local proof JSON.
- Treat Stuart's source as architecture/name/logic evidence, not as directly shippable web-runtime code unless rights and cleanup are explicitly reviewed.
- Keep public docs focused on methods, schemas, and sanitized evidence.

## Prerequisites before any web runtime prototype

Do not begin a WebGPU renderer, WASM runtime, browser game port, or netcode prototype until these prerequisites are met:

1. Public-safe input policy exists for every asset, save, archive, media file, and fixture used by the prototype.
2. Portable parser contracts exist for the target formats, with golden fixtures and byte-preservation tests.
3. Asset-loader outputs are normalized into documented intermediate structures suitable for Node, Electron, and browser execution.
4. The Electron typed backend remains the native workflow authority, and the prototype has no dependency on raw local paths, private runtime evidence, or original executable mutation.
5. Renderer scope is limited to an asset viewer or isolated clean-room scene.
6. Any runtime behavior selected for simulation has documented source/binary/runtime evidence and acceptance tests.
7. Browser support matrix, secure-context hosting plan, cross-origin-isolation needs, and fallback behavior are written down.
8. Build/package boundaries prevent WASM/WebGPU artifacts and private fixtures from entering community releases accidentally.
9. Browser proof, Electron desktop proof, packaged-bundle proof, and real runtime proof are labeled separately.
10. Stop conditions exist for private-data leakage, unsupported browser capabilities, unverified runtime semantics, or scope drift into a full port.

## Staged research plan

### Stage 0 - Keep the product lane native

Continue WinUI/AppCore/C# CLI/tools work for local files, copied profiles, Ghidra, CDB, VLC, capture, launch, patching, and private evidence. Browser UI proof remains fixture/UI proof and is not native runtime proof.

Exit evidence:

- typed job contracts remain intact;
- no renderer raw native privileges;
- release policy still excludes private/runtime families.

### Stage 1 - Portable parsers and validators

Move stable parsers and validators toward portable TypeScript, Rust, or C/C++ cores with explicit contracts. Prioritize saves/options, patch catalog validation, archive chunk walking, texture metadata, and dependency graphs.

Exit evidence:

- golden fixtures;
- byte-preservation and re-encode tests where mutation is allowed;
- Node/Electron parity.

### Stage 2 - Browser-safe asset loaders

Allow user-provided public-safe archives or sanitized fixtures to be loaded into browser memory through explicit file-picker/import flows. Produce structured JSON/binary intermediate outputs.

Exit evidence:

- no arbitrary local path access;
- no private asset bundling;
- loader outputs documented and stable.

### Stage 3 - WASM parser or simulation modules

Compile selected clean-room modules to WASM only when performance, portability, or shared logic justifies it. Keep APIs narrow: parse, validate, diff, serialize, or simulate-one-step.

Exit evidence:

- WASM and non-WASM outputs match;
- browser hosting headers are documented if threads are used;
- debug and release builds are reproducible.

### Stage 4 - Web asset viewers

Build browser viewers for textures, meshes, and simple scenes after loader outputs are stable. Evaluate WebGPU behind feature detection, with WebGL/2D/no-preview fallbacks where needed.

Exit evidence:

- public-safe fixture scene;
- browser matrix;
- screenshots or pixel checks labeled as viewer proof only.

### Stage 5 - Clean-room renderer prototype

Prototype a renderer for one small public-safe scene using documented intermediate assets and clean-room shaders. This is renderer feasibility, not game parity.

Exit evidence:

- documented material/render assumptions;
- WebGPU feature/limit checks;
- fallback behavior;
- visual proof plus known gaps.

### Stage 6 - Clean-room runtime slices

Prototype isolated runtime systems such as movement, camera, weapon energy, damage, or mission-script interpretation only when the RE coverage map has enough evidence and tests to define expected behavior.

Exit evidence:

- replayable input/state trace;
- deterministic or tolerance-bound comparison;
- explicit source/binary/runtime evidence links.

### Stage 7 - Netcode research

Evaluate network authority, replication, prediction, rollback/replay, and transport options only after deterministic or server-authoritative runtime slices exist.

Exit evidence:

- authority model;
- state serialization;
- latency/loss test harness;
- chosen transport rationale;
- public-safe asset/content versioning plan.

## Current goal instruction

For the 2026-05-01 Ralph-loop goal, this dossier is the deliverable. It should guide future planning and prevent premature porting.

Do not implement a WebGPU renderer, WASM runtime, browser game port, or netcode layer as part of the current goal.
