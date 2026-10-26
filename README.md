# Book-to-Movie Prints

Generates a print-ready A4 PDF gallery pairing novels with their film adaptations. Each book+movie pair becomes one page in the PDF. Designed for a film/book club event; starter set of 50 English and Hindi pairings included.

## Quick start

```powershell
# 1. Set up Python environment
uv sync

# 2. Get a free TMDb API key (see below) and save it:
echo YOUR_KEY > TMDB_key.txt

# 3. Fetch metadata and images
uv run python scripts/populate.py

# 4. Render the PDF
uv run python scripts/render.py
# Output: output/gallery.pdf
```

## TMDb API key

1. Sign up at https://www.themoviedb.org/signup (free, no card required).
2. Go to Settings → API → Request an API Key → Developer.
3. Copy the **API Key (v3 auth)** and save it to `TMDB_key.txt` in the project root.

Open Library (for book metadata) requires no key.

## Adding entries

Open `data/data.csv` and add a row. The only required fields for auto-fill are `movie_title`, `movie_year`, `book_title`, and `book_author`. Fill `faithfulness`, `realism`, and `blurb` yourself — `populate.py` will never overwrite cells that already have content.

Run `uv run python scripts/populate.py` again to fetch the new entry.

## Project structure

```
Book_to_Movie_Prints/
├── data/
│   ├── data.csv          # one row per book–movie pair
│   ├── bookcovers/       # downloaded cover images
│   └── movieposters/     # downloaded poster images
├── scripts/
│   ├── populate.py       # fetches metadata and images from TMDb + Open Library
│   ├── render.py         # renders HTML template → PDF via headless Chrome
│   └── template.html     # Jinja2 A4 page template
├── output/
│   ├── gallery.pdf       # final deliverable
│   └── gallery.html      # browser preview (open to tweak CSS without re-running Python)
├── TMDB_key.txt          # your TMDb key (gitignored)
├── pyproject.toml        # Python packages (uv); uv.lock pins exact versions
└── uv.lock
```

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs Python 3.14 for you)
- Google Chrome (or Edge — see `scripts/render.py` to switch)
- `uv sync`
