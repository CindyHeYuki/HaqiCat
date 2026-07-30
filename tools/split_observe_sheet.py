"""Split a transparent two-frame observation sheet and mirror both poses."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--size", type=int, default=256)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(args.sheet).convert("RGBA") as sheet:
        cell_width = sheet.width // 2
        boxes = (
            (0, 0, cell_width, sheet.height),
            (cell_width, 0, sheet.width, sheet.height),
        )

        for index, box in enumerate(boxes, start=1):
            frame = sheet.crop(box)
            frame.thumbnail((args.size, args.size), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (args.size, args.size))
            offset = ((args.size - frame.width) // 2, (args.size - frame.height) // 2)
            canvas.alpha_composite(frame, offset)

            left_path = args.output_dir / f"haqi_cat_observe_left_{index:02d}.png"
            right_path = args.output_dir / f"haqi_cat_observe_right_{index:02d}.png"
            canvas.save(left_path, optimize=True)
            canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(
                right_path,
                optimize=True,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
