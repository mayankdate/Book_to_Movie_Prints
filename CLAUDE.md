# Book-to-Movie Prints

A gallery of A4 prints pairing novels with their film adaptations, for a one-off club event. Each entry becomes a single A4 page in a multi-page PDF ready for a print shop.

Mix of English and Hindi cinema; starter set is 50 entries.

## Code rules

- Never code unnecessary fallbacks, silence warnings, or silently skip things.
- Keep code simple and straightforward.

## How it works

Two scripts, one data file, one template:

1. **`data/data.csv`** holds one row per entry. You own the editorial fields; the APIs fill the rest.
2. **`scripts/populate.py`** reads the CSV, calls TMDb and Open Library for anything that's empty, downloads book covers and movie posters into their folders, writes everything back. Idempotent, cell-level — rerun it whenever you add new rows.
3. **`scripts/template.html`** is the Jinja2 template for a single A4 page. Change it once to restyle every entry.
4. **`scripts/render.py`** merges template + CSV, drives headless Chrome, writes `output/gallery.pdf`.

## One-time setup

### 1. Python environment

From the project root:

```powershell
uv sync
```

### 2. Chrome

`render.py` uses the Chrome you have installed, so no separate browser download is needed. If Chrome isn't there, change `channel="chrome"` in `scripts/render.py` to `channel="msedge"` to use Edge instead.

### 3. TMDb API key

1. Sign up at https://www.themoviedb.org/signup (free, no card). Verify your email.
2. Go to https://www.themoviedb.org/settings/api → **Request an API Key** → **Developer**.
3. Fill in the form: application name = anything (e.g. "Book to Movie Prints"), URL = `http://localhost`, summary = one line. Approval is instant.
4. Copy the key labeled **API Key (v3 auth)**.
5. Save it to **`TMDB_key.txt`** at the project root — one line, just the key, no quotes. This file is in `.gitignore`.

Open Library needs no key.

## Running

```powershell
uv run python scripts/populate.py      # fetches metadata, downloads images
uv run python scripts/render.py        # builds output/gallery.pdf
```

`populate.py` prints one line per entry showing what it fetched or what it couldn't find. Any row it fails on stays empty; `render.py` renders those slots as labeled placeholders. The CSV is saved after every row, so Ctrl+C is safe.

Preview as you tweak the design by opening `output/gallery.html` in a browser — no need to re-run Python for CSS-only changes.

## Adding entries

Append rows to `data.csv`. Minimum fields to let `populate.py` do its job: `movie_title`, `movie_year`, `book_title`, `book_author`. Fill `faithfulness`, `realism`, and `blurb` by hand before or after; `populate.py` never touches cells that already have content.

Running `populate.py` again only hits the APIs for rows with empty cells, so you can run it as often as you like.

## CSV columns

| Column | Filled by | Notes |
|---|---|---|
| `movie_title`, `movie_year` | you | drive the TMDb search |
| `director`, `studio`, `lead_cast`, `genre`, `language` | populate.py (TMDb) | pre-fill to override |
| `book_title`, `book_author` | you | drive the Open Library search |
| `book_year` | populate.py (Open Library) | pre-fill to override |
| `faithfulness` | you | Faithful · Loose · Reimagined |
| `realism` | you | Fiction · Based on real events · Dramatized biography · Memoir |
| `blurb` | you | one short paragraph |
| `book_image`, `movie_image` | populate.py | filename only; auto-written after download |

### Missing image handling in `render.py`

- Empty `book_image` or `movie_image` → labeled placeholder in the slot. Silent (you're mid-work).
- Filename present but file missing from disk → placeholder plus terminal warning naming the file.

## Project structure

```
Book_to_Movie_Prints/
├── TMDB_key.txt                    # (gitignored) your TMDb API key, one line
├── pyproject.toml
├── uv.lock
├── .gitignore
├── data/
│   ├── data.csv                    # the data
│   ├── bookcovers/                 # downloaded book covers
│   └── movieposters/               # downloaded movie posters
├── scripts/
│   ├── template.html               # A4 page template
│   ├── populate.py                 # fetches metadata + images
│   └── render.py                   # builds the PDF
└── output/
    ├── gallery.pdf                 # the deliverable
    └── gallery.html                # debug preview
```

## Design knobs

In `scripts/template.html`:

- `--accent`, `--paper`, `--ink`, `--rule`, `--muted` CSS variables at the top.
- `.image-area { height: 118mm; }` — book cover / poster box height.
- `.page { padding: 16mm 20mm ... }` — page margins.

## Credentials

TMDb API key goes in `TMDB_key.txt` at the project root (gitignored). Never hardcode or commit it.
