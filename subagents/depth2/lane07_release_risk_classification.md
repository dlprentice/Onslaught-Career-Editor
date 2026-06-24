# Private/Public Release Risk Classification by Path Family (Lane 07)

## Scope
Classification is for release hygiene only (no implementation): which path families are safer for a **public branch/release** vs what should stay **private-only** by default.

Evidence basis used in this pass:
- Current tracked file distribution (notably: `reverse-engineering/**` 12,766, `game/**` 5,507, `media/**` 19)
- Existing repo guidance in `AGENTS.md` and `.gitignore`
- Observed path contents (game install payloads, media artifacts, RE scratch corpus, state/orchestration artifacts)

## Risk Classes
| Class | Meaning | Public policy stance |
|---|---|---|
| `R0` | Low release risk, authored source/docs, no obvious third-party payloads | Include by default |
| `R1` | Mostly safe but needs lightweight curation | Include with review |
| `R2` | Mixed provenance or feature-coupled/legal ambiguity | Conditional include (explicit gates) |
| `R3` | High legal/privacy/operational leakage risk | Exclude by default |
| `R4` | Private-only or redistribution-prohibited in practice | Hard exclude |

## Path-Family Classification Matrix
| Path family | Approx tracked volume | Primary risk vectors | Class | Candidate public posture | Candidate private posture |
|---|---:|---|---|---|---|
| `Program.cs`, `BesFilePatcher.cs`, `App*.cs`, `MainWindow*.xaml*`, `Views/**`, `Onslaught - Career Editor.csproj`, `Onslaught - Career Editor.sln` | ~core app set | Authored application code | `R0` | Include | Include |
| `patcher.py`, `onslaught/**`, `onslaught_explorer.py` | 21 | Authored Python implementation | `R0` | Include | Include |
| `OnslaughtCareerEditor.UiTests/**`, `tests_pyqt/**` | 9 | Test quality signal, low IP risk | `R0` | Include | Include |
| `README.MD`, `LICENSE`, root technical `.md` docs | ~15 | Documentation-only; confirm no embedded proprietary dumps | `R1` | Include with quick content scan | Include |
| `roadmap/**` | 16 | Planning metadata, low direct legal risk | `R1` | Include with curation for internal-only notes | Include |
| `lore/**` | 14 | Attribution/history text, potential quote/provenance concerns | `R1` | Include with citation sanity check | Include |
| `lore-book/**` | 496 | Curated lore + mirrored technical narratives; possible derivative excerpts | `R1` | Include with content review | Include |
| `reverse-engineering/save-file/**` | 10 | Technical findings; low binary payload risk | `R1` | Include with redaction of raw proprietary blobs if any | Include |
| `reverse-engineering/game-mechanics/**` | 4 | Reverse-engineering narrative, low artifact risk | `R1` | Include | Include |
| `reverse-engineering/project-meta/**` | 6 | Attribution/legal notes, low payload risk | `R1` | Include | Include |
| `reverse-engineering/source-code/**` | 22 | Source-parity notes may quote proprietary/internal sources | `R2` | Conditional include after quote-length/provenance review | Include |
| `reverse-engineering/game-assets/**` | 16 | Can drift into extracted asset metadata or proprietary structure exports | `R2` | Conditional include after per-file review | Include |
| `reverse-engineering/binary-analysis/functions/**` | 361 | Potential heavy derivative disassembly/decompile output | `R2` | Conditional include; prefer summarized docs over raw dumps | Include |
| `reverse-engineering/binary-analysis/*.jsonl` (mutation ledgers/logs/state) | small count, high sensitivity | Internal workflow telemetry, potentially noisy/sensitive operational residue | `R3` | Exclude by default | Include |
| `reverse-engineering/binary-analysis/scratch/**` | 12,317 | Massive transient archive; derivative dumps, workflow residue | `R4` | Hard exclude | Include |
| `reverse-engineering/binary-analysis` top-level curated `.md/.json` audits | dozens | Mixed; some safe docs, some raw export artifacts | `R2` | Conditional include with strict file-level allowlist | Include |
| `game/**` | 5,507 | Retail game binaries/assets/manuals/audio/video redistribution risk | `R4` | Hard exclude | Include |
| `BEA_Widescreen.exe`, `BEA.exe.gzf` | 2 | Executable/binary redistribution risk | `R4` | Hard exclude | Include (private workflows only) |
| `media/packaging/**`, `media/publications/**`, `media/wallpapers/**`, `media/portraits/**`, `media/flash/**` | 14 | Likely third-party/game-origin copyrighted media | `R4` | Hard exclude unless explicit documented permission | Include |
| `media/patches/**` | 1 | May contain third-party binary patch bundles | `R3` | Exclude by default; include only if license/provenance verified | Include |
| `media/generated-art/**` | 5 | Potentially original, but authorship/provenance still needed | `R2` | Conditional include with provenance note | Include |
| `references/Onslaught`, `references/AYAResourceExtractor` (gitlinks) | 2 | Submodule target visibility/license/ownership dependency | `R2` | Conditional include if URLs are public + license-compatible | Include |
| `.gitmodules` | 1 | Can expose private fork endpoints if misconfigured | `R2` | Include only after URL review | Include |
| `tools/*.py`, `tools/*.sh`, `tools/*.java` | 31 | Mostly authored utilities; some tightly coupled to private RE ops | `R2` | Conditional include via allowlist (utility scripts only) | Include |
| `patches/*.py`, `patches/archive/**` | 5 | Binary patch research; legal/redistribution ambiguity depending on payload | `R2` | Conditional include after payload/provenance review | Include |
| `save-attempts/*.bes`, `save-attempts/*.bea` | 15 | Game-derived binary files, possible user/profile fingerprints | `R3` | Exclude by default | Include |
| `discord_channel_dumps/**` | 11 | Conversation logs / privacy / consent risk | `R4` | Hard exclude | Include only if strictly necessary |
| `subagents/**` | growing | Internal orchestration artifacts and prompt residue | `R3` | Exclude by default | Include |
| `wave_online_audit*/**` | 8 | Internal audit artifacts and workflow outputs | `R3` | Exclude by default | Include |
| `*_state.json`, `*_state.json.tmp` | session files | Internal state/history leakage | `R3` | Exclude by default | Include |
| `bin/**`, `obj/**`, `.venv/**`, `__pycache__/**`, `.tmp_*` | generated | Build/runtime detritus | `R3` | Exclude | Exclude/optional |

## Candidate Public Include Policy (Allowlist-First)
Recommended candidate family allowlist for a public branch/release source snapshot:

1. Core authored app code and project files
- `*.cs`, `*.xaml`, `*.csproj`, `*.sln`
- `Views/**`, `onslaught/**`, `patcher.py`, `onslaught_explorer.py`

2. Tests and baseline docs
- `OnslaughtCareerEditor.UiTests/**`, `tests_pyqt/**`
- `README.MD`, `LICENSE`, selected root `.md`
- `roadmap/**`, `lore/**`, `lore-book/**` (reviewed)

3. Curated reverse-engineering documentation only
- Prefer explicit allowlist under `reverse-engineering/**` for narrative docs
- Keep `save-file/**`, `game-mechanics/**`, `project-meta/**` as first candidates
- Gate `source-code/**`, `game-assets/**`, `binary-analysis/functions/**` behind manual review

4. Utilities (curated)
- Include only reviewed `tools/**` and `patches/**` scripts that contain no proprietary payloads and no private-environment assumptions that leak sensitive details

## Candidate Public Exclude Policy (Denylist Baseline)
Recommended baseline denylist candidates for public branch/release packaging:

- `game/**`
- `media/packaging/**`
- `media/publications/**`
- `media/wallpapers/**`
- `media/portraits/**`
- `media/flash/**`
- `BEA_Widescreen.exe`
- `BEA.exe.gzf`
- `reverse-engineering/binary-analysis/scratch/**`
- `reverse-engineering/binary-analysis/*.jsonl`
- `reverse-engineering/binary-analysis/function_mutation_tracking_state.json`
- `save-attempts/**`
- `discord_channel_dumps/**`
- `subagents/**`
- `wave_online_audit*/**`
- `*_state.json`
- `*_state.json.tmp`
- `bin/**`, `obj/**`, `.venv/**`, `__pycache__/**`, `.tmp_*/**`

## Conditional Gates for `R2` Families
Before including any `R2` family publicly, apply all relevant gates:

1. Provenance gate
- Confirm authorship or redistribution permission is explicit and documented.

2. Derivative-content gate
- Prefer summaries over raw decompile/disassembly dumps.
- Remove long proprietary excerpts or raw binary-derived bulk artifacts.

3. Endpoint/privacy gate
- Verify no private URLs, machine-local absolute paths, or personal data appear.

4. Submodule gate
- Ensure `.gitmodules` points to public, intended remotes with compatible licensing.

5. Artifact payload gate
- For patch/media/tool bundles, ensure no embedded proprietary binaries are shipped inadvertently.

## Policy Candidate Profiles

### Public OSS Profile (Conservative)
- Use strict allowlist-first posture.
- Treat all `R3`/`R4` as excluded.
- Include `R2` only after explicit documented review.

### Private Collaboration Profile (Operational)
- Permit `R0`-`R2` broadly.
- Keep `R3` where operationally needed.
- Keep `R4` only where legally and workflow-justified within private boundaries.

## Highest-Priority Risk Families (Immediate Attention if Preparing Public Release)
1. `game/**` and root executable artifacts (`BEA_Widescreen.exe`, `BEA.exe.gzf`)
2. `reverse-engineering/binary-analysis/scratch/**`
3. `media/**` except possibly reviewed `media/generated-art/**`
4. `save-attempts/**`
5. `discord_channel_dumps/**`

## Open Decision Points (Policy, Not Implementation)
1. Whether any subset of `media/generated-art/**` is explicitly publishable with provenance notes.
2. Whether `reverse-engineering/binary-analysis/functions/**` should be published at all, or summarized into smaller curated docs.
3. Whether submodule pointers in `.gitmodules` should target upstream public repos for release-facing branches.
4. Whether `tools/**` should be split conceptually into public-safe vs private-ops families for easier policy enforcement.
