"""Pair Level 100 retail reference frames with reconstruction capture frames by
level offset, and report the per-region pixel deltas at each matched offset.

Why this exists
---------------
`compare_capture.py` compares exactly one pair of images. The Level 100
reference set is 183 frames keyed by *level offset in milliseconds from t0*, and
the reconstruction's `gameplay` capture plan emits frames at the same nominal
offsets. Deciding which retail frame a reconstruction frame should be compared
against is therefore arithmetic, not judgement - and it should be done by a tool
so that a bad number cannot be quietly improved by picking a friendlier frame.

Pairing rule
------------
Retail's realised offsets jitter around their nominals by up to ~13 ms (burst
scheduler drift, documented in RETAIL-LEVEL100-GAMEPLAY-CAPTURE-2026-07-25.md).
The reconstruction's offsets do not jitter at all - they are exact engine frame
ordinals. So pairing is nearest-offset within a tolerance, and the realised
pairing error is REPORTED for every pair rather than assumed to be zero.

Retail's own cross-run pairing error over this set was -22..+20 ms, median 0, and
matched-offset comparison is stated to be valid to +-25 ms. A pair whose offset
error exceeds that is flagged, not silently used.

Honesty rules baked in
----------------------
* Frames of different sizes are refused, exactly as `compare_capture.py` refuses
  them. No resampling.
* Every retail frame carries a `stability` class. Pan frames have a cross-run
  floor of mad ~5-10 and are reference-only; the tool prints the class beside
  every result so a number can never be read as a tolerance it is not.
* Missing reconstruction offsets are reported as missing. Nothing is
  interpolated or substituted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_capture import load_rgb, region_stats  # noqa: E402

DEFAULT_RETAIL_ROOT = Path("local-lab/retail-reference-pristine/level100-gameplay")
DEFAULT_RUNS = ("opening-pan-run1", "hud-timeline-run1")


def load_retail(root: Path, runs: tuple[str, ...]) -> list[dict]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    frames = [f for f in manifest["frames"] if f["path"].split("/")[0] in runs]
    if not frames:
        raise SystemExit(f"no retail frames from runs {runs} in {root / 'manifest.json'}")
    return sorted(frames, key=lambda f: f["levelOffsetMs"])


def load_rebuild(manifest_path: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("plan") != "gameplay":
        raise SystemExit(
            f"{manifest_path} is a '{manifest.get('plan')}' capture, not 'gameplay'."
        )
    shots = [s for s in manifest["shots"] if s.get("levelOffsetMs") is not None]
    return manifest, sorted(shots, key=lambda s: s["levelOffsetMs"])


def nearest(frames: list[dict], offset_ms: int) -> dict:
    return min(frames, key=lambda f: abs(f["levelOffsetMs"] - offset_ms))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rebuild-manifest", required=True, type=Path,
                    help="capture-manifest.json from Capture-Frontend.ps1 -Plan gameplay")
    ap.add_argument("--retail-root", type=Path, default=DEFAULT_RETAIL_ROOT)
    ap.add_argument("--runs", default=",".join(DEFAULT_RUNS))
    ap.add_argument("--regions", type=Path,
                    help="JSON: {name: [x0,y0,x1,y1], ...}")
    ap.add_argument("--offsets", default="",
                    help="comma-separated level offsets in ms to compare in "
                         "detail. Default: every paired offset, summary only.")
    ap.add_argument("--tolerance-ms", type=int, default=25,
                    help="retail's stated matched-offset validity (default 25)")
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--pairs-out", type=Path,
                    help="write the reference/candidate path pairs so "
                         "compare_capture.py can be re-run on any of them by hand")
    args = ap.parse_args(argv)

    runs = tuple(r.strip() for r in args.runs.split(",") if r.strip())
    retail = load_retail(args.retail_root, runs)
    manifest, rebuild = load_rebuild(args.rebuild_manifest)
    rebuild_dir = args.rebuild_manifest.parent

    regions: dict[str, list[int]] = {"FULL FRAME": [0, 0, 640, 480]}
    if args.regions:
        regions.update(json.loads(args.regions.read_text(encoding="utf-8")))

    detail = {int(o) for o in args.offsets.split(",") if o.strip()} if args.offsets else None

    print(f"rebuild capture : {args.rebuild_manifest}")
    print(f"  plan={manifest.get('plan')} planned={manifest.get('plannedShots')} "
          f"captured={manifest.get('capturedShots')} zeroFrame={manifest.get('gameplayZeroFrame')}")
    if manifest.get("boundary"):
        print(f"  BOUNDARY: {manifest['boundary']}")
    print(f"retail reference: {args.retail_root} runs={runs} frames={len(retail)}")
    print()

    pairs = []
    for shot in rebuild:
        offset = shot["levelOffsetMs"]
        ref = nearest(retail, offset)
        error = ref["levelOffsetMs"] - offset
        cand_path = rebuild_dir / shot.get("file", Path(shot["path"]).name)
        pairs.append({
            "levelOffsetMs": offset,
            "retailOffsetMs": ref["levelOffsetMs"],
            "pairingErrorMs": error,
            "withinToleranceMs": abs(error) <= args.tolerance_ms,
            "phase": ref["phase"],
            "stability": ref["stability"],
            "reference": str(args.retail_root / ref["path"]),
            "candidate": str(cand_path),
            "retailMeanRGB": ref["meanRGB"],
            "rebuildMeanRGB": shot.get("meanRGB"),
        })

    out_of_tolerance = [p for p in pairs if not p["withinToleranceMs"]]
    print(f"paired {len(pairs)} offsets; "
          f"{len(out_of_tolerance)} outside +-{args.tolerance_ms} ms")
    if pairs:
        errs = sorted(p["pairingErrorMs"] for p in pairs)
        print(f"pairing error ms: min={errs[0]} median={errs[len(errs)//2]} max={errs[-1]}")
    print()

    header = ("offset   retailOff   errMs  full changed%  full material%  full meanD   "
              "retail meanRGB          rebuild meanRGB")
    print(header)
    print("-" * len(header))

    report = {
        "rebuildManifest": str(args.rebuild_manifest),
        "retailRoot": str(args.retail_root),
        "runs": list(runs),
        "toleranceMs": args.tolerance_ms,
        "boundary": manifest.get("boundary"),
        "plannedShots": manifest.get("plannedShots"),
        "capturedShots": manifest.get("capturedShots"),
        "pairs": [],
    }

    for pair in pairs:
        ref_img = load_rgb(Path(pair["reference"]))
        cand_path = Path(pair["candidate"])
        if not cand_path.is_file():
            print(f"{pair['levelOffsetMs']:>6}   MISSING reconstruction frame {cand_path.name}")
            pair["missing"] = True
            report["pairs"].append(pair)
            continue
        cand_img = load_rgb(cand_path)
        if ref_img.size != cand_img.size:
            print(f"{pair['levelOffsetMs']:>6}   REFUSED size {ref_img.size} vs {cand_img.size}")
            pair["refused"] = f"{ref_img.size} vs {cand_img.size}"
            report["pairs"].append(pair)
            continue

        wanted = regions if (detail is None or pair["levelOffsetMs"] in detail) else {
            "FULL FRAME": regions["FULL FRAME"]}
        stats = {name: region_stats(ref_img, cand_img, tuple(box))
                 for name, box in wanted.items()}
        pair["regions"] = stats
        report["pairs"].append(pair)

        full = stats["FULL FRAME"]
        print(f"{pair['levelOffsetMs']:>6}   {pair['retailOffsetMs']:>9}  {pair['pairingErrorMs']:>6}"
              f"  {full['changedPct']:12.2f}  {full['materialPct']:14.2f}  {full['meanAbsDelta']:10.2f}"
              f"   {str(full['refMeanRGB']):<22} {full['cmpMeanRGB']}")

        if detail is not None and pair["levelOffsetMs"] in detail:
            print(f"         phase={pair['phase']}  stability={pair['stability']}")
            width = max(len(k) for k in regions)
            for name in regions:
                s = stats[name]
                print(f"           {name.ljust(width)}  changed {s['changedPct']:7.2f}%"
                      f"  material {s['materialPct']:7.2f}%  meanD {s['meanAbsDelta']:7.2f}"
                      f"  maxD {s['maxAbsDelta']:4d}"
                      f"  {s['refMeanRGB']} -> {s['cmpMeanRGB']}")
            print()

    if args.pairs_out:
        args.pairs_out.parent.mkdir(parents=True, exist_ok=True)
        args.pairs_out.write_text(
            json.dumps([{k: p[k] for k in ("levelOffsetMs", "reference", "candidate")}
                        for p in pairs], indent=2), encoding="utf-8")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
