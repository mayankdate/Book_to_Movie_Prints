"""Render output/gallery.pdf from data/data.csv using scripts/template.html.

Run from any directory:
    python scripts/render.py
"""
import csv
from pathlib import Path
from jinja2 import Template
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "data.csv"
TEMPLATE = ROOT / "scripts" / "template.html"
BOOK_DIR = ROOT / "data" / "bookcovers"
POSTER_DIR = ROOT / "data" / "movieposters"
GALLERY_HTML = ROOT / "output" / "gallery.html"
GALLERY_PDF = ROOT / "output" / "gallery.pdf"

with open(DATA, newline="", encoding="utf-8") as f:
    entries = list(csv.DictReader(f))

# When an image file named in the CSV is not on disk, clear the field so the
# template renders a labeled placeholder, and report which files are missing.
missing = []
for e in entries:
    if e["book_image"] and not (BOOK_DIR / e["book_image"]).exists():
        missing.append(f"data/bookcovers/{e['book_image']}  (for {e['movie_title']})")
        e["book_image"] = ""
    if e["movie_image"] and not (POSTER_DIR / e["movie_image"]).exists():
        missing.append(f"data/movieposters/{e['movie_image']}  (for {e['movie_title']})")
        e["movie_image"] = ""

if missing:
    print("Missing image files (rendered as placeholders):")
    for m in missing:
        print(f"  {m}")

template = Template(TEMPLATE.read_text(encoding="utf-8"))
html = template.render(entries=entries, base_url=ROOT.as_uri() + "/")
GALLERY_HTML.write_text(html, encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page()
    page.goto(GALLERY_HTML.as_uri(), wait_until="load")
    page.pdf(
        path=str(GALLERY_PDF),
        format="A4",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
    )
    browser.close()

print(f"Rendered {len(entries)} entries -> {GALLERY_PDF.relative_to(ROOT)}")
