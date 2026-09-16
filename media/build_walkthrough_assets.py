#!/usr/bin/env python3
"""Build 1920x1080 story frames for the Cowork Adoption Intelligence walkthrough."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SEGMENTS_PATH = Path(__file__).with_name("walkthrough_segments.json")
OUTPUT = Path(__file__).with_name("composed")

WIDTH = 1920
HEIGHT = 1080
INK = "#172033"
MUTED = "#667085"
TEAL = "#00A89D"
TEAL_DARK = "#008272"
LIGHT = "#F4F7F9"
WHITE = "#FFFFFF"
NAVY = "#07111E"
REPOSITORY = "github.com/microsoft/Cowork-Adoption-Intelligence"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (
        ["segoeuib.ttf", "aptos-display-bold.ttf", "arialbd.ttf"]
        if bold
        else ["segoeui.ttf", "aptos.ttf", "arial.ttf"]
    )
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def linear_gradient(
    top: tuple[int, int, int], bottom: tuple[int, int, int]
) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        amount = y / max(HEIGHT - 1, 1)
        color = tuple(
            round(top[index] * (1 - amount) + bottom[index] * amount)
            for index in range(3)
        )
        for x in range(WIDTH):
            pixels[x, y] = color
    return image


def dark_background() -> Image.Image:
    image = linear_gradient((8, 24, 38), (3, 9, 16)).convert("RGBA")
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((1150, -260, 2200, 790), fill=(0, 168, 157, 68))
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    return Image.alpha_composite(image, glow).convert("RGB")


def light_background() -> Image.Image:
    return linear_gradient((250, 252, 253), (235, 241, 245))


def wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: str,
    spacing: int,
) -> int:
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.getbbox("Ag")[3] + spacing
    return y


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius, fill=255
    )
    return mask


def paste_dashboard(image: Image.Image, source: Path) -> None:
    card_x, card_y, card_w, card_h = 240, 174, 1440, 810
    shadow = Image.new("RGBA", (card_w + 100, card_h + 100), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (50, 68, card_w + 50, card_h + 68),
        radius=20,
        fill=(4, 15, 28, 90),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    image.paste(shadow, (card_x - 50, card_y - 50), shadow)

    dashboard = Image.open(source).convert("RGB").resize(
        (card_w, card_h), Image.Resampling.LANCZOS
    )
    mask = rounded_mask((card_w, card_h), 18)
    image.paste(dashboard, (card_x, card_y), mask)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=18,
        outline="#C8D1DC",
        width=2,
    )


def build_dark(segment: dict) -> Image.Image:
    image = dark_background()
    draw = ImageDraw.Draw(image)
    draw.text(
        (92, 58), segment["eyebrow"], font=load_font(22, True), fill="#8393A7"
    )
    draw.rounded_rectangle((92, 184, 190, 190), radius=3, fill=TEAL)
    draw.text((92, 230), segment["kicker"], font=load_font(28, True), fill=TEAL)

    title_font = load_font(78, True)
    title_lines = wrap(draw, segment["title"], title_font, 1500)
    y = draw_lines(draw, title_lines, 92, 310, title_font, WHITE, 18)

    subtitle_font = load_font(31)
    subtitle_lines = wrap(draw, segment["subtitle"], subtitle_font, 1370)
    draw_lines(draw, subtitle_lines, 92, y + 28, subtitle_font, "#CBD5E1", 12)

    draw.text(
        (92, 948),
        "Template in testing | Built for approved Cowork data",
        font=load_font(19),
        fill="#96A3B4",
    )
    draw.text((92, 994), REPOSITORY, font=load_font(22), fill="#7E8B9C")
    return image


def build_dashboard(segment: dict) -> Image.Image:
    image = light_background()
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 5), fill=TEAL)
    draw.text(
        (92, 32), segment["eyebrow"], font=load_font(20, True), fill=TEAL_DARK
    )
    draw.text((92, 68), segment["title"], font=load_font(44, True), fill=INK)
    draw.text((650, 84), segment["subtitle"], font=load_font(25), fill=MUTED)

    source = ROOT / segment["source"].replace("/", "\\")
    if not source.exists():
        raise FileNotFoundError(f"Missing dashboard source: {source}")
    paste_dashboard(image, source)

    caption_x, caption_y, caption_w, caption_h = 305, 882, 1310, 82
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (caption_x, caption_y, caption_x + caption_w, caption_y + caption_h),
        radius=14,
        fill=(4, 15, 28, 235),
        outline=(0, 168, 157, 255),
        width=2,
    )
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(image)
    caption_font = load_font(25, True)
    caption_lines = wrap(draw, segment["caption"], caption_font, caption_w - 72)
    block_height = len(caption_lines) * (caption_font.getbbox("Ag")[3] + 5)
    y = caption_y + max(12, (caption_h - block_height) // 2)
    draw_lines(
        draw, caption_lines, caption_x + 36, y, caption_font, WHITE, 5
    )
    return image


def build_summary(segment: dict) -> Image.Image:
    image = light_background()
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 5), fill=TEAL)
    draw.text(
        (92, 52), segment["eyebrow"], font=load_font(22, True), fill=TEAL_DARK
    )
    draw.text((92, 100), segment["title"], font=load_font(54, True), fill=INK)

    bullet_font = load_font(31)
    y = 238
    for bullet in segment["bullets"]:
        draw.ellipse((104, y + 10, 124, y + 30), fill=TEAL)
        lines = wrap(draw, bullet, bullet_font, 1460)
        y = draw_lines(draw, lines, 154, y, bullet_font, INK, 9) + 30

    draw.text((92, 982), segment["footer"], font=load_font(20), fill=TEAL_DARK)
    draw.text((1390, 52), REPOSITORY, font=load_font(18), fill=MUTED)
    return image


def main() -> None:
    segments = json.loads(SEGMENTS_PATH.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT.glob("*.png"):
        old.unlink()

    for segment in segments:
        if segment["kind"] == "dark":
            image = build_dark(segment)
        elif segment["kind"] == "dashboard":
            image = build_dashboard(segment)
        elif segment["kind"] == "summary":
            image = build_summary(segment)
        else:
            raise ValueError(f"Unknown segment kind: {segment['kind']}")

        destination = ROOT / segment["image"].replace("/", "\\")
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, optimize=True)
        print(destination)


if __name__ == "__main__":
    main()
