#!/usr/bin/env python3
"""Focused contract tests for tools/parity_lab.py."""

from __future__ import annotations

import hashlib
import io
import json
import datetime as dt
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing, redirect_stderr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import parity_lab  # noqa: E402


def write_text(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_drcov(
    path: pathlib.Path,
    block_starts: list[int],
    module_path: pathlib.Path,
    serial: int = 0,
) -> pathlib.Path:
    block_rows = "\n".join(
        f"module[  0]: 0x{start:08x},  5" for start in block_starts
    )
    return write_text(
        path,
        "\n".join(
            [
                "DRCOV VERSION: 3",
                "DRCOV FLAVOR: drcov",
                "Module Table: version 5, count 1",
                (
                    "Columns: id, containing_id, start, end, entry, offset, "
                    "preferred_base, checksum, timestamp, path"
                ),
                (
                    (" " * serial)
                    + "0, 0, 0x00401000, 0x009D8000, 0x00401000, "
                    "0000000000001000, 0x00400000, 0x00000000, "
                    f"0x3ed21313, {module_path.resolve()}"
                ),
                f"BB Table: {len(block_starts)} bbs",
                "module id, start, size:",
                block_rows,
                "",
            ]
        ),
    )


class ParityLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="bea-parity-test-")
        self.root = pathlib.Path(self.temporary.name)
        self.static_exe = self.root / "BEA.original.exe"
        self.target_exe = self.root / "BEA.exe"
        pe = bytearray(0x400)
        pe[:2] = b"MZ"
        pe[0x3C:0x40] = (0x80).to_bytes(4, "little")
        pe[0x80:0x84] = b"PE\0\0"
        pe[0x84:0x86] = (0x14C).to_bytes(2, "little")
        pe[0x88:0x8C] = (0x3ED21313).to_bytes(4, "little")
        pe[0x94:0x96] = (0xE0).to_bytes(2, "little")
        pe[0x98:0x9A] = (0x10B).to_bytes(2, "little")
        pe[0x98 + 0x1C : 0x98 + 0x20] = (0x00400000).to_bytes(4, "little")
        pe[0x98 + 0x38 : 0x98 + 0x3C] = (0x005D8000).to_bytes(4, "little")
        self.static_exe.write_bytes(pe)
        self.target_exe.write_bytes(pe)
        imported_md5 = parity_lab.md5_file(self.static_exe)
        self.inventory = write_text(
            self.root / "functions.tsv",
            "\n".join(
                [
                    (
                        "address\tname\tnameSource\tbodyBytes\tbodyMin\tbodyMax"
                        "\tbodyRanges\ttags"
                    ),
                    (
                        "0x00401000\tKnown_Function\tUSER_DEFINED\t12\t"
                        "0x00401000\t0x00401015\t2\t"
                    ),
                    (
                        "0x00402000\tFUN_00402000\tDEFAULT\t16\t"
                        "0x00402000\t0x0040200f\t1\t"
                    ),
                    "",
                ]
            ),
        )
        self.ranges = write_text(
            self.root / "ranges.tsv",
            "\n".join(
                [
                    "# schema=bea-ghidra-parity-graph.v2",
                    f"# executableMd5={imported_md5}",
                    "# executablePath=synthetic/BEA.original.exe",
                    "# imageBase=0x00400000",
                    "# language=x86:LE:32:default",
                    "# compilerSpec=windows",
                    (
                        "functionAddress\tfunctionName\trangeOrdinal\t"
                        "rangeMin\trangeMax\trangeBytes"
                    ),
                    "0x00401000\tKnown_Function\t1\t0x00401000\t0x00401005\t6",
                    "0x00401000\tKnown_Function\t2\t0x00401010\t0x00401015\t6",
                    "0x00402000\tFUN_00402000\t1\t0x00402000\t0x0040200f\t16",
                    "",
                ]
            ),
        )
        self.edges = write_text(
            self.root / "calls.tsv",
            "\n".join(
                [
                    "# schema=bea-ghidra-parity-graph.v2",
                    f"# executableMd5={imported_md5}",
                    "# executablePath=synthetic/BEA.original.exe",
                    "# imageBase=0x00400000",
                    "# language=x86:LE:32:default",
                    "# compilerSpec=windows",
                    (
                        "callerAddress\tcallerName\tcalleeAddress\tcalleeName"
                        "\tcallSiteCount\tedgeKind"
                    ),
                    (
                        "0x00401000\tKnown_Function\t0x00402000\tFUN_00402000"
                        "\t2\tSTATIC_DIRECT"
                    ),
                    "",
                ]
            ),
        )
        self.graph_receipt = self.root / "parity-graph.ready.json"
        self.graph_receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": "bea-ghidra-parity-graph-receipt.v2",
                    "program": {
                        "executableMd5": imported_md5,
                        "executablePath": "synthetic/BEA.original.exe",
                        "imageBase": "0x00400000",
                        "language": "x86:LE:32:default",
                        "compilerSpec": "windows",
                    },
                    "bodyRanges": {
                        "file": self.ranges.name,
                        "bytes": self.ranges.stat().st_size,
                        "sha256": parity_lab.sha256_file(self.ranges),
                        "functionCount": 2,
                        "rangeCount": 3,
                    },
                    "directCalls": {
                        "file": self.edges.name,
                        "bytes": self.edges.stat().st_size,
                        "sha256": parity_lab.sha256_file(self.edges),
                        "directEdgeCount": 1,
                        "directCallSiteCount": 2,
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        self.baselines = [
            write_drcov(
                self.root / f"idle-{index}.log", [0], self.target_exe, index
            )
            for index in range(2)
        ]
        self.actions = [
            write_drcov(
                self.root / f"action-{index}.log",
                [0, 0x1000],
                self.target_exe,
                index,
            )
            for index in range(2)
        ]
        target_hash = parity_lab.sha256_file(self.target_exe)
        self.baseline_receipts = [
            self._write_coverage_receipt(
                path, "baseline", index, target_hash, "NONE_BASELINE"
            )
            for index, path in enumerate(self.baselines)
        ]
        self.action_receipts = [
            self._write_coverage_receipt(
                path, "action", index, target_hash, "MECHANICALLY_VERIFIED"
            )
            for index, path in enumerate(self.actions)
        ]

    def _write_coverage_receipt(
        self,
        log_path: pathlib.Path,
        role: str,
        index: int,
        target_hash: str,
        action_status: str,
    ) -> pathlib.Path:
        path = self.root / f"{role}-{index}.receipt.json"
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": "bea-drcov-capture-receipt.v1",
                    "runId": f"{role}-{index}",
                    "role": role,
                    "logPath": str(log_path.resolve()),
                    "logSha256": parity_lab.sha256_file(log_path),
                    "targetSha256": target_hash,
                    "captureComplete": True,
                    "actionStatus": action_status,
                    "tool": "drcov",
                    "toolVersion": "test",
                    "actionProtocol": "synthetic test protocol",
                }
            ),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def _embedded_facts(path: pathlib.Path) -> dict[str, object]:
        return {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": parity_lab.sha256_file(path),
            "lastWriteUtc": "2026-07-29T00:00:00.0000000Z",
        }

    @staticmethod
    def _stable_page(value: int) -> dict[str, object]:
        return {
            "expected": value,
            "stable": True,
            "requiredSamples": 4,
            "samples": [
                {"elapsedMilliseconds": index * 125, "value": value}
                for index in range(4)
            ],
        }

    @staticmethod
    def _iso(value: dt.datetime) -> str:
        return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")

    def _write_window_input_receipt(
        self,
        *,
        path: pathlib.Path,
        kind: str,
        x: int,
        y: int,
        process_id: int,
        hwnd: str,
        generated: dt.datetime,
    ) -> pathlib.Path:
        events = 3 if kind == "click" else 1
        payload = {
            "schemaVersion": "game-window-input.v1",
            "generatedAt": self._iso(generated),
            "processName": "BEA.exe",
            "processId": process_id,
            "hwndHex": hwnd,
            "status": "sent",
            "plannedOnly": False,
            "backgroundWindowMessagesAllowed": True,
            "actionCount": 1,
            "keyEventsSent": 0,
            "sendInputEventsSent": 0,
            "scanKeybdEventsSent": 0,
            "windowMessageEventsSent": events,
            "mouseEventsSent": events,
            "deliveryFailure": None,
            "releaseFailures": [],
            "unconfirmedReleaseKeys": [],
            "transport": "messages",
            "sendInputFailures": [],
            "occlusionBefore": {
                "probed": True,
                "unoccluded": True,
                "mask": 0,
            },
            "occlusionAfter": {
                "probed": True,
                "unoccluded": True,
                "mask": 0,
            },
            "cursorProbes": [
                {
                    "step": kind,
                    "postedClientX": x,
                    "postedClientY": y,
                    "globals": {
                        "a": {"address": "0x0089BDA8", "asInt32": x},
                        "b": {"address": "0x0089BDA4", "asInt32": y},
                        "mouseGate": {
                            "address": "0x0089BDF0",
                            "asInt32": 0,
                        },
                    },
                    "matchedX": ["0x0089BDA8"],
                    "matchedY": ["0x0089BDA4"],
                }
            ],
            "actions": [{"kind": kind, "x": x, "y": y}],
            "selectedWindow": {
                "processId": process_id,
                "processName": "BEA.exe",
                "hwndHex": hwnd,
                "minimized": False,
                "executablePath": str(self.target_exe.resolve()),
                "workingDirectory": str(self.target_exe.resolve().parent),
            },
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _write_options_click_receipt(
        self,
        *,
        path: pathlib.Path,
        process_id: int,
        hwnd: str,
        generated: dt.datetime,
    ) -> pathlib.Path:
        payload = {
            "schemaVersion": "bea-options-click-receipt.v1",
            "generatedAtUtc": self._iso(generated),
            "processId": process_id,
            "hwndHex": hwnd,
            "transport": "PostMessage-button-only",
            "precondition": {
                "page": 0,
                "cursorX": 219,
                "cursorY": 404,
                "mouseGate": 0,
            },
            "action": {
                "clientX": 219,
                "clientY": 404,
                "mouseMovePosted": False,
                "buttonDownPosted": True,
                "buttonUpPosted": True,
            },
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _install_options_canary_graph(self) -> None:
        canaries = [
            (0x004623E0, "CFEPMain__DoAction"),
            (0x0051F7E0, "CFEPOptions__EnsureOptionsContext"),
            (0x0051F6D0, "CFEPOptions__RenderPreCommon"),
            (0x0051B660, "CFrontEnd__ClickToStart"),
            (0x00464520, "CFEPMain__ActiveNotification"),
            (0x00462D40, "CFEPMain__Render"),
        ]
        inventory_lines = self.inventory.read_text(encoding="utf-8").splitlines()
        inventory_lines.extend(
            (
                f"0x{address:08X}\t{name}\tUSER_DEFINED\t16\t"
                f"0x{address:08X}\t0x{address + 15:08X}\t1\t"
            )
            for address, name in canaries
        )
        inventory_lines.append("")
        self.inventory.write_text(
            "\n".join(inventory_lines), encoding="utf-8", newline="\n"
        )

        range_lines = self.ranges.read_text(encoding="utf-8").splitlines()
        range_lines.extend(
            (
                f"0x{address:08X}\t{name}\t1\t"
                f"0x{address:08X}\t0x{address + 15:08X}\t16"
            )
            for address, name in canaries
        )
        range_lines.append("")
        self.ranges.write_text(
            "\n".join(range_lines), encoding="utf-8", newline="\n"
        )

        receipt = json.loads(self.graph_receipt.read_text(encoding="utf-8"))
        receipt["bodyRanges"].update(
            {
                "bytes": self.ranges.stat().st_size,
                "sha256": parity_lab.sha256_file(self.ranges),
                "functionCount": 8,
                "rangeCount": 9,
            }
        )
        self.graph_receipt.write_text(
            json.dumps(receipt, indent=2), encoding="utf-8"
        )

    def _write_options_receipt(
        self,
        *,
        log_path: pathlib.Path,
        campaign: str,
        sequence: int,
        token: str,
        role: str,
        serial: int,
        common: dict[str, object],
    ) -> pathlib.Path:
        page = 0 if role == "baseline" else 17
        started = dt.datetime(
            2026, 7, 29, 12, 0, tzinfo=dt.timezone.utc
        ) + dt.timedelta(seconds=(serial - 1) * 20)
        appeared = started + dt.timedelta(seconds=1)
        common_epoch = started + dt.timedelta(seconds=3)
        observation_started = started + dt.timedelta(seconds=4)
        observation_end = observation_started + dt.timedelta(seconds=5)
        finished = started + dt.timedelta(seconds=10)
        process_id = 1000 + serial
        drrun_process_id = 2000 + serial
        hwnd = f"0x{0x3000 + serial:X}"
        shared_click = self._write_window_input_receipt(
            path=self.root / f"shared-click-{serial}.json",
            kind="click",
            x=320,
            y=240,
            process_id=process_id,
            hwnd=hwnd,
            generated=started + dt.timedelta(seconds=1.5),
        )
        shared_cursor = self._write_window_input_receipt(
            path=self.root / f"shared-cursor-{serial}.json",
            kind="move",
            x=219,
            y=404,
            process_id=process_id,
            hwnd=hwnd,
            generated=started + dt.timedelta(seconds=2),
        )
        action_input = (
            self._write_options_click_receipt(
                path=self.root / f"action-input-{serial}.json",
                process_id=process_id,
                hwnd=hwnd,
                generated=common_epoch + dt.timedelta(milliseconds=100),
            )
            if role == "action"
            else None
        )
        protocol = common["protocol"]
        protocol_text = json.dumps(
            protocol, separators=(",", ":"), ensure_ascii=False
        )
        payload = {
            "schemaVersion": "bea-drcov-capture-receipt.v2",
            "runId": f"{campaign}-{sequence}-{serial}",
            "role": role,
            "logPath": str(log_path.resolve()),
            "logSha256": parity_lab.sha256_file(log_path),
            "targetSha256": common["targetFacts"]["sha256"],
            "captureComplete": True,
            "actionStatus": (
                "NONE_BASELINE" if role == "baseline" else "MECHANICALLY_VERIFIED"
            ),
            "tool": "DynamoRIO drcov",
            "toolVersion": "synthetic-11.3.0",
            "actionProtocol": "bea-options-drcov-protocol.v1",
            "scenario": "options-main-to-options.v1",
            "campaignId": campaign,
            "sequenceIndex": sequence,
            "orderToken": token,
            "protocolVersion": "bea-options-drcov-protocol.v1",
            "protocol": protocol,
            "protocolSha256": hashlib.sha256(
                protocol_text.encode("utf-8")
            ).hexdigest(),
            "targetPath": common["targetFacts"]["path"],
            "drrunPath": common["drrunFacts"]["path"],
            "drrunSha256": common["drrunFacts"]["sha256"],
            "targetUnchanged": True,
            "workingDirectory": str(self.target_exe.resolve().parent),
            "gameArguments": ["-skipfmv"],
            "requestedCaptureSeconds": 5,
            "artifacts": {
                "targetBefore": common["targetFacts"],
                "targetAfter": common["targetFacts"],
                "drrunBefore": common["drrunFacts"],
                "drrunAfter": common["drrunFacts"],
                "recorderBefore": common["recorderFacts"],
                "recorderAfter": common["recorderFacts"],
                "inputSenderBefore": common["senderFacts"],
                "inputSenderAfter": common["senderFacts"],
            },
            "precondition": {
                "passed": True,
                "viewport": {"width": 640, "height": 480},
                "contract": {
                    "activePageAddress": "0x0089D950",
                    "clickToStartPage": 12,
                    "mainMenuPage": 0,
                    "sharedClick": {"x": 320, "y": 240},
                    "optionsCursor": {"x": 219, "y": 404},
                    "stableSamples": 4,
                    "sampleIntervalMilliseconds": 125,
                    "settleMilliseconds": 1000,
                },
                "startPage": self._stable_page(12),
                "mainPage": self._stable_page(0),
                "settledMainPage": self._stable_page(0),
                "settledCursor": {"x": 219, "y": 404, "mouseGate": 0},
                "sharedClickReceipt": self._embedded_facts(shared_click),
                "optionsCursorReceipt": self._embedded_facts(shared_cursor),
                "commonEpochAtUtc": self._iso(common_epoch),
            },
            "outcome": {
                "passed": True,
                "expectedPage": page,
                "initialPage": self._stable_page(page),
                "finalPage": self._stable_page(page),
                "observationSamples": [
                    {
                        "atUtc": self._iso(
                            observation_started
                            + dt.timedelta(milliseconds=index * 125)
                        ),
                        "value": page,
                    }
                    for index in range(40)
                ],
                "actionInputReceipt": (
                    self._embedded_facts(action_input)
                    if action_input is not None
                    else None
                ),
            },
            "corpus": {
                "unchanged": True,
                "defaultOptionsBefore": common["defaultOptionsFacts"],
                "defaultOptionsAfter": common["defaultOptionsFacts"],
                "saveCorpusBefore": common["saveCorpus"],
                "saveCorpusAfter": common["saveCorpus"],
            },
            "process": {
                "targetProcessId": process_id,
                "targetParentProcessId": drrun_process_id,
                "targetDescendsFromDrrun": True,
                "drrunProcessId": drrun_process_id,
                "targetHwndHex": hwnd,
                "moduleBase": "0x00400000",
                "startedAtUtc": self._iso(started),
                "gameAppearedAtUtc": self._iso(appeared),
                "observationStartedAtUtc": self._iso(observation_started),
                "observationEndAtUtc": self._iso(observation_end),
                "targetExitCode": 0,
                "drrunExitCode": 0,
                "observationCompleted": True,
                "guestExitedBeforeWindow": False,
                "forcedTermination": False,
            },
            "cleanup": {
                "matchingProcessScanPerformed": True,
                "extraMatchingTargetsDetected": 0,
                "extraMatchingDrrunsDetected": 0,
                "targetSurvivorCount": 0,
                "drrunSurvivorCount": 0,
                "problems": [],
            },
            "startedAtUtc": self._iso(started),
            "finishedAtUtc": self._iso(finished),
            "failure": None,
        }
        receipt_path = self.root / f"{campaign}-{sequence}-{serial}.receipt.json"
        receipt_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return receipt_path

    def _options_campaign_fixture(
        self,
    ) -> tuple[list[pathlib.Path], list[pathlib.Path], list[pathlib.Path], list[pathlib.Path]]:
        self._install_options_canary_graph()
        drrun = write_text(self.root / "drrun.exe", "synthetic drrun\n")
        recorder = write_text(self.root / "recorder.ps1", "synthetic recorder\n")
        sender = write_text(self.root / "sender.ps1", "synthetic sender\n")
        default_options = write_text(
            self.root / "defaultoptions.bea", "synthetic options\n"
        )
        save_root = self.root / "savegames"
        save_root.mkdir(exist_ok=True)
        save_file = write_text(save_root / "career.bes", "synthetic save\n")
        save_row = {
            "relativePath": "career.bes",
            "bytes": save_file.stat().st_size,
            "sha256": parity_lab.sha256_file(save_file),
            "lastWriteUtc": "2026-07-29T00:00:00.0000000Z",
        }
        save_canonical = (
            f"{save_row['relativePath']}\t{save_row['bytes']}\t"
            f"{save_row['sha256']}\t{save_row['lastWriteUtc']}"
        )
        protocol = {
            "version": "bea-options-drcov-protocol.v1",
            "scenario": "options-main-to-options.v1",
            "activePageAddress": "0x0089D950",
            "cursorXAddress": "0x0089BDA8",
            "cursorYAddress": "0x0089BDA4",
            "mouseGateAddress": "0x0089BDF0",
            "clickToStartPage": 12,
            "mainMenuPage": 0,
            "optionsPage": 17,
            "sharedClick": {"x": 320, "y": 240},
            "optionsCursor": {"x": 219, "y": 404},
            "pageStableSamples": 4,
            "pageSampleIntervalMilliseconds": 125,
            "mainMenuSettleMilliseconds": 1000,
            "observationSeconds": 5,
            "gameArguments": ["-skipfmv"],
            "actionCanaries": [
                "0x004623E0",
                "0x0051F7E0",
                "0x0051F6D0",
            ],
            "sharedCanaries": [
                "0x0051B660",
                "0x00464520",
                "0x00462D40",
            ],
            "campaignSchedules": {
                "C1": ["B1", "A1", "A2", "B2", "B3", "A3"],
                "C2": ["A4", "B4", "B5", "A5", "A6", "B6"],
            },
        }
        common: dict[str, object] = {
            "protocol": protocol,
            "targetFacts": self._embedded_facts(self.target_exe),
            "drrunFacts": self._embedded_facts(drrun),
            "recorderFacts": self._embedded_facts(recorder),
            "senderFacts": self._embedded_facts(sender),
            "defaultOptionsFacts": self._embedded_facts(default_options),
            "saveCorpus": {
                "root": str(save_root.resolve()),
                "fileCount": 1,
                "totalBytes": save_file.stat().st_size,
                "aggregateSha256": hashlib.sha256(
                    save_canonical.encode("utf-8")
                ).hexdigest(),
                "files": [save_row],
            },
        }
        schedules = {
            "C1": ("B1", "A1", "A2", "B2", "B3", "A3"),
            "C2": ("A4", "B4", "B5", "A5", "A6", "B6"),
        }
        action_canary_rvas = [0x000623E0, 0x0011F7E0, 0x0011F6D0]
        shared_canary_rvas = [0x0011B660, 0x00064520, 0x00062D40]
        baselines: list[pathlib.Path] = []
        baseline_receipts: list[pathlib.Path] = []
        actions: list[pathlib.Path] = []
        action_receipts: list[pathlib.Path] = []
        serial = 0
        for campaign, schedule in schedules.items():
            for sequence, token in enumerate(schedule, start=1):
                serial += 1
                role = "baseline" if token.startswith("B") else "action"
                rvas = list(shared_canary_rvas)
                if role == "action":
                    rvas.extend([0x00002000, *action_canary_rvas])
                    rvas.append(0x00001010 if campaign == "C1" else 0x00001020)
                starts = [rva - 0x1000 for rva in rvas]
                log = write_drcov(
                    self.root / f"{campaign}-{sequence}.log",
                    starts,
                    self.target_exe,
                    serial,
                )
                receipt = self._write_options_receipt(
                    log_path=log,
                    campaign=campaign,
                    sequence=sequence,
                    token=token,
                    role=role,
                    serial=serial,
                    common=common,
                )
                if role == "baseline":
                    baselines.append(log)
                    baseline_receipts.append(receipt)
                else:
                    actions.append(log)
                    action_receipts.append(receipt)
        return baselines, baseline_receipts, actions, action_receipts

    def _options_arguments(
        self,
        *,
        baselines: list[pathlib.Path],
        baseline_receipts: list[pathlib.Path],
        actions: list[pathlib.Path],
        action_receipts: list[pathlib.Path],
        output: pathlib.Path,
    ) -> list[str]:
        return [
            "coverage-diff",
            *sum((["--baseline", str(path)] for path in baselines), []),
            *sum(
                (
                    ["--baseline-receipt", str(path)]
                    for path in baseline_receipts
                ),
                [],
            ),
            *sum((["--action", str(path)] for path in actions), []),
            *sum(
                (["--action-receipt", str(path)] for path in action_receipts),
                [],
            ),
            "--ghidra",
            str(self.inventory),
            "--body-ranges",
            str(self.ranges),
            "--call-edges",
            str(self.edges),
            "--graph-receipt",
            str(self.graph_receipt),
            "--static-exe",
            str(self.static_exe),
            "--target-exe",
            str(self.target_exe),
            "--scenario",
            "options-main-to-options.v1",
            "--action-canary",
            "0x004623E0",
            "--action-canary",
            "0x0051F7E0",
            "--action-canary",
            "0x0051F6D0",
            "--shared-canary",
            "0x0051B660",
            "--shared-canary",
            "0x00464520",
            "--shared-canary",
            "0x00462D40",
            "--options-contract",
            "--out",
            str(output),
        ]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_drcov_v3_bare_hex_segment_offset(self) -> None:
        parsed = parity_lab.parse_drcov(self.baselines[0])
        blocks, modules = parity_lab.select_module_blocks(parsed, "BEA.exe")
        self.assertEqual(0x1000, modules[0].offset)
        self.assertEqual([(0x1000, 5)], blocks)

    def test_image_derivation_rejects_an_unreviewed_same_layout_patch(self) -> None:
        changed = bytearray(self.target_exe.read_bytes())
        changed[0x200] ^= 0x01
        self.target_exe.write_bytes(changed)
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "byte derivation is not reviewed"
        ):
            parity_lab.image_derivation(self.static_exe, self.target_exe)

    def test_repeated_coverage_diff_maps_fragmented_ranges_and_direct_edges(self) -> None:
        output = self.root / "coverage"
        arguments = [
            "coverage-diff",
            *sum((["--baseline", str(path)] for path in self.baselines), []),
            *sum(
                (["--baseline-receipt", str(path)] for path in self.baseline_receipts),
                [],
            ),
            *sum((["--action", str(path)] for path in self.actions), []),
            *sum(
                (["--action-receipt", str(path)] for path in self.action_receipts),
                [],
            ),
            "--ghidra",
            str(self.inventory),
            "--body-ranges",
            str(self.ranges),
            "--call-edges",
            str(self.edges),
            "--graph-receipt",
            str(self.graph_receipt),
            "--static-exe",
            str(self.static_exe),
            "--target-exe",
            str(self.target_exe),
            "--scenario",
            "synthetic-fire",
            "--out",
            str(output),
        ]
        self.assertEqual(0, parity_lab.main(arguments))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("CORRELATED", manifest["comparability"])
        self.assertEqual("NONE", manifest["actionVerifiedBy"])
        self.assertEqual(1, manifest["stableActionNovelBlockCount"])
        candidates = [
            json.loads(line)
            for line in (output / "functions.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        unknown = next(row for row in candidates if row["name"] == "FUN_00402000")
        self.assertEqual("ACTION_ONLY_STABLE_FUNCTION", unknown["classification"])
        self.assertEqual(2, unknown["actionSupport"])
        self.assertEqual(0, unknown["baselineSupport"])
        self.assertEqual(1, unknown["stableActionNovelBlocks"])
        self.assertEqual("Known_Function", unknown["callers"][0]["name"])
        with closing(sqlite3.connect(output / "coverage.sqlite")) as connection:
            row = connection.execute(
                "SELECT mapping_quality FROM coverage_block WHERE rva=0x2000 LIMIT 1"
            ).fetchone()
        self.assertEqual("EXACT_GHIDRA_RANGES", row[0])
        self.assertEqual(0, parity_lab.main(["verify", "--manifest", str(output / "manifest.json")]))

    def test_coverage_canary_mechanically_verifies_a_posted_action(self) -> None:
        for receipt_path in self.action_receipts:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["actionStatus"] = "POSTED_NOT_ACKNOWLEDGED"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        output = self.root / "coverage-canary"
        arguments = [
            "coverage-diff",
            *sum((["--baseline", str(path)] for path in self.baselines), []),
            *sum(
                (["--baseline-receipt", str(path)] for path in self.baseline_receipts),
                [],
            ),
            *sum((["--action", str(path)] for path in self.actions), []),
            *sum(
                (["--action-receipt", str(path)] for path in self.action_receipts),
                [],
            ),
            "--ghidra",
            str(self.inventory),
            "--body-ranges",
            str(self.ranges),
            "--call-edges",
            str(self.edges),
            "--graph-receipt",
            str(self.graph_receipt),
            "--static-exe",
            str(self.static_exe),
            "--target-exe",
            str(self.target_exe),
            "--action-canary",
            "0x00402000",
            "--scenario",
            "synthetic-posted-action",
            "--out",
            str(output),
        ]
        self.assertEqual(0, parity_lab.main(arguments))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("COMPARABLE", manifest["comparability"])
        self.assertEqual("COVERAGE_CANARY", manifest["actionVerifiedBy"])
        self.assertEqual(
            {
                "actionHits": 2,
                "actionRuns": 2,
                "address": "0x00402000",
                "baselineHits": 0,
                "baselineRuns": 2,
                "name": "FUN_00402000",
                "passed": True,
            },
            manifest["actionCanaries"][0],
        )

    def test_options_v2_two_campaign_contract_closes_durable_evidence(self) -> None:
        (
            baselines,
            baseline_receipts,
            actions,
            action_receipts,
        ) = self._options_campaign_fixture()
        output = self.root / "options-proof"
        arguments = self._options_arguments(
            baselines=baselines,
            baseline_receipts=baseline_receipts,
            actions=actions,
            action_receipts=action_receipts,
            output=output,
        )
        self.assertEqual(0, parity_lab.main(arguments))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("COMPARABLE", manifest["comparability"])
        self.assertEqual(
            "RECEIPT_AND_COVERAGE_CANARY", manifest["actionVerifiedBy"]
        )
        self.assertEqual(
            6, sum(row["role"] == "baseline" for row in manifest["runs"])
        )
        self.assertEqual(
            6, sum(row["role"] == "action" for row in manifest["runs"])
        )
        self.assertEqual(4, manifest["stableActionNovelBlockCount"])
        self.assertEqual(
            {
                "campaign1OnlyStableBlockCount": 1,
                "campaign2OnlyStableBlockCount": 1,
                "durableMappingCounts": {"EXACT_GHIDRA_RANGES": 4},
                "durableStableBlockCount": 4,
            },
            manifest["crossCampaign"],
        )
        self.assertTrue(
            all(
                all(row["passed"] for row in campaign["actionCanaries"])
                and all(row["passed"] for row in campaign["sharedCanaries"])
                for campaign in manifest["campaigns"]
            )
        )
        self.assertEqual(
            0,
            parity_lab.main(
                ["verify", "--manifest", str(output / "manifest.json")]
            ),
        )

    def test_options_v2_rejects_sequence_corpus_and_page_drift(self) -> None:
        (
            baselines,
            baseline_receipts,
            actions,
            action_receipts,
        ) = self._options_campaign_fixture()
        receipt_path = action_receipts[0]
        original_receipt = receipt_path.read_text(encoding="utf-8")
        mutators = (
            (
                "sequence",
                lambda payload: payload.__setitem__("sequenceIndex", 1),
                "order token disagrees",
            ),
            (
                "corpus",
                lambda payload: payload["corpus"].__setitem__("unchanged", False),
                "corpus changed",
            ),
            (
                "page",
                lambda payload: payload["outcome"]["observationSamples"][0].__setitem__(
                    "value", 99
                ),
                "page changed",
            ),
            (
                "overlap",
                lambda payload: payload.__setitem__(
                    "finishedAtUtc", "2026-07-29T12:00:50Z"
                ),
                "overlap or are not chronological",
            ),
        )
        for label, mutate, expected in mutators:
            with self.subTest(label=label):
                payload = json.loads(original_receipt)
                mutate(payload)
                receipt_path.write_text(json.dumps(payload), encoding="utf-8")
                arguments = self._options_arguments(
                    baselines=baselines,
                    baseline_receipts=baseline_receipts,
                    actions=actions,
                    action_receipts=action_receipts,
                    output=self.root / f"options-{label}",
                )
                errors = io.StringIO()
                with redirect_stderr(errors):
                    self.assertEqual(2, parity_lab.main(arguments))
                self.assertIn(expected, errors.getvalue())
        receipt_path.write_text(original_receipt, encoding="utf-8")

    def test_options_v2_rejects_protocol_and_bound_receipt_forgery(self) -> None:
        (
            _,
            _,
            _,
            action_receipts,
        ) = self._options_campaign_fixture()
        receipt_path = action_receipts[0]
        original_receipt = receipt_path.read_text(encoding="utf-8")
        payload = json.loads(original_receipt)

        del payload["protocol"]["cursorXAddress"]
        protocol_text = json.dumps(
            payload["protocol"], separators=(",", ":"), ensure_ascii=False
        )
        payload["protocolSha256"] = hashlib.sha256(
            protocol_text.encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "protocol contract drift"
        ):
            parity_lab.validate_options_drcov_receipt_v2(
                payload, path=receipt_path
            )

        payload = json.loads(original_receipt)
        shared_path = pathlib.Path(
            payload["precondition"]["sharedClickReceipt"]["path"]
        )
        original_shared = shared_path.read_text(encoding="utf-8")
        shared_payload = json.loads(original_shared)
        shared_payload["actions"][0]["kind"] = "move"
        shared_path.write_text(json.dumps(shared_payload), encoding="utf-8")
        payload["precondition"]["sharedClickReceipt"] = self._embedded_facts(
            shared_path
        )
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "action differs from the protocol"
        ):
            parity_lab.validate_options_drcov_receipt_v2(
                payload, path=receipt_path
            )
        shared_path.write_text(original_shared, encoding="utf-8")

        payload = json.loads(original_receipt)
        shared_payload = json.loads(original_shared)
        shared_payload["selectedWindow"]["minimized"] = True
        shared_path.write_text(json.dumps(shared_payload), encoding="utf-8")
        payload["precondition"]["sharedClickReceipt"] = self._embedded_facts(
            shared_path
        )
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "selected-window identity drifted"
        ):
            parity_lab.validate_options_drcov_receipt_v2(
                payload, path=receipt_path
            )
        shared_path.write_text(original_shared, encoding="utf-8")

        payload = json.loads(original_receipt)
        payload["process"]["observationEndAtUtc"] = (
            payload["process"]["observationStartedAtUtc"]
        )
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "timestamps are inconsistent"
        ):
            parity_lab.validate_options_drcov_receipt_v2(
                payload, path=receipt_path
            )

    def test_options_v2_allows_identical_log_content_from_distinct_runs(self) -> None:
        (
            baselines,
            baseline_receipts,
            actions,
            action_receipts,
        ) = self._options_campaign_fixture()
        baselines[1].write_bytes(baselines[0].read_bytes())
        payload = json.loads(baseline_receipts[1].read_text(encoding="utf-8"))
        payload["logSha256"] = parity_lab.sha256_file(baselines[1])
        baseline_receipts[1].write_text(json.dumps(payload), encoding="utf-8")
        output = self.root / "options-identical-log-content"
        arguments = self._options_arguments(
            baselines=baselines,
            baseline_receipts=baseline_receipts,
            actions=actions,
            action_receipts=action_receipts,
            output=output,
        )
        self.assertEqual(0, parity_lab.main(arguments))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("COMPARABLE", manifest["comparability"])

    def test_options_v2_failed_campaign_canary_is_unscored(self) -> None:
        (
            baselines,
            baseline_receipts,
            actions,
            action_receipts,
        ) = self._options_campaign_fixture()
        deficient_log = actions[0]
        shared_rvas = [0x0011B660, 0x00064520, 0x00062D40]
        deficient_rvas = [
            *shared_rvas,
            0x00002000,
            0x000623E0,
            0x0011F7E0,
            0x00001010,
        ]
        write_drcov(
            deficient_log,
            [rva - 0x1000 for rva in deficient_rvas],
            self.target_exe,
            99,
        )
        deficient_receipt = action_receipts[0]
        payload = json.loads(deficient_receipt.read_text(encoding="utf-8"))
        payload["logSha256"] = parity_lab.sha256_file(deficient_log)
        deficient_receipt.write_text(json.dumps(payload), encoding="utf-8")

        output = self.root / "options-canary-failure"
        arguments = self._options_arguments(
            baselines=baselines,
            baseline_receipts=baseline_receipts,
            actions=actions,
            action_receipts=action_receipts,
            output=output,
        )
        self.assertEqual(0, parity_lab.main(arguments))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("UNSCORED", manifest["comparability"])
        c1 = next(
            row for row in manifest["campaigns"] if row["campaignId"] == "C1"
        )
        failed = next(
            row
            for row in c1["actionCanaries"]
            if row["address"] == "0x0051F6D0"
        )
        self.assertFalse(failed["passed"])

    def test_graph_ready_receipt_binds_both_static_exports(self) -> None:
        functions = parity_lab.load_functions(self.inventory, self.ranges)
        edges = parity_lab.load_call_edges(self.edges)
        facts = parity_lab.validate_graph_receipt(
            self.graph_receipt,
            self.ranges,
            self.edges,
            functions,
            edges,
        )
        self.assertEqual(
            "ghidra-parity-graph-ready-receipt", facts["kind"]
        )

        payload = json.loads(self.graph_receipt.read_text(encoding="utf-8"))
        payload["directCalls"]["sha256"] = "00" * 32
        self.graph_receipt.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "hash/size disagrees"
        ):
            parity_lab.validate_graph_receipt(
                self.graph_receipt,
                self.ranges,
                self.edges,
                functions,
                edges,
            )

    def test_symbol_map_is_rva_based_and_disambiguates_names(self) -> None:
        duplicate_inventory = write_text(
            self.root / "duplicate-functions.tsv",
            self.inventory.read_text(encoding="utf-8").replace(
                "FUN_00402000", "Known_Function"
            ),
        )
        output = self.root / "symbols.tsv"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "symbol-map",
                    "--ghidra",
                    str(duplicate_inventory),
                    "--body-ranges",
                    str(self.ranges),
                    "--static-exe",
                    str(self.static_exe),
                    "--target-exe",
                    str(self.target_exe),
                    "--out",
                    str(output),
                ]
            ),
        )
        text = output.read_text(encoding="utf-8")
        self.assertIn("0x00001000", text)
        self.assertIn("gh_HUMAN_LABEL_Known_Function_RVA_001000", text)
        self.assertIn("gh_DEFAULT_METADATA_Known_Function_RVA_002000", text)

        repeated_output = self.root / "symbols-repeat.tsv"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "symbol-map",
                    "--ghidra",
                    str(duplicate_inventory),
                    "--body-ranges",
                    str(self.ranges),
                    "--static-exe",
                    str(self.static_exe),
                    "--target-exe",
                    str(self.target_exe),
                    "--out",
                    str(repeated_output),
                ]
            ),
        )
        self.assertEqual(output.read_bytes(), repeated_output.read_bytes())

        long_name = "VeryLongFunctionName_" + ("X" * 260)
        long_inventory = write_text(
            self.root / "long-functions.tsv",
            self.inventory.read_text(encoding="utf-8")
            .replace("Known_Function", long_name)
            .replace("FUN_00402000", long_name),
        )
        long_output = self.root / "long-symbols.tsv"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "symbol-map",
                    "--ghidra",
                    str(long_inventory),
                    "--body-ranges",
                    str(self.ranges),
                    "--static-exe",
                    str(self.static_exe),
                    "--target-exe",
                    str(self.target_exe),
                    "--out",
                    str(long_output),
                ]
            ),
        )
        symbol_rows = [
            line.split("\t")
            for line in long_output.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#") and not line.startswith("rva\t")
        ]
        symbol_names = [row[2] for row in symbol_rows]
        self.assertEqual(len(symbol_names), len(set(symbol_names)))
        self.assertTrue(all(len(name) <= 220 for name in symbol_names))
        self.assertTrue(any(name.endswith("RVA_001000") for name in symbol_names))
        self.assertTrue(any(name.endswith("RVA_002000") for name in symbol_names))

    def test_symbol_map_rejects_a_range_crossing_module_end(self) -> None:
        inventory = write_text(
            self.root / "tail-functions.tsv",
            "\n".join(
                [
                    (
                        "address\tname\tnameSource\tbodyBytes\tbodyMin\tbodyMax"
                        "\tbodyRanges\ttags"
                    ),
                    (
                        "0x009D7FF8\tTailCrossing\tUSER_DEFINED\t9\t"
                        "0x009D7FF8\t0x009D8000\t1\t"
                    ),
                    "",
                ]
            ),
        )
        ranges = write_text(
            self.root / "tail-ranges.tsv",
            "\n".join(
                [
                    "# schema=bea-ghidra-parity-graph.v2",
                    f"# executableMd5={parity_lab.md5_file(self.static_exe)}",
                    "# imageBase=0x00400000",
                    (
                        "functionAddress\tfunctionName\trangeOrdinal\t"
                        "rangeMin\trangeMax\trangeBytes"
                    ),
                    (
                        "0x009D7FF8\tTailCrossing\t1\t"
                        "0x009D7FF8\t0x009D8000\t9"
                    ),
                    "",
                ]
            ),
        )
        self.assertEqual(
            2,
            parity_lab.main(
                [
                    "symbol-map",
                    "--ghidra",
                    str(inventory),
                    "--body-ranges",
                    str(ranges),
                    "--static-exe",
                    str(self.static_exe),
                    "--target-exe",
                    str(self.target_exe),
                    "--out",
                    str(self.root / "tail-symbols.tsv"),
                ]
            ),
        )
        self.assertFalse((self.root / "tail-symbols.tsv").exists())

    def test_symbol_proof_binds_reproducible_extension_and_call_pairs(self) -> None:
        trace = self.root / "proof.run"
        trace.write_bytes(b"trace")
        dll = self.root / "symbols-a.dll"
        repro_dll = self.root / "symbols-b.dll"
        dll.write_bytes(b"reproducible-dll")
        repro_dll.write_bytes(b"reproducible-dll")
        symbol_map = write_text(
            self.root / "symbols.tsv",
            "\n".join(
                [
                    "# schema=bea-debugger-symbol-map.v1",
                    "# imageBase=0x00400000",
                    f"# runtimeTargetSha256={parity_lab.sha256_file(self.target_exe)}",
                    "rva\tsize\tname",
                    "0x1000\t4\tKnownA",
                    "0x1010\t4\tKnownB",
                    "0x1020\t4\tNever",
                    "",
                ]
            ),
        )
        input_commands = write_text(
            self.root / "proof.commands",
            "\n".join(
                [
                    f".load {dll.resolve()}",
                    f"!beasym {symbol_map.resolve()} BEA",
                    'dx @$cursession.TTD.Calls("BEA!KnownA").Count()',
                    "dx @$cursession.TTD.Calls(0x00401000).Count()",
                    'dx @$cursession.TTD.Calls("BEA!KnownB").Count()',
                    "dx @$cursession.TTD.Calls(0x00401010).Count()",
                    'dx @$cursession.TTD.Calls("BEA!Never").Count()',
                    "dx @$cursession.TTD.Calls(0x00401020).Count()",
                    "",
                ]
            ),
        )
        query_dir = self.root / "query"
        query_dir.mkdir()
        generated_commands = write_text(
            query_dir / "commands.txt",
            "\n".join(
                [
                    ".echo === TTDQUERY BEGIN ===",
                    input_commands.read_text(encoding="utf-8").rstrip(),
                    ".echo === TTDQUERY OUTPUT END ===",
                    ".echo === TTDQUERY COMPLETE ===",
                    "",
                ]
            ),
        )
        cdb = self.root / "cdb.exe"
        cdb.write_bytes(b"cdb")
        log = write_text(query_dir / "cdb.log", "log\n")
        stdout = write_text(query_dir / "cdb-stdout.txt", "stdout\n")
        stderr = write_text(query_dir / "cdb-stderr.txt", "")
        output = [
            f"0:000> .load {dll.resolve()}",
            (
                "BEASYM_OK module=BEA base=0x400000 size=0x5d8000 "
                f"rows=3 added=3 retryRecovered=1 rejected=0 malformed=0 "
                f'outOfModule=0 map="{symbol_map.resolve()}"'
            ),
            '@$cursession.TTD.Calls("BEA!KnownA").Count() : 0x1',
            "@$cursession.TTD.Calls(0x00401000).Count() : 0x1",
            '@$cursession.TTD.Calls("BEA!KnownB").Count() : 0x2',
            "@$cursession.TTD.Calls(0x00401010).Count() : 0x2",
            '@$cursession.TTD.Calls("BEA!Never").Count() : 0x0',
            "@$cursession.TTD.Calls(0x00401020).Count() : 0x0",
        ]
        query = self.root / "query-result.json"
        query.write_text(
            json.dumps(
                {
                    "schemaVersion": "ttd-query-result.v3",
                    "trace": str(trace.resolve()),
                    "traceBytes": trace.stat().st_size,
                    "traceSha256": parity_lab.sha256_file(trace),
                    "cdb": str(cdb.resolve()),
                    "commandScript": str(generated_commands.resolve()),
                    "logPath": str(log.resolve()),
                    "stdoutPath": str(stdout.resolve()),
                    "stderrPath": str(stderr.resolve()),
                    "ok": True,
                    "timedOut": False,
                    "problems": [],
                    "warnings": [],
                    "knownAnswer": {
                        "AllAgree": True,
                        "Image": str(self.target_exe.resolve()),
                        "Sha256": parity_lab.sha256_file(self.target_exe),
                        "Module": "BEA",
                        "ReadAtBase": "0x00400000",
                        "Checks": [
                            {
                                "Name": "SizeOfImage",
                                "FromTrace": 0x005D8000,
                            }
                        ],
                    },
                    "negativeControl": {"Passed": True},
                    "output": output,
                }
            ),
            encoding="utf-8",
        )
        proof = self.root / "proof"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "symbol-proof",
                    "--query-result",
                    str(query),
                    "--symbol-map",
                    str(symbol_map),
                    "--dll",
                    str(dll),
                    "--repro-dll",
                    str(repro_dll),
                    "--command-file",
                    str(input_commands),
                    "--expect-call",
                    "BEA!KnownA,0x00401000,1",
                    "--expect-call",
                    "BEA!KnownB,0x00401010,2",
                    "--expect-call",
                    "BEA!Never,0x00401020,0",
                    "--out",
                    str(proof),
                ]
            ),
        )
        receipt = json.loads((proof / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual("PASS", receipt["bridgeVerdict"])
        self.assertEqual(3, receipt["loadAccounting"]["added"])
        self.assertEqual("PARTIAL", receipt["captureProvenance"])
        self.assertEqual(
            parity_lab.sha256_file(dll),
            receipt["artifacts"]["extensionDll"]["sha256"],
        )

    def test_lossless_capture_bundle_and_hash_verification(self) -> None:
        target = self.target_exe
        target_hash = hashlib.sha256(target.read_bytes()).hexdigest().upper()
        d3d9 = write_text(
            self.root / "d3d9.log",
            "\n".join(
                [
                    "# bea-d3d9-proxy v1",
                    "# time=2026-07-29T00:00:00Z pid=1234",
                    f"# exe={target.resolve()}",
                    "# real=C:\\Windows\\System32\\d3d9.dll",
                    "# cfg firstframe=0 maxframes=1 maxverts=8 noverts=0 strictcov=1",
                    "D3D9 create sdk=0x1F real=0x12345678",
                    "DEV create adapter=0 bb=640x480 pure=1",
                    "S 0 begin",
                    "D 0 0 DPUP prim=TRIFAN primc=2 verts=4 ab=1 sb=5 db=6",
                    "V 0 0 0 xyzrhw=(0,0,0,1) diff=0xFFFFFFFF",
                    "S 0 end draws=1",
                    "P 0 draws=1",
                    "# capture window closed at frame 1",
                    "# refusals total=0 warnings=0",
                    "",
                ]
            ),
        )
        receipt = self.root / "receipt.json"
        trace = self.root / "synthetic.run"
        trace.write_bytes(b"T" * 123)
        receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": "ttd-record-receipt.v3",
                    "name": "synthetic",
                    "targetSha256": target_hash,
                    "traceFile": str(trace),
                    "traceBytes": 123,
                    "traceSha256": parity_lab.sha256_file(trace),
                    "recorderVersion": "test",
                    "guestOutcome": "stopped",
                    "guestRanCleanly": True,
                    "recordedAtUtc": "2026-07-29T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        query = self.root / "result.json"
        query.write_text(
            json.dumps(
                {
                    "schemaVersion": "ttd-query-result.v3",
                    "trace": str(trace),
                    "traceBytes": 123,
                    "traceSha256": parity_lab.sha256_file(trace),
                    "ok": True,
                    "timedOut": False,
                    "problems": [],
                    "knownAnswer": {"AllAgree": True, "Sha256": target_hash},
                    "negativeControl": {"Passed": True},
                    "output": ["###KNOWN call-count=1", "BEA!Known_Function"],
                }
            ),
            encoding="utf-8",
        )
        output = self.root / "bundle"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "capture-bundle",
                    "--bundle-id",
                    "synthetic-bundle",
                    "--scenario",
                    "synthetic",
                    "--role",
                    "reference",
                    "--question",
                    "Does the bundle preserve every source line?",
                    "--positive-control",
                    "one known TTD marker",
                    "--target-exe",
                    str(target),
                    "--d3d9-log",
                    str(d3d9),
                    "--ttd-receipt",
                    str(receipt),
                    "--ttd-result",
                    str(query),
                    "--out",
                    str(output),
                ]
            ),
        )
        manifest = json.loads((output / "bundle.json").read_text(encoding="utf-8"))
        self.assertEqual("COMPLETE", manifest["captureHealth"])
        self.assertEqual("CORRELATED", manifest["comparability"])
        self.assertEqual(
            manifest["d3d9"][0]["parseAccounting"]["totalLines"],
            manifest["d3d9"][0]["parseAccounting"]["accountedLines"],
        )
        self.assertEqual(0, parity_lab.main(["verify", "--manifest", str(output / "bundle.json")]))
        with closing(sqlite3.connect(output / "capture.sqlite")) as connection:
            events = connection.execute("SELECT COUNT(*) FROM d3d9_event").fetchone()[0]
            markers = connection.execute(
                "SELECT COUNT(*) FROM ttd_line WHERE marker_kind IS NOT NULL"
            ).fetchone()[0]
        self.assertEqual(manifest["d3d9"][0]["parseAccounting"]["totalLines"], events)
        self.assertEqual(1, markers)
        trace.write_bytes(b"X" * 123)
        self.assertEqual(
            1,
            parity_lab.main(
                ["verify", "--manifest", str(output / "bundle.json")]
            ),
        )

    def test_legacy_unhashed_ttd_artifacts_never_claim_complete(self) -> None:
        trace = self.root / "legacy.run"
        trace.write_bytes(b"L" * 64)
        receipt = self.root / "legacy-receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": "ttd-record-receipt.v2",
                    "name": "legacy",
                    "targetSha256": parity_lab.sha256_file(self.target_exe),
                    "traceFile": str(trace),
                    "traceBytes": 64,
                    "guestRanCleanly": True,
                }
            ),
            encoding="utf-8",
        )
        query = self.root / "legacy-result.json"
        query.write_text(
            json.dumps(
                {
                    "schemaVersion": "ttd-query-result.v2",
                    "trace": str(trace),
                    "traceBytes": 64,
                    "ok": True,
                    "timedOut": False,
                    "problems": [],
                    "knownAnswer": {
                        "AllAgree": True,
                        "Sha256": parity_lab.sha256_file(self.target_exe),
                    },
                    "negativeControl": {"Passed": True},
                    "output": ["###KNOWN legacy=1"],
                }
            ),
            encoding="utf-8",
        )
        output = self.root / "legacy-bundle"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "capture-bundle",
                    "--bundle-id",
                    "legacy-unhashed",
                    "--scenario",
                    "legacy",
                    "--role",
                    "reference",
                    "--target-exe",
                    str(self.target_exe),
                    "--ttd-receipt",
                    str(receipt),
                    "--ttd-result",
                    str(query),
                    "--out",
                    str(output),
                ]
            ),
        )
        manifest = json.loads(
            (output / "bundle.json").read_text(encoding="utf-8")
        )
        self.assertEqual("PARTIAL", manifest["captureHealth"])
        self.assertEqual("UNSCORED", manifest["comparability"])
        self.assertFalse(manifest["ttdReceipts"][0]["traceHashDeclared"])
        self.assertFalse(manifest["ttdResults"][0]["traceHashDeclared"])

    def test_ttd_exec_coverage_receipt_is_identity_linked_and_queryable(self) -> None:
        trace = self.root / "coverage.run"
        trace.write_bytes(b"T" * 64)
        collector = self.root / "ttd_exec_coverage.exe"
        collector.write_bytes(b"collector")
        replay = self.root / "TTDReplay.dll"
        replay.write_bytes(b"replay")
        replay_cpu = self.root / "TTDReplayCPU.dll"
        replay_cpu.write_bytes(b"replay-cpu")
        coverage = self.root / "coverage.jsonl"
        rows = [
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "metadata",
                "upstream_commit": "test",
                "api_package": "test",
                "trace": str(trace.resolve()),
                "trace_bytes": "64",
                "module_requested": "BEA.exe",
                "module_name": str(self.target_exe.resolve()),
                "module_base": "0x400000",
                "module_size": "0x5D8000",
                "module_timestamp": "0x3ED21313",
                "module_checksum": "0x0",
                "module_load_sequence": "0x2",
                "module_unload_sequence": "0xFFFFFFFFFFFFFFFE",
                "lifetime_min": "0x34:0x0",
                "lifetime_max": "0x100:0x0",
                "requested_from": "0x34:0x0",
                "requested_to": "0x100:0x0",
                "watchpoint_access": "execute",
                "range_semantics": "half-open-byte-ranges",
                "window_semantics": "inclusive-position-bounds",
                "collector": "parallel-safe-atomic-byte-bitmap",
                "replay_mode": "parallel",
                "uint64_encoding": "decimal-string",
            },
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "range",
                "index": 0,
                "rva_start": "0x1000",
                "rva_end_exclusive": "0x1003",
                "va_start": "0x401000",
                "va_end_exclusive": "0x401003",
                "byte_count": 3,
            },
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "range",
                "index": 1,
                "rva_start": "0x2000",
                "rva_end_exclusive": "0x2001",
                "va_start": "0x402000",
                "va_end_exclusive": "0x402001",
                "byte_count": 1,
            },
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "assertion",
                "expectation": "hit",
                "rva": "0x1000",
                "va": "0x401000",
                "observed": True,
                "pass": True,
            },
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "gap-summary",
                "total": "1",
                "kind_no_gap": "0",
                "kind_context_switch": "0",
                "kind_unrecorded": "1",
                "kind_large": "0",
                **{
                    f"event_{index}": "1" if index == 0 else "0"
                    for index in range(17)
                },
            },
            {
                "schema": "bea.ttd.exec-coverage.v1",
                "kind": "summary",
                "range_count": 2,
                "covered_bytes": "4",
                "callback_hits": "2",
                "stop_reason": "Process",
                "steps_executed": "10",
                "instructions_executed": "9",
                "final_position": "0x100:0x1",
                "replay_complete": True,
                "marker_assertions_passed": True,
                "collector_checks_passed": True,
            },
        ]
        parity_lab.write_jsonl(coverage, rows)
        target_facts = parity_lab.artifact_facts(self.target_exe, "target")
        coverage_facts = parity_lab.artifact_facts(coverage, "coverage")
        collector_facts = parity_lab.artifact_facts(collector, "collector")
        replay_facts = parity_lab.artifact_facts(replay, "replay")
        replay_cpu_facts = parity_lab.artifact_facts(replay_cpu, "replay-cpu")
        trace_facts = parity_lab.artifact_facts(trace, "trace")
        build_receipt = self.root / "collector-build-receipt.json"
        build_receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": "bea-ttd-exec-coverage-build.v2",
                    "collector": {"sha256": collector_facts["sha256"]},
                    "runtime": {
                        "replaySha256": replay_facts["sha256"],
                        "replayCpuSha256": replay_cpu_facts["sha256"],
                    },
                    "reproducibility": {
                        "isolatedBuilds": [
                            {
                                "root": "C:\\build-a",
                                "bytes": collector_facts["bytes"],
                                "sha256": collector_facts["sha256"],
                                "selfTest": "PASS",
                            },
                            {
                                "root": "C:\\build-b",
                                "bytes": collector_facts["bytes"],
                                "sha256": collector_facts["sha256"],
                                "selfTest": "PASS",
                            },
                        ],
                        "buildCount": 2,
                        "byteIdentical": True,
                        "distinctOutputRoots": True,
                        "pdbAlternatePath": "ttd_exec_coverage.pdb",
                        "allSelfTestsPassed": True,
                    },
                }
            ),
            encoding="utf-8",
        )
        receipt = self.root / "coverage-receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schemaVersion": "bea-ttd-exec-coverage-receipt.v2",
                    "collectorExitCode": 0,
                    "replayComplete": True,
                    "markerAssertionsPassed": True,
                    "collectorChecksPassed": True,
                    "trace": trace_facts,
                    "target": {
                        **target_facts,
                        "pe": {
                            "timestamp": "0x3ED21313",
                            "sizeOfImage": "0x005D8000",
                            "checksum": "0x00000000",
                        },
                    },
                    "collector": collector_facts,
                    "replayRuntime": {
                        "version": "test",
                        "replay": replay_facts,
                        "replayCpu": replay_cpu_facts,
                    },
                    "buildReceipt": parity_lab.artifact_facts(
                        build_receipt, "build-receipt"
                    ),
                    "coverage": {
                        **coverage_facts,
                        "assertionCount": 1,
                    },
                }
            ),
            encoding="utf-8",
        )
        output = self.root / "ttd-coverage-bundle"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "capture-bundle",
                    "--bundle-id",
                    "synthetic-ttd-coverage",
                    "--scenario",
                    "synthetic",
                    "--role",
                    "reference",
                    "--target-exe",
                    str(self.target_exe),
                    "--ttd-coverage",
                    str(coverage),
                    "--ttd-coverage-receipt",
                    str(receipt),
                    "--out",
                    str(output),
                ]
            ),
        )
        manifest = json.loads((output / "bundle.json").read_text(encoding="utf-8"))
        self.assertEqual("COMPLETE", manifest["captureHealth"])
        self.assertEqual("CORRELATED", manifest["comparability"])
        self.assertEqual(4, manifest["ttdCoverage"][0]["coveredBytes"])
        self.assertTrue(
            manifest["ttdCoverageReceipts"][0]["buildReceipt"][
                "reproducibilityVerified"
            ]
        )
        with closing(sqlite3.connect(output / "capture.sqlite")) as connection:
            self.assertEqual(
                2,
                connection.execute("SELECT COUNT(*) FROM ttd_exec_range").fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM ttd_exec_assertion WHERE pass=1"
                ).fetchone()[0],
            )

        marker_fail_rows = json.loads(json.dumps(rows))
        marker_row = next(
            row for row in marker_fail_rows if row["kind"] == "assertion"
        )
        marker_row["expectation"] = "miss"
        marker_row["pass"] = False
        marker_summary = next(
            row for row in marker_fail_rows if row["kind"] == "summary"
        )
        marker_summary["marker_assertions_passed"] = False
        marker_summary["collector_checks_passed"] = False
        marker_fail_coverage = self.root / "coverage-marker-fail.jsonl"
        parity_lab.write_jsonl(marker_fail_coverage, marker_fail_rows)
        with closing(parity_lab.open_database(":memory:")) as connection:
            marker_result, _ = parity_lab.ingest_ttd_exec_coverage(
                connection, marker_fail_coverage
            )
        self.assertEqual("COMPLETE", marker_result["health"])
        self.assertTrue(marker_result["replayComplete"])
        self.assertFalse(marker_result["markerAssertionsPassed"])
        self.assertFalse(marker_result["acceptancePassed"])

        assertion_mismatch_rows = json.loads(json.dumps(rows))
        assertion_mismatch = next(
            row for row in assertion_mismatch_rows if row["kind"] == "assertion"
        )
        assertion_mismatch["observed"] = False
        assertion_mismatch["pass"] = False
        mismatch_summary = next(
            row for row in assertion_mismatch_rows if row["kind"] == "summary"
        )
        mismatch_summary["marker_assertions_passed"] = False
        mismatch_summary["collector_checks_passed"] = False
        assertion_mismatch_coverage = self.root / "coverage-assertion-mismatch.jsonl"
        parity_lab.write_jsonl(
            assertion_mismatch_coverage, assertion_mismatch_rows
        )
        with closing(parity_lab.open_database(":memory:")) as connection:
            with self.assertRaisesRegex(
                parity_lab.ParityLabError, "Inconsistent TTD assertion"
            ):
                parity_lab.ingest_ttd_exec_coverage(
                    connection, assertion_mismatch_coverage
                )

        unknown_stop_rows = json.loads(json.dumps(rows))
        next(
            row for row in unknown_stop_rows if row["kind"] == "summary"
        )["stop_reason"] = "Thread"
        unknown_stop_coverage = self.root / "coverage-unknown-stop.jsonl"
        parity_lab.write_jsonl(unknown_stop_coverage, unknown_stop_rows)
        with closing(parity_lab.open_database(":memory:")) as connection:
            with self.assertRaisesRegex(
                parity_lab.ParityLabError, "unsupported stop reason"
            ):
                parity_lab.ingest_ttd_exec_coverage(
                    connection, unknown_stop_coverage
                )

        invalid_rows = json.loads(json.dumps(rows))
        invalid_rows[0]["requested_from"] = "0x1:0x0"
        invalid_coverage = self.root / "coverage-outside-instance.jsonl"
        parity_lab.write_jsonl(invalid_coverage, invalid_rows)
        with closing(parity_lab.open_database(":memory:")) as connection:
            with self.assertRaisesRegex(
                parity_lab.ParityLabError,
                "outside trace lifetime|outside selected module-instance lifetime",
            ):
                parity_lab.ingest_ttd_exec_coverage(connection, invalid_coverage)

        trace.write_bytes(b"X" * trace.stat().st_size)
        with closing(parity_lab.open_database(":memory:")) as connection:
            replaced_trace_receipt, _ = parity_lab.ingest_ttd_exec_receipt(
                connection, receipt
            )
        self.assertEqual("ERROR", replaced_trace_receipt["health"])
        self.assertFalse(replaced_trace_receipt["traceHashMatches"])
        self.assertEqual(
            1,
            parity_lab.main(
                ["verify", "--manifest", str(output / "bundle.json")]
            ),
        )

    def test_ttd_coverage_diff_maps_exact_action_bytes_to_fun_candidate(self) -> None:
        collector = self.root / "shared-ttd-exec.exe"
        collector.write_bytes(b"collector")
        replay = self.root / "shared-TTDReplay.dll"
        replay.write_bytes(b"replay")
        replay_cpu = self.root / "shared-TTDReplayCPU.dll"
        replay_cpu.write_bytes(b"replay-cpu")
        target_facts = parity_lab.artifact_facts(self.target_exe, "target")

        def make_bundle(
            role: str,
            rva: int,
            position_min: str,
            position_max: str,
        ) -> pathlib.Path:
            run_root = self.root / f"ttd-{role}"
            run_root.mkdir()
            trace = run_root / f"{role}.run"
            trace.write_bytes(role.encode("ascii") * 32)
            coverage = run_root / "coverage.jsonl"
            rows = [
                {
                    "schema": "bea.ttd.exec-coverage.v1",
                    "kind": "metadata",
                    "trace": str(trace.resolve()),
                    "trace_bytes": str(trace.stat().st_size),
                    "module_requested": "BEA.exe",
                    "module_name": str(self.target_exe.resolve()),
                    "module_base": "0x400000",
                    "module_size": "0x5D8000",
                    "module_timestamp": "0x3ED21313",
                    "module_checksum": "0x0",
                    "module_load_sequence": "0x1",
                    "module_unload_sequence": "0xFFFFFFFFFFFFFFFE",
                    "lifetime_min": "0x1:0x0",
                    "lifetime_max": "0x40:0x0",
                    "requested_from": position_min,
                    "requested_to": position_max,
                    "watchpoint_access": "execute",
                    "range_semantics": "half-open-byte-ranges",
                    "window_semantics": "inclusive-position-bounds",
                    "collector": "parallel-safe-atomic-byte-bitmap",
                    "replay_mode": "parallel",
                    "uint64_encoding": "decimal-string",
                },
                {
                    "schema": "bea.ttd.exec-coverage.v1",
                    "kind": "range",
                    "index": 0,
                    "rva_start": f"0x{rva:X}",
                    "rva_end_exclusive": f"0x{rva + 3:X}",
                    "va_start": f"0x{0x400000 + rva:X}",
                    "va_end_exclusive": f"0x{0x400000 + rva + 3:X}",
                    "byte_count": 3,
                },
                {
                    "schema": "bea.ttd.exec-coverage.v1",
                    "kind": "assertion",
                    "expectation": "hit",
                    "rva": f"0x{rva:X}",
                    "va": f"0x{0x400000 + rva:X}",
                    "observed": True,
                    "pass": True,
                },
                {
                    "schema": "bea.ttd.exec-coverage.v1",
                    "kind": "gap-summary",
                    "total": "0",
                    "kind_no_gap": "0",
                    "kind_context_switch": "0",
                    "kind_unrecorded": "0",
                    "kind_large": "0",
                    **{f"event_{index}": "0" for index in range(17)},
                },
                {
                    "schema": "bea.ttd.exec-coverage.v1",
                    "kind": "summary",
                    "range_count": 1,
                    "covered_bytes": "3",
                    "callback_hits": "1",
                    "stop_reason": "Position",
                    "steps_executed": "3",
                    "instructions_executed": "3",
                    "final_position": position_max,
                    "replay_complete": True,
                    "marker_assertions_passed": True,
                    "collector_checks_passed": True,
                },
            ]
            parity_lab.write_jsonl(coverage, rows)
            receipt = run_root / "receipt.json"
            receipt.write_text(
                json.dumps(
                    {
                        "schemaVersion": "bea-ttd-exec-coverage-receipt.v1",
                        "collectorExitCode": 0,
                        "replayComplete": True,
                        "markerAssertionsPassed": True,
                        "collectorChecksPassed": True,
                        "trace": parity_lab.artifact_facts(trace, "trace"),
                        "target": {
                            **target_facts,
                            "pe": {
                                "timestamp": "0x3ED21313",
                                "sizeOfImage": "0x005D8000",
                                "checksum": "0x00000000",
                            },
                        },
                        "collector": parity_lab.artifact_facts(
                            collector, "collector"
                        ),
                        "replayRuntime": {
                            "version": "test",
                            "replay": parity_lab.artifact_facts(replay, "replay"),
                            "replayCpu": parity_lab.artifact_facts(
                                replay_cpu, "replay-cpu"
                            ),
                        },
                        "coverage": {
                            **parity_lab.artifact_facts(coverage, "coverage"),
                            "assertionCount": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )
            bundle = self.root / f"ttd-{role}-bundle"
            self.assertEqual(
                0,
                parity_lab.main(
                    [
                        "capture-bundle",
                        "--bundle-id",
                        f"synthetic-{role}",
                        "--scenario",
                        "synthetic-ttd-diff",
                        "--role",
                        role,
                        "--target-exe",
                        str(self.target_exe),
                        "--ttd-coverage",
                        str(coverage),
                        "--ttd-coverage-receipt",
                        str(receipt),
                        "--out",
                        str(bundle),
                    ]
                ),
            )
            return bundle / "bundle.json"

        baseline = make_bundle("baseline", 0x1000, "0x10:0x0", "0x20:0x0")
        action = make_bundle("action", 0x2000, "0x20:0x1", "0x30:0x0")
        output = self.root / "ttd-diff"
        self.assertEqual(
            0,
            parity_lab.main(
                [
                    "ttd-coverage-diff",
                    "--baseline-bundle",
                    str(baseline),
                    "--action-bundle",
                    str(action),
                    "--ghidra",
                    str(self.inventory),
                    "--body-ranges",
                    str(self.ranges),
                    "--call-edges",
                    str(self.edges),
                    "--graph-receipt",
                    str(self.graph_receipt),
                    "--static-exe",
                    str(self.static_exe),
                    "--target-exe",
                    str(self.target_exe),
                    "--scenario",
                    "synthetic-ttd-diff",
                    "--action-canary",
                    "0x00402000",
                    "--out",
                    str(output),
                ]
            ),
        )
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("CORRELATED", manifest["comparability"])
        self.assertEqual(
            "exactly-one-active-for-window",
            manifest["collectorIdentity"]["moduleInstancePolicy"],
        )
        self.assertEqual(3, manifest["stableActionNovelBytes"])
        self.assertEqual(
            {"EXACT_GHIDRA_RANGES": 3},
            manifest["stableActionNovelMappingBytes"],
        )
        candidates = [
            json.loads(line)
            for line in (output / "functions.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
        ]
        candidate = next(row for row in candidates if row["name"] == "FUN_00402000")
        self.assertEqual("ACTION_ONLY_STABLE_FUNCTION", candidate["classification"])
        self.assertEqual(3, candidate["stableActionNovelBytes"])
        self.assertEqual(
            0,
            parity_lab.main(["verify", "--manifest", str(output / "manifest.json")]),
        )

        baseline_payload = json.loads(baseline.read_text(encoding="utf-8"))
        bundled_coverage = pathlib.Path(
            baseline_payload["ttdCoverage"][0]["path"]
        )
        replaced = bytearray(bundled_coverage.read_bytes())
        replaced[-2] = ord(" ")
        bundled_coverage.write_bytes(replaced)
        with self.assertRaisesRegex(
            parity_lab.ParityLabError, "no longer matches its bundle manifest"
        ):
            parity_lab._load_ttd_bundle_run(
                baseline,
                expected_role="baseline",
                expected_scenario="synthetic-ttd-diff",
                target_facts=target_facts,
            )

    def test_ttd_independence_counts_trace_content_not_windows(self) -> None:
        def run(role: str, trace_hash: str, window: int) -> dict:
            return {
                "role": role,
                "coverage": {
                    "requestedFrom": f"0x{window:X}:0x0",
                    "requestedTo": f"0x{window + 1:X}:0x0",
                },
                "receipt": {"traceSha256": trace_hash},
            }

        pseudoreplicates = parity_lab.ttd_independence_summary(
            [run("baseline", "A" * 64, index) for index in range(3)],
            [run("action", "A" * 64, index + 10) for index in range(3)],
        )
        self.assertEqual(3, pseudoreplicates["baselineWindowCount"])
        self.assertEqual(1, pseudoreplicates["baselineDistinctTraceCount"])
        self.assertFalse(pseudoreplicates["independentlyReplicated"])

        independent = parity_lab.ttd_independence_summary(
            [
                run("baseline", character * 64, index)
                for index, character in enumerate(("A", "B", "C"))
            ],
            [
                run("action", character * 64, index + 10)
                for index, character in enumerate(("A", "B", "C"))
            ],
        )
        self.assertEqual(3, independent["baselineDistinctTraceCount"])
        self.assertEqual(3, independent["actionDistinctTraceCount"])
        self.assertTrue(independent["independentlyReplicated"])

    def test_malformed_or_unknown_d3d9_record_cannot_be_complete(self) -> None:
        database = self.root / "parse.sqlite"
        connection = parity_lab.open_database(database)
        log = write_text(
            self.root / "unknown.log",
            "\n".join(
                [
                    "# bea-d3d9-proxy v1",
                    "X unrecognized record",
                    "# refusals total=0 warnings=0",
                    "",
                ]
            ),
        )
        facts = parity_lab.artifact_facts(log, "d3d9-proxy-log")
        artifact_id = parity_lab.add_artifact(connection, facts)
        parsed = parity_lab.parse_d3d9_log(log, connection, artifact_id)
        connection.close()
        self.assertEqual("PARTIAL", parsed.health)
        self.assertEqual(1, parsed.unknown_records)
        self.assertEqual(parsed.total_lines, parsed.accounted_lines)

    def test_apitrace_wrapper_integrity_contracts_are_fail_closed(self) -> None:
        source = (
            pathlib.Path(__file__).resolve().parent / "Record-ApitraceD3D9.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("ExpectedD3DRetraceSha256", source)
        self.assertIn("$beaExitCode -eq 0", source)
        self.assertIn("$guestExitedBeforeWindow", source)
        self.assertIn("schemaVersion = 'bea-apitrace-d3d9-receipt.v5'", source)
        self.assertNotRegex(source, r"\.Kill\(\)")
        self.assertIn("function Test-ProcessDescendsFrom", source)
        self.assertIn("-AncestorProcessId $apiProcess.Id", source)
        launch_selection = source[
            source.index("$ownedCandidates = @(") :
            source.index("$beaId = $bea.Id")
        ]
        self.assertIn("Test-ProcessDescendsFrom", launch_selection)
        same_path_audit = source[
            source.index("$samePathSurvivors = @(") :
            source.index("if ($null -eq $receipt)")
        ]
        self.assertNotIn(".Kill(", same_path_audit)
        self.assertIn("they were not killed because path and launch time do", source)
        self.assertIn("$primaryProblem = $_.Exception.Message", source)
        self.assertIn("if ($null -eq $receipt)", source)
        self.assertIn("problem = $primaryProblem", source)
        self.assertIn("$receipt.process.forcedTermination = $forcedTermination", source)
        self.assertIn(
            "primaryCaptureProcessTreeKillAttemptCount =",
            source,
        )
        self.assertIn(
            "primaryCaptureProcessTreeKillSuccessCount =",
            source,
        )
        self.assertNotIn("processTreeTermination = $true", source)
        self.assertLess(
            source.index("$receipt.cleanup ="),
            source.index("$receiptPath ="),
        )
        self.assertLess(
            source.index("samePathSurvivorsWereKilled = $false"),
            source.index("$receiptPath ="),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
