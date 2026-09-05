import { defineConfig } from 'astro/config';

// GitHub Pages project site: https://akrivonos.github.io/evropeica/
// To move to an org/user site (evropeica.github.io) or a custom domain, set
// `site` to that origin and `base` to '/'. All internal links go through
// src/lib/url.ts, so nothing else changes.
export default defineConfig({
  site: 'https://akrivonos.github.io',
  base: '/evropeica',
});
