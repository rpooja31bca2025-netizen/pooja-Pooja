import traceback

from fastapi import (
    APIRouter,
    Form,
    Request,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from pydantic import BaseModel, Field

from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.ai.image_generator import generate_image

from app.layout_builder import build_comic_layout
from app.exporters import save_pdf


router = APIRouter()


class PromptRequest(BaseModel):

    story_prompt: str = Field(
        ...,
        min_length=3
    )

    character_name: str = Field(
        ...,
        min_length=1
    )

    setting: str = Field(
        ...,
        min_length=1
    )

    tone: str = Field(
        ...,
        min_length=1
    )

    art_style: str = Field(
        ...,
        min_length=1
    )


def create_comic(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    # Step 1:
    # Generate the 5-panel outline
    outline = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style
    )

    # Step 2:
    # Generate narration and dialogue
    story = generate_story(
        outline=outline,
        character_name=character_name,
        setting=setting,
        tone=tone
    )

    # Step 3:
    # Generate one image for every panel
    image_paths = []

    for panel in outline:

        image_path = generate_image(
            prompt=panel["image_prompt"],
            panel_number=panel["panel_number"],
            art_style=art_style
        )

        image_paths.append(image_path)

    # Step 4:
    # Combine everything
    layout = build_comic_layout(
        outline=outline,
        story=story,
        image_paths=image_paths
    )

    # Step 5:
    # Create PDF
    pdf_path = save_pdf(
        layout
    )

    return {
        "outline": outline,
        "story": story,
        "layout": layout,
        "pdf_path": pdf_path
    }


# =========================================================
# HOME PAGE
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# GENERATE COMIC
# =========================================================

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate_comic(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    try:

        result = create_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": result["layout"],
                "pdf_path": result["pdf_path"]
            }
        )

    except Exception as exc:

        traceback.print_exc()

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=500
        )


# =========================================================
# JSON API
# =========================================================

@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    data: PromptRequest
):

    try:

        result = create_comic(
            story_prompt=data.story_prompt,
            character_name=data.character_name,
            setting=data.setting,
            tone=data.tone,
            art_style=data.art_style
        )

        return {
            "success": True,
            "layout": result["layout"],
            "pdf_path": result["pdf_path"]
        }

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# TEST IMAGE
# =========================================================

@router.get(
    "/test-image",
    response_class=HTMLResponse
)
async def test_image(
    request: Request,

    prompt: str = (
        "A brave fox exploring "
        "an enchanted forest"
    )
):

    try:

        image_path = generate_image(
            prompt=prompt,
            panel_number=999,
            art_style="comic book"
        )

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": [
                    {
                        "panel_number": 1,

                        "title": "Image Test",

                        "scene_description": prompt,

                        "image_prompt": prompt,

                        "image": image_path,

                        "caption": "",

                        "narration": "",

                        "dialogue": ""
                    }
                ],

                "pdf_path": None
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# EXPORT SUCCESS
# =========================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request
):

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={}
    )


# =========================================================
# DOWNLOAD
# =========================================================

@router.get(
    "/download"
)
async def download_comic(
    pdf: str
):

    return RedirectResponse(
        url=pdf
    )