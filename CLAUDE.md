# BooKi — textbook PDF → ABR Core Anki cloze cards

The user is a radiology resident preparing for the ABR Core exam. Their primary decks are
**Crack the Core 2022** and **Core Radiology (1st Edition)**; other decks (War Machine, Manual
Yields, Other) are minor. This project adds cards from textbook PDFs that fill gaps in those
decks. Fewer, better cards beat coverage.

## Workflow (one subchapter / ~30 pages per run)

1. **Read** the requested PDF pages: text via `pdftotext` (no `-layout`; two-column pages read
   correctly), and render any rotated or garbled table as an image and read it visually.
2. **Collect figures** with `tools/crop_figs.py`, then check every crop on a contact sheet.
   Auto-detection sometimes misses panels: re-crop those by hand with explicit clip coordinates.
3. **Draft candidate facts**, grouped by card type (below).
4. **Check each candidate against active cards** (see "Overlap check").
5. **Present the outline** to the user (one screen): candidates per type, each with its
   overlap check result (new / delta / skip + the matching card). **Stop and wait for approval.**
6. **Write cards** for approved facts only. Save the import file to `cards/` and figures to `cards/media/`.
7. **Push** with `tools/push_anki.py <file> cards/media` (Anki must be open with AnkiConnect),
   then verify the card count in the deck.
8. **Report**: notes/cards added, skipped facts and why, `flag::verify` and `flag::outdated` items,
   and pages not covered.

## Overlap check (mandatory)

- Compare **only against cards that are not suspended** (`-is:suspended`), across all decks,
  including earlier BooKi decks. Suspended cards don't count: the user may never see them.
- For each candidate, search 2–4 key terms with `tools/search_active.py` and read the matching
  notes. Crack the Core often has long summary notes: read those in full.
- A fact counts as covered only if it sits **inside a cloze** in the active card. Unclozed
  context text is never tested, so it does not count.
- Decide:
  - **Covered**: the same fact, testable the same way → skip. List it in the outline with the
    matching deck so the user can overrule.
  - **Partial**: covered, but the book adds something worth testing → write only the new part
    (or add it to Back Extra).
  - **New** → write the card.
- The check reflects active cards at generation time. It does not track cards the user
  unsuspends later.
- AnkiConnect access to non-BooKi decks is **read-only**: never edit, suspend, move, or delete them.

## What to make cards about

Use these types to *find* facts; let the chapter decide the mix (no quotas).

| `type::` tag   | What it covers |
|----------------|----------------|
| `management`   | Next best step, what changes treatment (e.g., negative mediastinal PET → surgery) |
| `pitfall`      | Normal variants, mimics, false positives/negatives, artifacts |
| `aunt-minnie`  | Image → diagnosis (figure on front, diagnosis as the cloze) |
| `sign`         | Named signs and classic descriptors, whenever the source mentions one |
| `tracer`       | Per-radiotracer facts: mechanism of localization, half-life/energy, dose, prep, excretion/critical organ, key pitfalls |
| `technical`    | Acquisition, patient prep, quantitation (e.g., SUV) |
| `nis`          | Regulations, radiation safety, medical events, pregnancy/breastfeeding, release |
| `physics`      | Physics and QC |
| `ddx`          | Short differential lists only (≤ 4 items) |

## Card-writing rules

- One fact per note, a few words per cloze; enough context that the answer is unambiguous.
- Paraphrase; never copy book text verbatim.
- Hide a list under **one** cloze number (`c1` throughout) unless each item is independently
  high-yield; avoid >2 cloze numbers per note.
- **Numbers**: only ones you act on: doses, timing windows, decision thresholds (e.g., glucose
  150/200 mg/dL, SUV 2.5), and NPV/PPV values that drive a decision. Leave out descriptive
  sensitivity/specificity and incidence figures.
- **Images**: only when the image itself teaches the finding (recognition). The figure goes on
  the front, above the cloze. No decorative images, and don't reuse near-identical whole-body
  images for unrelated facts. Captions go in Back Extra (shortened), never on the image.
- **Back Extra**: `<Book> Fig x.y, p.<printed page>` plus one or two lines of context. Cite the
  printed page (see "Starting a new book" for the PDF → printed offset).
- Anything I add beyond the source (corrections, newer knowledge) is labelled as such in Back Extra.
- **Outdated content** (the book's edition predates current practice):
  keep the card faithful to the book, add `flag::outdated`, and note the current practice in Back Extra.
- Institution- or guideline-dependent values get `flag::verify`.

## Starting a new book

Nothing in the tools is book-specific; each book only needs, on first use:
- a short name (`<Book>`, e.g. used in decks and Back Extra) and a lowercase slug (`<book>`);
- the PDF → printed page offset, worked out from one page and recorded in each chapter file's docstring;
- its edition year, to judge what is `flag::outdated`.

## Decks and tags

- Deck: `BooKi::<Book>::<Chapter short name>` (e.g., `BooKi::<Book>::Ch07 Thyroid`).
- Tags (hierarchical):
  - `ABR::<Section>::<Topic>` (e.g., `ABR::NucMed::Oncology`)
  - `type::<type>` (table above)
  - `src::<book>::ch<NN>` (e.g., `src::<book>::ch07`)
  - `flag::verify`, `flag::outdated` as needed
- The Anki notetype is the built-in **Cloze** (`Text`, `Back Extra`). Media filenames are
  `<book>_ch<NN>_p<pdfpage>_<n>.jpg`.

## Tools

- `tools/crop_figs.py <pdf> <first> <last> <outdir> <prefix>` (prefix = `<book>_ch<NN>`): crops each figure (clusters of embedded
  images + vector overlays) to JPEG. Needs PyMuPDF (scratch venv; not installed system-wide).
- `tools/search_active.py <queries.txt> [extra filter]`: overlap check. Each line is
  `label | anki search terms`; prints unsuspended matching notes with their deck.
- `tools/build_cards.py`: `build(cards, deck, src, abr, ...)` writes the import file, applies
  tags, enforces ≤ 2 cloze numbers, and copies figures to `cards/media/`.
- `cards/<book>_ch<NN>.py`: one per chapter. It holds that chapter's card list and a docstring
  listing the facts skipped as covered. Start each one from `tools/chapter_template.py`.
  Run it as `python3 cards/<book>_ch<NN>.py <figdir>`.
- `tools/push_anki.py <file> [media_dir]`: uploads media and adds notes (duplicate check scoped to the deck).
- `cards/` is git-ignored (the repo is public): chapter card lists, import files, and
  figures derived from copyrighted books never get committed.
- To redo a chapter: delete only its BooKi deck (after confirming every note in it is ours), then push.
