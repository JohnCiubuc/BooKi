"""Overlap check: search UNSUSPENDED Anki cards (all decks) for each query, print matching note text.
Usage: search_active.py <queries.txt> [extra Anki search, e.g. '-deck:BooKi*']
queries.txt: one line per candidate, "label | anki search terms"."""
import html, json, re, sys, urllib.request

def ac(action, **params):
    req = json.dumps({"action": action, "version": 6, "params": params}).encode()
    r = json.load(urllib.request.urlopen("http://localhost:8765", req))
    if r["error"]:
        raise SystemExit(f"{action}: {r['error']}")
    return r["result"]

def plain(s):
    s = re.sub(r"\{\{c\d+::(.*?)(::[^}]*)?\}\}", r"[\1]", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

extra = sys.argv[2] if len(sys.argv) > 2 else ""
for line in open(sys.argv[1], encoding="utf-8"):
    if "|" not in line:
        continue
    label, terms = (x.strip() for x in line.split("|", 1))
    cards = ac("findCards", query=f"-is:suspended {extra} ({terms})")  # parens: OR must not escape the filters
    notes = list(dict.fromkeys(ac("cardsToNotes", cards=cards))) if cards else []
    print(f"\n## {label}  [{terms}] → {len(notes)} active notes")
    infos = ac("notesInfo", notes=notes[:4]) if notes else []
    decks = {}
    if infos:
        for c in ac("cardsInfo", cards=cards[:40]):
            decks.setdefault(c["note"], c["deckName"].split("::")[0])
    for n in infos:
        text = " / ".join(plain(f["value"]) for f in n["fields"].values() if f["value"].strip())
        print(f"  - ({decks.get(n['noteId'], '?')}) {text[:220]}")
