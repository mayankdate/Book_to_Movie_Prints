# Book-to-Movie Prints

A gallery of A4 posters pairing novels with their film adaptations, for a one-off club event. Printed once, framed, used, done.

## Code rules

- Never code unnecessary fallbacks, silence warnings, or silently skip things.
- Keep code simple and straightforward.

## Structure

- `data/data.csv` — one row per entry.
- `data/bookcovers/` — image files referenced by the `book_image` column (filename only, no path).
- `data/movieposters/` — image files referenced by the `movie_image` column (filename only, no path).
- `scripts/template.html` — Jinja2 template for a single A4 page. Change once to restyle every entry.
- `scripts/render.py` — reads the CSV, renders the template with headless Chromium, writes `output/gallery.pdf`.
- `output/gallery.pdf` — the deliverable.
- `output/gallery.html` — intermediate HTML, left on disk so you can preview design tweaks in a browser without re-running Python.

## Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

The script uses the Chrome you already have installed, so no separate browser download is needed. If Chrome isn't installed, install it, or change `channel="chrome"` in `scripts/render.py` to `channel="msedge"` to use Edge instead.

## Run

```powershell
python scripts/render.py
```

## CSV columns

| Column | Notes |
|---|---|
| `movie_title`, `movie_year`, `director`, `studio`, `lead_cast`, `genre` | Film side of the stat block. |
| `book_title`, `book_author`, `book_year` | Book side of the stat block. |
| `language` | English, Hindi, etc. Shown as a tag. |
| `faithfulness` | Faithful · Loose · Reimagined. Shown as a tag. |
| `realism` | Fiction · Based on real events · Dramatized biography · Memoir. Shown as a tag. |
| `blurb` | One short paragraph. The first letter is dropped-cap styled. |
| `book_image` | Filename only, e.g. `godfather.jpg`. Resolved against `data/bookcovers/`. |
| `movie_image` | Filename only, e.g. `godfather.jpg`. Resolved against `data/movieposters/`. |

## Missing image handling

- If `book_image` or `movie_image` is empty in the CSV, the slot renders as a labeled placeholder.
- If the field names a filename but the file is not on disk, same thing — placeholder rendered, and the missing path is printed to the terminal when `render.py` runs, so you know which images still need sourcing.

## Design knobs (in `scripts/template.html`)

- `--accent`, `--paper`, `--ink`, `--rule`, `--muted` CSS variables.
- Image slot height: `.image-area { height: 118mm; }`.
- Page padding: `.page { padding: 16mm 20mm ... }`.
