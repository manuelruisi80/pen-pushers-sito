# Redazione Insights · Pen-Pushers Publishing

Questo repository È la cartella `/insights/` di pen-pushers.com.
Hostinger pubblica automaticamente il branch **main**. Le bozze vanno sempre sul branch **bozze**:
Manuel le approva facendo il merge di `bozze` in `main` su GitHub.

## Chi siamo (per scrivere con la voce giusta)
- **Pen-Pushers Publishing**, Firenze, fondata da **Manuel Ruisi** (founder, product builder, growth consultant, 20+ anni nel digitale).
- Headline: *Creazione di prodotti digitali. Costruzione di sistemi. Generando crescita.*
- Promessa: analizziamo dove un'azienda perde opportunità, costruiamo gli strumenti digitali necessari e colleghiamo visibilità, acquisizione commerciale e automazione in un unico percorso.
- Servizi (prezzi di riferimento, da citare solo se utile e sempre "a partire da"/"di riferimento"):
  - Sito web base 4 pagine — 600 € tasse incluse
  - SEO / Google Business Profile — 250 € tasse incluse
  - Brand identity "Startup Coordinated Image" — 700 € tasse incluse
  - **KRELIA** (krelia.it) — CRM e ricerca lead B2B: installazione 350 €, ricerca continua 399 €/mese
  - **Innovation** con **404brain.tech** — automazioni e AI su misura, su preventivo
- Settore prioritario: PMI B2B tecniche (Ho.Re.Ca. tecnico: cucine professionali, refrigerazione, HVAC, manutenzione; poi impiantisti, antincendio, movimento terra, laboratori odontotecnici).
- Pubblico: titolari e responsabili commerciali di PMI italiane (5–50 addetti), professionisti, startup.

## Regole che non si violano
1. **Utile prima di tutto.** Ogni articolo risponde a UNA domanda concreta che un cliente si fa. Niente articoli "riempitivo".
2. **Niente invenzioni.** Nessuna statistica, percentuale, studio, cliente o citazione inventati. Dati numerici o normativi solo se verificati con una ricerca web nel giorno stesso, e allora la fonte va in `sources`.
3. **Mai promettere** primi posti su Google, vendite garantite, lead illimitati o agevolazioni fiscali automatiche (Transizione 5.0 e incentivi: "da verificare con il commercialista").
4. **Mai nominare clienti reali** o dati di lead/aziende presenti in KRELIA.
5. **Mai parlare male dei concorrenti** né citarli per nome.
6. **Niente duplicati:** prima di scrivere leggi i titoli in `_src/articles/` e scegli un tema diverso (anche come intento di ricerca).
7. Italiano corretto, tono diretto e professionale, frasi brevi, "tu" al lettore. Niente gergo inutile: si spiega come a un imprenditore, non a un tecnico.

## Formato di un articolo
File: `_src/articles/AAAA-MM-GG-<slug>.json` con questi campi:
- `slug`: parole chiave in minuscolo separate da trattini (es. `seo-locale-ristoranti-firenze`), unico.
- `date`: `AAAA-MM-GG` · `time`: `09:00` (primo articolo) / `09:30` (secondo)
- `cat`: una tra *Lead generation B2B*, *Siti web & SEO*, *Brand identity*, *AI & automazioni*, *Settori · Ho.Re.Ca. tecnico*, *Settori · <altro settore>*, *Crescita & vendite*, *Guide pratiche*
- `title`: titolo per il lettore (max ~90 caratteri), con la parola chiave principale.
- `seo_title`: max 60 caratteri + ` | Pen-Pushers Publishing`
- `desc`: 140–155 caratteri, cosa impara chi legge.
- `lead`: 2–3 frasi di apertura sul problema del lettore.
- `mins`: minuti di lettura (≈ parole/200).
- `motif`: uno tra `sphere`, `network`, `growth`, `nib`, `grid`, `funnel` (varia rispetto agli ultimi articoli).
- `ig_hook`: frase breve e forte per l'immagine Instagram (max ~60 caratteri).
- `ig_caption`: testo del post Instagram (gancio, 3–6 punti, invito "Articolo completo su pen-pushers.com/insights (link in bio)", 6–10 hashtag italiani pertinenti + #PenPushersPublishing). Max 2000 caratteri.
- `cta_title`, `cta_text`: invito finale collegato al servizio giusto.
- `body_html`: corpo in HTML semplice: `<h2>`, `<h3>`, `<p>`, `<ul>/<ol>/<li>`, `<strong>`, `<blockquote>`, `<div class="box"><span class="mono">Titolo</span>…</div>`. 900–1400 parole. Niente `<h1>`, niente stili inline, niente immagini.
- `photo` (obbligatoria): foto di riferimento da Unsplash o Pexels, virata automaticamente in oro e verde.
  `{"url": "https://images.unsplash.com/photo-XXXXXXXXXXXXX-xxxxxxxxxxxx?w=2000&q=85&fm=jpg", "author": "Nome Fotografo", "source": "Unsplash", "page": "https://unsplash.com/photos/...", "focus": 0.5}`
  - Solo foto **gratuite** (Unsplash License o Pexels License). MAI le foto "Unsplash+" (premium, firmate spesso Getty Images).
  - Soggetto coerente col tema e realistico (persone al lavoro, uffici, cucine professionali, impianti, cantieri…). Niente loghi, marchi o persone riconoscibili in pose imbarazzanti.
  - Non riusare una foto già usata da un altro articolo.
  - Come trovarla: WebSearch con `allowed_domains: ["unsplash.com"]` (o pexels.com), poi WebFetch della pagina della foto chiedendo: licenza (gratuita o Unsplash+), nome del fotografo e URL esatto del meta tag og:image. Da quell'URL tieni solo la parte `https://images.unsplash.com/photo-...` (prima del `?`) e aggiungi `?w=2000&q=85&fm=jpg`. Per Pexels: `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=2000`.
  - `focus` (0–1) sposta il ritaglio verticale: 0.3 tiene la parte alta, 0.7 la parte bassa.
  - La foto la scarica GitHub Actions dopo il push (il nostro ambiente non raggiunge Unsplash): dopo il push aspetta il commit "Immagini aggiornate [automatico]" e controlla `_src/photos/registro.txt`.
- facoltativi: `faq` (lista di `{q, a}`, 3–4 domande vere), `sources` (lista di `{title, url}`).

## Struttura consigliata del corpo
1. Il problema (con un esempio concreto del settore)
2. Perché succede / errori comuni
3. Il metodo in passi numerati
4. Box "In sintesi" o checklist
5. Cosa aspettarsi in modo onesto
6. (FAQ)

## Procedura
1. `python3 _src/build.py` rigenera tutto (pagine, copertine, immagini Instagram, feed, sitemap). Deve stampare `OK`.
2. Commit sul branch `bozze`, push.
3. GitHub Actions scarica le foto e rigenera le immagini con la foto (commit "Immagini aggiornate [automatico]", 1–2 minuti). Fai `git pull` e controlla a occhio le immagini nuove in `img/covers/` e `img/social/`.
