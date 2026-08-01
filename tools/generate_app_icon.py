#!/usr/bin/env python3
"""Generate the Onslaught Toolkit application icon.

The artwork is ORIGINAL to this project. It deliberately borrows nothing from
Battle Engine Aquila's own logo, box art, or in-game assets, which are the
rights holders' and are never tracked in this repository. The mark is a pair of
abstract angular wings over a level horizon: the game's signature move is the
walker/jet transformation, so the wing reads as "flight mode" while the bar
beneath it reads as ground. Both are plain geometry drawn from the app's own
accent palette.

Run:  py -3 tools/generate_app_icon.py
Writes: OnslaughtCareerEditor.WinUI/Assets/AppIcon.ico (+ a PNG preview)

Deterministic: the same source produces byte-identical output, so regenerating
never churns the tracked icon.
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw

# Palette taken from App.xaml's own shell brushes so the icon matches the app.
BACKGROUND_TOP = (23, 60, 146)      # ShellHeroBrush  #173C92
BACKGROUND_BOTTOM = (16, 20, 28)    # ShellPageBrush  #10141C
ACCENT = (86, 140, 255)             # brightened ShellAccentBrush for small sizes
ACCENT_SOFT = (150, 186, 255)
HORIZON = (244, 247, 251)           # ShellTextBrush  #F4F7FB

# Rendered large, then downsampled: that is what keeps 16px legible.
CANVAS = 1024
ICON_SIZES = [256, 128, 64, 48, 32, 24, 16]


def _rounded_mask(size: int, radius_ratio: float = 0.22) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (size - 1, size - 1)],
        radius=int(size * radius_ratio),
        fill=255,
    )
    return mask


def _vertical_gradient(size: int, top: tuple, bottom: tuple) -> Image.Image:
    gradient = Image.new("RGB", (1, size))
    for y in range(size):
        t = y / max(size - 1, 1)
        gradient.putpixel(
            (0, y),
            (
                round(top[0] + (bottom[0] - top[0]) * t),
                round(top[1] + (bottom[1] - top[1]) * t),
                round(top[2] + (bottom[2] - top[2]) * t),
            ),
        )
    return gradient.resize((size, size), Image.NEAREST)


def render(size: int) -> Image.Image:
    base = _vertical_gradient(size, BACKGROUND_TOP, BACKGROUND_BOTTOM).convert("RGBA")
    draw = ImageDraw.Draw(base)

    u = size / 1024.0  # one design unit

    # The wing: a swept chevron, heavier on the leading edge. Drawn as two
    # stacked shapes so it still reads as a wing when it is 16 pixels wide.
    upper = [
        (512 * u, 214 * u),
        (838 * u, 566 * u),
        (688 * u, 566 * u),
        (512 * u, 376 * u),
        (336 * u, 566 * u),
        (186 * u, 566 * u),
    ]
    draw.polygon(upper, fill=ACCENT)

    lower = [
        (512 * u, 436 * u),
        (700 * u, 640 * u),
        (324 * u, 640 * u),
    ]
    draw.polygon(lower, fill=ACCENT_SOFT)

    # The horizon: ground the mark, and give the silhouette a stable base edge.
    bar_top = 726 * u
    bar_height = 62 * u
    draw.rounded_rectangle(
        [(228 * u, bar_top), (796 * u, bar_top + bar_height)],
        radius=bar_height / 2,
        fill=HORIZON,
    )

    base.putalpha(_rounded_mask(size))
    return base


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    assets = repo_root / "OnslaughtCareerEditor.WinUI" / "Assets"
    assets.mkdir(parents=True, exist_ok=True)

    master = render(CANVAS)
    frames = [master.resize((s, s), Image.LANCZOS) for s in ICON_SIZES]

    ico_path = assets / "AppIcon.ico"
    frames[0].save(ico_path, format="ICO", sizes=[(s, s) for s in ICON_SIZES])

    preview_path = assets / "AppIcon-256.png"
    frames[0].save(preview_path, format="PNG")

    print(f"wrote {ico_path} ({ico_path.stat().st_size} bytes)")
    print(f"wrote {preview_path} ({preview_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
