import { defineConfig } from 'astro/config';

// GitHub Pages organisation site: https://evropeica.github.io/
// Served from the domain root, so `base` is '/'. Internal links still go
// through src/lib/url.ts, which makes moving to a custom domain later a
// one-line change here.
export default defineConfig({
  site: 'https://evropeica.github.io',
  base: '/',
});
