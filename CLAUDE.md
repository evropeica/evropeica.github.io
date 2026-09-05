# evropeica

Reference website + engine for the Evropéïća Ukrainian Latin orthography.

## The one rule
`docs/RULEBOOK.md` is normative. Engine, Python port, fixtures and page text must agree with it. If you change behaviour: rulebook → engine (TS + Python) → `tests/cases.json` → `npm test` → `py tools/evropeica.py --self-test --cross-check` → `py tools/check_site.py` → page text.

## Stack
- Astro 5.x static site, no framework components; vanilla TS in `<script>`.
- Engine: `src/lib/transliterate.ts` (v1.0). Python twin: `tools/evropeica.py`.
- Site spellchecker: `tools/check_site.py` (twins every Latin string with its Cyrillic and diffs against the engine; v2.0 words come from `data/v2-lexicon.json`).
- Keyboard: `keyboards/evropeica.kmn` → compile with `npx --yes @keymanapp/kmc build keyboards/evropeica.kmn`, copy the `.kmx` to `public/keyboards/` (the compiled file in `keyboards/` is a build artifact and is git-ignored).

## Layout
- `src/pages/index.astro`, `spec/index.astro`, `spec/v1.astro`, `spec/v2.astro`, `converter.astro`, `keyboard.astro`
- `src/layouts/Base.astro` — nav, footer, global CSS
- `src/lib/url.ts` — `withBase()`; every internal link goes through it because the site is served from a `/evropeica` base path
- `docs/RULEBOOK.md` — the specification
- `tests/` — `cases.json` + `run.mjs`

## Writing site text (RULEBOOK §6)
- `/spec/v1/` is pure v1.0: no stress marks, no v2.0 words.
- Other pages: v2.0 vocabulary allowed (must be in the lexicon); stress marks used on index, spec/index, converter, keyboard; `/spec/v2/` prose is unstressed except the v2.1 examples.
- Every Latin paragraph/heading/cell needs a Cyrillic twin so the checker can verify it.
- Brand is `Evropéïća` with Latin ï (U+00EF). Never Cyrillic ї inside Latin words, never ľ.

## Deployment
GitHub Pages via `.github/workflows/deploy.yml` on push to `master`. The workflow runs the three checks before building. Published at https://evropeica.github.io/ from the organisation repo `evropeica/evropeica.github.io`, served at the domain root (`base: '/'`). Internal links still go through `withBase()`, so a custom domain later means changing `site` in `astro.config.mjs` and adding a `CNAME`.

## Licensing
Dual: MIT for code, CC BY 4.0 for the specification and site content. Keep new files consistent with that split and do not paste in text of unknown provenance.

## Environment
- Windows. Python is `py` (3.14); bare `python` is a Store stub. Node 24.
- `npm run dev` → http://localhost:4321; `npm run build` → `dist/`.
- Local scratch and superseded working notes live in `_local/` (git-ignored).

## Related
- Lexykon — stress dictionary intended to drive the future v2.1 converter.
- Reference systems worth consulting: Belarusian Łacinka, the Czech ÚJČ transcription rules for Ukrainian, DSTU 9112:2021.
