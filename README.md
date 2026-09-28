# ComicCraft — AI Comic Story Creator

Turn a story idea into an illustrated, panel-by-panel comic using Google's Gemini models, then export it as a PDF.

## Features

- Story prompt + character, setting, tone, and art style controls
- Gemini Flash writes the story as structured panels (title, caption, image prompt)
- Gemini image model draws each panel
- Comic-book grid preview page
- One-click PDF export

## Setup

```bash
cd ComicCraft
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Add your Gemini API key to `.env` (get one at https://aistudio.google.com/apikey):

```
GEMINI_API_KEY=your-key-here
```

## Run

```bash
python run.py
```

Open http://localhost:5000, describe your story, and hit **Generate comic**.

## Project structure

```
ComicCraft/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── main.py              # (alternative entry point)
│   ├── routes.py            # HTTP routes
│   ├── ai/
│   │   ├── gemini_story.py      # story → structured panels
│   │   ├── gemini_flash.py      # quick one-shot text helper
│   │   └── image_generator.py   # panel image generation
│   ├── services/
│   │   ├── layout_builder.py    # comic-page grid layout
│   │   └── exporters.py         # PDF export
│   └── schemas.py           # Pydantic models
├── templates/               # Jinja templates
├── static/                  # CSS, JS, generated panels & exports
├── .env
├── requirements.txt
└── run.py
```

## Notes

- Generated images land in `static/panels/`, PDFs in `static/exports/`.
- The last generated comic is kept in memory; add a database for persistence.
