# BooKi
From PDF to ANKI Cards

BooKi turns radiology textbook chapters (PDF) into a small set of high-yield Anki cloze cards for
the **ABR Core exam**, working alongside Claude Code. It fills gaps in the decks you already study
(e.g. Crack the Core, Core Radiology) instead of duplicating them.

No textbook content is stored here: PDFs, generated card files and cropped figures are git-ignored.

## How it works

One subchapter (~30 pages) per run:

1. **Read** the PDF pages: text via `pdftotext`; rotated or garbled tables are read as page images.
2. **Crop figures** (`tools/crop_figs.py`) and check them visually.
3. **Draft candidate facts** by card type: management, pitfall, aunt-minnie (image → diagnosis),
   sign, tracer, technical, NIS, physics, short differentials.
4. **Overlap check** (`tools/search_active.py`) against your **unsuspended** Anki cards only.
   A fact counts as covered only if an active card clozes it.
5. **Outline approval**: you approve a one-screen list before any cards are written.
6. **Build** (`cards/<book>_ch<NN>.py` → `tools/build_cards.py`) and **push** to Anki
   (`tools/push_anki.py`) via AnkiConnect.

The full rules (card-writing style, number and image policy, tags, flags) are in
[`CLAUDE.md`](CLAUDE.md), which Claude Code loads automatically in this folder.

## Requirements

- [Anki](https://apps.ankiweb.net/) running, with the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on
- `poppler-utils` (`pdftotext`, `pdftoppm`)
- Python 3 with Pillow; [PyMuPDF](https://pymupdf.readthedocs.io/) for figure cropping
  (install it in a venv: `python3 -m venv .venv && .venv/bin/pip install pymupdf`)

## Usage

Works with any book. Replace `<book>_ch<NN>` with your own slug, e.g. `mettler_ch11`.

```bash
# 1. crop figures from a PDF page range
.venv/bin/python tools/crop_figs.py "<book>.pdf" <first> <last> /tmp/figs <book>_ch<NN>

# 2. overlap check: one "label | anki search" per line
python3 tools/search_active.py queries.txt '-deck:BooKi*'

# 3. start the chapter's card list from the template, fill it in, then build
cp tools/chapter_template.py cards/<book>_ch<NN>.py
python3 cards/<book>_ch<NN>.py /tmp/figs

# 4. push to Anki (skips notes already in the deck)
python3 tools/push_anki.py cards/<book>_ch<NN>.txt cards/media
```

A chapter file sets the book name, deck, tags and slug, plus a list of
`(type, cloze_text, back_extra, figure_or_None, flags)` tuples and a docstring of facts skipped as
already covered. The whole `cards/` folder stays local: it is git-ignored because its content is
derived from copyrighted books.

## Layout

```
CLAUDE.md            workflow and card rules (the spec)
tools/
  crop_figs.py       crop figures from PDF pages to JPEG
  search_active.py   overlap check against unsuspended Anki cards
  build_cards.py     card list → Anki import file, tags, figure copy
  push_anki.py       upload media and add notes through AnkiConnect
  chapter_template.py  starting point for a chapter's card list
cards/               local only (git-ignored): per-chapter card lists, import files, figures
```

## Tags

- `ABR::<Section>::<Topic>`, e.g. `ABR::NucMed::PET-Oncology`
- `type::management|pitfall|aunt-minnie|sign|tracer|technical|nis|physics|ddx`
- `src::<book>::ch<NN>`
- `flag::verify` (institution- or guideline-dependent) and `flag::outdated` (the source predates current practice)

## Disclaimer

For personal study. Cards are written with an AI model and can contain errors: check them
against the source page cited on each card, especially those tagged `flag::verify` or `flag::outdated`.
