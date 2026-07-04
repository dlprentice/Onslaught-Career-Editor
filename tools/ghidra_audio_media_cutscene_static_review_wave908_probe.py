#!/usr/bin/env python3
"""Validate Wave908 audio/media/cutscene static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave908-audio-media-cutscene-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_audio_media_cutscene_static_review_wave908_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-static-review-2026-05-26.md"
STATIC_SYSTEM = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

FUNCTION_DOCS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CSoundManager__Init",
        "CSoundManager__PlaySample",
        "CSoundManager__LoadCompressedSampleBank",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "pcsoundmanager.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CPCSoundManager__CreateSampleFromData",
        "CPCSoundManager__DecodeADPCM",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "wavread.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CWaveSoundRead__Open",
        "WavRead__WaveReadFile",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "OggLoader.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "COggLoader__ThreadProc_ReadPathIntoBuffer",
        "COggFileRead__ReadDecodedPcm",
        "OggVorbisStream__ReadPcmSamples",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cutscene.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CCutscene__Load",
        "CCutscene__Start",
        "CCutscene__Update",
        "CCutscene__SetTrackSlotByFlag",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "RTCutscene.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CRTCutscene__BuildCurrentFrameOutputs",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Camera.cpp" / "_index.md": (
        "Wave908",
        "audio-media-cutscene-static-review-wave908",
        "CMovieCamera__GetPos",
        "CPanCamera__Update",
        "CGenericCamera__GetPos",
    ),
}

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified"

EXPECTED_FAMILIES = {
    "CSoundManager": 34,
    "CPCSoundManager": 20,
    "CMusic": 11,
    "CWaveSoundRead": 11,
    "COggFileRead": 9,
    "COggLoader": 4,
    "OggVorbisStream": 2,
    "CSample": 2,
    "CPCSample": 2,
    "WavRead": 2,
    "Audio": 1,
    "CSoundEvent": 1,
    "CBinkOpenThread": 9,
    "CDXFMV": 4,
    "CFMV": 1,
    "CCutscene": 14,
    "CRTCutscene": 12,
    "CCutsceneAnimNode": 1,
    "CMovieCamera": 10,
    "CGenericCamera": 4,
    "CThingCamera": 2,
    "CControllableCamera": 3,
    "CViewPointCamera": 1,
    "CPanCamera": 9,
    "CInterpolatedCamera": 1,
    "CCamera": 1,
}

EXPECTED_CLUSTERS = {
    "audio-core": 36,
    "audio-backend": 24,
    "music-streaming": 11,
    "audio-readers": 28,
    "fmv-bink": 14,
    "cutscene": 27,
    "camera": 31,
}

REQUIRED_ANCHORS = (
    "CSoundManager__Init",
    "CSoundManager__CreateSample",
    "CSoundManager__PlaySample",
    "CSoundManager__FadeTo",
    "CSoundManager__LoadCompressedSampleBank",
    "CPCSoundManager__CreateSampleFromData",
    "CPCSoundManager__CreateSoundBuffer",
    "CPCSoundManager__DecodeADPCM",
    "CMusic__Init",
    "CMusic__UpdateStatus",
    "CWaveSoundRead__Open",
    "COggLoader__ThreadProc_ReadPathIntoBuffer",
    "OggVorbisStream__ReadPcmSamples",
    "COggFileRead__ReadDecodedPcm",
    "CBinkOpenThread__WorkerMain",
    "CDXFMV__ctor_base",
    "CDXFMV__VFunc_06_0053f180",
    "CFMV__PlayFullscreenWithLoadingGate",
    "CCutscene__Load",
    "CCutscene__Start",
    "CCutscene__Update",
    "CCutscene__SetTrackSlotByFlag",
    "CRTCutscene__BuildCurrentFrameOutputs",
    "CMovieCamera__GetPos",
    "CMovieCamera__GetOrientation",
    "CPanCamera__Update",
    "CGenericCamera__GetPos",
    "CCamera__GetAspectRatio",
)

CORE_ANCHORS = (
    "Wave908",
    "audio-media-cutscene-static-review-wave908",
    "static-coherent audio/media/cutscene/camera core",
    "6113/6113 = 100.00%",
    "171",
    "26",
    "CSoundManager",
    "34",
    "CPCSoundManager",
    "20",
    "CCutscene",
    "14",
    "CRTCutscene",
    "12",
    "CMusic",
    "11",
    "CWaveSoundRead",
    "11",
    "CMovieCamera",
    "10",
    "COggFileRead",
    "9",
    "CBinkOpenThread",
    "9",
    "CPanCamera",
    "9",
    *REQUIRED_ANCHORS,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime audio behavior proven",
    "runtime video behavior proven",
    "runtime cutscene behavior proven",
    "runtime camera behavior proven",
    "runtime directsound playback proven",
    "all systems complete",
    "every system is complete",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def clean_signature(signature: str) -> bool:
    return bool(signature) and not signature.startswith("undefined ") and not re.search(r"\bparam_\d+\b", signature)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(all(clean_signature(row.get("signature", "")) for row in rows), "quality TSV has unclean signature", failures)


def check_artifacts(failures: list[str]) -> None:
    baseline = read_json(BASE / "audio-media-cutscene-baseline.json")
    require(baseline.get("tag") == "audio-media-cutscene-static-review-wave908", "baseline tag mismatch", failures)
    require(baseline.get("classification") == "static-coherent audio/media/cutscene/camera core", "baseline classification mismatch", failures)
    require(baseline.get("selectedRows") == 171, "baseline selected rows mismatch", failures)
    require(baseline.get("selectedFamilies") == 26, "baseline family count mismatch", failures)
    require(baseline.get("commentedRows") == 171, "baseline commented rows mismatch", failures)
    require(baseline.get("cleanSignatureRows") == 171, "baseline clean rows mismatch", failures)
    require(baseline.get("missingRequiredAnchors") == [], "baseline missing anchors", failures)
    require(baseline.get("clusterCounts") == EXPECTED_CLUSTERS, "baseline cluster counts mismatch", failures)
    require(baseline.get("familyCounts") == EXPECTED_FAMILIES, "baseline family counts mismatch", failures)

    family_rows = read_tsv(BASE / "audio-media-cutscene-family-summary.tsv")
    cluster_rows = read_tsv(BASE / "audio-media-cutscene-cluster-summary.tsv")
    anchor_rows = read_tsv(BASE / "audio-media-cutscene-function-anchors.tsv")
    require({row["family"]: int(row["rows"]) for row in family_rows} == EXPECTED_FAMILIES, "family summary mismatch", failures)
    require({row["cluster"]: int(row["rows"]) for row in cluster_rows} == EXPECTED_CLUSTERS, "cluster summary mismatch", failures)
    require(len(anchor_rows) == 171, "anchor row count mismatch", failures)
    require(all(row.get("status") == "OK" for row in anchor_rows), "anchor status not OK", failures)
    require(all(row.get("comment", "").strip() for row in anchor_rows), "anchor missing comment", failures)
    require(all(clean_signature(row.get("signature", "")) for row in anchor_rows), "anchor unclean signature", failures)
    anchor_names = {row["name"] for row in anchor_rows}
    for name in REQUIRED_ANCHORS:
        require(name in anchor_names, f"missing required anchor: {name}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in FUNCTION_DOCS.items():
        text = read_text(path)
        for token in tokens + (BACKUP_PATH,):
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-audio-media-cutscene-static-review-wave908")
        == r"py -3 tools\ghidra_audio_media_cutscene_static_review_wave908_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_artifacts(failures)
    check_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave908 audio/media/cutscene static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave908 audio/media/cutscene static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
