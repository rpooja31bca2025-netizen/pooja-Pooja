# Project Design Phase

## System Architecture

ComicCraft consists of three main components.

1. Frontend – HTML, CSS, and Jinja2 are used to collect user input and display comics.
2. Backend – FastAPI handles user requests and comic generation.
3. AI Integration – Gemini generates stories, while Stable Diffusion generates images.

## Main Modules

* gemini_flash.py – Generates comic outlines.
* gemini_pro.py – Generates stories and dialogues.
* image_generator.py – Generates comic images.
* layout_builder.py – Organizes comic panels.
* exporters.py – Creates PDF files.
* routes.py – Handles application routes.

## Workflow

User Input → Story Generation → Image Generation → Comic Layout → Preview → PDF Download
