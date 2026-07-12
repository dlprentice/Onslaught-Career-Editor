#!/usr/bin/env python3
"""Focused tests for scoped BEA window input sequence parsing."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "send_game_window_input.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell") or "powershell"


class SendGameWindowInputTests(unittest.TestCase):
    def ps_quote(self, value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def run_helper(
        self,
        sequence: str,
        print_only: bool = True,
        extra_args: str = "",
    ) -> subprocess.CompletedProcess[str]:
        command = f"& {self.ps_quote(str(SCRIPT))} -Sequence {self.ps_quote(sequence)}"
        if print_only:
            command += " -PrintOnly"
        if extra_args:
            command += f" {extra_args}"
        encoded_command = base64.b64encode(command.encode("utf-16le")).decode("ascii")
        return subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-OutputFormat",
                "Text",
                "-EncodedCommand",
                encoded_command,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_accepts_backslash_and_click_for_cloak_probe(self) -> None:
        result = self.run_helper("tap:BACKSLASH,wait:250,click:320x240")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["actionCount"], 3)
        actions = payload["actions"]
        self.assertEqual(actions[0]["key"], "BACKSLASH")
        self.assertEqual(actions[0]["virtualKey"], 0xDC)
        self.assertEqual(actions[0]["scanCode"], 0x2B)
        self.assertEqual(actions[2]["kind"], "click")
        self.assertEqual(actions[2]["x"], 320)
        self.assertEqual(actions[2]["y"], 240)

    def test_accepts_exact_left_right_modifier_keys(self) -> None:
        result = self.run_helper("tap:RSHIFT,tap:LSHIFT,tap:RCTRL,tap:LCTRL")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["actionCount"], 4)
        actions = payload["actions"]
        self.assertEqual(
            [(action["key"], action["scanCode"], action["extended"]) for action in actions],
            [
                ("RSHIFT", 0x36, False),
                ("LSHIFT", 0x2A, False),
                ("RCTRL", 0x1D, True),
                ("LCTRL", 0x1D, False),
            ],
        )

    def test_accepts_o_for_runtime_pause_probe(self) -> None:
        result = self.run_helper("tap:O,wait:500")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["actionCount"], 2)
        actions = payload["actions"]
        self.assertEqual(actions[0]["key"], "O")
        self.assertEqual(actions[0]["virtualKey"], 0x4F)
        self.assertEqual(actions[0]["scanCode"], 0x18)
        self.assertFalse(actions[0]["extended"])

    def test_rejects_unknown_keys(self) -> None:
        result = self.run_helper("tap:OEM_5")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported key", result.stderr)
        self.assertIn("OEM_5", result.stderr)

    def test_rejects_alt_f4_risk_keys(self) -> None:
        result = self.run_helper("down:ALT,tap:F4,up:ALT")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported key", result.stderr)
        self.assertIn("ALT", result.stderr)

    def test_real_send_requires_expected_copied_game_identity(self) -> None:
        result = self.run_helper("tap:ENTER", print_only=False, extra_args="-ProcessId 1 -HwndHex 0x1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ExpectedExecutablePath and ExpectedWorkingDirectory", result.stderr)

    def test_real_send_without_target_is_nonzero_planned_only(self) -> None:
        result = self.run_helper("tap:ENTER", print_only=False)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "target-required")
        self.assertTrue(payload["plannedOnly"])

    def test_real_send_no_ready_window_is_nonzero(self) -> None:
        result = self.run_helper(
            "tap:ENTER",
            print_only=False,
            extra_args=(
                "-ProcessId 1 -HwndHex 0x1 "
                f"-ExpectedExecutablePath {self.ps_quote(str(SCRIPT))} "
                f"-ExpectedWorkingDirectory {self.ps_quote(str(ROOT))}"
            ),
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotEqual(payload["status"], "ready")
        self.assertTrue(payload["plannedOnly"])

    def test_background_window_messages_require_explicit_arm(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[switch]$AllowBackgroundWindowMessages", script)
        self.assertIn("ALLOW BACKGROUND BEA WINDOW MESSAGES", script)
        self.assertIn("refusing background window messages", script)

        fallback_index = script.index("$useWindowMessages = -not $focused")
        refusal_index = script.index("refusing background window messages", fallback_index)
        post_message_index = script.index(
            "if ([GameWindowInputNative]::PostMessage($selected.handle",
            fallback_index,
        )
        self.assertLess(refusal_index, post_message_index)

    def test_canary_mode_requires_receipt_and_rejects_background_messages(self) -> None:
        missing_hash = self.run_helper(
            "tap:Q",
            extra_args="-RuntimeReceiptPath 'missing-receipt.json'",
        )
        self.assertNotEqual(missing_hash.returncode, 0)
        self.assertIn("requires", missing_hash.stderr.lower())

        background = self.run_helper(
            "tap:Q",
            extra_args=(
                "-RuntimeReceiptPath 'missing-receipt.json' "
                f"-ExpectedReceiptSha256 {'a' * 64} "
                "-AllowBackgroundWindowMessages "
                "-BackgroundWindowMessagesArm 'ALLOW BACKGROUND BEA WINDOW MESSAGES'"
            ),
        )
        self.assertNotEqual(background.returncode, 0)
        self.assertIn("background", background.stderr.lower())

    def test_canary_revalidates_same_receipt_immediately_before_actions(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("runtime_process_identity.psm1", script)
        calls = [
            index
            for index in range(len(script))
            if script.startswith("Assert-RuntimeProcessReceipt", index)
        ]
        self.assertGreaterEqual(len(calls), 2)
        action_loop = script.index("foreach ($action in $actions)")
        self.assertLess(calls[-1], action_loop)
        self.assertIn("-RequireWindow", script[calls[-1] : action_loop])

    def test_successful_key_downs_are_released_in_reverse_order_from_finally(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        held_keys = script.index("$heldKeys = [System.Collections.Generic.List[object]]::new()")
        action_loop = script.index("foreach ($action in $actions)", held_keys)
        finally_block = script.index("finally", action_loop)
        reverse_loop = script.index("$heldKeys.Count - 1", finally_block)
        release_call = script.index("SendScanKey", reverse_loop)
        self.assertLess(held_keys, action_loop)
        self.assertLess(action_loop, finally_block)
        self.assertLess(finally_block, reverse_loop)
        self.assertLess(reverse_loop, release_call)


if __name__ == "__main__":
    unittest.main(verbosity=2)
