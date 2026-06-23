#!/usr/bin/env python3
"""Focused tests for repo_line_endings_check.py."""

from __future__ import annotations

import unittest

import repo_line_endings_check as check


class RepoLineEndingsCheckTests(unittest.TestCase):
    def test_classifies_line_endings(self) -> None:
        self.assertEqual("none", check.classify_line_endings(b"abc"))
        self.assertEqual("lf", check.classify_line_endings(b"abc\nnext\n"))
        self.assertEqual("crlf", check.classify_line_endings(b"abc\r\nnext\r\n"))
        self.assertEqual("mixed", check.classify_line_endings(b"abc\r\nnext\n"))
        self.assertEqual("mixed", check.classify_line_endings(b"abc\rnext\r\n"))

    def test_normalizes_line_endings(self) -> None:
        data = b"one\r\ntwo\nthree\rfour"

        self.assertEqual(b"one\ntwo\nthree\nfour", check.normalize_line_endings(data, "lf"))
        self.assertEqual(b"one\r\ntwo\r\nthree\r\nfour", check.normalize_line_endings(data, "crlf"))

    def test_extracts_explicit_eol_entries(self) -> None:
        lf_line = "i/lf    w/mixed attr/text eol=lf      \tREADME.MD"
        crlf_line = "i/lf    w/crlf  attr/text eol=crlf    \tgame/cardid.txt"
        auto_line = "i/-text w/-text attr/text=auto         \tgame/data/Dial.raw"

        self.assertEqual(check.EolEntry("README.MD", "lf"), check.expected_from_eol_line(lf_line))
        self.assertEqual(check.EolEntry("game/cardid.txt", "crlf"), check.expected_from_eol_line(crlf_line))
        self.assertIsNone(check.expected_from_eol_line(auto_line))


if __name__ == "__main__":
    unittest.main(verbosity=2)
