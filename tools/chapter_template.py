"""<Book title> — Ch<NN> <chapter title>, PDF pp <first>-<last> (printed p.<a>-<b>; printed = PDF − <offset>).
Overlap-checked <date> against unsuspended cards. Skipped as covered: <facts + matching deck>.
Copy to cards/<book>_ch<NN>.py (cards/ is git-ignored), fill in, then run:
    python3 cards/<book>_ch<NN>.py <figdir>"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from build_cards import build

BOOK = "Book"            # short name shown in Back Extra and deck, e.g. "Mettler"
SLUG = "book_ch00"       # file/media prefix, e.g. "mettler_ch11"
DECK = f"BooKi::{BOOK}::Ch00 Short title"
SRC = "book::ch00"       # → tag src::book::ch00
ABR = "Section::Topic"   # → tag ABR::Section::Topic, e.g. "NucMed::PET-Oncology"

F = lambda page_idx: f"{SLUG}_p{page_idx}.jpg"   # figure file from tools/crop_figs.py, e.g. F("338_0")
B = BOOK + " "
# (type, cloze text, back extra, figure or None, flags) — see CLAUDE.md for types and rules
cards = [
    ("pitfall", "Example: {{c1::answer}} with enough context to be unambiguous.",
     B + "Fig x.y, p.123. One or two lines of context.", None, ""),
]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build(cards, deck=DECK, src=SRC, abr=ABR, out_txt=os.path.join(here, f"{SLUG}.txt"),
          figdir=sys.argv[1], media_out=os.path.join(here, "media"))
