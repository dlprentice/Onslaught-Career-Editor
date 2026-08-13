#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import re_cexplosion_factory_identity_reproof as proof


SPECIMEN = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe.original.backup")


class CExplosionFactoryIdentityReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = SPECIMEN.read_bytes()
        cls.image = proof.PeImage(cls.raw)

    def test_body_contract(self) -> None:
        result = proof.verify_body(self.image)
        self.assertEqual(152, result["bytes"])
        self.assertEqual(39, result["instructions"])
        self.assertEqual(["0x005e4454", "0x005e43dc"], result["vtables"])

    def test_direct_call_and_cleanup_contract(self) -> None:
        rows, summary = proof.verify_calls(self.image)
        self.assertEqual(24, len(rows))
        self.assertEqual(22, summary["fourByteDedicatedCallerCleanups"])
        self.assertEqual(2, summary["eightByteCombinedTwoCallCleanups"])
        self.assertEqual(2, summary["resolverResultFlows"])

    def test_body_poison_is_rejected(self) -> None:
        raw = bytearray(self.raw)
        offset = self.image.offset(0x0050FF77)
        raw[offset] ^= 1
        poisoned = proof.PeImage(bytes(raw))
        with self.assertRaisesRegex(proof.ReproofError, "body SHA-256 differs"):
            proof.verify_body(poisoned)

    def test_call_poison_is_rejected(self) -> None:
        raw = bytearray(self.raw)
        offset = self.image.offset(proof.EXPECTED_CALLS[0])
        raw[offset] = 0x90
        poisoned = proof.PeImage(bytes(raw))
        with self.assertRaisesRegex(proof.ReproofError, "direct-call census differs"):
            proof.verify_calls(poisoned)

    def test_trailing_pad_poison_is_rejected(self) -> None:
        raw = bytearray(self.raw)
        raw[self.image.offset(proof.END_EXCLUSIVE)] = 0xCC
        poisoned = proof.PeImage(bytes(raw))
        with self.assertRaisesRegex(proof.ReproofError, "alignment pad differs"):
            proof.verify_body(poisoned)

    def test_hash_bound_reader_rejects_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.bin"
            path.write_bytes(b"wrong")
            with self.assertRaisesRegex(proof.ReproofError, "SHA-256 differs"):
                proof.read_bound(path, hashlib.sha256(b"right").hexdigest())

    @staticmethod
    def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, delimiter="\t", fieldnames=list(rows[0]),
                                    lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def inspection_fixture(self, directory: Path, parameter_source: str) -> dict[str, str]:
        comment = b"x" * 512
        (directory / "pre-comment.txt").write_bytes(comment)
        tags = ("comment-hardened,factory,pickup,retail-binary-evidence,signature-corrected,"
                "signature-recovered,static-reaudit,world-physics-manager,"
                "worldphysics-factory-tail-wave558")
        target = {
            "address": "0x0050ff10", "name": "CWorldPhysicsManager__CreatePickup",
            "fqname": "CWorldPhysicsManager__CreatePickup", "namespace": "Global",
            "nameSource": "USER_DEFINED", "signatureSource": "USER_DEFINED",
            "callingConvention": "__cdecl", "returnType": "void *", "returnStorage": "EAX:4",
            "parameterCount": "1", "parameterName": "pickup_type", "parameterType": "int",
            "parameterStorage": "Stack[0x4]:4", "parameterSource": parameter_source,
            "stackParameterBytes": "4", "customStorage": "false", "varArgs": "false",
            "inline": "false", "noReturn": "false", "isThunk": "false", "thunkTarget": "",
            "bodyRanges": "0x0050ff10-0x0050ffa7", "bodyBytes": "152",
            "bodyRangeSha256": proof.BODY_RANGE_SHA256, "bodyBytesSha256": proof.BODY_SHA256,
            "instructionCount": "39", "commentBytes": str(len(comment)),
            "commentSha256": hashlib.sha256(comment).hexdigest(), "repeatableCommentBytes": "0",
            "tags": tags,
        }
        self.write_tsv(directory / "target.tsv", [target])
        incoming = [{"toAddress": "0x0050ff10", "fromInTargetBody": "false",
                     "fromAddress": f"0x{call:08x}", "referenceType": "UNCONDITIONAL_CALL"}
                    for call in proof.EXPECTED_CALLS]
        self.write_tsv(directory / "incoming.tsv", incoming)
        self.write_tsv(directory / "symbols.tsv", [{"namespace": "Global", "type": "Function",
                       "source": "USER_DEFINED", "primary": "true"}])
        self.write_tsv(directory / "name-census.tsv", [{"query": "CWorldPhysicsManager__CreatePickup"}])
        self.write_tsv(directory / "outgoing.tsv", [
            {"fromAddress": "0x0050ff4f", "toAddress": "0x005490e0", "referenceType": "UNCONDITIONAL_CALL"},
            {"fromAddress": "0x0050ff68", "toAddress": "0x004f3e10", "referenceType": "UNCONDITIONAL_CALL"},
            {"fromAddress": "0x0050ff77", "toAddress": "0x005e4454", "referenceType": "DATA"},
            {"fromAddress": "0x0050ff7d", "toAddress": "0x005e43dc", "referenceType": "DATA"},
        ])
        for name in ("functions.tsv", "instructions.tsv", "program.tsv", "summary.tsv"):
            (directory / name).write_text("fixture\n", encoding="utf-8", newline="\n")
        return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in proof.EXPECTED_INSPECTION_HASHES}

    def test_inspection_accepts_exact_user_defined_parameter_source(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            hashes = self.inspection_fixture(directory, "USER_DEFINED")
            with patch.object(proof, "EXPECTED_INSPECTION_HASHES", hashes):
                result = proof.verify_inspection(directory)
            self.assertEqual(result["parameterSource"], "USER_DEFINED")

    def test_inspection_rejects_parameter_source_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            hashes = self.inspection_fixture(directory, "DEFAULT")
            with patch.object(proof, "EXPECTED_INSPECTION_HASHES", hashes):
                with self.assertRaisesRegex(proof.ReproofError, "parameterSource differs"):
                    proof.verify_inspection(directory)


if __name__ == "__main__":
    unittest.main()
