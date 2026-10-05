#!/usr/bin/env python3
"""
Scarica le foto indicate negli articoli (campo "photo") in _src/photos/<slug>.jpg.
Gira su GitHub Actions, che può raggiungere Unsplash e Pexels.
Fonti ammesse: unsplash.com (solo foto gratuite, non Unsplash+) e pexels.com.
"""
import os, json, glob, io, re, sys, urllib.request, html as htmlmod
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'photos')
os.makedirs(OUT, exist_ok=True)
ALLOWED = ('https://unsplash.com/', 'https://images.unsplash.com/', 'https://images.pexels.com/', 'https://www.pexels.com/')

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36',
      'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)


def image_url(p):
    """Ricava l'indirizzo diretto dell'immagine: CDN diretto, oppure og:image della pagina della foto."""
    url = p['url']
    if url.startswith(('https://images.unsplash.com/', 'https://images.pexels.com/')):
        return url
    page = p.get('page') or url
    m = re.search(r'unsplash\.com/photos/(?:[^/?#]*-)?([A-Za-z0-9_-]{11})(?:[/?#]|$)', page)
    if m:
        page = 'https://unsplash.com/photos/' + m.group(1)
    html = get(page).read().decode('utf-8', 'ignore')
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', html) or \
        re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', html)
    if not m:
        raise RuntimeError('og:image non trovata in ' + page)
    img = htmlmod.unescape(m.group(1))
    if 'images.unsplash.com' in img:
        img = re.sub(r'([?&])(w|h|fit|crop|q|auto|fm)=[^&]*', r'\1', img).replace('&&', '&').rstrip('&?')
        img += ('&' if '?' in img else '?') + 'w=2000&q=85&fm=jpg'
    elif 'images.pexels.com' in img:
        img = img.split('?')[0] + '?auto=compress&cs=tinysrgb&w=2000'
    return img


ok = err = 0
LOG = []
def log(m):
    print(m); LOG.append(m)
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
        log(f'SALTATA {a["slug"]}: fonte non ammessa {url}'); err += 1; continue
    try:
        resp = get(image_url(p))
        log(f'  {a["slug"]}: {resp.status} {resp.geturl()[:120]} {resp.headers.get("content-type")}')
        data = resp.read()
        im = Image.open(io.BytesIO(data)).convert('RGB')
        im.thumbnail((2000, 2000))
        im.save(dest, quality=88)
        log(f'OK {a["slug"]} {im.size}'); ok += 1
    except Exception as ex:
        log(f'ERRORE {a["slug"]}: {ex}'); err += 1
log(f'foto scaricate: {ok}, errori: {err}')
open(os.path.join(OUT, 'registro.txt'), 'w').write('\n'.join(LOG) + '\n')
