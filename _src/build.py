#!/usr/bin/env python3
"""
Generatore della sezione Insights di pen-pushers.com.

Il repository corrisponde alla cartella /insights/ del sito (Hostinger la
aggiorna da solo a ogni push sul branch main).

Uso:  python3 _src/build.py
Legge  _src/articles/*.json  e rigenera:
  index.html, <slug>.html, feed.json, sitemap.xml, insights.css,
  img/covers/<slug>.jpg (1200x630), img/social/<slug>.jpg (1080x1350), img/stories/<slug>.jpg (1080x1920)
"""
import os, json, glob, html, math, re, shutil
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_src')
SITE = 'https://pen-pushers.com'
BASE = SITE + '/insights'
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']

BG = (3, 16, 8); CARD = (6, 23, 16); GOLD = (184, 144, 63); GOLD_HI = (226, 196, 138); GOLD_LO = (112, 80, 34)
WHITE = (255, 255, 255); MUTED = (168, 164, 154)

REQUIRED = ['slug', 'date', 'cat', 'title', 'seo_title', 'desc', 'lead', 'mins', 'motif', 'ig_hook', 'ig_caption', 'cta_title', 'cta_text', 'body_html']
MOTIFS = ['sphere', 'network', 'growth', 'nib', 'grid', 'funnel']


def font(name, size):
    files = {'black': 'archivo-latin-900-normal.woff', 'bold': 'archivo-latin-800-normal.woff',
             'reg': 'archivo-latin-500-normal.woff', 'mono': 'ibm-plex-mono-latin-500-normal.woff'}
    return ImageFont.truetype(os.path.join(SRC, 'fonts', files[name]), size)


def date_it(d):
    y, m, dd = map(int, d.split('-'))
    return f'{dd} {MESI[m - 1]} {y}'


# ------------------------------------------------------------------ articoli
def load_articles():
    arts = []
    for f in sorted(glob.glob(os.path.join(SRC, 'articles', '*.json'))):
        a = json.load(open(f, encoding='utf-8'))
        missing = [k for k in REQUIRED if k not in a or a[k] in ('', None)]
        if missing:
            raise SystemExit(f'ERRORE {os.path.basename(f)}: mancano {missing}')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', a['slug']):
            raise SystemExit(f'ERRORE {os.path.basename(f)}: slug non valido "{a["slug"]}"')
        if a['motif'] not in MOTIFS:
            raise SystemExit(f'ERRORE {os.path.basename(f)}: motif deve essere uno di {MOTIFS}')
        if '[' in a['title'] or '[' in a['desc']:
            raise SystemExit(f'ERRORE {os.path.basename(f)}: segnaposto tra [ ] ancora presenti')
        a.setdefault('time', '09:00')
        arts.append(a)
    slugs = [a['slug'] for a in arts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        raise SystemExit(f'ERRORE: slug duplicati {dup}')
    arts.sort(key=lambda a: (a['date'], a['time']), reverse=True)
    return arts


# ------------------------------------------------------------------ immagini
def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, name, width, max_lines, start, minsize):
    size = start
    while size >= minsize:
        f = font(name, size)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
        size -= 4
    f = font(name, minsize)
    return f, wrap(draw, text, f, width)[:max_lines]


def glow(im, cx, cy, r, strength=40):
    g = Image.new('L', im.size, 0)
    ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=strength)
    g = g.filter(ImageFilter.GaussianBlur(r / 2))
    layer = Image.new('RGB', im.size, GOLD_LO)
    im.paste(layer, (0, 0), g)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_motif(im, kind, cx, cy, S, seed):
    d = ImageDraw.Draw(im, 'RGBA')
    if kind == 'sphere':
        N, ga = 420, math.pi * (3 - math.sqrt(5)); a = seed % 628 / 100; tilt = .32; pts = []
        for i in range(N):
            y = 1 - i / (N - 1) * 2; r = math.sqrt(1 - y * y); th = ga * i
            x, z = math.cos(th) * r, math.sin(th) * r
            x2 = x * math.cos(a) + z * math.sin(a); z2 = -x * math.sin(a) + z * math.cos(a)
            pts.append((y * math.sin(tilt) + z2 * math.cos(tilt), x2, y * math.cos(tilt) - z2 * math.sin(tilt)))
        pts.sort()
        R = S * .42
        d.ellipse([cx - S * .58, cy - S * .16, cx + S * .58, cy + S * .16], outline=GOLD + (110,), width=max(2, S // 260))
        for z, x, y in pts:
            t = (z + 1) / 2; rr = (1 + 2.6 * t) * S / 330
            c = lerp(GOLD_LO, GOLD_HI, .2 + .8 * t)
            d.ellipse([cx + x * R - rr, cy + y * R - rr, cx + x * R + rr, cy + y * R + rr], fill=c + (int(60 + 195 * t),))
    elif kind == 'network':
        nodes = [(.5, .5), (.18, .24), (.8, .18), (.88, .6), (.62, .88), (.2, .8), (.06, .5), (.44, .1), (.38, .68)]
        edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 7), (7, 2), (2, 3), (3, 4), (4, 8), (8, 5), (5, 6), (6, 1), (8, 0)]
        P = [(cx - S / 2 + x * S, cy - S / 2 + y * S) for x, y in nodes]
        for a, b in edges:
            d.line([P[a], P[b]], fill=GOLD + (120,), width=max(2, S // 220))
        for i, (a, b) in enumerate(edges):
            u = ((seed * 7 + i * 37) % 100) / 100
            x, y = P[a][0] + (P[b][0] - P[a][0]) * u, P[a][1] + (P[b][1] - P[a][1]) * u; rr = S / 110
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD_HI + (255,))
        for i, (x, y) in enumerate(P):
            rr = S / (24 if i == 0 else 40)
            d.ellipse([x - rr * 1.6, y - rr * 1.6, x + rr * 1.6, y + rr * 1.6], outline=GOLD + (140,), width=max(2, S // 300))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD_HI if i == 0 else GOLD)
    elif kind == 'growth':
        x0, y0 = cx - S / 2, cy + S / 2
        for i in range(6):
            h = S * (.16 + i * .13); bx = x0 + S * (.04 + i * .16)
            d.rounded_rectangle([bx, y0 - h, bx + S * .1, y0], radius=S / 80, fill=GOLD_LO + (150,))
        pts = [(.0, .82), (.18, .66), (.34, .72), (.5, .46), (.66, .52), (.82, .24), (.97, .06)]
        P = [(x0 + x * S, cy - S / 2 + y * S) for x, y in pts]
        d.line(P, fill=GOLD + (255,), width=max(4, S // 70), joint='curve')
        ex, ey = P[-1]; q = S / 26
        d.polygon([(ex + q, ey - q), (ex - q * 1.1, ey - q * .4), (ex + q * .4, ey + q * 1.1)], fill=GOLD_HI)
        for k in range(30):
            x = x0 + ((k * 0.618 + seed * .01) % 1) * S; y = cy - S / 2 + ((k * 0.382) % 1) * S; rr = S / 260
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD_HI + (160,))
    elif kind == 'nib':
        top, bot, hw = cy - S * .45, cy + S * .45, S * .23
        sh = [(cx, bot), (cx - hw * .25, bot - S * .2), (cx - hw, top + S * .36), (cx - hw * .9, top + S * .13), (cx - hw * .55, top),
              (cx + hw * .55, top), (cx + hw * .9, top + S * .13), (cx + hw, top + S * .36), (cx + hw * .25, bot - S * .2)]
        mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon(sh, fill=255)
        grad = Image.new('RGB', im.size)
        gd = ImageDraw.Draw(grad)
        for yy in range(int(top), int(bot) + 1):
            gd.line([(cx - hw - 2, yy), (cx + hw + 2, yy)], fill=lerp(GOLD_HI, GOLD_LO, (yy - top) / (bot - top)))
        im.paste(grad, (0, 0), mask)
        d = ImageDraw.Draw(im, 'RGBA')
        hy = top + S * .44; hr = S * .04
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=BG)
        d.line([(cx, hy), (cx, bot - 2)], fill=BG, width=max(3, S // 120))
        for k in (.2, .27):
            d.arc([cx - hw * .7, top + S * k, cx + hw * .7, top + S * (k + .18)], 200, 340, fill=GOLD_LO + (220,), width=max(2, S // 200))
    elif kind == 'grid':
        n = 7; step = S / n
        for i in range(n):
            for j in range(n):
                x, y = cx - S / 2 + (i + .5) * step, cy - S / 2 + (j + .5) * step
                dist = math.hypot(i - 3, j - 3) / 4.3
                rr = step * (.36 - .22 * dist)
                on = ((i * 3 + j * 5 + seed) % 7) < 3
                d.rounded_rectangle([x - rr, y - rr, x + rr, y + rr], radius=rr * .3,
                                    fill=(GOLD if on else GOLD_LO) + (int(255 - 150 * dist),))
    elif kind == 'funnel':
        for i in range(6):
            w = S * (1 - i * .14); y = cy - S * .45 + i * S * .17; h = S * .11
            d.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + h], radius=h / 2, fill=lerp(GOLD_LO, GOLD_HI, i / 5) + (230,))
        rr = S / 30
        d.ellipse([cx - rr, cy + S * .5, cx + rr, cy + S * .5 + 2 * rr], fill=GOLD_HI)


def photo_path(a):
    p = os.path.join(SRC, 'photos', a['slug'] + '.jpg')
    return p if a.get('photo') and os.path.exists(p) else None


def gold_photo(path, size, focus=0.5):
    """Foto ritagliata a 'size' e virata nei colori del brand: ombre verde scuro, luci oro."""
    from PIL import ImageOps, ImageEnhance
    im = Image.open(path).convert('RGB')
    W, H = size
    r = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * r)), max(H, round(im.height * r))), Image.LANCZOS)
    x = int((im.width - W) * 0.5); y = int((im.height - H) * focus)
    im = im.crop((x, y, x + W, y + H))
    g = ImageOps.autocontrast(im.convert('L'), cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.12)
    return ImageOps.colorize(g, black=(2, 12, 6), mid=(96, 76, 38), white=(238, 212, 156), midpoint=110)


def fade(im, box, direction, start_alpha=255, end_alpha=0):
    """Sfuma il colore di fondo sopra una zona della foto (per leggere il testo)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    grad = Image.new('L', (w, h))
    gd = ImageDraw.Draw(grad)
    n = w if direction in ('right', 'left') else h
    for i in range(n):
        t = i / max(1, n - 1)
        a = int(start_alpha + (end_alpha - start_alpha) * (t ** 1.4))
        if direction == 'right':
            gd.line([(i, 0), (i, h)], fill=a)
        elif direction == 'down':
            gd.line([(0, i), (w, i)], fill=a)
        elif direction == 'up':
            gd.line([(0, h - 1 - i), (w, h - 1 - i)], fill=a)
    im.paste(Image.new('RGB', (w, h), BG), (x0, y0), grad)


def brand(d, x, y, scale=1.0):
    d.text((x, y), 'PEN-PUSHERS', font=font('black', int(30 * scale)), fill=GOLD)
    d.text((x + 2, y + int(34 * scale)), 'P U B L I S H I N G', font=font('bold', int(13 * scale)), fill=WHITE)


def make_cover(a, path, seed):
    W, H = 1200, 630
    pp = photo_path(a)
    if pp:
        im = Image.new('RGB', (W, H), BG)
        ph = gold_photo(pp, (700, H), a['photo'].get('focus', 0.5))
        im.paste(ph, (W - 700, 0))
        fade(im, (W - 700, 0, W - 700 + 380, H), 'right')
        fade(im, (0, H - 140, W, H), 'up', 200, 0)
    else:
        im = Image.new('RGB', (W, H), BG)
        glow(im, 930, 315, 330, 60)
        draw_motif(im, a['motif'], 930, 315, 400, seed)
    d = ImageDraw.Draw(im)
    brand(d, 64, 56)
    d.text((64, 170), a['cat'].upper(), font=font('mono', 20), fill=GOLD)
    f, lines = fit_text(d, a['title'], 'bold', 640, 4, 56, 34)
    y = 210
    for ln in lines:
        d.text((64, y), ln, font=f, fill=WHITE); y += int(f.size * 1.08)
    d.line([(64, 556), (164, 556)], fill=GOLD, width=3)
    d.text((64, 572), 'pen-pushers.com/insights', font=font('mono', 18), fill=MUTED)
    im.save(path, quality=86, optimize=True, progressive=True)


def make_social(a, path, seed):
    W, H = 1080, 1350
    im = Image.new('RGB', (W, H), BG)
    pp = photo_path(a)
    if pp:
        ph = gold_photo(pp, (W, 820), a['photo'].get('focus', 0.5))
        im.paste(ph, (0, 0))
        fade(im, (0, 0, W, 220), 'down', 210, 0)
        fade(im, (0, 420, W, 821), 'up', 255, 0)
    else:
        glow(im, 780, 420, 380, 70)
        draw_motif(im, a['motif'], 760, 400, 460, seed)
    d = ImageDraw.Draw(im)
    brand(d, 72, 72, 1.15)
    d.text((72, 720), a['cat'].upper(), font=font('mono', 26), fill=GOLD)
    f, lines = fit_text(d, a['ig_hook'], 'black', 936, 4, 92, 56)
    y = 770
    for ln in lines:
        d.text((72, y), ln, font=f, fill=WHITE); y += int(f.size * 1.04)
    d.rounded_rectangle([72, 1200, 72 + 440, 1270], radius=35, fill=GOLD)
    d.text((104, 1218), "Leggi l'articolo · link in bio", font=font('bold', 26), fill=BG)
    d.text((W - 72 - d.textlength('pen-pushers.com', font=font('mono', 24)), 1222), 'pen-pushers.com', font=font('mono', 24), fill=MUTED)
    im.save(path, quality=88, optimize=True, progressive=True)


def make_story(a, path, seed):
    """Storia Instagram 1080x1920: testi dentro la zona sicura (lontani da 250 px in alto e in basso)."""
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), BG)
    pp = photo_path(a)
    if pp:
        ph = gold_photo(pp, (W, 1180), a['photo'].get('focus', 0.5))
        im.paste(ph, (0, 0))
        fade(im, (0, 0, W, 420), 'down', 220, 0)
        fade(im, (0, 680, W, 1181), 'up', 255, 0)
    else:
        glow(im, 780, 700, 420, 70)
        draw_motif(im, a['motif'], 760, 680, 520, seed)
    d = ImageDraw.Draw(im)
    brand(d, 72, 260, 1.15)
    d.text((72, 1080), a['cat'].upper(), font=font('mono', 28), fill=GOLD)
    f, lines = fit_text(d, a['ig_hook'], 'black', 936, 4, 96, 58)
    y = 1132
    for ln in lines:
        d.text((72, y), ln, font=f, fill=WHITE); y += int(f.size * 1.04)
    d.text((72, 1520), 'NUOVO ARTICOLO', font=font('mono', 24), fill=MUTED)
    d.rounded_rectangle([72, 1562, 72 + 470, 1636], radius=37, fill=GOLD)
    d.text((106, 1582), "Leggi l'articolo · link in bio", font=font('bold', 28), fill=BG)
    im.save(path, quality=88, optimize=True, progressive=True)


# ------------------------------------------------------------------ pagine
HEAD_COMMON = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400..900&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="/insights/insights.css?v={ver}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/feed+json" title="Insights Pen-Pushers Publishing" href="/insights/feed.json">
<meta name="theme-color" content="#031008">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Pen-Pushers Publishing">'''

ORG = {"@type": "Organization", "@id": SITE + "/#organization", "name": "Pen-Pushers Publishing", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/apple-touch-icon.png"}}


def header(current):
    cur = ' aria-current="page"' if current else ''
    return f'''<header class="top">
  <div class="wrap">
    <a href="/" class="logo">PEN-PUSHERS<span>PUBLISHING</span></a>
    <nav class="nav mono" aria-label="Principale">
      <a href="/#creazione">Servizi</a>
      <a href="/#sistemi">Sistemi</a>
      <a href="/#progetti">Progetti</a>
      <a href="/insights/"{cur}>Insights</a>
    </nav>
    <a href="/#contatti" class="btn">Parliamo del tuo progetto</a>
  </div>
</header>'''


FOOTER = '''<footer class="foot mono">
  <div class="wrap">
    <span class="brand">PEN-PUSHERS PUBLISHING</span>
    <span>P.IVA IT05504050484 · © {year}</span>
    <a href="/insights/" style="color:inherit;text-decoration:none">Insights</a>
  </div>
</footer>'''


def e(s):
    return html.escape(s, quote=True)


def card(a, featured=False):
    return f'''      <a class="card reveal{' featured' if featured else ''}" href="/insights/{a["slug"]}.html">
        <img class="thumb" src="/insights/img/covers/{a["slug"]}.jpg" alt="" width="1200" height="630" loading="lazy">
        <span class="meta mono"><span>{e(a["cat"])}</span><span>{a["mins"]} min</span></span>
        <h2>{e(a["title"])}</h2>
        <p>{e(a["desc"])}</p>
        <span class="go">Leggi l'articolo →</span>
      </a>'''


def article_page(a, related, ver):
    url = f'{BASE}/{a["slug"]}.html'; img = f'{BASE}/img/covers/{a["slug"]}.jpg'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": url + "#article", "headline": a['title'], "description": a['desc'], "image": img,
         "datePublished": a['date'], "dateModified": a.get('updated', a['date']), "inLanguage": "it-IT",
         "mainEntityOfPage": url, "articleSection": a['cat'],
         "author": {"@type": "Person", "name": "Manuel Ruisi", "url": SITE + "/"}, "publisher": ORG},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Insights", "item": BASE + "/"},
            {"@type": "ListItem", "position": 3, "name": a['title'], "item": url}]}]}
    if a.get('faq'):
        ld['@graph'].append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q['q'], "acceptedAnswer": {"@type": "Answer", "text": q['a']}} for q in a['faq']]})
    faq_html = ''
    if a.get('faq'):
        faq_html = '<h2>Domande frequenti</h2>\n' + '\n'.join(f'<h3>{e(q["q"])}</h3>\n<p>{e(q["a"])}</p>' for q in a['faq'])
    sources = ''
    if a.get('sources'):
        sources = '<div class="box"><span class="mono">Fonti</span><ul>' + ''.join(
            f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["title"])}</a></li>' for s in a['sources']) + '</ul></div>'
    credit = ''
    if a.get('photo') and a['photo'].get('author'):
        ph = a['photo']
        credit = (f'<p class="credit mono">Foto di <a href="{e(ph.get("page", ph["url"]))}" rel="noopener" target="_blank">{e(ph["author"])}</a>'
                  f' su {e(ph.get("source", "Unsplash"))}</p>')
    more = '\n'.join(card(o) for o in related)
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a["seo_title"])}</title>
<meta name="description" content="{e(a["desc"])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Manuel Ruisi">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(a["title"])}">
<meta property="og:description" content="{e(a["desc"])}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="article:published_time" content="{a["date"]}">
{HEAD_COMMON.format(ver=ver)}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{header(False)}
<main>
  <div class="narrow">
    <nav class="crumbs mono" aria-label="Percorso"><a href="/">Home</a> / <a href="/insights/">Insights</a></nav>
    <header class="art-head">
      <div class="cat mono rise">{e(a["cat"])}</div>
      <h1 class="rise d1">{e(a["title"])}</h1>
      <p class="lead rise d2">{e(a["lead"])}</p>
      <div class="byline mono"><span>Di Manuel Ruisi</span><span><time datetime="{a["date"]}">{date_it(a["date"])}</time></span><span>{a["mins"]} min di lettura</span></div>
    </header>
    <img class="art-cover rise d2" src="/insights/img/covers/{a["slug"]}.jpg" alt="{e(a["title"])}" width="1200" height="630">
    {credit}
    <article class="body">
{a["body_html"].strip()}
{faq_html}
{sources}
    </article>
    <aside class="cta reveal">
      <h2>{e(a["cta_title"])}</h2>
      <p>{e(a["cta_text"])}</p>
      <a href="/#contatti" class="btn">Parliamo del tuo progetto</a>
    </aside>
  </div>
  <section class="more wrap" aria-label="Altri articoli">
    <h2>Continua a leggere</h2>
    <div class="grid">
{more}
    </div>
  </section>
</main>
{FOOTER.format(year=a["date"][:4])}
</body>
</html>
'''


def index_page(arts, ver):
    url = BASE + '/'
    desc = 'Insights di Pen-Pushers Publishing: guide pratiche su siti web, SEO, lead generation B2B, automazioni e AI per far crescere le imprese.'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": "Insights · Pen-Pushers Publishing", "inLanguage": "it-IT",
         "description": desc, "publisher": ORG,
         "hasPart": [{"@type": "Article", "headline": a['title'], "url": f'{BASE}/{a["slug"]}.html', "datePublished": a['date']} for a in arts[:30]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Insights", "item": url}]}]}
    cats = []
    for a in arts:
        if a['cat'] not in cats:
            cats.append(a['cat'])
    chips = ' · '.join(e(c) for c in cats[:8])
    cards = '\n'.join(card(a, i == 0) for i, a in enumerate(arts))
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Insights · Guide su crescita digitale, SEO e lead generation B2B | Pen-Pushers Publishing</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="Insights · Pen-Pushers Publishing">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/og-image.jpg">
{HEAD_COMMON.format(ver=ver)}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{header(True)}
<main>
  <section class="hero">
    <div class="wrap">
      <div class="mono rise" style="color:var(--gold)">Insights · Pen-Pushers Publishing</div>
      <h1 class="rise d1">Idee per<br><em>crescere.</em></h1>
      <p class="rise d2">Guide pratiche su siti web, Google, lead generation B2B, automazioni e AI. Scritte per chi fa impresa, non per chi fa tecnologia.</p>
      <p class="mono rise d2" style="font-size:12px;color:var(--mut);margin-top:22px">{len(arts)} articoli · {chips}</p>
    </div>
  </section>
  <section class="wrap" aria-label="Articoli">
    <div class="grid">
{cards}
    </div>
  </section>
</main>
{FOOTER.format(year=date.today().year)}
</body>
</html>
'''


def related_for(a, arts):
    others = [o for o in arts if o['slug'] != a['slug']]
    same = [o for o in others if o['cat'] == a['cat']]
    rest = [o for o in others if o['cat'] != a['cat']]
    return (same + rest)[:3]


def main():
    arts = load_articles()
    ver = max(a['date'] for a in arts).replace('-', '') if arts else '1'
    os.makedirs(os.path.join(ROOT, 'img', 'covers'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'img', 'social'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'img', 'stories'), exist_ok=True)
    shutil.copy(os.path.join(SRC, 'insights.css'), os.path.join(ROOT, 'insights.css'))
    for i, a in enumerate(arts):
        seed = sum(map(ord, a['slug']))
        make_cover(a, os.path.join(ROOT, 'img', 'covers', a['slug'] + '.jpg'), seed)
        make_social(a, os.path.join(ROOT, 'img', 'social', a['slug'] + '.jpg'), seed)
        make_story(a, os.path.join(ROOT, 'img', 'stories', a['slug'] + '.jpg'), seed)
        with open(os.path.join(ROOT, a['slug'] + '.html'), 'w', encoding='utf-8') as fh:
            fh.write(article_page(a, related_for(a, arts), ver))
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(index_page(arts, ver))
    feed = {"version": "https://jsonfeed.org/version/1.1", "title": "Insights · Pen-Pushers Publishing",
            "home_page_url": BASE + '/', "feed_url": BASE + '/feed.json', "language": "it",
            "items": [{"id": f'{BASE}/{a["slug"]}.html', "url": f'{BASE}/{a["slug"]}.html', "title": a['title'],
                       "summary": a['desc'], "image": f'{BASE}/img/covers/{a["slug"]}.jpg', "date_published": a['date'],
                       "tags": [a['cat']], "_mins": a['mins']} for a in arts[:20]]}
    with open(os.path.join(ROOT, 'feed.json'), 'w', encoding='utf-8') as fh:
        json.dump(feed, fh, ensure_ascii=False, indent=1)
    urls = [(BASE + '/', arts[0]['date'] if arts else date.today().isoformat())] + \
           [(f'{BASE}/{a["slug"]}.html', a.get('updated', a['date'])) for a in arts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         '\n'.join(f'  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>' for u, d in urls) + '\n</urlset>\n'
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write(sm)
    print(f'OK: {len(arts)} articoli generati')


if __name__ == '__main__':
    main()
