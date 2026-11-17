#!/usr/bin/env python3
"""Bygger in 360°-visningarna i sidorna på alla tio språk.

Körs från repots rot: python3 verktyg/rundturer.py
Sidor som redan har en visning (markören <!--pano:) hoppas över, så skriptet kan köras igen
efter att nya sidor lagts till. Texterna finns i verktyg/rundturer_text.py.
Bilderna ligger i assets/pano/<id>-2048.jpg och -4096.jpg (kopior av VR-fotograferingen,
originalen är orörda). Visaren är Pannellum 2.5.6 (MIT), laddas från egen server först vid klick.
360°-materialet är bara för webbplatsen, aldrig för Google.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rundturer_text import (BEDS, CAP_BATH, CAP_LOFT, CAP_MAIN, CAT_TITLE, CATS, CHIP, DRONE, DT, LANGS,
                            ROOM, ROOMS, SCENES, SEC, TYPE_ROOM, UI)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTERS = {"01", "04", "05", "06", "09", "12", "15", "22", "29"}
e = lambda s: html.escape(s, quote=True)


def scene_text(lang, sid):
    """(titel, bildtext) för en scen på ett språk."""
    for n, (ids, dbl_down, dbl_up) in ROOMS.items():
        if sid in ids:
            b = BEDS[lang]
            d = b[0] if dbl_down else b[1]
            u = b[2] if dbl_up else b[3]
            room = f"{ROOM[lang]} {n}"
            k = ids.index(sid)
            if k == 0:
                return room, CAP_MAIN[lang].format(d=d, u=u)
            if k == 1:
                return f"{room} · {CHIP['loft'][lang]}", CAP_LOFT[lang].format(u=u)
            return f"{room} · {CHIP['bath'][lang]}", CAP_BATH[lang]
    t, c = SCENES[sid]
    return t[lang], c[lang]


def picture(rel, name, alt, sizes="(min-width: 900px) 50vw, 100vw", w=1600, h=900):
    b = f"{rel}assets/img/{name}"
    return (f'<picture><source type="image/webp" srcset="{b}-800.webp 800w, {b}-1600.webp 1600w" sizes="{sizes}">'
            f'<img src="{b}-1600.jpg" srcset="{b}-800.jpg 800w, {b}-1600.jpg 1600w" sizes="{sizes}" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></picture>')


class Page:
    def __init__(self, lang, path):
        self.lang, self.path = lang, path
        self.file = os.path.join(ROOT, (lang + "/" if lang != "sv" else "") + path)
        depth = path.count("/") + (0 if lang == "sv" else 1)
        self.rel = "../" * depth
        self.s = open(self.file, encoding="utf-8").read()
        self.used = []

    def viewer(self, key, scenes, first=None, chips=None, poster=None):
        lang, rel = self.lang, self.rel
        first = first or scenes[0]
        poster = poster or first
        assert poster in POSTERS, poster
        self.used += scenes
        t, c = scene_text(lang, first)
        pt, pc = scene_text(lang, poster)
        chips = chips if chips is not None else scenes
        cb = "".join(f'<button type="button" data-scene="{s}" aria-pressed="{"true" if s == first else "false"}">{e(lbl)}</button>'
                     for s, lbl in ((s, self.chip_label(s, scenes)) for s in chips))
        alt = f"{pt}. {pc}" if pc else pt
        return (f'<!--pano:{key}--><div class="pano-wrap">'
                f'<div class="pano" data-scenes="{",".join(scenes)}" data-first="{first}" data-base="{rel}assets/pano/" role="region" aria-label="{e(UI["region"][lang])}: {e(t)}">'
                f'{picture(rel, "pano-" + poster, alt)}'
                f'<button type="button" class="pano-start"><span class="pano-btn">{e(UI["start"][lang])}</span></button>'
                f'<div class="pano-view"></div></div>'
                f'<div class="pano-chips" role="group" aria-label="{e(UI["views"][lang])}">{cb}</div>'
                f'<p class="pano-cap" aria-live="polite"><strong>{e(t)}</strong> <span>{e(c)}</span></p>'
                f'<p class="pano-hint" hidden>{e(UI["hint"][lang])}</p>'
                f'</div><!--/pano:{key}-->')

    def chip_label(self, sid, scenes):
        # Visning av ett enda rum: korta knappar (Rummet, Loftet, Badrummet).
        if set(scenes) <= {s for ids, _, _ in ROOMS.values() for s in ids} and len(scenes) == 3:
            for ids, _, _ in ROOMS.values():
                if sid in ids:
                    return CHIP[("main", "loft", "bath")[ids.index(sid)]][self.lang]
        return scene_text(self.lang, sid)[0]

    def sub(self, pattern, repl, flags=re.S, count=1):
        new, n = re.subn(pattern, repl, self.s, count=count, flags=flags)
        if not n:
            raise SystemExit(f"Hittade inte mönstret i {self.lang}/{self.path}: {pattern[:80]}")
        self.s = new

    def insert_after(self, pattern, block):
        m = re.search(pattern, self.s, re.S)
        if not m:
            raise SystemExit(f"Hittade inte {pattern[:60]} i {self.lang}/{self.path}")
        self.s = self.s[:m.end()] + "\n" + block + self.s[m.end():]

    def save(self):
        lang = self.lang
        data = {"ui": {k: UI[k][lang] for k in ("start", "loading", "err", "hint")},
                "s": {sid: list(scene_text(lang, sid)) for sid in dict.fromkeys(self.used)}}
        js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        self.sub(r'(<script type="application/json" id="t">)', f'<script type="application/json" id="pano-t">{js}</script>\n\\1')
        open(self.file, "w", encoding="utf-8").write(self.s)


def bed_plan(dbl_down, dbl_up):
    def beds(y, dbl):
        if dbl:
            return f'<rect x="34" y="{y}" width="52" height="13" rx="2"/>'
        return f'<rect x="24" y="{y}" width="32" height="13" rx="2"/><rect x="64" y="{y}" width="32" height="13" rx="2"/>'
    return ('<svg class="bed-plan" viewBox="0 0 120 100" aria-hidden="true" focusable="false">'
            '<path class="bp-house" d="M6 38 L60 6 L114 38 V96 H6 Z"/><path class="bp-floor" d="M6 58 H86"/>'
            '<path class="bp-ladder" d="M94 58 L100 96 M104 58 L110 96 M96 70 H106 M98 82 H108"/>'
            f'<g class="bp-beds">{beds(42, dbl_up)}{beds(80, dbl_down)}</g></svg>')


def room_types(lang):
    """Namn och antal per rumstyp, hämtat från språkets egen rumsöversikt."""
    s = open(os.path.join(ROOT, (lang + "/" if lang != "sv" else "") + "rum/index.html"), encoding="utf-8").read()
    out = {}
    for art in re.findall(r'<article class="card">(.*?)</article>', s, re.S):
        slug = re.search(r'href="[^"]*rum/(\w+)"', art).group(1)
        name = re.search(r'<h2[^>]*>(.*?)</h2>', art).group(1)
        count = re.findall(r'<span>(.*?)</span>', re.search(r'<div class="meta">(.*?)</div>', art).group(1))[-1]
        out[slug] = (name, count)
    return out


def done(p):
    return "<!--pano:" in p.s


def do_home(lang):
    p = Page(lang, "index.html")
    if done(p): return
    v = p.viewer("gard", ["05", "01", "02", "03", "04", "27", "28", "29"], chips=["01", "03", "04", "05", "29"])
    p.sub(r'<div class="media-slot video"><video[^>]*>.*?</video></div>(\s*<div class="stack-lg">\s*<p class="eyebrow">.*?</p>\s*<h2>.*?</h2>\s*)<p class="lede">.*?</p>(\s*<div class="btn-row">)<a class="btn btn-green" href="rundtur/">.*?</a>',
          lambda m: f'{v}{m.group(1)}<p class="lede">{e(SEC["home_lede"][lang])}</p>{m.group(2)}<a class="btn btn-green" href="rundtur/">{e(SEC["whole"][lang])}</a>')
    p.save()


def do_rum_index(lang):
    p = Page(lang, "rum/index.html")
    if done(p): return
    types = room_types(lang)
    cards = []
    for no, (n, slug) in enumerate(CATS, 1):
        ids, dd, du = ROOMS[n]
        b = BEDS[lang]
        name, count = types[slug]
        v = p.viewer(f"rum{n}", list(ids))
        cards.append(
            f'<article class="cat">'
            f'<h3 class="cat-title"><span class="cat-no" aria-hidden="true">{no}</span>{e(CAT_TITLE[n][lang])}</h3>'
            f'<div class="cat-plan">{bed_plan(dd, du)}<dl class="cat-dl">'
            f'<div><dt>{e(DT["up"][lang])}</dt><dd>{e(b[0] if du else b[1])}</dd></div>'
            f'<div><dt>{e(DT["down"][lang])}</dt><dd>{e(b[0] if dd else b[1])}</dd></div>'
            f'<div><dt>{e(DT["type"][lang])}</dt><dd><a href="{p.rel}rum/{slug}">{name}</a></dd></div>'
            f'<div><dt>{e(DT["count"][lang])}</dt><dd>{count}</dd></div></dl></div>'
            f'{v}<p class="small muted">{e(UI["shot"][lang].format(n=n))}</p></article>')
    block = (f'<section class="section paper" id="rumstyper">\n  <div class="wrap stack-lg">\n'
             f'    <div class="section-head"><p class="eyebrow">{e(SEC["rum_eyebrow"][lang])}</p><h2>{e(SEC["rum_h2"][lang])}</h2>'
             f'<p class="lede">{e(SEC["rum_lede"][lang])}</p></div>\n    <div class="cat-grid">{"".join(cards)}</div>\n  </div>\n</section>')
    p.insert_after(r'<section class="section">\s*<div class="wrap grid-2">.*?</section>', block)
    # Nästa sektion var också "paper"; gör den ljus så att banden växlar.
    p.sub(r'(<!--/pano:rum6-->.*?</section>\s*)<section class="section paper">', r'\1<section class="section">')
    p.save()


def do_room(lang, slug):
    p = Page(lang, f"rum/{slug}.html")
    if done(p): return
    n = TYPE_ROOM[slug]
    ids = list(ROOMS[n][0])
    m = re.search(r'<div class="media-slot" style="aspect-ratio:16/8">.*?<strong>(.*?)</strong>.*?</div></div>', p.s, re.S)
    head = m.group(1)
    v = p.viewer(f"rum{n}", ids)
    p.s = p.s[:m.start()] + (f'<h2 style="font-size:var(--step-2)">{head}</h2>{v}'
                             f'<p class="small muted">{e(UI["shot"][lang].format(n=n))} <a href="{p.rel}rum/#rumstyper">{e(SEC["compare"][lang])}</a></p>') + p.s[m.end():]
    p.save()


FEST_H = {}


def do_fest(lang):
    p = Page(lang, "fest-och-event/index.html")
    if done(p): return
    m = re.search(r'<div class="media-slot">.*?<strong>(.*?)</strong>.*?</div></div>', p.s, re.S)
    FEST_H[lang] = m.group(1)
    v = p.viewer("fest", ["22", "23", "24", "25", "26"])
    p.s = p.s[:m.start()] + f'<div class="stack">{v}<p class="small">{e(SEC["fest_cap"][lang])}</p></div>' + p.s[m.end():]
    p.save()


def do_brollop(lang):
    p = Page(lang, "fest-och-event/brollop.html")
    if done(p): return
    v = p.viewer("brollop", ["22", "23", "24", "25", "26"])
    block = (f'<section class="section band">\n  <div class="wrap split">\n    <div class="stack-lg"><p class="eyebrow">{e(SEC["venue"][lang])}</p>'
             f'<h2>{FEST_H[lang]}</h2><p class="lede">{e(SEC["brollop_lede"][lang])}</p></div>\n    {v}\n  </div>\n</section>\n')
    i = p.s.rfind('<section class="section">', 0, p.s.find("<form"))
    p.s = p.s[:i] + block + p.s[i:]
    p.save()


def do_foretag(lang):
    p = Page(lang, "foretag/index.html")
    if done(p): return
    v = p.viewer("foretag", ["06", "08", "07"])
    block = (f'<section class="section paper">\n  <div class="wrap split">\n    {v}\n    <div class="stack-lg"><p class="eyebrow">{e(SEC["rooms"][lang])}</p>'
             f'<h2>{e(SEC["team_h2"][lang])}</h2><p class="lede">{e(SEC["team_lede"][lang])}</p>'
             f'<a class="textlink" href="{p.rel}rum/#rumstyper">{e(SEC["compare"][lang])}</a></div>\n  </div>\n</section>')
    p.insert_after(r'<section class="section">\s*<div class="wrap">\s*<div class="section-head">.*?</section>', block)
    p.save()


def do_langtid(lang):
    p = Page(lang, "foretag/langtidsboende.html")
    if done(p): return
    v = p.viewer("kok", ["29", "28", "27"])
    block = (f'<section class="section paper">\n  <div class="wrap split">\n    <div class="stack-lg"><p class="eyebrow">{e(SEC["kitchen"][lang])}</p>'
             f'<h2>{e(SEC["kitchen_h2"][lang])}</h2><p class="lede">{e(SEC["kitchen_lede"][lang])}</p></div>\n    {v}\n  </div>\n</section>')
    p.insert_after(r'<section class="section">\s*<div class="wrap split">.*?</section>', block)
    p.save()


def do_minigolf(lang):
    p = Page(lang, "minigolf/index.html")
    if done(p): return
    v = p.viewer("minigolf", ["04", "02", "03", "05"], chips=["04", "03"])
    block = (f'<section class="section paper">\n  <div class="wrap split">\n    {v}\n    <div class="stack-lg"><p class="eyebrow">{e(SEC["course"][lang])}</p>'
             f'<h2>{e(SEC["golf_h2"][lang])}</h2><p class="lede">{e(SEC["golf_lede"][lang])}</p></div>\n  </div>\n</section>')
    p.insert_after(r'<section class="section">\s*<div class="wrap split".*?</section>', block)
    p.save()


def do_upptack(lang):
    p = Page(lang, "upptack/index.html")
    if "fran-luften-01" in p.s: return
    block = (f'<section class="section band">\n  <div class="wrap split">\n    <figure class="ph photo wide">{picture(p.rel, "fran-luften-01", DRONE["01"][lang], w=1600, h=1200)}</figure>\n'
             f'    <div class="stack-lg"><p class="eyebrow">{e(SEC["above"][lang])}</p><h2>{e(SEC["above_h2"][lang])}</h2>'
             f'<p class="lede">{e(SEC["above_lede"][lang])}</p><a class="textlink" href="{p.rel}galleri/">{e(SEC["more_photos"][lang])}</a></div>\n  </div>\n</section>\n')
    i = p.s.rfind("</main>")
    p.s = p.s[:i] + block + p.s[i:]
    open(p.file, "w", encoding="utf-8").write(p.s)


def do_galleri(lang):
    p = Page(lang, "galleri/index.html")
    if "fran-luften-" in p.s: return
    prefix = re.search(r'<button type="button" aria-label="([^"]*?): ', p.s).group(1)
    items = "".join(
        f'<div class="{"g-wide" if k in ("01", "13") else ""}" data-cat="garden" data-title="{e(DRONE[k][lang])}"><button type="button" aria-label="{prefix}: {e(DRONE[k][lang])}">'
        f'<figure class="ph photo ">{picture(p.rel, "fran-luften-" + k, DRONE[k][lang], w=1600, h=1200)}</figure></button></div>'
        for k in ("01", "13", "02", "03", "14", "22", "09"))
    p.sub(r'(</div>)(\s*</div>\s*</section>\s*<div class="lightbox")', lambda m: m.group(1) + items + m.group(2))
    open(p.file, "w", encoding="utf-8").write(p.s)


def do_rundtur(lang):
    p = Page(lang, "rundtur/index.html")
    if done(p): return
    allsc = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17",
             "22", "23", "24", "25", "26", "27", "28", "29", "18"]
    v = p.viewer("hela", allsc, chips=["01", "03", "04", "05", "06", "09", "12", "15", "22", "26", "29"])
    p.sub(r'<div class="media-slot"><figure.*?</figure><div class="inner">.*?</div></div>', lambda m: v)
    p.sub(r'(<div class="stack"><p class="eyebrow">[^<]*</p><h1>)[^<]*(</h1>)', lambda m: m.group(1) + e(SEC["tour_h1"][lang]) + m.group(2))
    # Drönarfilmen saknade källa på den här sidan.
    p.s = re.sub(r'(<video controls muted playsinline preload="none" poster="[^"]*">)(?!<source)', lambda m: m.group(1) + f'<source src="{p.rel}assets/video/flyover.mp4" type="video/mp4">', p.s)
    figs = "".join(f'<figure class="stack">{picture(p.rel, "fran-luften-" + k, DRONE[k][lang], sizes="(min-width: 900px) 25vw, 50vw", w=1600, h=1200)}'
                   f'<figcaption class="small muted">{e(DRONE[k][lang])}</figcaption></figure>' for k in ("01", "13", "03", "22"))
    block = (f'<section class="section">\n  <div class="wrap stack-lg">\n    <div class="section-head"><p class="eyebrow">{e(SEC["above"][lang])}</p>'
             f'<h2>{e(SEC["above_h2"][lang])}</h2></div>\n    <div class="grid-4">{figs}</div>\n    <a class="textlink" href="{p.rel}galleri/">{e(SEC["more_photos"][lang])}</a>\n  </div>\n</section>\n')
    i = p.s.rfind("</main>")
    p.s = p.s[:i] + block + p.s[i:]
    p.save()


def main():
    for lang in LANGS:
        do_home(lang)
        do_rum_index(lang)
        for slug in TYPE_ROOM:
            do_room(lang, slug)
        do_fest(lang)
        do_brollop(lang)
        do_foretag(lang)
        do_langtid(lang)
        do_minigolf(lang)
        do_upptack(lang)
        do_galleri(lang)
        do_rundtur(lang)
    print("Klart.")


if __name__ == "__main__":
    main()
