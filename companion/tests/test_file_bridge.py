"""Owned real-fixture protocol checks for the companion's protected I/O boundary."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
BRIDGE: Path | None = None
RACE_HARNESS: Path | None = None
RUN_ROOT: Path | None = None
FIXTURE = REPO / "tests_shared/fixtures/gold_career_save.bin"


class FileBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if BRIDGE is None or RUN_ROOT is None:
            raise unittest.SkipTest("Pass --bridge or set ONSLAUGHT_FILE_BRIDGE.")
        cls.original = FIXTURE.read_bytes()
        assert len(cls.original) == 10004
        cls.fixture_hash = hashlib.sha256(cls.original).hexdigest()

    def setUp(self) -> None:
        assert RUN_ROOT is not None
        self.root = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=RUN_ROOT))
        self.input = self.root / "original.bes"
        shutil.copyfile(FIXTURE, self.input)
        self.output_dir = self.root / "output"
        self.output_dir.mkdir()
        self.output = self.output_dir / "copy.bes"

    def tearDown(self) -> None:
        self.assertEqual(self.fixture_hash, hashlib.sha256(FIXTURE.read_bytes()).hexdigest())

    def call_raw(self, raw: str) -> tuple[int, dict]:
        assert BRIDGE is not None
        result = subprocess.run([str(BRIDGE)], input=raw, text=True,
                                capture_output=True, timeout=15, check=False)
        self.assertEqual("", result.stderr, result.stderr)
        self.assertEqual(1, len(result.stdout.splitlines()), result.stdout)
        response = json.loads(result.stdout)
        self.assertEqual(1, response["protocol"])
        return result.returncode, response

    def call(self, request: dict) -> tuple[int, dict]:
        return self.call_raw(json.dumps(request) + "\n")

    def open(self, path: Path | None = None) -> dict:
        code, response = self.call({"protocol": 1, "op": "open", "input": str(path or self.input)})
        self.assertEqual(0, code, response)
        self.assertTrue(response["ok"], response)
        return response

    def publish_request(self, snapshot: dict, prepared: bytes | None = None) -> dict:
        return {"protocol": 1, "op": "publish", "input": str(self.input),
                "identity": snapshot["identity"], "sha256": snapshot["sha256"],
                "output": str(self.output),
                "bytes": base64.b64encode(self.original if prepared is None else prepared).decode("ascii")}

    def refuse(self, request: dict) -> dict:
        code, response = self.call(request)
        self.assertNotEqual(0, code, response)
        self.assertFalse(response["ok"], response)
        self.assertFalse(response["may_have_output"], response)
        return response

    def test_open_owns_exact_bytes_and_physical_identity(self) -> None:
        snapshot = self.open()
        self.assertEqual(self.original, base64.b64decode(snapshot["bytes"]))
        self.assertEqual(self.fixture_hash.upper(), snapshot["sha256"])
        self.assertEqual(10004, snapshot["size"])
        self.assertTrue(snapshot["identity"])
        self.assertEqual(self.original, self.input.read_bytes())

    def test_byte_for_byte_round_trip_and_reopen(self) -> None:
        snapshot = self.open()
        code, result = self.call(self.publish_request(snapshot))
        self.assertEqual(0, code, result)
        self.assertTrue(result["original_verified"])
        self.assertTrue(result["verified"])
        reopened = self.open(self.output)
        self.assertEqual(self.original, base64.b64decode(reopened["bytes"]))
        self.assertNotEqual(snapshot["identity"], reopened["identity"])
        self.assertEqual([self.output], list(self.output_dir.iterdir()))
        self.assertEqual(self.original, self.input.read_bytes())

    def test_prepared_edit_preserves_all_unselected_and_unknown_bytes(self) -> None:
        snapshot = self.open()
        prepared = bytearray(self.original)
        # Independent literal layout oracle, deliberately not a call to the UI codec.
        start = 0x23F6 + 4 * 4
        prepared[start:start + 3] = (123456).to_bytes(3, "little")
        code, result = self.call(self.publish_request(snapshot, bytes(prepared)))
        self.assertEqual(0, code, result)
        actual = self.output.read_bytes()
        self.assertEqual(10004, len(actual))
        self.assertEqual(123456, int.from_bytes(actual[start:start + 3], "little"))
        self.assertEqual(self.original[:start], actual[:start])
        self.assertEqual(self.original[start + 3:], actual[start + 3:])
        self.assertEqual(bytes(prepared), base64.b64decode(result["bytes"]))
        self.assertEqual(hashlib.sha256(actual).hexdigest().upper(), result["sha256"])
        self.assertEqual(self.original, self.input.read_bytes())

    def test_same_bytes_new_source_identity_refused(self) -> None:
        snapshot = self.open()
        self.input.rename(self.root / "old.bes")
        shutil.copyfile(FIXTURE, self.input)
        self.refuse(self.publish_request(snapshot))
        self.assertFalse(self.output.exists())

    def test_changed_source_bytes_refused(self) -> None:
        snapshot = self.open()
        changed = bytearray(self.original)
        changed[-1] ^= 1
        self.input.write_bytes(changed)
        self.refuse(self.publish_request(snapshot))
        self.assertEqual(bytes(changed), self.input.read_bytes())
        self.assertEqual([], list(self.output_dir.iterdir()))

    def test_existing_destination_preserved(self) -> None:
        snapshot = self.open()
        self.output.write_bytes(self.original)
        self.refuse(self.publish_request(snapshot))
        self.assertEqual(self.original, self.output.read_bytes())
        self.assertEqual(self.original, self.input.read_bytes())

    def test_input_cannot_be_the_destination(self) -> None:
        request = self.publish_request(self.open())
        request["output"] = str(self.input)
        self.refuse(request)
        self.assertEqual(self.original, self.input.read_bytes())

    def test_missing_destination_directory_not_created(self) -> None:
        request = self.publish_request(self.open())
        request["output"] = str(self.root / "absent" / "copy.bes")
        self.refuse(request)
        self.assertFalse((self.root / "absent").exists())

    def test_game_tree_destination_refused(self) -> None:
        snapshot = self.open()
        (self.output_dir / "BEA.exe").write_bytes(b"owned test marker, not an executable")
        (self.output_dir / "data").mkdir()
        self.refuse(self.publish_request(snapshot))
        self.assertFalse(self.output.exists())

    def test_wrong_length_source_refused(self) -> None:
        self.input.write_bytes(self.original[:-1])
        self.refuse({"protocol": 1, "op": "open", "input": str(self.input)})

    def test_malformed_protocol_refused_without_writes(self) -> None:
        requests = ["", "not json\n", "[]\n", '{"protocol":true}\n',
                    '{"protocol":"1"}\n', '{"protocol":2}\n',
                    '{"protocol":1,"protocol":1,"op":"open","input":"/x.bes"}\n',
                    '{"protocol":1,"op":"delete"}\n', "x" * 65537 + "\n"]
        for raw in requests:
            with self.subTest(raw=raw[:80]):
                code, response = self.call_raw(raw)
                self.assertEqual(2, code, response)
                self.assertFalse(response["ok"])
        self.assertEqual(self.original, self.input.read_bytes())

    def test_bad_paths_and_unknown_fields_refused(self) -> None:
        for path in ["relative.bes", str(self.input) + " ", str(self.root / "original.bin"), "\0.bes"]:
            with self.subTest(path=path):
                self.refuse({"protocol": 1, "op": "open", "input": path})
        self.refuse({"protocol": 1, "op": "open", "input": str(self.input), "overwrite": True})

    def test_malformed_prepared_bytes_and_hash_refused(self) -> None:
        request = self.publish_request(self.open())
        for field, value in [("bytes", "!"), ("bytes", base64.b64encode(self.original[:-1]).decode()),
                             ("bytes", base64.b64encode(self.original + b"x").decode()),
                             ("sha256", "0"), ("sha256", "z" * 64), ("identity", "")]:
            with self.subTest(field=field, length=len(value)):
                self.refuse(request | {field: value})
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(sys.platform == "linux", "Linux alias acceptance; Windows requires its own host.")
    def test_source_hardlink_rejected_before_and_after_open(self) -> None:
        snapshot = self.open()
        alias = self.root / "alias.bes"
        os.link(self.input, alias)
        self.refuse({"protocol": 1, "op": "open", "input": str(alias)})
        self.refuse(self.publish_request(snapshot))
        self.assertEqual(self.original, alias.read_bytes())
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(sys.platform == "linux", "Linux alias acceptance; Windows requires its own host.")
    def test_source_and_ancestor_symlinks_rejected(self) -> None:
        alias = self.root / "alias.bes"
        alias.symlink_to(self.input)
        self.refuse({"protocol": 1, "op": "open", "input": str(alias)})
        folder_alias = self.root / "folder-alias"
        folder_alias.symlink_to(self.output_dir, target_is_directory=True)
        request = self.publish_request(self.open())
        request["output"] = str(folder_alias / "copy.bes")
        self.refuse(request)
        self.assertEqual([], list(self.output_dir.iterdir()))

    @unittest.skipUnless(sys.platform == "linux", "Linux alias acceptance; Windows requires its own host.")
    def test_dangling_destination_symlink_preserved(self) -> None:
        snapshot = self.open()
        target = self.root / "absent.bes"
        self.output.symlink_to(target)
        self.refuse(self.publish_request(snapshot))
        self.assertTrue(self.output.is_symlink())
        self.assertFalse(target.exists())

    @unittest.skipUnless(sys.platform == "linux", "Native race harness currently covers Linux descriptor publication.")
    def test_transaction_races(self) -> None:
        if RACE_HARNESS is None:
            self.skipTest("Pass --race-harness to run the separate native race executable.")
        result = subprocess.run([str(RACE_HARNESS), str(self.input), str(self.root)],
                                text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"], report)
        self.assertEqual(6, len(report["passed"]))


def main() -> int:
    global BRIDGE, RACE_HARNESS, RUN_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", default=os.environ.get("ONSLAUGHT_FILE_BRIDGE"))
    parser.add_argument("--race-harness")
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    if not args.bridge:
        parser.error("--bridge or ONSLAUGHT_FILE_BRIDGE is required")
    BRIDGE = Path(args.bridge).resolve(strict=True)
    RACE_HARNESS = Path(args.race_harness).resolve(strict=True) if args.race_harness else None
    owner = args.output_root or REPO / "local-data/companion"
    owner.mkdir(parents=True, exist_ok=True)
    RUN_ROOT = Path(tempfile.mkdtemp(prefix="file-bridge-tests-", dir=owner))
    print(f"Owned fixture copies and results: {RUN_ROOT}", flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FileBridgeTests)
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
