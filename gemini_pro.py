import os
import json
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-3.8-flash"
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing."
    )

client = genai.Client(api_key=API_KEY)


def _extract_json(text: str):
    """
    Extract JSON object/array from Gemini response.
    """

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    start = text.find("[")

    if start == -1:
        raise ValueError(
            "Could not find JSON array."
        )

    end = text.rfind("]")

    if end == -1:
        raise ValueError(
            "Could not find JSON ending."
        )

    return json.loads(
        text[start:end + 1]
    )


def generate_story(
    outline,
    character_name,
    setting,
    tone
):
    """
    Expand the 5-panel outline into
    narration, captions and dialogue.
    """

    outline_json = json.dumps(
        outline,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are the comic-story writer for ComicCraft.

Create detailed narration and dialogue
for the following 5-panel comic.

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

OUTLINE:

{outline_json}

Return ONLY valid JSON.

Return exactly 5 objects.

Each object must contain:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue

Example:

[
  {{
    "panel_number": 1,
    "title": "The Beginning",
    "scene_description": "A peaceful forest.",
    "caption": "Morning in the forest.",
    "narration": "The hero begins a new adventure.",
    "dialogue": "{character_name}: What could be waiting ahead?"
  }}
]

Rules:

1. Maintain continuity between panels.
2. Use the same character.
3. Match the requested tone.
4. Keep dialogue natural.
5. Keep each panel readable.
6. Do not use markdown.
7. Return only JSON.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    story = _extract_json(
        response.text
    )

    if not isinstance(story, list):
        raise ValueError(
            "Invalid story format."
        )

    result = []

    for index in range(5):

        source = (
            story[index]
            if index < len(story)
            else {}
        )

        result.append(
            {
                "panel_number": index + 1,
                "title": source.get(
                    "title",
                    f"Panel {index + 1}"
                ),
                "scene_description": source.get(
                    "scene_description",
                    ""
                ),
                "caption": source.get(
                    "caption",
                    ""
                ),
                "narration": source.get(
                    "narration",
                    ""
                ),
                "dialogue": source.get(
                    "dialogue",
                    ""
                ),
            }
        )

    return result