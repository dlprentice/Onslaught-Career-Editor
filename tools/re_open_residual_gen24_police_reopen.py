#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation-25 reopen of police-refuted residual terminals.

Parent: Gen24 small-table tip (unmutated).
Reopens residual rows that six-way police REFUTED / load-bearing NEEDS_WORK:

1. All 20 Gen16 OFFSET_ENVELOPE promotions still TERMINAL_BOUNDED_AMBIGUITY on
   Gen24 whose deeper plate left wholeSpanTerminal=false (envelope launder).
2. Gen24 INDEX bulk residual 0x004f5ac5 (small table + large INDEX remainder).

Does not invent names or REBUILD_READY. Returns rows to OPEN_DARK_RESIDUAL
with explicit cheapest falsifiers and reopened DARK_TEXT_CLASSIFICATION questions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "RESIDUAL_TERMINAL_POLICE_REOPEN"
ADVANCE_SCHEMA = "bea.re.residual-terminal-police-reopen-advance.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
PARENT_GEN24 = Path(
    "local-lab/residual-terminal-generation24-small-table-20260805-v1/"
    "generation-24-residual-terminal-small-table"
)
GEN16_RECOVERY = Path(
    "local-lab/open-dark-code-like-mass-gen15-20260805-v1/recovery.tsv"
)
DEEPER = Path(
    "local-lab/open-dark-code-like-mass-gen15-20260805-v1/deeper-rows.json"
)
DEFAULT_OUT = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen"
)
INDEX_BULK_START = "0x004f5ac5"

RESIDUAL_COLUMNS = [
    "entityKey", "startVa", "endVa", "bytes", "observedBytes",
    "observationState", "classification", "classificationVerdict", "terminalState",
    "bytePattern", "prevFunc", "nextFunc", "campaignState", "lever",
    "requiresElevation", "cheapestFalsifier", "questionIds", "lastMeasurementDate",
]
QUESTION_COLUMNS = [
    "questionId", "questionType", "entityKey", "priority", "score", "state",
    "requiresElevation", "recommendedInstrument", "question", "cheapestFalsifier",
    "source", "currentOwner", "generation", "attemptCount",
    "parentQuestionId", "lastOutcome", "lastMeasurementDate",
]
CONTRACT_COLUMNS = [
    "contractId", "entityKey", "entityKind", "entryVa", "currentName", "nativeShippedName",
    "contractState", "semanticGrade", "receiver", "inputs", "returns", "writes",
    "sideEffects", "preconditions", "failureModes", "authorVerdict", "runtimeVerdict",
    "refuterVerdict", "questionIds", "evidenceRefs", "cheapestFalsifier",
    "rebuildOwner", "rebuildImplementation", "parityTests", "rebuildState",
    "remainingUncertainty", "supersedesEntityKeys", "lastMeasurementDate",
]
ADJUDICATION_COLUMNS = [
    "adjudicationId", "baseContractId", "entityKey", "overlaySchema",
    "overlayReadySha256", "questionIdsAddressed", "refuterVerdict",
    "refuterEvidenceSha256", "semanticPromotionApplied", "terminalState",
    "successorQuestionIds", "remainingUncertainty", "measuredAtUtc",
]
SUPERSESSION_COLUMNS = [
    "supersessionId", "oldEntityKey", "newEntityKey", "kind", "verdict",
    "evidenceRefs", "measuredAtUtc",
]

FALSIFIER_ENVELOPE = (
    "Police reopen: Gen16 OFFSET_ENVELOPE whole-span terminal disagreed with "
    "deeper wholeSpanTerminal=false / openBytes; re-check with full-cover+"
    "control-end envelope gate; residual-split or inbound before re-terminal"
)
FALSIFIER_INDEX = (
    "Police reopen: Gen24 small-table + bulk INDEX remainder (rest>max(cpr,32)); "
    "re-compose with INDEX length cap; residual-split before terminal"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short_id(prefix: str, material: str) -> str:
    return f"{prefix}-{hashlib.sha256(material.encode()).hexdigest()[:14]}"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle, fieldnames=columns, delimiter="\t",
            lineterminator="\n", extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def _file_stamp(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def collect_reopen_starts() -> list[dict]:
    rows = _read_tsv(GEN16_RECOVERY)
    deeper = {
        d["startVa"].lower(): d
        for d in json.loads(DEEPER.read_text(encoding="utf-8"))
        if "startVa" in d
    }
    out: list[dict] = []
    for r in rows:
        if (r.get("recoveryLane") or "") != "OFFSET_ENVELOPE":
            continue
        d = deeper.get(r["startVa"].lower()) or {}
        if d.get("wholeSpanTerminal") is False or int(d.get("openBytes") or 0) > 0:
            out.append(
                {
                    "startVa": r["startVa"],
                    "endVa": r["endVa"],
                    "reason": "OFFSET_ENVELOPE_vs_deeper_open",
                    "falsifier": FALSIFIER_ENVELOPE,
                }
            )
    out.append(
        {
            "startVa": INDEX_BULK_START,
            "endVa": "",  # filled from residual
            "reason": "SMALL_TABLE_BULK_INDEX",
            "falsifier": FALSIFIER_INDEX,
        }
    )
    # unique by start
    by: dict[str, dict] = {}
    for item in out:
        by[item["startVa"].lower()] = item
    return list(by.values())


def build_generation(
    *,
    parent: Path,
    out: Path,
    measured_at: str | None = None,
) -> dict:
    measured_at = measured_at or _utc_now()
    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != 24:
        raise SystemExit(f"parent must be Gen24, got {parent_ready.get('generation')}")
    parent_advance = (parent_ready.get("advance") or {}).get("kind")
    if parent_advance != "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE":
        raise SystemExit(f"parent advance {parent_advance}")

    parent_res_sha = _sha_file(parent / "campaign-residuals.tsv")
    parent_fn_sha = _sha_file(parent / "campaign-functions.tsv")
    parent_ready_sha = _sha_file(parent / "campaign.ready.json")

    residuals = _read_tsv(parent / "campaign-residuals.tsv")
    questions = _read_tsv(parent / "campaign-questions.tsv")
    contracts = _read_tsv(parent / "campaign-contracts.tsv")
    adjudications = _read_tsv(parent / "campaign-adjudications.tsv")
    supersessions = _read_tsv(parent / "campaign-supersessions.tsv")
    functions = _read_tsv(parent / "campaign-functions.tsv")
    scenarios = _read_tsv(parent / "campaign-scenarios.tsv")
    levers = _read_tsv(parent / "campaign-levers.tsv")
    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("cardinality drift")

    res_by_start = {r["startVa"].lower(): r for r in residuals}
    con_by_entity = {c["entityKey"]: c for c in contracts}
    q_by_id = {q["questionId"]: q for q in questions}

    targets = collect_reopen_starts()
    proofs_applied: list[dict] = []
    reopened_qids: list[str] = []

    for t in targets:
        start = t["startVa"].lower()
        residual = res_by_start.get(start)
        if residual is None:
            raise SystemExit(f"missing residual {t['startVa']}")
        if residual.get("campaignState") not in {
            "TERMINAL_BOUNDED_AMBIGUITY",
            "TERMINAL_DATA",
        }:
            # already open — skip
            continue
        if residual.get("observationState") == "EXECUTED":
            raise SystemExit(f"EXECUTED reopen forbidden {t['startVa']}")
        ek = residual["entityKey"]
        contract = con_by_entity.get(ek)
        if contract is None or contract.get("entityKind") != "TEXT_RESIDUAL":
            raise SystemExit(f"bad contract {ek}")

        # reopen residual
        residual["classification"] = "AMBIGUOUS"
        residual["classificationVerdict"] = "POLICE_REOPEN_OPEN"
        residual["terminalState"] = "OPEN"
        residual["campaignState"] = "OPEN_DARK_RESIDUAL"
        residual["bytePattern"] = "MIXED_OR_CODE_LIKE_BYTES"
        residual["lever"] = "STATIC_CLASSIFICATION_FIRST"
        residual["cheapestFalsifier"] = t["falsifier"]
        residual["lastMeasurementDate"] = measured_at[:10]

        qid = _short_id("Q", f"reopen|{ek}|{t['reason']}")
        residual["questionIds"] = qid
        questions.append(
            {
                "questionId": qid,
                "questionType": "DARK_TEXT_CLASSIFICATION",
                "entityKey": ek,
                "priority": "HIGH",
                "score": "90",
                "state": "OPEN",
                "requiresElevation": "False",
                "recommendedInstrument": "residual-split|inbound|strict-envelope",
                "question": (
                    f"Reopened after police: {t['reason']} at {residual['startVa']}"
                ),
                "cheapestFalsifier": t["falsifier"],
                "source": "POLICE_REOPEN_GEN25",
                "currentOwner": "UNASSIGNED",
                "generation": "25",
                "attemptCount": "0",
                "parentQuestionId": "",
                "lastOutcome": "UNSCORED",
                "lastMeasurementDate": measured_at[:10],
            }
        )
        reopened_qids.append(qid)

        contract["contractState"] = "OPEN"
        contract["semanticGrade"] = "C0_OPAQUE"
        contract["authorVerdict"] = "POLICE_REOPEN"
        contract["runtimeVerdict"] = "UNSCORED"
        contract["refuterVerdict"] = "UNSCORED"
        contract["questionIds"] = qid
        contract["evidenceRefs"] = (
            f"police-reopen#{t['reason']};"
            f"synthesis#local-lab/per-gen-review-20260805-v1/SYNTHESIS.md"
        )
        contract["cheapestFalsifier"] = t["falsifier"]
        contract["rebuildOwner"] = "UNASSIGNED"
        contract["rebuildImplementation"] = "UNMAPPED"
        contract["parityTests"] = "UNMAPPED"
        contract["rebuildState"] = "NOT_READY"
        contract["remainingUncertainty"] = (
            f"Reopened residual ({t['reason']}); not REBUILD_READY; not named."
        )
        contract["lastMeasurementDate"] = measured_at[:10]

        adjudications.append(
            {
                "adjudicationId": _short_id("A", f"reopen|{ek}|{t['reason']}"),
                "baseContractId": contract["contractId"],
                "entityKey": ek,
                "overlaySchema": "bea.re.police-reopen.v1",
                "overlayReadySha256": "",
                "questionIdsAddressed": qid,
                "refuterVerdict": "REOPENED",
                "refuterEvidenceSha256": "",
                "semanticPromotionApplied": "False",
                "terminalState": "OPEN_DARK_RESIDUAL",
                "successorQuestionIds": qid,
                "remainingUncertainty": t["falsifier"],
                "measuredAtUtc": measured_at,
            }
        )
        supersessions.append(
            {
                "supersessionId": _short_id("S", f"reopen|{ek}|{t['reason']}"),
                "oldEntityKey": ek,
                "newEntityKey": ek,
                "kind": ADVANCE_KIND,
                "verdict": "REOPENED",
                "evidenceRefs": f"reason#{t['reason']}",
                "measuredAtUtc": measured_at,
            }
        )
        proofs_applied.append(
            {
                "startVa": residual["startVa"],
                "endVa": residual["endVa"],
                "entityKey": ek,
                "reason": t["reason"],
            }
        )

    n = len(proofs_applied)
    if n < 1:
        raise SystemExit("no reopen targets applied")

    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated during build")
    if _sha_file(parent / "campaign.ready.json") != parent_ready_sha:
        raise SystemExit("parent ready mutated during build")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if (parent / "_reducer").is_dir():
        shutil.copytree(parent / "_reducer", out / "_reducer")

    _write_tsv(out / "campaign-functions.tsv", list(functions[0].keys()), functions)
    _write_tsv(out / "campaign-residuals.tsv", RESIDUAL_COLUMNS, residuals)
    _write_tsv(out / "campaign-questions.tsv", QUESTION_COLUMNS, questions)
    _write_tsv(out / "campaign-contracts.tsv", CONTRACT_COLUMNS, contracts)
    _write_tsv(out / "campaign-scenarios.tsv", list(scenarios[0].keys()), scenarios)
    _write_tsv(out / "campaign-levers.tsv", list(levers[0].keys()), levers)
    _write_tsv(out / "campaign-adjudications.tsv", ADJUDICATION_COLUMNS, adjudications)
    _write_tsv(out / "campaign-supersessions.tsv", SUPERSESSION_COLUMNS, supersessions)

    term_pad = sum(1 for r in residuals if r.get("campaignState") == "TERMINAL_PADDING")
    term_data = sum(1 for r in residuals if r.get("campaignState") == "TERMINAL_DATA")
    term_ambig = sum(
        1 for r in residuals if r.get("campaignState") == "TERMINAL_BOUNDED_AMBIGUITY"
    )
    open_dark = sum(1 for r in residuals if r.get("campaignState") == "OPEN_DARK_RESIDUAL")
    open_exec = sum(
        1 for r in residuals if r.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
    )
    if term_pad + term_data + term_ambig + open_dark + open_exec != 6117:
        raise SystemExit(
            f"partition {term_pad}+{term_data}+{term_ambig}+{open_dark}+{open_exec}"
        )

    pc = parent_ready.get("counts") or {}
    parent_ambig = int(pc.get("residualTerminalBoundedAmbiguity") or 0)
    parent_data = int(pc.get("residualTerminalData") or 0)
    parent_dark = int(pc.get("residualOpenDark") or 0)
    # n reopened from ambig (and maybe 0 from data)
    data_reopened = parent_data - term_data
    ambig_reopened = parent_ambig - term_ambig
    if data_reopened + ambig_reopened != n:
        raise SystemExit(
            f"reopen split data={data_reopened} ambig={ambig_reopened} n={n}"
        )
    if open_dark != parent_dark + n:
        raise SystemExit(f"dark {open_dark} != {parent_dark}+{n}")
    if open_exec != int(pc.get("residualOpenExecuted") or 0):
        raise SystemExit("exec drifted")

    q_open = sum(1 for q in questions if q.get("state") == "OPEN")
    q_closed = sum(1 for q in questions if q.get("state") == "CLOSED_SURVIVED")

    counts = {
        "functions": len(functions),
        "residuals": len(residuals),
        "questions": len(questions),
        "scenarios": len(scenarios),
        "levers": len(levers),
        "contracts": len(contracts),
        "adjudications": len(adjudications),
        "supersessions": len(supersessions),
        "residualTerminalPadding": term_pad,
        "residualTerminalData": term_data,
        "residualTerminalBoundedAmbiguity": term_ambig,
        "residualOpenDark": open_dark,
        "residualOpenExecuted": open_exec,
        "questionsOpen": q_open,
        "questionsClosedSurvived": q_closed,
        "residualTerminalsAddedThisGeneration": 0,
        "residualReopenedThisGeneration": n,
        "questionsReopenedThisGeneration": len(set(reopened_qids)),
        "terminalPaddingAddedThisGeneration": 0,
        "terminalDataAddedThisGeneration": -data_reopened,
        "terminalBoundedAmbiguityAddedThisGeneration": -ambig_reopened,
        "openDarkClosedThisGeneration": -n,
        "openExecutedClosedThisGeneration": 0,
    }

    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "residual-terminal-police-reopen-v1",
            "note": "Gen25 police reopen of laundered envelope/index terminals",
        },
        "generatedAtUtc": measured_at,
        "generation": 25,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": 24,
            "advanceKind": parent_advance,
            "residualsSha256": parent_res_sha,
            "functionsSha256": parent_fn_sha,
        },
        "sourceSnapshot": parent_ready.get("sourceSnapshot"),
        "advance": {
            "kind": ADVANCE_KIND,
            "schema": ADVANCE_SCHEMA,
            "verdict": "REOPENED",
            "measuredAtUtc": measured_at,
            "reopened": proofs_applied,
            "promotions": {
                "residualReopened": n,
                "openDarkAdded": n,
                "questionsReopened": len(set(reopened_qids)),
            },
            "delta": {
                "namesChanged": 0,
                "writesProved": 0,
                "rebuildParityProved": 0,
                "ghidraMutated": False,
                "functionsChanged": 0,
                "residualsReopened": n,
            },
            "semanticLimitations": [
                "Reopen only; not REBUILD_READY; no invented names.",
                "Envelope instrument tightened for future composes.",
                "INDEX after small-table capped for future composes.",
                f"{open_dark} OPEN_DARK + {open_exec} OPEN_EXECUTED remain.",
            ],
        },
        "counts": counts,
        "policies": parent_ready.get("policies"),
        "outputs": {
            "campaignResiduals": "campaign-residuals.tsv",
            "campaignQuestions": "campaign-questions.tsv",
            "campaignContracts": "campaign-contracts.tsv",
            "campaignAdjudications": "campaign-adjudications.tsv",
            "campaignSupersessions": "campaign-supersessions.tsv",
        },
    }
    (out / "campaign.ready.json").write_text(
        json.dumps(ready, indent=2) + "\n", encoding="utf-8"
    )
    receipt = {
        "schema": "bea.re.police-reopen-generation-receipt.v1",
        "status": "APPLIED",
        "generation": 25,
        "out": str(out.resolve()),
        "parent": str(parent.resolve()),
        "parentResidualsSha256": parent_res_sha,
        "nReopened": n,
        "reopenedStarts": [p["startVa"] for p in proofs_applied],
        "counts": counts,
        "readySha256": _sha_file(out / "campaign.ready.json"),
        "measuredAtUtc": measured_at,
    }
    (out / "generation-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated after child write")
    return receipt


def verify_generation(campaign: Path, parent: Path) -> dict:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != 25:
        raise SystemExit(f"expected Gen25, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != ADVANCE_KIND:
        raise SystemExit("bad advance")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    states = Counter(r.get("campaignState") for r in residuals)
    if len(residuals) != 6117:
        raise SystemExit("residuals")
    parent_res = _sha_file(parent / "campaign-residuals.tsv")
    if (ready.get("parentCampaign") or {}).get("residualsSha256") != parent_res:
        raise SystemExit("parent residuals sha drift")
    n = int((ready.get("counts") or {}).get("residualReopenedThisGeneration") or 0)
    if n < 1:
        raise SystemExit("no reopens")
    # each reopened start must be OPEN_DARK
    for p in (ready.get("advance") or {}).get("reopened") or []:
        start = p["startVa"].lower()
        hit = next(
            (r for r in residuals if r["startVa"].lower() == start), None
        )
        if hit is None or hit.get("campaignState") != "OPEN_DARK_RESIDUAL":
            raise SystemExit(f"reopen not open {p['startVa']}")
    print(
        "CAMPAIGN_VERIFIED",
        json.dumps(
            {
                "generation": 25,
                "nReopened": n,
                "states": dict(states),
                "counts": ready.get("counts"),
            }
        ),
    )
    return {"status": "CAMPAIGN_VERIFIED", "nReopened": n, "states": dict(states)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--parent", type=Path, default=PARENT_GEN24)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--parent", type=Path, default=PARENT_GEN24)
    args = p.parse_args(argv)
    if args.cmd == "build":
        receipt = build_generation(parent=args.parent, out=args.out)
        print(json.dumps(receipt, indent=2))
        print("POLICE_REOPEN_GENERATION_APPLIED")
        return 0
    if args.cmd == "verify":
        verify_generation(args.campaign, args.parent)
        print("POLICE_REOPEN_GENERATION_VERIFIED")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
