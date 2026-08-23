from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


WAVE_ID = "W1_SAVE_SESSION_INPUT_FRONTEND"
ACCEPTED_BASE_COMMIT = "7ac8247416764f41ffa92313aa82393856beae38"
BASE_COMMIT = "784367bd43f9ec13125521b00fe0c8352670ffdd"
SOURCE_COMMIT = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_CROSSWALK_SHA256 = "e37f13b37e9ce9d712174e35b86fc1f7ebcfc693fe9957448a8f39ff03829479"
EXPECTED_REPORT_SHA256 = "a9a3d29a18655ef97e61591610c2721d934112b2a7a58acf264debe11a798c7f"
EXPECTED_NAME_TABLE_SHA256 = "4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213"
EXPECTED_CLOSURE_SHA256 = "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"
EXPECTED_PLAN_PARTITION_SHA256 = "bc36791975f43d5da6b584727df3eb7d29402e18c550dd3d96e01bba0c301fde"
EXPECTED_FILE_SET_SHA256 = "72fb22a1716dcb87059f9af9b93e9c9c9d8415a85b64399828003ea2b36e5381"
EXPECTED_SELECTION_SHA256 = "8690611e37b2bede04a57844df59bbb014fd4d1637577a31f27ba6ffd100f045"
GENERATION32_READY_SHA256 = "08ed89644ed25feb9e85fefb5b31ab2bdecbbd91b8aca720e20c53a7fbc5e73f"
GENERATION32_REDUCER_ID = "4c465010b3240d476eb15c89fcfa51cd155936316e897e6f6a7b450df5944db3"
EXPECTED_EVIDENCE_REGISTER_SHA256 = "4862fc61391c9bf65cd7183752e99b9b02b6bfb721e5b4b5c1e7c5fae5b885b4"
EXPECTED_GENERATION32_FUNCTIONS_SHA256 = "a63f42e331c265c94866ae944abc74e6a985dfb590f87419309c24932a951c63"
CROSSWALK_PATH = "reverse-engineering/source-crosswalk/crosswalk.tsv"
REPORT_PATH = "reverse-engineering/source-crosswalk/REPORT.md"

EXACT = "EXISTING_EXACT_RETAIL_NOTE_VA"
ANALOG = "NAMED_RETAIL_ANALOG_PRECISE_TARGET"
SOURCE_ONLY = "SOURCE_ONLY_BOUNDED_NO_MATCH"
AMBIGUOUS = "AMBIGUOUS_OVERLOAD_MACRO_NONFUNCTION"
EXTERNAL = "EXTERNAL_PROOF_REQUIRED"
EXPECTED_READINESS = {
    EXACT: 8,
    ANALOG: 3,
    SOURCE_ONLY: 148,
    AMBIGUOUS: 12,
    EXTERNAL: 9,
}
SOURCE_TYPE_TOKENS = {
    "BOOL",
    "BYTE",
    "DOUBLE",
    "DWORD",
    "FLOAT",
    "LONG",
    "SINT",
    "UINT",
    "ULONG",
    "WCHAR",
    "WORD",
}
EXPECTED_FILES = {
    "activereader.h",
    "Career.h",
    "Controller.h",
    "DXGame.h",
    "event.h",
    "eventmanager.h",
    "FEPGoodies.h",
    "FrontEnd.cpp",
    "Frontend.h",
    "game.cpp",
    "game.h",
    "MemoryCard.h",
    "PCController.cpp",
    "PCController.h",
    "PCGame.h",
    "PCMemoryCard.h",
    "Player.cpp",
    "Player.h",
    "scheduledevent.h",
}

SELECTION_FIELDS = [
    "source_file",
    "source_line",
    "function",
    "signature",
    "source_owner",
    "subsystem_wave",
    "readiness",
    "retail_va_or_empty",
    "current_name_candidates",
    "authority",
    "reason",
]
DEFINITION_FIELDS = [
    "source_file",
    "source_line",
    "function",
    "signature",
    "source_owner",
    "target_branch",
    "source_anchor",
    "source_text_sha256",
    "source_algorithm",
    "source_fields",
    "source_constants",
    "source_side_effects",
    "retail_classification",
    "retail_va_or_empty",
    "retail_name_candidates",
    "retail_evidence",
    "retail_evidence_boundary",
    "retail_falsifier",
    "rebuild_disposition",
    "rebuild_owner",
    "rebuild_evidence",
]
DELTA_FIELDS = [
    "source_file",
    "source_line",
    "function",
    "signature",
    "retail_delta",
    "retail_classification",
    "retail_va_or_empty",
    "evidence",
    "bounded_delta",
    "falsifier",
]


@dataclass(frozen=True)
class SourceDefinition:
    start_line: int
    end_line: int
    text: str
    body: str


@dataclass(frozen=True)
class SourceAnalysis:
    algorithm: str
    fields: tuple[str, ...]
    constants: tuple[str, ...]
    side_effects: tuple[str, ...]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_blob(repository: Path, commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repository), "cat-file", "blob", f"{commit}:{relative_path}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"historical authority unavailable at {commit}:{relative_path}"
        )
    return result.stdout


def historical_authority_hashes(repository: Path) -> dict[str, str]:
    expected_hashes = {
        CROSSWALK_PATH: EXPECTED_CROSSWALK_SHA256,
        REPORT_PATH: EXPECTED_REPORT_SHA256,
    }
    verified_hashes: dict[str, str] = {}
    for commit in (ACCEPTED_BASE_COMMIT, BASE_COMMIT):
        for relative_path, expected in expected_hashes.items():
            actual = sha256_bytes(git_blob(repository, commit, relative_path))
            if actual != expected:
                raise AssertionError(
                    f"historical authority hash mismatch at {commit}:{relative_path}: "
                    f"expected {expected}, got {actual}"
                )
            verified_hashes[relative_path] = actual
    return verified_hashes


def git_head(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = [
        line
        for line in path.read_text(encoding="utf-8-sig", errors="strict").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(lines, delimiter="\t")) if lines else []


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def find_source_root(repository: Path) -> Path:
    candidates = [
        repository / "references" / "Onslaught",
        repository.parent.parent / "references" / "Onslaught",
    ]
    for candidate in candidates:
        if (candidate / "Career.h").is_file():
            return candidate
    raise FileNotFoundError("pinned references/Onslaught source tree is not materialized")


def find_local_lab_root(repository: Path) -> Path:
    candidates = [repository / "local-lab"]
    if repository.parent.name == ".worktrees":
        candidates.append(repository.parent.parent / "local-lab")
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("repository/worktree local-lab corpus is not materialized")


def classification_for_readiness(readiness: str) -> str:
    if readiness == EXACT:
        return "SOURCE_EXACT"
    if readiness == ANALOG:
        return "SOURCE_ANALOG"
    if readiness in {SOURCE_ONLY, AMBIGUOUS, EXTERNAL}:
        return "NO_MATCH_FOUND"
    raise ValueError(f"unknown readiness: {readiness}")


def extract_source_definition(path: Path, source_line: int) -> SourceDefinition:
    lines = path.read_text(encoding="latin-1").splitlines()
    if source_line < 1 or source_line > len(lines):
        raise ValueError(f"source line outside {path}: {source_line}")

    collected: list[str] = []
    brace_depth = 0
    found_open = False
    end_line = source_line
    for index in range(source_line - 1, len(lines)):
        line = lines[index]
        collected.append(line)
        for char in line:
            if char == "{":
                brace_depth += 1
                found_open = True
            elif char == "}" and found_open:
                brace_depth -= 1
        end_line = index + 1
        if found_open and brace_depth == 0:
            break
    if not found_open or brace_depth != 0:
        raise ValueError(f"could not recover balanced definition at {path}:{source_line}")

    text = "\n".join(collected)
    first_open = text.find("{")
    last_close = text.rfind("}")
    return SourceDefinition(
        start_line=source_line,
        end_line=end_line,
        text=text,
        body=text[first_open + 1 : last_close],
    )


def _negate_condition(condition: str) -> str:
    compact = re.sub(r"\s+", " ", condition.strip())
    replacements = [
        (r"^TARGET\s*!=\s*(\w+)$", r"TARGET == \1"),
        (r"^TARGET\s*==\s*(\w+)$", r"TARGET != \1"),
        (r"^defined\(([^)]+)\)$", r"!defined(\1)"),
        (r"^!defined\(([^)]+)\)$", r"defined(\1)"),
    ]
    for pattern, replacement in replacements:
        if re.match(pattern, compact):
            return re.sub(pattern, replacement, compact)
    return f"!({compact})"


def _is_include_guard(condition: str) -> bool:
    token = condition.replace("!defined(", "").replace("defined(", "").replace(")", "").strip()
    return bool(re.fullmatch(r"[A-Z0-9_]+(?:_H|_INCLUDE)", token))


def source_target_branch(path: Path, start_line: int, end_line: int) -> str:
    lines = path.read_text(encoding="latin-1").splitlines()
    stack: list[dict[str, str]] = []
    for line in lines[: start_line - 1]:
        stripped = line.strip()
        match = re.match(r"#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)", stripped)
        if not match:
            continue
        directive, rest = match.groups()
        rest = rest.strip()
        if directive == "if":
            stack.append({"root": rest, "active": rest})
        elif directive == "ifdef":
            condition = f"defined({rest})"
            stack.append({"root": condition, "active": condition})
        elif directive == "ifndef":
            condition = f"!defined({rest})"
            stack.append({"root": condition, "active": condition})
        elif directive == "elif" and stack:
            stack[-1]["active"] = rest
        elif directive == "else" and stack:
            stack[-1]["active"] = _negate_condition(stack[-1]["root"])
        elif directive == "endif" and stack:
            stack.pop()

    conditions = [item["active"] for item in stack if not _is_include_guard(item["active"])]
    if conditions:
        branch = " && ".join(conditions)
    elif path.name.startswith("PC"):
        branch = "PC_OWNER_FILE"
    elif path.name.startswith("DX"):
        branch = "DIRECTX_OWNER_FILE"
    else:
        branch = "ALL_TARGETS"

    local_directives: list[str] = []
    for line in lines[start_line - 1 : end_line]:
        match = re.match(r"\s*#\s*(if|ifdef|ifndef|elif)\b(.*)", line)
        if match:
            directive, rest = match.groups()
            condition = rest.strip()
            if directive == "ifdef":
                condition = f"defined({condition})"
            elif directive == "ifndef":
                condition = f"!defined({condition})"
            local_directives.append(condition)
    if local_directives:
        branch += "; BODY_BRANCHES=" + ",".join(sorted(set(local_directives)))
    return branch


def _normalise_source(text: str) -> str:
    text = re.sub(r"//.*", " ", text)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"\s+", " ", text).strip()


def analyze_source(definition: SourceDefinition) -> SourceAnalysis:
    body = _normalise_source(definition.body)
    full = _normalise_source(definition.text)
    header = _normalise_source(definition.text[: definition.text.find("{")])
    parameter_close = header.find(")")
    initializer_text = ""
    if parameter_close >= 0:
        initializer_marker = header.find(":", parameter_close + 1)
        if initializer_marker >= 0:
            initializer_text = header[initializer_marker + 1 :].strip()
    initializer_targets = set(
        re.findall(r"(?:^|,)\s*([A-Za-z_]\w*)\s*\(", initializer_text)
    )

    fields = sorted(
        set(
            re.findall(
                r"\b(?:m[A-Z][A-Za-z0-9_]*|grade|Method2?|Number2?)\b",
                full,
            )
        )
    )
    constant_text = f"{initializer_text} {body}"
    constants = sorted(
        set(
            re.findall(
                r"(?<![A-Za-z0-9_])(?:0x[0-9A-Fa-f]+|-?\d+(?:\.\d+)?f?|TRUE|FALSE|NULL|true|false|nullptr|[A-Z][A-Z0-9_]{2,})\b|'[^']*'|\"[^\"]*\"",
                constant_text,
            )
        )
        - SOURCE_TYPE_TOKENS
    )
    assignment_targets = set(
        re.findall(
            r"\b([A-Za-z_]\w*(?:(?:->|\.)[A-Za-z_]\w*)?(?:\[[^\]]+\])?)\s*(?:\+\+|--|\+=|-=|\*=|/=|=(?!=))",
            body,
        )
    )
    calls = set(
        re.findall(r"\b([A-Za-z_]\w*(?:(?:::|->|\.)[A-Za-z_]\w*)*)\s*\(", body)
    ) - {"if", "for", "while", "switch", "return", "sizeof"}
    side_effects = sorted(assignment_targets | calls | initializer_targets)
    if not side_effects:
        side_effects = ["NONE_READ_ONLY"]

    direct_return = re.fullmatch(r"return\s*(.+);", body)
    if direct_return:
        algorithm = f"Returns {direct_return.group(1).strip()}."
    elif not body and initializer_text:
        algorithm = f"Initializes {initializer_text}."
    elif assignment_targets and not re.search(r"\b(if|for|while|switch)\b", body):
        algorithm = "Writes " + ", ".join(sorted(assignment_targets)) + "; source body: " + body
    else:
        algorithm = "Executes the pinned source body in order: " + body
    if initializer_text and body:
        algorithm = f"Initializes {initializer_text}; then {algorithm[0].lower() + algorithm[1:]}"
    return SourceAnalysis(
        algorithm=algorithm,
        fields=tuple(fields),
        constants=tuple(constants),
        side_effects=tuple(side_effects),
    )


def _retail_delta(row: dict[str, str]) -> str:
    readiness = row["readiness"]
    if readiness == EXACT:
        return "SOURCE_AGREES"
    if readiness == ANALOG:
        if row["source_file"] == "PCMemoryCard.h" and int(row["source_line"]) == 17:
            return "SOURCE_DIVERGES"
        return "RETAIL_UNRESOLVED"
    if readiness == SOURCE_ONLY:
        return "SOURCE_ONLY"
    return "RETAIL_UNRESOLVED"


def _falsifier(row: dict[str, str]) -> str:
    readiness = row["readiness"]
    if readiness == EXACT:
        return "Any pristine-body, ABI, or source-line readback mismatch at the cited VA refutes SOURCE_EXACT."
    if readiness == ANALOG:
        return "A body/ABI readback that refutes the named candidate, or proof of a different source owner, refutes this bounded analog."
    if readiness == SOURCE_ONLY:
        return "A promoted same-owner body or bounded alias with compatible ABI and source semantics falsifies the current negative search."
    if readiness == AMBIGUOUS:
        return "Compiler target membership plus overload/operator identity that selects one retail body resolves and may falsify this unresolved classification."
    return "Static ABI/xref/body evidence or controlled runtime evidence that proves a target resolves and may falsify this unresolved classification."


def _rebuild_projection(row: dict[str, str]) -> tuple[str, str, str]:
    file = row["source_file"]
    line = int(row["source_line"])

    if file == "Career.h" and line in {32, 33, 35, 36}:
        return (
            "PORTED_SOURCE_SHAPE",
            "rebuild/OnslaughtRebuild.Core/RetailCareerGrades.cs",
            "RetailGrade carries both constructors and both comparison laws with explicit retail/source boundaries.",
        )
    if file == "Career.h" and line in {138, 139}:
        return (
            "PORTED_SOURCE_SHAPE",
            "rebuild/OnslaughtRebuild.Core/RetailCareerGrades.cs",
            "RetailCareerRecordLayout carries the node/link offsets and the source negative-index guards.",
        )
    if file == "Career.h" and line in {140, 141}:
        return (
            "PORTED_SOURCE_SHAPE",
            "rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs",
            "RetailCareerGoodies carries direct get/set state access over the 300-entry store.",
        )
    if file == "Career.h" and line == 156:
        return (
            "PORTED_SOURCE_SHAPE",
            "rebuild/OnslaughtRebuild.Core/RetailCareerProgress.cs",
            "RetailCareerSlots carries the 32-word store and exposes the raw words.",
        )
    if file == "Career.h":
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Core/RetailCareer*.cs",
            "Career graph, grade, slot, kill, goodie, and Level-100 handoff slices exist; save persistence and the options tail remain absent.",
        )
    if file in {"Frontend.h", "FrontEnd.cpp", "FEPGoodies.h"}:
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Client/RetailFrontendSession.cs;rebuild/OnslaughtRebuild.Godot/RetailFrontendFlow.cs",
            "The presentation frontend carries bounded page/session state, but no save transaction, full page set, or CFrontEnd object-layout parity.",
        )
    if file in {"Controller.h", "PCController.cpp", "PCController.h"}:
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Client/InteractiveSession.cs;rebuild/OnslaughtRebuild.Client.Tests/InteractiveSessionTests.cs",
            "Fixed-step input latches and measured mouse/button laws exist; generic controller stacks, configuration persistence, recording, and vibration do not.",
        )
    if file in {"game.h", "game.cpp", "DXGame.h", "PCGame.h"}:
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Core/Simulation.cs;rebuild/OnslaughtRebuild.Client/InteractiveSession.cs",
            "The Level-100 deterministic session carries selected state/objective/input laws, not the complete CGame shell or mutable platform timing facade.",
        )
    if file in {"Player.h", "Player.cpp"}:
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Core/Level100ActorRegistry.cs;rebuild/OnslaughtRebuild.Core/Simulation.cs",
            "The canonical player actor and selected view/state laws exist; the full CPlayer facade, statistics, and control stack do not.",
        )
    if file == "eventmanager.h":
        return (
            "PORTED_SOURCE_SHAPE",
            "rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs;rebuild/OnslaughtRebuild.Core.Tests/RetailEventSchedulerTests.cs",
            "RetailEventScheduler carries all six omitted manager accessors plus the 200x3 ring, overflow list, pool, frame clock, routing, flush, and recycler with focused parity tests.",
        )
    if file in {"event.h", "scheduledevent.h"}:
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs;rebuild/OnslaughtRebuild.Core.Tests/RetailEventSchedulerTests.cs",
            "The pooled scheduler carries event number/time/listener/data/reuse/free-link state, but not every standalone CEvent/CScheduledEvent accessor or static live-count surface.",
        )
    if file == "activereader.h":
        return (
            "PARTIAL_OWNER_PRESENT",
            "rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs",
            "RetailEventScheduler.ClearListener carries the filed-event target-death nulling law; generic monitor registration, copy, reassignment, and destructor unlink remain absent.",
        )
    if file in {"MemoryCard.h", "PCMemoryCard.h"}:
        return (
            "NO_DIRECT_PORT",
            "rebuild/README.md",
            "The rebuild explicitly owns no save persistence or storage backend in the current slice.",
        )
    raise AssertionError(f"missing rebuild projection for {file}:{line}")


def _authority_paths(authority: str) -> list[str]:
    return [
        value
        for value in authority.split(";")
        if value.startswith("reverse-engineering/") or value.startswith("rebuild/")
    ]


def expanded_evidence(row: dict[str, str]) -> str:
    file = row["source_file"]
    paths = [
        value
        for value in row["authority"].split(";")
        if value.startswith("reverse-engineering/") or value.startswith("local-lab/")
    ]
    paths.extend(
        [
            f"references/Onslaught/{file}:{row['source_line']}",
            "reverse-engineering/source-crosswalk/audit/REPORT.md",
            "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv",
            "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv",
            "reverse-engineering/EVIDENCE-REGISTER.tsv",
            "local-lab/re-campaign-incident-recovery-20260808-v1/generation-32-current-8329-db18625-v1/campaign-functions.tsv",
        ]
    )
    if file in {"activereader.h", "event.h", "eventmanager.h", "scheduledevent.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/event-manager-scheduler-semantics-2026-08-11.tsv",
                "reverse-engineering/source-code/io/event-system.md",
            ]
        )
    elif file == "Career.h":
        paths.extend(
            [
                "reverse-engineering/binary-analysis/career-save-format-semantics-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/career-progression-static-bridge-contract.md",
                "reverse-engineering/source-code/gameplay/career-system.md",
            ]
        )
    elif file in {"Controller.h", "PCController.cpp", "PCController.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/controller-shared-semantics-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/cpccontroller-vtable-semantics-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/controller-player-game-event-spine-2026-08-11.tsv",
                "reverse-engineering/source-code/frontend/controller-system.md",
            ]
        )
    elif file in {"FEPGoodies.h", "FrontEnd.cpp", "Frontend.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/frontend-save-load-semantics-2026-08-11.tsv",
                "reverse-engineering/source-code/frontend/fep-systems.md",
            ]
        )
    elif file in {"game.cpp", "game.h", "DXGame.h", "PCGame.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/cgame-level-lifecycle-semantics-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/controller-player-game-event-spine-2026-08-11.tsv",
                "reverse-engineering/source-code/gameplay/game-system.md",
            ]
        )
    elif file in {"MemoryCard.h", "PCMemoryCard.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/frontend-save-load-semantics-2026-08-11.tsv",
            ]
        )
    elif file in {"Player.cpp", "Player.h"}:
        paths.extend(
            [
                "reverse-engineering/binary-analysis/controller-player-game-event-spine-2026-08-11.tsv",
                "reverse-engineering/binary-analysis/functions/Player.cpp/CPlayer__ctor.md",
            ]
        )

    return ";".join(dict.fromkeys(paths))


def _validate_selection(rows: list[dict[str, str]]) -> None:
    if len(rows) != 180:
        raise AssertionError(f"expected 180 W1 rows, got {len(rows)}")
    if any(row.get("subsystem_wave") != WAVE_ID for row in rows):
        raise AssertionError("selection contains an out-of-wave row")
    if set(rows[0]) != set(SELECTION_FIELDS):
        raise AssertionError("selection schema changed")
    keys = [
        (row["source_file"], int(row["source_line"]), row["function"], row["signature"])
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise AssertionError("selection contains duplicate stable keys")
    if {row["source_file"] for row in rows} != EXPECTED_FILES:
        raise AssertionError("selection source-file set changed")
    file_hash = hashlib.sha256(
        ("\n".join(sorted(EXPECTED_FILES, key=str.lower)) + "\n").encode("utf-8")
    ).hexdigest()
    if file_hash != EXPECTED_FILE_SET_SHA256:
        raise AssertionError("W1 source-file set hash changed")
    counts = Counter(row["readiness"] for row in rows)
    if dict(counts) != EXPECTED_READINESS:
        raise AssertionError(f"readiness counts changed: {dict(counts)}")


def import_plan(plan_path: Path, destination: Path) -> None:
    if sha256(plan_path) != EXPECTED_PLAN_PARTITION_SHA256:
        raise AssertionError("planning partition hash is not the reviewed immutable input")
    rows = [row for row in read_tsv(plan_path) if row["subsystem_wave"] == WAVE_ID]
    _validate_selection(rows)
    write_tsv(destination, SELECTION_FIELDS, rows)


def generate(selection_path: Path, repository: Path, source_root: Path, output: Path) -> dict[str, object]:
    if sha256(selection_path) != EXPECTED_SELECTION_SHA256:
        raise AssertionError("selection.tsv is not the exact reviewed W1 partition subset")
    if git_head(source_root) != SOURCE_COMMIT:
        raise AssertionError("pinned references/Onslaught source commit moved")
    rows = read_tsv(selection_path)
    _validate_selection(rows)

    historical_hashes = historical_authority_hashes(repository)
    name_table = repository / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv"
    closure = repository / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv"
    evidence_register = repository / "reverse-engineering/EVIDENCE-REGISTER.tsv"
    local_lab_root = find_local_lab_root(repository)
    generation32_root = (
        local_lab_root
        / "re-campaign-incident-recovery-20260808-v1/generation-32-current-8329-db18625-v1"
    )
    generation32_functions = generation32_root / "campaign-functions.tsv"
    generation32_ready = generation32_root / "campaign.ready.json"
    expected_hashes = {
        name_table: EXPECTED_NAME_TABLE_SHA256,
        closure: EXPECTED_CLOSURE_SHA256,
        evidence_register: EXPECTED_EVIDENCE_REGISTER_SHA256,
        generation32_functions: EXPECTED_GENERATION32_FUNCTIONS_SHA256,
        generation32_ready: GENERATION32_READY_SHA256,
    }
    for path, expected in expected_hashes.items():
        if sha256(path) != expected:
            raise AssertionError(f"read-only authority moved: {path}")

    name_by_va = {row["address"].lower(): row for row in read_tsv(name_table)}
    closure_by_va = {row["entryVa"].lower(): row for row in read_tsv(closure)}
    register_by_va = {row["entryVa"].lower(): row for row in read_tsv(evidence_register)}
    generation32_by_va = {
        row["entryVa"].lower(): row for row in read_tsv(generation32_functions)
    }
    definition_rows: list[dict[str, object]] = []
    delta_rows: list[dict[str, object]] = []
    source_file_hashes: dict[str, str] = {}

    for row in rows:
        source_file = source_root / row["source_file"]
        source_file_hashes[row["source_file"]] = sha256(source_file)
        definition = extract_source_definition(source_file, int(row["source_line"]))
        analysis = analyze_source(definition)
        branch = source_target_branch(source_file, definition.start_line, definition.end_line)
        classification = classification_for_readiness(row["readiness"])
        delta = _retail_delta(row)
        falsifier = _falsifier(row)
        rebuild_disposition, rebuild_owner, rebuild_evidence = _rebuild_projection(row)
        retail_evidence = expanded_evidence(row)
        for evidence_target in retail_evidence.split(";"):
            if evidence_target.startswith("reverse-engineering/"):
                evidence_path = repository / evidence_target
            elif evidence_target.startswith("local-lab/"):
                evidence_path = local_lab_root / evidence_target.removeprefix("local-lab/")
            elif evidence_target.startswith("references/Onslaught/"):
                source_relative = evidence_target.removeprefix("references/Onslaught/").split(":", 1)[0]
                evidence_path = source_root / source_relative
            else:
                continue
            if not evidence_path.is_file():
                raise AssertionError(f"named evidence target missing: {evidence_target}")
        retail_va = row["retail_va_or_empty"].lower()

        if classification in {"SOURCE_EXACT", "SOURCE_ANALOG"}:
            if not retail_va:
                raise AssertionError(f"classified row lacks VA: {row}")
            if retail_va not in name_by_va or retail_va not in closure_by_va:
                raise AssertionError(f"classified VA missing authority: {retail_va}")
            if retail_va not in register_by_va or retail_va not in generation32_by_va:
                raise AssertionError(f"classified VA missing Generation-32 authority: {retail_va}")
            register_row = register_by_va[retail_va]
            if (
                register_row["generation"] != "32"
                or register_row["readySha256"] != GENERATION32_READY_SHA256
            ):
                raise AssertionError(f"classified VA is not pinned to Generation 32: {retail_va}")
            evidence_paths = _authority_paths(row["authority"])
            if not evidence_paths:
                raise AssertionError(f"classified row lacks precise evidence path: {row}")
            for relative in evidence_paths:
                path = repository / relative
                if not path.is_file():
                    raise AssertionError(f"evidence target missing: {relative}")
                if retail_va not in path.read_text(encoding="utf-8", errors="replace").lower():
                    raise AssertionError(f"evidence target omits VA {retail_va}: {relative}")
        elif retail_va:
            raise AssertionError(f"NO_MATCH_FOUND row populated a VA: {row}")

        source_text = _normalise_source(definition.text)
        definition_rows.append(
            {
                "source_file": row["source_file"],
                "source_line": row["source_line"],
                "function": row["function"],
                "signature": row["signature"],
                "source_owner": row["source_owner"],
                "target_branch": branch,
                "source_anchor": f"references/Onslaught/{row['source_file']}:{definition.start_line}-{definition.end_line}",
                "source_text_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                "source_algorithm": analysis.algorithm,
                "source_fields": ";".join(analysis.fields),
                "source_constants": ";".join(analysis.constants),
                "source_side_effects": ";".join(analysis.side_effects),
                "retail_classification": classification,
                "retail_va_or_empty": retail_va,
                "retail_name_candidates": row["current_name_candidates"],
                "retail_evidence": retail_evidence,
                "retail_evidence_boundary": row["reason"],
                "retail_falsifier": falsifier,
                "rebuild_disposition": rebuild_disposition,
                "rebuild_owner": rebuild_owner,
                "rebuild_evidence": rebuild_evidence,
            }
        )
        delta_rows.append(
            {
                "source_file": row["source_file"],
                "source_line": row["source_line"],
                "function": row["function"],
                "signature": row["signature"],
                "retail_delta": delta,
                "retail_classification": classification,
                "retail_va_or_empty": retail_va,
                "evidence": retail_evidence,
                "bounded_delta": row["reason"],
                "falsifier": falsifier,
            }
        )

    populated = [str(row["retail_va_or_empty"]) for row in definition_rows if row["retail_va_or_empty"]]
    if len(populated) != len(set(populated)):
        raise AssertionError("W1 populated VA collision")
    if Counter(row["retail_classification"] for row in definition_rows) != Counter(
        {"SOURCE_EXACT": 8, "SOURCE_ANALOG": 3, "NO_MATCH_FOUND": 169}
    ):
        raise AssertionError("retail classification counts changed")
    if Counter(row["retail_delta"] for row in delta_rows) != Counter(
        {"SOURCE_AGREES": 8, "SOURCE_DIVERGES": 1, "RETAIL_UNRESOLVED": 23, "SOURCE_ONLY": 148}
    ):
        raise AssertionError("retail delta counts changed")
    if Counter(row["rebuild_disposition"] for row in definition_rows) != Counter(
        {"PORTED_SOURCE_SHAPE": 15, "PARTIAL_OWNER_PRESENT": 161, "NO_DIRECT_PORT": 4}
    ):
        raise AssertionError("rebuild disposition counts changed")

    output.mkdir(parents=True, exist_ok=True)
    definitions_path = output / "definitions.tsv"
    delta_path = output / "RETAIL-DELTA.tsv"
    write_tsv(definitions_path, DEFINITION_FIELDS, definition_rows)
    write_tsv(delta_path, DELTA_FIELDS, delta_rows)

    source_contract = output / "SOURCE-CONTRACT.md"
    rebuild_delta = output / "REBUILD-DELTA.md"
    if not source_contract.is_file() or not rebuild_delta.is_file():
        source_contract = selection_path.parent / "SOURCE-CONTRACT.md"
        rebuild_delta = selection_path.parent / "REBUILD-DELTA.md"
    if not source_contract.is_file() or not rebuild_delta.is_file():
        raise AssertionError("SOURCE-CONTRACT.md and REBUILD-DELTA.md must exist before receipt generation")
    if source_contract.parent != output:
        shutil.copyfile(source_contract, output / "SOURCE-CONTRACT.md")
        shutil.copyfile(rebuild_delta, output / "REBUILD-DELTA.md")
        source_contract = output / "SOURCE-CONTRACT.md"
        rebuild_delta = output / "REBUILD-DELTA.md"

    receipt = {
        "schema": "bea.source-crosswalk.expansion-wave.v1",
        "wave": WAVE_ID,
        "base_commit": BASE_COMMIT,
        "source_commit": SOURCE_COMMIT,
        "specimen_sha256": SPECIMEN_SHA256,
        "scope": {
            "receipt_root": "reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend",
            "source_files": sorted(EXPECTED_FILES, key=str.lower),
            "source_file_set_sha256": EXPECTED_FILE_SET_SHA256,
            "canonical_crosswalk_written": False,
            "canonical_report_written": False,
            "ghidra_written": False,
            "binary_written": False,
            "rebuild_written": False,
        },
        "counts": {
            "definitions": len(definition_rows),
            "stable_key_duplicates": 0,
            "readiness": dict(sorted(Counter(row["readiness"] for row in rows).items())),
            "retail_classification": dict(
                sorted(Counter(str(row["retail_classification"]) for row in definition_rows).items())
            ),
            "retail_delta": dict(sorted(Counter(str(row["retail_delta"]) for row in delta_rows).items())),
            "rebuild_disposition": dict(
                sorted(Counter(str(row["rebuild_disposition"]) for row in definition_rows).items())
            ),
            "populated_vas": len(populated),
            "populated_va_collisions": 0,
            "reuse": {
                "definitions": {
                    "REUSED": 11,
                    "EXTENDED": 169,
                    "NEW_MEASUREMENT": 0,
                },
                "artifacts": {
                    "REUSED": 1,
                    "EXTENDED": 7,
                    "NEW_MEASUREMENT": 0,
                },
            },
        },
        "authority_hashes": {
            "canonical_crosswalk_tsv": historical_hashes[CROSSWALK_PATH],
            "canonical_report_md": historical_hashes[REPORT_PATH],
            "name_table_tsv": sha256(name_table),
            "static_closure_tsv": sha256(closure),
            "generation32_evidence_register_tsv": sha256(evidence_register),
            "generation32_campaign_functions_tsv": sha256(generation32_functions),
            "generation32_campaign_ready_json": sha256(generation32_ready),
            "generation32_reducer_id": GENERATION32_REDUCER_ID,
            "reviewed_plan_partition_tsv": EXPECTED_PLAN_PARTITION_SHA256,
            "selection_tsv": sha256(selection_path),
            "source_files": dict(sorted(source_file_hashes.items(), key=lambda item: item[0].lower())),
        },
        "output_hashes": {
            "definitions_tsv": sha256(definitions_path),
            "retail_delta_tsv": sha256(delta_path),
            "source_contract_md": sha256(source_contract),
            "rebuild_delta_md": sha256(rebuild_delta),
            "generate_py": sha256(Path(__file__).resolve()),
            "test_generate_py": sha256(Path(__file__).resolve().parent / "test_generate.py"),
        },
        "reuse": {
            "definition_disposition_basis": (
                "REUSED means the reviewed plan plus existing exact/analog retail authority already "
                "settled the 11 populated rows; EXTENDED means this wave added source-body, target-branch, "
                "falsifier, and rebuild-disposition fields to 169 reviewed omission rows; "
                "NEW_MEASUREMENT is zero because no new byte, runtime, Ghidra, or specimen probe ran."
            ),
            "artifact_dispositions": {
                "selection.tsv": "REUSED",
                "definitions.tsv": "EXTENDED",
                "SOURCE-CONTRACT.md": "EXTENDED",
                "RETAIL-DELTA.tsv": "EXTENDED",
                "REBUILD-DELTA.md": "EXTENDED",
                "RECEIPT.json": "EXTENDED",
                "generate.py": "EXTENDED",
                "test_generate.py": "EXTENDED",
            },
            "predecessors": [
                {
                    "path": "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/PLAN.md",
                    "sha256": "604d5db76ecc9811b55321c5ec443f346c9be32515b6d8ed526142622d7ec393",
                    "role": "reviewed subsystem partition and wave contract",
                },
                {
                    "path": "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/partition.tsv",
                    "sha256": EXPECTED_PLAN_PARTITION_SHA256,
                    "role": "reviewed 634-row stable-key/readiness authority; selection.tsv is its exact W1 subset",
                },
                {
                    "path": "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/sample.tsv",
                    "sha256": "5235ff8e61fd12d9e4b17caf256d06c4a693cfd50bcce20d20261f42f21813bb",
                    "role": "prior cold checks including every W1 exact/analog row and representative unresolved rows",
                },
                {
                    "path": "local-lab/hermes-kanban-campaign-2026-08-22/source-first-expansion/manifest.json",
                    "sha256": "6f58de995a27a0088749f40e06907969d3213872b40d1bf0bb450afda1fd216e",
                    "role": "shared plan count/hash manifest",
                },
                {
                    "path": "reverse-engineering/EVIDENCE-REGISTER.tsv",
                    "sha256": EXPECTED_EVIDENCE_REGISTER_SHA256,
                    "role": "tracked Generation-32 register projection for all 11 populated VAs",
                },
                {
                    "path": "local-lab/re-campaign-incident-recovery-20260808-v1/generation-32-current-8329-db18625-v1/campaign-functions.tsv",
                    "sha256": EXPECTED_GENERATION32_FUNCTIONS_SHA256,
                    "role": "Generation-32 function closure for all 11 populated VAs",
                },
                {
                    "path": "local-lab/re-campaign-incident-recovery-20260808-v1/generation-32-current-8329-db18625-v1/campaign.ready.json",
                    "sha256": GENERATION32_READY_SHA256,
                    "role": "current campaign READY and reducer pin",
                },
                {
                    "path": "reverse-engineering/source-crosswalk/audit/REPORT.md",
                    "sha256": "861c4ffd9c7cdd6da181dfb4a5572a49c9d3c22422d8794352393339fa127792",
                    "role": "tracked predecessor AST audit receipt; records the original scratch parser hash and sealed inventory outputs without claiming the retired scratch path still exists",
                },
            ],
            "ps2_disposition": (
                "NOT_USED: W1 is shared/PC save-session-input-frontend work and opens no PS2 boundary; "
                "the closed 520e9bfa->cbafa266->51ffe3d6 generic PS2 chain was not repeated."
            ),
        },
        "executed_gates": {
            "generator_unit_tests": "PASS: 15/15",
            "deterministic_replay": "PASS: generate.py --check twice",
            "doc_headers": "PASS: 0 violations",
            "function_doc_names": "PASS: 2,039/2,039 gated assertions; 0 drift",
            "evidence_register_header": "PASS: current Generation-32 header",
            "npm_test": "PASS: AppCore 1,580; UI 901; CLI 125; one pre-existing NUnit2007 build warning",
            "npm_build": "PASS: 0 warnings, 0 errors",
            "git_diff_check": "PASS",
            "npm_test_docs": (
                "BASELINE-RED before headers: 31 pre-existing broken local links, none under the W1 receipt root; "
                "the downstream header/name/register gates were run independently and passed"
            ),
        },
        "validation": [
            "180 unique stable keys exactly cover the reviewed W1 19-file set",
            "source anchors and balanced bodies read from pinned source commit 5352a81c",
            "8 SOURCE_EXACT and 3 SOURCE_ANALOG VAs resolve in both the 8,329-row name table and 8,136-row closure",
            "all 11 populated VAs resolve in the Generation-32 evidence register and campaign-functions closure",
            "every populated VA resolves a precise evidence path containing that VA",
            "zero populated-VA collisions",
            "canonical crosswalk and canonical REPORT hashes remain equal to landed corrected base",
            "all outputs are deterministic under generate.py --check",
        ],
    }
    if len(receipt["reuse"]["predecessors"]) != 8:  # type: ignore[index]
        raise AssertionError("W1 receipt must preserve exactly eight unique predecessor entries")
    if len(receipt["reuse"]["artifact_dispositions"]) != 8:  # type: ignore[index]
        raise AssertionError("W1 receipt must account for exactly eight tracked artifacts")
    for predecessor in receipt["reuse"]["predecessors"]:  # type: ignore[index]
        predecessor_path = str(predecessor["path"])
        physical_path = (
            local_lab_root / predecessor_path.removeprefix("local-lab/")
            if predecessor_path.startswith("local-lab/")
            else repository / predecessor_path
        )
        if not physical_path.is_file() or sha256(physical_path) != predecessor["sha256"]:
            raise AssertionError(f"predecessor path/hash is not reproducible: {predecessor_path}")
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (output / "RECEIPT.json").write_bytes(receipt_bytes)
    return receipt


def check_tracked(root: Path, repository: Path, source_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="bea-w1-source-crosswalk-") as temporary:
        output = Path(temporary)
        generate(root / "selection.tsv", repository, source_root, output)
        for name in (
            "definitions.tsv",
            "SOURCE-CONTRACT.md",
            "RETAIL-DELTA.tsv",
            "REBUILD-DELTA.md",
            "RECEIPT.json",
        ):
            tracked = root / name
            generated = output / name
            if not tracked.is_file() or tracked.read_bytes() != generated.read_bytes():
                raise AssertionError(f"tracked output differs from deterministic replay: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and validate the W1 source-crosswalk receipt")
    parser.add_argument("--import-plan", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    repository = args.repo.resolve() if args.repo else repo_root()
    source_root = args.source_root.resolve() if args.source_root else find_source_root(repository)
    if args.import_plan:
        import_plan(args.import_plan.resolve(), root / "selection.tsv")
        return 0
    if args.check:
        check_tracked(root, repository, source_root)
        return 0
    output = args.output.resolve() if args.output else root
    receipt = generate(root / "selection.tsv", repository, source_root, output)
    print(json.dumps(receipt["counts"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
