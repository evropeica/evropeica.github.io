#!/usr/bin/env python3
"""
Evropéïća site spellchecker (docs/RULEBOOK.md §6, S1-S6).

For every .astro file under src/pages/, extracts Latin/Cyrillic "twins"
(S3: heading `Lat / Cyr`, a <p>/<li>/<td> immediately followed by a sibling
<p class="cyr">, the two columns of a <div class="bilingual">, and
Cyrillic/Latin example-word table columns) and compares each twin word by
word against the reference engine (tools/evropeica.py), accepting a
mismatch when data/v2-lexicon.json lists it as an approved v2.0 spelling
(S2). It also runs the character-inventory checks (S4, V21-3) on every
Latin word on the page, independent of twins.

Usage:
    py tools/check_site.py                 human-readable report, exit 1 if any finding
    py tools/check_site.py --json          machine-readable report
    py tools/check_site.py --fix-chars     rewrite unambiguous S4 substitutions in place
                                            (Cyrillic ї->ï, Ї->Ï, ľ->l, Ľ->L inside Latin
                                            words) and report what changed. Does not touch
                                            anything else. The user runs this, not the agent.

Standard library only (html.parser for pragmatic HTML parsing).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evropeica import transliterate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = REPO_ROOT / 'src' / 'pages'
LEXICON_PATH = REPO_ROOT / 'data' / 'v2-lexicon.json'
V1_PAGE_RELPATH = 'src/pages/spec/v1.astro'

# Pages written in another natural language carry no Cyrillic twins and are not
# Ukrainian Latin, so neither the twin rules nor the §1 inventory apply to them.
SKIP_DIRS = {'en'}


def pages():
    """Every .astro page the rulebook's site rules (S1-S6) actually govern."""
    for path in sorted(PAGES_DIR.rglob('*.astro')):
        if SKIP_DIRS & set(path.relative_to(PAGES_DIR).parts[:-1]):
            continue
        yield path

# --------------------------------------------------------------------------
# Shared word tokenizer: a maximal run of Unicode letters, optionally
# continued across an internal apostrophe/hyphen (so "м'яч", "пів-яблука"
# and "don't" each stay one token, matching how transliterate() needs to
# see them, and how S4's apostrophe rule needs to see them).
# --------------------------------------------------------------------------
APOSTROPHE_CHARS = "'’ʼ‘′"
# A "letter" here also swallows any combining diacritical marks stacked on it
# (Cyrillic stress is written as a base vowel + combining U+0301, since
# Cyrillic has no precomposed accented vowels) so a stressed word like
# "мо́ре" stays one token instead of splitting at the combining mark.
_LETTER = r"[^\W\d_][̀-ͯ]*"
WORD_RE = re.compile(
    r"(?:" + _LETTER + r")+(?:[" + re.escape(APOSTROPHE_CHARS) + r"\-](?:" + _LETTER + r")+)*",
    re.UNICODE,
)

ACCENT_MAP = {
    'á': 'a', 'é': 'e', 'ý': 'y', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ḯ': 'ï',
    'Á': 'A', 'É': 'E', 'Ý': 'Y', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ḯ': 'Ï',
}
ACCENT_CHARS = set(ACCENT_MAP)

DIACRITIC_LETTERS = set('čćžłďťźśńŕïĭ')  # marks a word as "Ukrainian Latin" (S4 rule c)

# §1 "Complete inventory" + v2.1 accents. q/x/w are tolerated (Complete inventory
# omits them because the *engine* never emits them, but §1's grey group explicitly
# allows them inside foreign names) so real foreign proper nouns (Windows, Twitter,
# XKB...) don't drown out genuine typos like ľ/ě/ü.
ALLOWED_LATIN_BASE = set('abcčćdďefghiïĭjklłmnńopqrŕsśštťuvwxyzźž')
ALLOWED_LATIN = ALLOWED_LATIN_BASE | {c.upper() for c in ALLOWED_LATIN_BASE} | ACCENT_CHARS


def nfc(s: str) -> str:
    """Normalize to NFC (precomposed) so a precomposed 'ć' (U+0107) and a
    decomposed 'c'+combining-acute compare equal wherever either might sneak
    in (editors, JSON round-trips, etc.)."""
    return unicodedata.normalize('NFC', s)


def is_cyrillic_char(ch: str) -> bool:
    return 0x0400 <= ord(ch) <= 0x04FF


def strip_accents(word: str) -> str:
    return ''.join(ACCENT_MAP.get(ch, ch) for ch in word)


def strip_combining(word: str) -> str:
    """Drop combining diacritical marks (U+0300-U+036F) -- the Cyrillic-side
    convention for marking stress on мо́ре-style example words, since
    Cyrillic has no precomposed accented vowels. transliterate() would just
    pass these through unchanged (R1), which is correct for engine output
    but would poison a plain word-for-word spelling comparison."""
    return ''.join(ch for ch in word if not (0x0300 <= ord(ch) <= 0x036F))


def is_v1_page(path: Path) -> bool:
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = str(path)
    return rel == V1_PAGE_RELPATH


# --------------------------------------------------------------------------
# Preprocessing: strip frontmatter / <script> / <style> / {expr} while
# keeping line numbers stable (replace with spaces, keep newlines).
# --------------------------------------------------------------------------

def _blank_span(text: str, start: int, end: int) -> str:
    seg = text[start:end]
    blanked = ''.join(ch if ch == '\n' else ' ' for ch in seg)
    return text[:start] + blanked + text[end:]


def strip_frontmatter(text: str) -> str:
    m = re.match(r'^---\r?\n.*?\r?\n---\r?\n', text, re.DOTALL)
    if m:
        return _blank_span(text, 0, m.end())
    return text


def strip_script_style(text: str) -> str:
    for pattern in (r'<script\b.*?</script\s*>', r'<style\b.*?</style\s*>'):
        while True:
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if not m:
                break
            text = _blank_span(text, m.start(), m.end())
    return text


def strip_braces(text: str) -> str:
    """Treat every balanced {...} Astro/JS expression as opaque (blanked)."""
    out = list(text)
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    for j in range(start, i + 1):
                        if out[j] != '\n':
                            out[j] = ' '
                    start = None
    return ''.join(out)


def preprocess(raw: str) -> str:
    text = strip_frontmatter(raw)
    text = strip_script_style(text)
    text = strip_braces(text)
    return text


# --------------------------------------------------------------------------
# Minimal DOM tree
# --------------------------------------------------------------------------

class ElementNode:
    __slots__ = ('tag', 'attrs', 'children', 'line')

    def __init__(self, tag, attrs, line):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.line = line


class TextNode:
    __slots__ = ('text', 'line')

    def __init__(self, text, line):
        self.text = text
        self.line = line


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ElementNode('#root', {}, 1)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        node = ElementNode(tag, attrs, line)
        self.stack[-1].children.append(node)
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        line = self.getpos()[0]
        node = ElementNode(tag, attrs, line)
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == tag:
                del self.stack[idx:]
                return
        # stray/unmatched end tag: ignore

    def handle_data(self, data):
        if not data:
            return
        line = self.getpos()[0]
        self.stack[-1].children.append(TextNode(data, line))


def elem_children(node):
    return [c for c in node.children if isinstance(c, ElementNode)]


def has_class(node, cls):
    classes = (node.attrs.get('class') or '').split()
    return cls in classes


def flatten_text(node):
    parts = []

    def walk(n):
        if isinstance(n, TextNode):
            parts.append(n.text)
            return
        if n.tag in ('script', 'style'):
            return
        for c in n.children:
            walk(c)

    walk(node)
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()


# --------------------------------------------------------------------------
# Twin extraction (S3)
# --------------------------------------------------------------------------

HEADING_TAGS = {'h1', 'h2', 'h3'}
# Strip a leading enumeration label that only ever appears on the Latin side
# of a heading (version numbers "v1.0 — ", or sub-item letters "a) "), so
# word-position alignment with the Cyrillic side (which never repeats it)
# isn't thrown off by an extra leading token.
LEADING_LABEL_RE = re.compile(r'^\s*(?:[a-zA-Z]\)|v?\d+(?:\.\d+)*\s*[—-])\s*', re.IGNORECASE)


def collect_heading_twins(root):
    twins = []

    def walk(node):
        if isinstance(node, TextNode):
            return
        if node.tag in HEADING_TAGS:
            text = flatten_text(node)
            if ' / ' in text:
                latin, cyr = text.split(' / ', 1)
                cyr = cyr.strip()
                if any(is_cyrillic_char(ch) for ch in cyr):
                    latin = LEADING_LABEL_RE.sub('', latin.strip())
                    twins.append((node.line, latin, cyr))
        for c in node.children:
            walk(c)

    walk(root)
    return twins


def collect_sibling_twins(root):
    twins = []

    def walk(node):
        if isinstance(node, TextNode):
            return
        kids = elem_children(node)
        for i in range(len(kids) - 1):
            a, b = kids[i], kids[i + 1]
            if a.tag in ('p', 'li', 'td') and not has_class(a, 'cyr') \
                    and b.tag == 'p' and has_class(b, 'cyr'):
                latin, cyr = flatten_text(a), flatten_text(b)
                if latin and cyr:
                    twins.append((a.line, latin, cyr))
        for c in node.children:
            walk(c)

    walk(root)
    return twins


BLOCK_TAGS = {'p', 'li', 'h3'}


def collect_bilingual_twins(root):
    twins = []

    def collect_blocks(node):
        blocks = []

        def walk(n):
            if isinstance(n, TextNode):
                return
            if n.tag == 'table':
                return
            if n.tag in BLOCK_TAGS:
                txt = flatten_text(n)
                if txt:
                    blocks.append((n.line, txt))
                return
            for c in n.children:
                walk(c)

        walk(node)
        return blocks

    def walk_root(node):
        if isinstance(node, TextNode):
            return
        if node.tag == 'div' and has_class(node, 'bilingual'):
            kids = elem_children(node)
            if len(kids) >= 2:
                latin_blocks = collect_blocks(kids[0])
                cyr_blocks = collect_blocks(kids[1])
                for (lline, ltext), (_, ctext) in zip(latin_blocks, cyr_blocks):
                    twins.append((lline, ltext, ctext))
        for c in node.children:
            walk_root(c)

    walk_root(root)
    return twins


def classify_header(text):
    low = text.lower()
    if '(lat)' in low or 'латинка' in low:
        return 'lat'
    if '(cyr)' in low or 'кирилиця' in low:
        return 'cyr'
    if any(is_cyrillic_char(ch) for ch in text):
        return 'cyr'
    return 'lat'


def _first_tr(table_node):
    found = []

    def walk(n):
        if found or isinstance(n, TextNode):
            return
        if n.tag == 'tr':
            found.append(n)
            return
        for c in n.children:
            if not found:
                walk(c)

    walk(table_node)
    return found[0] if found else None


def _all_tr(table_node):
    rows = []

    def walk(n):
        if isinstance(n, TextNode):
            return
        if n.tag == 'tr':
            rows.append(n)
            return
        for c in n.children:
            walk(c)

    walk(table_node)
    return rows


def collect_table_twins(root):
    twins = []

    def walk(node):
        if isinstance(node, TextNode):
            return
        if node.tag == 'table':
            header_tr = _first_tr(node)
            if header_tr is not None:
                header_cells = [c for c in elem_children(header_tr) if c.tag in ('th', 'td')]
                if any(c.tag == 'th' for c in header_cells) and header_cells:
                    classes = [classify_header(flatten_text(c)) for c in header_cells]
                    pairs = []
                    n = len(classes)
                    i = 0
                    while i < n:
                        if classes[i] == 'cyr':
                            j = i + 1
                            while j < n and classes[j] == 'lat':
                                pairs.append((i, j))
                                j += 1
                            i = j
                        else:
                            i += 1
                    if pairs:
                        for tr in _all_tr(node):
                            if tr is header_tr:
                                continue
                            cells = [c for c in elem_children(tr) if c.tag in ('td', 'th')]
                            for (ci, cj) in pairs:
                                if ci < len(cells) and cj < len(cells):
                                    cyr_txt = flatten_text(cells[ci])
                                    lat_txt = flatten_text(cells[cj])
                                    if cyr_txt and lat_txt:
                                        twins.append((tr.line, lat_txt, cyr_txt))
            return  # tables don't nest here; skip descending further
        for c in node.children:
            walk(c)

    walk(root)
    return twins


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------

class Finding:
    __slots__ = ('file', 'line', 'rule', 'message')

    def __init__(self, file, line, rule, message):
        self.file = file
        self.line = line
        self.rule = rule
        self.message = message

    def as_dict(self):
        return {'file': self.file, 'line': self.line, 'rule': self.rule, 'message': self.message}


def compare_twin(relpath, line, latin_text, cyr_text, v1_page, lexicon):
    findings = []
    latin_words = WORD_RE.findall(latin_text)
    cyr_words = WORD_RE.findall(cyr_text)
    for lw, cw in zip(latin_words, cyr_words):
        expected = strip_accents(transliterate(strip_combining(cw)))
        if v1_page:
            if any(ch in ACCENT_CHARS for ch in lw):
                findings.append(Finding(relpath, line, 'S1',
                                         f"stress mark not allowed on /spec/v1/: '{lw}'"))
            observed = lw
        else:
            observed = strip_accents(lw)
        if observed != expected:
            if not v1_page and lexicon.get(cw.lower()) == observed.lower():
                continue
            findings.append(Finding(
                relpath, line, 'TWIN',
                f"'{cw}' -> expected '{expected}', found '{observed}'"))
    return findings


def check_char_rules(relpath, root):
    findings = []

    def check_word(line, word):
        has_latin = any(ch.isalpha() and unicodedata.name(ch, '').startswith('LATIN') for ch in word)
        has_cyr = any(is_cyrillic_char(ch) for ch in word)
        if has_latin and has_cyr:
            bad = ''.join(sorted({ch for ch in word if is_cyrillic_char(ch)}))
            findings.append(Finding(relpath, line, 'S4',
                                     f"Cyrillic character(s) '{bad}' inside Latin word '{word}'"))
        if has_latin and not has_cyr:
            bad_chars = ''.join(sorted({ch for ch in word if ch.isalpha() and ch not in ALLOWED_LATIN}))
            if bad_chars:
                findings.append(Finding(
                    relpath, line, 'S4',
                    f"character(s) '{bad_chars}' outside the §1 inventory in '{word}'"))
            has_diacritic = any(ch.lower() in DIACRITIC_LETTERS for ch in word)
            if has_diacritic and any(a in word for a in APOSTROPHE_CHARS):
                findings.append(Finding(relpath, line, 'S4',
                                         f"apostrophe inside Ukrainian Latin word '{word}'"))
            acute_count = sum(1 for ch in word if ch in ACCENT_CHARS)
            if acute_count > 1:
                findings.append(Finding(relpath, line, 'V21-3',
                                         f"more than one stress mark in '{word}'"))

    def walk(node):
        if isinstance(node, TextNode):
            for m in WORD_RE.finditer(node.text):
                check_word(node.line, m.group(0))
            return
        if node.tag in ('code', 'script', 'style'):
            return
        for c in node.children:
            walk(c)

    walk(root)
    return findings


def fixable_words(root):
    """Words containing a fixable S4 mistake: Cyrillic ї/Ї mixed into a Latin
    word, or the invalid diacritic ľ/Ľ. Returns (line, original_word, fixed_word)."""
    out = []

    def scan(node):
        if isinstance(node, TextNode):
            for m in WORD_RE.finditer(node.text):
                word = m.group(0)
                has_latin = any(ch.isalpha() and unicodedata.name(ch, '').startswith('LATIN') for ch in word)
                fixed = word.replace('ї', 'ï').replace('Ї', 'Ï').replace('ľ', 'l').replace('Ľ', 'L')
                if has_latin and fixed != word:
                    out.append((node.line, word, fixed))
            return
        if node.tag in ('code', 'script', 'style'):
            return
        for c in node.children:
            scan(c)

    scan(root)
    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def load_lexicon():
    if not LEXICON_PATH.exists():
        return {}
    data = json.loads(LEXICON_PATH.read_text(encoding='utf-8'))
    return {nfc(k.lower()): nfc(v.lower()) for k, v in data.items() if not k.startswith('_')}


def parse_file(raw):
    raw = nfc(raw)
    text = preprocess(raw)
    builder = TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


def check_file(path, lexicon):
    relpath = path.relative_to(REPO_ROOT).as_posix()
    raw = path.read_text(encoding='utf-8')
    root = parse_file(raw)
    v1_page = is_v1_page(path)

    twins = []
    twins += collect_heading_twins(root)
    twins += collect_sibling_twins(root)
    twins += collect_bilingual_twins(root)
    twins += collect_table_twins(root)

    findings = []
    for line, latin_text, cyr_text in twins:
        findings += compare_twin(relpath, line, latin_text, cyr_text, v1_page, lexicon)
    findings += check_char_rules(relpath, root)
    return findings, root


def run_check():
    lexicon = load_lexicon()
    all_findings = []
    for path in pages():
        findings, _ = check_file(path, lexicon)
        all_findings.extend(findings)
    return all_findings


def run_fix_chars():
    changes = defaultdict(list)
    for path in pages():
        raw = nfc(path.read_text(encoding='utf-8'))
        root = parse_file(raw)
        fixes = fixable_words(root)
        if not fixes:
            continue
        lines = raw.split('\n')
        for line_no, word, fixed in fixes:
            idx = line_no - 1
            if 0 <= idx < len(lines) and word in lines[idx]:
                lines[idx] = lines[idx].replace(word, fixed)
                changes[path].append((line_no, word, fixed))
        path.write_text('\n'.join(lines), encoding='utf-8')
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(description='Evropéïća site spellchecker (RULEBOOK §6)')
    parser.add_argument('--json', action='store_true', help='emit machine-readable JSON')
    parser.add_argument('--fix-chars', action='store_true',
                         help='rewrite unambiguous S4 character substitutions in place')
    args = parser.parse_args(argv)

    if args.fix_chars:
        changes = run_fix_chars()
        total = sum(len(v) for v in changes.values())
        for path, fixes in changes.items():
            relpath = path.relative_to(REPO_ROOT).as_posix()
            for line_no, word, fixed in fixes:
                print(f"{relpath}:{line_no}  FIXED  '{word}' -> '{fixed}'")
        print(f"{total} substitution(s) applied across {len(changes)} file(s)")
        return 0

    findings = run_check()
    findings.sort(key=lambda f: (f.file, f.line))

    if args.json:
        print(json.dumps([f.as_dict() for f in findings], ensure_ascii=False, indent=2))
        return 1 if findings else 0

    by_file = defaultdict(list)
    for f in findings:
        by_file[f.file].append(f)

    for file in sorted(by_file):
        for f in by_file[file]:
            print(f"{f.file}:{f.line}  [{f.rule}]  {f.message}")

    print()
    print("Findings per file:")
    for file in sorted(by_file):
        print(f"  {file}: {len(by_file[file])}")

    rule_counts = Counter(f.rule for f in findings)
    print("Findings by rule:")
    for rule, count in rule_counts.most_common():
        print(f"  {rule}: {count}")

    print(f"Total: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
