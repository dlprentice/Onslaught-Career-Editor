# Lane 06 Save/Options Format Claim Audit (Read-only)

Date: 2026-03-04
Scope: `BesFilePatcher.cs`, `patcher.py`, `reverse-engineering/save-file/**`, `AGENTS.md` save-format sections, skills `bes-file-format` + `critical-patterns`.

## Outcome
- Core save/options format behavior is aligned across code + docs for:
  - true dword offsets (`file_off = 0x0002 + career_off`)
  - options entries/tail placement (`0x24BE`, tail=`file_size-0x56`)
  - `defaultoptions.bea` vs `.bes` load semantics (`flag=0` vs `flag=1`)
  - kill-counter packed encoding + top-byte preservation policy.
- Found 1 high-risk contradiction and 2 lower-risk wording/guardrail gaps.

## Findings

### 1) High: `AGENTS.md` contradicts itself on `0x249A` semantics
Evidence:
- Marks `0x249A` as unused/padding: `AGENTS.md:190`.
- Later says `0x249A` is part of invert-Y toggle offsets: `AGENTS.md:275`.
- Code/docs/skills consistently treat `0x249A` as reserved/unused:
  - `reverse-engineering/save-file/save-format.md:153`, `:281`
  - `reverse-engineering/save-file/struct-layouts.md:22`, `:292`
  - `/home/dlprentice/.codex/skills/bes-file-format/SKILL.md:42`
  - `/home/dlprentice/.codex/skills/critical-patterns/SKILL.md:63`

Risk:
- A reader following `AGENTS.md:275` could incorrectly patch `0x249A`, touching a reserved dword.

Suggested fix:
- Change `AGENTS.md:275` invert-Y list to `0x249E/0x24A2/0x24A6/0x24AA` (remove `0x249A`).

### 2) Medium: `patcher.py` docstring understates options-copy span
Evidence:
- Docstring says `copy_options_entries` copies a single `0x20-byte` block: `patcher.py:633`.
- Actual implementation copies full entries region `0x20*N`: `patcher.py:775-777`.
- CLI help and docs already describe `0x20*N`: `patcher.py:54`, `:1728`; `save-format.md:348-349`.

Risk:
- Integrators reading function docs may assume one-entry copy behavior and build wrong wrappers/tests.

Suggested fix:
- Reword `patcher.py:633` to “include options entries region (`0x20*N` bytes, starting at `0x24BE`).”

### 3) Medium-Low: Controller-config guidance is documented but not enforced
Evidence:
- Docs recommend values `1..4`: `reverse-engineering/save-file/save-format.md:321-334`.
- Python accepts any `0..0xFFFFFFFF`: `patcher.py:749-757`.
- C# writes any `uint` override without range guard: `BesFilePatcher.cs:867-870`.

Risk:
- Users can write undefined controller config values while docs imply only 1..4 are sane.

Suggested fix:
- Either enforce `1..4` (strict) or keep permissive writes but emit explicit warning for out-of-range values.

## Confirmed Alignment (No Mismatch Found)
- `defaultoptions.bea` behavior and `.bes` load caveat align in docs and both codepaths:
  - `AGENTS.md:160-167`
  - `reverse-engineering/save-file/save-format.md:286-295`
  - `BesFilePatcher.cs:259-261`, `:286-288`
  - `patcher.py:1158`, `:1184-1189`
- Kill packed encoding + meta preservation align:
  - `save-format.md:147`, `:175`
  - `BesFilePatcher.cs:903-911`
  - `patcher.py:700-716`
- Options entries/tail layout claims align:
  - `save-format.md:162-164`, `:397-401`
  - `BesFilePatcher.cs:484-503`
  - `patcher.py:227-253`, `:1170-1191`

## Notes
- Read-only audit only.
- No state-file changes were made (`developer_agent_state.json` / `documentation_agent_state.json` untouched).
