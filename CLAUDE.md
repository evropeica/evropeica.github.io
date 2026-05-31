# evropeica

Reference website for the Evropeїca Ukrainian Latin orthography project.

## Stack
- Astro 5.x static site
- TypeScript for the transliteration engine
- No framework components — vanilla JS for the converter interactivity

## Structure
- `src/lib/transliterate.ts` — core Layer 1.0 transliteration engine
- `src/pages/` — Astro pages (spec, converter)
- `src/layouts/Base.astro` — shared layout with nav + footer

## Layers
- **1.0** — Pure 1:1 transliteration from Cyrillic (2019 pravopys)
- **1.x** — Extensions for dialects, Old Ukrainian (planned)
- **2.0** — Orthography rules for foreign-origin words (original pronunciation)
- **3.0** — TBD

## Content language
Bilingual: Latin script (primary) + Cyrillic (secondary/italic)

## Dev
```bash
npm install
npm run dev    # http://localhost:4321
npm run build  # static output to dist/
```
