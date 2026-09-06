#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Smoke tests for tools/export_packets.py over a 5-VA list.

No Ghidra is required: the suite builds a tiny fake headless that emits the
same stdout markers and file shapes as ExportTriagePacket.java, then asserts
the driver's real contracts against it:

  * one headless invocation covers all requested VAs (the ONE-run gate)
  * the -readOnly -noanalysis flags are present on the composed command
  * the READY receipt and per-packet image hash are verified after the run
  * a re-run skips matching-image packets and never relaunches headless
  * --force removes and re-cuts; a foreign-image packet refuses instead
  * the driver refuses the live project by default
  * the tracked 5-VA list parses to exactly the named VAs
  * the Java exporter's static contract holds (usage arity, -readOnly
    banner, no setX mutation APIs on the program)

If test_incremental_rerun_skips_matching_packets ever passes trivially, the
incremental gate is decoration.
"""

from __future__ import annotations

import hashlib
import importlib.util
import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

TOOL = Path(__file__).resolve().parent / "export_packets.py"
REPO_ROOT = Path(__file__).resolve().parents[1]
VA_LIST = REPO_ROOT / "tools" / "packet-va-cgame-level-flow.txt"
IMAGE = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

EXPECTED_VAS = [
    "0x00423bc0",
    "0x0046c360",
    "0x0046cdf0",
    "0x0046dc30",
    "0x0046e910",
]

FAKE_HEADLESS_INNER = """\
import hashlib, json, os, sys
args = sys.argv[1:]
with open(os.path.join(os.path.dirname(__file__), "headless-calls.jsonl"), "a") as log:
    log.write(json.dumps(args) + "\\n")
# Launched as: python fake-headless-inner.py <project_root> <name> <flags...>
rest = args
project_root, project_name = rest[0], rest[1]
flags = rest[2:]
assert "-readOnly" in flags, "fake headless requires -readOnly"
assert "-noanalysis" in flags, "fake headless requires -noanalysis"
i = flags.index("-postScript")
addresses, out, ready = flags[i + 2], flags[i + 3], flags[i + 4]
closure = flags[i + 5] if len(flags) > i + 5 else None
os.makedirs(out, exist_ok=True)
entries = []
for line in open(addresses, encoding="utf-8"):
    t = line.strip()
    if not t or t.startswith("#"):
        continue
    t = t.split("#")[0].strip()
    if t and ("0x" + t[2:].lower()) not in entries:
        entries.append("0x" + t[2:].lower())
names = {
    "0x00423bc0": "CLIParams__ParseCommandLine",
    "0x0046c360": "CGame__Init",
    "0x0046cdf0": "CGame__LoadLevel",
    "0x0046dc30": "CGame__RestartLoopRunLevel",
    "0x0046e910": "CGame__Update",
}
for entry in entries:
    packet = os.path.join(out, "packet-%s.json" % entry)
    assert not os.path.exists(packet), "leftover packet: " + packet
    grade = {"present": False, "gradeBefore": None,
             "gradeAfter": None, "closureClass": None,
             "confidence": None, "source": None,
             "receiptSha256": None}
    if closure and os.path.isfile(closure):
        with open(closure, encoding="utf-8") as handle:
            header = handle.readline().rstrip("\\n").split("\\t")
            idx = {name: pos for pos, name in enumerate(header)}
            for row in handle:
                fields = row.rstrip("\\n").split("\\t")
                if fields and fields[idx["entryVa"]].lower() == entry:
                    grade = {"present": True,
                             "gradeBefore": fields[idx["gradeBefore"]],
                             "gradeAfter": fields[idx["gradeAfter"]],
                             "closureClass": fields[idx["closureClass"]],
                             "confidence": fields[idx["confidence"]],
                             "source": "closure.tsv",
                             "receiptSha256": fields[idx["receiptSha256"]]}
    if entry in names:
        body = {
            "schema": "bea.re.triage-packet.v1",
            "status": "READY",
            "requestedVa": entry,
            "entryVa": entry,
            "name": names[entry],
            "decompiled": True,
            "decompile": "void %s(void) { }" % names[entry],
            "callers": [], "callees": [], "stringRefs": [],
            "vtable": {"slotZeroDword": "00000000", "pointsToExecutable": False},
            "campaignGrade": grade,
            "executableSha256": IMAGE,
        }
    else:
        body = {
            "schema": "bea.re.triage-packet.v1",
            "status": "NOT_FUNCTION",
            "requestedVa": entry,
            "executableSha256": IMAGE,
            "section": None,
        }
    text = json.dumps(body, indent=2)
    open(packet, "w", encoding="utf-8").write(text)
manifest_packets = {}
for entry in entries:
    name = "packet-%s.json" % entry
    raw = open(os.path.join(out, name), "rb").read()
    manifest_packets[name] = {"sha256": hashlib.sha256(raw).hexdigest()}
manifest = {"schema": "bea.re.triage-run-manifest.v1",
            "executableSha256": IMAGE, "packetsWritten": len(entries),
            "programName": "BEA.exe", "programMd5": "fake-md5",
            "imageBase": "00400000", "language": "fake-x86",
            "campaignGradesSource": closure,
            "campaignGradesSha256": hashlib.sha256(open(closure, "rb").read()).hexdigest() if closure else None,
            "packets": manifest_packets}
open(os.path.join(out, "run-manifest.json"), "w", encoding="utf-8").write(
    json.dumps(manifest, indent=2))
open(ready, "w", encoding="utf-8").write(json.dumps(
    {"schema": "bea.re.triage-ready.v1", "status": "READY",
     "executableSha256": IMAGE, "packetsWritten": len(entries),
     "manifest": {"sha256": hashlib.sha256(open(os.path.join(out, "run-manifest.json"), "rb").read()).hexdigest()},
     "outputDirName": os.path.basename(out)}, indent=2))
print("TRIAGE_PACKETS_READY count=%d exe=%s" % (len(entries), IMAGE))
"""


def write_fake_headless(root: Path) -> Path:
    """An executable host-native stub; no Ghidra program is opened."""
    inner = root / "fake-headless-inner.py"
    inner.write_text(FAKE_HEADLESS_INNER.replace("IMAGE", repr(IMAGE)), encoding="utf-8")
    if os.name == "nt":
        fake = root / "fake-analyzeHeadless.bat"
        fake.write_text("@echo off\r\n" + f'"{sys.executable}" "{inner}" %*\r\n',
                        encoding="utf-8")
    else:
        fake = root / "fake-analyzeHeadless"
        fake.write_text(f"#!{sys.executable}\n" + inner.read_text(), encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return fake


def make_project(root: Path) -> Path:
    project = root / "proj"
    project.mkdir()
    (project / "BEA.gpr").write_text("fake", encoding="utf-8")
    return project


def make_output(root: Path) -> Path:
    out = root / "packets"
    out.mkdir()
    return out


def write_va_list(root: Path, vas: list[str]) -> Path:
    path = root / "addresses.txt"
    path.write_text("\n".join(vas) + "\n", encoding="utf-8")
    return path


def run_driver(extra: list[str], root: Path, fake: Path, va_list: Path,
               out: Path) -> tuple[int, str]:
    # The driver treats a passed-but-absent --closure-tsv as a refusal, so the
    # stubs always create an empty stand-in file.
    closure = root / "no-closure.tsv"
    closure.touch()
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            str(va_list),
            str(out),
            "--ghidra",
            str(fake),
            "--project-root",
            str(root / "proj"),
            "--closure-tsv",
            str(closure),
            *extra,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_tracked_va_list_parses_to_the_named_cgame_vas(root=None) -> None:
    text = VA_LIST.read_text(encoding="utf-8")
    entries = [
        line.split("#", 1)[0].strip().lower()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert entries == EXPECTED_VAS, entries


def test_current_route_requires_explicit_project_and_ghidra(root: Path) -> None:
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS[:1])
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(va_list), str(out), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 2, combined
    assert "--project-root" in combined, combined
    assert "--ghidra" in combined, combined


def test_one_run_emits_all_five_packets(root: Path) -> None:
    fake = write_fake_headless(root)
    project = make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 0, output
    for entry in EXPECTED_VAS:
        packet = out / f"packet-{entry}.json"
        assert packet.is_file(), packet
        body = json.loads(packet.read_text(encoding="utf-8"))
        assert body["schema"] == "bea.re.triage-packet.v1"
        assert body["executableSha256"] == IMAGE
    ready = json.loads((out / "triage-ready.json").read_text(encoding="utf-8"))
    assert ready["status"] == "READY"
    assert "PACKETS_OK wrote=5 skipped=0" in output, output


def test_driver_composes_read_only_invocation(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver(["--dry-run"], root, fake, va_list, out)
    assert code == 0, output
    assert "-readOnly" in output and "-noanalysis" in output, output
    assert "ExportTriagePacket.java" in output, output
    assert str(out) in output, output


def test_incremental_rerun_skips_matching_packets(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 0, output
    # A re-run must skip everything without launching headless again.
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 0, output
    assert "SKIP all 5" in output, output
    assert "PACKETS_OK" not in output, output


def test_force_recuts_after_removing_packets(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 0, output
    # The driver refuses --force while run bookkeeping exists; a real re-cut
    # starts from a clean output dir minus the packets being refreshed.
    (out / "triage-ready.json").unlink()
    (out / "run-manifest.json").unlink()
    code, output = run_driver(["--force"], root, fake, va_list, out)
    assert code == 0, output
    assert "PACKETS_OK wrote=5 skipped=0" in output, output


def test_foreign_image_packet_refuses_instead_of_overwriting(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 0, output
    # Corrupt the packet's image identity, then re-run: the driver must refuse
    # rather than silently overwrite evidence cut from a different image.
    packet = out / f"packet-{EXPECTED_VAS[0]}.json"
    body = json.loads(packet.read_text(encoding="utf-8"))
    body["executableSha256"] = "deadbeef" * 8
    packet.write_text(json.dumps(body), encoding="utf-8")
    (out / "triage-ready.json").unlink()
    (out / "run-manifest.json").unlink()
    code, output = run_driver([], root, fake, va_list, out)
    assert code == 1, output
    assert "different image" in output, output
    # And --force is the documented escape hatch.
    code, output = run_driver(["--force"], root, fake, va_list, out)
    assert code == 0, output
    body = json.loads(packet.read_text(encoding="utf-8"))
    assert body["executableSha256"] == IMAGE


def test_driver_refuses_live_project_by_default(root: Path) -> None:
    fake = write_fake_headless(root)
    live = root / "live"
    live.mkdir()
    (live / "BEA.gpr").write_text("fake", encoding="utf-8")
    # The refusal keys on the real live path; simulate by patching the module
    # constant rather than writing to C:\Users\david\Ghidra.
    source = TOOL.read_text(encoding="utf-8")
    patched = source.replace(
        'LIVE_PROJECT_ROOT = Path(r"C:\\Users\\david\\Ghidra\\Projects")',
        f"LIVE_PROJECT_ROOT = Path(r'{live}')",
    )
    assert patched != source, "live-path constant moved; update this test"
    module = root / "patched_driver.py"
    module.write_text(patched, encoding="utf-8")
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS[:1])
    (root / "no-closure.tsv").touch()
    proc = subprocess.run(
        [
            sys.executable,
            str(module),
            str(va_list),
            str(out),
            "--ghidra",
            str(fake),
            "--project-root",
            str(live),
            "--closure-tsv",
            str(root / "no-closure.tsv"),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 1, combined
    assert "live maintainer project" in combined, combined


def output_bytes(out: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in out.iterdir() if p.is_file()}


def test_dry_run_does_not_create_output_or_launch(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = root / "absent/packets"
    vas = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver(["--dry-run"], root, fake, vas, out)
    assert code == 0, output
    assert not out.parent.exists()
    assert not (root / "headless-calls.jsonl").exists()


def test_output_refuses_project_through_bind_alias(root: Path) -> None:
    fake = write_fake_headless(root)
    project = make_project(root)
    alias = root / "bind-alias"
    alias.mkdir()
    out = alias / "missing/packets"
    vas = write_va_list(root, EXPECTED_VAS[:1])
    spec = importlib.util.spec_from_file_location("export_packets_alias", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_samefile = Path.samefile

    def samefile(path, other):
        if path == alias and Path(other) == project:
            return True
        return original_samefile(path, other)

    captured = io.StringIO()
    with mock.patch.object(Path, "samefile", samefile), contextlib.redirect_stderr(captured):
        code = module.main([str(vas), str(out), "--ghidra", str(fake),
                            "--project-root", str(project), "--dry-run"])
    assert code == 1 and "outside the Ghidra project" in captured.getvalue(), captured.getvalue()
    assert list(alias.iterdir()) == []
    assert not (root / "headless-calls.jsonl").exists()


def test_force_refusal_preserves_committed_evidence(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    before = output_bytes(out)
    for flags in [["--force"], ["--force", "--dry-run"]]:
        code, output = run_driver(flags, root, fake, vas, out)
        assert code == 1 and "bookkeeping" in output, output
        assert output_bytes(out) == before
    assert len((root / "headless-calls.jsonl").read_text().splitlines()) == 1


def test_dry_run_preserves_orphan_packets_and_bookkeeping(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    packet = out / f"packet-{EXPECTED_VAS[0]}.json"
    packet.write_text(json.dumps({"executableSha256": IMAGE}))
    before = output_bytes(out)
    for flags, expected_code in [(["--dry-run"], 1), (["--dry-run", "--force"], 0)]:
        code, output = run_driver(flags, root, fake, vas, out)
        assert code == expected_code, output
        if expected_code:
            assert "unregistered packet" in output, output
        assert output_bytes(out) == before
    (out / "run-manifest.json").write_text('{"retained": true}')
    before = output_bytes(out)
    code, output = run_driver(["--dry-run"], root, fake, vas, out)
    assert code == 1 and "incomplete run bookkeeping" in output, output
    assert output_bytes(out) == before
    assert not (root / "headless-calls.jsonl").exists()


def test_unregistered_packet_requires_explicit_replacement(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    packet = out / f"packet-{EXPECTED_VAS[0]}.json"
    packet.write_text(json.dumps({"schema": "bea.re.triage-packet.v1",
                                  "executableSha256": IMAGE,
                                  "requestedVa": EXPECTED_VAS[0],
                                  "decompile": "unique retained evidence"}))
    before = output_bytes(out)
    code, output = run_driver([], root, fake, vas, out)
    assert code == 1 and "unregistered packet" in output, output
    assert output_bytes(out) == before
    assert not (root / "headless-calls.jsonl").exists()


def test_incremental_extension_refuses_unregistered_packet(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    packet = out / f"packet-{EXPECTED_VAS[1]}.json"
    packet.write_text(json.dumps({"schema": "bea.re.triage-packet.v1",
                                  "executableSha256": IMAGE,
                                  "requestedVa": EXPECTED_VAS[1],
                                  "decompile": "unique unregistered evidence"}))
    before = output_bytes(out)
    vas = write_va_list(root, EXPECTED_VAS[:2])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 1 and "unregistered packet" in output, output
    assert output_bytes(out) == before
    assert len((root / "headless-calls.jsonl").read_text().splitlines()) == 1


def test_incremental_extension_preserves_packets_and_commits_all_hashes(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    packet = out / f"packet-{EXPECTED_VAS[0]}.json"
    first = packet.read_bytes()
    vas = write_va_list(root, EXPECTED_VAS)
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0 and "wrote=4 skipped=1" in output, output
    assert packet.read_bytes() == first
    manifest_file = out / "run-manifest.json"
    manifest = json.loads(manifest_file.read_text())
    ready = json.loads((out / "triage-ready.json").read_text())
    assert ready["manifest"]["sha256"] == hashlib.sha256(manifest_file.read_bytes()).hexdigest()
    assert ready["packetsWritten"] == manifest["packetsWritten"] == 5
    for name, row in manifest["packets"].items():
        assert row["sha256"] == hashlib.sha256((out / name).read_bytes()).hexdigest()
    assert len((root / "headless-calls.jsonl").read_text().splitlines()) == 2
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0 and "SKIP all 5" in output, output


def test_failed_recut_keeps_the_original_packet(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    packet = out / f"packet-{EXPECTED_VAS[0]}.json"
    packet.write_text('{"unique old evidence": true}')
    before = packet.read_bytes()
    inner = root / "fake-headless-inner.py"
    bad = inner.read_text().replace('"status": "READY"', '"status": "FAILED"')
    inner.write_text(bad)
    if os.name != "nt":
        fake.write_text(f"#!{sys.executable}\n" + bad)
    code, output = run_driver(["--force"], root, fake, vas, out)
    assert code == 1 and "retained for review" in output, output
    assert packet.read_bytes() == before
    assert not (out / "triage-ready.json").exists()


def test_skip_requires_bound_receipts(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    manifest = out / "run-manifest.json"
    manifest.write_text(manifest.read_text() + " ")
    before = output_bytes(out)
    code, output = run_driver([], root, fake, vas, out)
    assert code == 1 and "manifest hash mismatch" in output, output
    assert output_bytes(out) == before


def test_publication_failure_restores_original_packets(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:2])
    for entry in EXPECTED_VAS[:2]:
        (out / f"packet-{entry}.json").write_text(json.dumps({"retained": entry}))
    before = output_bytes(out)
    closure = root / "empty-closure.tsv"
    closure.touch()
    spec = importlib.util.spec_from_file_location("export_packets_publication", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_replace = Path.replace
    replaced = 0

    def fail_second_packet(path: Path, target: Path) -> Path:
        nonlocal replaced
        if path.name.startswith("packet-") and Path(target).parent == out:
            replaced += 1
            if replaced == 2:
                raise OSError("injected second publication failure")
        return original_replace(path, target)

    output = io.StringIO()
    with mock.patch.object(Path, "replace", fail_second_packet), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = module.main([str(vas), str(out), "--force", "--ghidra", str(fake),
                            "--project-root", str(root / "proj"), "--closure-tsv", str(closure)])
    assert code == 1 and replaced == 2, output.getvalue()
    assert "injected second publication failure" in output.getvalue()
    assert output_bytes(out) == before


def test_extension_rechecks_an_unrequested_inherited_packet(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    before = output_bytes(out)
    victim = out / f"packet-{EXPECTED_VAS[0]}.json"
    inner = root / "fake-headless-inner.py"
    payload = f"from pathlib import Path\nPath({str(victim)!r}).write_text('changed by another writer')\n" + inner.read_text()
    inner.write_text(payload)
    if os.name != "nt":
        fake.write_text(f"#!{sys.executable}\n" + payload)
    vas = write_va_list(root, EXPECTED_VAS[1:2])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 1 and "hash mismatch" in output, output
    assert (out / "run-manifest.json").read_bytes() == before["run-manifest.json"]
    assert (out / "triage-ready.json").read_bytes() == before["triage-ready.json"]
    assert not (out / f"packet-{EXPECTED_VAS[1]}.json").exists()


def test_extension_refuses_a_different_closure_before_launch(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    vas = write_va_list(root, EXPECTED_VAS[:1])
    code, output = run_driver([], root, fake, vas, out)
    assert code == 0, output
    before = output_bytes(out)
    changed = root / "different-closure.tsv"
    changed.write_text("entryVa\tgradeAfter\n")
    vas = write_va_list(root, EXPECTED_VAS[1:2])
    code, output = run_driver(["--closure-tsv", str(changed)], root, fake, vas, out)
    assert code == 1 and "closure provenance differs" in output, output
    assert output_bytes(out) == before
    assert len((root / "headless-calls.jsonl").read_text().splitlines()) == 1


def test_native_paths_and_arguments_are_passed_without_a_shell(root: Path) -> None:
    if os.name == "nt":
        return  # Windows uses the separate guarded batch contract below.
    nested = root / "space ; literal"
    nested.mkdir()
    fake = write_fake_headless(nested)
    make_project(nested)
    out = make_output(nested)
    vas = write_va_list(nested, EXPECTED_VAS[:1])
    code, output = run_driver(["--program", "BEA name;literal.exe"], nested, fake, vas, out)
    assert code == 0, output
    args = json.loads((nested / "headless-calls.jsonl").read_text())
    assert args[args.index("-process") + 1] == "BEA name;literal.exe"


def test_windows_batch_quoting_retains_its_guard(root: Path) -> None:
    spec = importlib.util.spec_from_file_location("export_packets", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    argv = module.windows_batch_argv(root / "with space/analyzeHeadless.bat", ["safe path", "-readOnly"])
    assert argv[1:4] == ["/d", "/s", "/c"] and '"safe path"' in argv[-1], argv
    try:
        module.windows_batch_argv(root / "analyzeHeadless.bat", ["bad&argument"])
    except module.DriverError:
        pass
    else:
        raise AssertionError("Windows shell metacharacter was accepted")


def test_java_exporter_static_contract(root=None) -> None:
    java = (REPO_ROOT / "tools" / "ExportTriagePacket.java").read_text(encoding="utf-8")
    assert "getScriptArgs()" in java
    assert "TRIAGE_PACKETS_READY" in java
    assert "bea.re.triage-packet.v1" in java
    assert "bea.re.triage-ready.v1" in java
    # Read-only posture is asserted in the file's own contract banner.
    assert "-readOnly" in java and "-noanalysis" in java
    # No mutation APIs anywhere in the exporter.
    for forbidden in (
        "setName(",
        "setSignature(",
        "setComment(",
        "createFunction(",
        "delete(",
        "remove(",
        "startTransaction",
    ):
        assert forbidden not in java, forbidden
    # The image identity is bound in every packet header by construction.
    assert "executableSha256" in java


def test_closure_tsv_join_when_present(root: Path) -> None:
    fake = write_fake_headless(root)
    make_project(root)
    out = make_output(root)
    va_list = write_va_list(root, EXPECTED_VAS[:1])
    closure = root / "closure.tsv"
    closure.write_text(
        "entryVa\tgradeBefore\tgradeAfter\tclosureClass\tconfidence\treceiptSha256\n"
        f"{EXPECTED_VAS[0]}\tOPAQUE\tC1_CANDIDATE_PARTIAL\tSEALED_STATIC_RECEIPT\t"
        "HIGH_STATIC\t57b10550\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            str(va_list),
            str(out),
            "--ghidra",
            str(fake),
            "--project-root",
            str(root / "proj"),
            "--closure-tsv",
            str(closure),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    body = json.loads(
        (out / f"packet-{EXPECTED_VAS[0]}.json").read_text(encoding="utf-8")
    )
    assert body["campaignGrade"]["present"] is True
    assert body["campaignGrade"]["gradeAfter"] == "C1_CANDIDATE_PARTIAL"


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for test in tests:
        root = Path(tempfile.mkdtemp(prefix="p4-packets-"))
        try:
            test(root)
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
        except Exception as exc:  # unexpected: still a failure
            failed += 1
            print(f"FAIL {test.__name__}: unexpected {type(exc).__name__}: {exc}")
        finally:
            import shutil

            shutil.rmtree(root, ignore_errors=True)
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
