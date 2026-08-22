#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-tests for contract_coverage.py.

The defect this gate closes is a coverage dashboard that quietly inflates
progress: a classifier that invents VERIFIED from thin air, counts one witness
twice as two, or reads scope discipline ("did not widen the C2") as a block is
worse than no dashboard, because it would be quoted as authority. Most of what
is below is therefore FALSIFICATION: build a minimal synthetic corpus, break
one honesty property at a time, and assert the classifier refuses.

If ``test_skeleton_is_the_honest_default`` ever passes trivially, this gate is
decoration.

A second half runs against the REAL tracked corpus when it is present
(``reverse-engineering/EVIDENCE-REGISTER.tsv``): structural invariants only --
row count equals the pinned denominator, statuses inside the vocabulary,
totals add up -- never specific live classifications, because sibling lanes
own those notes and legitimately move them under us.

Run: py -3 tools/contract_coverage_tests.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "contract_coverage.py"

STATE_AUTH = {
    "generation": 31,
    "lineageId": "test-lineage",
    "readySha256": "2e77c62d236edacbe4974ca844a6ac0b692e84b3259b884b8afc25a29aad4219",
}


def state_json(n_functions: int) -> str:
    return json.dumps({"current_re_authority": {
        **STATE_AUTH,
        "counts": {"functions": n_functions, "contracts": n_functions + 4},
    }})

REGISTER_HEADER = "entryVa\tname\tgrade\tresolution\tcontractState\tevidence\tgeneration\treadySha256"
PRISTINE_IMAGE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
WAVE1_REVIEW_FLOOR_VAS = {
    "0x00405a40", "0x00405ed0", "0x00405ef0", "0x00405f20", "0x00405f40",
    "0x00405f50", "0x00405f60", "0x00405f80", "0x00406000", "0x004063a0",
    "0x00407940", "0x00408150", "0x00409880", "0x0040a560", "0x0040e7d0",
}
WAVE1_PRESERVED_STATUS_BY_VA = {
    "0x00405f00": "REVIEW_READY",
    "0x00406020": "REVIEW_READY",
    "0x00406040": "REVIEW_READY",
    "0x00406050": "REVIEW_READY",
    "0x00406560": "DISPUTED",
    "0x00406fc0": "VERIFIED",
    "0x00407310": "VERIFIED",
    "0x004080f0": "REVIEW_READY",
    "0x00409de0": "REVIEW_READY",
    "0x0040e910": "REVIEW_READY",
}


def w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def base_register_row(va: str, name: str, grade: str = "OPAQUE",
                      evidence: str = "BASELINE_STATIC;ANALYST_METADATA_ONLY;RUNTIME_BOUNDED") -> str:
    return "\t".join([va, name, grade, "OPEN_JOIN", "OPEN_EXECUTED", evidence, "31", "2e77c62d"])


def make_corpus(root: Path, rows: list[str]) -> None:
    """Minimal tracked-corpus shape: state + register only."""
    w(root, "developer_state.json", state_json(len(rows)))
    w(root, "reverse-engineering/EVIDENCE-REGISTER.tsv",
      "# bea.re.evidence-register.v2\n# generatedAtUtc: test\n" + REGISTER_HEADER + "\n"
      + "\n".join(rows) + "\n")


def full_contract(name: str, va: str, evidence_grade: str = "MEASURED") -> str:
    return f"""# {name}

Status: active static contract (factory draft)
Evidence: {evidence_grade} — focused coverage fixture.
Source File: fixture.cpp | Binary: BEA.exe, SHA-256 `{PRISTINE_IMAGE_SHA256}`

> Address: `{va}`

## Identity
- Body fixture SHA-256 `{'a' * 64}`.

## Calling convention
unknown

## Prototype and parameter semantics
unknown

## Return value meaning
unknown

## Globals read/written
not_applicable

## Callees relied on / callers
unknown

## Behavior summary
unknown

## Error / edge behavior
unknown

## Runtime corroboration (TTD, bounded)
not_determinable

## Evidence
Fixture evidence exists only for this focused scanner test.

## Confidence
2 - structurally complete fixture only.

## Unresolved questions
Semantic behavior remains unknown.
"""


def run_tool(root: Path) -> tuple[int, str, dict | None]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--repo-root", str(root), "--out", str(root / "out" / "coverage.json")],
        capture_output=True, text=True)
    out_path = root / "out" / "coverage.json"
    payload = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else None
    return proc.returncode, proc.stdout + proc.stderr, payload


def status_of(payload: dict, name: str) -> dict:
    for f in payload["functions"]:
        if f["name"] == name:
            return f
    raise AssertionError(f"{name} absent from payload")


# ---------------------------------------------------------------------------
# fixtures: one per status
# ---------------------------------------------------------------------------

FIX_REGISTER_ROWS = [
    base_register_row("0x00401000", "CRedirect__Subject"),
    base_register_row("0x00401020", "CDisputed__OldNameHolder"),
    base_register_row("0x00401040", "CBlocked__GatedThing"),
    # two independent witness kinds -> VERIFIED
    base_register_row("0x00401060", "CTwoWitness__VerifiedThing",
                      evidence="BASELINE_STATIC;ANALYST_METADATA_ONLY;"
                               "RUNTIME_BOUNDED;TTD_APPLYDAMAGE_LIFE_SHIELD_WRITES_REPLICATED"),
    base_register_row("0x00401080", "CCampaign__PartialCandidate",
                      grade="C1_CANDIDATE_PARTIAL"),
    base_register_row("0x004010a0", "CEnvelope__MeasuredOnly"),
    base_register_row("0x004010c0", "FUN_004010c0"),
]

NOTES = {
    # STALE: the note about the function declares itself a redirect page.
    "functions/T/CRedirect__Subject.md": (
        "# CRedirect__Subject\n\n"
        "> Address: `0x00401000`\n"
        "> Status: **superseded name — this note is a redirect, not evidence**\n\n"
        "Read the canonical record elsewhere.\n"
    ),
    # DISPUTED: the function named ON a dispute line (line-scoped).
    "functions/D/CDisputed__OldNameHolder.md": (
        "# CDisputed__OldNameHolder\n\n"
        "| `0x00401020` | `CDisputed__OldNameHolder` | class proven false and "
        "withdrawn on correction day |\n\n"
        "Separate prose mentions CDisputed__OldNameHolder with no dispute at all.\n"
    ),
    # BLOCKED: its own note forbids implementing from it.
    "functions/B/CBlocked__GatedThing.md": (
        "# CBlocked__GatedThing\n\n"
        "Evidence: INFERRED — hypothesis only, no byte read yet.\n\n"
        "Do not implement Core from this RE root until the owning lane names "
        "the arm.\n"
    ),
    # VERIFIED-by-note+manifest: MEASURED envelope + manifest strong witness.
    "functions/V/CTwoWitness__VerifiedThing.md": (
        "# CTwoWitness__VerifiedThing\n\n"
        "> Address: `0x00401060`\n"
        "Evidence: MEASURED — independently re-read from the pristine backup.\n"
    ),
    # PROVISIONAL: measured envelope, no grade, no second-witness language.
    "functions/P/CEnvelope__MeasuredOnly.md": (
        "# CEnvelope__MeasuredOnly\n\n"
        "> Address: `0x004010a0`\n"
        "Evidence: MEASURED — body bytes pinned below.\n\n"
        "First insn `sub esp, 0x3c`.\n"
    ),
}


def make_full_corpus(root: Path) -> None:
    make_corpus(root, FIX_REGISTER_ROWS)
    for rel, text in NOTES.items():
        w(root, "reverse-engineering/binary-analysis/" + rel, text)
    # manifest granting CTwoWitness__VerifiedThing a second, distinct witness
    w(root, "reverse-engineering/binary-analysis/promotion-manifest-test.tsv",
      "addr\tliveName\texactness\tconfidence\n"
      "0x00401060\tCTwoWitness__VerifiedThing\tCOMPLETE_ENUMERATION\tHIGH\n"
      "0x00401080\tCCampaign__PartialCandidate\tCOMPLETE_ENUMERATION\tLOW\n")


# ---------------------------------------------------------------------------
# per-status fixtures
# ---------------------------------------------------------------------------


def test_stale_from_redirect_note() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-stale-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CRedirect__Subject")
        assert row["status"] == "STALE", row
        assert "note-declares-redirect" in row["flags"], row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_disputed_from_line_scoped_withdrawal() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-disp-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CDisputed__OldNameHolder")
        assert row["status"] == "DISPUTED", row
        assert row["notes"], row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_blocked_from_own_note_gate() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-blk-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CBlocked__GatedThing")
        assert row["status"] == "BLOCKED", row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_verified_needs_two_distinct_kinds_or_promotion() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-ver-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CTwoWitness__VerifiedThing")
        assert row["status"] == "VERIFIED", row
        assert "MANIFEST_WITNESS" in row["witnessKinds"], row
        assert "NOTE_MEASURED" in row["witnessKinds"], row
        assert len(row["witnessKinds"]) >= 2, row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_verified_from_register_replication_suffix() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-ver2-"))
    try:
        make_corpus(root, [
            base_register_row("0x00401000", "CReplicated__Thing",
                              evidence="BASELINE_STATIC;ANALYST_METADATA_ONLY;RUNTIME_BOUNDED;"
                                       "TTD_APPLYDAMAGE_LIFE_SHIELD_WRITES_REPLICATED"),
            base_register_row("0x00401020", "CSurvivor__Adjudicated",
                              evidence="BASELINE_STATIC;ANALYST_METADATA_ONLY;RUNTIME_BOUNDED;"
                                       "INDEPENDENT_REFUTATION_SURVIVED"),
        ])
        code, out, payload = run_tool(root)
        assert code == 0, out
        assert status_of(payload, "CReplicated__Thing")["status"] == "VERIFIED"
        assert status_of(payload, "CSurvivor__Adjudicated")["status"] == "VERIFIED"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_review_ready_from_campaign_grade() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-rev-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CCampaign__PartialCandidate")
        assert row["status"] == "REVIEW_READY", row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_provisional_from_measured_envelope_without_second_witness() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-prov-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CEnvelope__MeasuredOnly")
        assert row["status"] == "PROVISIONAL", row
        assert row["witnessKinds"] == ["NOTE_MEASURED"], row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_skeleton_is_the_honest_default() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-skel-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "FUN_004010c0")
        assert row["status"] == "SKELETON", row
        assert "name-only" in row["evidenceClasses"], row
        assert row["witnessKinds"] == [], row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_valid_factory_contract_promotes_only_joined_skeleton() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-contract-"))
    try:
        make_corpus(root, [
            base_register_row("0x00401000", "CFactory__Contracted"),
            base_register_row("0x00401020", "CFactory__Untouched"),
        ])
        w(root,
          "reverse-engineering/contracts/factory/"
          "CFactory__Contracted__00401000.md",
          full_contract("CFactory__Contracted", "0x00401000"))

        code, out, payload = run_tool(root)
        assert code == 0, out
        contracted = status_of(payload, "CFactory__Contracted")
        untouched = status_of(payload, "CFactory__Untouched")
        assert contracted["status"] == "REVIEW_READY", contracted
        assert contracted["witnessKinds"] == [], contracted
        assert contracted["contracts"] == [
            "reverse-engineering/contracts/factory/"
            "CFactory__Contracted__00401000.md"
        ], contracted
        assert untouched["status"] == "SKELETON", untouched
        assert untouched.get("contracts", []) == [], untouched
        assert len(payload["functions"]) == 2
        assert sum(payload["statusCounts"].values()) == 2
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_factory_contract_preserves_stronger_status_and_measured_floor() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-contract-floor-"))
    try:
        make_corpus(root, [
            base_register_row("0x00401000", "CFactory__InferredOnly"),
            base_register_row("0x00401020", "CFactory__ReviewReady",
                              grade="C1_CANDIDATE_PARTIAL"),
            base_register_row(
                "0x00401040", "CFactory__Verified",
                evidence="BASELINE_STATIC;ANALYST_METADATA_ONLY;"
                         "INDEPENDENT_REFUTATION_SURVIVED"),
        ])
        w(root,
          "reverse-engineering/contracts/factory/"
          "CFactory__InferredOnly__00401000.md",
          full_contract("CFactory__InferredOnly", "0x00401000", "INFERRED"))
        w(root,
          "reverse-engineering/contracts/factory/"
          "CFactory__ReviewReady__00401020.md",
          full_contract("CFactory__ReviewReady", "0x00401020"))
        w(root,
          "reverse-engineering/contracts/factory/"
          "CFactory__Verified__00401040.md",
          full_contract("CFactory__Verified", "0x00401040"))

        code, out, payload = run_tool(root)
        assert code == 0, out
        inferred = status_of(payload, "CFactory__InferredOnly")
        review_ready = status_of(payload, "CFactory__ReviewReady")
        verified = status_of(payload, "CFactory__Verified")
        assert inferred["status"] == "SKELETON", inferred
        assert "byte-read" not in inferred["evidenceClasses"], inferred
        assert review_ready["status"] == "REVIEW_READY", review_ready
        assert verified["status"] == "VERIFIED", verified
        assert verified["witnessKinds"] == [], verified
        assert len(payload["functions"]) == 3
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_factory_contract_path_crlf_and_va_case_are_deterministic() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-contract-normalize-"))
    try:
        make_corpus(root, [
            base_register_row("0X00401000", "CFactory__CanonicalInventoryName"),
        ])
        path = root / (
            "reverse-engineering/contracts/MiXeD/"
            "CFactory__ContractDocument__00401000.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            full_contract("CFactory__ContractDocument", "0x00401000")
            .replace("\n", "\r\n").encode("utf-8")
        )

        code1, out1, payload1 = run_tool(root)
        code2, out2, payload2 = run_tool(root)
        assert code1 == code2 == 0, out1 + out2
        row = status_of(payload1, "CFactory__CanonicalInventoryName")
        assert row["status"] == "REVIEW_READY", row
        assert row["contracts"] == [
            "reverse-engineering/contracts/MiXeD/"
            "CFactory__ContractDocument__00401000.md"
        ], row
        assert payload1["functions"] == payload2["functions"]
        assert payload1["statusCounts"] == payload2["statusCounts"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_invalid_factory_contracts_fail_closed_without_counting() -> None:
    scenarios = []

    def duplicate_va(root: Path) -> None:
        make_corpus(root, [base_register_row("0x00401000", "CFactory__Inventory")])
        w(root, "reverse-engineering/contracts/a/CFactory__First__00401000.md",
          full_contract("CFactory__First", "0x00401000"))
        w(root, "reverse-engineering/contracts/b/CFactory__Second__00401000.md",
          full_contract("CFactory__Second", "0x00401000"))

    scenarios.append(("duplicate-va", duplicate_va, "DUPLICATE_VA"))

    def duplicate_name(root: Path) -> None:
        make_corpus(root, [
            base_register_row("0x00401000", "CFactory__InventoryA"),
            base_register_row("0x00401020", "CFactory__InventoryB"),
        ])
        w(root,
          "reverse-engineering/contracts/a/CFactory__DuplicateName__00401000.md",
          full_contract("CFactory__DuplicateName", "0x00401000"))
        w(root,
          "reverse-engineering/contracts/b/cfactory__duplicatename__00401020.md",
          full_contract("cfactory__duplicatename", "0x00401020"))

    scenarios.append(("duplicate-name", duplicate_name, "DUPLICATE_NAME"))

    def anonymous_name(root: Path) -> None:
        make_corpus(root, [base_register_row("0x00401000", "CFactory__Inventory")])
        w(root, "reverse-engineering/contracts/a/FUN_00401000__00401000.md",
          full_contract("FUN_00401000", "0x00401000"))

    scenarios.append(("anonymous-name", anonymous_name, "ANONYMOUS_NAME"))

    def bad_filename_va(root: Path) -> None:
        make_corpus(root, [base_register_row("0x00401000", "CFactory__Inventory")])
        w(root, "reverse-engineering/contracts/a/CFactory__BadStem__00401020.md",
          full_contract("CFactory__BadStem", "0x00401000"))

    scenarios.append(("bad-filename-va", bad_filename_va, "VA_STEM_MISMATCH"))

    def missing_structure(root: Path) -> None:
        make_corpus(root, [base_register_row("0x00401000", "CFactory__Inventory")])
        text = full_contract("CFactory__MissingSection", "0x00401000").replace(
            "## Unresolved questions\nSemantic behavior remains unknown.\n", "")
        w(root,
          "reverse-engineering/contracts/a/CFactory__MissingSection__00401000.md",
          text)

    scenarios.append(("missing-structure", missing_structure, "MISSING_SECTION"))

    def orphan_va(root: Path) -> None:
        make_corpus(root, [base_register_row("0x00401000", "CFactory__Inventory")])
        w(root, "reverse-engineering/contracts/a/CFactory__Orphan__00401020.md",
          full_contract("CFactory__Orphan", "0x00401020"))

    scenarios.append((
        "orphan-va", orphan_va, "not present in the canonical function inventory"
    ))

    for label, arrange, expected in scenarios:
        root = Path(tempfile.mkdtemp(prefix=f"ccov-contract-{label}-"))
        try:
            arrange(root)
            code, out, payload = run_tool(root)
            assert code == 2, (label, code, out)
            assert expected in out, (label, expected, out)
            assert payload is None, label
        finally:
            shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# falsification: the honesty contract must actually bind
# ---------------------------------------------------------------------------


def test_one_witness_twice_is_not_two() -> None:
    """A measured note PLUS a manifest row with a WEAK value must not verify."""
    root = Path(tempfile.mkdtemp(prefix="ccov-onew-"))
    try:
        make_corpus(root, [base_register_row("0x00401000", "CWeak__OnceWitnessed")])
        w(root, "reverse-engineering/binary-analysis/functions/W/CWeak__OnceWitnessed.md",
          "# CWeak__OnceWitnessed\n\nEvidence: MEASURED — bytes pinned.\n")
        # patch-surface-shaped manifest: confidence STATIC_ONLY is NOT a witness
        w(root, "patches/patch-surface-rows.tsv",
          "va\toffset\toriginal_bytes\tpatched_bytes\teffect\tconfidence\n"
          "0x00401000\t0x00001000\tcdcd\tabab\tsome effect\tSTATIC_ONLY\n")
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CWeak__OnceWitnessed")
        assert row["status"] != "VERIFIED", row
        assert row["witnessKinds"] == ["NOTE_MEASURED"], row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_scope_discipline_is_not_a_block() -> None:
    """"did not widen / did not mill" is bookkeeping, never BLOCKED."""
    root = Path(tempfile.mkdtemp(prefix="ccov-scope-"))
    try:
        make_corpus(root, [base_register_row("0x00401000", "CScope__Disciplined")])
        w(root, "reverse-engineering/binary-analysis/functions/S/CScope__Disciplined.md",
          "# CScope__Disciplined\n\n"
          "Did not mill FUN_*. Did not widen the existing Gen31 C2 row. "
          "Did not implement lock sets.\n")
        code, out, payload = run_tool(root)
        assert code == 0, out
        row = status_of(payload, "CScope__Disciplined")
        assert row["status"] == "SKELETON", row
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_denominator_mismatch_fails_closed_and_writes_nothing() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-denom-"))
    try:
        # register with FEWER rows than the pinned denominator
        make_corpus(root, FIX_REGISTER_ROWS[:3])
        (root / "developer_state.json").write_text(state_json(7), encoding="utf-8")
        code, out, payload = run_tool(root)
        assert code == 2, (code, out)
        assert "denominator" in out.lower(), out
        assert payload is None, "fail-closed run must not publish a dashboard"
        assert not (root / "out").exists(), "no output directory on failure"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_missing_register_fails_closed() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-noreg-"))
    try:
        w(root, "developer_state.json", state_json(7))
        code, out, payload = run_tool(root)
        assert code == 2, (code, out)
        assert payload is None
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_missing_current_re_authority_fails_closed() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-noauth-"))
    try:
        w(root, "developer_state.json", json.dumps({"something_else": {}}))
        w(root, "reverse-engineering/EVIDENCE-REGISTER.tsv",
          "# bea.re.evidence-register.v2\n" + REGISTER_HEADER + "\n"
          + "\n".join(FIX_REGISTER_ROWS) + "\n")
        code, out, payload = run_tool(root)
        assert code == 2, (code, out)
        assert payload is None
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_dispute_requires_the_line_not_the_file() -> None:
    """Mentioning a function on a clean line must NOT inherit a dispute
    recorded elsewhere in the same note."""
    root = Path(tempfile.mkdtemp(prefix="ccov-linescope-"))
    try:
        make_corpus(root, [
            base_register_row("0x00401000", "CClean__Bystander"),
            base_register_row("0x00401020", "COther__WithdrawnName"),
        ])
        w(root, "reverse-engineering/binary-analysis/functions/O/COther__WithdrawnName.md",
          "# COther__WithdrawnName\n\n"
          "| `0x00401020` | `COther__WithdrawnName` | old label **withdrawn** "
          "pending re-measurement |\n\n"
          "Related: CClean__Bystander shares the translation unit.\n")
        code, out, payload = run_tool(root)
        assert code == 0, out
        assert status_of(payload, "CClean__Bystander")["status"] == "SKELETON"
        assert status_of(payload, "COther__WithdrawnName")["status"] == "DISPUTED"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_totals_always_add_up() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-totals-"))
    try:
        make_full_corpus(root)
        code, out, payload = run_tool(root)
        assert code == 0, out
        total = sum(payload["statusCounts"].values())
        assert total == len(payload["functions"]), total
        assert total == payload["denominator"]["functions"], total
        assert total >= 7, total
        assert sum(payload["evidenceClassCounts"].values()) >= total
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_reruns_are_byte_identical_when_inputs_are_unchanged() -> None:
    root = Path(tempfile.mkdtemp(prefix="ccov-idem-"))
    try:
        make_full_corpus(root)
        code1, _, p1 = run_tool(root)
        raw1 = (root / "out" / "coverage.json").read_bytes()
        time.sleep(1.1)
        code2, _, p2 = run_tool(root)
        raw2 = (root / "out" / "coverage.json").read_bytes()
        assert code1 == code2 == 0
        for key in ("schema", "statusCounts", "evidenceClassCounts", "functions"):
            assert p1[key] == p2[key], key
        assert p1["generatedAtUtc"]  # stamps exist
        assert raw1 == raw2
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# real-corpus invariants and the fixed wave-1 join receipt
# ---------------------------------------------------------------------------


def test_real_corpus_invariants() -> None:
    repo = Path(__file__).resolve().parents[1]
    register = repo / "reverse-engineering" / "EVIDENCE-REGISTER.tsv"
    if not register.exists():
        print("SKIP real-corpus invariants (no register in this checkout)")
        return
    out_dir = Path(tempfile.mkdtemp(prefix="ccov-real-"))
    try:
        out_path = out_dir / "coverage.json"
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--repo-root", str(repo),
             "--out", str(out_path)],
            capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode == 0, out
        payload = json.loads(out_path.read_text(encoding="utf-8"))
        assert payload["schema"] == "bea.re.contract-coverage.v1"
        assert payload["inputs"]["registerRows"] == 8329
        assert payload["inputs"]["contractFiles"] == 25
        assert payload["inputs"]["contractRowsJoined"] == 25
        assert payload["denominator"]["functions"] == 8329
        assert len(payload["functions"]) == 8329
        assert sum(payload["statusCounts"].values()) == 8329
        assert payload["statusCounts"] == {
            "STALE": 0,
            "DISPUTED": 44,
            "BLOCKED": 58,
            "VERIFIED": 591,
            "REVIEW_READY": 451,
            "PROVISIONAL": 1,
            "SKELETON": 7184,
        }
        known = {"STALE", "DISPUTED", "BLOCKED", "VERIFIED", "REVIEW_READY",
                 "PROVISIONAL", "SKELETON"}
        by_va = {row["va"]: row for row in payload["functions"]}
        joined = {
            row["va"] for row in payload["functions"] if row.get("contracts")
        }
        assert joined == WAVE1_REVIEW_FLOOR_VAS | set(WAVE1_PRESERVED_STATUS_BY_VA)
        floor_rows = {
            row["va"] for row in payload["functions"]
            if "factory-contract-review-floor" in row["flags"]
        }
        assert floor_rows == WAVE1_REVIEW_FLOOR_VAS
        for va in WAVE1_REVIEW_FLOOR_VAS:
            assert by_va[va]["status"] == "REVIEW_READY", by_va[va]
            assert by_va[va]["witnessKinds"] == [], by_va[va]
        for va, expected_status in WAVE1_PRESERVED_STATUS_BY_VA.items():
            assert by_va[va]["status"] == expected_status, by_va[va]
            assert "factory-contract-review-floor" not in by_va[va]["flags"], by_va[va]
        for row in payload["functions"]:
            assert row["status"] in known
            assert isinstance(row["notes"], list)
            assert isinstance(row.get("contracts", []), list)
        assert payload["elapsedSeconds"] < 300, "corpus scan must stay well under 5 min"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed += 1
            print(f"FAIL {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
