/**
 * Evropeica transliteration engine — Layer 1.0 (pure 1:1 from Cyrillic)
 * Based on 2019 Ukrainian pravopys.
 */

const CHAR_MAP: Record<string, string> = {
  'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
  'д': 'd', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'y',
  'і': 'i', 'ї': 'ï', 'й': 'j', 'к': 'k', 'л': 'ł',
  'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
  'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'ch',
  'ц': 'c', 'ч': 'č', 'ш': 'š', 'щ': 'šč',
};

const SOFT_MAP: Record<string, string> = {
  'д': 'ď', 'з': 'ź', 'л': 'l', 'н': 'ń',
  'р': 'ŕ', 'с': 'ś', 'т': 'ť', 'ц': 'ć',
};

const IOTATED: Record<string, [string, string]> = {
  'я': ['ja', 'a'],
  'ю': ['ju', 'u'],
  'є': ['je', 'e'],
};

const APOSTROPHES = new Set(["'", '’', 'ʼ', ''', '‘']);

function isUkrainianCyrillic(ch: string): boolean {
  const code = ch.charCodeAt(0);
  return (code >= 0x0400 && code <= 0x04FF) || ch === 'ґ' || ch === 'Ґ';
}

function isCyrillicVowel(ch: string): boolean {
  return 'аеєиіїоуюя'.includes(ch.toLowerCase());
}

function isWordBoundary(ch: string): boolean {
  return !ch || /[\s\-–—]/.test(ch);
}

function isAllCapsWord(tokens: string[], pos: number): boolean {
  let start = pos;
  while (start > 0 && tokens[start - 1] && isUkrainianCyrillic(tokens[start - 1])) start--;
  let end = pos + 1;
  while (end < tokens.length && tokens[end] && isUkrainianCyrillic(tokens[end])) end++;
  const chars = tokens.slice(start, end).filter(t => isUkrainianCyrillic(t));
  return chars.length > 1 && chars.every(c => c === c.toUpperCase());
}

function matchCase(source: string, target: string, allcaps: boolean): string {
  if (!source || !target) return target;
  if (allcaps) return target.toUpperCase();
  if (source[0] === source[0].toUpperCase() && source[0] !== source[0].toLowerCase()) {
    return target[0].toUpperCase() + target.slice(1);
  }
  return target.toLowerCase();
}

const D_PREFIXES = new Set(['від', 'над', 'під', 'од', 'перед', 'серед']);

function isPrefixBoundary(tokens: string[], dPos: number): boolean {
  for (const prefix of D_PREFIXES) {
    const plen = prefix.length;
    if (dPos < plen - 1) continue;
    const start = dPos - (plen - 1);
    const candidate = tokens.slice(start, dPos + 1).map(t => t.toLowerCase()).join('');
    if (candidate === prefix) {
      if (start === 0 || !isUkrainianCyrillic(tokens[start - 1])) {
        return true;
      }
    }
  }
  return false;
}

export function transliterate(input: string): string {
  const tokens = [...input];
  const result: string[] = [];
  const n = tokens.length;
  let i = 0;

  while (i < n) {
    const tok = tokens[i];

    if (APOSTROPHES.has(tok)) {
      i++;
      continue;
    }

    if (!isUkrainianCyrillic(tok)) {
      result.push(tok);
      i++;
      continue;
    }

    const lower = tok.toLowerCase();
    const allcaps = isAllCapsWord(tokens, i);

    // Soft sign
    if (lower === 'ь') {
      i++;
      continue;
    }

    // Digraphs: дж, дз
    if (lower === 'д' && i + 1 < n) {
      const next = tokens[i + 1]?.toLowerCase();
      if (next === 'ж' && !isPrefixBoundary(tokens, i)) {
        result.push(matchCase(tok, 'dž', allcaps));
        i += 2;
        continue;
      }
      if (next === 'з' && !isPrefixBoundary(tokens, i)) {
        result.push(matchCase(tok, 'dz', allcaps));
        i += 2;
        continue;
      }
    }

    // Iotated vowels: я, ю, є
    if (lower in IOTATED) {
      const [full, short] = IOTATED[lower];
      const prev = i > 0 ? tokens[i - 1] : '';
      const prevLower = prev.toLowerCase();

      // After soft sign → short form (consonant was already softened)
      if (prevLower === 'ь') {
        result.push(matchCase(tok, short, allcaps));
        i++;
        continue;
      }

      // Word-initial or after boundary/apostrophe → full iotated form
      if (i === 0 || isWordBoundary(prev) || APOSTROPHES.has(prev) || !isUkrainianCyrillic(prev)) {
        result.push(matchCase(tok, full, allcaps));
        i++;
        continue;
      }

      // After vowel → full iotated form
      if (isCyrillicVowel(prev)) {
        result.push(matchCase(tok, full, allcaps));
        i++;
        continue;
      }

      // After consonant mid-word → full iotated form
      result.push(matchCase(tok, full, allcaps));
      i++;
      continue;
    }

    // Soft consonant: consonant followed by ь
    if (lower in SOFT_MAP && i + 1 < n && tokens[i + 1]?.toLowerCase() === 'ь') {
      result.push(matchCase(tok, SOFT_MAP[lower], allcaps));
      i += 2;
      continue;
    }

    // Л before і → soft l (no stroke)
    if (lower === 'л' && i + 1 < n && tokens[i + 1]?.toLowerCase() === 'і') {
      result.push(matchCase(tok, 'l', allcaps));
      i++;
      continue;
    }

    // Standard character map
    if (lower in CHAR_MAP) {
      result.push(matchCase(tok, CHAR_MAP[lower], allcaps));
      i++;
      continue;
    }

    // Passthrough for unmapped Cyrillic
    result.push(tok);
    i++;
  }

  return result.join('');
}
