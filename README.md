# Evropéïća

Ukrainian Latin orthography project — a layered system for writing Ukrainian with the Latin alphabet, plus its reference website, transliteration engine, keyboard layout and conformance tools.

**Normative rules live in [docs/RULEBOOK.md](docs/RULEBOOK.md).** Everything else (engine, tests, site text) must agree with it.

## What is Evropéïća?

Evropéïća (Європеїця) is a Latin-script orthography for Ukrainian in the Czech/Polish diacritic tradition (Č, Š, Ž, Ł, Ń…), closest to Belarusian Łacinka. It is layered:

| Layer | Name | What it does |
|---|---|---|
| **v1.0** | Transliterácija | Deterministic 1:1 transliteration of modern Cyrillic (2019 pravopys). Implemented by the engine. |
| v1.x | Rozšyreńńa | Dialect / Old Ukrainian letters (planned). |
| **v2.0** | Ortografija | Etymological spelling of foreign words: g/h, θ→t, β→b, -ter/-der, foreign l, -ija. Lexicon-driven. |
| **v2.1** | Nahołos | Acute stress marks (á é ý í ḯ ó ú) when stress is not on the first root vowel. |

### v1.0 in one table

| Cyr | Lat | Cyr | Lat | Cyr | Lat |
|-----|-----|-----|-----|-----|-----|
| А а | A a | К к | K k | Ф ф | F f |
| Б б | B b | Л л | Ł ł / L l | Х х | Ch ch |
| В в | V v | М м | M m | Ц ц | C c |
| Г г | H h | Н н | N n | Ч ч | Č č |
| Ґ ґ | G g | О о | O o | Ш ш | Š š |
| Д д | D d | П п | P p | Щ щ | Šč šč |
| Е е | E e | Р р | R r | Ь ь | softens (ĭ residual) |
| Є є | Je je / e | С с | S s | Ю ю | Ju ju / u |
| Ж ж | Ž ž | Т т | T t | Я я | Ja ja / a |
| З з | Z z | У у | U u | Ї ї | Ï ï |
| И и | Y y | Й й | J j | | |
| І і | I i | | | | |

Soft consonants: Ď Ź L Ń Ŕ Ś Ť Ć (before ь or я/ю/є; л also before і).

```
Київ → Kyïv                     знання → znańńa      Ілля → Illa
Щастя не купиш за гроші         мільярд → miljard    Нью-Йорк → Ńju-Jork
  → Ščasťa ne kupyš za hroši    дзьоб → dźob         м'яч → mjač
```

## Repository

```
docs/RULEBOOK.md          normative rules (R1–R10, V2-§n, V21-n, S1–S6)
docs/audit-2026-09-05.md  audit that triggered the current rule set
src/lib/transliterate.ts  v1.0 engine (TypeScript, used by the site)
tools/evropeica.py        Python port of the engine (+ --self-test, --cross-check)
tools/check_site.py       site spellchecker: compares every Latin/Cyrillic twin on the pages
data/v2-lexicon.json      accepted v2.0 spellings (Cyrillic → Latin)
tests/cases.json          engine fixtures, one block per rule
tests/run.mjs             npm test
keyboards/evropeica.kmn   Keyman source (QWERTZ, two dead keys, AltGr)
public/keyboards/*.kmx    compiled keyboard
src/pages/                index, spec/{index,v1,v2}, converter, keyboard
src/layouts/Base.astro    shared layout
```

## Develop

```bash
npm install
npm run dev              # http://localhost:4321
npm test                 # engine fixtures
py tools/evropeica.py --self-test --cross-check
py tools/check_site.py   # page text vs engine + lexicon
npm run build            # static output in dist/
```

Node ≥ 22.6 (tests import `.ts` directly). Python 3.12+ for the tools.

## Changing a rule

1. Edit the rule in `docs/RULEBOOK.md` (give it an ID).
2. Change `src/lib/transliterate.ts` and `tools/evropeica.py`.
3. Add fixtures to `tests/cases.json`; `npm test` and `py tools/evropeica.py --self-test --cross-check` must pass.
4. Run `py tools/check_site.py` and fix the page text it flags.

## Relation to Belarusian Łacinka

The core alphabet is close to Belarusian Łacinka (same Czech/Polish diacritics, ł/l split). Differences: Ukrainian letters (Ї→Ï, Є→Je, Щ→Šč), extra soft letters (Ď, Ť, Ŕ) instead of the i-digraph, geminate softening written on both letters (znańńa, as in Czech transcription of Ukrainian), and the apostrophe: Ukrainian drops it and writes the vowel with j (м'яч → mjač), while Belarusian Łacinka has no apostrophe at all and writes j directly.

## License

TBD — decide before publishing (suggested: MIT for code, CC BY 4.0 for the specification text).
