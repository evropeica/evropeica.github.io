# Evropéïća Rulebook

**Status:** normative. When this file, the engine (`src/lib/transliterate.ts`), the fixtures (`tests/cases.json`) and the site text disagree, this file wins and the others are bugs. Every rule has an ID (R1…R10, V2-§n, S1…) so humans and AI can cite it.

**Change process:** edit the rule here → change the engine → add/adjust a case in `tests/cases.json` → `npm test` → `py tools/check_site.py` (page text) → only then touch page text.

---

## 0. What Evropéïća is

A Latin orthography for Ukrainian in the Czech/Polish diacritic tradition, closest relative Belarusian Łacinka. It is layered:

| Layer | Name | What it does | Automated? |
|---|---|---|---|
| **v1.0** | Transliterácija | 1:1 mechanical transliteration of modern Ukrainian Cyrillic (2019 pravopys). Deterministic, reversible except the cases in §3. | Yes (engine) |
| v1.x | Rozšyreńńa | Dialect and Old Ukrainian letters (ы, ё, ъ, э …). Planned. | — |
| **v2.0** | Ortografija | Etymological spelling of foreign-origin words (g/h, th→t, β→b, -ter/-der, foreign l). Needs a lexicon or a human. | No |
| **v2.1** | Nahołos | Acute stress marks on non-default stress. Needs a stress dictionary (Lexykon). | No |

**Design principles** (from the original concept, Pobudova): follow the tradition of Ukrainian speech; be intuitive; be comfortable to write. Diacritic count is **not** a design target: a diacritic letter is preferred over a digraph wherever it reads better (Šč over Shch).

---

## 1. Alphabet (v1.0)

| Cyr | Lat | Group | Note |
|---|---|---|---|
| А а | A a | green | |
| Б б | B b | green | |
| В в | V v | green | |
| Г г | H h | yellow | fricative /ɦ/; v2.0 restores g in foreign words |
| Ґ ґ | G g | yellow | |
| Д д | D d | green | soft: Ď ď |
| Е е | E e | green | |
| Є є | Je je / e | yellow | see R2, R3 |
| Ж ж | Ž ž | red | |
| З з | Z z | green | soft: Ź ź |
| И и | Y y | yellow | |
| І і | I i | green | |
| Ї ї | Ï ï (U+00CF/U+00EF) | red | always /ji/; stressed form Ḯ ḯ (U+1E2E/U+1E2F) |
| Й й | J j | yellow | |
| К к | K k | green | |
| Л л | Ł ł / L l | yellow | ł hard, l soft — see R4 |
| М м | M m | green | |
| Н н | N n | green | soft: Ń ń |
| О о | O o | green | |
| П п | P p | green | |
| Р р | R r | green | soft: Ŕ ŕ |
| С с | S s | green | soft: Ś ś |
| Т т | T t | green | soft: Ť ť |
| У у | U u | green | |
| Ф ф | F f | green | |
| Х х | Ch ch | yellow | digraph, as in Czech/Polish |
| Ц ц | C c | yellow | soft: Ć ć |
| Ч ч | Č č | red | |
| Ш ш | Š š | red | |
| Щ щ | Šč šč | red | |
| Ь ь | (softens) / ĭ | red | see R5 |
| Ю ю | Ju ju / u | yellow | see R2, R3 |
| Я я | Ja ja / a | yellow | see R2, R3 |
| ’ (apostrophe) | — | | dropped, see R7 |

**Groups** (the colour scheme from Pobudova, now mapped): green = the Latin letter is obvious; yellow = a choice had to be made and is explained in this document; red = diacritic letters; purple = dialect/archaic letters reserved for v1.x (ы э ъ ё, currently passed through unchanged); grey = q x w, used only inside foreign names in their original spelling.

**Complete inventory of Latin letters the engine can emit:** a b c č ć ch d ď e f g h i ï ĭ j k l ł m n ń o p r ŕ s ś š šč t ť u v y z ź ž (and their capitals). v2.1 adds á é ý í ó ú ḯ. Anything else in Latin site text (ľ, ě, ü, Cyrillic ї inside a Latin word, an apostrophe inside a Ukrainian word) is an error.

---

## 2. Transliteration rules (v1.0)

Terminology: **soft-mappable consonants** = д з л н р с т ц (they have a soft letter: ď ź l ń ŕ ś ť ć). **Softeners** = ь, я, ю, є (and і, for л only). **Iotated vowels** = я ю є; ї is always ï.

### R1 — Base mapping
Each letter maps per the table in §1. Non-letter characters, Latin text, digits and punctuation pass through unchanged. Combining marks (e.g. U+0301 in мо́ре) pass through and attach to the transliterated vowel (móre).

### R2 — Iotated vowels: full form
я ю є → **ja ju je** at the start of a word, after a vowel, after й, after an apostrophe, after a hyphen, and after any consonant that is *not* soft-mappable.
яблуко → jabłuko · моя → moja · майя → majja · Юлія → Julija · свято → svjato · бюро → bjuro · Кюрі → Kjuri · Запоріжжя → Zaporižžja · ніччю → niččju · пів-яблука → piv-jabłuka.

### R3 — Soft-mappable consonant + я/ю/є: soft letter + plain vowel
The consonant takes its soft form and the vowel loses its j: ля → la, ню → ńu, тє → ťe, ся → śa, ря → ŕa, дю → ďu, зя → źa, ця → ća.
для → dla · люди → ludy · буряк → buŕak · пісня → pisńa · сміється → smijeťśa · народжуються → narodžujuťśa · земля → zemla.

### R4 — Л: ł hard, l soft
л → **ł** by default. л → **l** when soft: before ь, before я/ю/є (R3), and before **і**. л before и, е, а, о, у and before consonants is ł.
ліс → lis · Львів → Lviv · вільними → vilnymy · Ілько → Ilko · ламати → łamaty · яблуко → jabłuko · джерело → džereło · Лук'ян → Łukjan. (Other consonants before і stay hard: ніс → nis, тінь → tiń — the letter is the same, only л distinguishes.)

### R5 — Soft sign ь
**R5a.** Soft-mappable consonant + ь → soft letter; ь itself writes nothing. Also before о: льон → lon, сьогодні → śohodni, трьох → tŕoch.
день → deń · сіль → sil · мідь → miď · хлопець → chłopeć · батько → baťko · Хмельницький → Chmelnyćkyj · тьмяний → ťmjanyj.

**R5b.** Soft-mappable consonant + ь + я/ю/є → soft letter + **full** iotated vowel (the ь marks softness *and* a following /j/; both are written).
мільярд → miljard · коньяк → końjak · Ньютон → Ńjuton · Мольєр → Moljer · Нью-Йорк → Ńju-Jork · Дьяков → Ďjakov · Севастьян → Sevasťjan. (ьй is simply soft + j: бульйон → buljon, мільйон → miljon.)
This keeps the three-way contrast reversible: ня → ńa, нья → ńja, н’я → nja.

**R5c.** ь after a consonant that is *not* soft-mappable (б п в м ф г ґ к х ж ч ш щ): before я/ю/є → nothing (the vowel supplies j: бья → bja); before о → **j** (Бьорн → Bjorn); anywhere else → **ĭ**. These are all foreign or dialect spellings; standard Ukrainian orthography does not produce them.

### R6 — Geminates: soften both
When the same soft-mappable letter is doubled and followed by a softener, **both** letters take the soft form. Precedent: the Czech Academy's transcription rules for Ukrainian double the diacritic (життьовий → žyťťovyj, століття → stoliťťa, управління → upravliňňa — ÚJČ Internetová jazyková příručka §926), and Czech is where ď ť ň come from. Other systems attest either a j-glide with plain letters (DSTU 9112 Zaporižžja, Wiktionary Illjá) or an i-digraph (Polish Illia); none marks only the *last* letter. Phonetically the geminate is one long soft consonant, so marking both is also the honest spelling. For л the choice is forced: Iłla would insert the *hard* letter into an all-soft word and break reversibility.
знання → znańńa · життя → žyťťa · Ілля → Illa · Іллі → Illi · суддя → suďďa · стаття → staťťa · Полісся → Poliśśa · весілля → vesilla · Поділля → Podilla · ллється → lleťśa · ЗНАННЯ → ZNAŃŃA.
Doubled letters without a softener stay hard: Ганна → Hanna, Вінниця → Vinnyća, відділ → viddił. Clusters of *different* consonants are not assimilated in writing (пісня → pisńa, not piśńa), because Cyrillic does not mark it either.

### R7 — Apostrophe
The Ukrainian apostrophe (between a consonant and я/ю/є/ї) is dropped; the vowel takes its full form by R2.
м'яч → mjač · п'ять → pjať · об'єм → objem · кур'єр → kurjer · пір'я → pirja · з'їзд → zïzd · під'їзд → pidïzd · Лук'ян → Łukjan · Мін'юст → Minjust · В'ячеслав → Vjačesłav.
Any other apostrophe-like character (quotation marks ‘ ’, apostrophes inside Latin text such as *don't*) is kept. Accepted apostrophe code points: U+0027, U+2019, U+02BC, U+2018, U+2032.

### R8 — дж, дз
Written **dž, dz** — exactly the sum of the letters. No distinction is made between the affricate (джерело, дзвін) and the cluster at a prefix boundary (підживити, надзвичайний); Polish (dzwon vs odzyskać) lives with the same ambiguity. з in дз softens normally: ґедзь → gedź, дзьоб → dźob, дзюдо → dźudo, Дзюба → Dźuba.

### R9 — Case
Title case: only the first Latin letter of a multi-letter output is capitalised (Що → Ščo, Харків → Charkiv, Юрій → Jurij). A word whose Cyrillic letters are all capitals (two or more letters; apostrophes ignored) is emitted in all capitals (ЩО → ŠČO, ЄС → JES, ДЕНЬ → DEŃ, М'ЯЧ → MJAČ). A single capital letter is title case (Я → Ja, Щ → Šč).

### R10 — Everything else passes through
Non-Ukrainian Cyrillic (ы э ъ ё and other Cyrillic blocks) is left unchanged until v1.x defines it. Latin letters, digits, punctuation, whitespace, emoji: unchanged.

---

## 3. Known ambiguities (Latin → Cyrillic)

v1.0 is designed to be reversible; these are the residual ambiguities, all accepted:

| Latin | Could be | Resolution |
|---|---|---|
| dž, dz | дж/дз affricate or д+ж/д+з cluster | not distinguished (R8) |
| ja/ju/je after a vowel | я or й+а (йа) | йа/йу/йе do not occur in Ukrainian words |
| ï after a consonant | 'ї (з'їзд) or ї | apostrophe is recoverable from morphology only |
| ža/ča/ša/šča + … | жа or жя (Запоріжжя vs hypothetical Запоріжжа) | Ukrainian writes я after hushing consonants only in geminates (-жжя, -ччя, -шшя); reverse by morphology |
| bjo | бьо or бйо | 2019 pravopys prefers йо anyway |

---

## 4. v2.0 — Ortografija (foreign-origin words)

v2.0 is applied on top of v1.0 output, word by word, for words of foreign origin. It cannot be automated without a lexicon; on the site every v2.0 spelling must be listed in `data/v2-lexicon.json` (Cyrillic → v2 Latin) so the checker can accept it.

| ID | Rule | v1.0 | v2.0 |
|---|---|---|---|
| V2-§1 | Foreign /g/ written г → **g** (also word-final, in names, and word-initial before consonants) | heohrafija, prohrama, hrupa, Boh, Olha, Ołeh, hroza | geografija, programa, grupa, Bog, Olga, Ołeg, groza |
| V2-§2 | Foreign words that lost initial /h/ in Cyrillic get it back | arfa, istorija, Hannibal | harfa, historija, Hannibal |
| V2-§3 | Greek θ → **t** (not f) | marafon, mif, mifołohija, Afiny, efir, kafedra | maraton, mit, mitologija, Ateny, eter, katedra |
| V2-§4 | Greek eu → **ev** (never jev) or stays eu | Jevropa, jevrejśkyj | Evropa, eukariot; names allow both: Evgenij / Jevgenij |
| V2-§5 | Proper names from Latin-script languages keep their original spelling; Ukrainian case endings may be appended | — | Sigmund Freud, Goethe, Ljubljana; Macrona, Berlina |
| V2-§6 | -тр/-др → **-ter/-der** | teatr, centr, ministr, cylindr | teater, center, minister, cylinder |
| V2-§7 | Greek β → **b** | Vavyłon, Vizantija, symvoł, dyjavoł | Babylon, Bizantija, symbol, diabol |
| V2-§8 | Foreign (non-Slavic) л → plain **l** in every position | mifołohija, fiłosofija, hołohrama | mitologija, filosofija, holograma. Slavic names keep ł: Ołeg, Gałyna, Głevacha |
| V2-§9 | Endings: -ія stays **-ija** (geografija, religija, mitologija), never Latin-style -ia. -ція → -cija (transliteracija, specyfikacija). | | |
| V2-§10 | International brand and personal names are not transliterated at all; for common foreign nouns prefer the Ukrainian word (manager → kerivnyk) | | |

Words currently written in v2.0 on the site must appear in `data/v2-lexicon.json`.

---

## 5. v2.1 — Nahołos (stress)

| ID | Rule |
|---|---|
| V21-1 | Stress is marked with an acute accent: á é ý í ó ú **ḯ**. |
| V21-2 | No mark when stress falls on the first vowel of the root. Mark in every other position, including on a prefix vowel (ви́хід → výchid) and on any later vowel (говори́ти → hovorýty, замо́к → zamók). |
| V21-3 | One mark per word maximum. Monosyllables are never marked. |
| V21-4 | The mark goes on the vowel letter, including ï → ḯ: Украї́на → Ukraḯna, украї́нська → ukraḯnśka. Keyboard: dead acute, then AltGr+I. |
| V21-5 | Until the Lexykon integration exists, stress on the site is set by hand and must follow the УЛІФ/СУМ dictionary stress. |

---

## 6. Site text register (S-rules)

| ID | Rule |
|---|---|
| S1 | `/spec/v1/` and `/motyvacija/` are written in **pure v1.0** — no stress marks, no v2.0 vocabulary. Every Latin string there must equal the engine output for its Cyrillic twin. Motyvacija is long-form argument, and hand-placed stress on that much prose would be unverifiable until the stress dictionary lands, so it stays unstressed and says so at the top. |
| S1b | Pages in another natural language live under `src/pages/<lang>/` (currently `en/`). They carry no Cyrillic twins, so S1–S4 do not apply and `tools/check_site.py` skips them. Ukrainian quoted inside them is illustrative and must still be correct. |
| S2 | All other pages may use v2.0 vocabulary (every such word must be in `data/v2-lexicon.json`). Stress marks (v2.1) are used on `/`, `/spec/`, `/converter/` and `/keyboard/`; the long prose of `/spec/v2/` stays unstressed until the Lexykon integration, except the v2.1 examples table. The checker strips acute accents and applies the lexicon before comparing to the engine, so a wrong stress position is *not* caught automatically — check it against a dictionary. |
| S3 | Every Latin paragraph, heading and table cell has a Cyrillic twin. Pages are laid out as **two parallel columns**: the Latin text on the left, the same text in Cyrillic on the right. Prose pairs are written as `<div class="bi"><p>Lat</p><p class="cyr">Cyr</p></div>`; headings as `<h2 class="bi"><span class="lat">Lat</span><span class="cyr">Cyr</span></h2>`. An ornament that exists only on the Latin side (a numbered badge, say) carries `class="no-check"` so it is excluded from comparison. Text without a twin cannot be checked and is not allowed except for foreign names and code. |
| S4 | Only characters from the §1 inventory (plus v2.1 accents) may appear inside Latin Ukrainian words. In particular: Latin ï (U+00EF), never Cyrillic ї (U+0457); l, never ľ; no apostrophes inside words. |
| S5 | Brand name: **Evropéïća** (Latin ï, stress on é, v2.0 §4 form of Європеїця). Cyrillic form: Європеїця. The v1.0 transliteration Jevropeïća is never used as the name; the spec explains the derivation once. |
| S6 | Dashes: em dash — with spaces around it in running text, as in Ukrainian typography. |

---

## 7. Open questions (need a human decision)

1. **я/ю after hushing geminates** (Zaporižžja, niččju): keep 1:1 `ja/ju` (current) or write `Zaporižža`, `nićču` as pronounced? Current choice keeps reversibility.
2. **ĭ**: with R5b in place the letter appears only in foreign/dialect words (R5c). Keep it in the alphabet or drop it and write j?
3. **V2-§8 boundary**: which loanwords count as "foreign" for plain l (e.g. лампа, клас, план — Slavicised centuries ago)? Proposal: only Greek/Latin/Western learned vocabulary and modern borrowings; everyday old loans keep ł.
4. **V2-§2**: the list of words that regain initial h is closed (harfa, historija, histerija, homonim, hijerohlif…); it needs a lexicon, not a rule.
5. **ḯ is typographically weak (V21-4).** Stacking an acute over a diaeresis is rare in Latin typography and few text faces handle it well. Measured 2026-09-05: Source Serif 4 and PT Serif have no glyph for U+1E2F/U+1E2E at all; Literata, Charis SIL and Gentium Book Plus do, but even Literata collides the acute into the diaeresis, so at body size `Ukraḯna` reads as a smudge. Options: (a) keep it and accept the look, (b) leave stress unmarked on ї and note the exception, (c) mark stress on ї with a following modifier letter instead. The site currently keeps it, and avoids it in display-size text.

---

*This specification is licensed [CC BY 4.0](../LICENSE-CC-BY-4.0.txt). Quote it freely with attribution to the Evropéïća project. The reference implementation is MIT-licensed; see [LICENSE](../LICENSE).*
