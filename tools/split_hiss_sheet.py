"""Split a transparent three-frame hiss sheet into normalized pet sprites."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--character-height", type=int, default=218)
    parser.add_argument("--bottom-padding", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(args.sheet).convert("RGBA") as sheet:
        cell_width = sheet.width // 3
        boxes = (
            (0, 0, cell_width, sheet.height),
            (cell_width, 0, cell_width * 2, sheet.height),
            (cell_width * 2, 0, sheet.width, sheet.height),
        )

        for index, box in enumerate(boxes, start=1):
            frame = sheet.crop(box)
            content_box = frame.getbbox()
            if content_box is None:
                raise ValueError(f"hiss frame {index} contains no visible pixels")

            character = frame.crop(content_box)
            scale = min(
                (args.size - 16) / character.width,
                args.character_height / character.height,
            )
            resized = character.resize(
                (
                    max(1, round(character.width * scale)),
                    max(1, round(character.height * scale)),
                ),
                Image.Resampling.LANCZOS,
            )

            canvas = Image.new("RGBA", (args.size, args.size))
            offset = (
                (args.size - resized.width) // 2,
                args.size - args.bottom_padding - resized.height,
            )
            canvas.alpha_composite(resized, offset)
            canvas.save(
                args.output_dir / f"haqi_cat_hiss_{index:02d}.png",
                optimize=True,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
