#!/usr/bin/env python3
"""Derivation and safety tests for the 160-row name-cohort appliers.

Two Java appliers live in `tools/`:

  GhidraApplyNameCohort160.java    the LIVE_FORBIDDEN rehearsal instrument.  It
                                   refuses any project path under Ghidra\\Projects
                                   and requires both the "name-cohort" lane
                                   segment and the authoring session's scratch
                                   GUID.  It has no live mode and no flag that
                                   can give it one.  It stays this way forever.

  GhidraApplyNameCohort160V2.java  its live-capable twin, authored for the
                                   authorized 2026-08-17 promotion of the
                                   160-row name manifest.

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

Run:  python -m unittest tools.ghidra_name_cohort160_mutator_tests -v
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

BASE = TOOLS / "GhidraApplyNameCohort160.java"
V2 = TOOLS / "GhidraApplyNameCohort160V2.java"
MANIFEST = (
    REPO
    / "reverse-engineering"
    / "binary-analysis"
    / "name-cohort-promotion-manifest-2026-08-17.tsv"
)

# The rehearsal applier as authored in the scratch lane, CRLF, before the
# repository's `*.java text eol=lf` normalisation.  `BASE` must still round-trip
# to exactly these bytes: the tracked copy differs from the rehearsed one in
# line endings and in nothing else.
SCRATCH_ORIGINAL_CRLF_SHA256 = (
    "1a10a87839a470a0d9226e2da2a6ea04b829ecae069a1e02d97ef598a53d1de1"
)
BASE_SHA256 = "2e757f92fe7b0f6f1427159fa1b6966fdcd766dbfd491637922f452c4794a422"
V2_SHA256 = "a111399bcf4e5e0271c93cff566646d4a1b716f753a0796ffe56b4cd92527831"

MANIFEST_SHA256 = (
    "00362b034a124c27ff23ba1ff0501b8009a486ba729ca33db11427fe3631f214"
)
MANIFEST_ROWS = 160
MANIFEST_COLUMNS = [
    "addr",
    "provenance",
    "liveKind",
    "currentNameLive",
    "proposedName",
    "tier",
    "anchorKind",
    "anchorEvidence",
    "reason",
]

# The live maintainer project, lowercased, '/' folded to '\'.  V2 matches this
# by equals; nothing else can satisfy it.
REQUIRED_LIVE_PROJECT_DIR = r"c:\users\david\ghidra\projects\bea.rep"

# Rows the recorded GO recommendation explicitly dropped.  They were measured
# false or unusable and must never appear in the manifest.
REFUTED_ADDRESSES_THAT_MUST_NOT_SHIP = [
    "0x0044ca30",  # CExplosion__Init: claimed slot 108 runs past a 68-entry vtable
    "0x004dfa40",  # right ordinal, but the holder is CSimpleBuilding, not CUnit
    "0x004f07e0",  # valid but order-dependent; needs 0x004f0760 to land first
    "0x00409ef0",  # proposes the literal placeholder "<await body reading>"
    "0x00409f20",  # same
]

# The PRE state of the live database this cohort is pinned against (db.18620).
PINNED_PRE_STATE = {
    "PRE_FUNCTIONS": 8329,
    "PRE_INSTRUCTIONS": 551232,
    "PRE_REFERENCES": 234493,
    "PRE_DEFINED_DATA": 48583,
    "PRE_UNDEFINED_DATA": 3907629,
    "PRE_BOOKMARKS": 2301,
}
PINNED_DIGESTS = {
    "PRE_FUNCTION_NAME_DIGEST": (
        "1ea6683b48d7086ed4a214bbb74357d7ff964ebdc2c995f8a9d414626822b9c1"
    ),
    "PRE_FUNCTION_BODY_DIGEST": (
        "c066b5d6093342c507b816f9823680cbef032f74ae12ec95697ccbca789a187f"
    ),
}
PROGRAM_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)


# ---------------------------------------------------------------------------
# The complete reviewed difference between the rehearsal applier and V2.
V2_ALLOWLISTED_EDITS: list[tuple[str, str, str]] = [
    (
        "banner: the file header stops saying live-forbidden and states the "
        "authorization it runs under",
        "// LIVE_FORBIDDEN name-only applier for the re-pinned 160-row name cohort.\n"
        "//\n",
        "// AUTHORIZED LIVE name-only applier for the re-pinned 160-row name cohort.\n"
        "//\n"
        "// This is GhidraApplyNameCohort160 WITH EXACTLY ONE GATE INVERTED.  That\n"
        "// script is the rehearsal instrument and stays LIVE_FORBIDDEN forever; V2 is\n"
        "// its live-capable twin and differs from it only in the containment gate:\n"
        '// where the rehearsal applier requires a "name-cohort" lane segment plus the\n'
        "// authoring session's scratch GUID and refuses any path under Ghidra\\Projects,\n"
        "// V2 REQUIRES the live maintainer project directory by exact match and refuses\n"
        "// everything else, including the tracked repository snapshot.  Every other\n"
        "// gate, pin, verb, census and refusal message is carried over verbatim, and\n"
        "// tools/ghidra_name_cohort160_mutator_tests.py asserts that line by line.\n"
        "//\n"
        "// Use of this script is authorized ONLY for the 160-row cohort pinned below,\n"
        "// under the maintainer's delegated per-cohort grant of 2026-08-16 and the GO\n"
        "// recommendation recorded in developer_state as\n"
        "// _RECOMMENDATION_20260817_NAME_COHORT_LIVE_APPLY, which requires the five\n"
        "// refuted rows to stay dropped.  That grant is per-cohort and is NOT standing\n"
        "// authorization for Ghidra mutation.\n"
        "//\n",
    ),
    (
        "identity: Ghidra requires the class name to match the file name",
        "public class GhidraApplyNameCohort160 extends GhidraScript {\n",
        "public class GhidraApplyNameCohort160V2 extends GhidraScript {\n",
    ),
    (
        "identity: receipts and the live undo record must not claim to be "
        "rehearsal receipts",
        '    static final String SCHEMA = "bea.ghidra.name-cohort-repin.v1";\n',
        '    static final String SCHEMA = "bea.ghidra.name-cohort-repin.live.v2";\n',
    ),
    (
        "containment: the required-path constant replaces the lane and scratch "
        "segments, and the live project stops being a forbidden marker because "
        "it is now the requirement",
        '    static final String LANE_SEGMENT = "name-cohort";\n'
        "    static final String SCRATCH_SEGMENT =\n"
        '        "6174219b-0c29-4056-883b-580c862ff182";\n'
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
        "        println(\"NAMECOHORT_GATE containment=ok path=\" + raw);\n",
        "        for (String bad : REPO_FORBIDDEN) {\n"
        "            require(!p.contains(bad.replace('/', '\\\\')),\n"
        '                "REPO_FORBIDDEN - refusing a project path containing \'" + bad\n'
        '                + "\': " + raw);\n'
        "        }\n"
        "        require(p.equals(REQUIRED_LIVE_PROJECT_DIR),\n"
        '            "project is not the live maintainer project \'"\n'
        '            + REQUIRED_LIVE_PROJECT_DIR + "\': " + raw);\n'
        "        println(\"NAMECOHORT_LIVE_TARGET\"\n"
        '            + " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=160"\n'
        '            + " path=" + raw);\n'
        "        println(\"NAMECOHORT_GATE containment=ok path=\" + raw);\n",
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


class NameCohort160DerivationTests(unittest.TestCase):
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
        self.assertIn('LANE_SEGMENT = "name-cohort"', self.base)
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
                "public class GhidraApplyNameCohort160 extends GhidraScript {",
                'static final String SCHEMA = "bea.ghidra.name-cohort-repin.v1";',
                'static final String LANE_SEGMENT = "name-cohort";',
                "static final String SCRATCH_SEGMENT =",
                '"6174219b-0c29-4056-883b-580c862ff182";',
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
                "public class GhidraApplyNameCohort160V2 extends GhidraScript {",
                'static final String SCHEMA = "bea.ghidra.name-cohort-repin.live.v2";',
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
                'println("NAMECOHORT_LIVE_TARGET"',
                '+ " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=160"',
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
        self.assertEqual(match.group(1).replace("\\\\", "\\"), REQUIRED_LIVE_PROJECT_DIR)

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
        self.assertIn("NAMECOHORT_LIVE_TARGET", self.v2)
        self.assertNotIn("NAMECOHORT_LIVE_TARGET", self.base)

    # --------------------------------------------------- gates carried over --

    def test_no_pin_was_weakened(self) -> None:
        """Every identity, census and digest pin is byte-identical in both."""
        for const, value in PINNED_PRE_STATE.items():
            with self.subTest(const):
                literal = f"{const} = {value}L;"
                self.assertIn(literal, self.base)
                self.assertIn(literal, self.v2)
        for const, value in PINNED_DIGESTS.items():
            with self.subTest(const):
                self.assertIn(value, self.base)
                self.assertIn(value, self.v2)
        for literal in (
            PROGRAM_SHA256,
            '"3b456964020070efe696d2cc09464a55"',
            '"x86:LE:32:default"',
            '"00400000"',
            "MANIFEST_ROWS = 160L;",
        ):
            with self.subTest(literal[:40]):
                self.assertIn(literal, self.base)
                self.assertIn(literal, self.v2)

    def test_the_absolute_no_collision_gate_survives_verbatim(self) -> None:
        for needle in (
            "collision: proposed name",
            "duplicate proposed name",
            "duplicate manifest address",
            "duplicate current name",
            "rename cycle",
        ):
            with self.subTest(needle):
                self.assertEqual(
                    self.base.count(needle),
                    self.v2.count(needle),
                    f"the {needle!r} gate changed between the base and V2",
                )
                self.assertGreaterEqual(self.v2.count(needle), 1)

    def test_the_collateral_proof_gates_survive_verbatim(self) -> None:
        """Every non-target invariant checked after the rename, carried over.

        These are the checks that make the apply provable rather than hopeful:
        they run over ALL functions and ALL non-dynamic symbols, not just the
        160 targets, and each was provoked by an executed mutant probe.
        """
        for needle in (
            'requireEqual("collateral", "changed function names"',
            'requireEqual("collateral", "symbols added"',
            'requireEqual("collateral", "symbols removed"',
            'requireEqual("collateral", "non-dynamic symbol count"',
            'requireEqual("collateral", "functions", PRE_FUNCTIONS',
            'requireEqual("collateral", "instructions", PRE_INSTRUCTIONS',
            'requireEqual("collateral", "references", PRE_REFERENCES',
            'requireEqual("collateral", "definedData", PRE_DEFINED_DATA',
            'requireEqual("collateral", "undefinedData", PRE_UNDEFINED_DATA',
            'requireEqual("collateral", "bookmarks", PRE_BOOKMARKS',
            'requireEqual("collateral", "memory digest"',
            'requireEqual("collateral", "function shape digest"',
            'requireEqual("collateral", "function comment/tag digest"',
            'require(drift.isEmpty(), "collateral drift: " + drift);',
            'requireEqual("state", "function NAME digest", PRE_FUNCTION_NAME_DIGEST',
            '"POST name"',
        ):
            with self.subTest(needle):
                self.assertEqual(
                    self.base.count(needle),
                    self.v2.count(needle),
                    f"the {needle!r} gate changed between the base and V2",
                )
                self.assertGreaterEqual(self.v2.count(needle), 1)

    def test_setname_is_still_the_only_authorized_verb(self) -> None:
        """No body, boundary, comment, tag, data or byte write may appear."""
        forbidden_verbs = [
            "setBody(",
            "clearListing(",
            "createFunction(",
            "removeFunction(",
            "setComment(",
            "setPlateComment(",
            "addTag(",
            "createData(",
            "setBytes(",
            "disassemble(",
            "setCallingConvention(",
            "updateFunction(",
            "removeReference(",
            "setBookmark(",
        ]
        for verb in forbidden_verbs:
            with self.subTest(verb):
                self.assertNotIn(verb, self.v2, f"V2 can call {verb}")
                self.assertNotIn(verb, self.base)
        self.assertIn("setName(", self.v2)

    def test_the_transaction_is_still_single_and_atomic(self) -> None:
        self.assertEqual(self.base.count("startTransaction("), 1)
        self.assertEqual(self.v2.count("startTransaction("), 1)
        self.assertIn("endTransaction(", self.v2)


class NameCohort160ManifestTests(unittest.TestCase):
    """The manifest V2 is authorized to apply, and only that manifest."""

    @classmethod
    def setUpClass(cls) -> None:
        if not MANIFEST.exists():
            raise unittest.SkipTest(f"manifest not tracked yet: {MANIFEST}")
        cls.raw = MANIFEST.read_bytes()
        cls.lines = cls.raw.decode("utf-8").rstrip("\n").split("\n")

    def test_manifest_is_frozen(self) -> None:
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), MANIFEST_SHA256)

    def test_manifest_shape(self) -> None:
        self.assertEqual(self.lines[0].split("\t"), MANIFEST_COLUMNS)
        self.assertEqual(len(self.lines) - 1, MANIFEST_ROWS)

    def test_the_five_refuted_rows_are_not_in_the_manifest(self) -> None:
        addrs = {line.split("\t")[0] for line in self.lines[1:]}
        for addr in REFUTED_ADDRESSES_THAT_MUST_NOT_SHIP:
            with self.subTest(addr):
                self.assertNotIn(
                    addr,
                    addrs,
                    f"{addr} was dropped by the recorded recommendation and "
                    "must never ride along",
                )

    def test_no_row_is_a_no_op_and_no_name_repeats(self) -> None:
        addrs: list[str] = []
        current: list[str] = []
        proposed: list[str] = []
        for line in self.lines[1:]:
            cols = line.split("\t")
            addrs.append(cols[0])
            current.append(cols[3])
            proposed.append(cols[4])
            self.assertNotEqual(cols[3], cols[4], f"no-op rename at {cols[0]}")
        self.assertEqual(len(set(addrs)), MANIFEST_ROWS, "duplicate address")
        self.assertEqual(len(set(proposed)), MANIFEST_ROWS, "duplicate proposed name")
        self.assertEqual(len(set(current)), MANIFEST_ROWS, "duplicate current name")

    def test_the_rename_map_is_acyclic_with_no_collisions(self) -> None:
        """The absolute no-collision gate, restated over the manifest itself."""
        current = {line.split("\t")[3] for line in self.lines[1:]}
        proposed = {line.split("\t")[4] for line in self.lines[1:]}
        self.assertEqual(
            current & proposed,
            set(),
            "a proposed name is also some row's current name - that is a "
            "swap the absolute no-collision gate must refuse",
        )

    def test_every_row_is_a_legal_name_at_a_hex_address(self) -> None:
        legal = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,190}$")
        for line in self.lines[1:]:
            cols = line.split("\t")
            with self.subTest(cols[0]):
                self.assertRegex(cols[0], r"^0x[0-9a-f]{8}$")
                self.assertIn(cols[1], ("PROMOTE", "DEMOTE", "SLOTFIX"))
                self.assertIn(cols[2], ("FUNCTION", "SYMBOL:Label"))
                self.assertRegex(cols[4], legal)
                self.assertNotIn("<", cols[4])
                self.assertNotIn(">", cols[4])

    def test_the_provenance_and_kind_census_matches_the_recommendation(self) -> None:
        prov: dict[str, int] = {}
        kind: dict[str, int] = {}
        for line in self.lines[1:]:
            cols = line.split("\t")
            prov[cols[1]] = prov.get(cols[1], 0) + 1
            kind[cols[2]] = kind.get(cols[2], 0) + 1
        self.assertEqual(prov, {"PROMOTE": 31, "DEMOTE": 114, "SLOTFIX": 15})
        self.assertEqual(kind, {"FUNCTION": 158, "SYMBOL:Label": 2})


class NameCohort160MutatorMatrixTests(unittest.TestCase):
    """The 26 provoked gate probes, replayed from the executed receipt.

    These are not source assertions: each probe was a real headless run of a
    single-difference mutant against a scratch replica, and each had to refuse.
    The receipt lives in the authoring session's scratch lane, so this class
    skips on a fresh clone rather than failing.
    """

    RECEIPT = Path(
        r"C:\Users\david\AppData\Local\Temp\claude"
        r"\C--Users-david-source-Onslaught-Career-Editor"
        r"\6174219b-0c29-4056-883b-580c862ff182\scratchpad\name-cohort"
        r"\receipts\10-mutator-matrix.json"
    )

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.RECEIPT.exists():
            raise unittest.SkipTest("mutator matrix receipt not present")
        cls.matrix = json.loads(cls.RECEIPT.read_text(encoding="utf-8"))

    def _probes(self) -> list[dict]:
        m = self.matrix
        return m["probes"] if isinstance(m, dict) and "probes" in m else m

    def test_the_matrix_has_all_twenty_six_probes(self) -> None:
        self.assertEqual(len(self._probes()), 26)

    def test_every_probe_refused(self) -> None:
        for probe in self._probes():
            with self.subTest(probe["probe"]):
                self.assertEqual(probe["verdict"], "REFUSED")
                self.assertTrue(probe["refusalObserved"])
                self.assertNotEqual(probe["exit"], 0)

    def test_every_probe_refused_with_its_own_message(self) -> None:
        """A gate that refuses for the wrong reason is not the gate you tested."""
        messages = [p["expectedRefusal"] for p in self._probes()]
        self.assertEqual(
            len(set(messages)),
            len(messages),
            "two probes were graded against the same refusal message",
        )

    def test_no_probe_ever_applied_a_row(self) -> None:
        for probe in self._probes():
            with self.subTest(probe["probe"]):
                self.assertFalse(probe["appliedAnyway"])

    def test_the_containment_gate_itself_was_provoked(self) -> None:
        tags = {p["probe"] for p in self._probes()}
        for needed in ("p01-live-forbidden", "p02-outside-lane", "p03-outside-session"):
            self.assertIn(needed, tags)

    def test_the_collateral_gates_were_provoked_by_real_mutants(self) -> None:
        """m1-m4 mutated the applier itself, ran it writable, and were caught."""
        mutants = {p["probe"]: p for p in self._probes() if p["probe"].startswith("m")}
        self.assertEqual(
            set(mutants),
            {"m1-non-target-rename", "m2-comment-write", "m3-body-change", "m4-skip-one"},
        )
        for tag, probe in mutants.items():
            with self.subTest(tag):
                self.assertEqual(probe["verdict"], "REFUSED")
                self.assertFalse(probe["appliedAnyway"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
