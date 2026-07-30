"""Build jitter-free blink frames by compositing only aligned eye regions."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


EYE_REGIONS = (
    (90, 78, 128, 115),
    (134, 78, 166, 114),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("idle", type=Path)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("output_dir", type=Path)
    return parser.parse_args()


def align_subject(cell: Image.Image, target: Image.Image) -> Image.Image:
    source_box = cell.getchannel("A").getbbox()
    target_box = target.getchannel("A").getbbox()
    if source_box is None or target_box is None:
        raise ValueError("Blink source and idle target must contain opaque pixels.")

    target_width = target_box[2] - target_box[0]
    target_height = target_box[3] - target_box[1]
    subject = cell.crop(source_box).resize(
        (target_width, target_height),
        Image.Resampling.LANCZOS,
    )
    aligned = Image.new("RGBA", target.size)
    aligned.alpha_composite(subject, target_box[:2])
    return aligned


def eye_mask(size: tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size)
    draw = ImageDraw.Draw(mask)
    for region in EYE_REGIONS:
        draw.rounded_rectangle(region, radius=8, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(0.8))


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(args.idle).convert("RGBA") as idle:
        with Image.open(args.sheet).convert("RGBA") as sheet:
            cell_width = sheet.width // 2
            cells = (
                sheet.crop((0, 0, cell_width, sheet.height)),
                sheet.crop((cell_width, 0, sheet.width, sheet.height)),
            )

            mask = eye_mask(idle.size)
            names = ("half", "closed")
            for name, cell in zip(names, cells, strict=True):
                aligned = align_subject(cell, idle)
                frame = Image.composite(aligned, idle, mask)
                frame.save(
                    args.output_dir / f"haqi_cat_idle_blink_{name}.png",
                    optimize=True,
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
