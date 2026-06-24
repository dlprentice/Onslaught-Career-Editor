# Agent Lessons Learned

Status: active
Last updated: 2026-06-22

Durable operating lessons from the long WinUI product and reverse-engineering campaign. This file is for future agents after compaction, restart, handoff, or parallel work. Keep it practical and evidence-backed. Add lessons here when a real mistake, flaky path, proof gap, or workflow improvement is discovered.

## How To Use This File

- Read this after `AGENTS.md` when doing WinUI product, native UIA, release, or RE work.
- Add a short entry after every meaningful wave if the wave taught something reusable.
- Keep instructions in `AGENTS.md` high-signal; put longer explanations here.
- Do not replace validation evidence with lessons. Evidence still belongs in readiness notes, state ledgers, and test output.
- Prefer precise lessons tied to repo paths, commands, and failure modes over generic advice.

## Current Operating Truth

- WinUI 3 is the primary user-facing Windows product lane.
- Electron, WPF, and the old Python GUI/CLI parity app are archived/reference app lanes. Do not restart them as product work without an explicit strategy reset.
- Python under `tools/` remains active RE/tooling/lab support.
- Ghidra function-quality queue on the loaded Steam retail database is **6411/6411 = 100.00%** with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt. Wave1220 static closeout acceptance validates active current-risk focused accounting at **1179/1179 = 100.00%** with remaining active focused work `0`. This is rebuild-grade static-contract posture, not runtime gameplay proof, exact layout proof, rebuild parity, or no-noticeable-difference proof.
- `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila` is read-only source material. Mutation, patching, runtime proof, captures, caches, or copied saves must use copied profiles or app-owned artifact roots.
- Do not blur the installed-game read-only rule with Ghidra project work. Saved Ghidra name/signature/comment/type corrections are expected when evidence supports them, but they must run as explicit serialized mutation waves with dry run, apply, read-back, logs, public-safe docs, and state updates.
- Browser/Electron preview evidence is archived-reference evidence, not native WinUI or packaged-runtime proof.
- Static catalog extraction proves file/catalog coverage. It does not prove in-game runtime behavior, Goodies unlock flow, animation, model viewer behavior, or gameplay semantics.

## Search And Terminal Hygiene

- In this Windows/Codex lane, `rg` has repeatedly been unreliable. Use `git ls-files` plus targeted Node or Python scans unless a fresh check proves `rg` is healthy in the current shell.
- Do not keep retrying a known-bad search path. If the user or prior state says a tool is broken, switch immediately to the documented fallback and record the fallback if it is not already durable.
- Avoid opening long-lived terminal sessions casually. The unified exec process limit can be exhausted during long goals, which makes later validation harder.
- Prefer one-shot commands through the current controlled execution path. If a persistent REPL is already available and stable, reuse it instead of spawning more shells.
- Long-running UI goals should not leave idle helper processes behind. Use timeouts, poll existing sessions instead of spawning duplicates, and stop background servers or smokes when the wave no longer needs them.
- When the execution environment warns about process limits, treat that as a real operational defect. Stop opening new shells, use the stable REPL or existing session, and finish the current wave with a clean process posture.
- The Node REPL used in this Codex desktop lane may not expose `process.env`. For private environment variables in validation commands, prefer a shell wrapper such as `cmd.exe /c set NAME=value && command`.
- The same Windows REPL path may fail to spawn `npm` directly with `ENOENT`. Use `cmd.exe /c npm ...` or `npm.cmd` for npm-backed validation instead of diagnosing that as a repo failure.
- Keep inline validation one-liners simple. PowerShell quoting can corrupt Node `-e` snippets that contain regular expressions or nested quotes; if that happens, rerun with a simpler parse-only command and record it as a tooling/quoting artifact, not a repo failure.
- For private env-gated native smokes launched from the Node wrapper, verify that the env actually reaches the test. A PowerShell `$env:` wrapper proved more reliable than `cmd.exe /c set ... && dotnet test` for the real-catalog Asset Library smoke.
- Do not repeat a stale generated-artifact loop by habit. If release-profile or manifest artifacts change repeatedly, inspect which source file actually affects them before regenerating again.
- When a wave is interrupted or compacted with dirty tracked/untracked files, treat that dirty diff as active work. Inspect it, identify the intended wave, and either continue it or explicitly park it before starting a new thread of changes.
- Run .NET build and test commands serially. AppCore, AppCore.Host, C# CLI, and UI tests share build outputs and can fail with transient file locks when run in parallel.
- Record exact commands and outcomes in the active evidence ledger. A later agent should not need to infer what was run from commit messages alone.
- Be careful with prose that looks like a command. The doc-command checker can intentionally parse npm-script-looking phrases even inside evidence text, so use neutral wording such as "script references checked" unless documenting a real command.
- Avoid rote progress updates in long loops. If a status line repeats, replace it with the new fact learned, the blocker being investigated, or the exact validation still running.
- If a user points out a repeated operating mistake in chat, convert it into this file during the same wave before continuing broad implementation. Chat corrections are too easy to lose after compaction.
- Do not guess local skill paths after compaction. Use the exact `path` entry from the injected skill list for that session; Superpowers plugin skills live under the plugin cache path in this workspace, not under `.codex/skills/superpowers/`. A failed skill-file read is an agent routing mistake, not meaningful user-facing progress.
- For static Ghidra re-audit waves, treat one- or two-function tranches as a fallback for risky boundaries, not the default. When call cleanup, owner, and evidence quality are consistent, prefer larger coherent clusters and reusable probe/apply scaffolding so validation overhead buys more reviewed functions per wave. Do not weaken the proof contract for speed: dry/apply/read-back exports, probes, mutation logs, public-safe docs/state, backup, verification, and commit/push remain required for saved Ghidra changes.
- During static RE evidence gathering, prefer fresh wave-local exports, bounded file lists, and targeted source/docs scans before broad repo scans. If a broad scan is still needed, exclude generated scratch and ignored export folders; old `subagents/` or `reverse-engineering/binary-analysis/scratch` TSV/decompile exports can contain stale historical names and pollute current evidence.
- Do not run probes in parallel when they regenerate the same ignored RE evidence folder. Wave1109 showed that running `test:wave1108-current-risk-rank` beside a dependent Wave1109 probe can race on `subagents/ghidra-static-reaudit/wave1108-current-risk-rank/`; run shared-artifact generator/probe chains sequentially.
- Do not describe late raw-head/static-tail rows as "low-signal" when the function is important. Use evidence-density language instead: rows like `CUnit__ApplyDamage` may be harder to prove from source names or strings, but they can still be central connective infrastructure for damage, lifetime, render, cleanup, ownership, effects, or messaging.
- For high-use RE tables that agents read in Windows shells, prefer ASCII status words and escaped byte spellings over glyphs or accented renderings. For example, `WORKS`, `Decoded`, and `lat\\xEAte` survive PowerShell output better than checkmark icons or font-dependent `latete` variants.

## WinUI Native Testing Lessons

- Maximize the WinUI app before screenshot or broad interaction evidence unless the test is intentionally proving narrow-window behavior.
- The product app should start maximized by default unless a test intentionally overrides the window. This makes manual use and automated screenshots closer to the real desired workspace.
- Treat maximized WinUI evidence as the default screenshot posture. If a screenshot or smoke is intentionally not maximized, say why in the evidence instead of leaving future readers to infer it.
- If a native smoke launches a focus-taking window, warn the user before the run. If the user types into the smoke window, mark the run contaminated and rerun it instead of diagnosing product behavior from polluted input.
- Treat offscreen controls as normal on laptop-sized displays. Use automation IDs, `ScrollIntoView`, section navigation, or targeted invocation instead of assuming first-viewport visibility.
- First-viewport screenshots are useful only when explicitly labeled as first-viewport proof. Scrolled-section proof should say what was scrolled into view.
- Functional UI Automation and visual QA prove different things. UIA can drive offscreen controls through the accessibility tree; screenshots prove layout, contrast, density, and whether the product looks acceptable to a human.
- Accessibility is not just a test convenience. Missing automation IDs, unscrollable regions, bad focus order, or inaccessible action labels should be treated as product defects when they block reliable native automation.
- For deep pages, capture both the initial maximized viewport and at least one scrolled-section proof when claiming the whole workflow is visually healthy.
- Rebuild `OnslaughtCareerEditor.WinUI` before filtered UIA smoke after app-code changes. A filtered `dotnet test` can rebuild the test assembly while still launching an older WinUI executable.
- UIA can prove accessibility-tree state while missing visible trust issues. Inspect screenshots after meaningful UI work.
- User typing can contaminate live UI smoke if the app window takes focus. Before a smoke run, announce that the app may open and avoid treating a contaminated smoke failure as product evidence.
- Tests should prefer automation IDs and stable user-facing text. Exact copy assertions are useful when the copy is part of the product promise, but brittle when matching incidental layout text.
- Startup and deep-link states need their own assertions. A test that clicks into a later state can miss a bad initial state.
- Cross-page handoffs need destination-state assertions. A source button plus search text is not enough; assert the destination selected item, summary, and readiness state.
- Native `TreeView` group/null selection events can be transient during filtering or navigation. Do not clear selected media/player state unless the current filter or library state truly invalidates it.
- If the app claims a workflow is real, the smoke should prove at least one representative end-to-end path, not just that the screen opens.

## Product Surface Lessons

- WinUI product work should be native, direct, and player-safe. Avoid resurrecting Electron workbench assumptions as the product model.
- Keep technical details available but not dominant. Paths, hashes, offsets, codec/cache details, raw metadata, and command traces belong in details panels, evidence notes, or maintainer docs unless the user explicitly needs them.
- Every visible action should answer: what will happen, what file will be touched, whether the original stays unchanged, and what proof will exist afterward.
- Do not imply extracted media or models are live runtime proof. Say "cataloged", "extracted", "previewed", or "linked" when that is what was actually proven.
- Goodies are especially easy to overclaim. A Goodie row can be linked to catalog assets while runtime unlock criteria, wall placement, animation, and the in-game model viewer remain separate proof questions.
- Video Goodies should hand off to Media rather than pretending export or playback happens in the Asset Library row. The user should land on a selected video, not on a manual search chore.
- Avoid adding visual feature surfaces just because the data exists. If the next step is a Goodies wall/grid, design the interaction and test plan first.
- Do not let a useful catalog/export feature imply a game rebuild milestone. Showing a model wireframe, linked texture, or exported FBX proves that one tooling path works; it does not prove material assignment, animation, scripting, gameplay logic, or a from-scratch runtime.
- Goodies Browser ideas are product-design work. Record the source/runtime evidence and desired behavior, but do not start a new Goodies wall UI or textured model-viewer UI without an explicit design/test slice.
- In visual browsers, the selected object preview should stay primary. If an evidence/facts panel pushes artwork or model previews out of the first viewport, move or compact the facts and keep UIA assertions for the scrolled details.

## Static RE And Asset Lessons

- Static extraction output can come from source-shipped/reference assets, retail resource archives, or generated conversion products. Keep those categories separate in labels and evidence.
- For each asset claim, record whether it is found in the actual retail install, exported from a resource archive, derived from Stuart/source reference material, generated by an app/tool conversion, or still sample/mock data.
- When the user asks whether models, textures, or Goodies are actually extracted, answer with evidence buckets and counts, then list what remains unproven. Avoid collapsing "real extracted data" and "fully rendered product experience" into one claim.
- For Goodies Browser planning, separate FrontEnd art availability from runtime behavior. A catalog probe can prove Goodies icon/background/navigation textures exist and export to PNGs, but it does not prove the retail wall layout, animation, hit testing, unlock transition, or in-game model-viewer loop.
- For textured model work, distinguish direct texture-catalog rows from mesh-export sidecar textures. An FBX can have complete local sidecar coverage even when some texture names are not direct catalog rows; record both counts before calling a model "untextured" or "fully linked."
- If a private full-install catalog has direct texture links for every checked model row, it cannot prove the sidecar-only fallback UI. Use a deterministic fixture catalog with zero texture rows plus a local `MeshTextures` sidecar to test the `Preview sidecar texture` path, then separately rerun the private full-catalog breadth smoke.
- For Goodies provenance, prefer a direct read-only `goodie_*_res_PC.aya` archive census as the lowest-level guard before leaning on generated catalog/export outputs. The installed corpus can prove shipped archive count, wrapper tags, `GDIE -> GDAT` index/kind bytes, and the slot-232 archive gap without extracting private assets or launching the game.
- For Goodies model-viewer work, align three layers before product claims: source `GT_MESH` rules, installed `GDAT` kind bytes, and generated catalog Model rows. Then add narrow source-to-retail decompile guards for mesh deserialization, interaction/update branches, renderer dispatch context, and dynamic render queue/depth/LOD context before claiming behavior-level static confidence. Runtime in-game model-viewer behavior and textured WinUI rendering still need separate proof.
- Private full-install catalog smokes are strong product evidence for representative rows, but they still do not prove row-by-row coverage or public redistribution rights.
- Prefer read-only corpus scans before runtime probes. Runtime work is more expensive and riskier.
- When a recovered lookup table is small and bounded, add whole-table invariants instead of only sampled examples. The Goodies wall mapping is small enough to prove every visible index round-trips through the recovered coordinates.
- When a runtime reachability question spans several source layers, add a source-topology probe before planning runtime proof. Separate data definitions, resource helpers, unlock logic, coordinate mapping, selected-load flow, and cheat/display overrides so evidence can narrow the exact remaining gap.
- Source names are hypotheses until checked against retail binary/resources. Retail bytes, real saves, Ghidra xrefs, and runtime evidence are authority when they disagree.
- When adding a new source-only gameplay anchor, update both the positive source-coverage probe and the source-to-binary gap probe in the same wave. A green source scan is useful rebuild coverage, but it must still say "pending retail-binary identity" until Ghidra/read-back or runtime evidence closes that boundary.
- Keep source-anchor readiness notes focused on behavior facts and proof boundaries. Do not paste source excerpts or turn a token scan into a decompile/runtime claim.
- Source/read-back bridge probes are useful only when their claim is narrow. Name the exact source behavior, the exact retail helper/function notes being bridged, and the exact remaining gap such as missing control-flow identity or missing runtime proof.
- A bridge probe should write raw machine-readable evidence under ignored `subagents/` and publish only repo-relative paths, token names, counts, and explicit "not proven" boundaries.
- Do not rename Ghidra functions from a single weak signal. Use at least two signals such as source parity plus decompile behavior, or xrefs plus constants/strings.
- Read-only Ghidra inspection is allowed when useful. Ghidra mutation or project writes require an explicit mutation wave with dry-run, apply, read-back, and logs.
- Keep Ghidra GUI and headless modes separate. Headless runs need project locks clear and should be one-at-a-time.
- Run read-only Ghidra headless exports one-at-a-time too. Parallel exports can still collide on project locks, so rerun any lock-failed export serially before treating the evidence as usable.
- When the user asks to back up the actual Ghidra working project, copy the `.gpr` file and matching `.rep` directory to an out-of-repo backup location and verify file count, byte count, and project-file hash. Do not substitute repo evidence, exported TSVs, or release notes for the live Ghidra project backup.
- In Ghidra signature scripts, include the explicit `this` receiver in the parameter list for thiscall targets and treat Ghidra's saved read-back spelling as authority. If read-back exposes an inserted receiver or pointer normalization, preserve the mismatch log, update the script to the saved signature, rerun final dry/apply/read-back, and document the correction instead of deleting the evidence.
- On this workstation, locate the active Ghidra `.gpr` and matching `.rep` before backup instead of assuming the configured project root itself contains `BEA.gpr`. A zero-file backup means the source path was wrong, not that the backup succeeded.
- A timeout during Ghidra mutation does not prove rollback. Read back state before retrying.
- When launching Ghidra headless batch files from the Node REPL, `child_process.exec` with a fully quoted command string worked better than `execFile('cmd.exe', ['/d', '/s', '/c', ...])`; the latter can double-quote the batch path and fail before Ghidra starts.
- In the Windows/Codex lane, `tools/run_ghidra_batch_rename_headless.sh` can fail before Ghidra launch by expanding the repo path into a malformed `C:\mnt\c\...` preflight path. If standalone `ghidra_rename_map_preflight.py` already passed, rerun the same dry/apply operation directly through `analyzeHeadless.bat` and record the wrapper failure as tooling, not Ghidra mutation evidence.
- Ghidra headless may print extension manifest warnings and `REPORT: Save succeeded` during a no-analysis export script. Record those as tool-environment noise/project-save behavior unless the script itself mutates names, comments, signatures, bytes, or types.
- If Ghidra has function metadata but decompile export fails with `Bad decompile address`, do not assume the boundary is valid. Check whether `fn.getBody().contains(entry)` is true; if the body is empty or misses the entry, repair with a bounded data/instruction clear, decode, and explicit `setBody(range)` pass before applying semantic names/signatures.
- Probe assertions over Ghidra instruction exports should use the raw operands and call targets the exporter actually emits. Source-style labels in decompile output are useful, but they are not instruction evidence unless the TSV read-back contains them.
- When a tranche probe fails after apply, inspect metadata/xref/vtable TSV read-back before changing saved Ghidra state. Probe expectations can be wrong, especially for adjacent vtable slot order; the proof should follow the saved read-back evidence.
- Some real class evidence sits beyond the first few dozen vtable slots. Before concluding that a class does not own a body, make sure the vtable-slot exporter covers the needed slot range; Wave389 needed `ExportVtableSlots.java` widened from `32` to `256` slots to verify deep CGillM entries.
- Fresh read-only Ghidra exports are useful for upgrading older function notes into machine-checkable evidence. Keep the public claim to named-function read-back and selected body tokens when signatures remain undefined or exact source identity is not proven.
- Keep Ghidra read-back waves behavior-coherent and small enough to review. A target/profile helper batch is useful when every address supports the same subsystem question; mixing unrelated functions makes the public note harder to validate and easier to overclaim.
- Public Ghidra read-back notes should list the exact addresses, current names, token families, ignored raw-evidence path, and "not proven" boundaries. Future agents should be able to extend the evidence without opening private decompile files first.
- Source/read-back bridge checks should require the public readiness note and function notes to state the boundary explicitly. Related retail helper evidence can support a bridge, but it must not silently become proof of exact source identity, runtime behavior, or rebuild parity.
- When a source anchor includes a distinctive retail string or constant, use string xrefs plus fresh decompile tokens to build a candidate identity note before renaming. A candidate with strong string/constant evidence is still not final owner/name/signature proof until a deliberate rename/read-back wave closes it.
- Treat current Ghidra names as labels, not truth. A function currently named for one owner can still be a better candidate for a different source method; write the current name, inferred candidate meaning, and uncertainty separately.
- Do not treat "all named" or "recently commented" as "done." Saved Ghidra names, comments, and wrappers should remain candidates for reparse, downgrade, owner correction, signature/type hardening, tag cleanup, or replacement when later source, xref, vtable, constant, or runtime evidence disagrees.
- Reparse old semantic labels before building new claims on them. Names like `ctor_like` can be destructor-base bodies, and owner labels like `CUnit__...` can need correction to a base class such as `CActor__...` when source-parity, xrefs, and instruction read-back agree.
- When an old helper name sits in a neighboring source-owner cluster, verify surrounding source methods before preserving owner-specific labels. `0x00401b50` looked like a `CMCMine` scale helper, but source/decompile/xref review tied it to `CActor::GetFractionTime`.
- For destructor pairs, check the wrapper/body split before preserving old names. A real scalar-deleting destructor wrapper usually calls the base destructor, tests a delete flag, conditionally frees `this`, and returns `this`; the adjacent broad cleanup body is often the destructor-base target.
- By-value C++ returns often decompile as hidden output pointer params. Name those output params, such as `outRenderPos` or `outRenderOrientation`, when signatures are hardened so phantom `param_N` debt does not survive.
- When hardening a constructor-like Ghidra label, verify the real stack arity from instruction read-back before preserving decompiler parameters. A retail `ret 4` constructor can be a one-argument `__thiscall` ctor even when older decompiler output carried extra `param_N` artifacts.
- When deriving a string or data VA from retail bytes, record both the file offset and the VA/mapping assumption. Future agents should be able to re-run the xref export without repeating the byte-search step from scratch.
- Do not collapse candidate discovery, rename, and runtime proof into one wave. Candidate notes should be machine-checkable and public-safe first; rename/read-back and copied-profile runtime proof deserve their own deliberate gates.
- A probe that checks ignored raw Ghidra exports should also check the public note's "not proven" boundary. This prevents private decompile evidence from silently becoming an overbroad public claim.
- Caller xrefs can strengthen or weaken a candidate. If a source-looking candidate is reached through a surprising current owner path, document that path explicitly and keep the rename blocked until the object/signature story is resolved.
- When a caller decompile contains sibling source-behavior tokens, use that to refine the remaining gap instead of jumping straight to a rename. The right conclusion may be "activation/depletion behavior cluster found; source method boundaries still unresolved."
- Gap probes should distinguish no retail candidate, partial retail candidate, exact identity, and runtime proof. A source anchor with partial Ghidra evidence should not stay lumped into "source-only" if that hides progress, but it also should not graduate to exact identity.
- Negative function-name scans are triage, not absence proof. Record the exact export, row count, strict pattern, and zero-hit result, then keep decompile/control-flow/runtime identity open.
- Operand-token Ghidra searches need object-offset filtering. A token such as `0x5d8` can appear as an immediate address or vtable-like constant, so the proof row should separate raw operand-token rows from actual `[reg + offset]` object-field rows before drawing any RE conclusion.
- If a source-defined method has no direct source callsite in the checked source tree, document that before forcing a retail identity. The right next step may be a callback-chain hypothesis or copied-profile runtime proof, not another broad function-name or operand scan.
- When a source-to-binary gap has only remaining source-only anchors, a direct-name scan is useful as a guard but not as a promotion. If the all-functions export has zero strict matches, record the row count and patterns, keep the anchors source-only, and make the next wave a bounded decompile/control-flow search rather than claiming absence.
- A bounded decompile/control-flow search can promote an anchor to partial candidate even when the exact source method name is absent. Require source tokens, fresh read-only decompile tokens, constant/value read-back where relevant, and explicit language that inlining/reorganization and runtime behavior remain unproven.
- When promoting a source-only anchor to partial retail candidate, cite the bridge evidence file and update the source note, aggregate gap note, and guard probe together. Leaving any one of those stale will either overclaim exact identity or hide real progress.
- For retail gameplay candidates, prefer a cluster proof over a single-token proof: source tokens, current decompile index row, gate/order checks, field-offset operations, and read-only constant values should agree before reducing a source-only gap to partial-candidate status. Still leave exact method identity and runtime behavior unclaimed until separately proven.
- Value-token bridges count as partial candidate evidence only. Matching source constants and binary-doc constants can reduce a gap, but they do not prove exact retail function-body identity without decompile/read-back.
- One bridge evidence file may support multiple source anchors only when each anchor is named individually in the gap probe and the public note. Bundling multiple anchors into one vague partial claim makes later exact-identity work harder to audit.
- Do not let a strong transition-helper bridge absorb adjacent source anchors it does not prove. The Morph event/energy-gate bridge supports event and energy-gate anchors, but special-move transform rejection must stay source-only until separate read-back or runtime evidence covers it.
- Runtime-confirmed behavior can still be only partial source-identity evidence. The god-mode toggle has Steam UI/effect proof and source-compatible vulnerability tokens, but exact `CPlayer::SetIsGod` identity and environmental boundaries remain separate proof questions.
- Before launching a runtime proof, write the copied-profile proof matrix first. The matrix should name the exact question, copied artifacts, allowed mutations, private evidence outputs, stop checks, public-safe acceptance language, and what a green run still does not prove.
- Script/resource probes need evidence-domain labels. Loose text scripts, inflated packed resources, compiled/bytecode paths, and runtime-generated behavior are separate proof domains; a green literal-text scan narrows the question but must not be written as an impossibility proof.
- Runtime replay can produce useful yellow evidence. If bounded input stalls before the exact target sequence, record the loaded copied-save state, visible labels, input limitation, stop proof, and next harness improvement instead of promoting the run to reachability proof.
- When a runtime replay stalls against a known static invariant, add a named guard for the static invariant before rerunning runtime. Future runtime proof can then target a precise expected sequence instead of a vague screenshot memory.
- For runtime navigation questions, prefer an observer that logs game state or selected ids over screenshots alone. Screenshots prove visible state, but a debugger log can prove whether the runtime selected the expected id sequence.
- Before a runtime observer run, add a small parser or verifier for the expected log lines. That lets the later runtime pass fail on evidence shape instead of producing a private log that a future agent has to interpret by hand.
- Runtime observer parser tests should also guard the matching command file. A parser that only tests synthetic sample lines can go stale if breakpoint `.printf` text changes before the next copied-profile run.
- Runtime observer attach should use the exact managed game PID and prove the debugger log exists before sending proof input. Name-based attach can pick the wrong process or hide a failed CDB setup; a missing log is a setup failure, not gameplay evidence.
- CDB TCP server passwords should stay alphanumeric or underscore-only. A hyphenated password can make CDB exit before opening the log, which looks like a debugger/log failure unless the helper validates it first.
- On the current WinDbg/CDB package, direct local `-p <pid>` attach logs correctly, but `-server ... -p <pid>` can exit before opening the log. Runtime observer helpers should default to local attached logging and treat remote-server attach as separately unproven.
- For cloak/fire runtime questions, do not treat a post-input screenshot as a cloak-active baseline unless it contains an unmistakable visual cue. Prefer a latch/state observer and require the parser to prove activation before sending the fire input.
- Before sending runtime input for configurable controls, decode the active copied options file and preserve exact key identity. Generic `Shift` is not equivalent to `RShift`, and tutorial wording is weaker than current `defaultoptions.bea` binding evidence.
- CDB logs can splice warnings into observer output and can print multiple events on one physical line. Runtime log parsers should use repeated matches and include self-tests for noisy same-line events before treating event counts as evidence.
- CDB `gu` or other step-out commands inside breakpoint command strings can skip later commands for this target. Prefer explicit entry/return-path breakpoints for runtime observers, and document no-event results as input/state/setup gaps rather than behavior proof.
- Exact-PID CDB render observers can miss the first short no-input wait window immediately after attach while later input and wait windows are healthy. Treat this as a startup/render-hook warmup miss only when the failed artifact has zero render rows in window 1 and positive render rows in the later Q/wait/E windows; retry once into a fresh artifact root and keep the final accepted proof on the unchanged movement-state validator.
- For online/runtime proof ladders, source-bound compatibility is not runtime causality. A second-host command-source proof may share `upstreamPrivateLanProofHashMatch=true` with a host-authority private remote-client proof and still must keep `runtimeDrivenBySecondHostCommandSource=false` and `acceptedLiveSecondHostRuntimeDeliveryProof=false` until a direct second-host payload/session receipt is carried through scheduler, bridge, runtime, and CDB input windows. Executor validators must also enforce `bridgeProofSameBundleOwnership=true` so a stale or synthetic bridge proof cannot be paired with an unrelated enclosing proof.
- Separate binding-entry proof from gameplay dispatch proof. For cloak, decoded `Special function` keys were only half the story; the useful static bridge was controls remap `0x4C -> 0x3B` plus retail jump-table action `0x3B -> latch-helper call site`.
- When Ghidra has no function boundary around a relevant call site, export instruction context and decode small jump tables from read-only retail bytes before renaming or rerunning runtime input. A no-function call site can still be a real dispatch case.
- Runtime observers should log the gate inputs for the exact branch being tested, not only the final latch. For cloak, helper reachability without activation needs linked object `+0x2c`, linked object `+0xa0`, `this+0xfc`, and the threshold constant before the next runtime input wave.
- Avoid putting `gu` inside a hot render-loop CDB breakpoint when the proof target is an input handler. The first Goodies selection observer log was dominated by `get_goodie_number` render samples and CDB "commands were skipped" warnings, so future navigation proof should use after-call breakpoints inside `CFEPGoodies__ButtonPressed` or another focused handler path.
- CDB may print many breakpoint events onto one physical log line. Runtime log parsers should use repeated matches per line, not a single `search()` plus `continue`, or they can incorrectly downgrade real multi-event proof to an incomplete sequence.
- If a runtime observer proves input reaches a helper but the gate fields fail, move the next wave to state/object identification rather than broader key guessing or downstream behavior input. For cloak, linked object `+0xa0` not exceeding the threshold means fire-while-cloaked remains blocked until a cloak-active state is proven.
- When a runtime gate field maps to a likely source configuration field, add a source-to-retail guard before rerunning runtime. For cloak, source `mConfiguration->mStealth > 0` and retail profile `+0xa0 > 0` should drive the next setup/profile-selection probe.
- When a source class has pointer/list members, calculate the x86 field layout before naming a retail profile offset. For `CBattleEngineData`, `GenericSPtrSet` is 16 bytes in the 32-bit retail-compatible source layout, which places `mStealth` at `+0xa0` and `mConfigurationName` at `+0xa8`.
- Before rerunning a runtime observer, parse the smallest relevant read-only retail data file when source loader order is known. For cloak activation, `data/battle engine configurations.dat` shows `Sniper` is the only positive-`mStealth` profile, so runtime should target/verify `Sniper` before any fire-while-cloaked test.
- Inflated level resources are a separate setup-evidence domain from runtime proof. For level 710, parse the structural `BattleEngineConfigurations` header tables, not just raw string hits: read-only Ghidra export shows those names are loaded by `CWorld__LoadWorldHeader` and initial-spawn strings resolve into `CBattleEngineInitThing::mConfigurationId`, but that still does not prove a runtime transition into Sniper.
- When a single level-resource probe finds a promising setup target, immediately consider a read-only corpus index before runtime proof. The level configuration index showed base-world `Sniper` is limited to `710`, `720`, `731`, and `732`, which is more actionable than treating every runtime-table `Sniper` mention as equivalent.
- Broad scalar searches for small Goodie ids are noisy. For 71/72/73, separate stack/member offset hits from literal immediates, then focus review on Goodies/frontend/script/career-adjacent functions before treating any scalar hit as a hidden selector candidate.
- After a broad scalar scan yields a focused candidate queue, export bounded instruction context and decompile context before planning runtime work. The Goodies 71/72/73 focused queue classified as source-line/object-allocation metadata, stack cleanup/stride offsets, frontend page/icon state, virtual-keyboard constants, script runtime offsets, CRT noise, or texture parser offsets rather than direct selector evidence.

## Save And Patch Lessons

- Never synthesize `.bes` saves from scratch. Copy a known-good save or options file first.
- Retail save data is a true dword view at `file + 2`. Do not use old aligned-view offsets for writes.
- Preserve unknown save regions, padding, tails, and packed metadata unless the task is explicitly investigating them.
- Never patch the installed/original Steam `BEA.exe`. Patch copied profiles or app-owned artifact copies only.
- Executable patches need original-byte verification before apply and patched-byte verification afterward.
- Runtime-only/BSS flags cannot be made persistent by file patching unless a real file-backed code path exists.
- Windowed mode should use the proven copied-profile `force_windowed` patch path. Do not make `-forcewindowed` the primary product assumption.
- When AppCore already has a safe targeted save helper, expose or use that path for proof setup instead of ad hoc byte edits. Keep proof setup modes narrow and reject mixing with broad patch options so a copied-save runtime wave has a clean byte-level explanation.

## Release And Public-Safety Lessons

- Public release summaries must stay public-safe. Do not commit private screenshots, raw frames, full private paths, media caches, copied executables, raw proof JSON, or private game/save/media assets.
- `.codex/`, `subagents/`, `game/`, private `media/`, `save-attempts/`, state files, and operator directives are release-excluded by policy.
- If a tracked public doc is added or renamed, run the release manifest/profile checks and regenerate only when the check proves stale output.
- The curated release manifest lives at `release/readiness/curated_release_manifest.json`. Do not parse or document a nonexistent `release/curated_release_manifest.json` path.
- Do not let readiness reports imply unresolved blockers after follow-up commits fix them. Add post-fix traceability sections when needed.
- Commit hashes in evidence reports should be concrete when possible. If a report cannot contain its own final commit hash, state where traceability will be completed.
- Do not leave readiness notes or evidence tables with "pending final validation" language after validation has actually run. Replace pending language with exact command results before committing.
- Docs should describe current reality, not old strategy, planned behavior, or aspirational parity.
- Mirror docs must stay synchronized. When editing mirrored roadmap/lore-book docs, update both sides or run the tool that enforces the mirror.

## State And Handoff Lessons

- Update `developer_agent_state.json` for implementation, runtime, build, and test truth changes.
- Update `documentation_agent_state.json` for docs, release, evidence, and product-truth changes.
- Keep state JSON concise. Long narratives belong in readiness notes or campaign ledgers.
- The campaign progress ledger can be verbose, but it should still end each wave with remaining risks and next inspection target.
- Treat the lessons ledger as a real campaign artifact, not a nice-to-have. If the user has to correct the same class of behavior twice, update the durable lessons before the next complex wave.
- Keep both the active lessons file and lore-book mirror aligned. A lesson left only in chat or one mirror will be lost after compaction or handoff.
- When the user explicitly asks for more lessons, first audit this file and its mirror, then patch any missing reusable behavior before starting another product or RE slice.
- Do not mark the active `/goal` complete merely because a wave passed. Only complete it when the formal acceptance criteria are proven or remaining work is explicitly out-of-scope/speculative.
- At compaction or handoff, record branch and HEAD, dirty/clean status, last pushed commit, current wave, what was validated, what remains unproven, and exact paths for private evidence.
- After compaction, first re-read the active goal, `git status --short --branch`, HEAD, the latest pushed commits, and the active campaign state files. Do not restart an already-pushed wave just because the full prior transcript is gone.
- Treat chat summaries as navigation hints, not authority. The repo state, committed evidence files, current `git status`, and fresh validation output are the source of truth.
- Avoid stale temporal phrasing after compaction or long-running handoff. Say the concrete wave/date/status, not "just discussed" or other relative timing that implies live continuity the user did not experience.
- If the dirty tree already contains a partially documented wave, update that wave's evidence from pending to real results before adding a separate lesson or follow-up wave.
- If a compaction handoff says a small correction is still pending, inspect the current files before editing. The correction may already have landed in a partially completed wave, and duplicating it creates needless churn.
- If a prior wave is reported green and pushed, verify the branch/head and continue from the recorded next inspection target instead of re-opening old cleanup.
- If the user corrects an operating assumption, add a lesson immediately or in the next documentation batch. Repeated corrections are evidence that the operating contract needs to become durable repo memory.
- Keep "current capability," "representative proof," "runtime proof," and "future product slice" separate in state files. Blending those categories causes false confidence after handoff.
- When adding a new readiness note, cross-check nearby existing evidence before writing the "not proven" list. A fresh note must not accidentally downgrade already-proven historical proof, such as the copied-profile Goodies wall replay proving normal navigation skips from 70 to 74.
- Treat any "not proven" list as regression-sensitive documentation. Before publishing one, inspect the relevant readiness notes, state files, and latest campaign ledger entries so the note narrows the remaining gap instead of erasing proof from another lane.
- When new evidence refines an old claim, write the remaining gap precisely: for example, "hidden/non-grid reachability remains open" is safer than "runtime replay is not proven" when normal copied-profile wall replay is already documented.
- Record the proof domain beside each claim. Static source/Ghidra evidence, generated catalog evidence, copied-profile runtime evidence, packaged-app evidence, and future product slices are different confidence levels and should not be collapsed into one status sentence.
- A stealth/fade decompile pattern is not full cloak behavior. If a pass only proves interpolation or target-scaling context, record it as bounded candidate evidence and keep activation, energy burn, render flag identity, weapon-fired reset, and runtime behavior open.
- A transition helper can narrow transform special-move rejection without proving exact source methods. Treat retail state-machine or dash-lockout gates before transform branches as partial candidate evidence unless the jet/walker special-move methods are directly identified.
- When final evidence or state wording changes the doc-command checker count, rerun the checker and update the active wave only. Historical rows should keep the count they actually observed.
- Document lessons abundantly, but do not make the repo self-contradictory. Canonical reusable lessons belong here and in the lore-book mirror; command-level proof belongs in evidence ledgers; compact current truth belongs in state JSON.
- After Ghidra signature hardening, decompiler output can change semantic spelling, such as an integer-looking return becoming `return true`. Write focused probes against post-mutation read-back instead of stale pre-signature token text.
- If a caller decompile still contains `unaff_` or phantom `param_N` artifacts after a local signature guess, inspect the directly called helper signatures too. In the CThing hit tranche, hardening `CThing__CreateThingRefWithSquad` removed misleading caller artifacts and made the hit-dispatch claim reviewable.
- When a fresh Ghidra owner correction supersedes an older named-function row, update the older docs explicitly. The CAnimal correction showed that a prior `CAtmospheric__Destructor` label at `0x00404010` could survive in reference docs even after saved Ghidra was corrected, which would recreate false confidence during handoff.
- Shared no-op and return-zero vtable targets should be named as shared behavior when broad unrelated vtable owners point at the same body. Wave 339 corrected two owner-specific labels this way after `ExportVtableSlots.java` showed spawner-value and unrelated owners shared the same targets.

## Delegation Lessons

- Use subagents only for independent, bounded work that can run without blocking the immediate next local step.
- Worker agents should run with effective `gpt-5.5` and `xhigh` reasoning unless a higher-priority instruction forbids it.
- Give workers disjoint ownership. Tell them they are not alone in the codebase and must not revert other edits.
- Subagents should not edit repo state files. The main agent owns state and final integration.
- Read-only explorer output is useful for broad audits, but final claims still need local review and validation.

## What Is Still Not Proven By Current Work

- Full runtime Goodies behavior: unlock criteria, animation, live wall state, and in-game viewer behavior.
- Continuous frame streaming and semantic gameplay-state interpretation.
- Full static reconstruction of every model, texture, video, audio, script, and gameplay logic path.
- Signed/installer-grade WinUI release.
- Full public-source rebuild of the game from scratch.
- Broad packaged-runtime proof across every asset category and every media row.

## When To Add A Lesson

Add a lesson when a test passed but the screenshot revealed a visible issue, a command was flaky or misleading, a generated artifact changed for a non-obvious reason, a proof boundary was clarified, a repo strategy assumption changed, a runtime or RE workflow needed a safety correction, or a user had to correct the agent's operating assumption.

Do not add a lesson for routine implementation details that are already clear from code.
