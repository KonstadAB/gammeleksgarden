#!/usr/bin/env python3
"""Lägger in de dukade bilderna (illustrationer) på fest, bröllop och i galleriet, alla tio språk.

Körs efter verktyg/rundturer.py: python3 verktyg/dukat.py. Hoppar över sidor som redan har dem.
Bilderna är våra egna foton av lokalen, digitalt dukade, och märks alltid som illustration.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rundturer import Page, e, picture
from rundturer_text import DUKAT, DUKAT_H2, DUKAT_NOTE, ILL, LANGS

FEST = ["22", "23", "24", "25", "26", "26d"]


def cap(lang, k):
    return f"{DUKAT[k][lang]} ({ILL[lang]})"


def figs(p, keys):
    return "".join(f'<figure class="stack shot">{picture(p.rel, "dukat-" + k, cap(p.lang, k), sizes="(min-width: 900px) 33vw, 100vw", w=1600, h=1062)}'
                   f'<figcaption class="small muted">{e(cap(p.lang, k))}</figcaption></figure>' for k in keys)


def reviewer(p, key, first, poster):
    p.s = re.sub(r'<script type="application/json" id="pano-t">.*?</script>\n', "", p.s, flags=re.S)
    v = p.viewer(key, FEST, first=first, poster=poster)
    p.sub(rf'<!--pano:{key}-->.*?<!--/pano:{key}-->', lambda m: v)


def fest(lang):
    p = Page(lang, "fest-och-event/index.html")
    if "dukat-02" in p.s: return
    reviewer(p, "fest", "22", "22")
    block = (f'<section class="section">\n  <div class="wrap stack-lg">\n    <div class="section-head"><h2>{e(DUKAT_H2[lang])}</h2>'
             f'<p class="muted">{e(DUKAT_NOTE[lang])}</p></div>\n    <div class="grid-3">{figs(p, ["02", "12", "11", "10", "06", "08"])}</div>\n  </div>\n</section>\n\n')
    i = p.s.find('<section class="section band">')
    p.s = p.s[:i] + block + p.s[i:]
    p.save()


def brollop(lang):
    p = Page(lang, "fest-och-event/brollop.html")
    if "dukat-02" in p.s: return
    reviewer(p, "brollop", "26d", "26d")
    block = (f'\n<section class="section">\n  <div class="wrap stack-lg">\n    <div class="section-head"><h2>{e(DUKAT_H2[lang])}</h2>'
             f'<p class="muted">{e(DUKAT_NOTE[lang])}</p></div>\n    <div class="grid-3">{figs(p, ["02", "07", "06"])}</div>\n  </div>\n</section>')
    m = re.search(r'<!--/pano:brollop-->.*?</section>', p.s, re.S)
    p.s = p.s[:m.end()] + block + p.s[m.end():]
    p.save()


def galleri(lang):
    p = Page(lang, "galleri/index.html")
    if "/dukat-02" in p.s: return
    prefix = re.search(r'<button type="button" aria-label="([^"]*?): ', p.s).group(1)
    items = "".join(
        f'<div class="" data-cat="fest" data-title="{e(cap(lang, k))}"><button type="button" aria-label="{prefix}: {e(cap(lang, k))}">'
        f'<figure class="ph photo ">{picture(p.rel, "dukat-" + k, cap(lang, k), w=1600, h=1062)}</figure></button></div>'
        for k in ("02", "06", "08", "13"))
    p.sub(r'(</div>)(\s*</div>\s*</section>\s*<div class="lightbox")', lambda m: m.group(1) + items + m.group(2))
    open(p.file, "w", encoding="utf-8").write(p.s)


if __name__ == "__main__":
    for lang in LANGS:
        fest(lang); brollop(lang); galleri(lang)
    print("Klart.")
