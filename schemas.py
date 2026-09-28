"""Pydantic schemas for ComicCraft requests and comic data."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ComicRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Story idea from the user")
    character: str = Field(default="a curious hero")
    setting: str = Field(default="a bustling city")
    tone: str = Field(default="whimsical")
    art_style: str = Field(default="pop art")
    num_panels: int = Field(default=4, ge=2, le=8)


class Panel(BaseModel):
    index: int
    title: str
    caption: str
    image_prompt: str
    image_path: Optional[str] = None  # filled in after image generation


class Comic(BaseModel):
    title: str
    panels: List[Panel]
    tone: str
    art_style: str
