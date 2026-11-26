// Usage: node tools/poster/render.js <spec.json> [outDir]
// Renders one poster spec into the requested formats (PNG/JPEG for social, PDF for print).
// Gates: phone must match content/facts.md verbatim; title <= 7 words for social formats.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const QR = require('./node_modules/qrcode');

const ROOT = path.resolve(__dirname, '../..');
const FORMATS = {
  square:   { w: 1080, h: 1080, type: 'png' },   // Facebook feed 1:1
  portrait: { w: 1080, h: 1350, type: 'png' },   // Facebook/Instagram 4:5
  story:    { w: 1080, h: 1920, type: 'jpeg' },  // TikTok/Story 9:16 (TikTok photos = JPEG)
  a4:       { w: 794,  h: 1123, pdf: 'A4' },     // print, clinic wall
  a3:       { w: 1123, h: 1587, pdf: 'A3' },     // print, large sign
};

(async () => {
  const specPath = process.argv[2];
  if (!specPath) { console.error('usage: render.js <spec.json> [outDir]'); process.exit(2); }
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const outDir = path.resolve(process.argv[3] || path.join(ROOT, 'media/posters'));
  fs.mkdirSync(outDir, { recursive: true });
  const slug = spec.slug || path.basename(specPath, '.json');
  const errors = [];

  // clinic block from clinics.json, verified against content/facts.md
  if (spec.clinic) {
    const clinics = JSON.parse(fs.readFileSync(path.join(__dirname, 'clinics.json'), 'utf8'));
    const c = clinics[spec.clinic];
    if (!c) errors.push(`unknown clinic "${spec.clinic}" (use: ${Object.keys(clinics).join(', ')})`);
    else {
      const facts = fs.readFileSync(path.join(ROOT, 'content/facts.md'), 'utf8');
      if (!facts.includes(c.phone)) errors.push(`phone ${c.phone} not found in content/facts.md`);
      spec.clinic = c;
    }
  }
  const formats = spec.formats || ['square', 'portrait', 'story'];
  const words = (spec.title || '').replace(/\*/g, '').trim().split(/\s+/).filter(Boolean).length;
  if (formats.some(f => !FORMATS[f]?.pdf) && words > 7) errors.push(`title has ${words} words; social max is 7`);
  for (const f of formats) if (!FORMATS[f]) errors.push(`unknown format "${f}"`);
  if (errors.length) { console.error('REJECTED:\n- ' + errors.join('\n- ')); process.exit(1); }

  if (spec.qrUrl) spec.qr = await QR.toDataURL(spec.qrUrl, { margin: 1, width: 600, errorCorrectionLevel: 'M' });

  const browser = await chromium.launch();
  for (const f of formats) {
    const F = FORMATS[f];
    const page = await browser.newPage({ viewport: { width: F.w, height: F.h }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.join(__dirname, 'template.html'));
    await page.evaluate(s => render(s), { ...spec, w: F.w, h: F.h });
    await page.evaluate(() => document.fonts.ready);
    // overflow check: content must fit the canvas
    const k = await page.evaluate(() => fit());
    if (k < 0) { console.error(`REJECTED ${f}: text does not fit even at 55% — shorten it`); process.exitCode = 1; await page.close(); continue; }
    if (k < 0.8) console.warn(`WARN ${f}: text shrunk to ${Math.round(k * 100)}% — consider shorter copy`);
    const out = path.join(outDir, `${slug}-${f}.${F.pdf ? 'pdf' : F.type === 'jpeg' ? 'jpg' : 'png'}`);
    if (F.pdf) await page.pdf({ path: out, format: F.pdf, printBackground: true, pageRanges: '1', margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    else await page.locator('#p').screenshot({ path: out, type: F.type, ...(F.type === 'jpeg' ? { quality: 92 } : {}) });
    console.log('OK', path.relative(ROOT, out));
    await page.close();
  }
  await browser.close();
})();
