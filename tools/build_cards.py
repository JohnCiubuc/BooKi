"""Build an Anki cloze import file (+ copy figures) from a chapter's card list.
Card tuple: (type, text, extra, figure_or_None, flags) — figure is a filename in figdir; flags e.g. "verify outdated"."""
import os, re, shutil

def build(cards, deck, src, abr, out_txt, figdir, media_out):
    os.makedirs(media_out, exist_ok=True)
    lines = ["#separator:tab", "#html:true", "#notetype:Cloze", f"#deck:{deck}", "#tags column:3"]
    for typ, text, extra, fig, flags in cards:
        assert "\t" not in text + extra and "\n" not in text + extra, text
        nums = set(re.findall(r"\{\{c(\d+)::", text))
        assert nums and len(nums) <= 2 and text.count("{{") == text.count("}}"), text
        if fig:
            shutil.copy(os.path.join(figdir, fig), os.path.join(media_out, fig))
            text = f'<img src="{fig}"><br>{text}'
        tags = [f"ABR::{abr}", f"type::{typ}", f"src::{src}"] + [f"flag::{f}" for f in flags.split()]
        lines.append(f"{text}\t{extra}\t{' '.join(tags)}")
    open(out_txt, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    n_cards = sum(len(set(re.findall(r"\{\{c(\d+)::", c[1]))) for c in cards)
    print(f"{len(cards)} notes, {n_cards} cards, {sum(1 for c in cards if c[3])} with figures → {out_txt}")
