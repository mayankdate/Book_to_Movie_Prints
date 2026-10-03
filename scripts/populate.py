"""Populate empty fields in data/data.csv from TMDb and Open Library.

For each row, this fills only cells that are currently empty — anything already
filled is left alone. Downloads any missing poster or book cover to the right
folder and writes its filename back to the CSV. The CSV is saved after every
row, so a crash halfway through doesn't lose earlier work.

Needs TMDB_key.txt at the project root containing your TMDb API key on one line.
Get a free key at https://www.themoviedb.org/settings/api

Run from any directory:
    python scripts/populate.py
"""
import csv
import re
from pathlib import Path
import requests

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "data.csv"
BOOK_DIR = ROOT / "data" / "bookcovers"
POSTER_DIR = ROOT / "data" / "movieposters"
TMDB_KEY = (ROOT / "TMDB_key.txt").read_text(encoding="utf-8").strip()

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w780"
OL_SEARCH = "https://openlibrary.org/search.json"
OL_COVER = "https://covers.openlibrary.org/b/id/{id}-L.jpg"

LANG_NAMES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil",
    "te": "Telugu", "ml": "Malayalam", "mr": "Marathi", "pa": "Punjabi",
    "ur": "Urdu", "fr": "French", "es": "Spanish", "de": "German",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "sv": "Swedish",
    "zh": "Chinese", "ru": "Russian", "pt": "Portuguese",
}

HEADERS = {"User-Agent": "BookToMoviePrints/1.0 (club gallery project)"}

TMDB_COLS = ["director", "studio", "lead_cast", "genre", "language", "movie_image"]
OL_COLS = ["book_year", "book_image"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def download(url, dest):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    dest.write_bytes(r.content)


def tmdb_fetch(title, year):
    """Return dict of film fields plus poster_url, or None if no match."""
    s = requests.get(
        f"{TMDB_BASE}/search/movie", headers=HEADERS, timeout=30,
        params={"api_key": TMDB_KEY, "query": title, "year": year},
    )
    s.raise_for_status()
    results = s.json().get("results", [])
    if not results:
        return None
    movie_id = results[0]["id"]
    r = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}", headers=HEADERS, timeout=30,
        params={"api_key": TMDB_KEY, "append_to_response": "credits"},
    )
    r.raise_for_status()
    d = r.json()
    directors = [c["name"] for c in d["credits"]["crew"] if c["job"] == "Director"]
    cast = [c["name"] for c in d["credits"]["cast"][:3]]
    return {
        "director": ", ".join(directors),
        "studio": d["production_companies"][0]["name"] if d["production_companies"] else "",
        "lead_cast": ", ".join(cast),
        "genre": ", ".join(g["name"] for g in d["genres"][:2]),
        "language": LANG_NAMES.get(d["original_language"], d["original_language"]),
        "poster_url": f"{TMDB_IMG}{d['poster_path']}" if d.get("poster_path") else None,
    }


def ol_fetch(title, author):
    """Return {year, cover_url} or None if no match."""
    s = requests.get(
        OL_SEARCH, headers=HEADERS, timeout=30,
        params={"title": title, "author": author, "limit": 10},
    )
    s.raise_for_status()
    docs = s.json().get("docs", [])
    if not docs:
        return None
    with_cover = next((d for d in docs if d.get("cover_i")), None)
    chosen = with_cover or docs[0]
    year = chosen.get("first_publish_year")
    cover_id = chosen.get("cover_i")
    return {
        "year": str(year) if year else "",
        "cover_url": OL_COVER.format(id=cover_id) if cover_id else None,
    }


with open(DATA, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)


def save():
    with open(DATA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


for i, row in enumerate(rows, 1):
    print(f"[{i:>2}/{len(rows)}] {row['movie_title']} ({row['movie_year']})")
    changed = False

    if any(not row[c] for c in TMDB_COLS):
        try:
            data = tmdb_fetch(row["movie_title"], row["movie_year"])
        except requests.RequestException as e:
            data = None
            print(f"    TMDb error: {e}")
        if data is None:
            print(f"    TMDb: no match")
        else:
            for col in ["director", "studio", "lead_cast", "genre", "language"]:
                if not row[col] and data[col]:
                    row[col] = data[col]
                    changed = True
            if not row["movie_image"] and data["poster_url"]:
                fname = f"{slug(row['movie_title'])}_{row['movie_year']}.jpg"
                try:
                    download(data["poster_url"], POSTER_DIR / fname)
                    row["movie_image"] = fname
                    changed = True
                except requests.RequestException as e:
                    print(f"    poster download failed: {e}")

    if any(not row[c] for c in OL_COLS):
        try:
            data = ol_fetch(row["book_title"], row["book_author"])
        except requests.RequestException as e:
            data = None
            print(f"    Open Library error: {e}")
        if data is None:
            print(f"    Open Library: no match for '{row['book_title']}' by {row['book_author']}")
        else:
            if not row["book_year"] and data["year"]:
                row["book_year"] = data["year"]
                changed = True
            if not row["book_image"] and data["cover_url"]:
                fname = f"{slug(row['book_title'])}.jpg"
                try:
                    download(data["cover_url"], BOOK_DIR / fname)
                    row["book_image"] = fname
                    changed = True
                except requests.RequestException as e:
                    print(f"    cover download failed: {e}")

    if changed:
        save()

filled = sum(1 for r in rows if r["movie_image"]), sum(1 for r in rows if r["book_image"])
print(f"\nPosters: {filled[0]}/{len(rows)}.  Book covers: {filled[1]}/{len(rows)}.")
