#!/usr/bin/env python3
"""Byter 360°-visningarna från Pannellum till 3DVista-rundturen i /360/, på alla tio språk.

Körs från repots rot: python3 verktyg/tredvista.py (kan köras flera gånger).
Rundturen byggs i 3DVista på Daniels Mac (projekt GEG foton/arbetsyta/GEG-rundtur-v5.vtp),
publiceras som "Web / Mobile" till en lokal mapp och kopieras hit som /360/.
Skyltarna, namnen och startvyerna läggs in i projektfilen med geg-hotel/3dvista/build_vtp.py och build_labels.py.
360°-materialet är bara för webbplatsen, aldrig för Google.
"""
import glob
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rundturer_text import LANGS, UI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = lambda s: html.escape(s, quote=True)
OLD_HINT = {
    "sv": "Dra i bilden eller använd piltangenterna. Pilarna i bilden tar dig vidare.",
    "en": "Drag the image or use the arrow keys. The arrows in the image take you further.",
    "da": "Træk i billedet eller brug piletasterne. Pilene i billedet fører dig videre.",
    "nb": "Dra i bildet eller bruk piltastene. Pilene i bildet tar deg videre.",
    "fi": "Vedä kuvaa tai käytä nuolinäppäimiä. Kuvan nuolet vievät eteenpäin.",
    "de": "Zieh am Bild oder nutze die Pfeiltasten. Die Pfeile im Bild führen weiter.",
    "nl": "Sleep aan het beeld of gebruik de pijltjestoetsen. De pijlen in het beeld brengen je verder.",
    "fr": "Faites glisser l'image ou utilisez les flèches du clavier. Les flèches dans l'image vous font avancer.",
    "es": "Arrastra la imagen o usa las flechas del teclado. Las flechas de la imagen te llevan más allá.",
    "it": "Trascina l'immagine o usa i tasti freccia. Le frecce nell'immagine ti portano avanti.",
}
RING_HINT = {
    "sv": "Dra i bilden för att se dig omkring. Klicka på ringarna i golvet för att gå vidare.",
    "en": "Drag the image to look around. Click the rings on the floor to move on.",
    "da": "Træk i billedet for at se dig omkring. Klik på ringene på gulvet for at gå videre.",
    "nb": "Dra i bildet for å se deg rundt. Klikk på ringene i gulvet for å gå videre.",
    "fi": "Vedä kuvaa katsoaksesi ympärillesi. Siirry eteenpäin napsauttamalla lattialla olevia renkaita.",
    "de": "Zieh am Bild, um dich umzusehen. Klick auf die Ringe am Boden, um weiterzugehen.",
    "nl": "Sleep aan het beeld om rond te kijken. Klik op de ringen op de vloer om verder te gaan.",
    "fr": "Faites glisser l'image pour regarder autour de vous. Cliquez sur les anneaux au sol pour avancer.",
    "es": "Arrastra la imagen para mirar alrededor. Haz clic en los anillos del suelo para avanzar.",
    "it": "Trascina l'immagine per guardarti intorno. Clicca sugli anelli sul pavimento per andare avanti.",
}
FULL_ICON = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" '
             'fill="none" stroke="currentColor" stroke-width="2"/></svg>')


def full_button(lang):
    return f'<button type="button" class="pano-full" hidden aria-label="{e(UI["full"][lang])}">{FULL_ICON}</button>'


def page_lang(path):
    rel = os.path.relpath(path, ROOT).split(os.sep)
    return rel[0] if rel[0] in LANGS and rel[0] != "sv" else "sv"


def patch_tour():
    """Små ändringar i 3DVistas index.htm efter varje ny publicering."""
    f = os.path.join(ROOT, "360", "index.htm")
    s = open(f, encoding="utf-8").read()
    t = s
    if 'name="robots"' not in t:
        t = t.replace("<title>", '<meta name="robots" content="noindex">\n    <title>', 1)
    t = re.sub(r'<meta name="description" content="[^"]*"/>', '<meta name="description" content="360° rundtur på Gammeleksgården i Härslöv"/>', t)
    t = t.replace("Loading virtual tour. Please wait...", "360°")
    if t != s:
        open(f, "w", encoding="utf-8").write(t)


def main():
    patch_tour()
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if "/360/" in f:
            continue
        s = open(f, encoding="utf-8").read()
        if 'class="pano"' not in s:
            continue
        lang = page_lang(f)
        t = re.sub(r'data-base="((?:\.\./)*)assets/pano/"', r'data-tour="\g<1>360/"', s)
        t = t.replace('<div class="pano-view"></div></div>', '<div class="pano-view"></div>' + full_button(lang) + '</div>')
        j = lambda x: json.dumps(x, ensure_ascii=False)[1:-1]
        for old in (OLD_HINT[lang], RING_HINT[lang]):
            t = t.replace(e(old), e(UI["hint"][lang]))
            t = t.replace('"hint":"' + j(old) + '"', '"hint":"' + j(UI["hint"][lang]) + '"')
        if t != s:
            open(f, "w", encoding="utf-8").write(t)
            n += 1
    print(n, "sidor uppdaterade")


if __name__ == "__main__":
    main()
