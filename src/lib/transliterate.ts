/**
 * Evropéïća transliteration engine — v1.0 (1:1 from modern Ukrainian Cyrillic,
 * 2019 pravopys). The normative description of every rule implemented here is
 * docs/RULEBOOK.md; keep the two in sync and add a case to tests/cases.json
 * for every rule you touch.
 */

const CHAR_MAP: Record<string, string> = {
  'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
  'д': 'd', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'y',
  'і': 'i', 'ї': 'ï', 'й': 'j', 'к': 'k', 'л': 'ł',
  'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
  'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'ch',
  'ц': 'c', 'ч': 'č', 'ш': 'š', 'щ': 'šč',
};

/** Consonants that have a dedicated soft letter (R3). */
const SOFT_MAP: Record<string, string> = {
  'д': 'ď', 'з': 'ź', 'л': 'l', 'н': 'ń',
  'р': 'ŕ', 'с': 'ś', 'т': 'ť', 'ц': 'ć',
};

/** Iotated vowels: [full form after vowel/boundary/j, short form after a soft consonant]. */
const IOTATED: Record<string, [string, string]> = {
  'я': ['ja', 'a'],
  'ю': ['ju', 'u'],
  'є': ['je', 'e'],
};

const SOFT_SIGN = 'ь';

function isApostrophe(ch: string): boolean {
  const code = ch.charCodeAt(0);
  return code === 0x27 || code === 0x2019 || code === 0x02BC
      || code === 0x2018 || code === 0x2032;
}

function isCyrillic(ch: string | undefined): boolean {
  if (!ch) return false;
  const code = ch.charCodeAt(0);
  return code >= 0x0400 && code <= 0x04FF;
}

function isIotatedOrJi(ch: string | undefined): boolean {
  if (!ch) return false;
  const l = ch.toLowerCase();
  return l in IOTATED || l === 'ї';
}

/** Does `next` soften consonant `c`? ь and я/ю/є soften every soft-mappable consonant; і softens only л (R4). */
function softens(c: string, next: string | undefined): boolean {
  if (!next) return false;
  const l = next.toLowerCase();
  if (l === SOFT_SIGN || l in IOTATED) return true;
  return c === 'л' && l === 'і';
}

function isAllCapsWord(tokens: string[], pos: number): boolean {
  const inWord = (t: string | undefined) => !!t && (isCyrillic(t) || isApostrophe(t));
  let start = pos;
  while (start > 0 && inWord(tokens[start - 1])) start--;
  let end = pos + 1;
  while (end < tokens.length && inWord(tokens[end])) end++;
  const letters = tokens.slice(start, end).filter(isCyrillic);
  return letters.length > 1 && letters.every(c => c === c.toUpperCase());
}

function matchCase(source: string, target: string, allcaps: boolean): string {
  if (!source || !target) return target;
  if (allcaps) return target.toUpperCase();
  if (source[0] === source[0].toUpperCase() && source[0] !== source[0].toLowerCase()) {
    return target[0].toUpperCase() + target.slice(1);
  }
  return target.toLowerCase();
}

export function transliterate(input: string): string {
  const tokens = [...input];
  const out: string[] = [];
  const n = tokens.length;
  let i = 0;

  while (i < n) {
    const tok = tokens[i];
    const prev = i > 0 ? tokens[i - 1] : undefined;
    const next1 = tokens[i + 1];
    const next2 = tokens[i + 2];

    // R7 — apostrophe: suppressed only as a Cyrillic separator (consonant + apostrophe + я/ю/є/ї);
    // any other apostrophe (quotation marks, Latin text) passes through.
    if (isApostrophe(tok)) {
      if (isCyrillic(prev) && isIotatedOrJi(next1)) { i++; continue; }
      out.push(tok); i++; continue;
    }

    if (!isCyrillic(tok)) { out.push(tok); i++; continue; }

    const lower = tok.toLowerCase();
    const allcaps = isAllCapsWord(tokens, i);
    const put = (s: string, src: string = tok) => out.push(matchCase(src, s, allcaps));

    if (lower in SOFT_MAP) {
      const soft = SOFT_MAP[lower];
      const l1 = next1?.toLowerCase();

      // R6 — geminate: the same soft-mappable letter twice + softener → both soft (znańńa, Illa).
      if (l1 === lower && softens(lower, next2)) { put(soft); i++; continue; }

      // R5 — consonant + ь
      if (l1 === SOFT_SIGN) {
        const l2 = next2?.toLowerCase();
        if (l2 && l2 in IOTATED) {           // R5b: нья/нью/ньє → ńja/ńju/ńje (soft + j + vowel)
          put(soft); put(IOTATED[l2][0], next2); i += 3; continue;
        }
        put(soft); i += 2; continue;          // R5a: нь → ń (also before о: льон → lon)
      }

      // R3 — consonant + я/ю/є → soft consonant + plain vowel
      if (l1 && l1 in IOTATED) {
        put(soft); put(IOTATED[l1][1], next1); i += 2; continue;
      }

      // R4 — л before і is soft l; everywhere else л is ł
      if (lower === 'л' && l1 === 'і') { put('l'); i++; continue; }
    }

    // R5c — ь after a consonant without a soft letter (rare: foreign/dialect words)
    if (lower === SOFT_SIGN) {
      const l1 = next1?.toLowerCase();
      if (l1 && l1 in IOTATED) { i++; continue; }      // бья → bja: the vowel supplies j
      if (l1 === 'о') { put('j'); i++; continue; }     // бьо → bjo
      put('ĭ'); i++; continue;                          // residual: ĭ
    }

    // R2 — iotated vowel not consumed by a soft consonant: always full form (ja/ju/je)
    if (lower in IOTATED) { put(IOTATED[lower][0]); i++; continue; }

    if (lower in CHAR_MAP) { put(CHAR_MAP[lower]); i++; continue; }

    // Non-Ukrainian Cyrillic (ы э ъ ё …) passes through unchanged (reserved for v1.x).
    out.push(tok); i++;
  }

  return out.join('');
}
