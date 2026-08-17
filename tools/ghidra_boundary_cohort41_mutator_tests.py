#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Mutator tests for the 41-row function-boundary cohort applier.

Three tiers, in increasing strength:

1. `Cohort41MutatorSourceTests` - the source contract every prior boundary lane
   pins: which mutations are authorized, which are forbidden, which identity and
   census values are frozen, and that every gate carries a distinct refusal
   message.  Runs everywhere, no external state.

2. `Cohort41ManifestContractTests` - the immutable target manifest is re-measured
   from scratch (growth-only, entry-anchored, in-`.text`, non-overlapping,
   delta-exact, byteProof == added, terminator inside body) and, when the
   pristine specimen is materialised locally, every byteProof and terminator is
   reproduced from its bytes.

3. `Cohort41GateRefusalMatrixTests` - the executable half.  Prior lanes assert
   the happy path; these assert that **each gate refuses its own violation**.
   The matrix is produced by running the applier under Ghidra headless against a
   throwaway replica with one deliberately-broken manifest per gate, every run
   WRITABLE so a broken gate could persist damage.  Point
   `BEA_COHORT41_GATE_MATRIX` at the resulting gate-matrix.json to enforce it:

       python <scratch>/scripts/make_gate_probes.py <manifest> <outdir>
       python <scratch>/scripts/run_gate_matrix.py
       BEA_COHORT41_GATE_MATRIX=<...>/receipts/gate-matrix.json \
           python -m unittest tools.ghidra_boundary_cohort41_mutator_tests

   The REQUIRED_GATES list below is the contract: a matrix that omits a gate,
   fails to refuse, or reports an applied row fails the test.
"""

from __future__ import annotations

import hashlib
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "tools/GhidraRehearseBoundaryCohort41.java"
V2 = ROOT / "tools/GhidraRehearseBoundaryCohort41V2.java"
V3 = ROOT / "tools/GhidraRehearseBoundaryCohort41V3.java"
MANIFEST = (
    ROOT
    / "reverse-engineering/binary-analysis/"
    "boundary-cohort41-promotion-manifest-2026-08-16.tsv"
)
SPECIMEN = (
    ROOT
    / "local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe"
)

V1_SHA256 = "d3c2fe8b5b1687127d34d097e72c4819e46ad73ef6917a91c6175939c7e3c9c0"
V2_SHA256 = "5899b2d6d3580d48b7f5661eb40e42a3b103f41151ec77089ba010ecc674856c"
V3_SHA256 = "559941cd43097e9dee5291d0b3fae823166c740efe929bd82b27a3f6f0fb1eb5"
MANIFEST_SHA256 = "9abc5aedb1c7ff3c959670a714e457480e83ed6075b76a23cee5195e20399ed3"
MANIFEST_BYTES = 6217
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
IMAGE_BASE = 0x400000
TEXT_LO, TEXT_HI = 0x00401000, 0x005D7FFF

HEADER = (
    "addr\tcurrentRanges\tproposedRanges\tsubtype\tterminatorVa"
    "\tterminatorBytes\tdeltaBytes\tbyteProof\tagreesWithNote"
)

# Every gate the applier implements, paired with the exact refusal text it must
# emit.  Tier 3 requires a matrix entry that actually provoked each one.
REQUIRED_GATES = {
    "g01-header-drift": "manifest header drift",
    "g02-column-count": "column count",
    "g03-duplicate-address": "duplicate address in manifest",
    "g04-addr-not-0x": "address not 0x-prefixed",
    "g05-unparseable-range": "unparseable range text",
    "g06-not-at-entry": "proposed body does not start at the entry point",
    "g07-leaves-text": "proposed body leaves .text",
    "g08-drops-owned-bytes": "DROPS currently owned bytes",
    "g09-delta-mismatch": "!= measured",
    "g10-adds-nothing": "proposal adds nothing",
    "g11-target-target-overlap": "target/target overlap at",
    "g12-no-function-at-entry": "NO FUNCTION AT ENTRY",
    "g13-current-state-drift": "CURRENT STATE DRIFT",
    "g14-terminator-bytes-differ": "terminator bytes differ",
    "g15-terminator-outside-body": "terminator not inside the proposed body",
    "g16-malformed-byteproof": "malformed byteProof segment",
    "g17-byteproof-no-reproduce": "byteProof does not reproduce",
    "g18-byteproof-range-mismatch": "!= added ranges",
    "g19-ends-mid-instruction": "ENDS MID-INSTRUCTION",
    "g20-overlaps-existing-function": "OVERLAPS existing function",
    "g21-delta-not-numeric": "deltaBytes not numeric",
    "g22-row-count-apply": "row count 40 != 41",
    "g23-manifest-sha-pin": "manifest sha256",
    "g24-forbidden-project-path": "forbidden_project_path",
    "g25-not-in-rehearsal-scratch": "project_not_in_rehearsal_scratch",
    "g26-bad-mode": "reason=bad_mode",
    "g27-usage-arity": "reason=usage",
}

# Gates that cannot be provoked by doctoring a manifest or a path: they need a
# replica whose census or program identity has actually moved.  Tier 3 accepts
# these from a separate mutated-replica probe when present.
CENSUS_GATES = {
    "g28-pre-instruction-count": "PRE instruction count",
    "g29-pre-function-count": "PRE function count",
}

# ---------------------------------------------------------------------------
# V3 adds the classification invariant: every admitted byte must end fully
# classified.  These gates do not exist in V1/V2 at all, and three of them can
# only be provoked by deliberate self-sabotage (the probe-fault-* modes), since
# the applier's own confinement makes them structurally unreachable otherwise.
V3_REQUIRED_GATES = {
    # provoked by a doctored manifest.  Ghidra's restrictedSet bounds where a
    # disassembly may be seeded and followed, NOT how far the last instruction
    # may extend - so these two are load-bearing, not residual.
    "gV45-instruction-overruns-admitted-edge":
        "INSTRUCTION ESCAPED the proposed body",
    "gV46-post-classification-ends-mid-instruction":
        "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION",
    # provoked by probe-fault-strandbytes
    "gV30-unclassified-bytes-remain": "UNCLASSIFIED BYTES REMAIN",
    "gV31-classified-regression": "CLASSIFIED-BYTE REGRESSION",
    # provoked by probe-fault-precedentclear: the verbatim precedent shape,
    # which is exactly what turns 0x00450010's defined bytes into undefined ones
    "gV31b-regression-from-the-verbatim-precedent-shape":
        "CLASSIFIED-BYTE REGRESSION",
    "gV36-precondition-row-mutated": "PRECONDITION ROW WAS MUTATED",
    # provoked by probe-fault-escape
    "gV32-instruction-escape": "INSTRUCTION ESCAPE",
    "gV33-reference-escape": "REFERENCE ESCAPE",
    "gV38-post-instruction-pin": "POST instruction count",
    "gV39-post-reference-pin": "POST reference count",
    # provoked by probe-fault-extraclear
    "gV34-clear-plan-mismatch": "CLEAR PLAN MISMATCH",
    "gV35-jump-table-cleared": "JUMP/SEH TABLE ROW WAS CLEARED",
    # provoked by probe-fault-clearescape
    "gV37-clear-escaped-admitted": "CLEAR ESCAPED the admitted range",
    # provoked by re-running apply against an already-applied replica
    "gV40-reapply-current-state-drift": "CURRENT STATE DRIFT",
    "gV41-pre-instruction-pin": "PRE instruction count",
    "gV42-pre-reference-pin": "PRE reference count",
    "gV43-pre-bookmark-pin": "PRE bookmark count",
    "gV44-pre-admitted-undefined-pin": "PRE admitted-undefined byte count",
}

# Measured on a replica built from the off-volume PRE backup and reproduced
# digest-for-digest on a second independent replica.
V3_PINS = {
    "PRE_FUNCTIONS = 8329L",
    "PRE_INSTRUCTIONS = 551143L",
    "PRE_REFERENCES = 234478L",
    "PRE_BOOKMARKS = 2303L",
    "POST_FUNCTIONS = 8329L",
    "POST_INSTRUCTIONS = 551232L",
    "POST_REFERENCES = 234493L",
    "POST_BOOKMARKS = 2301L",
    "ADMITTED_BYTES = 3293L",
    "ADMITTED_UNDEFINED_BYTES = 274L",
    "CLEARED_UNITS = 25L",
    "CLEARED_BYTES = 63L",
}

# The ONLY spans V3 may clear.  Six rows, derived dynamically at run time and
# then required to equal this pin exactly.
V3_CLEAR_PLAN = [
    '"0x00417190\\t00417349-00417350"',
    '"0x00437490\\t00437a3e-00437a5b"',
    '"0x00450010\\t0045004d-00450050;00450052-00450059"',
    '"0x0045ffa0\\t00460020-00460026"',
    '"0x0046ff10\\t00470050-00470053"',
    '"0x004c4100\\t004c4148-004c4149"',
]


def rows() -> list[dict[str, str]]:
    text = MANIFEST.read_text(encoding="utf-8")
    lines = [l for l in text.split("\n") if l]
    assert lines[0] == HEADER
    out = []
    for line in lines[1:]:
        cells = line.split("\t")
        out.append(dict(zip(HEADER.split("\t"), cells)))
    return out


def to_set(text: str) -> set[int]:
    acc: set[int] = set()
    for part in text.split(";"):
        lo, hi = part.split("-")
        acc.update(range(int(lo, 16), int(hi, 16) + 1))
    return acc


class Cohort41MutatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v1 = V1.read_text(encoding="utf-8")
        cls.v2 = V2.read_text(encoding="utf-8")

    def test_applier_sources_are_frozen(self) -> None:
        self.assertEqual(hashlib.sha256(V1.read_bytes()).hexdigest(), V1_SHA256)
        self.assertEqual(hashlib.sha256(V2.read_bytes()).hexdigest(), V2_SHA256)

    def test_only_setbody_is_authorized(self) -> None:
        for source, label in ((self.v1, "v1"), (self.v2, "v2")):
            for forbidden in (
                "setName(",
                "setComment(",
                "setRepeatableComment(",
                "addTag(",
                "setCallingConvention(",
                "replaceParameters(",
                "setReturnType(",
                "setSignature(",
                "createData(",
                "removeData(",
                "clearListing(",
                "setBytes(",
                "createFunction(",
                "removeFunction(",
                "addMemoryReference(",
                "Disassembler",
                "disassemble",
            ):
                self.assertNotIn(forbidden, source, f"{label}: {forbidden}")
            # exactly one real call site; the only other mention is the header
            # comment naming the single authorized mutation.
            code = "\n".join(
                l for l in source.splitlines() if not l.lstrip().startswith("//")
            )
            self.assertEqual(code.count(".setBody("), 1, label)
            self.assertEqual(code.count("fn.setBody(row.proposed);"), 1, label)
            self.assertEqual(source.count(".setBody("), 2, label)
            self.assertIn("Function.setBody()", source)

    def test_live_is_forbidden_by_construction(self) -> None:
        for source in (self.v1, self.v2):
            self.assertIn('POLICY = "LIVE_FORBIDDEN"', source)
            self.assertIn('CONTAINMENT_SEGMENT = "boundary-rehearsal"', source)
            for marker in (
                '"ghidra\\\\projects"',
                '"ghidra/projects"',
                '"onslaught-career-editor\\\\reverse-engineering"',
                '"onslaught-career-editor/reverse-engineering"',
            ):
                self.assertIn(marker, source)
            self.assertIn("COHORT41_REFUSE reason=forbidden_project_path", source)
            self.assertIn(
                "COHORT41_REFUSE reason=project_not_in_rehearsal_scratch", source
            )

    def test_identity_and_census_are_pinned(self) -> None:
        for source in (self.v1, self.v2):
            for declaration in (
                'PROGRAM_NAME = "BEA.exe"',
                'PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"',
                'IMAGE_BASE = "00400000"',
                'LANGUAGE = "x86:LE:32:default"',
                'COMPILER_SPEC = "windows"',
                "TEXT_START = 0x00401000L",
                "TEXT_END = 0x005d7fffL",
                "PRE_FUNCTIONS = 8329L",
                "PRE_INSTRUCTIONS = 551143L",
                "TARGET_COUNT = 41",
                "MANIFEST_BYTES = 6217L",
            ):
                self.assertIn(declaration, source, declaration)
            self.assertIn(SPECIMEN_SHA256, source)
            self.assertIn(MANIFEST_SHA256, source)

    def test_every_gate_has_a_distinct_refusal_message(self) -> None:
        messages = [
            "reason=usage",
            "reason=bad_mode",
            "reason=no_project_locator",
            "reason=no_current_program",
            "program name ",
            "program md5 ",
            "program sha256 ",
            "image base ",
            "language ",
            "compiler spec",
            "text block geometry",
            "PRE function count ",
            "PRE instruction count ",
            "manifest bytes ",
            "manifest sha256 ",
            "manifest header drift",
            " column count ",
            "duplicate address in manifest",
            "row count ",
            "address not 0x-prefixed",
            "unparseable range text",
            "proposed body does not start at the entry point",
            "proposed body leaves .text",
            "proposal DROPS currently owned bytes: ",
            "proposal adds nothing",
            "target/target overlap at ",
            "NO FUNCTION AT ENTRY",
            "CURRENT STATE DRIFT: ",
            "READBACK STATE DRIFT: ",
            "terminator unreadable at ",
            "terminator bytes differ: ",
            "terminator not inside the proposed body",
            "malformed byteProof segment",
            "byteProof range unreadable at ",
            "byteProof does not reproduce at ",
            "byteProof ranges ",
            "proposal ENDS MID-INSTRUCTION inside ",
            "OVERLAPS existing function ",
            "setBody threw ",
            "in-process verify failed",
            "function census moved ",
            "instruction count moved ",
            "COHORT41_NO_MUTATION_PERFORMED",
        ]
        for source in (self.v1, self.v2):
            for message in messages:
                self.assertIn(message, source, message)

    def test_mutating_modes_refuse_before_touching_anything(self) -> None:
        for source in (self.v1, self.v2):
            # the gate sweep runs over every row before any setBody happens
            self.assertLess(
                source.index("boolean gatesPassed = failures.isEmpty();"),
                source.index("fn.setBody(row.proposed);"),
            )
            self.assertIn(
                "println(\"COHORT41_REFUSE reason=gate_failure count=\"", source
            )
            self.assertIn('println("COHORT41_NO_MUTATION_PERFORMED");', source)

    def test_post_mutation_census_is_asserted_unchanged(self) -> None:
        for source in (self.v1, self.v2):
            self.assertIn("if (postFunctions != preFunctions)", source)
            self.assertIn("if (postInstructions != preInstructions)", source)

    def test_v2_adds_only_the_staged_mid_batch_halt(self) -> None:
        self.assertIn('"probe-after-one".equals(mode)', self.v2)
        self.assertIn("COHORT41_PROBE_AFTER_ONE banner=mid-batch-halt", self.v2)
        self.assertIn("COHORT41_PARTIAL_STATE rowsApplied=", self.v2)
        self.assertIn("outer_rollback_required=true", self.v2)
        self.assertIn("recovery=RESTORE_VERIFIED_PRE_BACKUP", self.v2)
        self.assertIn('row.verdict = "HALTED_BEFORE_APPLY";', self.v2)
        self.assertNotIn("probe-after-one", self.v1)
        # the cohort digest pin and the row-count gate stay ENFORCED in v2:
        # only "probe-apply" disables them, and afterOne is a separate flag.
        self.assertIn("if (!probeMode) {", self.v2)
        self.assertIn("if (!probeMode && rows.size() != TARGET_COUNT)", self.v2)
        self.assertNotIn("afterOne && rows.size()", self.v2)

    def test_v2_differs_from_v1_only_in_the_staged_probe(self) -> None:
        import difflib

        added = [
            l[1:].strip()
            for l in difflib.unified_diff(
                self.v1.splitlines(), self.v2.splitlines(), n=0, lineterm=""
            )
            if l.startswith("+") and not l.startswith("+++")
        ]
        allowed = ("probe-after-one", "afterOne", "PROBE_AFTER_ONE",
                   "PARTIAL_STATE", "HALTED_BEFORE_APPLY", "appliedRows",
                   "rehearsal.v2", "GhidraRehearseBoundaryCohort41V2",
                   "rowsToApply=1", "outer_rollback_required", "recovery=",
                   "rowsPending=", "halted", "continue;", "}", "{",
                   "mid-batch halt", "pinned cohort digest, then setBody",
                   "leaving rows 2..41 untouched so partial state can be",
                   "proved coherent and recoverable.",
                   'println("COHORT41_FAIL reason=bad_mode value=" + mode);',
                   'if (!("dry".equals(mode)',   # the mode check, reflowed
                   "return;")

        for line in added:
            if not line:
                continue
            self.assertTrue(
                any(token in line for token in allowed),
                f"v2 introduced an unreviewed line: {line!r}",
            )


class Cohort41V3SourceTests(unittest.TestCase):
    """V3's contract: a bigger authorized-verb set, bounded exactly."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v3 = V3.read_text(encoding="utf-8")
        cls.code = "\n".join(
            l for l in cls.v3.splitlines() if not l.lstrip().startswith("//")
        )

    def test_v3_source_is_frozen(self) -> None:
        self.assertEqual(hashlib.sha256(V3.read_bytes()).hexdigest(), V3_SHA256)

    def test_v3_is_still_live_forbidden(self) -> None:
        self.assertIn('POLICY = "LIVE_FORBIDDEN"', self.v3)
        self.assertIn('CONTAINMENT_SEGMENT = "boundary-rehearsal"', self.v3)
        for marker in (
            '"ghidra\\\\projects"',
            '"ghidra/projects"',
            '"onslaught-career-editor\\\\reverse-engineering"',
            '"onslaught-career-editor/reverse-engineering"',
        ):
            self.assertIn(marker, self.v3, marker)
        self.assertIn("COHORT41_REFUSE reason=forbidden_project_path", self.v3)
        self.assertIn("COHORT41_REFUSE reason=project_not_in_rehearsal_scratch", self.v3)
        # no mode, flag or argument may switch the policy off
        self.assertNotIn("LIVE_ALLOWED", self.v3)
        self.assertEqual(self.code.count("FORBIDDEN_PATH_MARKERS"), 2)

    def test_v3_authorizes_exactly_four_verbs(self) -> None:
        # authorized, each with exactly one real call site
        self.assertEqual(self.code.count("fn.setBody(row.proposed);"), 1)
        self.assertEqual(self.code.count(".setBody("), 1)
        self.assertEqual(self.code.count("d.disassemble(") +
                         self.code.count("disassembler.disassemble("), 2)
        self.assertEqual(self.code.count("bm.removeBookmark("), 1)
        # clearCodeUnits: one in phase 2, one in each of the four fault
        # injectors, which are adverse-testing-only paths
        self.assertEqual(self.code.count("clearCodeUnits("), 5)
        for fault in ("precedentClearFault", "faultExtraClear", "faultClearEscape",
                      "faultStrand"):
            self.assertIn(fault, self.code)

    def test_v3_forbids_every_other_mutation(self) -> None:
        for forbidden in (
            "setName(",
            "setComment(",
            "setRepeatableComment(",
            "addTag(",
            "setCallingConvention(",
            "replaceParameters(",
            "setReturnType(",
            "setSignature(",
            "createData(",
            "createAsciiString(",
            "removeData(",
            "clearListing(",
            "setBytes(",
            "createFunction(",
            "removeFunction(",
            "addMemoryReference(",
            "addExternalReference(",
            "removeReference(",
            "createLabel(",
            "createSymbol(",
            "setPrimary(",
            "analyzeAll(",
            "analyzeChanges(",
        ):
            self.assertNotIn(forbidden, self.code, forbidden)

    def test_v3_disassembly_can_never_leave_the_admitted_bytes(self) -> None:
        # the restricted set handed to the disassembler is the row's own added
        # ranges - never the proposed body, never .text
        self.assertIn("disassembler.disassemble(seeds, restricted, true);", self.code)
        self.assertIn("classify(row, row.added, faultPrecedent, faultPrecedent);",
                      self.code)
        # phase 2 refuses to clear anything not wholly inside the added ranges
        self.assertIn(
            "if (!row.added.contains(unit.getMinAddress(), unit.getMaxAddress()))",
            self.code,
        )

    def test_v3_pins_its_own_remeasurement(self) -> None:
        for pin in V3_PINS:
            self.assertIn(pin, self.v3, pin)
        for span in V3_CLEAR_PLAN:
            self.assertIn(span, self.v3, span)
        self.assertEqual(self.v3.count('"0x00450010\\t'), 1)
        # the pinned stale-bookmark set is exactly 15 addresses
        block = self.v3.split("STALE_BOOKMARKS = {", 1)[1].split("};", 1)[0]
        self.assertEqual(len([t for t in block.split('"') if len(t) == 8]), 15)

    def test_v3_new_gates_each_have_a_distinct_message(self) -> None:
        for message in (
            "UNCLASSIFIED BYTES REMAIN in the admitted body: ",
            "CLASSIFIED-BYTE REGRESSION ",
            "CLEAR ESCAPED the admitted range at ",
            "JUMP/SEH TABLE ROW WAS CLEARED: ",
            "JUMP/SEH TABLE DATA CHANGED ",
            "PRECONDITION ROW WAS MUTATED: ",
            "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION",
            "INSTRUCTION ESCAPED the proposed body at ",
            "CLEAR PLAN MISMATCH derived=",
            "INSTRUCTION ESCAPE: program delta ",
            "REFERENCE ESCAPE: program delta ",
            "STALE BOOKMARK OUTSIDE the admitted ranges at ",
            "STALE BOOKMARK at an unclassified byte ",
            "PINNED STALE BOOKMARK ABSENT at ",
            "BOOKMARK CREATED OUTSIDE the admitted ranges at ",
            "BOOKMARK REMOVED OUTSIDE the admitted ranges at ",
            "BOOKMARKS SURVIVED hygiene: ",
            "PRE reference count ",
            "PRE bookmark count ",
            "PRE admitted-undefined byte count ",
            "POST instruction count ",
            "POST reference count ",
            "POST bookmark count ",
            "POST function count ",
            "admitted byte count ",
            "cleared unit count ",
            "cleared byte count ",
        ):
            self.assertIn(message, self.v3, message)

    def test_v3_gates_run_before_setbody_and_abort_on_failure(self) -> None:
        self.assertLess(
            self.code.index("UNCLASSIFIED BYTES REMAIN"),
            self.code.index("fn.setBody(row.proposed);"),
        )
        self.assertIn("if (settingBodies && failures.isEmpty()) {", self.code)
        self.assertIn("currentProgram.endTransaction(tx, commit);", self.code)
        self.assertIn("COHORT41_TRANSACTION_ABORTED", self.v3)

    def test_v3_fault_and_plan_modes_can_never_commit(self) -> None:
        self.assertIn(
            "commit = failures.isEmpty() && !planOnly && !faultMode;", self.code
        )
        self.assertIn("COHORT41_FAULT_UNDETECTED", self.v3)
        # probeMode disables pins; it must NOT cover the fault modes
        self.assertIn('boolean probeMode = "probe-apply".equals(mode);', self.code)

    def test_v3_does_not_weaken_any_v1_gate(self) -> None:
        v1 = V1.read_text(encoding="utf-8")
        carried = [
            "proposed body does not start at the entry point",
            "proposed body leaves .text",
            "proposal DROPS currently owned bytes: ",
            "proposal adds nothing",
            "target/target overlap at ",
            "NO FUNCTION AT ENTRY",
            "CURRENT STATE DRIFT: ",
            "READBACK STATE DRIFT: ",
            "terminator unreadable at ",
            "terminator bytes differ: ",
            "terminator not inside the proposed body",
            "malformed byteProof segment",
            "byteProof range unreadable at ",
            "byteProof does not reproduce at ",
            "byteProof ranges ",
            "proposal ENDS MID-INSTRUCTION inside ",
            "OVERLAPS existing function ",
            "setBody threw ",
            "in-process verify failed",
            "function census moved ",
            "manifest header drift",
            "duplicate address in manifest",
            "address not 0x-prefixed",
            "unparseable range text",
            "deltaBytes not numeric",
            "manifest sha256 ",
            "manifest bytes ",
            "row count ",
            "PRE function count ",
            "PRE instruction count ",
            "COHORT41_NO_MUTATION_PERFORMED",
        ]
        for message in carried:
            self.assertIn(message, v1, f"precondition: {message} in v1")
            self.assertIn(message, self.v3, f"v3 dropped the v1 gate {message!r}")


class Cohort41V3GateRefusalMatrixTests(unittest.TestCase):
    """Each NEW V3 gate must refuse its own violation on a real replica."""

    @classmethod
    def setUpClass(cls) -> None:
        path = os.environ.get("BEA_COHORT41_V3_GATE_MATRIX")
        if not path or not Path(path).is_file():
            raise unittest.SkipTest(
                "set BEA_COHORT41_V3_GATE_MATRIX to a gate-matrix-v3.json receipt"
            )
        cls.matrix = {
            entry["name"]: entry
            for entry in json.loads(Path(path).read_text(encoding="utf-8"))
        }

    def test_every_v3_gate_was_actually_provoked(self) -> None:
        missing = sorted(set(V3_REQUIRED_GATES) - set(self.matrix))
        self.assertFalse(missing, f"V3 gates never provoked: {missing}")

    def test_every_carried_over_gate_was_actually_provoked(self) -> None:
        missing = sorted(set(REQUIRED_GATES) - set(self.matrix))
        self.assertFalse(missing, f"carried-over gates never provoked: {missing}")

    def test_every_provoked_gate_refused_its_own_violation(self) -> None:
        for name, expected in {**REQUIRED_GATES, **CENSUS_GATES,
                               **V3_REQUIRED_GATES}.items():
            entry = self.matrix.get(name)
            if entry is None:
                continue
            with self.subTest(name):
                lines = entry["cohortLines"] + entry.get("receiptFailures", [])
                self.assertTrue(
                    any(expected in line for line in lines),
                    f"{name}: no line contained {expected!r}",
                )
                self.assertTrue(entry["refused"], name)

    def test_no_probe_ever_applied_a_row(self) -> None:
        for name, entry in self.matrix.items():
            with self.subTest(name):
                for line in entry["cohortLines"]:
                    self.assertNotIn("COHORT41_OK mode=apply", line)
                self.assertFalse(entry.get("applied"))

    def test_no_fault_probe_went_undetected(self) -> None:
        for name, entry in self.matrix.items():
            with self.subTest(name):
                for line in entry["cohortLines"]:
                    self.assertNotIn("COHORT41_FAULT_UNDETECTED", line)

    def test_every_mutating_refusal_rolled_back_to_the_pre_state(self) -> None:
        checked = 0
        for name, entry in self.matrix.items():
            if "rollbackLeftPreState" not in entry:
                continue
            checked += 1
            with self.subTest(name):
                self.assertTrue(
                    entry["rollbackLeftPreState"],
                    f"{name} refused but left the replica off its PRE state",
                )
        self.assertGreaterEqual(checked, 4, "no rollback evidence in the matrix")


class Cohort41ManifestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = rows()

    def test_manifest_identity_is_frozen(self) -> None:
        self.assertEqual(MANIFEST.stat().st_size, MANIFEST_BYTES)
        self.assertEqual(
            hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), MANIFEST_SHA256
        )
        self.assertEqual(len(self.rows), 41)
        self.assertEqual(len({r["addr"] for r in self.rows}), 41)

    def test_every_row_is_entry_anchored_growth_inside_text(self) -> None:
        seen: set[int] = set()
        for row in self.rows:
            entry = int(row["addr"], 16)
            current = to_set(row["currentRanges"])
            proposed = to_set(row["proposedRanges"])
            with self.subTest(row["addr"]):
                self.assertEqual(min(proposed), entry, "not entry-anchored")
                self.assertTrue(current <= proposed, "proposal drops owned bytes")
                self.assertTrue(proposed - current, "proposal adds nothing")
                self.assertGreaterEqual(min(proposed), TEXT_LO)
                self.assertLessEqual(max(proposed), TEXT_HI)
                self.assertEqual(
                    len(proposed) - len(current), int(row["deltaBytes"])
                )
                self.assertFalse(proposed & seen, "target/target overlap")
                seen |= proposed

    def test_byteproof_ranges_equal_added_ranges_and_terminator_is_inside(self) -> None:
        for row in self.rows:
            added = to_set(row["proposedRanges"]) - to_set(row["currentRanges"])
            proof: set[int] = set()
            for segment in row["byteProof"].split(" + "):
                span, _, _hexpart = segment.partition("=")
                lo, hi = (int(v, 16) for v in span.split("-"))
                proof.update(range(lo, hi + 1))
            tva = int(row["terminatorVa"], 16)
            tlen = len(row["terminatorBytes"]) // 2
            with self.subTest(row["addr"]):
                self.assertEqual(proof, added, "byteProof != added ranges")
                self.assertTrue(
                    set(range(tva, tva + tlen)) <= to_set(row["proposedRanges"]),
                    "terminator outside the proposed body",
                )

    @unittest.skipUnless(SPECIMEN.is_file(), "pristine specimen not materialised")
    def test_byteproof_and_terminator_reproduce_from_the_pristine_specimen(self) -> None:
        image = SPECIMEN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), SPECIMEN_SHA256)

        def at(va: int, n: int) -> bytes:
            return image[va - IMAGE_BASE: va - IMAGE_BASE + n]

        for row in self.rows:
            with self.subTest(row["addr"]):
                tva = int(row["terminatorVa"], 16)
                want = bytes.fromhex(row["terminatorBytes"])
                self.assertEqual(at(tva, len(want)), want, "terminator bytes")
                for segment in row["byteProof"].split(" + "):
                    span, _, hexpart = segment.partition("=")
                    lo, hi = (int(v, 16) for v in span.split("-"))
                    actual = at(lo, hi - lo + 1).hex()
                    if ".." in hexpart:
                        head, tail = hexpart.split("..")
                        self.assertTrue(actual.startswith(head))
                        self.assertTrue(actual.endswith(tail))
                    else:
                        self.assertTrue(actual.startswith(hexpart))


class Cohort41GateRefusalMatrixTests(unittest.TestCase):
    """Each gate must refuse ITS OWN violation - not merely exist in source."""

    @classmethod
    def setUpClass(cls) -> None:
        path = os.environ.get("BEA_COHORT41_GATE_MATRIX")
        if not path or not Path(path).is_file():
            raise unittest.SkipTest(
                "set BEA_COHORT41_GATE_MATRIX to a gate-matrix.json receipt"
            )
        cls.matrix = {
            entry["name"]: entry
            for entry in json.loads(Path(path).read_text(encoding="utf-8"))
        }

    def test_every_required_gate_was_actually_provoked(self) -> None:
        missing = sorted(set(REQUIRED_GATES) - set(self.matrix))
        self.assertFalse(missing, f"gates never provoked: {missing}")

    def test_every_provoked_gate_refused_its_own_violation(self) -> None:
        for name, expected in {**REQUIRED_GATES, **CENSUS_GATES}.items():
            entry = self.matrix.get(name)
            if entry is None:
                continue
            with self.subTest(name):
                # A gate may refuse on the console banner or in the `failures`
                # array of the emitted receipt; both are the applier speaking.
                lines = entry["cohortLines"] + entry.get("receiptFailures", [])
                self.assertTrue(
                    any(expected in line for line in lines),
                    f"{name}: no line contained {expected!r}; got {lines}",
                )
                self.assertTrue(entry["refused"], name)

    def test_no_probe_ever_applied_a_row(self) -> None:
        for name, entry in self.matrix.items():
            with self.subTest(name):
                for line in entry["cohortLines"]:
                    self.assertNotIn("COHORT41_OK mode=apply", line)
                    self.assertNotIn("mode=probe-apply rows=41", line)
                self.assertFalse(entry.get("applied"))

    def test_row_level_gates_report_no_mutation_performed(self) -> None:
        # Containment and argument gates return before the receipt stage, and a
        # -readOnly dry run cannot reach the mutation branch at all; every other
        # refusal has to state explicitly that nothing was mutated.
        early = {"g24-forbidden-project-path", "g25-not-in-rehearsal-scratch",
                 "g26-bad-mode", "g27-usage-arity", "g01-header-drift"}
        for name, entry in self.matrix.items():
            if name in early or entry.get("readOnlyRun"):
                continue
            with self.subTest(name):
                self.assertTrue(
                    entry.get("noMutation"),
                    f"{name} refused without COHORT41_NO_MUTATION_PERFORMED",
                )


if __name__ == "__main__":
    unittest.main()
