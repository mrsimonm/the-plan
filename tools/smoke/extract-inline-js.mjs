#!/usr/bin/env node
/* Extract every inline classic <script> from an HTML file so the syntax gate
   can run `node --check` on the app code exactly as the browser sees it.
   Skips <script src=…> and non-JS types (JSON-LD etc). */
import { readFileSync, writeFileSync } from "node:fs";

const [, , htmlPath, outPath] = process.argv;
if (!htmlPath || !outPath) {
  console.error("usage: extract-inline-js.mjs <index.html> <out.js>");
  process.exit(2);
}
const html = readFileSync(htmlPath, "utf8");
const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
const chunks = [];
let m;
while ((m = re.exec(html))) {
  const attrs = m[1];
  if (/\bsrc\s*=/i.test(attrs)) continue;
  const t = /type\s*=\s*["']?([^"'\s>]+)/i.exec(attrs);
  if (t && !/^(text\/javascript|module)$/i.test(t[1])) continue;
  chunks.push(m[2]);
}
if (!chunks.length) {
  console.error(`no inline scripts found in ${htmlPath}`);
  process.exit(2);
}
writeFileSync(outPath, chunks.join("\n;\n"));
console.log(
  `extracted ${chunks.length} inline script(s), ` +
    `${chunks.reduce((a, c) => a + c.length, 0)} bytes -> ${outPath}`
);
