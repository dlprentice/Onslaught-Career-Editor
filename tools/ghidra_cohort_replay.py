#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce a completed Ghidra cohort ceremony through the shared framework.

This is the proof harness for tools/GhidraApplyCohortManifest.java.  For each
completed cohort it rebuilds a replica byte-for-byte from the off-volume PRE
backup on D:, runs the framework's ceremony modes against it, and compares the
receipts to the numbers the original one-shot applier recorded.

CONTAINMENT.  Everything this harness writes lives under the ephemeral rehearsal
lane in the scratchpad plus the ignored receipt lane under local-lab/.  The live
maintainer project (C:\\Users\\david\\Ghidra\\Projects), the tracked snapshot
(reverse-engineering/ghidra) and the pristine specimen are never opened for
writing, and the D: backups are only ever read.  The framework itself refuses any
project path that is not inside a "cohort-rehearsal" segment, so a replica is the
only thing it can open.

Usage:
  python tools/ghidra_cohort_replay.py --cohort boundary-cohort41
  python tools/ghidra_cohort_replay.py --cohort all --steps identity,dry,apply,readback
  python tools/ghidra_cohort_replay.py --cohort abi-cohort294 --steps census
  python tools/ghidra_cohort_replay.py --sandbox        # build the standing sandbox
  python tools/ghidra_cohort_replay.py --verdict        # grade what has been run
  python tools/ghidra_cohort_replay.py --probes varargs # the varargs controls

REHEARSAL vs REPRODUCTION.  `COHORTS` holds both: a completed ceremony is graded
against its archived receipts, while a `rehearsalOnly` cohort has no archive and
a clean run is reported as REHEARSED_NOT_PROMOTED.  Nothing here authorizes a
live apply; the live twin's compiled cohort allowlist is the only authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
SPECS = TOOLS / "cohort-specs"

GHIDRA = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC"
    r"\support\analyzeHeadless.bat")
BACKUPS = Path(r"D:\BEA-Ghidra-Backups")

# The ephemeral rehearsal lane.  The path segment "cohort-rehearsal" is what the
# framework's containment gate requires; renaming it makes every run refuse.
LANE = Path(
    r"C:\Users\david\AppData\Local\Temp\claude"
    r"\C--Users-david-source-Onslaught-Career-Editor"
    r"\6174219b-0c29-4056-883b-580c862ff182\scratchpad\cohort-rehearsal")
RECEIPTS = REPO / "local-lab" / "ghidra-cohort-framework" / "receipts"
MANIFESTS = REPO / "local-lab" / "ghidra-cohort-framework" / "manifests"

SANDBOX = REPO / "local-lab" / "ghidra-noncanonical-sandbox"

SCRIPT = "GhidraApplyCohortManifest.java"

# Paths that must never be written by this harness.
FORBIDDEN_WRITE_ROOTS = [
    Path(r"C:\Users\david\Ghidra\Projects"),
    REPO / "reverse-engineering" / "ghidra",
    REPO / "local-lab" / "safe-copy-bea-pristine",
    REPO / "local-lab" / "pristine-verification-2026-07-26",
]

COHORTS: dict[str, dict] = {
    "boundary-cohort41": {
        # db.18619-era PRE backup: the state the boundary cohort was pinned to.
        "backup": BACKUPS / "2026-08-17-boundary-cohort41-pre-live-v2",
        "spec": SPECS / "boundary-cohort41.spec.tsv",
        "manifest": (REPO / "reverse-engineering" / "binary-analysis"
                     / "boundary-cohort41-promotion-manifest-2026-08-16.tsv"),
        # what the completed ceremony recorded
        "archived": {
            "source": "v3-applier/receipts/cycle-a/{apply,readback}.json "
                      "(replica-a, byte-identical to the live V4 receipts) and "
                      "the cca31d04 promotion commit",
            "rows": 41,
            "applied": 41,
            "preFunctions": 8329, "postFunctions": 8329,
            "preInstructions": 551143, "postInstructions": 551232,
            "preReferences": 234478, "postReferences": 234493,
            "preBookmarks": 2303, "postBookmarks": 2301,
            "preDefinedData": 48585, "postDefinedData": 48583,
            "preUndefinedData": 3907903, "postUndefinedData": 3907629,
            "bookmarksRemoved": 15,
            "clearedUnits": 25,
        },
    },
    "name-cohort160": {
        "backup": BACKUPS / "2026-08-17-name-cohort160-pre-live",   # db.18620
        "spec": SPECS / "name-cohort160.spec.tsv",
        "manifest": (REPO / "reverse-engineering" / "binary-analysis"
                     / "name-cohort-promotion-manifest-2026-08-17.tsv"),
        "archived": {
            "source": "name-cohort/receipts/33-live-apply.json and "
                      "34-live-readback.json",
            "rows": 160,
            "applied": 158,          # 158 functions + 2 labels
            "preFunctions": 8329, "postFunctions": 8329,
            "preInstructions": 551232, "postInstructions": 551232,
            "preReferences": 234493, "postReferences": 234493,
            "preBookmarks": 2301, "postBookmarks": 2301,
            "preDefinedData": 48583, "postDefinedData": 48583,
            "preUndefinedData": 3907629, "postUndefinedData": 3907629,
            "symbolsPre": 26096, "symbolsPost": 26096,
            "symbolsAdded": 160, "symbolsRemoved": 160,
            "functionNameDigestPost":
                "ee545445dc497fc993bd506ea47c1a9dbe59bbfc364f6c7c54393f61d9eccd66",
            "memoryDigest":
                "8b351ad844a48ef88657a4433d4bf632c4ef6d2db5044af99ef938632b66908f",
        },
    },
    "abi-cohort294": {
        "backup": BACKUPS / "2026-08-17-abi-signature-cohort294-pre-live",  # 18621
        "spec": SPECS / "abi-cohort294.spec.tsv",
        "manifest": MANIFESTS / "abi-signature-manifest-2026-08-17.tsv",
        "archived": {
            "source": "abi-cohort/live-receipts/apply.json and readback.json",
            "rows": 294,
            "applied": 294,
            "preFunctions": 8329, "postFunctions": 8329,
            "preInstructions": 551232, "postInstructions": 551232,
            "preReferences": 234493, "postReferences": 234493,
            "preBookmarks": 2301, "postBookmarks": 2301,
            "preDefinedData": 48583, "postDefinedData": 48583,
            "preUndefinedData": 3907629, "postUndefinedData": 3907629,
            "signaturesChanged": 294,
            "signaturesUntouched": 8035,
            "memoryDigest":
                "8b351ad844a48ef88657a4433d4bf632c4ef6d2db5044af99ef938632b66908f",
            "symbolDigest":
                "f092e8b3423f0ad9af037467f6c7ae049d42db1e9769451961dc957ab9174e47",
            "bookmarkDigest":
                "1885b7dfb591c7bddddcc633a16d43d2c6ed20ea142e4e720ef2a2240018f147",
            "definedDataDigest":
                "349804e42641df9bd4c5b158b5741b3bdfb76af54191187fe98df325852f932a",
        },
    },
}

SANDBOX_BACKUP = BACKUPS / "2026-08-17-abi-signature-cohort294-post-live"

# ---------------------------------------------------------------------------
# Completed cohorts that started as rehearsal-only and were later promoted.
# varargs-cohort2 was rehearsed 2026-08-17 against db.18623 and promoted
# 2026-08-18 against a fresh db.18627 PRE. The live twin's compiled allowlist
# is still the only live authorization.
REHEARSAL_COHORTS: dict[str, dict] = {
    "varargs-cohort2": {
        # PRE is the verified off-volume backup taken immediately before the
        # 2026-08-18 live apply (db.18627). Replay against that PRE, not the
        # older tentacle-chain snapshot.
        "backup": BACKUPS / "2026-08-18-varargs-cohort2-pre-live",   # db.18627
        "spec": SPECS / "varargs-cohort2.spec.tsv",
        "manifest": (REPO / "reverse-engineering" / "binary-analysis"
                     / "varargs-cohort2-promotion-manifest-2026-08-17.tsv"),
        "rehearsalOnly": False,
        "archived": {
            "source": "local-lab/varargs-cohort2-ceremony-2026-08-18/"
                      "{apply,readback}.json (live, 2026-08-18)",
            "rows": 2,
            "applied": 2,
            "preFunctions": 8329, "postFunctions": 8329,
            "preInstructions": 551232, "postInstructions": 551232,
            "preReferences": 234558, "postReferences": 234558,
            "preBookmarks": 2301, "postBookmarks": 2301,
            "preDefinedData": 48648, "postDefinedData": 48648,
            "preUndefinedData": 3907369, "postUndefinedData": 3907369,
        },
    },
}
COHORTS.update(REHEARSAL_COHORTS)


# --------------------------------------------------------------------- utils

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path) -> tuple[str, int, int]:
    """Provenance ONLY - never an oracle for "nothing changed".

    Measured (developer_state `_MATERIAL_SAFETY_FINDING_20260817_NO_HEADLESS_
    ROLLBACK`): headless writes a new db version even when the post-script
    throws or refuses, so a file-tree digest moves on any writable session
    whatever the script did.  This harness records the digest so a restore can be
    reproduced, and NEVER asserts equality on it.  The oracle is the framework's
    own semantic proof: the frozen-column census over all 8,329 function rows
    plus the program-scope censuses, re-read in a separate `readback` process.
    """
    rows = []
    total = 0
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "backup_manifest.json":
            size = p.stat().st_size
            total += size
            rows.append(f"{p.relative_to(root).as_posix()}\t{size}\t{sha256_file(p)}")
    digest = hashlib.sha256(("\n".join(rows)).encode("utf-8")).hexdigest()
    return digest, len(rows), total


def assert_write_allowed(dest: Path) -> None:
    resolved = dest.resolve()
    for root in FORBIDDEN_WRITE_ROOTS:
        try:
            resolved.relative_to(root.resolve())
        except (ValueError, OSError):
            continue
        raise SystemExit(f"REFUSING to write inside a protected owner: {root}")


def restore(dest: Path, backup: Path) -> tuple[str, int, int]:
    assert_write_allowed(dest)
    if not backup.exists():
        raise SystemExit(f"backup missing: {backup}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for p in sorted(backup.rglob("*")):
        if p.is_file() and p.name != "backup_manifest.json":
            out = dest / p.relative_to(backup)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
    return tree_digest(dest)


def headless(tag: str, project: Path, args: list[str], readonly: bool,
             logdir: Path, timeout: int = 7200) -> tuple[int, list[str], str]:
    logdir.mkdir(parents=True, exist_ok=True)
    cmd = [str(GHIDRA), str(project), "BEA", "-process", "BEA.exe", "-noanalysis"]
    if readonly:
        cmd.append("-readOnly")
    cmd += ["-scriptPath", str(TOOLS), "-postScript", SCRIPT] + args
    t0 = time.time()
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    combined = (cp.stdout or "") + "\n" + (cp.stderr or "")
    (logdir / f"{tag}.log").write_text(combined, encoding="utf-8", errors="replace")
    marks = ("COHORT_", "ERROR ", "Exception", "REFUSE", "SCRIPT ERROR")
    hits = [l.split("> ", 1)[-1].rstrip() for l in combined.splitlines()
            if any(m in l for m in marks)]
    rc = cp.returncode
    # analyzeHeadless exits 0 even when a post-script throws, so promote that
    if rc == 0 and "SCRIPT ERROR" in combined:
        rc = 90
    print(f"  [{tag}] exit={rc} {round(time.time() - t0, 1)}s")
    for line in hits[:40]:
        print("     ", line[:220])
    return rc, hits, combined


# ----------------------------------------------------------------- ceremony

STEP_MODES = {
    "census": ("census", True),
    "identity": ("identity", True),
    "dry": ("dry", True),
    "apply": ("apply", False),
    "readback": ("readback", True),
    "collateral": ("collateral", True),
}


def run_cohort(name: str, steps: list[str]) -> int:
    cfg = COHORTS[name]
    spec: Path = cfg["spec"]
    manifest: Path = cfg["manifest"]
    if not manifest.exists():
        raise SystemExit(f"manifest missing: {manifest}")
    spec_sha = sha256_file(spec)
    replica = LANE / "replicas" / name
    logs = LANE / "logs" / name
    out = RECEIPTS / name
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {name}")
    print(f"  spec      {spec.name} sha256={spec_sha}")
    print(f"  manifest  {manifest.name} sha256={sha256_file(manifest)}")

    fresh_needed = any(s in ("identity", "dry", "apply", "census") for s in steps)
    if fresh_needed and "readback" not in steps[:1]:
        digest, files, total = restore(replica, cfg["backup"])
        print(f"  replica   {replica}")
        print(f"  restored  files={files} bytes={total} treeDigest={digest}")
        (out / "replica-pre-tree.json").write_text(json.dumps({
            "backup": str(cfg["backup"]),
            "replica": str(replica),
            "files": files, "bytes": total, "treeDigest": digest,
        }, indent=2), encoding="utf-8")

    rc_total = 0
    for step in steps:
        mode, readonly = STEP_MODES[step]
        # A stale receipt from a previous run must never be reported as this
        # run's result: the framework only writes one when it gets far enough.
        for suffix in (".json", ".tsv"):
            stale = out / f"{step}{suffix}"
            if stale.exists():
                stale.unlink()
        args = [str(spec), spec_sha, str(manifest), mode,
                str(out / f"{step}.json"), str(out / f"{step}.tsv")]
        rc, _hits, _log = headless(step, replica, args, readonly, logs)
        rc_total |= rc
        receipt = out / f"{step}.json"
        if not receipt.exists():
            print("      NO RECEIPT WRITTEN - the script did not reach emit; "
                  "see the log")
            rc_total |= 1
        else:
            got = json.loads(receipt.read_text(encoding="utf-8"))
            print(f"     result={got.get('result')} committed={got.get('committed')}"
                  f" writesAttempted={got.get('writesAttempted')}")
            if got.get("result") != "PASS" and mode != "census":
                for f in got.get("failures", [])[:10]:
                    print("      FAIL:", f[:200])
                rc_total |= 1
    if "apply" in steps:
        digest, files, total = tree_digest(replica)
        (out / "replica-post-tree.json").write_text(json.dumps({
            "replica": str(replica), "files": files, "bytes": total,
            "treeDigestForProvenanceOnly": digest,
            "isThisAnOracle": False,
            "why": "headless advances the db version on any writable session, "
                   "even when the script refuses and writes nothing "
                   "(_MATERIAL_SAFETY_FINDING_20260817_NO_HEADLESS_ROLLBACK), "
                   "so file digests cannot show 'nothing changed'",
            "theOracleIs": "the framework's semantic proof: the frozen-column "
                           "census over all 8329 function rows plus the "
                           "program-scope symbol/bookmark/definedData/memory "
                           "censuses, re-read by the separate-process readback",
        }, indent=2), encoding="utf-8")
    return rc_total


# ------------------------------------------------------------------- probes

def _doctor(path: Path, edits: list[tuple[str, str]], dest: Path) -> Path:
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        if old not in text:
            raise SystemExit(f"probe edit not found in {path.name}: {old!r}")
        text = text.replace(old, new, 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(text.encode("utf-8"))
    return dest


def _doctor_manifest(manifest: Path, edits: dict[str, dict[str, str]],
                     dest: Path) -> Path:
    """Rewrite named cells of named rows, keeping the header and shape intact."""
    rows = [l for l in manifest.read_text(encoding="utf-8").split("\n") if l]
    header = rows[0].split("\t")
    out = [rows[0]]
    seen: set[str] = set()
    for line in rows[1:]:
        cells = line.split("\t")
        want = edits.get(cells[0])
        if want:
            seen.add(cells[0])
            for column, value in want.items():
                cells[header.index(column)] = value
        out.append("\t".join(cells))
    missing = set(edits) - seen
    if missing:
        raise SystemExit(f"probe edit targets no manifest row: {missing}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(("\n".join(out) + "\n").encode("utf-8"))
    return dest


def _repin_spec(spec: Path, manifest: Path, dest: Path,
                extra: list[tuple[str, str]] | None = None) -> Path:
    """Point a spec at a doctored manifest by re-deriving only its pins.

    Every other gate stays enforced - this is not a relaxation mode.  Without it
    a doctored manifest would refuse on the digest pin and the gate under test
    would never be reached.
    """
    raw = manifest.read_bytes()
    text = spec.read_text(encoding="utf-8")
    swaps = [
        ("manifestSha256\t", hashlib.sha256(raw).hexdigest()),
        ("manifestBytes\t", str(len(raw))),
    ]
    for key, value in swaps:
        old = [l for l in text.split("\n") if l.startswith(key)]
        if len(old) != 1:
            raise SystemExit(f"cannot re-pin {key} in {spec.name}")
        text = text.replace(old[0], key + value, 1)
    for old, new in (extra or []):
        if old not in text:
            raise SystemExit(f"spec edit not found in {spec.name}: {old!r}")
        text = text.replace(old, new, 1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(text.encode("utf-8"))
    return dest


# The one-row PRESERVE control.  Its target already carries varargs=true in the
# database (measured 2026-08-17: 10 of 8,329 functions do), and the control's
# manifest has NO varargs column at all, so "absent means do not touch" is
# exercised against a real variadic function rather than argued.  The proposal is
# a deliberately trivial parameter rename: it exists only to make the row a
# non-no-op so the prototype path actually runs, and it is never promoted.
PRESERVE_CONTROL_ADDR = "0x00441740"
PRESERVE_CONTROL_HEADER = (
    "addr\tliveName\tcurrentSignatureLive\tproposedSignature\tcallingConvention"
    "\treturnTypeProposed\tparamSpec\tarity\tarityBytes\tconfidence")
PRESERVE_CONTROL_ROW = (
    "0x00441740\tCConsole__Printf"
    "\tvoid __cdecl CConsole__Printf(void * console, char * format, ...)"
    "\tvoid __cdecl CConsole__Printf(void * console, char * fmt, ...)"
    "\t__cdecl\tvoid"
    "\tSTACK:void *:console:expl;STACK:char *:fmt:expl\t2\t8\tHIGH")


def _preserve_control_inputs(work: Path) -> tuple[Path, Path]:
    """A spec+manifest pair that never mentions varargs, written to the lane."""
    manifest = work / "varargs-preserve-control.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_bytes(
        (PRESERVE_CONTROL_HEADER + "\n" + PRESERVE_CONTROL_ROW + "\n")
        .encode("utf-8"))
    raw = manifest.read_bytes()
    base = read_spec_text(SPECS / "varargs-cohort2.spec.tsv")
    spec_lines = [
        l for l in base.split("\n")
        if not l.startswith(("cohortId\t", "cohortTitle\t", "manifestSha256\t",
                             "manifestBytes\t", "manifestRows\t",
                             "manifestColumns\t", "manifestHeaderPipe\t",
                             "col.", "expectedTargetsChanged\t",
                             "expectedFunctionsUntouched\t", "constant\t",
                             "enum\t", "unique\t"))
    ]
    spec_lines += [
        "cohortId\tvarargs-preserve-control",
        "cohortTitle\tPRESERVE control: no varargs column at all",
        f"manifestSha256\t{hashlib.sha256(raw).hexdigest()}",
        f"manifestBytes\t{len(raw)}",
        "manifestRows\t1",
        "manifestColumns\t10",
        "manifestHeaderPipe\t" + "|".join(PRESERVE_CONTROL_HEADER.split("\t")),
        "col.addr\taddr",
        "col.liveName\tliveName",
        "col.currentSignature\tcurrentSignatureLive",
        "col.proposedSignature\tproposedSignature",
        "col.callingConvention\tcallingConvention",
        "col.returnType\treturnTypeProposed",
        "col.paramSpec\tparamSpec",
        "col.arity\tarity",
        "col.arityBytes\tarityBytes",
        "unique\taddr",
        "expectedTargetsChanged\t1",
        "expectedFunctionsUntouched\t8328",
    ]
    spec = work / "varargs-preserve-control.spec.tsv"
    spec.write_bytes(("\n".join(spec_lines) + "\n").encode("utf-8"))
    return spec, manifest


def read_spec_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_varargs_controls() -> int:
    """Execute the varargs negative controls and the PRESERVE positive control.

    Every one of these is a real headless run on a replica restored from the
    off-volume PRE backup.  The negatives must REFUSE for their own reason and
    must not commit; the positive must PASS and leave varargs=true untouched,
    proven by a separate-process readback.
    """
    cfg = COHORTS["varargs-cohort2"]
    spec, manifest = cfg["spec"], cfg["manifest"]
    if not manifest.exists():
        raise SystemExit(f"manifest missing: {manifest}")
    work = LANE / "probes"
    out = RECEIPTS / "probes"
    out.mkdir(parents=True, exist_ok=True)
    logs = LANE / "logs" / "probes"

    # -- doctored inputs, all written into the ephemeral lane -----------------
    m_false = _doctor_manifest(manifest, {"0x0042b840": {
        "varargs": "false",
        "proposedSignature":
            "void __cdecl CConsole__AddString(void * console, char * format)",
        "paramSpec": "STACK:void *:console:expl;STACK:char *:format:expl",
    }}, work / "varargs-asked-false.tsv")
    # The tracked spec pins `constant varArgs=true` - the axis this cohort exists
    # for - so an asked-false row would refuse on that pin BEFORE the write and
    # the POST gate under test would never run.  Dropping exactly that one
    # cohort-specific pin is the whole relaxation; every framework gate stays on.
    s_false = _repin_spec(spec, m_false, work / "varargs-asked-false.spec.tsv",
                          extra=[("constant\tvarArgs=true\n", "")])
    m_illegal = _doctor_manifest(manifest, {"0x0055de9b": {"varargs": "yes"}},
                                 work / "varargs-illegal.tsv")
    s_illegal = _repin_spec(spec, m_illegal, work / "varargs-illegal.spec.tsv")
    m_disagree = _doctor_manifest(manifest, {"0x0055de9b": {"varargs": "false"}},
                                  work / "varargs-disagree.tsv")
    s_disagree = _repin_spec(spec, m_disagree,
                             work / "varargs-disagree.spec.tsv")
    p_spec, p_manifest = _preserve_control_inputs(work)
    # provenance: a spec may pin the applier's own source digest, and a pin that
    # matches nothing must refuse before any write.
    s_applier = _repin_spec(
        spec, manifest, work / "varargs-bad-applier.spec.tsv",
        extra=[("verb\tSET_PROTOTYPE",
                "applierSha256\t" + "00" * 32 + "\nverb\tSET_PROTOTYPE")])

    negatives = [
        # tag, spec, manifest, mode, writable, expected refusal
        ("p11-varargs-asked-true-written-false", spec, manifest,
         "probe-fault-varargsflip", True,
         "POST varargs expected [true] actual [false]"),
        ("p12-varargs-asked-false-written-true", s_false, m_false,
         "probe-fault-varargsflip", True,
         "POST varargs expected [false] actual [true]"),
        ("p13-varargs-preserve-true-stripped", p_spec, p_manifest,
         "probe-fault-varargsflip", True,
         "POST varargs expected [true] actual [false] (PRESERVE: the PRE value)"),
        ("p14-varargs-illegal-value", s_illegal, m_illegal, "dry", False,
         "illegal varargs value"),
        ("p15-varargs-signature-disagree", s_disagree, m_disagree, "dry", False,
         "varargs/proposedSignature disagree"),
        ("p16-applier-sha-pin", s_applier, manifest, "dry", False,
         "APPLIER SHA PIN"),
    ]

    results = []
    for tag, sp, mf, mode, writable, expect in negatives:
        replica = LANE / "replicas" / (f"varargs-{tag}" if writable
                                       else "varargs-probe-clean")
        if writable or not replica.exists():
            restore(replica, cfg["backup"])
        args = [str(sp), sha256_file(sp), str(mf), mode,
                str(out / f"{tag}.json"), str(out / f"{tag}.tsv")]
        for suffix in (".json", ".tsv"):
            stale = out / f"{tag}{suffix}"
            if stale.exists():
                stale.unlink()
        rc, _hits, log = headless(tag, replica, args, not writable, logs)
        refused = expect in log
        applied_anyway = False
        receipt = out / f"{tag}.json"
        if receipt.exists():
            got = json.loads(receipt.read_text(encoding="utf-8"))
            applied_anyway = bool(got.get("committed"))
            if got.get("result") == "PASS":
                refused = False
        undetected = "COHORT_FAULT_UNDETECTED" in log
        results.append(dict(probe=tag, mode=mode, expect=expect,
                            refusalObserved=refused,
                            appliedAnyway=applied_anyway,
                            faultUndetected=undetected,
                            verdict="REFUSED" if refused and not applied_anyway
                                    and not undetected else "NOT_REFUSED"))
        print(f"     -> {results[-1]['verdict']} (expected {expect!r})")
        if writable:
            shutil.rmtree(replica, ignore_errors=True)

    # -- the positive control: silence must PRESERVE varargs=true ------------
    control = dict(control="c01-varargs-preserved-by-silence",
                   target=PRESERVE_CONTROL_ADDR,
                   spec=str(p_spec), manifest=str(p_manifest))
    replica = LANE / "replicas" / "varargs-preserve-control"
    restore(replica, cfg["backup"])
    for step, mode, readonly in (("apply", "apply", False),
                                 ("readback", "readback", True)):
        tag = f"c01-preserve-{step}"
        args = [str(p_spec), sha256_file(p_spec), str(p_manifest), mode,
                str(out / f"{tag}.json"), str(out / f"{tag}.tsv")]
        rc, _hits, _log = headless(tag, replica, args, readonly, logs)
        receipt = out / f"{tag}.json"
        got = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() \
            else {}
        if step == "apply":
            control["result"] = got.get("result")
            control["committed"] = bool(got.get("committed"))
            control["varargsColumnBound"] = got.get("varargsColumnBound")
            control["failures"] = got.get("failures", [])[:5]
        else:
            control["readbackResult"] = got.get("result")
        tsv = out / f"{tag}.tsv"
        if tsv.exists():
            rows = [l.split("\t") for l in
                    tsv.read_text(encoding="utf-8").split("\n") if l]
            head = rows[0]
            row = rows[1]
            if step == "apply":
                control["varArgsPre"] = row[head.index("varArgsPre")]
                control["varArgsWanted"] = row[head.index("varArgsWanted")]
                control["renderedKeepsVariadicTail"] = row[
                    head.index("rendered")].endswith(", ...)")
            control["varArgsPost"] = row[head.index("varArgsPost")]
    control["verdict"] = ("PRESERVED"
                          if control.get("result") == "PASS"
                          and control.get("readbackResult") == "PASS"
                          and control.get("varArgsPre") == "true"
                          and control.get("varArgsWanted") == "PRESERVE"
                          and control.get("varArgsPost") == "true"
                          and control.get("renderedKeepsVariadicTail")
                          else "NOT_PRESERVED")
    print(f"     -> {control['verdict']} (silence must leave varargs=true)")
    shutil.rmtree(replica, ignore_errors=True)

    _merge_matrix(out / "matrix.json", results, [control])
    bad = [r for r in results if r["verdict"] != "REFUSED"]
    if control["verdict"] != "PRESERVED":
        bad.append(control)
    print(f"\nvarargs controls={len(results) + 1} "
          f"failed={len(bad)}")
    for r in bad:
        print("   FAILED CONTROL:", r.get("probe") or r.get("control"))
    return 0 if not bad else 1


def _merge_matrix(path: Path, probes: list[dict],
                  controls: list[dict] | None = None) -> None:
    """Add these results to the standing matrix instead of replacing it.

    The framework's own 15 probes and these varargs controls are separate runs;
    overwriting would silently retire proof that is still valid.
    """
    existing: dict = {"probes": [], "positiveControls": []}
    if path.exists():
        existing.update(json.loads(path.read_text(encoding="utf-8")))
    existing.setdefault("positiveControls", [])
    fresh = {p["probe"] for p in probes}
    existing["probes"] = [p for p in existing["probes"]
                          if p["probe"] not in fresh] + probes
    if controls:
        names = {c["control"] for c in controls}
        existing["positiveControls"] = [
            c for c in existing["positiveControls"]
            if c.get("control") not in names] + controls
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def run_probes(which: str) -> int:
    """Provoke gates with real headless runs, and require each to refuse.

    A gate whose refusal text merely exists in the source is not a gate you have
    tested.  These runs break one input at a time and require the framework to
    refuse for that specific reason.
    """
    work = LANE / "probes"
    work.mkdir(parents=True, exist_ok=True)
    out = RECEIPTS / "probes"
    out.mkdir(parents=True, exist_ok=True)
    logs = LANE / "logs" / "probes"

    name = COHORTS["name-cohort160"]
    boundary = COHORTS["boundary-cohort41"]
    name_spec, name_manifest = name["spec"], name["manifest"]
    b_spec, b_manifest = boundary["spec"], boundary["manifest"]

    # replicas: one clean PRE, plus the already-applied name replica for the
    # staleness probe.
    clean = LANE / "replicas" / "probe-clean"
    if not clean.exists():
        restore(clean, name["backup"])
    applied = LANE / "replicas" / "name-cohort160"

    cases: list[dict] = []

    def case(tag: str, project: Path, spec: Path, sha: str, manifest: Path,
             mode: str, expect: str, nargs: int = 6) -> None:
        cases.append(dict(tag=tag, project=project, spec=spec, sha=sha,
                          manifest=manifest, mode=mode, expect=expect,
                          nargs=nargs))

    ns = sha256_file(name_spec)
    if which in ("core", "all"):
        # containment: the standing sandbox has no cohort-rehearsal segment, so
        # the gated applier must refuse to open it.  This is the sandbox README's
        # claim, executed.
        sandbox_project = SANDBOX / "project"
        if sandbox_project.exists():
            case("p01-containment-sandbox", sandbox_project, name_spec, ns,
                 name_manifest, "identity",
                 "reason=project_not_in_rehearsal_scratch")
        case("p02-spec-sha-pin", clean, name_spec, "00" * 32, name_manifest,
             "identity", "SPEC SHA PIN")
        case("p03-bad-mode", clean, name_spec, ns, name_manifest, "frobnicate",
             "reason=bad_mode")
        case("p04-usage-arity", clean, name_spec, ns, name_manifest, "identity",
             "reason=usage", nargs=3)
        doc = _doctor(name_spec, [("verb\tSET_NAME", "hax\t1\nverb\tSET_NAME")],
                      work / "p05-unknown-key.spec.tsv")
        case("p05-spec-unknown-key", clean, doc, sha256_file(doc), name_manifest,
             "identity", "SPEC UNKNOWN KEY")
        doc = _doctor(name_spec, [("verb\tSET_NAME", "verb\tSET_EVERYTHING")],
                      work / "p06-unknown-verb.spec.tsv")
        case("p06-spec-unknown-verb", clean, doc, sha256_file(doc),
             name_manifest, "dry", "SPEC UNKNOWN VERB")
        doc = _doctor(name_spec, [("preInstructions\t551232",
                                   "preInstructions\t551231")],
                      work / "p07-weak-pin.spec.tsv")
        case("p07-pre-instruction-pin", clean, doc, sha256_file(doc),
             name_manifest, "identity", "PRE instruction count")
        doc = _doctor(b_spec, [("verb\tSET_BODY\n", "")],
                      work / "p08-undeclared-verb.spec.tsv")
        case("p08-verb-not-declared", clean, doc, sha256_file(doc), b_manifest,
             "dry", "VERB NOT DECLARED")
        bad_manifest = _doctor(
            name_manifest, [("0x00402dd0", "0x00402dd1")],
            work / "p09-bad-manifest.tsv")
        case("p09-manifest-sha-pin", clean, name_spec, ns, bad_manifest, "dry",
             "manifest sha256")
        if applied.exists():
            case("p10-current-state-staleness", applied, name_spec, ns,
                 name_manifest, "dry", "CURRENT name expected")

    fault_modes = ["probe-fault-strandbytes", "probe-fault-precedentclear",
                   "probe-fault-escape", "probe-fault-extraclear",
                   "probe-fault-clearescape"]
    fault_expect = {
        "probe-fault-strandbytes": "UNCLASSIFIED BYTES REMAIN",
        "probe-fault-precedentclear": "CLASSIFIED-BYTE REGRESSION",
        "probe-fault-escape": "INSTRUCTION ESCAPE:",
        "probe-fault-extraclear": "CLEAR PLAN MISMATCH",
        "probe-fault-clearescape": "CLEAR ESCAPED the admitted range",
    }

    results = []
    for c in cases:
        args = [str(c["spec"]), c["sha"], str(c["manifest"]), c["mode"],
                str(out / f"{c['tag']}.json"), str(out / f"{c['tag']}.tsv")]
        args = args[:c["nargs"]]
        rc, hits, log = headless(c["tag"], c["project"], args, True, logs)
        refused = c["expect"] in log
        receipt = out / f"{c['tag']}.json"
        applied_anyway = False
        if receipt.exists():
            got = json.loads(receipt.read_text(encoding="utf-8"))
            applied_anyway = bool(got.get("committed"))
            if got.get("result") == "PASS" and c["mode"] != "frobnicate":
                refused = False
        results.append(dict(probe=c["tag"], mode=c["mode"], expect=c["expect"],
                            refusalObserved=refused,
                            appliedAnyway=applied_anyway,
                            verdict="REFUSED" if refused and not applied_anyway
                                    else "NOT_REFUSED"))
        print(f"     -> {results[-1]['verdict']} (expected {c['expect']!r})")

    if which in ("fault", "all"):
        bs = sha256_file(b_spec)
        for mode in fault_modes:
            tag = mode
            replica = LANE / "replicas" / f"fault-{mode}"
            restore(replica, boundary["backup"])
            args = [str(b_spec), bs, str(b_manifest), mode,
                    str(out / f"{tag}.json"), str(out / f"{tag}.tsv")]
            rc, hits, log = headless(tag, replica, args, False, logs)
            expect = fault_expect[mode]
            refused = expect in log
            applied_anyway = False
            receipt = out / f"{tag}.json"
            if receipt.exists():
                got = json.loads(receipt.read_text(encoding="utf-8"))
                applied_anyway = bool(got.get("committed"))
                if got.get("result") == "PASS":
                    refused = False
            undetected = "COHORT_FAULT_UNDETECTED" in log
            results.append(dict(probe=tag, mode=mode, expect=expect,
                                refusalObserved=refused,
                                appliedAnyway=applied_anyway,
                                faultUndetected=undetected,
                                verdict="REFUSED"
                                        if refused and not applied_anyway
                                           and not undetected
                                        else "NOT_REFUSED"))
            print(f"     -> {results[-1]['verdict']} (expected {expect!r})")
            shutil.rmtree(replica, ignore_errors=True)

    _merge_matrix(out / "matrix.json", results)
    bad = [r for r in results if r["verdict"] != "REFUSED"]
    print(f"\nprobes={len(results)} refused={len(results) - len(bad)} "
          f"notRefused={len(bad)}")
    for r in bad:
        print("   NOT REFUSED:", r["probe"], r["expect"])
    return 0 if not bad else 1


# ------------------------------------------------------------------ verdict

def verdict() -> int:
    problems = 0
    report: dict[str, dict] = {}
    for name, cfg in COHORTS.items():
        arch = cfg["archived"]
        out = RECEIPTS / name
        apply_json = out / "apply.json"
        read_json = out / "readback.json"
        entry: dict[str, object] = {"archivedSource": arch["source"]}
        if not apply_json.exists():
            entry["status"] = "NOT_RUN"
            report[name] = entry
            continue
        got = json.loads(apply_json.read_text(encoding="utf-8"))
        counts = got.get("counts", {})
        checks: list[tuple[str, object, object, bool]] = []

        def cmp(label: str, want: object, actual: object) -> None:
            checks.append((label, want, actual, want == actual))

        cmp("result", "PASS", got.get("result"))
        cmp("committed", True, got.get("committed"))
        cmp("cohortId", name, got.get("cohortId"))
        cmp("reversibility",
            "CEREMONY_LEVEL_RESTORE_FROM_VERIFIED_PRE_BACKUP",
            got.get("reversibility"))
        cmp("rows", arch["rows"], counts.get("rows"))
        for key in ("preFunctions", "postFunctions", "preInstructions",
                    "postInstructions", "preReferences", "postReferences",
                    "preBookmarks", "postBookmarks", "preDefinedData",
                    "postDefinedData", "preUndefinedData", "postUndefinedData"):
            if key in arch:
                cmp(key, arch[key], counts.get(key))
        collateral = got.get("collateral") or ""
        fields = dict(
            tok.split("=", 1) for tok in collateral.split() if "=" in tok)
        if "applied" in arch:
            cmp("functionsChanged", str(arch["applied"]),
                fields.get("functionsChanged"))
        if "signaturesUntouched" in arch:
            cmp("functionsUntouched", str(arch["signaturesUntouched"]),
                fields.get("functionsUntouched"))
        if "symbolsAdded" in arch:
            cmp("symbolsAdded", str(arch["symbolsAdded"]),
                fields.get("symbolsAdded"))
            cmp("symbolsRemoved", str(arch["symbolsRemoved"]),
                fields.get("symbolsRemoved"))
        if "symbolsPre" in arch:
            cmp("symbolsPre", str(arch["symbolsPre"]), fields.get("symbolsPre"))
            cmp("symbolsPost", str(arch["symbolsPost"]), fields.get("symbolsPost"))
        if "memoryDigest" in arch:
            cmp("memoryDigest", arch["memoryDigest"], fields.get("memoryDigest"))
        if "symbolDigest" in arch:
            # NOT comparable by design: the framework's symbol census is a
            # superset of the ABI applier's (it adds the simple name and the
            # parent namespace), so its digest is a different serialisation of
            # the same table.  The comparable claim - "the non-dynamic symbol
            # census did not change at all" - is gated inside the framework, and
            # the row count is compared below.
            entry["symbolDigestNote"] = (
                "framework symbol census is a superset of the 2026-08-17 ABI "
                f"applier's; archived={arch['symbolDigest']} "
                f"framework={fields.get('symbolDigestPost')} - different "
                "serialisation, not a behavioural divergence")
        if "bookmarkDigest" in arch:
            cmp("bookmarkDigest", arch["bookmarkDigest"],
                fields.get("bookmarkDigestPost"))
        if "definedDataDigest" in arch:
            cmp("definedDataDigest", arch["definedDataDigest"],
                fields.get("definedDataDigestPost"))
        if "bookmarksRemoved" in arch:
            note = " ".join(got.get("notes", []))
            cmp("bookmarksRemoved", True,
                f"bookmarksRemoved={arch['bookmarksRemoved']}" in note)
        if read_json.exists():
            rb = json.loads(read_json.read_text(encoding="utf-8"))
            cmp("readbackResult", "PASS", rb.get("result"))
            cmp("readbackRows", arch["rows"], rb.get("counts", {}).get("rows"))
        else:
            checks.append(("readback", "present", "MISSING", False))

        divergences = [
            {"field": lab, "archived": w, "framework": a}
            for lab, w, a, ok in checks if not ok
        ]
        entry["checks"] = len(checks)
        entry["divergences"] = divergences
        if cfg.get("rehearsalOnly"):
            # There is no completed ceremony behind these numbers, so a clean run
            # is a rehearsal, never a reproduction and never an authorization.
            entry["status"] = ("REHEARSED_NOT_PROMOTED" if not divergences
                               else "REHEARSAL_DIVERGED")
        else:
            entry["status"] = "REPRODUCED" if not divergences else "DIVERGED"
        problems += len(divergences)
        report[name] = entry

    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / "verdict.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8")
    for name, entry in report.items():
        print(f"{name:20s} {entry['status']:12s} checks={entry.get('checks', 0)}")
        for d in entry.get("divergences", []):
            print(f"    DIVERGENCE {d['field']}: archived={d['archived']!r} "
                  f"framework={d['framework']!r}")
    print(f"\ntotal divergences: {problems}")
    return 0 if problems == 0 else 1


# ------------------------------------------------------------------ sandbox

SANDBOX_README = """# NONCANONICAL_SANDBOX_NEVER_SYNC_TO_LIVE

`project/` is a disposable Ghidra project restored from the post-ABI off-volume
backup `D:\\BEA-Ghidra-Backups\\2026-08-17-abi-signature-cohort294-post-live`
(db.18622 - the same geometry the tracked snapshot carries). It exists so that
proposals can be tried without a ceremony.

**It is not evidence, and it must never be copied toward the live maintainer
project, the tracked snapshot, or any backup that a receipt pins.**

- Never `robocopy` / `xcopy` / `Copy-Item` out of this folder into
  `C:\\Users\\david\\Ghidra\\Projects` or `reverse-engineering/ghidra/`.
- Anything measured here is a hypothesis. To become evidence it has to be
  re-measured on a fresh replica through
  `tools/ghidra_cohort_replay.py`, with gates enabled and a receipt.
- Rebuild it whenever it drifts: `python tools/ghidra_cohort_replay.py --sandbox`.
  It is cheaper to rebuild than to reason about what a previous experiment left
  behind.
- Its path deliberately does NOT contain a `cohort-rehearsal` segment, so the
  gated framework applier refuses to open it. Use ungated exploration scripts
  here, and the framework only on a real rehearsal replica.

## What a sandbox buys, honestly

It catches the class of proposal that **visibly breaks something**: a manifest
row whose address has no function, a rename that collides, a prototype whose
type will not resolve, a body that overlaps a neighbour, a clear that strands
bytes. Those are cheap to find here and expensive to find in a ceremony.

It does **not** catch the larger and more dangerous class: a proposal that
**applies cleanly and is silently wrong.** A confidently misattributed class
name, a plausible-but-false parameter count, a boundary that swallows the wrong
tail - all of those apply without a single gate firing, here and in the live
database alike. Nothing in a sandbox can tell you a name is *true*; it can only
tell you Ghidra accepted it.

So a clean sandbox run is a precondition, never a verdict. The verdict still
comes from the evidence that made the row: bytes, traces, RTTI, source, a
falsifier that could have refuted it. If the only thing you can say about a row
is "it applied", it is not ready, and this folder cannot make it ready.

A second honest limit: this sandbox is a *snapshot*. The moment a real promotion
lands, its geometry is stale, and an experiment run here can pass against a PRE
state that no longer exists. Check the db version before trusting anything.
"""


def build_sandbox() -> int:
    dest = SANDBOX / "project"
    assert_write_allowed(dest)
    digest, files, total = restore(dest, SANDBOX_BACKUP)
    SANDBOX.mkdir(parents=True, exist_ok=True)
    (SANDBOX / "README.md").write_text(SANDBOX_README, encoding="utf-8")
    (SANDBOX / "NONCANONICAL_SANDBOX_NEVER_SYNC_TO_LIVE").write_text(
        "This project is a disposable experiment surface. See README.md.\n"
        f"restored from: {SANDBOX_BACKUP}\n"
        f"tree digest:   {digest}\n"
        f"files:         {files}\n"
        f"bytes:         {total}\n", encoding="utf-8")
    (SANDBOX / "provenance.json").write_text(json.dumps({
        "status": "NONCANONICAL_SANDBOX_NEVER_SYNC_TO_LIVE",
        "restoredFrom": str(SANDBOX_BACKUP),
        "files": files, "bytes": total, "treeDigest": digest,
        "dbVersionAtRestore": sorted(
            p.name for p in dest.rglob("db.*.gbf")
            if "~00000000.db" in p.as_posix()),
        "gatedApplierCanOpenIt": False,
        "reason": "the path has no cohort-rehearsal segment, so "
                  "GhidraApplyCohortManifest refuses it by containment",
    }, indent=2), encoding="utf-8")
    print(f"sandbox at {dest}")
    print(f"  files={files} bytes={total} treeDigest={digest}")
    return 0


# --------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", default=None,
                    help="one of " + ", ".join(COHORTS) + ", or 'all'")
    ap.add_argument("--steps", default="identity,dry,apply,readback")
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--verdict", action="store_true")
    ap.add_argument("--probes", default=None,
                    choices=["core", "fault", "all", "varargs"],
                    help="provoke gates with real headless runs")
    ns = ap.parse_args(argv)

    if ns.sandbox:
        return build_sandbox()
    if ns.probes == "varargs":
        return run_varargs_controls()
    if ns.probes:
        return run_probes(ns.probes)
    if ns.verdict:
        return verdict()
    if not ns.cohort:
        ap.error("need --cohort, --sandbox or --verdict")
    steps = [s.strip() for s in ns.steps.split(",") if s.strip()]
    for s in steps:
        if s not in STEP_MODES:
            ap.error(f"unknown step {s}; known: {', '.join(STEP_MODES)}")
    names = list(COHORTS) if ns.cohort == "all" else [ns.cohort]
    for n in names:
        if n not in COHORTS:
            ap.error(f"unknown cohort {n}")
    rc = 0
    for n in names:
        rc |= run_cohort(n, steps)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
