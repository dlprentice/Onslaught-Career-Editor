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

import difflib
import hashlib
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "tools/GhidraRehearseBoundaryCohort41.java"
V2 = ROOT / "tools/GhidraRehearseBoundaryCohort41V2.java"
V3 = ROOT / "tools/GhidraRehearseBoundaryCohort41V3.java"
V4 = ROOT / "tools/GhidraApplyBoundaryCohort41V4.java"
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
V4_SHA256 = "9934bf3d245cc068eca372186f820bf5a002c8163b605b295f92604d9fb8ef01"
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


# ---------------------------------------------------------------------------
# The complete reviewed difference between V3 and V4.
#
# V4 is the live-capable applier authored for the authorized 2026-08-16
# cohort-41 promotion.  Its entire safety argument is that it is V3 with ONE
# gate inverted - containment - so this list is the contract, not a convenience:
# `Cohort41V4LiveApplierTests` replays it onto V3 and requires the result to be
# V4 byte for byte, and separately requires every line the two files differ on
# to be claimed by an entry here.  Adding an edit to V4 without adding it here
# fails both tests.  Every entry must be `banner`, `identity`, `policy` or
# `containment`; nothing else may ever be added.
V4_ALLOWLISTED_EDITS: list[tuple[str, str, str]] = [
    (
        "banner: the file header stops saying rehearsal-only and states the "
        "authorization it runs under",
        "// SCRATCH-REPLICA REHEARSAL ONLY for a 41-row function-boundary cohort.\n"
        "//\n"
        "// This script is LIVE_FORBIDDEN by construction: it refuses to run unless the\n"
        "// open project's directory sits under a path segment named\n"
        '// "boundary-rehearsal", and it refuses outright if the path looks like the\n'
        "// maintainer project or the tracked repository snapshot.  It has no live mode\n"
        "// and no flag that can give it one.\n",
        "// AUTHORIZED LIVE APPLIER for a 41-row function-boundary cohort.\n"
        "//\n"
        "// This script is V3 WITH EXACTLY ONE GATE INVERTED.  V3 is the rehearsal\n"
        "// instrument and stays LIVE_FORBIDDEN forever; V4 is its live-capable twin and\n"
        "// differs from it only in Gate 1, containment: where V3 requires a\n"
        '// "boundary-rehearsal" path segment and refuses the maintainer project, V4\n'
        "// REQUIRES the live maintainer project directory by exact match and refuses\n"
        "// everything else, including the tracked repository snapshot.  Every other\n"
        "// gate, pin, verb, census, and refusal message is carried over verbatim and\n"
        "// tools/ghidra_boundary_cohort41_mutator_tests.py asserts that line by line.\n"
        "//\n"
        "// Use of this script is authorized ONLY for the 41-row cohort pinned below,\n"
        "// under the maintainer authorization recorded 2026-08-16 in developer_state\n"
        "// as _MAINTAINER_AUTHORIZATION_20260816_GHIDRA_BOUNDARY_COHORT41.  That grant\n"
        "// is per-cohort and is NOT standing authorization for Ghidra mutation.\n",
    ),
    (
        "banner: the retained V3 rationale is marked as inherited",
        "// WHY V3 EXISTS\n",
        "// WHY V3 EXISTS  (V4 INHERITS ALL OF IT UNCHANGED)\n",
    ),
    (
        "banner: the usage line names the script that actually exists",
        "//   -postScript GhidraRehearseBoundaryCohort41V3.java\n",
        "//   -postScript GhidraApplyBoundaryCohort41V4.java\n",
    ),
    (
        "identity: Ghidra requires the class name to match the file name",
        "public class GhidraRehearseBoundaryCohort41V3 extends GhidraScript {\n",
        "public class GhidraApplyBoundaryCohort41V4 extends GhidraScript {\n",
    ),
    (
        "identity: receipts must not claim to be rehearsal receipts",
        '    private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.rehearsal.v3";\n',
        '    private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.apply.v4";\n',
    ),
    (
        "identity: the live undo record must not name the LIVE_FORBIDDEN script",
        '        int tx = currentProgram.startTransaction("cohort41-v3-" + mode);\n',
        '        int tx = currentProgram.startTransaction("cohort41-v4-" + mode);\n',
    ),
    (
        "policy: the declared policy constant, echoed into every receipt",
        '    private static final String POLICY = "LIVE_FORBIDDEN";\n',
        '    private static final String POLICY = "LIVE_AUTHORIZED_COHORT41";\n',
    ),
    (
        "containment: the required-path constant, and the live project stops "
        "being a forbidden marker because it is now the requirement",
        '    private static final String CONTAINMENT_SEGMENT = "boundary-rehearsal";\n'
        "    private static final String[] FORBIDDEN_PATH_MARKERS = {\n"
        r'        "ghidra\\projects", "ghidra/projects",' "\n"
        r'        "onslaught-career-editor\\reverse-engineering",' "\n"
        '        "onslaught-career-editor/reverse-engineering",\n'
        "    };\n",
        "    // The one and only project this applier may ever open.  Exact match on the\n"
        "    // lowercased absolute project directory: a scratch replica, a restored\n"
        "    // backup, a rehearsal copy, or any other clone can never satisfy it.\n"
        "    private static final String REQUIRED_LIVE_PROJECT_DIR =\n"
        r'        "c:\\users\\david\\ghidra\\projects\\bea.rep";' "\n"
        "    private static final String[] FORBIDDEN_PATH_MARKERS = {\n"
        r'        "onslaught-career-editor\\reverse-engineering",' "\n"
        '        "onslaught-career-editor/reverse-engineering",\n'
        "    };\n",
    ),
    (
        "containment: the gate's own comment",
        "        // ---- Gate 1: containment.  Never the live project, never the repo. ----\n",
        "        // ---- Gate 1: containment.  ONLY the live project, never the repo. ----\n",
    ),
    (
        "containment: THE GATE - require the live project by exact match, refuse "
        "everything else, and announce the live target",
        "        if (!lower.contains(CONTAINMENT_SEGMENT)) {\n"
        '            println("COHORT41_REFUSE reason=project_not_in_rehearsal_scratch path="\n'
        "                + projectPath);\n"
        "            return;\n"
        "        }\n",
        "        if (!lower.equals(REQUIRED_LIVE_PROJECT_DIR)) {\n"
        '            println("COHORT41_REFUSE reason=project_is_not_the_live_maintainer_project"\n'
        '                + " path=" + projectPath);\n'
        "            return;\n"
        "        }\n"
        '        println("COHORT41_LIVE_TARGET banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT"\n'
        '            + " policy=" + POLICY + " cohort=41 path=" + projectPath);\n',
    ),
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


class Cohort41V4LiveApplierTests(unittest.TestCase):
    """V4 is V3 with exactly one gate inverted - asserted line by line.

    V3 is the rehearsal instrument and must stay LIVE_FORBIDDEN forever.  V4 is
    the live-capable twin authored for the authorized 2026-08-16 cohort-41
    promotion.  The whole safety argument for running V4 against the maintainer
    database is that it carries every V3 gate verbatim, so this class proves
    that mechanically rather than by reading.

    `V4_ALLOWLISTED_EDITS` is the complete, reviewed edit list.  Applying it to
    V3 must reproduce V4 byte for byte (forward proof), and every line the two
    files differ on must be claimed by one of its entries (line-by-line proof).
    Any unreviewed edit - a relaxed pin, a dropped gate, a changed verb - fails
    both tests, because it would appear as an unclaimed differing line and it
    would break the reconstruction digest.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.v3 = V3.read_text(encoding="utf-8")
        cls.v4 = V4.read_text(encoding="utf-8")

    # ------------------------------------------------------------ identity --

    def test_v4_source_is_frozen(self) -> None:
        self.assertEqual(hashlib.sha256(V4.read_bytes()).hexdigest(), V4_SHA256)

    def test_v3_remains_the_unmodified_live_forbidden_rehearsal_instrument(self) -> None:
        # Authoring V4 must never have touched V3.
        self.assertEqual(hashlib.sha256(V3.read_bytes()).hexdigest(), V3_SHA256)
        self.assertIn('POLICY = "LIVE_FORBIDDEN"', self.v3)
        self.assertIn('CONTAINMENT_SEGMENT = "boundary-rehearsal"', self.v3)
        self.assertNotIn("REQUIRED_LIVE_PROJECT_DIR", self.v3)

    # -------------------------------------------- the two equivalence proofs --

    def test_applying_the_allowlisted_edits_to_v3_reproduces_v4_exactly(self) -> None:
        """Forward proof: the reviewed edit list is the WHOLE difference."""
        derived = self.v3
        for name, old, new in V4_ALLOWLISTED_EDITS:
            with self.subTest(name):
                self.assertEqual(
                    derived.count(old), 1, f"{name}: old text is not unique in V3"
                )
                derived = derived.replace(old, new, 1)
        self.assertEqual(
            derived.encode("utf-8"),
            V4.read_bytes(),
            "V4 on disk contains an edit that is not on the reviewed allowlist",
        )
        self.assertEqual(
            hashlib.sha256(derived.encode("utf-8")).hexdigest(),
            V4_SHA256,
            "the reviewed allowlist no longer reproduces the pinned V4 digest",
        )

    def test_every_differing_line_is_claimed_by_an_allowlisted_edit(self) -> None:
        """Line-by-line proof: no line moved that the allowlist does not own."""
        claimed_old: set[str] = set()
        claimed_new: set[str] = set()
        for _name, old, new in V4_ALLOWLISTED_EDITS:
            claimed_old.update(l for l in old.split("\n") if l.strip())
            claimed_new.update(l for l in new.split("\n") if l.strip())

        a = self.v3.split("\n")
        b = self.v4.split("\n")
        matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        removed: list[str] = []
        added: list[str] = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            removed.extend(l for l in a[i1:i2] if l.strip())
            added.extend(l for l in b[j1:j2] if l.strip())

        self.assertTrue(removed and added, "V4 is identical to V3")
        for line in removed:
            self.assertIn(
                line, claimed_old, f"V4 removed an unreviewed V3 line: {line!r}"
            )
        for line in added:
            self.assertIn(
                line, claimed_new, f"V4 added an unreviewed line: {line!r}"
            )

    def test_the_only_code_change_is_the_gate_the_policy_and_the_rename(self) -> None:
        """Comments cannot change behaviour; prove the CODE delta is tiny."""

        def code(text: str) -> list[str]:
            return [
                l.strip()
                for l in text.split("\n")
                if l.strip() and not l.strip().startswith("//")
            ]

        a, b = code(self.v3), code(self.v4)
        matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        removed: list[str] = []
        added: list[str] = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            removed.extend(a[i1:i2])
            added.extend(b[j1:j2])

        self.assertEqual(
            removed,
            [
                "public class GhidraRehearseBoundaryCohort41V3 extends GhidraScript {",
                'private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.rehearsal.v3";',
                'private static final String POLICY = "LIVE_FORBIDDEN";',
                'private static final String CONTAINMENT_SEGMENT = "boundary-rehearsal";',
                r'"ghidra\\projects", "ghidra/projects",',
                "if (!lower.contains(CONTAINMENT_SEGMENT)) {",
                'println("COHORT41_REFUSE reason=project_not_in_rehearsal_scratch path="',
                "+ projectPath);",
                'int tx = currentProgram.startTransaction("cohort41-v3-" + mode);',
            ],
        )
        self.assertEqual(
            added,
            [
                "public class GhidraApplyBoundaryCohort41V4 extends GhidraScript {",
                'private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.apply.v4";',
                'private static final String POLICY = "LIVE_AUTHORIZED_COHORT41";',
                "private static final String REQUIRED_LIVE_PROJECT_DIR =",
                r'"c:\\users\\david\\ghidra\\projects\\bea.rep";',
                "if (!lower.equals(REQUIRED_LIVE_PROJECT_DIR)) {",
                'println("COHORT41_REFUSE reason=project_is_not_the_live_maintainer_project"',
                '+ " path=" + projectPath);',
                'println("COHORT41_LIVE_TARGET banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT"',
                '+ " policy=" + POLICY + " cohort=41 path=" + projectPath);',
                'int tx = currentProgram.startTransaction("cohort41-v4-" + mode);',
            ],
        )

    # ---------------------------------------------- what the new gate means --

    def test_v4_requires_the_live_project_by_exact_match(self) -> None:
        self.assertIn(
            'REQUIRED_LIVE_PROJECT_DIR =\n        "c:\\\\users\\\\david\\\\ghidra'
            '\\\\projects\\\\bea.rep";',
            self.v4,
        )
        # Exact equality, not containment: no scratch replica, restored backup or
        # rehearsal clone whose path merely CONTAINS the live path can satisfy it.
        self.assertIn("if (!lower.equals(REQUIRED_LIVE_PROJECT_DIR)) {", self.v4)
        self.assertNotIn("lower.contains(REQUIRED_LIVE_PROJECT_DIR)", self.v4)
        self.assertNotIn("CONTAINMENT_SEGMENT", self.v4)
        # and it is compared against the real, absolute project directory
        self.assertIn("state.getProject().getProjectLocator().getProjectDir()", self.v4)
        self.assertIn("lower = projectPath.toLowerCase(Locale.ROOT)", self.v4)

    def test_v4_still_refuses_the_tracked_repository_snapshot(self) -> None:
        for marker in (
            '"onslaught-career-editor\\\\reverse-engineering"',
            '"onslaught-career-editor/reverse-engineering"',
        ):
            self.assertIn(marker, self.v4, marker)
        self.assertIn("COHORT41_REFUSE reason=forbidden_project_path", self.v4)
        # the repo refusal loop is carried over verbatim and still runs FIRST
        self.assertLess(
            self.v4.index("FORBIDDEN_PATH_MARKERS)"),
            self.v4.index("if (!lower.equals(REQUIRED_LIVE_PROJECT_DIR))"),
        )

    # ------------------------------------- every other gate carries verbatim --

    def test_v4_carries_every_pin_and_census_value_verbatim(self) -> None:
        for pinned in (
            'PROGRAM_NAME = "BEA.exe"',
            'PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"',
            f'"{SPECIMEN_SHA256}"',
            'IMAGE_BASE = "00400000"',
            'LANGUAGE = "x86:LE:32:default"',
            'COMPILER_SPEC = "windows"',
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
            "TARGET_COUNT = 41",
            f"MANIFEST_BYTES = {MANIFEST_BYTES}L",
            f'MANIFEST_SHA256 =\n        "{MANIFEST_SHA256}"',
            "MAX_RESYNC = 16",
        ):
            self.assertIn(pinned, self.v4, pinned)

    def test_v4_authorizes_no_verb_v3_did_not(self) -> None:
        def code(text: str) -> str:
            return "\n".join(
                l for l in text.split("\n") if not l.lstrip().startswith("//")
            )

        v3c, v4c = code(self.v3), code(self.v4)
        for verb in (
            ".setBody(",
            "clearCodeUnits(",
            "removeBookmark(",
            "disassemble(",
            "startTransaction(",
            "endTransaction(",
        ):
            self.assertEqual(v4c.count(verb), v3c.count(verb), verb)
        # nothing new that could write names, bytes, types or references
        for forbidden in (
            ".setName(",
            ".setComment(",
            "createFunction(",
            "removeFunction(",
            "setBytes(",
            "createData(",
            "addExternalReference(",
            "setPrimary(",
        ):
            self.assertNotIn(forbidden, v4c, forbidden)

    def test_v4_carries_every_v3_string_literal_verbatim(self) -> None:
        """Strongest carry-over proof: derived from V3, not from a hand list.

        Every gate message, sentinel, pin and format fragment in V3 is a string
        literal.  All of them must survive into V4 except the seven the
        allowlist deliberately rewrites.  A silently weakened or deleted gate
        loses its literal and fails here.
        """
        import re

        def literals(text: str) -> set[str]:
            code = "\n".join(
                l for l in text.split("\n") if not l.lstrip().startswith("//")
            )
            return set(re.findall(r'"(?:[^"\\]|\\.)*"', code))

        v3_lit, v4_lit = literals(self.v3), literals(self.v4)
        deliberately_replaced = {
            '"bea.ghidra.boundary-cohort-41.rehearsal.v3"',
            '"LIVE_FORBIDDEN"',
            '"boundary-rehearsal"',
            r'"ghidra\\projects"',
            '"ghidra/projects"',
            '"COHORT41_REFUSE reason=project_not_in_rehearsal_scratch path="',
            '"cohort41-v3-"',
        }
        self.assertEqual(
            v3_lit - v4_lit,
            deliberately_replaced,
            "V4 dropped a V3 string literal that is not on the allowlist",
        )
        self.assertEqual(
            v4_lit - v3_lit,
            {
                '"bea.ghidra.boundary-cohort-41.apply.v4"',
                '"LIVE_AUTHORIZED_COHORT41"',
                r'"c:\\users\\david\\ghidra\\projects\\bea.rep"',
                '"COHORT41_REFUSE reason=project_is_not_the_live_maintainer_project"',
                # note: '" path="' is NOT new - V3's forbidden-path refusal
                # already uses it, and V4's new refusal reuses it verbatim.
                '"COHORT41_LIVE_TARGET banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT"',
                '" policy="',
                '" cohort=41 path="',
                '"cohort41-v4-"',
            },
            "V4 introduced a string literal that is not on the allowlist",
        )

    def test_v4_carries_every_v3_refusal_message_verbatim(self) -> None:
        """Every gate message except the one that was deliberately inverted."""
        inverted = "COHORT41_REFUSE reason=project_not_in_rehearsal_scratch"
        for sentinel in (
            "COHORT41_NO_MUTATION_PERFORMED",
            "COHORT41_TRANSACTION_ABORTED",
            "COHORT41_GATE_FAIL",
            "UNCLASSIFIED BYTES REMAIN in the admitted body",
            "CLASSIFIED-BYTE REGRESSION",
            "CLEAR ESCAPED the admitted range at",
            "JUMP/SEH TABLE ROW WAS CLEARED",
            "JUMP/SEH TABLE DATA CHANGED",
            "PRECONDITION ROW WAS MUTATED",
            "INSTRUCTION ESCAPED the proposed body at",
            "INSTRUCTION ESCAPE: program delta ",
            "REFERENCE ESCAPE: program delta ",
            "CLEAR PLAN MISMATCH derived=",
            "STALE BOOKMARK OUTSIDE the admitted ranges at",
            "STALE BOOKMARK at an unclassified byte",
            "PINNED STALE BOOKMARK ABSENT at",
            "BOOKMARK CREATED OUTSIDE the admitted ranges at",
            "BOOKMARK REMOVED OUTSIDE the admitted ranges at",
            "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION",
        ):
            self.assertIn(sentinel, self.v4, sentinel)
        self.assertNotIn(inverted, self.v4)

    def test_v4_gates_still_run_before_setbody_and_abort_on_failure(self) -> None:
        self.assertIn("if (settingBodies && failures.isEmpty()) {", self.v4)
        self.assertIn(
            "commit = failures.isEmpty() && !planOnly && !faultMode;", self.v4
        )
        self.assertIn("currentProgram.endTransaction(tx, commit);", self.v4)
        # the mutating path still refuses before it opens the transaction
        self.assertLess(
            self.v4.index("COHORT41_REFUSE reason=gate_failure"),
            self.v4.index('startTransaction("cohort41-v4-"'),
        )

    def test_v4_clear_plan_and_stale_bookmark_pins_are_identical_to_v3(self) -> None:
        def block(text: str, start: str, end: str) -> str:
            i = text.index(start)
            return text[i : text.index(end, i)]

        for start, end in (
            ("private static final String[] CLEAR_PLAN", "};"),
            ("private static final String[] STALE_BOOKMARKS", "};"),
        ):
            self.assertEqual(
                block(self.v3, start, end), block(self.v4, start, end), start
            )

    def test_the_allowlist_admits_only_four_kinds_of_change(self) -> None:
        """No future edit may smuggle a fifth category into the allowlist."""
        allowed = {"banner", "identity", "policy", "containment"}
        seen = set()
        for name, old, new in V4_ALLOWLISTED_EDITS:
            category = name.split(":", 1)[0].strip()
            with self.subTest(name):
                self.assertIn(category, allowed, f"unreviewed category: {name!r}")
                self.assertNotEqual(old, new, "no-op allowlist entry")
            seen.add(category)
        self.assertEqual(seen, allowed, "an allowlist category went unused")
        # exactly one entry may touch the gate's control flow
        gate = [e for e in V4_ALLOWLISTED_EDITS if "THE GATE" in e[0]]
        self.assertEqual(len(gate), 1)


if __name__ == "__main__":
    unittest.main()
