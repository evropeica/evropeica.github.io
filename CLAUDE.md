# evropeica

Reference website + engine for the Evropéïća Ukrainian Latin orthography.

## The one rule
`docs/RULEBOOK.md` is normative. Engine, Python port, fixtures and page text must agree with it. If you change behaviour: rulebook → engine (TS + Python) → `tests/cases.json` → `npm test` → `py tools/evropeica.py --self-test --cross-check` → `py tools/check_site.py` → page text.

## Stack
- Astro 5.x static site, no framework components; vanilla TS in `<script>`.
- Engine: `src/lib/transliterate.ts` (v1.0). Python twin: `tools/evropeica.py`.
- Site spellchecker: `tools/check_site.py` (twins every Latin string with its Cyrillic and diffs against the engine; v2.0 words come from `data/v2-lexicon.json`).
- Keyboard: `keyboards/evropeica.kmn` → compile with `npx --yes @keymanapp/kmc build keyboards/evropeica.kmn`, copy `.kmx` to `public/keyboards/`.

## Layout
- `src/pages/index.astro`, `spec/index.astro`, `spec/v1.astro`, `spec/v2.astro`, `converter.astro`, `keyboard.astro`
- `src/layouts/Base.astro` — nav, footer, global CSS
- `docs/` — RULEBOOK, audits
- `tests/` — `cases.json` + `run.mjs`

## Writing site text (RULEBOOK §6)
- `/spec/v1/` is pure v1.0: no stress marks, no v2.0 words.
- Other pages: v2.0 vocabulary allowed (must be in the lexicon); stress marks used on index, spec/index, converter, keyboard; `/spec/v2/` prose is unstressed except the v2.1 examples.
- Every Latin paragraph/heading/cell needs a Cyrillic twin so the checker can verify it.
- Brand is `Evropéïća` with Latin ï (U+00EF). Never Cyrillic ї inside Latin words, never ľ.

## Environment
- Windows. Python is `py` (3.14); bare `python` is a Store stub. Node 24.
- `npm run dev` → http://localhost:4321; `npm run build` → `dist/`.

## Related
- Lexykon — stress dictionary for the future v2.1 converter.
- Belarusian Łacinka and the Czech ÚJČ transcription rules for Ukrainian are the two external reference systems.
