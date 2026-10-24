"""Push a tab-separated Anki cloze import file into Anki via AnkiConnect (localhost:8765)."""
import json, sys, urllib.request

def ac(action, **params):
    req = json.dumps({"action": action, "version": 6, "params": params}).encode()
    r = json.load(urllib.request.urlopen("http://localhost:8765", req))
    if r["error"]:
        raise SystemExit(f"{action}: {r['error']}")
    return r["result"]

deck, notes = None, []
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith("#deck:"):
        deck = line[6:]
    elif line and not line.startswith("#"):
        text, extra, tags = line.split("\t")
        notes.append((text, extra, tags.split()))
assert deck and notes

if len(sys.argv) > 2:  # optional media dir: upload every image referenced by <img src>
    import base64, os, re
    for name in sorted({m for t, _, _ in notes for m in re.findall(r'<img src="([^"]+)"', t)}):
        data = base64.b64encode(open(os.path.join(sys.argv[2], name), "rb").read()).decode()
        ac("storeMediaFile", filename=name, data=data)

ac("createDeck", deck=deck)
payload = [{"deckName": deck, "modelName": "Cloze",
            "fields": {"Text": t, "Back Extra": e}, "tags": tg,
            "options": {"allowDuplicate": False, "duplicateScope": "deck"}} for t, e, tg in notes]
ok = ac("canAddNotes", notes=payload)
addable = [n for n, k in zip(payload, ok) if k]
ids = ac("addNotes", notes=addable) if addable else []
print(f"{sum(i is not None for i in ids)} added, {len(payload) - len(addable)} skipped as duplicates, deck '{deck}'")
