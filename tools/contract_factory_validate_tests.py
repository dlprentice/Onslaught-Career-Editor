#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-tests for contract_factory_validate.py.

The defect this gate closes is a factory contract file that LOOKS complete
but is not: a silently dropped mandatory section, an invented FUN_* name, a
VA that collides with another file's, a digest that does not parse, or an
evidence path to something the repo does not contain. Each falsification
below builds a minimal contract tree, breaks exactly one honesty property at
a time, and asserts the validator refuses it — plus pass cases asserting a
fully honest contract is accepted (including CRLF/BOM/Unicode variants), and
determinism/exit-code contracts on the runner itself.

Run: py -3 tools/contract_factory_validate_tests.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "contract_factory_validate.py"

PRISTINE = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

# A real tracked file the default Evidence fixture cites; the synthetic repo
# scaffold below materializes it so existence checks behave like the live repo.
CLOSURE_TSV = "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv"


def run_tool(root: Path, *extra: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(root), "--repo-root", str(root), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def w(root: Path, rel: str, data: bytes | str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
    return p


def make_contract(
    va: str = "0x00404dd0",
    name: str = "CBattleEngine__Init",
    *,
    body_digest: str | None = "fc848420034efff85366537255817ba9888fab2c6a736cba271cd2ad845a6c13",
    image_sha: str | None = PRISTINE,
    confidence: str = "3 - clear from decompile; runtime corroborates execution",
    unresolved: str = "exact unit of arg2 unknown",
    evidence: str = (
        "- Closure row `" + CLOSURE_TSV + "` (C1_CANDIDATE_PARTIAL)."
    ),
) -> str:
    """A fully honest, structurally valid factory draft."""
    binary_part = f"Binary: BEA.exe, SHA-256 `{image_sha}`" if image_sha else "Binary: BEA.exe"
    digest_line = (
        f"- Body `[0x00404dd0,0x00405a01]`, 2858 bytes, SHA-256 `{body_digest}` "
        "(pristine specimen 74154bfa…; packet image hash matches)."
        if body_digest else ""
    )
    return f"""# {name}

Status: active static contract (factory draft)
Last updated: 2026-08-22
Source File: `references/Onslaught/BattleEngine.cpp` | {binary_part}

> Address: `{va}`

## Identity
{digest_line}
- Name provenance: Ghidra tracked table label, counted not recovered.

## Calling convention
thiscall; ECX carries this; no stack arguments visible in packet signature.

## Prototype and parameter semantics
```c
int __thiscall {name}(void *this);
```
No parameters beyond this; meaning of return as far as evidence shows below.

## Return value meaning
unknown - decompile shows int but no branch keys on the value.

## Globals read/written
not_applicable

## Callees relied on / callers
Callee: sub_00405a40 at 0x00405a40; inbound caller 0x00403d20.

## Behavior summary
Initialize engine state per packet decompile lines 12-40; early return when
already initialized.

## Error / edge behavior
Early return path when already initialized; otherwise full init sequence.

## Runtime corroboration (TTD, bounded)
Session all level-openings: invariant across 66 openings (bounded captures only).

## Evidence
{evidence}

## Confidence
{confidence}

## Unresolved questions
{unresolved}
"""


def make_repo(root: Path) -> None:
    """Minimal repo surface the fixture Evidence cites."""
    w(root, CLOSURE_TSV, "# closure\tva\tgrade\n")


class FactoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        make_repo(self.root)

    # -- helpers ---------------------------------------------------------

    def write_pass(self) -> Path:
        return w(self.root, "drafts/battleengine/CBattleEngine__Init__00404dd0.md",
                 make_contract())

    def write_bad(self, rel_dir: str = "d", **kwargs) -> Path:
        """Write one contract under a stem that always matches its own
        name/VA identity, so only the property under test can fire."""
        name = kwargs.get("name", "CBattleEngine__Init")
        va = kwargs.get("va", "0x00404dd0")
        hex8 = va.lower().removeprefix("0x").lstrip("0").zfill(8)
        return w(self.root, f"{rel_dir}/{name}__{hex8}.md",
                 make_contract(va=va, name=name, **{
                     k: v for k, v in kwargs.items() if k not in ("name", "va")}))

    def violations(self, code: str) -> list[str]:
        rc, out = run_tool(self.root)
        self.assertNotEqual(0, rc, f"expected nonzero exit for {code}; output:\n{out}")
        hits = [ln for ln in out.splitlines() if f"[{code}]" in ln]
        self.assertTrue(hits, f"no [{code}] diagnostic in output:\n{out}")
        return hits

    # -- pass cases -------------------------------------------------------

    def test_honest_contract_passes_with_zero_violations(self) -> None:
        self.write_pass()
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc, out)
        self.assertIn("OK", out)
        self.assertIn("1 file(s)", out)

    def test_alias_heading_satisfies_globals_requirement(self) -> None:
        # The brief's own heading wording must satisfy the gate (no false positive).
        w(self.root, "d/GlobalAlias__00404dd0.md",
          make_contract(name="GlobalAlias").replace(
              "## Globals read/written\nnot_applicable",
              "## Globally referenced data\nnot_applicable"))
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc, out)

    def test_crlf_and_bom_are_handled_identically(self) -> None:
        crlf = make_contract().replace("\n", "\r\n")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", crlf)
        bom_crlf = b"\xef\xbb\xbf" + make_contract(
            name="CBattleEngine__InitB", va="0x00405a40",
        ).replace("\n", "\r\n").encode("utf-8")
        w(self.root, "d/CBattleEngine__InitB__00405a40.md", bom_crlf)
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc, out)

    def test_unicode_dash_and_typographic_characters_do_not_break_parsing(self) -> None:
        w(self.root, "d/UnicodeDash__00404dd0.md",
          make_contract(name="UnicodeDash",
                        confidence="3 — en dash justification"))
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc, out)

    def test_tracked_name_ending_in_va_keeps_full_name_then_appends_va(self) -> None:
        name = "CBattleEngine__VFunc_7_00405ed0"
        w(self.root, f"d/{name}__00405ed0.md",
          make_contract(name=name, va="0x00405ed0"))
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc, out)

    # -- fail-closed classes ---------------------------------------------

    def test_missing_mandatory_section_fails_closed(self) -> None:
        self.write_bad().unlink()
        w(self.root, "d/CBattleEngine__Init__00404dd0.md",
          make_contract().replace("## Return value meaning\n", ""))
        self.violations("MISSING_SECTION")

    def test_missing_title_fails_closed(self) -> None:
        w(self.root, "d/CBattleEngine__Init__00404dd0.md",
          make_contract().replace("# CBattleEngine__Init", "Contract draft", 1))
        self.violations("MISSING_TITLE")

    def test_duplicate_title_fails_closed(self) -> None:
        text = make_contract().replace(
            "# CBattleEngine__Init", "# CBattleEngine__Init\n# OtherName", 1)
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("DUPLICATE_TITLE")

    def test_duplicate_title_with_tab_markdown_spacing_fails(self) -> None:
        text = make_contract().replace(
            "# CBattleEngine__Init", "# CBattleEngine__Init\n#\tOtherName", 1)
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("DUPLICATE_TITLE")

    def test_missing_address_fails_closed(self) -> None:
        w(self.root, "d/CBattleEngine__Init__00404dd0.md",
          make_contract().replace("> Address: `0x00404dd0`\n", ""))
        self.violations("MISSING_ADDRESS")

    def test_duplicate_address_fails_closed(self) -> None:
        text = make_contract().replace(
            "> Address: `0x00404dd0`",
            "> Address: `0x00404dd0`\n> Address: `0x00405a40`")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("DUPLICATE_ADDRESS")

    def test_duplicate_address_with_markdown_indentation_fails(self) -> None:
        text = make_contract().replace(
            "> Address: `0x00404dd0`",
            "> Address: `0x00404dd0`\n > Address: `0x00405a40`")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("DUPLICATE_ADDRESS")

    def test_malformed_address_fails_closed(self) -> None:
        w(self.root, "d/CBattleEngine__Init__00404dd0.md",
          make_contract().replace("`0x00404dd0`", "`not-a-va`", 1))
        self.violations("BAD_ADDRESS")

    def test_empty_mandatory_section_without_content_fails(self) -> None:
        self.write_bad(body_digest=None)
        text = make_contract(body_digest=None).replace(
            "unknown - decompile shows int but no branch keys on the value.", "")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        hits = self.violations("EMPTY_SECTION")
        self.assertIn("Return value meaning", hits[0])

    def test_va_filename_identity_mismatch_fails(self) -> None:
        # Filename pins <name>__<hex8>; the body's Address block must agree.
        w(self.root, "drafts/x/CBattleEngine__Init__00404dd0.md",
          make_contract(va="0x00405fff"))
        hits = self.violations("VA_STEM_MISMATCH")
        self.assertIn("00404dd0", hits[0])

    def test_name_filename_identity_mismatch_fails(self) -> None:
        w(self.root, "drafts/x/CBattleEngine__Init__00404dd0.md",
          make_contract(name="CBattleEngine__Other"))
        hits = self.violations("NAME_STEM_MISMATCH")
        self.assertIn("CBattleEngine__Init", hits[0])

    def test_noncanonical_address_text_normalizes_before_identity(self) -> None:
        # Same VA value in odd casing/padding must still collide with the
        # pass fixture, while the noncanonical spelling is independently
        # rejected: identity is the NORMALIZED VA, not the raw text.
        self.write_pass()
        twin = make_contract(name="OtherName").replace(
            "> Address: `0x00404dd0`", "> Address: `0X00404DD0`")
        w(self.root, "d/OtherName__00404dd0.md", twin)
        rc, out = run_tool(self.root)
        self.assertNotEqual(0, rc, out)
        self.assertIn("[NONCANONICAL_ADDRESS]", out)
        self.assertIn("[DUPLICATE_VA]", out)
        self.assertIn("OtherName__00404dd0.md", out)

    def test_forbidden_anonymous_fun_name_in_title_fails(self) -> None:
        w(self.root, "d/FUN_00405ed0__00405ed0.md", make_contract(name="FUN_00405ed0"))
        self.violations("ANONYMOUS_NAME")

    def test_forbidden_anonymous_fun_prefix_variant_fails(self) -> None:
        name = "FUN_00405ed0_extra"
        w(self.root, f"d/{name}__00405ed0.md",
          make_contract(name=name, va="0x00405ed0"))
        self.violations("ANONYMOUS_NAME")

    def test_forbidden_anonymous_fun_name_is_case_insensitive(self) -> None:
        name = "fun_00405ed0"
        w(self.root, f"d/{name}__00405ed0.md",
          make_contract(name=name, va="0x00405ed0"))
        self.violations("ANONYMOUS_NAME")

    def test_forbidden_anonymous_fun_name_with_prefix_underscore_fails(self) -> None:
        name = "_FUN_00405ed0"
        w(self.root, f"d/{name}__00405ed0.md",
          make_contract(name=name, va="0x00405ed0"))
        self.violations("ANONYMOUS_NAME")

    def test_two_files_colliding_on_one_va_fail(self) -> None:
        self.write_pass()
        w(self.root, "drafts/battleengine/CBattleEngine__InitDup__00404dd0.md",
          make_contract(name="CBattleEngine__InitDup"))
        self.violations("DUPLICATE_VA")

    def test_duplicate_tracked_name_across_files_fails(self) -> None:
        self.write_pass()
        w(self.root, "d/CBattleEngine__Init__00405a40.md",
          make_contract(va="0x00405a40"))
        self.violations("DUPLICATE_NAME")

    def test_duplicate_required_section_fails(self) -> None:
        w(self.root, "d/CBattleEngine__Init__00404dd0.md",
          make_contract() + "\n## Return value meaning\nunknown\n")
        self.violations("DUPLICATE_SECTION")

    def test_required_sections_inside_tilde_fence_do_not_count(self) -> None:
        text = make_contract().replace("## Identity", "~~~~\n## Identity", 1)
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text + "\n~~~~\n")
        self.violations("MISSING_SECTION")

    def test_filename_cannot_consume_va_suffix_from_full_tracked_name(self) -> None:
        name = "CBattleEngine__VFunc_7_00405ed0"
        w(self.root, "d/CBattleEngine__VFunc_7_00405ed0.md",
          make_contract(name=name, va="0x00405ed0"))
        hits = self.violations("BAD_STEM")
        self.assertIn("CBattleEngine__VFunc_7_00405ed0", hits[0])

    def test_evidence_path_to_nonexistent_repo_file_fails(self) -> None:
        self.write_bad(evidence="- Closure row `reverse-engineering/no-such-file-here.tsv`.")
        self.violations("EVIDENCE_PATH_MISSING")

    def test_missing_repo_path_under_unrecognized_top_level_fails(self) -> None:
        self.write_bad(evidence="- Claimed repo path `docs/definitely-missing.md`.")
        self.violations("EVIDENCE_PATH_MISSING")

    def test_missing_repo_root_file_fails(self) -> None:
        self.write_bad(evidence="- Claimed repo file `DOES-NOT-EXIST.md`.")
        self.violations("EVIDENCE_PATH_MISSING")

    def test_missing_repo_path_with_spaces_fails(self) -> None:
        self.write_bad(evidence="- Claimed repo path `docs/does not exist.md`.")
        self.violations("EVIDENCE_PATH_MISSING")

    def test_evidence_path_cannot_escape_repo_root(self) -> None:
        outside_name = f"{self.root.name}-outside-evidence.tsv"
        outside = self.root.parent / outside_name
        outside.write_text("not repository evidence\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        self.write_bad(
            evidence=f"- Claimed row `reverse-engineering/../../{outside_name}`.")
        self.violations("EVIDENCE_PATH_OUTSIDE_REPO")

    def test_submodule_exemption_cannot_hide_parent_traversal(self) -> None:
        w(self.root, ".gitmodules", """[submodule "references/Onslaught"]
\tpath = references/Onslaught
\turl = https://example.invalid/Onslaught.git
""")
        self.write_bad(
            evidence="- Claimed path `references/Onslaught/../../DOES-NOT-EXIST.md`.")
        self.violations("EVIDENCE_PATH_OUTSIDE_REPO")

    def test_bad_body_digest_syntax_fails(self) -> None:
        self.write_bad(body_digest="deadbeef")
        self.violations("BAD_DIGEST")

    def test_missing_body_digest_fails(self) -> None:
        self.write_bad(body_digest=None)
        self.violations("MISSING_BODY_DIGEST")

    def test_unlabeled_hex_token_is_not_a_body_digest_claim(self) -> None:
        digest = "fc848420034efff85366537255817ba9888fab2c6a736cba271cd2ad845a6c13"
        text = make_contract(body_digest=None).replace(
            "- Name provenance: Ghidra tracked table label, counted not recovered.",
            f"- Unlabeled token `{digest}`.\n"
            "- Name provenance: Ghidra tracked table label, counted not recovered.")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_BODY_DIGEST")

    def test_non_body_sha_label_is_not_a_body_digest_claim(self) -> None:
        digest = "fc848420034efff85366537255817ba9888fab2c6a736cba271cd2ad845a6c13"
        text = make_contract(body_digest=None).replace(
            "- Name provenance: Ghidra tracked table label, counted not recovered.",
            f"- Packet SHA-256 `{digest}`.\n"
            "- Name provenance: Ghidra tracked table label, counted not recovered.")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_BODY_DIGEST")

    def test_uppercase_body_digest_fails(self) -> None:
        self.write_bad(body_digest="FC848420034EFFF85366537255817BA9888FAB2C6A736CBA271CD2AD845A6C13")
        self.violations("BAD_DIGEST")

    def test_wrong_pristine_image_sha_fails(self) -> None:
        self.write_bad(image_sha="f" * 64)
        self.violations("IMAGE_SHA_MISMATCH")

    def test_pristine_hash_outside_binary_header_does_not_satisfy_image_identity(self) -> None:
        text = make_contract(image_sha=None, evidence=f"- Unlabeled image token `{PRISTINE}`.")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_IMAGE_DIGEST")

    def test_binary_image_claim_inside_evidence_is_not_a_header(self) -> None:
        text = make_contract(
            image_sha=None,
            evidence=f"- Binary: BEA.exe, SHA-256 `{PRISTINE}`.")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_IMAGE_DIGEST")

    def test_source_file_image_claim_inside_evidence_is_not_a_header(self) -> None:
        text = make_contract(
            image_sha=None,
            evidence=f"Source File: `fake` | Binary: BEA.exe, SHA-256 `{PRISTINE}`")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_IMAGE_DIGEST")

    def test_evidence_image_claim_before_address_is_not_a_header(self) -> None:
        fake = f"Source File: `fake` | Binary: BEA.exe, SHA-256 `{PRISTINE}`"
        text = make_contract(image_sha=None).replace(
            "> Address: `0x00404dd0`", f"## Evidence\n{fake}\n\n> Address: `0x00404dd0`", 1)
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", text)
        self.violations("MISSING_IMAGE_DIGEST")

    def test_confidence_out_of_range_fails(self) -> None:
        self.write_bad(confidence="5 - overconfident")
        self.violations("BAD_CONFIDENCE")

    def test_confidence_without_scale_justification_fails(self) -> None:
        self.write_bad(confidence="high confidence")
        expected_line = make_contract(confidence="high confidence").splitlines().index(
            "high confidence") + 1
        hits = self.violations("BAD_CONFIDENCE")
        self.assertIn(f": {expected_line}: [BAD_CONFIDENCE]", hits[0])

    def test_tbd_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="TBD")
        self.violations("PLACEHOLDER_SECTION")

    def test_bulleted_tbd_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="- TBD")
        self.violations("PLACEHOLDER_SECTION")

    def test_nested_bulleted_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="- - TBD")
        self.violations("PLACEHOLDER_SECTION")

    def test_ordered_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="1. TBD")
        self.violations("PLACEHOLDER_SECTION")

    def test_blockquoted_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="> TBD")
        self.violations("PLACEHOLDER_SECTION")

    def test_multiple_placeholder_lines_fail(self) -> None:
        self.write_bad(unresolved="TBD\nTODO")
        self.violations("PLACEHOLDER_SECTION")

    def test_fenced_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="```text\nTBD\n```")
        self.violations("PLACEHOLDER_SECTION")

    def test_todo_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="TODO")
        self.violations("PLACEHOLDER_SECTION")

    def test_dash_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="-")
        self.violations("PLACEHOLDER_SECTION")

    def test_na_placeholder_only_section_fails(self) -> None:
        self.write_bad(unresolved="N/A")
        self.violations("PLACEHOLDER_SECTION")

    def test_unresolved_questions_without_content_or_note_fails(self) -> None:
        self.write_bad(unresolved="")
        self.violations("EMPTY_SECTION")

    def test_whitespace_only_section_lines_are_rejected(self) -> None:
        self.write_bad(unresolved="   ")
        self.violations("EMPTY_SECTION")

    def test_invalid_utf8_fails_closed_not_crash(self) -> None:
        p = self.write_bad()
        p.write_bytes(p.read_bytes() + b"\xff\xfe garbage")
        rc, out = run_tool(self.root)
        self.assertNotEqual(0, rc, out)
        self.assertIn("[DECODE_ERROR]", out)

    # -- runner contracts --------------------------------------------------

    def test_exit_codes_and_summary_shape(self) -> None:
        self.write_pass()
        rc, out = run_tool(self.root)
        self.assertEqual(0, rc)
        self.assertIn("OK", out)

        empty = self.root / "empty-tree"
        empty.mkdir()
        rc, out = run_tool(empty)
        self.assertEqual(2, rc, out)
        self.assertIn("no .md files", out)

        missing = self.root / "does-not-exist"
        rc, out = run_tool(missing)
        self.assertEqual(2, rc, out)

    def test_diagnostic_output_is_byte_deterministic_across_runs(self) -> None:
        first_file = make_contract(body_digest="tooshort")
        w(self.root, "d/CBattleEngine__Init__00404dd0.md", first_file)
        second_file = make_contract(
            va="0x00409999", name="Zed__One",
            body_digest="ee66d0337f44ef3821a545793446cccd8d666f77ad8528c2997651ba7897202f",
            unresolved="",
        )
        w(self.root, "d/Zed__One__00409999.md", second_file)
        first = run_tool(self.root)
        second = run_tool(self.root)
        self.assertEqual(first, second)
        self.assertNotEqual(0, first[0])
        # Sorted by path: d/CBattleEngine… diagnostics come before d/Zed….md ones.
        a_at = first[1].index("__00404dd0.md:")
        z_at = first[1].index("__00409999.md:")
        self.assertLess(a_at, z_at)

    def test_diagnostics_use_root_relative_posix_paths(self) -> None:
        self.write_bad(body_digest="tooshort")
        rc, out = run_tool(self.root)
        self.assertNotEqual(0, rc, out)
        self.assertIn("d/CBattleEngine__Init__00404dd0.md:", out)
        self.assertNotIn(str(self.root), out)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
