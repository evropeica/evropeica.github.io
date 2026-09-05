// Engine conformance test: every case in tests/cases.json must pass through the engine unchanged.
// Run: npm test
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { transliterate } from '../src/lib/transliterate.ts';

const here = dirname(fileURLToPath(import.meta.url));
const cases = JSON.parse(readFileSync(join(here, 'cases.json'), 'utf8'));

let pass = 0, fail = 0;
for (const { cyr, lat, rule } of cases) {
  const got = transliterate(cyr);
  if (got === lat) { pass++; continue; }
  fail++;
  console.log(`FAIL [${rule ?? '-'}] ${cyr}\n   expected: ${lat}\n   got:      ${got}`);
}
console.log(`${pass} passed, ${fail} failed (${cases.length} cases)`);
process.exit(fail ? 1 : 0);
