import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync(new URL('../dist/index.html', import.meta.url), 'utf8');
if (!html.includes('<body>')) throw new Error('Unexpected generated HTML structure');
writeFileSync(new URL('../dist/bigben-preview.html', import.meta.url), html.replace('<body>', '<body data-standalone="true">'));
console.log('Standalone preview exported to dist/bigben-preview.html (no backend needed).');
