import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# IMPORTANT:
# This is the model that we already tested successfully.
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# BASIC GEMINI REQUEST
# =========================================================

def call_gemini(prompt, max_retries=3):

    last_error = None

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=6000,
                )
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text

        except Exception as error:

            last_error = error

            error_text = str(error)

            print(
                f"Gemini request failed "
                f"(attempt {attempt + 1}/{max_retries}):"
            )

            print(error_text)

            # Retry temporary API errors
            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

            raise

    raise last_error


# =========================================================
# JSON EXTRACTION
# =========================================================

def extract_json(text):

    text = text.strip()

    # Remove markdown fences
    if text.startswith("```json"):

        text = text[7:]

    elif text.startswith("```"):

        text = text[3:]

    if text.endswith("```"):

        text = text[:-3]

    text = text.strip()

    # Find the beginning of the JSON array
    start = text.find("[")

    if start == -1:

        raise ValueError(
            "No JSON array found in Gemini response."
        )

    text = text[start:]

    # Find the last complete closing bracket.
    end = text.rfind("]")

    if end != -1:

        text = text[:end + 1]

    return json.loads(text)


# =========================================================
# GENERATE COMIC OUTLINE
# =========================================================

def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    prompt = f"""
You are ComicCraft, an AI comic story generator.

Create a comic story containing exactly 5 panels.

STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

For every panel provide:

1. panel_number
2. title
3. scene_description
4. character_action
5. dialogue
6. narration
7. image_prompt

IMPORTANT RULES:

- Create exactly 5 panels.
- Keep each field SHORT.
- Each scene_description must be less than 40 words.
- Each character_action must be less than 30 words.
- Each dialogue must be one short sentence.
- Each narration must be less than 30 words.
- Each image_prompt must be less than 70 words.
- Do not use newline characters inside JSON strings.
- Do not use quotation marks inside string values.
- Return ONLY valid JSON.
- Do NOT use markdown.
- Do NOT use ```json.
- Make sure the JSON is completely closed before ending the response.

Return exactly this structure:

[
  {{
    "panel_number": 1,
    "title": "Short title",
    "scene_description": "Short scene",
    "character_action": "Short action",
    "dialogue": "Short dialogue",
    "narration": "Short narration",
    "image_prompt": "Short detailed visual prompt"
  }},
  {{
    "panel_number": 2,
    "title": "Short title",
    "scene_description": "Short scene",
    "character_action": "Short action",
    "dialogue": "Short dialogue",
    "narration": "Short narration",
    "image_prompt": "Short detailed visual prompt"
  }},
  {{
    "panel_number": 3,
    "title": "Short title",
    "scene_description": "Short scene",
    "character_action": "Short action",
    "dialogue": "Short dialogue",
    "narration": "Short narration",
    "image_prompt": "Short detailed visual prompt"
  }},
  {{
    "panel_number": 4,
    "title": "Short title",
    "scene_description": "Short scene",
    "character_action": "Short action",
    "dialogue": "Short dialogue",
    "narration": "Short narration",
    "image_prompt": "Short detailed visual prompt"
  }},
  {{
    "panel_number": 5,
    "title": "Short title",
    "scene_description": "Short scene",
    "character_action": "Short action",
    "dialogue": "Short dialogue",
    "narration": "Short narration",
    "image_prompt": "Short detailed visual prompt"
  }}
]
"""

    response_text = call_gemini(prompt)

    print("\n========== GEMINI COMIC RESPONSE ==========\n")
    print(response_text)
    print("\n============================================\n")

    try:

        result = extract_json(response_text)

        if not isinstance(result, list):

            raise ValueError(
                "Gemini did not return a JSON list."
            )

        if len(result) != 5:

            raise ValueError(
                f"Expected 5 panels but received {len(result)}."
            )

        # Make sure every panel has the required fields.
        required_fields = [
            "panel_number",
            "title",
            "scene_description",
            "character_action",
            "dialogue",
            "narration",
            "image_prompt",
        ]

        for index, panel in enumerate(result):

            for field in required_fields:

                if field not in panel:

                    raise ValueError(
                        f"Panel {index + 1} is missing "
                        f"field: {field}"
                    )

        return result

    except json.JSONDecodeError as error:

        print("\nJSON ERROR:")
        print(error)

        print("\nRAW GEMINI RESPONSE:")
        print(response_text)

        raise RuntimeError(
            "Gemini returned incomplete or invalid JSON. "
            "Please try generating the comic again."
        )

    except Exception as error:

        print("\nOUTLINE ERROR:")
        print(error)

        raise RuntimeError(
            f"Could not create comic outline: {error}"
        )