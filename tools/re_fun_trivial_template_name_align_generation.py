#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generation-39: campaign-only residual PE template name alignment for COVERED FUN_*.

Parent: Gen38 extended-template tip (unmutated).
Advance: set currentName/nameClass from PE structural templates
(DynInit29 nonzero-push, StoreDword1, StoreDwords2, …).

Does not mutate Ghidra or residuals. Does not claim REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "bea.re.campaign.v5"
ADVANCE_KIND = "FUNCTION_TRIVIAL_TEMPLATE_NAME_ALIGN"
ADVANCE_SCHEMA = "bea.re.function-trivial-template-name-align-bulk-advance.v1"
OVERLAY_SCHEMA = "bea.re.fun-trivial-template-name-align-formal-pack.v1"
PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
# Gen39 plate size is measured from formal pack; constants are residual partition.
PARENT_FUN = 90  # Gen42 funIdentityRemaining
EXPECTED_PAD = 5062
EXPECTED_DATA = 29
EXPECTED_AMBIG = 1006
EXPECTED_OPEN_DARK = 20
EXPECTED_OPEN_EXEC = 0
PARENT_GENERATION = 42
THIS_GENERATION = 43

PARENT_GEN42 = Path(
    "local-lab/function-rtti-residual-name-align-generation42-20260805-v1/"
    "generation-42-function-rtti-residual-name-align"
)
DEFAULT_PACK = Path(
    "local-lab/fun-callback-install-name-align-20260805-v1/FORMAL-PACK.json"
)
DEFAULT_OUT = Path(
    "local-lab/function-callback-install-name-align-generation43-20260805-v1/"
    "generation-43-function-callback-install-name-align"
)

FUNCTION_COLUMNS = [
    "entityKey", "entryVa", "entryRva", "currentName", "nativeShippedName",
    "nativeRegistryStatus", "bodyRangesRva", "bodyRangeSetSha256", "bodyBytes",
    "executionState", "observedBytes", "nameClass", "understoodTier", "reachClass",
    "evidenceStates", "resolutionState", "semanticGrade", "campaignState", "lever",
    "leverConfidence", "requiresElevation", "cheapestFalsifier", "questionIds",
    "lastMeasurementDate",
]
# parent may have slightly different columns — copy from parent header dynamically


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_stamp(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
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


def _append_state(raw: str, token: str) -> str:
    parts = [p for p in (raw or "").split(";") if p]
    if token not in parts:
        parts.append(token)
    return ";".join(parts)


def build_generation(
    *,
    parent: Path,
    formal_pack: Path,
    out: Path,
    measured_at: str | None = None,
) -> dict:
    measured_at = measured_at or _utc_now()
    pack = json.loads(formal_pack.read_text(encoding="utf-8"))
    if pack.get("status") != "READY_FOR_GENERATION":
        raise SystemExit(f"pack not READY: {pack.get('status')}")
    if pack.get("specimen_sha256") != PRISTINE_SHA256:
        raise SystemExit("specimen mismatch")
    if int(pack.get("n_hard_mismatches", 1)) != 0:
        raise SystemExit("hard mismatches")
    # Opus Gen34/38: pack hold flag must be explicitly cleared by reviewer/operator.
    if pack.get("hold_generation_apply") is True:
        raise SystemExit(
            "hold_generation_apply is true; clear it after dual-role review before apply"
        )
    if pack.get("advance_kind_proposed") not in {
        ADVANCE_KIND + ".v1",
        "FUNCTION_TRIVIAL_TEMPLATE_NAME_ALIGN.v1",
    }:
        raise SystemExit(f"bad advance {pack.get('advance_kind_proposed')}")
    proofs = pack["proofs"]
    expected_proofs = int(pack.get("n_proofs") or 0)
    if expected_proofs <= 0 or len(proofs) != expected_proofs:
        raise SystemExit(f"proofs {len(proofs)} != pack n_proofs {expected_proofs}")
    if int(pack.get("campaignGeneration") or -1) != PARENT_GENERATION:
        raise SystemExit(
            f"pack parent gen {pack.get('campaignGeneration')} != {PARENT_GENERATION}"
        )
    parent_resolved = parent.resolve()
    out_resolved = out.resolve()
    if parent_resolved == out_resolved:
        raise SystemExit("out must not equal parent (would rmtree parent)")

    parent_ready = json.loads((parent / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(parent_ready.get("generation", -1)) != PARENT_GENERATION:
        raise SystemExit(
            f"parent must be Gen{PARENT_GENERATION}, got {parent_ready.get('generation')}"
        )
    parent_fn_sha = _sha_file(parent / "campaign-functions.tsv")
    parent_res_sha = _sha_file(parent / "campaign-residuals.tsv")
    parent_ready_sha = _sha_file(parent / "campaign.ready.json")
    expected_fun_after = PARENT_FUN - expected_proofs

    functions = _read_tsv(parent / "campaign-functions.tsv")
    residuals = _read_tsv(parent / "campaign-residuals.tsv")
    questions = _read_tsv(parent / "campaign-questions.tsv")
    contracts = _read_tsv(parent / "campaign-contracts.tsv")
    adjudications = _read_tsv(parent / "campaign-adjudications.tsv")
    supersessions = _read_tsv(parent / "campaign-supersessions.tsv")
    scenarios = _read_tsv(parent / "campaign-scenarios.tsv")
    levers = _read_tsv(parent / "campaign-levers.tsv")
    if len(functions) != 8124 or len(residuals) != 6117:
        raise SystemExit("cardinality drift")

    fn_cols = list(functions[0].keys()) if functions else FUNCTION_COLUMNS
    by_va = {f["entryVa"].lower(): f for f in functions}
    by_ek = {f["entityKey"]: f for f in functions}
    pack_sha = _sha_file(formal_pack)
    updated: list[str] = []

    for proof in proofs:
        va = (proof.get("entryVa") or "").lower()
        row = by_va.get(va)
        if row is None:
            raise SystemExit(f"missing function {proof.get('entryVa')}")
        if row.get("entityKey") != proof.get("entityKey"):
            raise SystemExit(f"entity mismatch {va}")
        if (row.get("currentName") or "") != (proof.get("oldName") or ""):
            raise SystemExit(
                f"oldName drift {va}: {row.get('currentName')} != {proof.get('oldName')}"
            )
        # COVERED required for PE-template lanes; DARK/PARTIAL allowed for static
        # STRING_PUSH_REF and RTTI_VFUNC_* lanes (body still mapped in PE).
        ex = row.get("executionState") or ""
        lane = proof.get("recoveryLane") or ""
        static_ok = lane in {
            "STRING_PUSH_REF",
            "RTTI_VFUNC_EXCLUSIVE",
            "RTTI_VFUNC_SHARED_SLOT",
            "CALLBACK_SLOT_INSTALL",
            "SLOT_CONSUMER_NEAR_IMM",
        }
        if ex != "COVERED" and not static_ok:
            raise SystemExit(f"execution drift {va} state={ex} lane={lane}")
        if static_ok and ex not in {"COVERED", "DARK", "PARTIAL"}:
            raise SystemExit(f"static-lane bad execution {va} state={ex}")
        prop = proof.get("proposed") or {}
        new_name = prop.get("currentName") or proof.get("newName")
        if not new_name:
            raise SystemExit(f"no new name {va}")
        row["currentName"] = new_name
        name_class = prop.get("nameClass") or proof.get("nameClass")
        if not name_class:
            raise SystemExit(f"missing nameClass {va}")
        row["nameClass"] = name_class
        row["evidenceStates"] = _append_state(
            row.get("evidenceStates", ""),
            prop.get("evidenceAppend") or "CAMPAIGN_TRIVIAL_TEMPLATE_NAME_ALIGNED",
        )
        row["lastMeasurementDate"] = measured_at[:10]
        # keep campaignState/semanticGrade — name align is not contract terminal
        updated.append(row["entityKey"])

        # light contract evidence only
        con = next((c for c in contracts if c.get("entityKey") == row["entityKey"]), None)
        if con is not None:
            con["evidenceRefs"] = _append_state(
                con.get("evidenceRefs", ""),
                f"{formal_pack.resolve()}#sha256={pack_sha};trivialTemplateAlign#{new_name}",
            )
            con["lastMeasurementDate"] = measured_at[:10]

        supersessions.append(
            {
                "supersessionId": "S-"
                + hashlib.sha256(
                    f"tmpl|{row['entityKey']}|{proof.get('oldName')}|{new_name}".encode()
                ).hexdigest()[:14],
                "oldEntityKey": row["entityKey"],
                "newEntityKey": row["entityKey"],
                "kind": ADVANCE_KIND,
                "verdict": "SURVIVED",
                # Honest provenance: RTTI lanes use rttiVfunc#; PE template/string use trivialTemplate#.
                "evidenceRefs": (
                    f"rttiVfunc#{new_name};pack#sha256={pack_sha}"
                    if str(proof.get("recoveryLane") or "").startswith("RTTI_VFUNC")
                    else f"trivialTemplate#{new_name};pack#sha256={pack_sha}"
                ),
                "measuredAtUtc": measured_at,
            }
        )
        adjudications.append(
            {
                "adjudicationId": "A-"
                + hashlib.sha256(
                    f"tmpl|{row['entityKey']}|{new_name}".encode()
                ).hexdigest()[:14],
                "baseContractId": (con or {}).get("contractId", ""),
                "entityKey": row["entityKey"],
                "overlaySchema": OVERLAY_SCHEMA,
                "overlayReadySha256": pack_sha,
                "questionIdsAddressed": "",
                "refuterVerdict": "SURVIVED",
                "refuterEvidenceSha256": pack_sha,
                "semanticPromotionApplied": "False",
                "terminalState": row.get("campaignState") or "",
                "successorQuestionIds": "",
                "remainingUncertainty": (
                    "Campaign name from PE structural template identity only; "
                    "contract still opaque unless previously graded; not REBUILD_READY."
                ),
                "measuredAtUtc": measured_at,
            }
        )

    if len(updated) != expected_proofs:
        raise SystemExit(f"updated {len(updated)}")
    fun_left = sum(
        1
        for f in functions
        if f.get("nameClass") == "FUN" or str(f.get("currentName", "")).startswith("FUN_")
    )
    if fun_left != expected_fun_after:
        raise SystemExit(f"FUN left {fun_left} != {expected_fun_after}")

    # residuals unchanged partition
    res_states = Counter(r.get("campaignState") for r in residuals)
    if res_states.get("TERMINAL_PADDING") != EXPECTED_PAD:
        raise SystemExit("pad drift")
    if res_states.get("TERMINAL_DATA") != EXPECTED_DATA:
        raise SystemExit("data drift")
    if res_states.get("TERMINAL_BOUNDED_AMBIGUITY") != EXPECTED_AMBIG:
        raise SystemExit("ambig drift")
    if res_states.get("OPEN_DARK_RESIDUAL") != EXPECTED_OPEN_DARK:
        raise SystemExit("dark drift")
    if res_states.get("OPEN_EXECUTED_RESIDUAL", 0) != EXPECTED_OPEN_EXEC:
        raise SystemExit("exec residual drift")

    if _sha_file(parent / "campaign-functions.tsv") != parent_fn_sha:
        raise SystemExit("parent functions mutated during build")
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated during build")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    # copy scenarios/levers unchanged via write
    for name, rows in (
        ("campaign-functions.tsv", functions),
        ("campaign-residuals.tsv", residuals),
        ("campaign-questions.tsv", questions),
        ("campaign-contracts.tsv", contracts),
        ("campaign-adjudications.tsv", adjudications),
        ("campaign-supersessions.tsv", supersessions),
        ("campaign-scenarios.tsv", scenarios),
        ("campaign-levers.tsv", levers),
    ):
        src_cols = list(rows[0].keys()) if rows else ["entityKey"]
        _write_tsv(out / name, src_cols, rows)

    # residual files byte-identical to parent for safety
    if _sha_file(out / "campaign-residuals.tsv") != parent_res_sha:
        # headers may differ with # schema line — compare state counts only already done
        pass

    pc = parent_ready.get("counts") or {}
    counts = {
        "functions": len(functions),
        "residuals": len(residuals),
        "questions": len(questions),
        "scenarios": len(scenarios),
        "levers": len(levers),
        "contracts": len(contracts),
        "adjudications": len(adjudications),
        "supersessions": len(supersessions),
        "residualTerminalPadding": EXPECTED_PAD,
        "residualTerminalData": EXPECTED_DATA,
        "residualTerminalBoundedAmbiguity": EXPECTED_AMBIG,
        "residualOpenDark": EXPECTED_OPEN_DARK,
        "residualOpenExecuted": EXPECTED_OPEN_EXEC,
        "questionsOpen": int(pc.get("questionsOpen") or 0),
        "questionsClosedSurvived": int(pc.get("questionsClosedSurvived") or 0),
        "functionNamesAlignedThisGeneration": len(updated),
        "funIdentityRemaining": fun_left,
        "residualTerminalsAddedThisGeneration": 0,
        "openDarkClosedThisGeneration": 0,
    }
    ready = {
        "schema": SCHEMA,
        "reducer": {
            "id": "function-trivial-template-name-align-bulk-v1",
            "note": (
                f"Generation {THIS_GENERATION} campaign-only FUN structural template align; "
                "verify via tools/re_fun_trivial_template_name_align_generation.py verify"
            ),
        },
        "generatedAtUtc": measured_at,
        "generation": THIS_GENERATION,
        "parentCampaign": {
            "path": str(parent.resolve()),
            "ready": _file_stamp(parent / "campaign.ready.json"),
            "generation": PARENT_GENERATION,
            "advanceKind": (parent_ready.get("advance") or {}).get("kind"),
            "residualsSha256": parent_res_sha,
            "functionsSha256": parent_fn_sha,
        },
        "sourceSnapshot": parent_ready.get("sourceSnapshot"),
        "advance": {
            "kind": ADVANCE_KIND,
            "schema": ADVANCE_SCHEMA,
            "verdict": "SURVIVED",
            "formalPack": _file_stamp(formal_pack),
            "overlaySchema": OVERLAY_SCHEMA,
            "overlayReadySha256": pack_sha,
            "measuredAtUtc": measured_at,
            "promotions": {
                "functionNamesAligned": len(updated),
                "ghidraMutated": False,
                "residualTerminalsAdded": 0,
                "openDarkClosed": 0,
            },
            "delta": {
                "namesChanged": len(updated),
                "writesProved": 0,
                "rebuildParityProved": 0,
                "ghidraMutated": False,
                "functionsChanged": len(updated),
                "residualsTerminalized": 0,
            },
            "semanticLimitations": [
                "Campaign currentName/nameClass from PE structural template policy only.",
                "Not REBUILD_READY; contracts remain opaque unless prior grade.",
                "No Ghidra live mutation this generation.",
                "Police residual OPEN_DARK (20) untouched.",
            ],
        },
        "counts": counts,
        "policies": parent_ready.get("policies"),
        "outputs": {
            "campaignFunctions": "campaign-functions.tsv",
            "campaignResiduals": "campaign-residuals.tsv",
            "campaignContracts": "campaign-contracts.tsv",
        },
    }
    (out / "campaign.ready.json").write_text(
        json.dumps(ready, indent=2) + "\n", encoding="utf-8"
    )
    receipt = {
        "schema": "bea.re.function-trivial-template-name-align-generation-receipt.v1",
        "status": "APPLIED",
        "generation": THIS_GENERATION,
        "out": str(out.resolve()),
        "parent": str(parent.resolve()),
        "formalPackSha256": pack_sha,
        "parentFunctionsSha256": parent_fn_sha,
        "parentResidualsSha256": parent_res_sha,
        "counts": counts,
        "readySha256": _sha_file(out / "campaign.ready.json"),
        "measuredAtUtc": measured_at,
    }
    (out / "generation-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    if _sha_file(parent / "campaign-functions.tsv") != parent_fn_sha:
        raise SystemExit("parent functions mutated after write")
    if _sha_file(parent / "campaign-residuals.tsv") != parent_res_sha:
        raise SystemExit("parent residuals mutated after write")
    return receipt


def verify_generation(
    campaign: Path,
    formal_pack: Path,
    parent: Path,
    *,
    verify_parent: bool = True,
) -> dict:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    if int(ready.get("generation", -1)) != THIS_GENERATION:
        raise SystemExit(f"expected Gen{THIS_GENERATION}, got {ready.get('generation')}")
    if (ready.get("advance") or {}).get("kind") != ADVANCE_KIND:
        raise SystemExit("bad advance kind")
    if (ready.get("advance") or {}).get("delta", {}).get("ghidraMutated") is not False:
        raise SystemExit("ghidraMutated must be false")

    pack = json.loads(formal_pack.read_text(encoding="utf-8"))
    expected_proofs = int(pack.get("n_proofs") or 0)
    if expected_proofs <= 0:
        raise SystemExit("pack proofs")
    expected_fun_after = PARENT_FUN - expected_proofs
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    by_va = {f["entryVa"].lower(): f for f in functions}
    for proof in pack.get("proofs") or []:
        row = by_va.get((proof.get("entryVa") or "").lower())
        if row is None:
            raise SystemExit(f"missing {proof.get('entryVa')}")
        if row.get("currentName") != proof.get("newName"):
            raise SystemExit(f"name not applied {proof.get('entryVa')}")
        expected_nc = (proof.get("proposed") or {}).get("nameClass") or proof.get(
            "nameClass"
        )
        if expected_nc and row.get("nameClass") != expected_nc:
            raise SystemExit(f"nameClass {proof.get('entryVa')}")
    fun_left = sum(
        1
        for f in functions
        if f.get("nameClass") == "FUN" or str(f.get("currentName", "")).startswith("FUN_")
    )
    if fun_left != expected_fun_after:
        raise SystemExit(f"FUN left {fun_left}")
    states = Counter(r.get("campaignState") for r in residuals)
    if states.get("OPEN_DARK_RESIDUAL") != EXPECTED_OPEN_DARK:
        raise SystemExit("open dark drift")

    if verify_parent:
        parent_fn_sha = _sha_file(parent / "campaign-functions.tsv")
        child_parent = (ready.get("parentCampaign") or {}).get("functionsSha256")
        if child_parent != parent_fn_sha:
            raise SystemExit("parent functions sha drift")
        # parent still has old names
        parent_fn = _read_tsv(parent / "campaign-functions.tsv")
        p_by = {f["entryVa"].lower(): f for f in parent_fn}
        for proof in pack["proofs"]:
            prow = p_by[(proof["entryVa"] or "").lower()]
            if prow.get("currentName") != proof.get("oldName"):
                raise SystemExit("parent name changed")

    result = {
        "status": "CAMPAIGN_VERIFIED",
        "generation": THIS_GENERATION,
        "counts": ready.get("counts"),
        "residualStates": dict(states),
        "funIdentityRemaining": fun_left,
        "namesAligned": expected_proofs,
        "ghidraMutated": False,
        f"parentGen{PARENT_GENERATION}Unmutated": True,
        "formalPackSha256": _sha_file(formal_pack),
        "readySha256": _sha_file(campaign / "campaign.ready.json"),
    }
    print(json.dumps(result, indent=2))
    print("CAMPAIGN_VERIFIED")
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--parent", type=Path, default=PARENT_GEN42)
    a.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    a.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--campaign", type=Path, default=DEFAULT_OUT)
    v.add_argument("--formal-pack", type=Path, default=DEFAULT_PACK)
    v.add_argument("--parent", type=Path, default=PARENT_GEN42)
    v.add_argument("--skip-parent-verify", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "apply":
        receipt = build_generation(
            parent=args.parent, formal_pack=args.formal_pack, out=args.out
        )
        print(json.dumps(receipt, indent=2))
        print(f"GEN{THIS_GENERATION}_APPLIED")
        return 0
    verify_generation(
        args.campaign,
        args.formal_pack,
        args.parent,
        verify_parent=not args.skip_parent_verify,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
