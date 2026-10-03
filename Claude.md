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
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
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
python scripts/populate.py      # fetches metadata, downloads images
python scripts/render.py        # builds output/gallery.pdf
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

### Blurb trade-off

Blurbs are currently editorial — adaptation-focused one-liners written by me, like *"Puzo co-wrote the screenplay with Coppola, which is partly why the film captures the novel's weight so completely."* This fits the gallery's book-to-film theme but carries my error rate (small facts I might remember wrong).

The alternative is to delete the blurb column and have `populate.py` fetch TMDb's `overview` field instead — the official plot synopsis, like *"Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family..."* Zero factual risk from me, but it describes the film rather than the adaptation. I didn't wire this in because the editorial direction seems to fit a book-to-film gallery better, but it's a one-screen change in `populate.py` to switch.

## Project structure

```
Book_to_Movie_Prints/
├── Claude.md                       # this file
├── TMDB_key.txt                    # (gitignored) your TMDb API key, one line
├── requirements.txt
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

## Design decisions

- **Why one HTML template, not Canva:** 50+ entries in Canva means 50 manual edits every time the design changes. One template + one data file means a design tweak is a single CSS edit plus a re-render.
- **Why Playwright + system Chrome, not weasyprint:** weasyprint is one `pip install` on Linux and Mac but needs a separate GTK3 install on Windows. For a one-off project on Windows, that's the wrong trade. Playwright drives the Chrome you already have — no browser download, and modern CSS Just Works.
- **Why TMDb + Open Library:** TMDb is the standard for film metadata and poster art, free with a key, with excellent Bollywood coverage. Open Library covers book metadata and covers, no key needed. Together they handle both English and Hindi material reasonably well.
- **Why idempotent cell-level fills in populate.py:** so you can add rows piecemeal, override any fetched value by hand, and rerun as often as you like without re-downloading images or clobbering edits.
- **Design language:** editorial / museum-plaque — warm paper tone, serif title (Georgia), small-caps labels. Reads as "catalog" rather than "slideshow". Each page is one movie: title and subtitle on top, a four-tag strip (Language · Faithfulness · Realism · Genre), two portrait image slots side by side, a split stat block (The Novel ⟋ The Film), then a short blurb.

## Caveats on the starter data

Only three fields in the starter are editorial (not API-fillable): `faithfulness`, `realism`, `blurb`. Caveats attach to those plus the pairing choices themselves:

- "Faithfulness" and "Realism" are judgment calls with no authoritative API source. Several are debatable (The Shining, A Clockwork Orange, Little Women). Overwrite freely.
- Blurbs are adaptation-focused rather than plot synopses — see the "Blurb trade-off" section above. They are factually careful but written from memory, so expect the occasional wrong detail. Scan them before printing.
- A few titles live on the "novels" edge: 7 Khoon Maaf, The Blue Umbrella, and Shawshank come from novellas. Hamlet/Othello/Macbeth-based films (Haider, Omkara, Maqbool) were left out as plays — easy to add if you want them.
- Open Library's coverage of non-English books is spotty. For some Hindi/Bengali entries (Chokher Bali, Umrao Jaan Ada, Sahib Bibi Aur Ghulam, Pinjar), `book_year` and `book_image` may come back empty after `populate.py`. Fill those cells manually; a `book_year` typed in will stay.

## Copyright

Book covers and movie posters are copyrighted. This project uses them for a non-commercial, one-off club gallery — editorial display, not reproduction for sale. That's the usual fair-use territory for film clubs and festivals. Not legal advice, just the practice.
