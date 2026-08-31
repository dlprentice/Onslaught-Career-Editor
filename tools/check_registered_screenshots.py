#!/usr/bin/env python3
"""Fail if a tracked picture of the game is not registered, or if there are too many.

On 2026-08-01 the project relaxed a rule. It used to say plainly "do not track retail
game assets", and that was easy to hold because it admitted no exceptions. It now says
the game's own shipped files stay out but a few screenshots may come in - and a rule with
an exception is a rule that drifts, one reasonable-looking addition at a time, until the
repository is a screenshot gallery and nobody decided that.

So the exception is bounded here rather than only in prose:

  * every tracked image outside the app's own icon must appear in the register in
    reverse-engineering/project-meta/attribution.md, and
  * the count must stay under MAX_REGISTERED.

Neither check can tell a screenshot from an extracted texture - that judgement is human
and it is written down in AGENTS.md. What this can do is make sure the judgement was
made deliberately, by somebody who had to write a row explaining why, rather than by a
file appearing in a commit nobody read closely.

Run:  python ./tools/check_registered_screenshots.py            list what is tracked
      python ./tools/check_registered_screenshots.py --check    non-zero if unregistered
      python ./tools/check_registered_screenshots.py --self-test
"""

from __future__ import annotations

import argparse
import io
import pathlib
import subprocess
import sys


REGISTER = "reverse-engineering/project-meta/attribution.md"

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tga", ".dds")

# The app's own chrome, authored by this project. Not pictures of the game.
EXEMPT = {
    "OnslaughtCareerEditor.WinUI/Assets/AppIcon-256.png",
    "OnslaughtCareerEditor.WinUI/Assets/AppIcon.ico",
}

# The bound that matters. Enough stills become the asset: a cutscene dumped frame by
# frame is the cutscene. This number is small on purpose - raising it should feel like a
# decision, which means editing this line and saying why in the commit.
MAX_REGISTERED = 6


def repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for candidate in [here.parent.parent, *here.parents]:
        if (candidate / "package.json").is_file():
            return candidate
    raise SystemExit("Could not find the repository root.")


def tracked_images(root: pathlib.Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=False
    ).stdout.split()
    return sorted(
        name
        for name in out
        if name.lower().endswith(IMAGE_SUFFIXES) and name not in EXEMPT
    )


def register_text(root: pathlib.Path) -> str:
    path = root / REGISTER
    if not path.is_file():
        return ""
    return io.open(path, encoding="utf-8", errors="replace").read()


def unregistered(images: list[str], register: str) -> list[str]:
    return [name for name in images if name not in register]


def self_test() -> int:
    """The rule, on synthetic input. No repository state involved."""
    register = (
        "| `OnslaughtCareerEditor.WinUI/Assets/Screenshots/title-screen.jpg` | ... |\n"
    )

    cases: list[tuple[str, list[str], list[str]]] = [
        (
            "a registered screenshot passes",
            ["OnslaughtCareerEditor.WinUI/Assets/Screenshots/title-screen.jpg"],
            [],
        ),
        (
            "an unregistered one is caught",
            ["OnslaughtCareerEditor.WinUI/Assets/Screenshots/sneaky.jpg"],
            ["OnslaughtCareerEditor.WinUI/Assets/Screenshots/sneaky.jpg"],
        ),
        (
            "an extracted texture elsewhere in the tree is caught too",
            ["reverse-engineering/game-assets/hull.dds"],
            ["reverse-engineering/game-assets/hull.dds"],
        ),
    ]

    failures = 0
    for label, images, expected in cases:
        actual = unregistered(images, register)
        ok = actual == expected
        failures += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")

    # The count bound has to bite, or it is decoration.
    too_many = [f"img-{n}.jpg" for n in range(MAX_REGISTERED + 1)]
    ok = len(too_many) > MAX_REGISTERED
    failures += 0 if ok else 1
    print(f"  {'PASS' if ok else 'FAIL'}  the count bound rejects {len(too_many)} images")

    print("SELF-TEST PASS" if failures == 0 else f"SELF-TEST FAIL ({failures})")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on anything unregistered.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = repo_root()
    images = tracked_images(root)
    register = register_text(root)
    missing = unregistered(images, register)

    print(f"Tracked images (excluding the app's own icon): {len(images)}")
    for name in images:
        mark = "registered" if name not in missing else "NOT REGISTERED"
        print(f"  [{mark}] {name}")
    print(f"\nBound: {len(images)}/{MAX_REGISTERED}")

    if not args.check:
        return 0

    failed = False
    if missing:
        failed = True
        print(f"\nFAIL: {len(missing)} tracked image(s) are not in {REGISTER}.")
        print("Add a row saying what each one is and why it is tracked, or remove it.")
        print("The allowance and its conditions are in AGENTS.md.")

    if len(images) > MAX_REGISTERED:
        failed = True
        print(f"\nFAIL: {len(images)} tracked images exceeds the bound of {MAX_REGISTERED}.")
        print("Enough stills become the asset. Raise the bound deliberately or drop some.")

    if failed:
        return 1

    print("\nPASS: every tracked image is registered and the count is within bounds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
