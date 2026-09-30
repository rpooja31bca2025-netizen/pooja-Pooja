from datetime import datetime
from pathlib import Path
import os

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORTS_DIR = (
    BASE_DIR /
    "static" /
    "exports"
)

EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


class ComicPDF(FPDF):

    def header(self):

        self.set_font(
            "Arial",
            "B",
            18
        )

        self.cell(
            0,
            10,
            "ComicCraft",
            align="C"
        )

        self.ln(12)


def _clean_text(text):

    if text is None:
        return ""

    text = str(text)

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text


def save_pdf(layout):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"comic_{timestamp}.pdf"
    )

    output_path = (
        EXPORTS_DIR /
        filename
    )

    pdf = ComicPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Arial",
            "B",
            20
        )

        title = (
            f"Panel {panel['panel_number']}: "
            f"{_clean_text(panel['title'])}"
        )

        pdf.multi_cell(
            0,
            10,
            title
        )

        pdf.ln(5)

        image_url = panel.get(
            "image",
            ""
        )

        if image_url.startswith(
            "/static/"
        ):

            relative = image_url[
                len("/static/"):
            ]

            image_path = (
                BASE_DIR /
                "static" /
                relative
            )

            if image_path.exists():

                pdf.image(
                    str(image_path),
                    x=15,
                    y=45,
                    w=180
                )

                pdf.ln(115)

        pdf.set_font(
            "Arial",
            "",
            11
        )

        description = _clean_text(
            panel.get(
                "scene_description",
                ""
            )
        )

        if description:

            pdf.multi_cell(
                0,
                7,
                f"Scene: {description}"
            )

            pdf.ln(3)

        caption = _clean_text(
            panel.get(
                "caption",
                ""
            )
        )

        if caption:

            pdf.multi_cell(
                0,
                7,
                f"Caption: {caption}"
            )

            pdf.ln(3)

        narration = _clean_text(
            panel.get(
                "narration",
                ""
            )
        )

        if narration:

            pdf.multi_cell(
                0,
                7,
                f"Narration: {narration}"
            )

            pdf.ln(3)

        dialogue = _clean_text(
            panel.get(
                "dialogue",
                ""
            )
        )

        if dialogue:

            pdf.multi_cell(
                0,
                7,
                f"Dialogue: {dialogue}"
            )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )