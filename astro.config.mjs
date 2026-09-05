import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// GitHub Pages organisation site: https://evropeica.github.io/
// Served from the domain root, so `base` is '/'. Internal links go through
// src/lib/url.ts, so moving to a custom domain means changing `site` here
// and adding a CNAME.
export default defineConfig({
  site: 'https://evropeica.github.io',
  base: '/',
  integrations: [sitemap()],
});
