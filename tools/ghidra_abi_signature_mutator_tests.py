#!/usr/bin/env python3
r"""Derivation and safety tests for the 294-row ABI signature appliers.

Two Java appliers live in `tools/`:

  GhidraApplyAbiSignatures.java    the LIVE_FORBIDDEN rehearsal instrument.  It
                                   refuses any project path under Ghidra\\Projects
                                   and requires both the "abi-cohort" lane
                                   segment and the authoring session's scratch
                                   GUID.  It has no live mode and no flag that
                                   can give it one.  It stays this way forever.

  GhidraApplyAbiSignaturesV2.java  its live-capable twin, authored for the
                                   authorized 2026-08-17 promotion of the
                                   294-row ABI signature manifest.

V2's entire safety argument is that it is the rehearsal applier with ONE gate
inverted - containment - and every other gate, pin, verb, census and refusal
message carried over verbatim.  `V2_ALLOWLISTED_EDITS` below is that reviewed
difference, and it is a contract rather than documentation:

  * replaying the allowlist onto the rehearsal source must reproduce V2 byte
    for byte (forward proof), and
  * every line the two files differ on must be claimed by an allowlist entry
    (line-by-line proof), and
  * with comments stripped, the surviving code delta must be exactly the
    containment constants, the containment gate, the class name and the schema.

A relaxed pin, a dropped gate or a changed verb would appear as an unclaimed
differing line and would break the reconstruction digest, so it cannot be
smuggled in.  Every entry must be `banner`, `identity` or `containment`;
nothing else may ever be added.

REVERSIBILITY IS NOT CLAIMED HERE.  It was MEASURED in this Ghidra 12.1.2
headless build that `endTransaction(id, false)` does not revert
`Function.updateFunction`, that `Program.canUndo()` is false, and that headless
writes a new db version even when the script throws.  These tests therefore
assert the opposite of what a transaction-atomicity test would assert: that the
applier documents the no-rollback fact and that nothing in it claims an
in-process rollback for the mutating verb.  Reversibility for this cohort is a
ceremony-level property - an off-volume backup whose restore is byte-identical -
and is proven outside this file.

Run:  python -m unittest tools.ghidra_abi_signature_mutator_tests -v
"""
from __future__ import annotations

import difflib
import hashlib
import re
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

BASE = TOOLS / "GhidraApplyAbiSignatures.java"
V2 = TOOLS / "GhidraApplyAbiSignaturesV2.java"

# The manifest and the executed mutator matrix are authoring-session evidence
# that lives in the ignored scratch lane, not in the tracked tree: the manifest
# is 165 KB of per-row byte evidence for a cohort that is already applied and
# read back, and re-deriving it is what `reverse-engineering/` owns.  The tests
# that need them skip cleanly in a fresh clone rather than failing.
SCRATCH = Path(
    r"C:\Users\david\AppData\Local\Temp\claude"
    r"\C--Users-david-source-Onslaught-Career-Editor"
    r"\6174219b-0c29-4056-883b-580c862ff182\scratchpad\abi-cohort"
)
MANIFEST = SCRATCH / "out" / "abi-signature-manifest.tsv"
MUTANT_LOGS = SCRATCH / "mutant-logs"

# The rehearsal applier as authored in the scratch lane, CRLF, before the
# repository's `*.java text eol=lf` normalisation.  `BASE` must still round-trip
# to exactly these bytes: the tracked copy differs from the rehearsed one in
# line endings and in nothing else.
SCRATCH_ORIGINAL_CRLF_SHA256 = (
    "73778432c8fcd8cdf8971b85bc0f6510a9243e49e91ba8a4ca4e75484787c716"
)
BASE_SHA256 = "96941fc603ca2b060f509e004a49f0b538ba33e2f75213f7e5be5fe8946c9410"
V2_SHA256 = "7e08e1f7b777cadefd193b0017d0219a5c5882df7da2cc72ed2e8836fd27d479"

MANIFEST_SHA256 = (
    "d858563eb18f69837cb19236acde1771fc6d5847c2d75f8f7fc36728f0ea8d24"
)
MANIFEST_BYTES = 165137
MANIFEST_ROWS = 294
MANIFEST_COLUMNS = [
    "addr",
    "liveName",
    "currentSignatureLive",
    "currentSignatureSha256",
    "proposedSignature",
    "callingConvention",
    "returnTypeProposed",
    "paramSpec",
    "arity",
    "arityBytes",
    "retImmediate",
    "receiverInEcx",
    "returnUsage",
    "evidenceBytes",
    "confidence",
    "changeAxes",
    "frameCorroboration",
]

# The live maintainer project, lowercased, '/' folded to '\'.  V2 matches this
# by equals; nothing else can satisfy it.
REQUIRED_LIVE_PROJECT_DIR = r"c:\users\david\ghidra\projects\bea.rep"

# The PRE state of the live database this cohort is pinned against (db.18621).
PINNED_PRE_STATE = {
    "PRE_FUNCTIONS": 8329,
    "PRE_INSTRUCTIONS": 551232,
    "PRE_REFERENCES": 234493,
    "PRE_DEFINED_DATA": 48583,
    "PRE_UNDEFINED_DATA": 3907629,
    "PRE_BOOKMARKS": 2301,
}
PROGRAM_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# Measured from the manifest, and identical to the recorded GO recommendation.
# NO CALLING CONVENTION IS EVER RELABELLED, so this census must be invariant
# between the live signature and the proposed one.
CALLING_CONVENTION_CENSUS = {
    "__thiscall": 238,
    "__stdcall": 40,
    "__fastcall": 11,
    "__cdecl": 5,
}
CHANGE_AXIS_CENSUS = {"ARITY": 279, "RETURN": 8, "ARITY,RETURN": 7}
# Of the 286 rows that move arity, 190 remove a phantom stack parameter and
# 96 add a byte-proven one.
ARITY_DIRECTION_CENSUS = {"REMOVE": 190, "ADD": 96}
FRAME_CORROBORATION_CENSUS = {"EXACT": 157, "CONSISTENT_LOWER": 71, "n/a": 66}

# Hazard classes the recorded recommendation ruled NO-GO.  None may ever ride
# along in the manifest, and each is refused by a gate in the applier itself.
FORBIDDEN_MANIFEST_TOKENS = [
    # a hidden stack parameter Ghidra injects for an x87 ST0 return
    "__return_storage_ptr__",
    # no convention outside the four the applier allowlists
    "__vectorcall",
    # the frame comparator's contradiction verdict disqualifies a row outright
    "CONTRADICTS",
]

# The executed mutator matrix: every gate provoked with a deliberately broken
# input, and the refusal fragment that proves it refused for the RIGHT reason.
MUTATOR_MATRIX = {
    "T1a": "LIVE_FORBIDDEN",
    "T1b": "lacks the lane containment segment",
    "T1c": "lacks this session's scratch segment",
    "T2a": "program sha256 expected",
    "T2b": "program imageBase expected",
    "T3a": "state functions expected",
    "T3b": "state instructions expected",
    "T3c": "state references expected",
    "T3d": "state bookmarks expected",
    "T4a": "manifest sha256 expected",
    "T4b": "manifest sha256 expected",
    "T4c": "manifest rowCount expected",
    "T4d": "duplicate manifest address",
    "T4e": "is a no-op proposal",
    "T4f": "illegal calling convention",
    "T4g": "currentSignatureSha256 expected",
    "T4h": "arityBytes/arity mismatch",
    "T4i": "confidence expected",
    "T4j": "frame corroboration must never CONTRADICT",
    "T4k": "fabricate an EDX argument",
    "T4l": "stack param count expected",
    "T5a": "CURRENT signature expected",
    "T5b": "CURRENT signature expected",
    "T5c": "CURRENT name expected",
    "T6": "unknown data type",
    "T7a": "non-signature function state changed",
    "T7b": "NON-TARGET signature expected",
    "T7c": "collateral memory digest expected",
    "T7d": "POST signature expected",
}


# ---------------------------------------------------------------------------
# The complete reviewed difference between the rehearsal applier and V2.
V2_ALLOWLISTED_EDITS: list[tuple[str, str, str]] = [
    (
        "banner: the file header stops saying live-forbidden and states the "
        "authorization it runs under",
        "// LIVE_FORBIDDEN signature-only applier for the byte-derived ABI cohort.\n"
        "//\n",
        "// AUTHORIZED LIVE signature-only applier for the byte-derived ABI cohort.\n"
        "//\n"
        "// This is GhidraApplyAbiSignatures WITH EXACTLY ONE GATE INVERTED.  That\n"
        "// script is the rehearsal instrument and stays LIVE_FORBIDDEN forever; V2 is\n"
        "// its live-capable twin and differs from it only in the containment gate:\n"
        '// where the rehearsal applier requires an "abi-cohort" lane segment plus the\n'
        "// authoring session's scratch GUID and refuses any path under Ghidra\\Projects,\n"
        "// V2 REQUIRES the live maintainer project directory by exact match and refuses\n"
        "// everything else, including the tracked repository snapshot.  Every other\n"
        "// gate, pin, verb, census and refusal message is carried over verbatim, and\n"
        "// tools/ghidra_abi_signature_mutator_tests.py asserts that line by line.\n"
        "//\n"
        "// Use of this script is authorized ONLY for the 294-row cohort pinned below,\n"
        "// under the maintainer's delegated per-cohort grant of 2026-08-16 and the GO\n"
        "// recommendation recorded in developer_state as\n"
        "// _RECOMMENDATION_20260817_ABI_COHORT_LIVE_APPLY, which requires that NO\n"
        "// calling convention is ever relabelled and that the 642 no-go targets stay\n"
        "// dropped.  That grant is per-cohort and is NOT standing authorization for\n"
        "// Ghidra mutation.\n"
        "//\n",
    ),
    (
        "identity: Ghidra requires the class name to match the file name",
        "public class GhidraApplyAbiSignatures extends GhidraScript {\n",
        "public class GhidraApplyAbiSignaturesV2 extends GhidraScript {\n",
    ),
    (
        "identity: receipts and the live undo record must not claim to be "
        "rehearsal receipts",
        '    static final String SCHEMA = "bea.ghidra.abi-signature-correction.v1";\n',
        '    static final String SCHEMA = "bea.ghidra.abi-signature-correction.live.v2";\n',
    ),
    (
        "containment: the required-path constant replaces the lane and scratch "
        "segments, and the live project stops being a forbidden marker because "
        "it is now the requirement",
        '    static final String LANE_SEGMENT = "abi-cohort";\n'
        '    static final String SCRATCH_SEGMENT = "6174219b-0c29-4056-883b-580c862ff182";\n'
        r'    static final String[] LIVE_FORBIDDEN = {"ghidra\\projects", "ghidra/projects"};'
        "\n",
        "    // The one and only project this applier may ever open.  Exact match on\n"
        "    // the lowercased absolute project directory with '/' folded to '\\', so a\n"
        "    // scratch replica, a restored backup, a rehearsal copy or any other clone\n"
        "    // can never satisfy it.\n"
        "    static final String REQUIRED_LIVE_PROJECT_DIR =\n"
        r'        "c:\\users\\david\\ghidra\\projects\\bea.rep";'
        "\n"
        "    // The tracked repository snapshot stays forbidden and is still checked\n"
        "    // first, exactly as the rehearsal applier checked its forbidden markers.\n"
        "    static final String[] REPO_FORBIDDEN = {\n"
        r'        "onslaught-career-editor\\reverse-engineering",'
        "\n"
        '        "onslaught-career-editor/reverse-engineering"};'
        "\n",
    ),
    (
        "containment: the gate itself - contains() becomes equals(), which is "
        "the one and only inversion",
        "        for (String bad : LIVE_FORBIDDEN) {\n"
        "            require(!p.contains(bad.replace('/', '\\\\')),\n"
        '                "LIVE_FORBIDDEN - refusing a project path containing \'" + bad\n'
        '                + "\': " + raw);\n'
        "        }\n"
        "        require(p.contains(LANE_SEGMENT),\n"
        '            "project path lacks the lane containment segment \'" + LANE_SEGMENT\n'
        '            + "\': " + raw);\n'
        "        require(p.contains(SCRATCH_SEGMENT),\n"
        '            "project path lacks this session\'s scratch segment: " + raw);\n'
        '        println("ABISIG_GATE containment=ok path=" + raw);\n',
        "        for (String bad : REPO_FORBIDDEN) {\n"
        "            require(!p.contains(bad.replace('/', '\\\\')),\n"
        '                "REPO_FORBIDDEN - refusing a project path containing \'" + bad\n'
        '                + "\': " + raw);\n'
        "        }\n"
        "        require(p.equals(REQUIRED_LIVE_PROJECT_DIR),\n"
        '            "project is not the live maintainer project \'"\n'
        '            + REQUIRED_LIVE_PROJECT_DIR + "\': " + raw);\n'
        '        println("ABISIG_LIVE_TARGET"\n'
        '            + " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=294"\n'
        '            + " path=" + raw);\n'
        '        println("ABISIG_GATE containment=ok path=" + raw);\n',
    ),
]

ALLOWED_EDIT_CATEGORIES = ("banner:", "identity:", "containment:")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.split("\n")
        if line.strip() and not line.strip().startswith("//")
    ]


def _delta(a: list[str], b: list[str]) -> tuple[list[str], list[str]]:
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    removed: list[str] = []
    added: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        removed.extend(a[i1:i2])
        added.extend(b[j1:j2])
    return removed, added


def _top_level_param_count(signature: str) -> int:
    inner = signature[signature.index("(") + 1:signature.rindex(")")].strip()
    if not inner:
        return 0
    depth = 0
    n = 1
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            n += 1
    return n


class AbiSignatureDerivationTests(unittest.TestCase):
    """V2 is the rehearsal applier with exactly one gate inverted."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.v2 = V2.read_text(encoding="utf-8")

    # ------------------------------------------------------------ identity --

    def test_both_sources_are_frozen(self) -> None:
        self.assertEqual(_sha256(BASE), BASE_SHA256)
        self.assertEqual(_sha256(V2), V2_SHA256)

    def test_tracked_base_is_the_rehearsed_source_modulo_line_endings(self) -> None:
        """The tracked base differs from the rehearsed bytes in EOLs only."""
        crlf = BASE.read_bytes().replace(b"\n", b"\r\n")
        self.assertEqual(
            hashlib.sha256(crlf).hexdigest(),
            SCRATCH_ORIGINAL_CRLF_SHA256,
            "the tracked base is not the rehearsed applier with LF endings",
        )

    def test_base_remains_live_forbidden(self) -> None:
        """Authoring V2 must never have weakened the rehearsal instrument."""
        self.assertIn("LIVE_FORBIDDEN", self.base)
        self.assertIn('LANE_SEGMENT = "abi-cohort"', self.base)
        self.assertIn("SCRATCH_SEGMENT", self.base)
        self.assertNotIn("REQUIRED_LIVE_PROJECT_DIR", self.base)
        self.assertIn("p.contains(LANE_SEGMENT)", self.base)
        self.assertNotIn("p.equals(REQUIRED_LIVE_PROJECT_DIR)", self.base)

    def test_every_allowlist_entry_declares_a_permitted_category(self) -> None:
        for name, _old, _new in V2_ALLOWLISTED_EDITS:
            with self.subTest(name):
                self.assertTrue(
                    name.startswith(ALLOWED_EDIT_CATEGORIES),
                    f"edit category not permitted: {name!r}",
                )

    # ------------------------------------------- the equivalence proofs -----

    def test_applying_the_allowlist_to_the_base_reproduces_v2_exactly(self) -> None:
        """Forward proof: the reviewed edit list is the WHOLE difference."""
        derived = self.base
        for name, old, new in V2_ALLOWLISTED_EDITS:
            with self.subTest(name):
                self.assertEqual(
                    derived.count(old),
                    1,
                    f"{name}: old text is not unique in the base",
                )
                derived = derived.replace(old, new, 1)
        self.assertEqual(
            derived.encode("utf-8"),
            V2.read_bytes(),
            "V2 on disk contains an edit that is not on the reviewed allowlist",
        )
        self.assertEqual(
            hashlib.sha256(derived.encode("utf-8")).hexdigest(),
            V2_SHA256,
            "the reviewed allowlist no longer reproduces the pinned V2 digest",
        )

    def test_every_differing_line_is_claimed_by_an_allowlisted_edit(self) -> None:
        """Line-by-line proof: no line moved that the allowlist does not own."""
        claimed_old: set[str] = set()
        claimed_new: set[str] = set()
        for _name, old, new in V2_ALLOWLISTED_EDITS:
            claimed_old.update(l for l in old.split("\n") if l.strip())
            claimed_new.update(l for l in new.split("\n") if l.strip())

        removed, added = _delta(self.base.split("\n"), self.v2.split("\n"))
        removed = [l for l in removed if l.strip()]
        added = [l for l in added if l.strip()]

        self.assertTrue(removed and added, "V2 is identical to the base")
        for line in removed:
            self.assertIn(
                line, claimed_old, f"V2 removed an unreviewed base line: {line!r}"
            )
        for line in added:
            self.assertIn(line, claimed_new, f"V2 added an unreviewed line: {line!r}")

    def test_the_only_code_change_is_the_gate_the_schema_and_the_rename(self) -> None:
        """Comments cannot change behaviour; prove the CODE delta is tiny."""
        removed, added = _delta(_code_lines(self.base), _code_lines(self.v2))

        self.assertEqual(
            removed,
            [
                "public class GhidraApplyAbiSignatures extends GhidraScript {",
                'static final String SCHEMA = "bea.ghidra.abi-signature-correction.v1";',
                'static final String LANE_SEGMENT = "abi-cohort";',
                'static final String SCRATCH_SEGMENT = "6174219b-0c29-4056-883b-580c862ff182";',
                r'static final String[] LIVE_FORBIDDEN = {"ghidra\\projects", "ghidra/projects"};',
                "for (String bad : LIVE_FORBIDDEN) {",
                '"LIVE_FORBIDDEN - refusing a project path containing \'" + bad',
                "require(p.contains(LANE_SEGMENT),",
                "\"project path lacks the lane containment segment '\" + LANE_SEGMENT",
                "+ \"': \" + raw);",
                "require(p.contains(SCRATCH_SEGMENT),",
                '"project path lacks this session\'s scratch segment: " + raw);',
            ],
            "V2 removed a line of CODE that is not the gate, schema or rename",
        )
        self.assertEqual(
            added,
            [
                "public class GhidraApplyAbiSignaturesV2 extends GhidraScript {",
                'static final String SCHEMA = "bea.ghidra.abi-signature-correction.live.v2";',
                "static final String REQUIRED_LIVE_PROJECT_DIR =",
                r'"c:\\users\\david\\ghidra\\projects\\bea.rep";',
                "static final String[] REPO_FORBIDDEN = {",
                r'"onslaught-career-editor\\reverse-engineering",',
                '"onslaught-career-editor/reverse-engineering"};',
                "for (String bad : REPO_FORBIDDEN) {",
                '"REPO_FORBIDDEN - refusing a project path containing \'" + bad',
                "require(p.equals(REQUIRED_LIVE_PROJECT_DIR),",
                "\"project is not the live maintainer project '\"",
                "+ REQUIRED_LIVE_PROJECT_DIR + \"': \" + raw);",
                'println("ABISIG_LIVE_TARGET"',
                '+ " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=294"',
                '+ " path=" + raw);',
            ],
            "V2 added a line of CODE that is not the gate, schema or rename",
        )

    # ------------------------------------------------- the inverted gate ----

    def test_v2_requires_the_live_project_by_equals_not_contains(self) -> None:
        self.assertIn("require(p.equals(REQUIRED_LIVE_PROJECT_DIR),", self.v2)
        self.assertNotIn("p.contains(REQUIRED_LIVE_PROJECT_DIR)", self.v2)
        self.assertNotIn("LANE_SEGMENT", self.v2)
        self.assertNotIn("SCRATCH_SEGMENT", self.v2)

    def test_v2_pins_the_one_live_project_path(self) -> None:
        match = re.search(
            r'REQUIRED_LIVE_PROJECT_DIR\s*=\s*\n?\s*"([^"]+)"', self.v2
        )
        self.assertIsNotNone(match, "V2 has no REQUIRED_LIVE_PROJECT_DIR literal")
        assert match is not None
        # the Java literal is escaped; unescape to the real path
        self.assertEqual(
            match.group(1).replace("\\\\", "\\"), REQUIRED_LIVE_PROJECT_DIR
        )

    def test_v2_still_refuses_the_tracked_repository_snapshot(self) -> None:
        self.assertIn("REPO_FORBIDDEN", self.v2)
        self.assertIn("onslaught-career-editor", self.v2)
        # the repo refusal must run BEFORE the required-path check
        self.assertLess(
            self.v2.index("for (String bad : REPO_FORBIDDEN)"),
            self.v2.index("require(p.equals(REQUIRED_LIVE_PROJECT_DIR)"),
            "the repository refusal no longer runs first",
        )

    def test_v2_announces_that_it_is_hitting_the_live_project(self) -> None:
        self.assertIn("ABISIG_LIVE_TARGET", self.v2)
        self.assertNotIn("ABISIG_LIVE_TARGET", self.base)


class AbiSignatureGatesCarriedOverTests(unittest.TestCase):
    """Every gate that is not the containment gate is byte-identical in both."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.v2 = V2.read_text(encoding="utf-8")

    def _same(self, needle: str, minimum: int = 1) -> None:
        self.assertEqual(
            self.base.count(needle),
            self.v2.count(needle),
            f"the {needle!r} gate changed between the base and V2",
        )
        self.assertGreaterEqual(self.v2.count(needle), minimum)

    def test_no_pin_was_weakened(self) -> None:
        for const, value in PINNED_PRE_STATE.items():
            with self.subTest(const):
                literal = f"{const} = {value}L;"
                self.assertIn(literal, self.base)
                self.assertIn(literal, self.v2)
        for literal in (
            PROGRAM_SHA256,
            '"3b456964020070efe696d2cc09464a55"',
            '"x86:LE:32:default"',
            '"windows"',
            '"00400000"',
            "MANIFEST_ROWS = 294L;",
        ):
            with self.subTest(literal[:40]):
                self.assertIn(literal, self.base)
                self.assertIn(literal, self.v2)

    def test_the_manifest_integrity_gates_survive_verbatim(self) -> None:
        for needle in (
            'requireEqual("manifest", "sha256"',
            'requireEqual("manifest", "header"',
            'requireEqual("manifest", "rowCount"',
            "duplicate manifest address",
            "is a no-op proposal",
            "illegal calling convention",
            '"currentSignatureSha256"',
            "arityBytes/arity mismatch",
            '"confidence", "HIGH"',
            "frame corroboration must never CONTRADICT",
            '"stack param count"',
        ):
            with self.subTest(needle):
                self._same(needle)

    def test_the_hazard_class_gates_survive_verbatim(self) -> None:
        """The four fabrication hazards the reviewer's plan would have hit."""
        for needle in (
            # __fastcall + stack params would fabricate an EDX argument
            "fabricate an EDX argument",
            # a DEFAULT live signature is an absence; the row gate pins the
            # exact current prototype, so a DEFAULT one can never match
            '"CURRENT signature"',
            '"CURRENT calling convention"',
            # custom storage and thunks are refused rather than rewritten
            "uses custom variable storage",
            "is a thunk; a thunk's prototype follows its target",
            # no new type is ever defined, so no x87 shim can be invented
            "refuses to define new types",
        ):
            with self.subTest(needle):
                self._same(needle)

    def test_the_calling_convention_is_pinned_not_relabelled(self) -> None:
        """The convention is an INPUT gate on both sides, never a change."""
        # PRE: the live convention must already equal the manifest's
        self.assertIn('requireEqual(r.addrText, "CURRENT calling convention", r.cc,', self.v2)
        # POST: it must still equal it
        self.assertIn('requireEqual(r.addrText, "POST calling convention", r.cc,', self.v2)
        # and there is no setter for it anywhere
        self.assertNotIn("setCallingConvention(", self.v2)
        self.assertNotIn("setCallingConvention(", self.base)

    def test_type_resolution_is_lookup_only_and_runs_before_any_write(self) -> None:
        self._same("gateTypesResolvable")
        self._same("(lookup only, no new type defined)")
        for creator in ("new StructureDataType", "new TypedefDataType", "addDataType(",
                        "createStructure(", "resolve("):
            with self.subTest(creator):
                self.assertNotIn(creator, self.v2)
        # the gate must be invoked before the mutation loop
        self.assertLess(
            self.v2.index("gateTypesResolvable(rows);"),
            self.v2.index("int tx = currentProgram.startTransaction("),
            "type resolution no longer runs before the first write",
        )

    def test_every_non_mutating_gate_runs_before_the_first_write(self) -> None:
        """The no-rollback finding demands no gate can fail mid-cohort."""
        first_write = self.v2.index("int tx = currentProgram.startTransaction(")
        for gate in (
            "gateContainment();",
            "gateIdentity();",
            "gatePreCounts();",
            "gatePreRows(rows);",
            "gateTypesResolvable(rows);",
        ):
            with self.subTest(gate):
                self.assertLess(
                    self.v2.index(gate), first_write,
                    f"{gate} no longer runs before the first write",
                )

    def test_the_collateral_proof_gates_survive_verbatim(self) -> None:
        """Every non-target invariant checked after the write, carried over.

        These run over ALL 8,329 functions and ALL non-dynamic symbols, not
        just the 294 targets, and each was provoked by an executed mutant.
        """
        for needle in (
            'requireEqual("collateral", "changed function count"',
            'requireEqual("collateral", "untouched function count"',
            'requireEqual("collateral", "memory digest"',
            'requireEqual("collateral", "POST functions", PRE_FUNCTIONS',
            'requireEqual("collateral", "POST instructions", PRE_INSTRUCTIONS',
            'requireEqual("collateral", "POST references", PRE_REFERENCES',
            'requireEqual("collateral", "POST definedData", PRE_DEFINED_DATA',
            'requireEqual("collateral", "POST undefinedData", PRE_UNDEFINED_DATA',
            'requireEqual("collateral", "POST bookmarks", PRE_BOOKMARKS',
            '"the set of function entry points changed"',
            '"non-signature function state changed',
            '"NON-TARGET signature"',
            '"the non-dynamic symbol census changed',
            '"the bookmark census changed"',
            '"the defined-data census changed"',
            '"POST signature"',
            '"POST name"',
            '"POST stack parameter bytes"',
            '"POST varargs"',
            '"POST signature source"',
        ):
            with self.subTest(needle):
                self._same(needle)

    def test_updatefunction_is_the_only_authorized_verb(self) -> None:
        """No name, body, boundary, comment, tag, data or byte write."""
        forbidden_verbs = [
            "setName(",
            "setBody(",
            "clearListing(",
            "createFunction(",
            "removeFunction(",
            "setComment(",
            "setPlateComment(",
            "setRepeatableComment(",
            "addTag(",
            "removeTag(",
            "createData(",
            "createLabel(",
            "setBytes(",
            "disassemble(",
            "removeReference(",
            "addReference(",
            "setBookmark(",
            "removeBookmark(",
            "setCallingConvention(",
            "setCustomVariableStorage(",
        ]
        for verb in forbidden_verbs:
            with self.subTest(verb):
                self.assertNotIn(verb, self.v2, f"V2 can call {verb}")
                self.assertNotIn(verb, self.base)
        self.assertIn("updateFunction(", self.v2)
        # setVarArgs is in scope only to force varargs OFF, never on
        self.assertIn("f.setVarArgs(false);", self.v2)
        self.assertNotIn("setVarArgs(true)", self.v2)

    def test_the_no_rollback_finding_is_documented_and_not_contradicted(self) -> None:
        """This build has no working in-process rollback; say so, don't hide it."""
        for needle in (
            "endTransaction(id, false) does NOT revert",
            "Program.canUndo() is false",
            "An in-process rollback therefore CANNOT be the safety net",
            "gate can fail after the first write",
            "recovery is the ceremony backup restore",
        ):
            with self.subTest(needle):
                self._same(needle)
        # the mutating path must NOT claim an abort reverts the write
        self.assertIn(
            "commit = true;   // see the endTransaction note: abort is a no-op here",
            self.v2,
        )

    def test_the_transaction_count_is_unchanged(self) -> None:
        self.assertEqual(
            self.base.count("startTransaction("),
            self.v2.count("startTransaction("),
        )


class AbiSignatureManifestTests(unittest.TestCase):
    """The manifest V2 is authorized to apply, and only that manifest."""

    @classmethod
    def setUpClass(cls) -> None:
        if not MANIFEST.exists():
            raise unittest.SkipTest(f"authoring-lane manifest absent: {MANIFEST}")
        cls.raw = MANIFEST.read_bytes()
        cls.lines = cls.raw.decode("utf-8").rstrip("\n").split("\n")
        cls.rows = [l.split("\t") for l in cls.lines[1:]]
        cls.col = {n: i for i, n in enumerate(cls.lines[0].split("\t"))}

    def test_manifest_is_frozen(self) -> None:
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), MANIFEST_SHA256)
        self.assertEqual(len(self.raw), MANIFEST_BYTES)

    def test_manifest_shape(self) -> None:
        self.assertEqual(self.lines[0].split("\t"), MANIFEST_COLUMNS)
        self.assertEqual(len(self.rows), MANIFEST_ROWS)
        for row in self.rows:
            self.assertEqual(len(row), len(MANIFEST_COLUMNS))

    def test_no_calling_convention_is_ever_relabelled(self) -> None:
        """The one property that makes this cohort safe at all.

        The builder takes the convention straight from the live signature, so
        the declared convention must already appear in BOTH the current live
        prototype and the proposed one.  A relabel would show up here.
        """
        cc = self.col["callingConvention"]
        cur = self.col["currentSignatureLive"]
        new = self.col["proposedSignature"]
        for row in self.rows:
            with self.subTest(row[0]):
                self.assertIn(row[cc], row[cur], "convention absent from live")
                self.assertIn(row[cc], row[new], "convention absent from proposal")

    def test_the_calling_convention_census_matches_the_recommendation(self) -> None:
        seen: dict[str, int] = {}
        for row in self.rows:
            seen[row[self.col["callingConvention"]]] = (
                seen.get(row[self.col["callingConvention"]], 0) + 1
            )
        self.assertEqual(seen, CALLING_CONVENTION_CENSUS)

    def test_the_change_axis_census_matches_the_recommendation(self) -> None:
        seen: dict[str, int] = {}
        for row in self.rows:
            k = row[self.col["changeAxes"]]
            seen[k] = seen.get(k, 0) + 1
        self.assertEqual(seen, CHANGE_AXIS_CENSUS)

    def test_the_arity_direction_census_matches_the_recommendation(self) -> None:
        seen = {"ADD": 0, "REMOVE": 0}
        for row in self.rows:
            if "ARITY" not in row[self.col["changeAxes"]]:
                continue
            before = _top_level_param_count(row[self.col["currentSignatureLive"]])
            after = _top_level_param_count(row[self.col["proposedSignature"]])
            self.assertNotEqual(before, after, f"{row[0]} claims ARITY but does not move it")
            seen["ADD" if after > before else "REMOVE"] += 1
        self.assertEqual(seen, ARITY_DIRECTION_CENSUS)

    def test_the_frame_corroboration_census_never_contradicts(self) -> None:
        seen = {"EXACT": 0, "CONSISTENT_LOWER": 0, "n/a": 0}
        for row in self.rows:
            v = row[self.col["frameCorroboration"]]
            key = "CONSISTENT_LOWER" if v.startswith("CONSISTENT_LOWER") else v
            self.assertIn(key, seen, f"unexpected frame verdict {v!r} at {row[0]}")
            seen[key] += 1
        self.assertEqual(seen, FRAME_CORROBORATION_CENSUS)

    def test_every_row_is_high_confidence_and_a_real_change(self) -> None:
        for row in self.rows:
            with self.subTest(row[0]):
                self.assertEqual(row[self.col["confidence"]], "HIGH")
                self.assertNotEqual(
                    row[self.col["currentSignatureLive"]],
                    row[self.col["proposedSignature"]],
                    "no-op proposal",
                )

    def test_addresses_are_unique_and_well_formed(self) -> None:
        addrs = [row[0] for row in self.rows]
        self.assertEqual(len(set(addrs)), MANIFEST_ROWS, "duplicate address")
        for a in addrs:
            with self.subTest(a):
                self.assertRegex(a, r"^0x[0-9a-f]{8}$")

    def test_the_current_signature_self_hash_is_intact(self) -> None:
        for row in self.rows:
            with self.subTest(row[0]):
                self.assertEqual(
                    hashlib.sha256(
                        row[self.col["currentSignatureLive"]].encode("utf-8")
                    ).hexdigest(),
                    row[self.col["currentSignatureSha256"]],
                )

    def test_stack_param_spec_count_equals_arity(self) -> None:
        for row in self.rows:
            spec = row[self.col["paramSpec"]]
            nstack = sum(
                1 for p in spec.split(";") if p and p.split(":")[0] == "STACK"
            )
            with self.subTest(row[0]):
                self.assertEqual(nstack, int(row[self.col["arity"]]))
                self.assertEqual(
                    int(row[self.col["arityBytes"]]), int(row[self.col["arity"]]) * 4
                )

    def test_no_forbidden_hazard_token_appears_anywhere(self) -> None:
        text = self.raw.decode("utf-8")
        for token in FORBIDDEN_MANIFEST_TOKENS:
            with self.subTest(token):
                self.assertNotIn(token, text)

    def test_no_refuted_or_uncheckable_address_rides_along(self) -> None:
        """The 165 refuted and 44 uncheckable targets must stay dropped."""
        targets = {row[0] for row in self.rows}
        for name, expected_rows in (("REFUTED.tsv", 165), ("UNCHECKABLE.tsv", 44)):
            path = MANIFEST.parent / name
            if not path.exists():
                self.skipTest(f"authoring-lane evidence absent: {path}")
            lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
            addrs = {l.split("\t")[0] for l in lines[1:] if l.strip()}
            with self.subTest(name):
                self.assertEqual(len(addrs), expected_rows)
                self.assertEqual(
                    addrs & targets,
                    set(),
                    f"a {name} address is in the manifest",
                )

    def test_every_manifest_target_is_a_confirmed_verdict_with_no_reject_reason(
        self,
    ) -> None:
        """Nothing from any NO-GO class can be in the cohort by construction."""
        path = MANIFEST.parent / "cohort-verdict.tsv"
        if not path.exists():
            self.skipTest(f"authoring-lane evidence absent: {path}")
        lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
        col = {n: i for i, n in enumerate(lines[0].split("\t"))}
        by_addr: dict[str, list[str]] = {}
        for line in lines[1:]:
            if not line.strip():
                continue
            cells = line.split("\t")
            by_addr.setdefault(cells[0], cells)
        for row in self.rows:
            cells = by_addr.get(row[0])
            with self.subTest(row[0]):
                self.assertIsNotNone(cells, "target is not in the verdict ledger")
                assert cells is not None
                self.assertEqual(cells[col["verdict"]], "CONFIRMED")
                self.assertEqual(cells[col["rejectReason"]], "")


class AbiSignatureMutatorMatrixTests(unittest.TestCase):
    """Every gate was provoked by an executed mutant and refused."""

    @classmethod
    def setUpClass(cls) -> None:
        if not MUTANT_LOGS.is_dir():
            raise unittest.SkipTest(f"authoring-lane logs absent: {MUTANT_LOGS}")

    def test_the_matrix_has_every_probe(self) -> None:
        present = {p.stem for p in MUTANT_LOGS.glob("*.log")}
        self.assertEqual(
            present,
            set(MUTATOR_MATRIX),
            "the executed matrix does not match the declared one",
        )

    def test_every_probe_refused_with_its_own_message(self) -> None:
        for tid, fragment in MUTATOR_MATRIX.items():
            log = (MUTANT_LOGS / f"{tid}.log").read_text(
                encoding="utf-8", errors="replace"
            )
            with self.subTest(tid):
                self.assertIn("REFUSE:", log, f"{tid} did not refuse at all")
                self.assertIn(
                    fragment,
                    log,
                    f"{tid} refused, but not for its own reason",
                )

    def test_no_probe_ever_reached_a_passing_apply(self) -> None:
        for tid in MUTATOR_MATRIX:
            log = (MUTANT_LOGS / f"{tid}.log").read_text(
                encoding="utf-8", errors="replace"
            )
            with self.subTest(tid):
                self.assertNotIn("ABISIG_VERDICT mode=apply result=PASS", log)

    def test_the_containment_gate_itself_was_provoked(self) -> None:
        """A scratch copy placed under Ghidra\\Projects must still be refused."""
        log = (MUTANT_LOGS / "T1a.log").read_text(encoding="utf-8", errors="replace")
        self.assertIn("LIVE_FORBIDDEN - refusing a project path containing", log)

    def test_the_collateral_gates_were_provoked_by_real_mutants(self) -> None:
        """T7a-T7d actually wrote to a throwaway replica and were caught."""
        for tid in ("T7a", "T7b", "T7c", "T7d"):
            log = (MUTANT_LOGS / f"{tid}.log").read_text(
                encoding="utf-8", errors="replace"
            )
            with self.subTest(tid):
                self.assertIn("REFUSE:", log)
        # T7c must prove the byte write really happened before being caught
        t7c = (MUTANT_LOGS / "T7c.log").read_text(encoding="utf-8", errors="replace")
        self.assertIn("MUTPROBE flipped", t7c)
        self.assertIn("collateral memory digest expected", t7c)


if __name__ == "__main__":
    unittest.main()
