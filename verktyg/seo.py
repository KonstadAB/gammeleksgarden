#!/usr/bin/env python3
"""SEO-verktyg för gammeleksgården.se (endast standardbiblioteket).

  python3 verktyg/seo.py kontroll             Kontrollerar alla sidor (före lansering: noindex krävs)
  python3 verktyg/seo.py kontroll --lanserad  Samma kontroll efter lansering (noindex får bara finnas på undantagen)
  python3 verktyg/seo.py sitemap              Skriver en ny sitemap till stdout

Domänen skrivs i punycode (xn--gammeleksgrden-uib.se) i alla maskinläsbara adresser,
se HANDOFF.md för motiveringen.
"""
import collections
import datetime
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://xn--gammeleksgrden-uib.se/'
LANGS = ['sv', 'en', 'da', 'nb', 'fi', 'de', 'nl', 'fr', 'es', 'it']
# Sidor som aldrig ska indexeras eller stå i sitemap
NOINDEX_ALLTID = {'404.html', 'exempel/sjalvincheckning/index.html'}
# Indexerbara men utelämnade ur sitemap (tunna sidor). Alla språkversioner.
EJ_I_SITEMAP = ('bokningsvillkor/', 'integritet/')


class Sida(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.imgs = []
        self.title = ''
        self._title = False
        self.meta = {}
        self.links = []
        self.ld = []
        self._ld = False
        self._buf = ''
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'img':
            self.imgs.append(a)
        elif tag == 'title':
            self._title = True
        elif tag == 'meta' and a.get('name'):
            self.meta[a['name']] = a.get('content') or ''
        elif tag == 'link':
            self.links.append(a)
        elif tag == 'script' and a.get('type') == 'application/ld+json':
            self._ld, self._buf = True, ''

    def handle_endtag(self, tag):
        if tag == 'title':
            self._title = False
        elif tag == 'script' and self._ld:
            self._ld = False
            self.ld.append(self._buf)

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._ld:
            self._buf += data

    @property
    def canonical(self):
        c = [l['href'] for l in self.links if l.get('rel') == 'canonical']
        return c[0] if len(c) == 1 else None

    @property
    def hreflang(self):
        return {l['hreflang']: l['href'] for l in self.links
                if l.get('rel') == 'alternate' and l.get('hreflang')}


def sidor():
    res = {}
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                p = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/')
                s = Sida()
                with open(os.path.join(ROOT, p), encoding='utf-8') as fh:
                    s.feed(fh.read())
                res[p] = s
    return dict(sorted(res.items()))


def url_till_fil(u):
    rest = u[len(BASE):]
    return rest + 'index.html' if rest == '' or rest.endswith('/') else rest + '.html'


def sprak(p):
    forsta = p.split('/')[0]
    return forsta if forsta in LANGS[1:] else 'sv'


def kontroll(lanserad=False):
    allt = sidor()
    fel = collections.defaultdict(list)
    titlar = collections.defaultdict(list)
    beskr = collections.defaultdict(list)
    for p, s in allt.items():
        robots = s.meta.get('robots', '')
        if p in NOINDEX_ALLTID:
            if 'noindex' not in robots:
                fel['noindex saknas (ska alltid ha noindex)'].append(p)
            continue
        if lanserad and 'noindex' in robots:
            fel['noindex kvar efter lansering'].append(p)
        if not lanserad and 'noindex' not in robots:
            fel['NOINDEX SAKNAS – sajten är inte lanserad'].append(p)
        titlar[s.title].append(p)
        d = s.meta.get('description', '')
        beskr[d].append(p)
        if not 120 <= len(d) <= 160:
            fel['description inte 120–160 tecken'].append('%s (%d)' % (p, len(d)))
        if s.h1 != 1:
            fel['inte exakt en h1'].append('%s (%d)' % (p, s.h1))
        c = s.canonical
        if not c or not c.startswith(BASE):
            fel['canonical saknas eller fel domän'].append(p)
        elif url_till_fil(c) != p:
            fel['canonical pekar inte på sidan själv'].append('%s -> %s' % (p, c))
        hl = s.hreflang
        if set(hl) != set(LANGS) | {'x-default'}:
            fel['hreflang ofullständig'].append(p)
        elif hl.get(sprak(p)) != c:
            fel['hreflang för eget språk = canonical'].append(p)
        for lang, u in hl.items():
            f = url_till_fil(u)
            if f not in allt:
                fel['hreflang till sida som saknas'].append('%s -> %s' % (p, u))
            elif allt[f].hreflang != hl:
                fel['hreflang inte ömsesidig'].append('%s <-> %s' % (p, f))
            elif lang != 'x-default' and allt[f].lang != lang:
                fel['hreflang-språk matchar inte lang'].append(f)
        for img in s.imgs:
            if 'alt' not in img:
                fel['bild utan alt'].append('%s %s' % (p, img.get('src')))
        typer = []
        for blob in s.ld:
            try:
                j = json.loads(blob)
            except ValueError as e:
                fel['ogiltig JSON-LD'].append('%s %s' % (p, e))
                continue
            t = j.get('@type')
            t = t if isinstance(t, list) else [t]
            typer += t
            if '&amp;' in blob:
                fel['HTML-entitet i JSON-LD'].append(p)
            if {'Hotel', 'WebSite'} & set(t):
                continue
            for u in re.findall(r'"(%s[^"#]*)"' % re.escape(BASE), blob):
                if '/assets/' in u:
                    continue
                if url_till_fil(u) not in allt:
                    fel['JSON-LD-adress till sida som saknas'].append('%s %s' % (p, u))
                elif sprak(url_till_fil(u)) != sprak(p):
                    fel['JSON-LD-adress på annat språk'].append('%s %s' % (p, u))
        ar_start = p == 'index.html' or re.fullmatch(r'[a-z]{2}/index\.html', p)
        if not ar_start and 'BreadcrumbList' not in typer:
            fel['BreadcrumbList saknas'].append(p)
    for t, ps in titlar.items():
        if len(ps) > 1:
            fel['dubblerad title'].append('%s: %s' % (t, ', '.join(ps)))
    for d, ps in beskr.items():
        if len(ps) > 1:
            fel['dubblerad description'].append(', '.join(ps))
    print('%d sidor kontrollerade (%s)' % (len(allt), 'efter lansering' if lanserad else 'före lansering'))
    for k, v in fel.items():
        print('\n%s: %d' % (k, len(v)))
        for x in v[:20]:
            print('  ' + x)
    if not fel:
        print('Inga fel.')
    return 1 if fel else 0


def sitemap():
    allt = sidor()
    idag = datetime.date.today().isoformat()
    rader = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    # Svenska först, sedan språken i samma ordning som hreflang
    ordning = sorted((p for p in allt if p not in NOINDEX_ALLTID),
                     key=lambda p: (p.split('/', 1)[1] if sprak(p) != 'sv' else p,
                                    LANGS.index(sprak(p))))
    for p in ordning:
        rel = p if sprak(p) == 'sv' else p.split('/', 1)[1]
        if rel.startswith(EJ_I_SITEMAP):
            continue
        s = allt[p]
        alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, s.hreflang[l])
                       for l in LANGS + ['x-default'])
        rader.append('  <url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (s.canonical, idag, alts))
    rader.append('</urlset>')
    print('\n'.join(rader))
    return 0


if __name__ == '__main__':
    kommando = sys.argv[1] if len(sys.argv) > 1 else ''
    if kommando == 'kontroll':
        sys.exit(kontroll('--lanserad' in sys.argv))
    if kommando == 'sitemap':
        sys.exit(sitemap())
    print(__doc__)
    sys.exit(2)
