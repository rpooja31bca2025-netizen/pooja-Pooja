import os
import re
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

PANELS_DIR = (
    BASE_DIR /
    "static" /
    "panels"
)

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

USE_STABLE_DIFFUSION = (
    os.getenv(
        "USE_STABLE_DIFFUSION",
        "false"
    ).lower()
    == "true"
)

HF_MODEL_ID = os.getenv(
    "HF_MODEL_ID",
    "stable-diffusion-v1-5/stable-diffusion-v1-5"
)

_pipeline = None


def _safe_filename(text: str):
    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text
    )

    return text[:80]


def _load_font(size=24):
    """
    Try to load a common Windows font.
    """

    possible_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]

    for font_path in possible_fonts:

        if os.path.exists(font_path):

            try:
                return ImageFont.truetype(
                    font_path,
                    size
                )
            except Exception:
                pass

    return ImageFont.load_default()


def _create_demo_image(
    prompt: str,
    output_path: Path,
    panel_number: int
):
    """
    Creates a clean placeholder image.

    This allows the complete application
    to run even before Stable Diffusion
    is installed.
    """

    width = 1024
    height = 768

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        [15, 15, width - 15, height - 15],
        outline="black",
        width=8
    )

    title_font = _load_font(42)
    text_font = _load_font(24)

    draw.text(
        (50, 50),
        f"COMICCRAFT - PANEL {panel_number}",
        fill="black",
        font=title_font
    )

    draw.text(
        (50, 125),
        "AI Illustration",
        fill="black",
        font=text_font
    )

    # Wrap prompt
    words = prompt.split()
    lines = []
    current = ""

    for word in words:

        test = (
            current + " " + word
        ).strip()

        if len(test) > 55:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 220

    for line in lines[:12]:

        draw.text(
            (50, y),
            line,
            fill="black",
            font=text_font
        )

        y += 38

    draw.text(
        (50, 680),
        "Enable Stable Diffusion in .env "
        "for real AI illustrations.",
        fill="black",
        font=text_font
    )

    image.save(
        output_path,
        format="PNG"
    )


def _get_pipeline():

    global _pipeline

    if _pipeline is not None:
        return _pipeline

    try:

        import torch

        from diffusers import (
            StableDiffusionPipeline
        )

        dtype = (
            torch.float16
            if torch.cuda.is_available()
            else torch.float32
        )

        _pipeline = (
            StableDiffusionPipeline
            .from_pretrained(
                HF_MODEL_ID,
                torch_dtype=dtype
            )
        )

        if torch.cuda.is_available():

            _pipeline = (
                _pipeline.to("cuda")
            )

        else:

            _pipeline = (
                _pipeline.to("cpu")
            )

        return _pipeline

    except Exception as exc:

        raise RuntimeError(
            "Could not load Stable Diffusion. "
            f"Details: {exc}"
        )


def generate_image(
    prompt: str,
    panel_number: int,
    art_style: str = "comic book"
):
    """
    Generate a panel image.

    If USE_STABLE_DIFFUSION=false,
    a placeholder image is created so
    the entire application can be tested.
    """

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt[:30])}.png"
    )

    output_path = (
        PANELS_DIR /
        filename
    )

    final_prompt = f"""
Comic book illustration.

Art style:
{art_style}

Scene:
{prompt}

Requirements:
consistent character design,
clear composition,
expressive characters,
detailed environment,
cinematic lighting,
high quality,
no text,
no watermark.
"""

    if not USE_STABLE_DIFFUSION:

        _create_demo_image(
            final_prompt,
            output_path,
            panel_number
        )

    else:

        pipeline = _get_pipeline()

        result = pipeline(
            final_prompt,
            num_inference_steps=25,
            guidance_scale=7.5
        )

        image = result.images[0]

        image.save(
            output_path
        )

    return (
        f"/static/panels/{filename}"
    )