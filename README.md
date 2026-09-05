# Evropéïća

**A Latin orthography for Ukrainian — specified, implemented and tested.**

🌐 **[akrivonos.github.io/evropeica](https://akrivonos.github.io/evropeica/)** · 📖 **[Rulebook](docs/RULEBOOK.md)** · ⌨️ **[Keyboard](public/keyboards/evropeica.kmx)**

Evropéïća (Європеїця) writes Ukrainian in the Latin alphabet using the Czech/Polish diacritic tradition — Č, Š, Ž, Ł, Ń — the same family as Belarusian Łacinka. It is not a romanization for passports; it is an attempt at an orthography you could actually read and write a language in.

```
Ще не вмерла України ні слава, ні воля  →  Šče ne vmerła Ukraïny ni słava, ni vola
Щастя не купиш за гроші                →  Ščasťa ne kupyš za hroši
Всі люди народжуються вільними         →  Vsi ludy narodžujuťśa vilnymy
```

This repository holds the specification, a reference implementation in TypeScript and Python, a conformance test suite, a keyboard layout, and the website that documents it all.

## Why it is organised this way

An orthography proposal is usually a document, and documents drift from their own examples. Here the rules are **executable**:

- **[docs/RULEBOOK.md](docs/RULEBOOK.md)** is normative. Every rule has an ID (`R1`–`R10`, `V2-§n`, `V21-n`, `S1`–`S6`).
- **[src/lib/transliterate.ts](src/lib/transliterate.ts)** implements the v1.0 rules and cites those IDs in its comments.
- **[tools/evropeica.py](tools/evropeica.py)** is an independent Python port, cross-checked against the TypeScript engine string by string.
- **[tests/cases.json](tests/cases.json)** holds 142 fixtures, tagged by rule ID.
- **[tools/check_site.py](tools/check_site.py)** re-transliterates every Ukrainian sentence on the website and fails if the published Latin text disagrees with the engine.

If the spec, the code and the website ever disagree, CI says so before the site deploys.

## The layers

| Layer | Name | What it does | Automated |
|---|---|---|---|
| **v1.0** | Transliterácija | Deterministic 1:1 transliteration of modern Cyrillic (2019 pravopys) | ✅ engine |
| v1.x | Rozšyreńńa | Dialect and Old Ukrainian letters | planned |
| **v2.0** | Ortografija | Etymological spelling of loanwords: g/h, θ→t, β→b, -ter/-der, foreign l | lexicon-driven |
| **v2.1** | Nahołos | Acute stress marks, only when stress is not on the first root vowel | needs a stress dictionary |

Each layer adds rules on top of the previous one. v1.0 is stable and fully mechanical; v2.0 and v2.1 need a lexicon or a human, and are the current work.

## The alphabet (v1.0)

| Cyr | Lat | Cyr | Lat | Cyr | Lat |
|-----|-----|-----|-----|-----|-----|
| А а | A a | К к | K k | Ф ф | F f |
| Б б | B b | Л л | Ł ł / L l | Х х | Ch ch |
| В в | V v | М м | M m | Ц ц | C c |
| Г г | H h | Н н | N n | Ч ч | Č č |
| Ґ ґ | G g | О о | O o | Ш ш | Š š |
| Д д | D d | П п | P p | Щ щ | Šč šč |
| Е е | E e | Р р | R r | Ь ь | softens |
| Є є | Je je / e | С с | S s | Ю ю | Ju ju / u |
| Ж ж | Ž ž | Т т | T t | Я я | Ja ja / a |
| З з | Z z | У у | U u | Ї ї | Ï ï |
| И и | Y y | Й й | J j | | |
| І і | I i | | | | |

Soft consonants **Ď Ź L Ń Ŕ Ś Ť Ć** appear before ь or я/ю/є (and for л, also before і).

The interesting cases, all decided in the rulebook:

| | | Rule |
|---|---|---|
| знання → **znańńa** | життя → **žyťťa** | Geminates soften on both letters (R6) |
| Ілля → **Illa** | Львів → **Lviv** | Ł is hard, L is soft (R4, R6) |
| мільярд → **miljard** | Нью-Йорк → **Ńju-Jork** | ь before a iotated vowel keeps the /j/ (R5b) |
| дзьоб → **dźob** | джерело → **džereło** | дз and дж are just d+z, d+ž; з still softens (R8) |
| м'яч → **mjač** | п'ять → **pjať** | The apostrophe is dropped, the vowel carries j (R7) |

## Repository

```
docs/RULEBOOK.md          normative specification — start here
src/lib/transliterate.ts  v1.0 engine (TypeScript), used by the site converter
src/pages/                website: home, spec, converter, keyboard
tools/evropeica.py        Python port of the engine
tools/check_site.py       verifies website text against the engine
data/v2-lexicon.json      accepted v2.0 loanword spellings
tests/                    fixtures + runner
keyboards/evropeica.kmn   Keyman keyboard source (QWERTZ, two dead keys)
public/keyboards/         compiled .kmx, served from the site
```

## Running it

Requires Node ≥ 22.6 (the tests import TypeScript directly) and Python ≥ 3.12.

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static output in dist/
```

The three correctness checks, all of which CI runs before deploying:

```bash
npm test                                        # 142 engine fixtures
py tools/evropeica.py --self-test --cross-check # Python port matches TypeScript
py tools/check_site.py                          # website text matches the engine
```

Transliterate from the command line:

```bash
py tools/evropeica.py "Слава Україні"
```

## Changing a rule

Order matters, because everything downstream is checked against the rulebook:

1. Edit the rule in `docs/RULEBOOK.md` and give it an ID.
2. Update `src/lib/transliterate.ts` **and** `tools/evropeica.py`.
3. Add fixtures to `tests/cases.json` tagged with that ID.
4. Run all three checks above; they must be green.
5. Fix any website text `check_site.py` flags.

After editing the keyboard source, recompile it and copy the result into `public/`:

```bash
npx --yes @keymanapp/kmc build keyboards/evropeica.kmn
cp keyboards/evropeica.kmx public/keyboards/
```

## Open questions

Listed in full in [RULEBOOK §7](docs/RULEBOOK.md). The substantive ones:

- **я/ю after hushing geminates** — keep the reversible 1:1 `Zaporižžja`, or write `Zaporižža` as pronounced?
- **ĭ** — now that ь before a iotated vowel is handled by R5b, this letter only appears in foreign and dialect words. Keep it in the alphabet?
- **Foreign l (V2-§8)** — where is the boundary for old, thoroughly naturalised loans like лампа or клас?
- **Stress marks are not machine-checkable.** The site checker strips accents before comparing, so a mark on the wrong vowel passes silently until the stress dictionary lands.

## Relation to other systems

The core alphabet is close to **Belarusian Łacinka**: same diacritics, same ł/l split. Differences: Ukrainian-specific letters (Ї→Ï, Є→Je, Щ→Šč), dedicated soft letters (Ď, Ť, Ŕ) instead of an i-digraph, and the apostrophe, which Ukrainian drops in favour of a written j (м'яч → mjač).

For long soft geminates the model is the **Czech Academy's transcription rules for Ukrainian**, which double the diacritic (століття → stoliťťa). Other systems either use a j-glide with plain letters (DSTU 9112, `Zaporižžja`) or an i-digraph (Polish, `Illia`); none marks only the last letter of the pair.

## Status

A personal proposal, not a standard and not endorsed by any institution. v1.0 is stable and I would not expect it to change; v2.0 and v2.1 are still moving. Corrections to the rules, the lexicon or the examples are welcome as issues or pull requests.

## License

Dual-licensed, so that the tooling stays reusable and the orthography stays freely quotable:

- **Code** — MIT ([LICENSE](LICENSE)). Covers `src/`, `tools/`, `tests/`, `keyboards/`, and the build configuration.
- **Specification and content** — CC BY 4.0 ([LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt)). Covers `docs/RULEBOOK.md`, `data/v2-lexicon.json`, and the prose, tables and examples of the website.

The website pages under `src/pages/` are code and content in one file: the Astro markup is MIT, the orthographic text it contains is also available under CC BY 4.0. Quoting the specification only requires attribution to the Evropéïća project with a link back.
