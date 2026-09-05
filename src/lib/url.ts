/** Prefix an absolute site path with the configured `base` (GitHub Pages project site). */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return base + path;
}
