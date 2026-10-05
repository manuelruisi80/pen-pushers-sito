#!/usr/bin/env python3
"""
Scarica le foto indicate negli articoli (campo "photo") in _src/photos/<slug>.jpg.
Gira su GitHub Actions, che può raggiungere Unsplash e Pexels.
Fonti ammesse: unsplash.com (solo foto gratuite, non Unsplash+) e pexels.com.
"""
import os, json, glob, io, sys, urllib.request
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'photos')
os.makedirs(OUT, exist_ok=True)
ALLOWED = ('https://unsplash.com/', 'https://images.unsplash.com/', 'https://images.pexels.com/', 'https://www.pexels.com/')

ok = err = 0
for f in sorted(glob.glob(os.path.join(SRC, 'articles', '*.json'))):
    a = json.load(open(f, encoding='utf-8'))
    p = a.get('photo')
    if not p or not p.get('url'):
        continue
    dest = os.path.join(OUT, a['slug'] + '.jpg')
    if os.path.exists(dest):
        continue
    url = p['url']
    if not url.startswith(ALLOWED):
        print(f'SALTATA {a["slug"]}: fonte non ammessa {url}'); err += 1; continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (PenPushers Insights builder)'})
        data = urllib.request.urlopen(req, timeout=60).read()
        im = Image.open(io.BytesIO(data)).convert('RGB')
        im.thumbnail((2000, 2000))
        im.save(dest, quality=88)
        print(f'OK {a["slug"]} {im.size}'); ok += 1
    except Exception as ex:
        print(f'ERRORE {a["slug"]}: {ex}'); err += 1
print(f'foto scaricate: {ok}, errori: {err}')
