// Slide images -> one PDF, one slide per page (LinkedIn document post).
// Usage, from inside a carousel folder:
//   NODE_PATH="<folder-with-node_modules>/node_modules" node carousel-pdf.js [srcDir] [out.pdf]
// Defaults: srcDir = instagram, out = carousel.pdf. Page size comes from the first PNG.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const SRC = process.argv[2] || 'instagram';
const OUT = process.argv[3] || 'carousel.pdf';

function pngSize(buf) {
  if (buf.length > 24 && buf[0] === 0x89 && buf[1] === 0x50) {
    return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  }
  return null;
}

(async () => {
  const dir = fs.existsSync(SRC) ? SRC : '.';
  const files = fs.readdirSync(dir).filter(f => /\.(png|jpe?g)$/i.test(f)).sort();
  if (!files.length) {
    console.error(`No slide images found in ${dir}`);
    process.exit(1);
  }

  const size = pngSize(fs.readFileSync(path.join(dir, files[0]))) || { w: 1080, h: 1350 };

  const imgs = files.map(f => {
    const b64 = fs.readFileSync(path.join(dir, f)).toString('base64');
    const mime = f.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
    return `<img src="data:${mime};base64,${b64}">`;
  }).join('\n');

  const html = `<!doctype html><html><head><style>
    @page { size: ${size.w}px ${size.h}px; margin: 0; }
    * { margin: 0; padding: 0; }
    img { display: block; width: ${size.w}px; height: ${size.h}px; page-break-after: always; }
    img:last-child { page-break-after: auto; }
  </style></head><body>${imgs}</body></html>`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'load' });
  await page.pdf({ path: OUT, width: `${size.w}px`, height: `${size.h}px`, printBackground: true });
  await browser.close();
  console.log(`PDF created: ${OUT} (${files.length} pages, ${size.w}x${size.h})`);
})();
