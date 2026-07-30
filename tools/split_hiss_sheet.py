"""Split a transparent hiss sheet with one shared crop and scale."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--frame-count", type=int, default=5)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--character-height", type=int, default=218)
    parser.add_argument("--bottom-padding", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(args.sheet).convert("RGBA") as sheet:
        boundaries = [
            index * sheet.width // args.frame_count
            for index in range(args.frame_count + 1)
        ]
        frames = [
            sheet.crop(
                (
                    boundaries[index],
                    0,
                    boundaries[index + 1],
                    sheet.height,
                )
            )
            for index in range(args.frame_count)
        ]
        content_boxes = [frame.getbbox() for frame in frames]
        if any(box is None for box in content_boxes):
            raise ValueError("hiss sheet contains an empty frame")

        visible_boxes = [box for box in content_boxes if box is not None]
        common_box = (
            min(box[0] for box in visible_boxes),
            min(box[1] for box in visible_boxes),
            max(box[2] for box in visible_boxes),
            max(box[3] for box in visible_boxes),
        )
        common_width = common_box[2] - common_box[0]
        common_height = common_box[3] - common_box[1]
        scale = min(
            (args.size - 16) / common_width,
            args.character_height / common_height,
        )
        resized_size = (
            max(1, round(common_width * scale)),
            max(1, round(common_height * scale)),
        )
        offset = (
            (args.size - resized_size[0]) // 2,
            args.size - args.bottom_padding - resized_size[1],
        )

        for index, frame in enumerate(frames, start=1):
            character = frame.crop(common_box).resize(
                resized_size,
                Image.Resampling.LANCZOS,
            )
            canvas = Image.new("RGBA", (args.size, args.size))
            canvas.alpha_composite(character, offset)
            canvas.save(
                args.output_dir / f"haqi_cat_hiss_{index:02d}.png",
                optimize=True,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
