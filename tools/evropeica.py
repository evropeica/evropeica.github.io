#!/usr/bin/env python3
"""
Pure-Python port of the Evropéïća v1.0 transliteration engine.

Faithful reimplementation of `transliterate()` from src/lib/transliterate.ts —
same rule order, same edge cases (R1-R10). The normative rule descriptions
live in docs/RULEBOOK.md; keep this file, the TS engine and the rulebook in
sync. Standard library only.

Usage:
    py tools/evropeica.py "текст текст"        transliterate and print
    py tools/evropeica.py --self-test          run tests/cases.json
    py tools/evropeica.py --cross-check        also diff against the TS engine
                                                (via node) on cases.json AND every
                                                Cyrillic string found under src/pages
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# --- R1: base character mapping -------------------------------------------
CHAR_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
    'д': 'd', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'y',
    'і': 'i', 'ї': 'ï', 'й': 'j', 'к': 'k', 'л': 'ł',
    'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'ch',
    'ц': 'c', 'ч': 'č', 'ш': 'š', 'щ': 'šč',
}

# Consonants that have a dedicated soft letter (R3 / R4 / R5).
SOFT_MAP = {
    'д': 'ď', 'з': 'ź', 'л': 'l', 'н': 'ń',
    'р': 'ŕ', 'с': 'ś', 'т': 'ť', 'ц': 'ć',
}

# Iotated vowels: (full form after vowel/boundary/j, short form after a soft consonant).
IOTATED = {
    'я': ('ja', 'a'),
    'ю': ('ju', 'u'),
    'є': ('je', 'e'),
}

SOFT_SIGN = 'ь'

# R7 — accepted apostrophe code points.
APOSTROPHE_CODES = {0x27, 0x2019, 0x02BC, 0x2018, 0x2032}


def is_apostrophe(ch):
    return bool(ch) and ord(ch) in APOSTROPHE_CODES


def is_cyrillic(ch):
    return bool(ch) and 0x0400 <= ord(ch) <= 0x04FF


def is_iotated_or_ji(ch):
    if not ch:
        return False
    lo = ch.lower()
    return lo in IOTATED or lo == 'ї'


def softens(c, nxt):
    """Does `nxt` soften consonant `c`? ь and я/ю/є soften every soft-mappable
    consonant; і softens only л (R4)."""
    if not nxt:
        return False
    lo = nxt.lower()
    if lo == SOFT_SIGN or lo in IOTATED:
        return True
    return c == 'л' and lo == 'і'


def is_all_caps_word(tokens, pos):
    def in_word(t):
        return t is not None and (is_cyrillic(t) or is_apostrophe(t))

    n = len(tokens)
    start = pos
    while start > 0 and in_word(tokens[start - 1]):
        start -= 1
    end = pos + 1
    while end < n and in_word(tokens[end]):
        end += 1
    letters = [c for c in tokens[start:end] if is_cyrillic(c)]
    return len(letters) > 1 and all(c == c.upper() for c in letters)


def match_case(source, target, allcaps):
    if not source or not target:
        return target
    if allcaps:
        return target.upper()
    if source[0] == source[0].upper() and source[0] != source[0].lower():
        return target[0].upper() + target[1:]
    return target.lower()


def transliterate(text: str) -> str:
    tokens = list(text)
    n = len(tokens)
    out = []
    i = 0

    def get(idx):
        return tokens[idx] if 0 <= idx < n else None

    while i < n:
        tok = tokens[i]
        prev = get(i - 1)
        next1 = get(i + 1)
        next2 = get(i + 2)

        # R7 — apostrophe: suppressed only as a Cyrillic separator (consonant +
        # apostrophe + я/ю/є/ї); any other apostrophe passes through.
        if is_apostrophe(tok):
            if is_cyrillic(prev) and is_iotated_or_ji(next1):
                i += 1
                continue
            out.append(tok)
            i += 1
            continue

        if not is_cyrillic(tok):
            out.append(tok)
            i += 1
            continue

        lower = tok.lower()
        allcaps = is_all_caps_word(tokens, i)

        def put(s, src=tok):
            out.append(match_case(src, s, allcaps))

        if lower in SOFT_MAP:
            soft = SOFT_MAP[lower]
            l1 = next1.lower() if next1 else None

            # R6 — geminate: same soft-mappable letter twice + softener → both soft.
            if l1 == lower and softens(lower, next2):
                put(soft)
                i += 1
                continue

            # R5 — consonant + ь
            if l1 == SOFT_SIGN:
                l2 = next2.lower() if next2 else None
                if l2 and l2 in IOTATED:  # R5b
                    put(soft)
                    put(IOTATED[l2][0], next2)
                    i += 3
                    continue
                put(soft)  # R5a
                i += 2
                continue

            # R3 — consonant + я/ю/є → soft consonant + plain vowel
            if l1 and l1 in IOTATED:
                put(soft)
                put(IOTATED[l1][1], next1)
                i += 2
                continue

            # R4 — л before і is soft l; everywhere else л is ł
            if lower == 'л' and l1 == 'і':
                put('l')
                i += 1
                continue

        # R5c — ь after a consonant without a soft letter (foreign/dialect)
        if lower == SOFT_SIGN:
            l1 = next1.lower() if next1 else None
            if l1 and l1 in IOTATED:
                i += 1
                continue
            if l1 == 'о':
                put('j')
                i += 1
                continue
            put('ĭ')
            i += 1
            continue

        # R2 — iotated vowel not consumed by a soft consonant: always full form
        if lower in IOTATED:
            put(IOTATED[lower][0])
            i += 1
            continue

        if lower in CHAR_MAP:
            put(CHAR_MAP[lower])
            i += 1
            continue

        # R10 — non-Ukrainian Cyrillic (ы э ъ ё …) passes through unchanged.
        out.append(tok)
        i += 1

    return ''.join(out)


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def run_self_test(verbose=True):
    cases_path = REPO_ROOT / 'tests' / 'cases.json'
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    passed = 0
    failed = 0
    for case in cases:
        cyr, lat, rule = case['cyr'], case['lat'], case.get('rule', '-')
        got = transliterate(cyr)
        if got == lat:
            passed += 1
        else:
            failed += 1
            if verbose:
                print(f"FAIL [{rule}] {cyr}\n   expected: {lat}\n   got:      {got}")
    if verbose:
        print(f"{passed} passed, {failed} failed ({len(cases)} cases)")
    return failed == 0, passed, failed, len(cases)


# --------------------------------------------------------------------------
# Cross-check against the TS engine (via node)
# --------------------------------------------------------------------------

CYR_RUN_RE = re.compile(
    r'[Ѐ-ӿ]'
    r"[Ѐ-ӿ’ʼ‘′'\-\s.,:;!?()«»\"0-9]*"
)


def extract_cyrillic_strings_from_astro(path: Path):
    """Best-effort extraction of every Cyrillic run of text in an .astro file
    (used only to widen cross-check coverage; not the site spellchecker)."""
    text = path.read_text(encoding='utf-8')
    found = set()
    for m in CYR_RUN_RE.finditer(text):
        s = m.group(0).strip()
        s = re.sub(r'\s+', ' ', s)
        if s:
            found.add(s)
    return found


def gather_cross_check_strings():
    strings = set()
    cases_path = REPO_ROOT / 'tests' / 'cases.json'
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    for case in cases:
        strings.add(case['cyr'])

    pages_dir = REPO_ROOT / 'src' / 'pages'
    for astro_file in sorted(pages_dir.rglob('*.astro')):
        strings |= extract_cyrillic_strings_from_astro(astro_file)

    return sorted(strings)


NODE_SCRIPT = """
import { transliterate } from './src/lib/transliterate.ts';
import { readFileSync } from 'node:fs';
const input = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(input.map((s) => transliterate(s))));
"""


def run_node_engine(strings):
    proc = subprocess.run(
        ['node', '--input-type=module', '-e', NODE_SCRIPT],
        input=json.dumps(strings, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=str(REPO_ROOT),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"node engine failed:\n{proc.stderr}")
    return json.loads(proc.stdout)


def run_cross_check(verbose=True):
    strings = gather_cross_check_strings()
    if verbose:
        print(f"Cross-checking {len(strings)} strings against the TS engine via node...")
    ts_results = run_node_engine(strings)
    mismatches = []
    for s, ts_out in zip(strings, ts_results):
        py_out = transliterate(s)
        if py_out != ts_out:
            mismatches.append((s, py_out, ts_out))
    if verbose:
        for s, py_out, ts_out in mismatches:
            print(f"MISMATCH {s!r}\n   python: {py_out}\n   ts:     {ts_out}")
        print(f"{len(strings) - len(mismatches)} matched, {len(mismatches)} mismatched ({len(strings)} strings)")
    return len(mismatches) == 0, mismatches, len(strings)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Evropéïća v1.0 transliteration engine (Python port)")
    parser.add_argument('text', nargs='?', help='Cyrillic text to transliterate')
    parser.add_argument('--self-test', action='store_true', help='run tests/cases.json against this engine')
    parser.add_argument('--cross-check', action='store_true',
                         help='also diff against the TS engine (via node) on cases.json + site strings')
    args = parser.parse_args(argv)

    if args.self_test or args.cross_check:
        ok = True
        if args.self_test or args.cross_check:
            self_test_ok, *_ = run_self_test(verbose=True)
            ok = ok and self_test_ok
        if args.cross_check:
            cross_ok, *_ = run_cross_check(verbose=True)
            ok = ok and cross_ok
        return 0 if ok else 1

    if args.text is None:
        parser.print_help()
        return 1

    print(transliterate(args.text))
    return 0


if __name__ == '__main__':
    sys.exit(main())
