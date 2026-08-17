#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safety, derivation and losslessness tests for the cohort manifest framework.

The framework replaces three near-duplicate one-shot appliers:

  tools/GhidraApplyBoundaryCohort41V4.java   geometry verbs (bounded disassemble,
                                             bounded clear, stale-bookmark
                                             removal, setBody)
  tools/GhidraApplyNameCohort160V2.java      setName only
  tools/GhidraApplyAbiSignaturesV2.java      prototype/signature only

Two files carry it:

  tools/GhidraApplyCohortManifest.java       the LIVE_FORBIDDEN instrument.  It
                                             refuses any project path under
                                             Ghidra\\Projects or the tracked
                                             snapshot and requires a
                                             "cohort-rehearsal" lane segment.
                                             It stays this way forever.
  tools/GhidraApplyCohortManifestLive.java   its live-capable twin.

The twin's entire safety argument is that it is the instrument with ONE gate
inverted - containment - and every other gate, pin, verb, census and refusal
message carried over verbatim.  `LIVE_ALLOWLISTED_EDITS` below is that reviewed
difference, and it is a contract rather than documentation:

  * replaying the allowlist onto the instrument must reproduce the twin byte for
    byte (forward proof), and
  * every line the two files differ on must be claimed by an allowlist entry
    (line-by-line proof), and
  * with comments stripped, the surviving code delta must be exactly the
    containment constants, the containment gate, the cohort authorization check,
    the class name, the framework id and the policy.

A relaxed pin, a dropped gate or a changed verb would appear as an unclaimed
differing line and would break the reconstruction, so it cannot be smuggled in.
Every entry must be `banner`, `identity`, `policy` or `containment`; nothing
else may ever be added.

GATE_INVENTORY is the losslessness contract: every gate any of the three
original appliers implemented appears there with the applier it came from, and
`test_every_inventoried_gate_exists_in_the_framework` fails if its refusal text
is not in the framework source.

Run:  python -m unittest tools.ghidra_cohort_framework_tests -v
Emit the twin from the instrument + allowlist:
      python tools/ghidra_cohort_framework_tests.py --emit-live
"""
from __future__ import annotations

import difflib
import hashlib
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

BASE = TOOLS / "GhidraApplyCohortManifest.java"
LIVE = TOOLS / "GhidraApplyCohortManifestLive.java"
SPEC_DIR = TOOLS / "cohort-specs"

BOUNDARY_SPEC = SPEC_DIR / "boundary-cohort41.spec.tsv"
NAME_SPEC = SPEC_DIR / "name-cohort160.spec.tsv"
ABI_SPEC = SPEC_DIR / "abi-cohort294.spec.tsv"

BOUNDARY_MANIFEST = (
    REPO / "reverse-engineering" / "binary-analysis"
    / "boundary-cohort41-promotion-manifest-2026-08-16.tsv"
)
NAME_MANIFEST = (
    REPO / "reverse-engineering" / "binary-analysis"
    / "name-cohort-promotion-manifest-2026-08-17.tsv"
)
# The ABI manifest is retail-derived and stays out of git; the replay lane keeps
# the byte-identical copy the completed ceremony used.
ABI_MANIFEST = (
    REPO / "local-lab" / "ghidra-cohort-framework" / "manifests"
    / "abi-signature-manifest-2026-08-17.tsv"
)

REQUIRED_LIVE_PROJECT_DIR = r"c:\users\david\ghidra\projects\bea.rep"
PROGRAM_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# ---------------------------------------------------------------------------
# THE GATE INVENTORY.
#
# id -> (refusal fragment that must appear in the framework source,
#        origin applier the gate is carried over from)
#
# origin codes:
#   B  tools/GhidraApplyBoundaryCohort41V4.java
#   N  tools/GhidraApplyNameCohort160V2.java
#   A  tools/GhidraApplyAbiSignaturesV2.java
#   F  new in the framework - a strengthening the consolidation made possible.
#      Every F entry must be a gate NONE of the three had; an F entry may never
#      replace a B/N/A one.
GATE_INVENTORY: dict[str, tuple[str, str]] = {
    # -- containment and policy ------------------------------------------
    "c01-forbidden-project-path": ("reason=forbidden_project_path", "BNA"),
    "c02-not-in-rehearsal-scratch": (
        "reason=project_not_in_rehearsal_scratch", "B"),
    "c03-no-project-locator": ("reason=no_project_locator", "B"),
    "c04-no-current-program": ("reason=no_current_program", "B"),
    "c05-bad-mode": ("reason=bad_mode", "B"),
    "c06-usage-arity": ("reason=usage", "B"),
    "c07-policy-echoed": ('POLICY = "LIVE_FORBIDDEN"', "B"),
    # -- program identity ------------------------------------------------
    "i01-program-name": ("program name expected", "BNA"),
    "i02-program-md5": ("program md5 expected", "BNA"),
    "i03-program-sha256": ("program sha256 expected", "BNA"),
    "i04-image-base": ("program imageBase expected", "BNA"),
    "i05-language": ("program language expected", "BNA"),
    "i06-compiler-spec": ("program compilerSpec expected", "BNA"),
    "i07-text-block-geometry": ("text block geometry", "B"),
    # -- PRE metric pins -------------------------------------------------
    "p01-pre-functions": ("PRE function count", "BNA"),
    "p02-pre-instructions": ("PRE instruction count", "BNA"),
    "p03-pre-references": ("PRE reference count", "BNA"),
    "p04-pre-defined-data": ("PRE definedData count", "NA"),
    "p05-pre-undefined-data": ("PRE undefinedData count", "NA"),
    "p06-pre-bookmarks": ("PRE bookmark count", "BNA"),
    "p07-pre-function-name-digest": ("PRE function NAME digest", "N"),
    "p08-pre-function-body-digest": ("PRE function BODY digest", "N"),
    "p09-pre-frozen-digest": ("PRE frozen-census digest", "F"),
    # -- manifest integrity ----------------------------------------------
    "m01-manifest-sha-pin": ("manifest sha256", "BNA"),
    "m02-manifest-byte-pin": ("manifest bytes", "B"),
    "m03-manifest-header": ("manifest header drift", "BNA"),
    "m04-manifest-row-count": ("row count ", "BNA"),
    "m05-row-column-count": ("column count ", "BNA"),
    "m06-duplicate-address": ("duplicate address in manifest", "BNA"),
    "m07-addr-not-0x": ("address not 0x-prefixed", "BNA"),
    "m08-no-op-rename": ("is a no-op rename", "N"),
    "m09-no-op-proposal": ("is a no-op proposal", "A"),
    "m10-illegal-enum-value": ("illegal value in ", "NA"),
    "m11-illegal-prefix-value": ("matches no allowed prefix", "A"),
    "m12-constant-column": ("must equal [", "A"),
    "m13-generic-duplicate-column": ("duplicate ", "N"),
    "m14-rename-cycle": ("rename cycle:", "N"),
    "m15-illegal-proposed-name": ("illegal proposed name", "N"),
    "m16-illegal-return-type": ("illegal return type", "A"),
    "m17-illegal-param-type": ("illegal param type", "A"),
    "m18-illegal-param-name": ("illegal param name", "A"),
    "m19-illegal-param-mode": ("illegal param mode", "A"),
    "m20-param-field-count": ("paramSpec field count expected", "A"),
    "m21-arity-bytes-mismatch": ("arityBytes/arity mismatch", "A"),
    "m22-stack-param-count": ("stack param count expected", "A"),
    "m23-fastcall-edx-hazard": ("fabricate an EDX argument", "A"),
    "m24-current-signature-sha": ("CURRENT signature sha256 expected", "A"),
    "m25-forbidden-token": ("FORBIDDEN MANIFEST TOKEN present", "A"),
    "m26-unparseable-range": ("unparseable range text", "B"),
    "m27-delta-not-numeric": ("deltaBytes not numeric", "B"),
    "m28-spec-sha-pin": ("SPEC SHA PIN", "F"),
    "m29-spec-unknown-key": ("SPEC UNKNOWN KEY", "F"),
    "m30-spec-unknown-verb": ("SPEC UNKNOWN VERB", "F"),
    "m31-spec-syntax": ("SPEC SYNTAX", "F"),
    "m32-column-binding-missing": (
        "which the header does not contain", "F"),
    # -- verb declaration (the framework's own structural gate) ----------
    "v01-verb-not-declared": ("VERB NOT DECLARED", "F"),
    "v02-verb-binding-missing": ("does not bind", "F"),
    "v03-verb-dependency": ("VERB DEPENDENCY", "F"),
    "v04-no-verb-declared": ("declares no verb", "F"),
    # -- per-row current-state staleness ---------------------------------
    "s01-no-function-at-entry": ("NO FUNCTION AT ENTRY", "BNA"),
    "s02-function-entry-exact": ("function entry expected", "NA"),
    "s03-current-name-drift": ("CURRENT name expected", "NA"),
    "s04-current-signature-drift": ("CURRENT signature expected", "A"),
    "s05-current-cc-drift": ("CURRENT calling convention expected", "A"),
    "s06-current-body-drift": ("CURRENT STATE DRIFT", "B"),
    "s07-custom-variable-storage": ("uses custom variable storage", "A"),
    "s08-thunk": ("is a thunk", "A"),
    "s09-external": ("is external", "A"),
    "s10-label-is-a-function": (
        "is a function, but the manifest says SYMBOL:Label", "N"),
    "s11-no-primary-symbol": ("no primary symbol at", "N"),
    "s12-primary-symbol-dynamic": ("primary symbol is dynamic", "N"),
    "s13-symbol-type": ("symbolType expected", "N"),
    "s14-unknown-data-type": ("unknown data type", "A"),
    # -- collision -------------------------------------------------------
    "x01-name-collision": ("collision: proposed name", "N"),
    "x02-pre-holder-missing": ("is not held at", "N"),
    "x03-target-target-overlap": ("target/target overlap at", "B"),
    "x04-overlaps-existing-function": ("OVERLAPS existing function", "B"),
    # -- geometry --------------------------------------------------------
    "g01-not-at-entry": ("proposed body does not start at the entry point", "B"),
    "g02-leaves-text": ("proposed body leaves .text", "B"),
    "g03-drops-owned-bytes": ("DROPS currently owned bytes", "B"),
    "g04-delta-mismatch": ("!= measured", "B"),
    "g05-adds-nothing": ("proposal adds nothing", "B"),
    "g06-terminator-unreadable": ("terminator unreadable at", "B"),
    "g07-terminator-bytes-differ": ("terminator bytes differ", "B"),
    "g08-terminator-outside-body": (
        "terminator not inside the proposed body", "B"),
    "g09-malformed-byteproof": ("malformed byteProof segment", "B"),
    "g10-byteproof-unreadable": ("byteProof range unreadable at", "B"),
    "g11-byteproof-no-reproduce": ("byteProof does not reproduce at", "B"),
    "g12-byteproof-range-mismatch": ("!= added ranges", "B"),
    "g13-ends-mid-instruction": ("ENDS MID-INSTRUCTION", "B"),
    "g14-admitted-byte-pin": ("admitted byte count", "B"),
    "g15-admitted-undefined-pin": ("PRE admitted-undefined byte count", "B"),
    # -- classification (bounded disassemble / clear) --------------------
    "k01-unclassified-bytes-remain": ("UNCLASSIFIED BYTES REMAIN", "B"),
    "k02-classified-regression": ("CLASSIFIED-BYTE REGRESSION", "B"),
    "k03-clear-escaped-admitted": ("CLEAR ESCAPED the admitted range", "B"),
    "k04-table-row-cleared": ("JUMP/SEH TABLE ROW WAS CLEARED", "B"),
    "k05-table-data-changed": ("JUMP/SEH TABLE DATA CHANGED", "B"),
    "k06-precondition-row-mutated": ("PRECONDITION ROW WAS MUTATED", "B"),
    "k07-post-ends-mid-instruction": (
        "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION", "B"),
    "k08-instruction-escaped-body": ("INSTRUCTION ESCAPED the proposed body", "B"),
    "k09-admitted-still-undefined": ("admitted bytes still undefined", "B"),
    "k10-cleared-unit-pin": ("cleared unit count", "B"),
    "k11-cleared-byte-pin": ("cleared byte count", "B"),
    "k12-clear-plan-mismatch": ("CLEAR PLAN MISMATCH", "B"),
    "k13-instruction-escape": ("INSTRUCTION ESCAPE:", "B"),
    "k14-reference-escape": ("REFERENCE ESCAPE:", "B"),
    # -- bounded bookmark hygiene ----------------------------------------
    "b01-stale-outside-admitted": (
        "STALE BOOKMARK OUTSIDE the admitted ranges at", "B"),
    "b02-stale-at-unclassified": ("STALE BOOKMARK at an unclassified byte", "B"),
    "b03-pinned-stale-absent": ("PINNED STALE BOOKMARK ABSENT at", "B"),
    "b04-created-outside-admitted": (
        "BOOKMARK CREATED OUTSIDE the admitted ranges at", "B"),
    "b05-removed-outside-admitted": (
        "BOOKMARK REMOVED OUTSIDE the admitted ranges at", "B"),
    "b06-survived-hygiene": ("BOOKMARKS SURVIVED hygiene", "B"),
    "b07-unpinned-bookmark-removal": (
        "that are not in the pinned removed set", "F"),
    "b08-bookmarks-gained": ("bookmarks GAINED", "F"),
    # -- POST per row ----------------------------------------------------
    "o01-post-name": ("POST name expected", "NA"),
    "o02-post-body": ("POST body expected", "B"),
    "o03-post-admitted-undefined": (
        "POST admitted bytes still undefined", "B"),
    "o04-post-signature": ("POST signature expected", "A"),
    "o05-post-cc": ("POST calling convention expected", "A"),
    "o06-post-stack-bytes": ("POST stack parameter bytes expected", "A"),
    "o07-post-varargs": ("POST varargs expected", "A"),
    "o08-post-signature-source": ("POST signature source expected", "A"),
    "o09-post-custom-storage": ("POST uses custom variable storage", "A"),
    "o10-post-stack-count": ("POST stack parameter count expected", "A"),
    "o11-post-name-census": ("is not exactly one symbol at", "N"),
    "o12-pre-name-still-held": ("is still held at", "N"),
    "o13-other-holders-changed": ("changed: expected", "N"),
    "o14-post-functions": ("POST function count", "BNA"),
    "o15-post-instructions": ("POST instruction count", "B"),
    "o16-post-references": ("POST reference count", "B"),
    "o17-post-bookmarks": ("POST bookmark count", "B"),
    "o18-post-defined-data": ("POST definedData count", "NA"),
    "o19-post-undefined-data": ("POST undefinedData count", "NA"),
    "o20-post-name-digest": ("POST function NAME digest", "F"),
    "o21-post-body-digest": ("POST function BODY digest", "F"),
    "o22-post-frozen-digest": ("POST frozen-census digest", "F"),
    "o23-apply-threw": ("in-process verify failed", "B"),
    "o24-rendered-prototype": ("rendered prototype expected", "A"),
    # -- readback --------------------------------------------------------
    "r01-readback-name": ("READBACK name expected", "N"),
    "r02-readback-signature": ("READBACK signature expected", "A"),
    "r03-readback-body-drift": ("READBACK STATE DRIFT", "B"),
    "r04-readback-range-mismatch": ("READBACK RANGE MISMATCH", "B"),
    "r05-readback-unclassified": ("READBACK UNCLASSIFIED BYTES", "B"),
    "r06-readback-census": ("READBACK census for", "N"),
    "r07-readback-pre-name-held": ("READBACK: the PRE name", "N"),
    "r08-readback-stack-bytes": ("READBACK stack parameter bytes expected", "A"),
    "r09-readback-varargs": ("READBACK varargs expected", "A"),
    "r10-readback-signature-source": (
        "READBACK signature source expected", "A"),
    "r11-readback-custom-storage": ("READBACK uses custom variable storage", "A"),
    # -- full non-target collateral, frozen columns ----------------------
    "l01-entry-point-set-changed": (
        "the set of function entry points changed", "NA"),
    "l02-non-target-column-changed": ("NON-TARGET 0x", "NA"),
    "l03-target-moved-frozen-column": ("moved FROZEN column", "F"),
    "l04-target-did-not-change": ("did not change at all", "NA"),
    "l05-changed-count": ("changed function count", "NA"),
    "l06-untouched-count": ("untouched function count", "A"),
    "l07-symbol-census-changed": ("the non-dynamic symbol census changed", "A"),
    "l08-symbols-added-pin": ("symbols added ", "N"),
    "l09-symbols-removed-pin": ("symbols removed ", "N"),
    "l10-symbol-count": ("non-dynamic symbol count", "N"),
    "l11-unexpected-added-symbol": ("UNEXPECTED ADDED SYMBOL", "N"),
    "l12-unexpected-removed-symbol": ("UNEXPECTED REMOVED SYMBOL", "N"),
    "l13-bookmark-census-changed": ("the bookmark census changed", "A"),
    "l14-defined-data-census-changed": (
        "the defined-data census changed", "A"),
    "l15-defined-data-outside-admitted": (
        "DEFINED DATA CHANGED OUTSIDE the admitted ranges at", "F"),
    "l16-memory-digest": ("collateral memory digest expected", "NA"),
    "l17-collateral-drift": ("collateral drift", "N"),
    "l18-short-memory-read": ("SHORT MEMORY READ at", "NA"),
}

# The frozen per-function collateral column list, in order.  A column may only
# be added here together with the measurement that shows it is stable.
FROZEN_COLUMNS = [
    "name", "rangeSpec", "bodyBytes", "bodyRangeCount", "signatureShape",
    "callingConvention", "varArgs", "signatureSource", "symbolSource",
    "thunk", "thunkedEntry", "external", "noReturn", "customStorage",
    "stackParamBytes", "stackParamCount", "commentSha",
    "repeatableCommentSha", "tags", "namespace",
]

VERBS = [
    "DISASSEMBLE_BOUNDED", "CLEAR_BOUNDED", "REMOVE_STALE_BOOKMARK",
    "SET_BODY", "SET_NAME", "SET_PROTOTYPE",
]

# The only Ghidra mutation calls the framework may contain, and how many times.
# Anything else is an unauthorized verb.
AUTHORIZED_MUTATION_CALLS = {
    ".setBody(": 1,
    ".setName(": 2,            # Function.setName and Symbol.setName
    ".updateFunction(": 1,
    ".setVarArgs(": 1,
    ".removeBookmark(": 1,
    ".disassemble(": 2,        # bounded phase 1, and the escape fault injector
    ".clearCodeUnits(": 5,     # resync, precedent, extraclear, clearescape,
                               # strand - the last four are fault injectors that
                               # can never commit
}

FORBIDDEN_MUTATION_CALLS = [
    ".setComment(",
    ".setRepeatableComment(",
    ".addTag(",
    ".removeTag(",
    ".setCallingConvention(",
    ".setReturnType(",
    ".setCustomVariableStorage(",
    ".createData(",
    ".removeData(",
    ".clearListing(",
    ".setBytes(",
    ".createFunction(",
    ".removeFunction(",
    ".addMemoryReference(",
    ".setPrimary(",
    ".setPinned(",
    ".createLabel(",
    ".removeSymbol(",
    ".setNoReturn(",
    ".setThunkedFunction(",
    ".setBookmark(",
]

# Strings that would claim a reversibility this build does not have.  None may
# appear in the framework, because no receipt may claim transaction-level
# atomicity.
FORBIDDEN_REVERSIBILITY_CLAIMS = [
    "rolled-back",
    "rolled_back",
    "TRANSACTION_ABORTED",
    "rolls the LOGICAL state back",
    "never left half-",
    "transaction is atomic",
    "atomic",
]

# The framework is allowed to say, once, that it makes no atomicity claim.  That
# disclaimer is stripped before the scan so it cannot mask a real claim.
ALLOWED_DISCLAIMER = "never_claims_transaction_level_atomicity"


def code_only(text: str) -> str:
    """Non-comment source lines: what actually reaches a receipt or the log."""
    return "\n".join(
        line for line in text.split("\n") if not line.strip().startswith("//"))


# ---------------------------------------------------------------------------
# The complete reviewed difference between the instrument and its live twin.
LIVE_ALLOWLISTED_EDITS: list[tuple[str, str, str]] = [
    (
        "banner: the file header stops describing the shared instrument and "
        "states that this is the live-capable twin",
        "// COHORT MANIFEST FRAMEWORK - the single reusable Ghidra promotion applier.\n"
        "//\n",
        "// COHORT MANIFEST FRAMEWORK - LIVE-CAPABLE TWIN.\n"
        "//\n"
        "// This is GhidraApplyCohortManifest WITH EXACTLY ONE GATE INVERTED.  That file\n"
        "// is the rehearsal instrument and stays LIVE_FORBIDDEN forever; this is its\n"
        "// live-capable twin and differs from it only in the containment gate: where the\n"
        '// rehearsal framework requires a "cohort-rehearsal" path segment and refuses any\n'
        "// path under Ghidra\\Projects, this REQUIRES the live maintainer project\n"
        "// directory by exact match, refuses everything else including the tracked\n"
        "// repository snapshot, and additionally refuses any cohort id that is not in its\n"
        "// compiled authorization allowlist.  Every other gate, pin, verb, census and\n"
        "// refusal message is carried over verbatim, and\n"
        "// tools/ghidra_cohort_framework_tests.py asserts that line by line.\n"
        "//\n",
    ),
    (
        "banner: the policy paragraph states the per-cohort authorization this "
        "twin runs under instead of claiming to be live-forbidden",
        "// POLICY.  This file is LIVE_FORBIDDEN by construction.  Its containment gate\n"
        '// requires a "cohort-rehearsal" path segment and refuses any project path under\n'
        "// Ghidra\\Projects or under the tracked repository snapshot.  There is no mode,\n"
        "// spec key, or argument that can give it a live mode.  The live-capable twin is\n"
        "// GhidraApplyCohortManifestLive.java, produced from this file by the reviewed\n"
        "// allowlisted derivation in tools/ghidra_cohort_framework_tests.py - the same\n"
        "// one-gate-inverted pattern already audited for V4 / V2 - and it additionally\n"
        "// refuses any cohort id that is not in its compiled authorization allowlist.\n",
        "// POLICY.  This file is the LIVE-CAPABLE twin and its use is authorized only per\n"
        "// cohort: LIVE_AUTHORIZED_COHORTS below is the compiled allowlist, and a cohort\n"
        "// absent from it can never reach live whatever its spec says.  Its containment\n"
        "// gate requires the live maintainer project directory by exact match and refuses\n"
        "// everything else, including the tracked repository snapshot.  The rehearsal\n"
        "// instrument is GhidraApplyCohortManifest.java, which stays LIVE_FORBIDDEN\n"
        "// forever; this file is derived from it by the reviewed allowlisted derivation\n"
        "// in tools/ghidra_cohort_framework_tests.py - the same one-gate-inverted pattern\n"
        "// already audited for V4 / V2.\n",
    ),
    (
        "banner: the usage line names the script that actually exists",
        "//   -postScript GhidraApplyCohortManifest.java\n",
        "//   -postScript GhidraApplyCohortManifestLive.java\n",
    ),
    (
        "identity: Ghidra requires the class name to match the file name",
        "public class GhidraApplyCohortManifest extends GhidraScript {\n",
        "public class GhidraApplyCohortManifestLive extends GhidraScript {\n",
    ),
    (
        "policy: the framework id and the declared policy constant, both echoed "
        "into every receipt, and the containment constants - the live project "
        "stops being a forbidden marker because it is now the requirement",
        '    static final String FRAMEWORK = "bea.ghidra.cohort-framework.v1";\n'
        '    static final String POLICY = "LIVE_FORBIDDEN";\n'
        '    static final String CONTAINMENT_SEGMENT = "cohort-rehearsal";\n'
        "    static final String[] FORBIDDEN_PATH_MARKERS = {\n"
        r'        "ghidra\\projects", "ghidra/projects",' "\n"
        r'        "onslaught-career-editor\\reverse-engineering",' "\n"
        '        "onslaught-career-editor/reverse-engineering",\n'
        "    };\n",
        '    static final String FRAMEWORK = "bea.ghidra.cohort-framework.live.v1";\n'
        '    static final String POLICY = "LIVE_AUTHORIZED_PER_COHORT";\n'
        "    // The one and only project this twin may ever open.  Exact match on the\n"
        "    // lowercased absolute project directory with '/' folded to '\\', so a\n"
        "    // scratch replica, a restored backup, a rehearsal copy or any other clone\n"
        "    // can never satisfy it.\n"
        "    static final String REQUIRED_LIVE_PROJECT_DIR =\n"
        r'        "c:\\users\\david\\ghidra\\projects\\bea.rep";' "\n"
        "    // The tracked repository snapshot stays forbidden and is still checked\n"
        "    // first, exactly as the rehearsal framework checked its forbidden markers.\n"
        "    static final String[] FORBIDDEN_PATH_MARKERS = {\n"
        r'        "onslaught-career-editor\\reverse-engineering",' "\n"
        '        "onslaught-career-editor/reverse-engineering",\n'
        "    };\n"
        "    // Cohorts the maintainer has authorized for a live apply, one entry per\n"
        "    // completed per-cohort grant.  A cohort id absent from this list can never\n"
        "    // reach live, whatever its spec declares.\n"
        "    static final String[] LIVE_AUTHORIZED_COHORTS = {\n"
        '        "boundary-cohort41", "name-cohort160", "abi-cohort294",\n'
        "    };\n",
    ),
    (
        "containment: THE GATE - require the live project by exact match, refuse "
        "everything else, and announce the live target",
        "        if (!lower.contains(CONTAINMENT_SEGMENT)) {\n"
        '            println("COHORT_REFUSE reason=project_not_in_rehearsal_scratch path="\n'
        "                + projectPath);\n"
        "            return;\n"
        "        }\n",
        "        if (!lower.equals(REQUIRED_LIVE_PROJECT_DIR)) {\n"
        '            println("COHORT_REFUSE reason=project_is_not_the_live_maintainer_project"\n'
        '                + " path=" + projectPath);\n'
        "            return;\n"
        "        }\n"
        '        println("COHORT_LIVE_TARGET banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT"\n'
        '            + " policy=" + POLICY + " path=" + projectPath);\n',
    ),
    (
        "containment: only an allowlisted cohort may reach live at all",
        '        cohortId = spec.opt("cohortId", "<missing>");\n',
        '        cohortId = spec.opt("cohortId", "<missing>");\n'
        "        if (!Arrays.asList(LIVE_AUTHORIZED_COHORTS).contains(cohortId)) {\n"
        '            println("COHORT_REFUSE reason=cohort_not_live_authorized cohort="\n'
        '                + cohortId + " allowlist="\n'
        "                + Arrays.asList(LIVE_AUTHORIZED_COHORTS));\n"
        "            return;\n"
        "        }\n",
    ),
]

ALLOWED_EDIT_CATEGORIES = ("banner:", "identity:", "policy:", "containment:")


def derive_live(base_text: str) -> str:
    """Replay the allowlist onto the instrument source."""
    out = base_text
    for reason, before, after in LIVE_ALLOWLISTED_EDITS:
        if out.count(before) != 1:
            raise AssertionError(
                f"allowlist entry [{reason}] matched {out.count(before)} times")
        out = out.replace(before, after, 1)
    return out


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


def read_spec(path: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.rstrip("\r")
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, _, value = line.partition("\t")
        out.setdefault(key.strip(), []).append(value.strip())
    return out


class FrameworkDerivationTests(unittest.TestCase):
    """The live twin is the instrument with exactly one gate inverted."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.live = LIVE.read_text(encoding="utf-8")

    def test_replaying_the_allowlist_reproduces_the_twin_byte_for_byte(self) -> None:
        self.assertEqual(derive_live(self.base), self.live)

    def test_every_differing_line_is_claimed_by_an_allowlist_entry(self) -> None:
        claimed: list[str] = []
        for _reason, before, after in LIVE_ALLOWLISTED_EDITS:
            claimed.extend(l for l in before.split("\n") if l.strip())
            claimed.extend(l for l in after.split("\n") if l.strip())
        claimed_set = {l.strip() for l in claimed}
        removed, added = _delta(self.base.split("\n"), self.live.split("\n"))
        for line in removed + added:
            if not line.strip():
                continue
            self.assertIn(line.strip(), claimed_set,
                          f"unclaimed differing line: {line!r}")

    def test_every_allowlist_entry_is_a_permitted_category(self) -> None:
        for reason, _b, _a in LIVE_ALLOWLISTED_EDITS:
            self.assertTrue(reason.startswith(ALLOWED_EDIT_CATEGORIES), reason)

    def test_the_code_delta_is_only_containment_identity_and_policy(self) -> None:
        removed, added = _delta(_code_lines(self.base), _code_lines(self.live))
        joined = " ".join(removed + added)
        for token in ("CONTAINMENT_SEGMENT", "REQUIRED_LIVE_PROJECT_DIR",
                      "ghidra/projects", "LIVE_AUTHORIZED_COHORTS",
                      "POLICY", "FRAMEWORK", "class GhidraApplyCohortManifest",
                      "cohortId"):
            self.assertTrue(token in joined, f"expected in delta: {token}")
        # nothing about gates, pins, verbs or censuses may appear in the delta
        for forbidden in ("checkMetric", "fail(", "digestOf", "frozenCensus",
                          "setBody", "setName", "updateFunction",
                          "clearCodeUnits", "disassemble", "removeBookmark",
                          "spec.num", "gateMetrics", "collateralProof"):
            self.assertTrue(forbidden not in joined,
                            f"the derivation touched {forbidden}")

    def test_the_instrument_stays_live_forbidden(self) -> None:
        self.assertIn('POLICY = "LIVE_FORBIDDEN"', self.base)
        self.assertIn('CONTAINMENT_SEGMENT = "cohort-rehearsal"', self.base)
        self.assertIn("reason=project_not_in_rehearsal_scratch", self.base)
        for marker in (r'"ghidra\\projects"', '"ghidra/projects"'):
            self.assertIn(marker, self.base)
        self.assertNotIn("REQUIRED_LIVE_PROJECT_DIR", self.base)
        self.assertNotIn(REQUIRED_LIVE_PROJECT_DIR.replace("\\", "\\\\"),
                         self.base)

    def test_the_twin_requires_the_live_project_by_equals(self) -> None:
        self.assertIn("p.equals(REQUIRED_LIVE_PROJECT_DIR)".replace("p.", "lower."),
                      self.live)
        self.assertIn('POLICY = "LIVE_AUTHORIZED_PER_COHORT"', self.live)
        self.assertNotIn("CONTAINMENT_SEGMENT", self.live)
        # the tracked snapshot is still refused, and still checked first
        for marker in (r'"onslaught-career-editor\\reverse-engineering"',
                       '"onslaught-career-editor/reverse-engineering"'):
            self.assertIn(marker, self.live)

    def test_the_twin_allowlists_cohorts_and_only_the_three_completed_ones(self) -> None:
        self.assertIn("LIVE_AUTHORIZED_COHORTS", self.live)
        self.assertIn("reason=cohort_not_live_authorized", self.live)
        for cohort in ("boundary-cohort41", "name-cohort160", "abi-cohort294"):
            self.assertIn(f'"{cohort}"', self.live)

    def test_the_twin_carries_no_extra_containment_relaxation(self) -> None:
        """A live path must not be reachable from a contains() test."""
        self.assertNotIn("lower.contains(REQUIRED_LIVE_PROJECT_DIR)", self.live)


class FrameworkGateInventoryTests(unittest.TestCase):
    """Losslessness: every gate the three appliers had exists here."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.live = LIVE.read_text(encoding="utf-8")

    def test_every_inventoried_gate_exists_in_the_framework(self) -> None:
        missing = [f"{g} ({o}): {f!r}"
                   for g, (f, o) in sorted(GATE_INVENTORY.items())
                   if f not in self.base]
        self.assertEqual(missing, [], f"{len(missing)} gate(s) lost")

    def test_every_inventoried_gate_also_exists_in_the_live_twin(self) -> None:
        # the one inverted gate, and the policy constant it renames
        inverted = {"c02-not-in-rehearsal-scratch", "c07-policy-echoed"}
        missing = [g for g, (f, _o) in sorted(GATE_INVENTORY.items())
                   if g not in inverted and f not in self.live]
        self.assertEqual(missing, [])

    def test_every_origin_code_is_valid(self) -> None:
        for gate, (_f, origin) in GATE_INVENTORY.items():
            with self.subTest(gate=gate):
                self.assertTrue(origin)
                for ch in origin:
                    self.assertIn(ch, "BNAF", f"{gate}: bad origin {origin}")
                if "F" in origin:
                    self.assertEqual(origin, "F",
                                     f"{gate}: an F gate may not also claim B/N/A")

    def test_each_original_applier_is_represented(self) -> None:
        counts = {"B": 0, "N": 0, "A": 0, "F": 0}
        for _f, origin in GATE_INVENTORY.values():
            for ch in origin:
                counts[ch] += 1
        # the three appliers had 45 / 26 / 29 provoked gates respectively; the
        # inventory must carry at least that many from each.
        self.assertGreaterEqual(counts["B"], 45, counts)
        self.assertGreaterEqual(counts["N"], 26, counts)
        self.assertGreaterEqual(counts["A"], 29, counts)
        self.assertGreater(counts["F"], 0, counts)

    def test_no_gate_id_is_duplicated_by_refusal_text(self) -> None:
        """A gate that refuses for another gate's reason is not that gate."""
        seen: dict[str, str] = {}
        for gate, (fragment, _o) in GATE_INVENTORY.items():
            self.assertNotIn(fragment, seen,
                             f"{gate} shares its refusal text with {seen.get(fragment)}")
            seen[fragment] = gate


class FrameworkVerbTests(unittest.TestCase):
    """Verbs are opt-in and nothing else can be written."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.code = "\n".join(
            l for l in cls.base.splitlines() if not l.lstrip().startswith("//"))

    def test_only_the_authorized_mutation_calls_appear(self) -> None:
        for call, want in AUTHORIZED_MUTATION_CALLS.items():
            with self.subTest(call=call):
                self.assertEqual(self.code.count(call), want,
                                 f"{call} appears {self.code.count(call)} times")

    def test_no_forbidden_mutation_call_appears(self) -> None:
        for call in FORBIDDEN_MUTATION_CALLS:
            with self.subTest(call=call):
                self.assertNotIn(call, self.code)

    def test_the_verb_list_is_exactly_the_six_declared_verbs(self) -> None:
        for verb in VERBS:
            self.assertTrue(f'"{verb}"' in self.base, verb)
        self.assertTrue("KNOWN_VERBS = Arrays.asList(" in self.base)
        block = self.base.split("KNOWN_VERBS = Arrays.asList(", 1)[1]
        block = block.split(");", 1)[0]
        got = [t.strip().strip('",') for t in block.replace("\n", " ").split()]
        got = [t for t in got if t and t.startswith("V_")]
        self.assertEqual(len(got), len(VERBS))

    def test_a_column_a_non_declared_verb_owns_is_refused(self) -> None:
        self.assertIn("VERB NOT DECLARED", self.base)
        self.assertIn("this framework refuses an undeclared mutation", self.base)
        # every optional verb-owned column binding must appear in the owner map
        for key in ("col.currentName", "col.proposedName", "col.currentRanges",
                    "col.proposedRanges", "col.terminatorVa",
                    "col.terminatorBytes", "col.deltaBytes", "col.byteProof",
                    "col.currentSignature", "col.currentSignatureSha256",
                    "col.proposedSignature", "col.returnType", "col.paramSpec",
                    "col.arity", "col.arityBytes"):
            self.assertIn(f'owner.put("{key}"', self.base)

    def test_every_mutation_phase_is_guarded_by_its_verb(self) -> None:
        for verb, marker in (
            ("V_SET_BODY", "fn.setBody(row.proposed)"),
            ("V_SET_NAME", "SourceType.USER_DEFINED)"),
            ("V_SET_PROTOTYPE", "row.rendered = applyPrototype(row)"),
        ):
            self.assertIn(f"verbs.contains({verb})", self.base)
            self.assertIn(marker, self.base)

    def test_the_frozen_column_list_is_pinned(self) -> None:
        for column in FROZEN_COLUMNS:
            self.assertIn(f'"{column}"', self.base)
        block = self.base.split("static final String[] FROZEN_COLUMNS = {", 1)[1]
        block = block.split("};", 1)[0]
        got = [t.strip().strip('",') for t in block.replace("\n", " ").split()]
        got = [t for t in got if t]
        self.assertEqual(got, FROZEN_COLUMNS)


class FrameworkNoRollbackTests(unittest.TestCase):
    """The measured no-rollback reality, honoured in code and in receipts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")
        cls.live = LIVE.read_text(encoding="utf-8")

    def test_no_receipt_claims_transaction_level_atomicity(self) -> None:
        for text, label in ((self.base, "instrument"), (self.live, "twin")):
            scan = code_only(text).replace(ALLOWED_DISCLAIMER, "")
            for claim in FORBIDDEN_REVERSIBILITY_CLAIMS:
                with self.subTest(label=label, claim=claim):
                    self.assertTrue(
                        claim not in scan,
                        f"{label} emits the reversibility claim {claim!r}")

    def test_the_measured_reversibility_facts_are_stated(self) -> None:
        for text in (self.base, self.live):
            self.assertIn("CEREMONY_LEVEL_RESTORE_FROM_VERIFIED_PRE_BACKUP", text)
            self.assertIn("NOT_AVAILABLE_MEASURED_2026_08_17", text)
            self.assertIn("Program.canUndo() is false", text)
            self.assertIn("writes a NEW DATABASE VERSION even when the script "
                          "throws", text)
            self.assertIn("never claims one", text)

    def test_the_receipt_records_the_gate_order(self) -> None:
        for text in (self.base, self.live):
            self.assertIn(
                'ALL_NON_MUTATING_GATES_FOR_ALL_ROWS_BEFORE_', text)

    def test_all_gates_run_before_the_first_write(self) -> None:
        """The refusal sweep must precede startTransaction in source order."""
        for text in (self.base, self.live):
            sweep = text.index("COHORT_NO_MUTATION_PERFORMED")
            tx = text.index("int tx = currentProgram.startTransaction(")
            self.assertLess(sweep, tx)
            self.assertIn("allNonMutatingGatesPassed=true", text)
            self.assertIn("firstWriteMayNowProceed=true", text)

    def test_a_fault_or_plan_run_can_never_commit(self) -> None:
        for text in (self.base, self.live):
            self.assertIn(
                "commit = failures.isEmpty() && !planOnly && !faultMode;", text)
            self.assertEqual(text.count("commit = failures.isEmpty()"), 1)
            self.assertEqual(text.count("boolean commit = false;"), 1)

    def test_the_only_endtransaction_uses_the_guarded_flag(self) -> None:
        for text in (self.base, self.live):
            code = code_only(text)
            self.assertEqual(code.count("endTransaction("), 1)
            self.assertTrue(
                "currentProgram.endTransaction(tx, commit);" in code)
            self.assertEqual(code.count("startTransaction("), 1)


class SemanticProofOnlyTests(unittest.TestCase):
    """"Nothing changed" is proven semantically, never by a file digest.

    Measured in developer_state `_MATERIAL_SAFETY_FINDING_20260817_NO_HEADLESS_
    ROLLBACK`: headless advances the database file version on any writable
    session, even when the post-script refuses and writes nothing.  A file-tree
    digest therefore cannot be the oracle, and neither the framework nor the
    replay harness may assert equality on one.
    """

    REPLAY = TOOLS / "ghidra_cohort_replay.py"

    def test_the_framework_never_reads_a_project_file_digest(self) -> None:
        code = code_only(BASE.read_text(encoding="utf-8"))
        for banned in ("Files.readAllBytes(Paths.get(state",
                       "getProjectDir().listFiles", "treeDigest",
                       "walkFileTree"):
            self.assertTrue(banned not in code, banned)

    def test_the_collateral_proof_is_a_semantic_census(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        for needed in ("frozenCensus()", "symbolCensus()", "bookmarkCensus()",
                       "definedDataCensus()", "memoryDigest()",
                       "preFrozen.keySet()"):
            self.assertTrue(needed in base, needed)

    def test_the_harness_never_asserts_tree_digest_equality(self) -> None:
        text = self.REPLAY.read_text(encoding="utf-8")
        code = code_only(text).replace("#", "\n#")
        for banned in ("assert digest ==", "digest == ", "treeDigest ==",
                       'cmp("treeDigest"'):
            self.assertTrue(banned not in code, banned)
        self.assertTrue("Provenance ONLY - never an oracle" in text)
        self.assertTrue('"isThisAnOracle": False' in text)

    def test_the_harness_refuses_to_write_into_a_protected_owner(self) -> None:
        text = self.REPLAY.read_text(encoding="utf-8")
        for needed in (r"C:\Users\david\Ghidra\Projects",
                       'REPO / "reverse-engineering" / "ghidra"',
                       'REPO / "local-lab" / "safe-copy-bea-pristine"',
                       "assert_write_allowed",
                       "REFUSING to write inside a protected owner"):
            self.assertTrue(needed in text, needed)


class CohortSpecTests(unittest.TestCase):
    """The three completed ceremonies, expressed as specs rather than programs."""

    def test_all_three_specs_exist(self) -> None:
        for spec in (BOUNDARY_SPEC, NAME_SPEC, ABI_SPEC):
            self.assertTrue(spec.exists(), spec)

    def test_every_spec_key_is_known_to_the_framework(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        block = base.split("KNOWN_SPEC_KEYS = new LinkedHashSet<>(Arrays.asList(", 1)[1]
        block = block.split("));", 1)[0]
        known = {t.strip().strip('",') for t in block.replace("\n", " ").split()}
        known = {t for t in known if t}
        for spec in (BOUNDARY_SPEC, NAME_SPEC, ABI_SPEC):
            for key in read_spec(spec):
                with self.subTest(spec=spec.name, key=key):
                    self.assertIn(key, known)

    def test_every_spec_pins_the_pristine_program_identity(self) -> None:
        for spec in (BOUNDARY_SPEC, NAME_SPEC, ABI_SPEC):
            s = read_spec(spec)
            with self.subTest(spec=spec.name):
                self.assertEqual(s["programSha256"], [PROGRAM_SHA256])
                self.assertEqual(s["programMd5"], ["3b456964020070efe696d2cc09464a55"])
                self.assertEqual(s["programName"], ["BEA.exe"])
                self.assertEqual(s["imageBase"], ["00400000"])
                self.assertEqual(s["language"], ["x86:LE:32:default"])
                self.assertEqual(s["compilerSpec"], ["windows"])

    def test_each_spec_declares_only_the_verbs_its_ceremony_used(self) -> None:
        self.assertEqual(
            read_spec(BOUNDARY_SPEC)["verb"],
            ["DISASSEMBLE_BOUNDED", "CLEAR_BOUNDED", "REMOVE_STALE_BOOKMARK",
             "SET_BODY"])
        self.assertEqual(read_spec(NAME_SPEC)["verb"], ["SET_NAME"])
        self.assertEqual(read_spec(ABI_SPEC)["verb"], ["SET_PROTOTYPE"])

    def test_the_name_spec_cannot_reach_a_body_or_a_signature(self) -> None:
        s = read_spec(NAME_SPEC)
        for forbidden in ("col.proposedRanges", "col.currentRanges",
                          "col.proposedSignature", "col.paramSpec",
                          "col.returnType"):
            self.assertNotIn(forbidden, s)

    def test_the_abi_spec_cannot_reach_a_name_or_a_body(self) -> None:
        s = read_spec(ABI_SPEC)
        for forbidden in ("col.proposedName", "col.currentName",
                          "col.proposedRanges", "col.currentRanges"):
            self.assertNotIn(forbidden, s)

    def test_the_boundary_spec_cannot_reach_a_name_or_a_signature(self) -> None:
        s = read_spec(BOUNDARY_SPEC)
        for forbidden in ("col.proposedName", "col.currentName",
                          "col.proposedSignature", "col.paramSpec"):
            self.assertNotIn(forbidden, s)

    def test_the_manifest_pins_match_the_manifests_on_disk(self) -> None:
        for spec, manifest in ((BOUNDARY_SPEC, BOUNDARY_MANIFEST),
                               (NAME_SPEC, NAME_MANIFEST),
                               (ABI_SPEC, ABI_MANIFEST)):
            if not manifest.exists():
                self.skipTest(f"{manifest} is not materialised in this clone")
            s = read_spec(spec)
            with self.subTest(spec=spec.name):
                self.assertEqual(s["manifestSha256"], [_sha256(manifest)])
                rows = [l for l in manifest.read_text(encoding="utf-8").split("\n")
                        if l]
                self.assertEqual(s["manifestRows"], [str(len(rows) - 1)])
                self.assertEqual(
                    s["manifestHeaderPipe"], ["|".join(rows[0].split("\t"))])
                self.assertEqual(
                    s["manifestColumns"], [str(len(rows[0].split("\t")))])

    def test_the_pins_reproduce_the_archived_ceremony_numbers(self) -> None:
        """These are the numbers the three completed receipts recorded."""
        b = read_spec(BOUNDARY_SPEC)
        self.assertEqual(b["preInstructions"], ["551143"])
        self.assertEqual(b["preReferences"], ["234478"])
        self.assertEqual(b["preBookmarks"], ["2303"])
        self.assertEqual(b["postInstructions"], ["551232"])
        self.assertEqual(b["postReferences"], ["234493"])
        self.assertEqual(b["postBookmarks"], ["2301"])
        self.assertEqual(b["manifestRows"], ["41"])
        self.assertEqual(b["expectedTargetsChanged"], ["41"])

        n = read_spec(NAME_SPEC)
        self.assertEqual(n["preInstructions"], ["551232"])
        self.assertEqual(n["preReferences"], ["234493"])
        self.assertEqual(n["manifestRows"], ["160"])
        self.assertEqual(n["expectedTargetsChanged"], ["158"])
        self.assertEqual(n["expectedSymbolsAdded"], ["160"])
        self.assertEqual(n["expectedSymbolsRemoved"], ["160"])

        a = read_spec(ABI_SPEC)
        self.assertEqual(a["manifestRows"], ["294"])
        self.assertEqual(a["expectedTargetsChanged"], ["294"])
        self.assertEqual(a["expectedFunctionsUntouched"], ["8035"])

    def test_the_abi_spec_keeps_the_no_go_hazards_out(self) -> None:
        a = read_spec(ABI_SPEC)
        self.assertIn("__return_storage_ptr__", a["forbidToken"])
        self.assertIn("__vectorcall", a["forbidToken"])
        self.assertIn("CONTRADICTS", a["forbidToken"])
        self.assertIn("confidence=HIGH", a["constant"])

    def test_the_name_spec_keeps_the_five_refuted_rows_out(self) -> None:
        if not NAME_MANIFEST.exists():
            self.skipTest("name manifest absent")
        addrs = {
            line.split("\t", 1)[0]
            for line in NAME_MANIFEST.read_text(encoding="utf-8").split("\n")[1:]
            if line
        }
        for refuted in ("0x0044ca30", "0x004dfa40", "0x004f07e0",
                        "0x00409ef0", "0x00409f20"):
            self.assertTrue(refuted not in addrs,
                            f"refuted row {refuted} shipped as a target")


class NegativeControlTests(unittest.TestCase):
    """The tests above must have teeth."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = BASE.read_text(encoding="utf-8")

    def test_a_weakened_pre_pin_would_be_caught(self) -> None:
        tampered = self.base.replace("PRE instruction count", "pre instr count")
        self.assertTrue(tampered != self.base)
        self.assertTrue(
            GATE_INVENTORY["p02-pre-instructions"][0] not in tampered)

    def test_a_deleted_collateral_gate_would_be_caught(self) -> None:
        tampered = self.base.replace(
            "DEFINED DATA CHANGED OUTSIDE the admitted ranges at", "")
        self.assertTrue(
            GATE_INVENTORY["l15-defined-data-outside-admitted"][0]
            not in tampered)

    def test_an_equals_to_contains_reversion_would_be_caught(self) -> None:
        live = LIVE.read_text(encoding="utf-8")
        tampered = live.replace("lower.equals(REQUIRED_LIVE_PROJECT_DIR)",
                                "lower.contains(REQUIRED_LIVE_PROJECT_DIR)")
        self.assertTrue(tampered != live)
        self.assertTrue("lower.contains(REQUIRED_LIVE_PROJECT_DIR)" in tampered)

    def test_a_smuggled_verb_would_be_caught(self) -> None:
        tampered = self.base.replace(
            "f.setVarArgs(false);", "f.setVarArgs(false);\n f.setComment(null);")
        self.assertTrue(".setComment(" in code_only(tampered))

    def test_a_rollback_claim_would_be_caught(self) -> None:
        tampered = self.base.replace(
            'j.append("  \\"committed\\": ")',
            'j.append("  \\"rolled-back\\": ")')
        self.assertTrue("rolled-back" in code_only(tampered))

    def test_symbol_source_is_unlocked_only_for_a_rename_cohort(self) -> None:
        """The one column the replay showed a rename must be allowed to move.

        The 2026-08-17 name applier never carried symbolSource in its shape
        census, so unlocking it for SET_NAME targets loses no gate.  The ABI
        applier DID freeze it, and that freeze must survive for every cohort
        that does not declare SET_NAME.
        """
        block = self.base.split("static Set<String> mutableColumnsFor(", 1)[1]
        block = block.split("\n    }", 1)[0]
        name_arm = block.split("verbs.contains(V_SET_NAME)", 1)[1]
        name_arm = name_arm.split("if (verbs.contains", 1)[0]
        self.assertTrue('out.add("symbolSource")' in name_arm)
        for other in ("V_SET_BODY", "V_SET_PROTOTYPE"):
            arm = block.split(f"verbs.contains({other})", 1)[1]
            arm = arm.split("if (verbs.contains", 1)[0]
            self.assertTrue('out.add("symbolSource")' not in arm, other)
        self.assertEqual(block.count('out.add("symbolSource")'), 1)

    def test_a_widened_mutable_column_set_would_be_caught(self) -> None:
        block = self.base.split("static Set<String> mutableColumnsFor(", 1)[1]
        block = block.split("\n    }", 1)[0]
        for banned in ('out.add("commentSha")', 'out.add("tags")',
                       'out.add("callingConvention")',
                       'out.add("namespace")'):
            self.assertTrue(banned not in block, banned)


class ReplayReceiptTests(unittest.TestCase):
    """If the reproduction lane has run, its receipts must match the archive."""

    LANE = REPO / "local-lab" / "ghidra-cohort-framework" / "receipts"

    ARCHIVED = {
        "boundary-cohort41": {
            "postInstructions": 551232,
            "postReferences": 234493,
            "postBookmarks": 2301,
            "postFunctions": 8329,
            "rows": 41,
        },
        "name-cohort160": {
            "postInstructions": 551232,
            "postReferences": 234493,
            "postBookmarks": 2301,
            "postFunctions": 8329,
            "rows": 160,
        },
        "abi-cohort294": {
            "postInstructions": 551232,
            "postReferences": 234493,
            "postBookmarks": 2301,
            "postFunctions": 8329,
            "rows": 294,
        },
    }

    def test_the_provoked_gate_matrix_refused_every_probe(self) -> None:
        """Presence of a refusal string is not proof that the gate fires.

        `ghidra_cohort_replay.py --probes all` breaks one input at a time on a
        scratch replica and requires the framework to refuse for that specific
        reason, including the five self-sabotage modes that only deliberate
        confinement-breaking can reach.
        """
        matrix = self.LANE / "probes" / "matrix.json"
        if not matrix.exists():
            self.skipTest("the provocation matrix has not been run")
        probes = json.loads(matrix.read_text(encoding="utf-8"))["probes"]
        self.assertGreaterEqual(len(probes), 10)
        not_refused = [p["probe"] for p in probes
                       if p["verdict"] != "REFUSED"]
        self.assertEqual(not_refused, [])
        applied = [p["probe"] for p in probes if p["appliedAnyway"]]
        self.assertEqual(applied, [], "a probe committed anyway")
        expectations = [p["expect"] for p in probes]
        self.assertEqual(len(set(expectations)), len(expectations),
                         "two probes graded against the same refusal message")

    def test_replayed_apply_receipts_match_the_archived_ceremonies(self) -> None:
        if not self.LANE.exists():
            self.skipTest("the reproduction lane has not been run in this clone")
        checked = 0
        for cohort, want in self.ARCHIVED.items():
            path = self.LANE / cohort / "apply.json"
            if not path.exists():
                continue
            got = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(cohort=cohort):
                self.assertEqual(got["result"], "PASS")
                self.assertEqual(got["cohortId"], cohort)
                self.assertTrue(got["committed"])
                self.assertEqual(
                    got["reversibility"],
                    "CEREMONY_LEVEL_RESTORE_FROM_VERIFIED_PRE_BACKUP")
                for key, value in want.items():
                    if key == "rows":
                        self.assertEqual(got["counts"]["rows"], value)
                    else:
                        self.assertEqual(got["counts"][key], value, key)
            checked += 1
        if checked == 0:
            self.skipTest("no replay receipts present")


def _emit_live() -> int:
    text = derive_live(BASE.read_text(encoding="utf-8"))
    LIVE.write_text(text, encoding="utf-8", newline="")
    print(f"wrote {LIVE} ({len(text.encode('utf-8'))} bytes, "
          f"sha256 {hashlib.sha256(text.encode('utf-8')).hexdigest()})")
    return 0


if __name__ == "__main__":
    if "--emit-live" in sys.argv:
        raise SystemExit(_emit_live())
    unittest.main(verbosity=2)
