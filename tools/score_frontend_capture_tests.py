"""Self-tests for score_frontend_capture.py.

The point of task #113 was that the frontend gate could not fail for the reason
it claimed to guard. Replacing it with a gate that also cannot fail would be the
same defect in a new coat, so the central test here is the FALSIFICATION one:
inject a deliberate regression and assert the gate reports FAIL and exits
non-zero. If `test_regression_is_caught` ever passes trivially, the gate is
worthless again.

These build their own images and plan in a temp directory, so they run in a
fresh clone with no retail material present - which is also what lets the
"no reference set" case be tested rather than assumed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

TOOL = Path(__file__).resolve().parent / "score_frontend_capture.py"

W, H = 40, 30
FILL = (23, 23, 48)
CHROME = (200, 180, 90)
CHROME_BOX = (4, 4, 20, 16)
# A patch that differs between the two retail runs: retail cannot reproduce it
# itself, so a difference there must NOT be charged to the reconstruction.
ANIMATED_BOX = (24, 18, 36, 28)

OFFSETS = [0, 500, 1000]


def write_frame(path: Path, chrome: tuple[int, int, int], animated: int) -> None:
    img = Image.new("RGB", (W, H), FILL)
    for x in range(*CHROME_BOX[0::2]):
        for y in range(*CHROME_BOX[1::2]):
            img.putpixel((x, y), chrome)
    for x in range(*ANIMATED_BOX[0::2]):
        for y in range(*ANIMATED_BOX[1::2]):
            img.putpixel((x, y), (animated, animated, animated))
    img.save(path)


def build_fixture(root: Path, *, chrome: tuple[int, int, int]) -> tuple[Path, Path]:
    """Lay out a retail reference set, a capture, and a plan. `chrome` is the
    colour the CAPTURE draws its chrome in; retail always draws CHROME."""
    ref_root = root / "reference"
    (ref_root / "run1").mkdir(parents=True)
    (ref_root / "run2").mkdir(parents=True)
    capture = root / "capture"
    capture.mkdir()

    for offset in OFFSETS:
        # run1 and run2 agree on chrome and disagree on the animated patch.
        write_frame(ref_root / "run1" / f"mm-t{offset:06d}ms.png", CHROME, 10)
        write_frame(ref_root / "run2" / f"mm-t{offset:06d}ms.png", CHROME, 250)
        # The capture matches run1's animated value; the floor still excuses it.
        write_frame(capture / f"mainmenu-t{offset:06d}ms.png", chrome, 10)

    (capture / "capture-manifest.json").write_text(json.dumps({
        "plan": "mainmenu", "capturePurpose": "production", "sourceCommit": "0" * 40,
    }), encoding="utf-8")

    regions = root / "regions.json"
    regions.write_text(json.dumps({"chrome": list(CHROME_BOX)}), encoding="utf-8")

    plan = root / "plan.json"
    plan.write_text(json.dumps({
        "referenceRoot": str(ref_root),
        "_measurementProvenance": {"marginPp": 2.0},
        "pages": [{
            "id": "TEST_PAGE",
            "capturePlan": "mainmenu",
            "shotPrefix": "mainmenu",
            "reference": {"run": "run1", "prefix": "mm"},
            "noiseFloor": {"run": "run2", "prefix": "mm"},
            "regions": str(regions),
            "samples": OFFSETS,
            "measured": {"FULL FRAME": 0.0, "chrome": 0.0},
            "regressionCeiling": {"FULL FRAME": 2.0, "chrome": 2.0},
        }],
        "unscored": [],
    }), encoding="utf-8")
    return plan, capture


def run(plan: Path, capture: Path, out: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--capture-dir", str(capture),
         "--plan", str(plan), "--json-out", str(out)],
        capture_output=True, text=True, check=False)
    report = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
    return proc.returncode, report


def test_clean_capture_passes(root: Path) -> None:
    plan, capture = build_fixture(root, chrome=CHROME)
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "PASS", report["verdict"]
    assert code == 0, code
    # And it passed WHILE the animated patch differed from the noise-floor run,
    # which is the floor doing its job rather than the gate being blind.
    worst = report["pages"][0]["worstGapPct"]
    assert worst["FULL FRAME"] == 0.0, worst


def test_regression_is_caught(root: Path) -> None:
    """THE test. A deliberate one-element regression must FAIL the gate."""
    plan, capture = build_fixture(root, chrome=(90, 200, 180))
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "FAIL", report["verdict"]
    assert code == 1, code
    breaches = {b["region"] for b in report["pages"][0]["breaches"]}
    assert breaches == {"FULL FRAME", "chrome"}, breaches
    assert report["pages"][0]["worstGapPct"]["chrome"] == 100.0


def test_missing_reference_set_is_unscored_not_pass(root: Path) -> None:
    """A fresh clone has no retail material. That must read as UNSCORED - the
    whole defect being fixed here is 'no evidence' rendering as 'no problem'."""
    plan, capture = build_fixture(root, chrome=CHROME)
    body = json.loads(plan.read_text(encoding="utf-8"))
    body["referenceRoot"] = str(root / "does-not-exist")
    plan.write_text(json.dumps(body), encoding="utf-8")
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "UNSCORED", report["verdict"]
    assert code == 0, code
    assert report["pages"] == []


def test_capture_plan_with_no_page_is_unscored(root: Path) -> None:
    plan, capture = build_fixture(root, chrome=CHROME)
    manifest = capture / "capture-manifest.json"
    body = json.loads(manifest.read_text(encoding="utf-8"))
    body["plan"] = "startup"
    manifest.write_text(json.dumps(body), encoding="utf-8")
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "UNSCORED", report["verdict"]
    assert code == 0, code


def test_pairing_outside_tolerance_is_an_error(root: Path) -> None:
    """A frame far from its retail counterpart must be an ERROR, never a
    quietly-used approximation."""
    plan, capture = build_fixture(root, chrome=CHROME)
    for offset in OFFSETS:
        (capture / f"mainmenu-t{offset:06d}ms.png").rename(
            capture / f"mainmenu-t{offset + 900:06d}ms.png")
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "ERROR", report["verdict"]
    assert code == 1, code
    assert any("tolerance" in e for e in report["pages"][0]["errors"]), report


def test_size_mismatch_is_refused(root: Path) -> None:
    plan, capture = build_fixture(root, chrome=CHROME)
    for offset in OFFSETS:
        path = capture / f"mainmenu-t{offset:06d}ms.png"
        Image.open(path).resize((W * 2, H * 2)).save(path)
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "ERROR", report["verdict"]
    assert code == 1, code
    assert any("REFUSED" in e for e in report["pages"][0]["errors"]), report


def test_ceiling_naming_an_unknown_region_is_an_error(root: Path) -> None:
    """A ceiling on a region that does not exist would silently gate nothing."""
    plan, capture = build_fixture(root, chrome=CHROME)
    body = json.loads(plan.read_text(encoding="utf-8"))
    body["pages"][0]["regressionCeiling"]["chrom"] = 2.0
    plan.write_text(json.dumps(body), encoding="utf-8")
    code, report = run(plan, capture, root / "out.json")
    assert report["verdict"] == "ERROR", report["verdict"]
    assert code == 1, code


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for test in tests:
        root = Path(tempfile.mkdtemp(prefix="score-frontend-"))
        try:
            test(root)
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
        finally:
            shutil.rmtree(root, ignore_errors=True)
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
