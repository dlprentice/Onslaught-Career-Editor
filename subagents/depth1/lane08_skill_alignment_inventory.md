# Skill Alignment Inventory (Lane 08)

## Summary
This repository is primarily a `.bes`/`.bea` save-editor + RE documentation project with active C#/Python parity work and a pinned-but-operationally-sensitive Ghidra MCP workflow. The most relevant Codex skills are those covering save-file semantics, binary/cheat analysis, and RE evidence discipline. Highest drift risk is concentrated where runtime/tooling behavior and retail-vs-source assumptions can change quickly.

## Relevant Skills

| Skill | Relevance to this repo | Current priority |
|---|---|---|
| `bes-file-format` | Directly maps to core `.bes` patch/analyze workflows (`BesFilePatcher.cs`, `patcher.py`, save docs). | Critical |
| `career-file-format` | Complements `.bes` modeling/terminology and career progression semantics used across app + docs. | Critical |
| `critical-patterns` | Encodes known foot-guns (true dword view, packed bits, preservation rules) that historically caused corruption/crashes. | Critical |
| `binary-patching` | Needed for `patches/` and executable-level experiments plus cave/offset translation discipline. | High |
| `cheat-codes` | Needed for runtime-only god mode and cheat table investigations (`cheat-codes.md`, decode tooling). | High |
| `ghidra-analysis` | Core for function/xref/decompile workflows and MCP-driven rename/signature/documentation loops. | High |
| `stuart-source-code` | Important reference lane for source-to-binary mapping while respecting “source != retail layout” constraints. | High |
| `onslaught-controls` | Relevant to options entries/tail snapshot and control binding interpretation. | Medium-High |
| `documentation-standards` | Useful for keeping RE notes/indexes and mutation evidence records consistent and auditable. | Medium |
| `onslaught-architecture` | Supports subsystem ownership inference and naming confidence during binary analysis. | Medium |
| `aya-resource-format` | Repo includes AYA extraction references and tooling context; secondary to save/editor lane currently. | Medium-Low |
| `aya-file-format` | Same as above, useful when media/asset lanes are reopened. | Medium-Low |
| `aya-asset-format` | Same as above; contextual relevance for extraction/debug tasks. | Medium-Low |
| `texture-extraction` | Relevant for media extraction workflows, not current primary execution lane. | Low-Medium |
| `fbx-export` | Relevant for AYA mesh export chain, currently non-primary for active app delivery scope. | Low-Medium |
| `aya-architecture` | Contextual for extractor internals; secondary in current project focus. | Low |
| `aya-development` | Build/debug support for extractor references; secondary lane. | Low |
| `msl-scripting` | Potentially relevant for mission/script analysis tasks; not core to save editor baseline. | Low |

## High-Risk Drift Candidates

| Skill | Why drift risk is high | Typical failure mode if stale |
|---|---|---|
| `bes-file-format` | Offsets/semantics are strict and corrected over time (retail true-dword view, tail behavior, packed counters). | Corrupt saves, wrong field writes, false regressions |
| `critical-patterns` | Captures historical bug-prevention rules that are easy to forget during refactors. | Reintroduction of known corruption bugs |
| `binary-patching` | Hook/cave and VA-to-file assumptions can shift with new experiments and validation. | Incorrect patches or misleading disassembly conclusions |
| `cheat-codes` | Runtime gating/call-site evidence evolves as RE deepens (e.g., “decoded but unverified” statuses). | Incorrect user-facing claims about god mode/cheats |
| `ghidra-analysis` | MCP/runtime behavior changes by plugin/bridge version and transport health rules. | Mutation scripts that “succeed” without real commits/read-back |
| `stuart-source-code` | Constant risk of over-trusting internal PC source for retail port layout details. | Bad offset mapping and incorrect inferred behavior |
| `onslaught-controls` | Control bindings/options tail interpretation may shift with new BEA.exe findings. | Wrong config edits or incorrect UI assumptions |
| `career-file-format` | Secondary abstractions can lag behind concrete `.bes` corrections. | Inconsistent docs/CLI/UI behavior across lanes |

## Verification Targets

1. Save-format ground truth
- `AGENTS.md` sections: Critical Rules, File Format (.bes), defaultoptions/god-mode/cheat notes.
- `reverse-engineering/save-file/save-format.md`
- `reverse-engineering/save-file/struct-layouts.md`
- `reverse-engineering/save-file/grade-system.md`
- `reverse-engineering/save-file/kill-tracking.md`
- `reverse-engineering/save-file/goodies-system.md`

2. Runtime cheat and controls evidence
- `reverse-engineering/game-mechanics/cheat-codes.md`
- `reverse-engineering/game-mechanics/god-mode.md`
- `tools/cheat_table_decode.py`
- `tools/options_entries_decode.py`

3. Authoritative implementation parity
- `BesFilePatcher.cs` (authoritative C# engine)
- `patcher.py` (Python parity CLI)
- `Program.cs` (CLI wiring/flags)
- `onslaught_explorer.py` (GUI parity surface)

4. Ghidra/MCP operational validity
- `AGENTS.md` sections: Active MCP Configuration, guardrails, lock-step rules
- `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md`
- `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `reverse-engineering/binary-analysis/function_mutation_attempt_log.jsonl`
- `reverse-engineering/binary-analysis/function_mutation_ledger.jsonl`

5. Source-reference sanity checks (non-authoritative for retail layout)
- `references/Onslaught/Career.h`
- `references/Onslaught/Career.cpp`
- `references/Onslaught/CLIParams.h`
- `references/Onslaught/CLIParams.cpp`

6. Binary patch workflow anchors
- `patches/` (active experiments)
- `tools/run_ghidra_batch_rename_headless.sh`
- `tools/run_ghidra_headless_postscript.sh`
- `tools/GhidraBatchRename.java`
