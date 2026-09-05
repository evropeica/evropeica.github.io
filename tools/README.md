# tools/

## `evropeica.py` — the v1.0 engine, ported to Python
- `py tools/evropeica.py "текст"` — transliterate and print.
- `py tools/evropeica.py --self-test` — check this port against `tests/cases.json`.
- `py tools/evropeica.py --cross-check` — also diff against `src/lib/transliterate.ts`
  (spawns `node`) on every fixture plus every Cyrillic string found under `src/pages/`.
  Both must print 0 failures/mismatches before this file is trusted.

## `check_site.py` — the site spellchecker (RULEBOOK §6)
- `py tools/check_site.py` — scan `src/pages/**/*.astro`, print findings, exit 1 if any.
- `py tools/check_site.py --json` — same, machine-readable.
- `py tools/check_site.py --fix-chars` — rewrite only the unambiguous S4 character fixes
  (Cyrillic `ї`/`Ї` → `ï`/`Ï`, `ľ`/`Ľ` → `l`/`L`) in place and report what changed. Review
  the diff before committing; it does not touch anything else.

Rule IDs in the output point back to `docs/RULEBOOK.md`: `S1` = a stress mark on
`/spec/v1/`, where none is allowed; `TWIN` = a Latin/Cyrillic pair (S3) whose Latin side
doesn't match `transliterate(cyr)` (per S2, a lexicon hit still counts as a pass); `S4` =
a character outside the §1 inventory, a Cyrillic look-alike inside a Latin word, or a
stray apostrophe; `V21-3` = more than one stress mark in one word.

## `data/v2-lexicon.json`
Cyrillic word (lowercase) → accepted v2.0 Latin spelling (lowercase, no stress marks),
per RULEBOOK §4. To add a word: confirm the spelling against §4 (or add a §4 example
first), then add one `"cyr": "lat"` entry — checked pages other than `/spec/v1/` will
then accept that spelling instead of flagging it against the raw v1.0 engine output.
