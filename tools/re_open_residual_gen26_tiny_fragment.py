#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gen26 tiny OPEN_DARK (1–3B) fragment instrument.

Exports OPEN_DARK residuals with size in 1..3 from Generation 26 tip.
Recovery lanes (TERMINAL_BOUNDED_AMBIGUITY or TERMINAL_PADDING):

  PREV_INSN_SPAN / JMP_OVER_FRAGMENT / SWITCH_CASE_ENTRY
    reused from unit-split static PE classifiers (same as OPEN_EXECUTED).

  EXACT_INSN
    residual bytes are exactly one complete instruction at startVa.

  EXACT_INSN_SEQ
    residual fully covered by sequential complete instructions starting
    at startVa (no open tail).

  PURE_PAD
    residual is pure 0x00/0x90/0xCC pad → TERMINAL_PADDING.

Does not mutate Gen26. Does not invent names or REBUILD_READY.
hold_generation_apply default True on plate; Gen27 apply is separate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_X86, CS_MODE_32, Cs
except ImportError:  # pragma: no cover
    Cs = None  # type: ignore

SCHEMA = "bea.re.open-residual-gen26-tiny-fragment.v1"
PACK_SCHEMA = "bea.re.open-residual-gen26-tiny-fragment-formal-pack.v1"
ADVANCE_KIND = "RESIDUAL_TERMINAL_OPEN_TINY_FRAGMENT.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
EXPECTED_OPEN_DARK = 98
EXPECTED_OPEN_EXECUTED = 0
EXPECTED_RESIDUALS = 6117
MAX_TINY = 3

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEN26 = Path(
    "local-lab/residual-terminal-generation26-unit-split-20260805-v1/"
    "generation-26-residual-terminal-unit-split"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/open-residual-gen26-tiny-fragment-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE re-decode: tiny fragment no longer matches unit-span / exact insn / pad; "
    "residual membership of a named body; REBUILD_READY claim"
)


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stamp(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha(path),
    }


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def try_exact_insn_seq(
    data: bytes, start: int, end: int, ib: int, secs, md, mass
) -> dict[str, Any] | None:
    """Residual fully covered by one or more complete insns starting at start."""
    n = end - start
    if n < 1 or n > MAX_TINY:
        return None
    # need a little over-read so capstone can finish last insn if it equals n
    blob = mass.span_bytes(data, start, end + 8, ib, secs)
    if blob is None or len(blob) < n:
        return None
    core = blob[:n]
    insns = list(md.disasm(blob, start))
    if not insns or insns[0].address != start:
        return None
    covered = 0
    seq: list[dict[str, Any]] = []
    for insn in insns:
        if covered >= n:
            break
        if insn.address != start + covered:
            return None
        if covered + insn.size > n:
            return None
        covered += insn.size
        seq.append(
            {
                "va": f"0x{insn.address:08x}",
                "mnemonic": insn.mnemonic,
                "op_str": insn.op_str,
                "size": insn.size,
                "bytesHex": insn.bytes.hex(),
            }
        )
    if covered != n or not seq:
        return None
    if len(seq) == 1:
        return {
            "lane": "EXACT_INSN",
            "shapeKind": f"EXACT_INSN/{seq[0]['mnemonic']}",
            "insns": seq,
            "note": f"exact {seq[0]['mnemonic']} {n}B",
        }
    return {
        "lane": "EXACT_INSN_SEQ",
        "shapeKind": "EXACT_INSN_SEQ/" + "+".join(i["mnemonic"] for i in seq),
        "insns": seq,
        "note": f"exact seq n={len(seq)} {n}B",
    }


def classify_tiny(
    data: bytes, start: int, end: int, ib: int, secs, md, mass, us_mod
) -> dict[str, Any] | None:
    n = end - start
    if n < 1 or n > MAX_TINY:
        return None
    blob = mass.span_bytes(data, start, end, ib, secs)
    if blob is None:
        return None
    if mass.is_pure_pad(blob):
        return {
            "lane": "PURE_PAD",
            "shapeKind": "PURE_PAD",
            "terminalState": "TERMINAL_PADDING",
            "note": f"pure pad {n}B",
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        }
    # unit-split lanes first (prev-insn / jmp-over / switch)
    unit = us_mod.classify_executed_unit(data, start, end, ib, secs, md, mass)
    if unit is not None:
        return {
            **unit,
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        }
    exact = try_exact_insn_seq(data, start, end, ib, secs, md, mass)
    if exact is not None:
        return {
            **exact,
            "terminalState": "TERMINAL_BOUNDED_AMBIGUITY",
            "peBytesSha256": hashlib.sha256(blob).hexdigest(),
        }
    return None


def proposed_for(rec: dict[str, Any]) -> dict[str, Any]:
    term = rec.get("terminalState") or "TERMINAL_BOUNDED_AMBIGUITY"
    return {
        "classification": "PADDING" if term == "TERMINAL_PADDING" else "CODE_CANDIDATE",
        "classificationVerdict": f"STATIC_TINY_FRAGMENT/{rec['lane']}",
        "terminalState": term,
        "campaignState": term,
        "bytePattern": (
            "PAD_BYTES" if term == "TERMINAL_PADDING" else "MIXED_OR_CODE_LIKE_BYTES"
        ),
        "contractState": term,
        "shapeKind": rec["shapeKind"],
        "recoveryLane": rec["lane"],
        "requiresQuestionSupersession": True,
        "cheapestFalsifier": DEFAULT_FALSIFIER,
        "sourceState": "OPEN_DARK_RESIDUAL",
    }


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    if Cs is None:
        raise SystemExit("capstone required")
    mass = _load_mod(
        "re_open_dark_code_like_mass", ROOT / "tools" / "re_open_dark_code_like_mass.py"
    )
    us_mod = _load_mod(
        "re_open_residual_gen25_ttd_unit_split",
        ROOT / "tools" / "re_open_residual_gen25_ttd_unit_split.py",
    )

    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation") or 0) != 26:
        raise SystemExit(f"expected Gen26, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != "RESIDUAL_TERMINAL_OPEN_UNIT_SPLIT":
        raise SystemExit(f"unexpected advance {(ready.get('advance') or {}).get('kind')}")

    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    if len(residuals) != EXPECTED_RESIDUALS:
        raise SystemExit(f"residuals {len(residuals)}")
    dark = [r for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL"]
    executed = [
        r for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    ]
    if len(dark) != EXPECTED_OPEN_DARK:
        raise SystemExit(f"OPEN_DARK {len(dark)}")
    if len(executed) != EXPECTED_OPEN_EXECUTED:
        raise SystemExit(f"OPEN_EXECUTED {len(executed)}")

    tiny = []
    for r in dark:
        b = int(r["endVa"], 16) - int(r["startVa"], 16)
        if 1 <= b <= MAX_TINY:
            tiny.append(r)

    out_dir.mkdir(parents=True, exist_ok=True)
    export_cols = [
        "entityKey",
        "startVa",
        "endVa",
        "bytes",
        "observationState",
        "campaignState",
        "questionIds",
        "prevFunc",
        "nextFunc",
        "cheapestFalsifier",
    ]
    _write_tsv(out_dir / "open-dark-tiny.tsv", export_cols, tiny)
    _write_tsv(out_dir / "open-dark.tsv", export_cols, dark)

    data = specimen.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    ib, secs = mass.pe_map(data)
    md = Cs(CS_ARCH_X86, CS_MODE_32)

    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    lane_counts: Counter = Counter()

    for r in tiny:
        start = int(r["startVa"], 16)
        end = int(r["endVa"], 16)
        rec = classify_tiny(data, start, end, ib, secs, md, mass, us_mod)
        if rec is None:
            still.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "bytes": end - start,
                    "lane": "STILL_OPEN",
                    "entityKey": r.get("entityKey") or "",
                    "questionIds": r.get("questionIds") or "",
                    "cheapestFalsifier": (
                        "Tiny fragment not unit-span / exact-insn / pad; "
                        "need abs-ptr inbound or TTD"
                    ),
                }
            )
            lane_counts["STILL_OPEN"] += 1
            continue
        prop = proposed_for(rec)
        proofs.append(
            {
                "startVa": r["startVa"],
                "endVa": r["endVa"],
                "bytes": end - start,
                "kind": rec["shapeKind"],
                "subspanKinds": rec["shapeKind"],
                "recoveryLane": rec["lane"],
                "peBytesSha256": rec["peBytesSha256"],
                "recheckNote": rec.get("note") or "",
                "entityKey": r.get("entityKey") or "",
                "questionIds": r.get("questionIds") or "",
                "sourceState": "OPEN_DARK_RESIDUAL",
                "detail": {
                    k: v
                    for k, v in rec.items()
                    if k
                    not in {
                        "lane",
                        "shapeKind",
                        "note",
                        "terminalState",
                        "peBytesSha256",
                    }
                },
                "proposedTerminalState": prop["terminalState"],
                "proposed": prop,
            }
        )
        lane_counts[rec["lane"]] += 1

    # still-open non-tiny dark counted for awareness
    n_non_tiny = len(dark) - len(tiny)

    hard: list[str] = []
    for p in proofs:
        if p["sourceState"] != "OPEN_DARK_RESIDUAL":
            hard.append(f"non_dark {p['startVa']}")
        if not p.get("questionIds"):
            hard.append(f"no_qid {p['startVa']}")
        term = p["proposedTerminalState"]
        if term not in {"TERMINAL_BOUNDED_AMBIGUITY", "TERMINAL_PADDING"}:
            hard.append(f"bad_term {p['startVa']}")
        s = int(p["startVa"], 16)
        e = int(p["endVa"], 16)
        again = classify_tiny(data, s, e, ib, secs, md, mass, us_mod)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"recheck_fail {p['startVa']}")

    pack: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "status": (
            "READY_FOR_GENERATION"
            if proofs and not hard
            else "EMPTY"
            if not proofs and not hard
            else "BLOCKED"
        ),
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 26,
        "n_open_dark_input": EXPECTED_OPEN_DARK,
        "n_open_executed_input": EXPECTED_OPEN_EXECUTED,
        "n_tiny_input": len(tiny),
        "n_proofs": len(proofs),
        "n_still_open_tiny": len(still),
        "n_non_tiny_dark": n_non_tiny,
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard,
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Exported {len(tiny)} tiny (1–3B) OPEN_DARK from Gen26 ({EXPECTED_OPEN_DARK} total dark).",
            f"Tiny fragment proofs: {len(proofs)} ({dict(Counter(p['recoveryLane'] for p in proofs))}).",
            f"Still open tiny: {len(still)}; non-tiny dark remaining: {n_non_tiny}.",
            "Lanes: unit-span / exact-insn / pure-pad only.",
            "Gen27 apply withheld (hold_generation_apply).",
        ],
        "non_claims": [
            "Does not invent function names or REBUILD_READY",
            "Does not claim CALL entry",
            "Does not close non-tiny OPEN_DARK",
        ],
        "proofs": proofs,
    }

    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": 26,
        "formalPackStatus": pack["status"],
        "counts": {
            "n_open_dark_input": EXPECTED_OPEN_DARK,
            "n_tiny_input": len(tiny),
            "formalPackProofs": len(proofs),
            "stillOpenTiny": len(still),
            "nonTinyDark": n_non_tiny,
            "laneCounts": dict(lane_counts),
            "recoveryLaneProofCounts": pack["recoveryLaneCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "cheapestNext": [
            "Gen27 apply tiny proofs after dual-role review",
            "Abs-ptr / shape instruments for remaining non-tiny OPEN_DARK",
            "Do not re-close police envelopes without new evidence",
        ],
        "proofStarts": [p["startVa"] for p in proofs],
        "parentResidualsSha256": _sha(campaign / "campaign-residuals.tsv"),
    }

    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    _write_tsv(
        out_dir / "still-open.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "lane",
            "entityKey",
            "questionIds",
            "cheapestFalsifier",
        ],
        still,
    )
    _write_tsv(
        out_dir / "proofs.tsv",
        [
            "startVa",
            "endVa",
            "bytes",
            "recoveryLane",
            "kind",
            "peBytesSha256",
            "entityKey",
            "questionIds",
            "recheckNote",
        ],
        proofs,
    )
    integrity = {
        "schema": "bea.re.open-residual-gen26-tiny-fragment.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "open_dark_98": len(dark) == EXPECTED_OPEN_DARK,
            "open_executed_0": len(executed) == 0,
            "specimen_pristine": True,
            "empty_or_ready": pack["status"] in {"EMPTY", "READY_FOR_GENERATION"},
            "no_gen27_apply": True,
            "gen26_unmutated": True,
            "hold_generation_apply": True,
            "all_proofs_rechecked": len(hard) == 0,
        },
        "ledger_sha_pre": {
            "campaign-residuals.tsv": _sha(campaign / "campaign-residuals.tsv"),
            "campaign.ready.json": _sha(campaign / "campaign.ready.json"),
        },
        "sources": {
            "formalPack": _stamp(out_dir / "FORMAL-PACK.json"),
            "summary": _stamp(out_dir / "SUMMARY.json"),
            "specimen": _stamp(specimen),
        },
    }
    integrity["checks"]["gen26_residuals_unchanged"] = (
        integrity["ledger_sha_pre"]["campaign-residuals.tsv"]
        == _sha(campaign / "campaign-residuals.tsv")
    )
    (out_dir / "INTEGRITY.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        f"""# Gen26 tiny OPEN_DARK (1–3B) fragment plate

Status: **MEASURED** / formal pack **{pack['status']}**  
Tiny input: **{len(tiny)}** · proofs: **{len(proofs)}** · still open tiny: **{len(still)}**

Gen27 apply: **held**.
""",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("OPEN_RESIDUAL_GEN26_TINY_FRAGMENT_MEASURED")
    print(f"formal_pack_status={pack['status']}")
    print(f"n_proofs={pack['n_proofs']}")
    return {"summary": summary, "pack": pack}


def verify_plate(plate: Path, campaign: Path, specimen: Path) -> None:
    summary = json.loads((plate / "SUMMARY.json").read_text(encoding="utf-8"))
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    integrity = json.loads((plate / "INTEGRITY.json").read_text(encoding="utf-8"))
    if summary["counts"]["n_open_dark_input"] != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark")
    for name, sha in (integrity.get("ledger_sha_pre") or {}).items():
        if _sha(campaign / name) != sha:
            raise SystemExit(f"ledger mutated {name}")
    if _sha(specimen) != SPECIMEN_SHA256:
        raise SystemExit("specimen")
    if pack.get("status") not in {"EMPTY", "READY_FOR_GENERATION"}:
        raise SystemExit("pack status")
    if not pack.get("hold_generation_apply"):
        raise SystemExit("must hold generation apply")
    rebuilt = build(campaign=campaign, specimen=specimen, out_dir=plate / "_scratch")
    import shutil

    shutil.rmtree(plate / "_scratch", ignore_errors=True)
    if rebuilt["pack"]["n_proofs"] != pack["n_proofs"]:
        raise SystemExit("proof count drift")
    if rebuilt["pack"]["status"] != pack["status"]:
        raise SystemExit("status drift")
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "formalPackStatus": pack["status"],
                "n_proofs": pack["n_proofs"],
                "lanes": pack.get("recoveryLaneCounts"),
            },
            indent=2,
        )
    )
    print("OPEN_RESIDUAL_GEN26_TINY_FRAGMENT_VERIFIED")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build tiny-fragment plate")
    b.add_argument("--campaign", type=Path, default=DEFAULT_GEN26)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify", help="Verify plate vs Gen26")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    v.add_argument("--campaign", type=Path, default=DEFAULT_GEN26)
    v.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        return 0
    if args.cmd == "verify":
        verify_plate(args.plate, args.campaign, args.specimen)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
