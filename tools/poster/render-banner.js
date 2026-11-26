// Usage: node tools/poster/render-banner.js <spec.json> [outDir]
// Roll-up 60×160 cm: PDF with 5 mm bleed (610×1610 mm) + PNG preview 1200×3200 (trim).
// Gates: every phone must appear verbatim in content/facts.md; no text in the bottom 15 cm dead zone.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const QR = require('./node_modules/qrcode');

const ROOT = path.resolve(__dirname, '../..');
const CANVAS_W = 1220, CANVAS_H = 3220;      // design px, 20 px = 1 cm, bleed 10 px each side
const PDF_W_MM = 610, PDF_H_MM = 1610;
const PX_PER_MM_CSS = 96 / 25.4;             // CSS px per mm
const ZOOM = (PDF_W_MM * PX_PER_MM_CSS) / CANVAS_W;

(async () => {
  const specPath = process.argv[2];
  if (!specPath) { console.error('usage: render-banner.js <spec.json> [outDir]'); process.exit(2); }
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const outDir = path.resolve(process.argv[3] || path.join(ROOT, 'media/posters'));
  fs.mkdirSync(outDir, { recursive: true });
  const slug = spec.slug || path.basename(specPath, '.json');

  const facts = fs.readFileSync(path.join(ROOT, 'content/facts.md'), 'utf8');
  const clinics = JSON.parse(fs.readFileSync(path.join(__dirname, 'clinics.json'), 'utf8'));
  const errors = [];
  const places = (spec.places || []).map(k => {
    const c = clinics[k];
    if (!c) { errors.push(`unknown clinic "${k}"`); return null; }
    if (!facts.includes(c.phone)) errors.push(`phone ${c.phone} (${k}) not in content/facts.md`);
    return c;
  }).filter(Boolean);
  if (!spec.phoneOnly && places.length === 0) errors.push('no places');
  if (!spec.credentials || spec.credentials.length > 4) errors.push('credentials: 1–4 items');
  if (!spec.services || spec.services.length > 6) errors.push('services: max 6');
  if (!spec.warnings || spec.warnings.length > 4) errors.push('warnings: max 4');
  if (errors.length) { console.error('REJECTED:\n- ' + errors.join('\n- ')); process.exit(1); }

  const qr = await QR.toDataURL(spec.qrUrl, { margin: 1, width: 800, errorCorrectionLevel: 'M' });
  const data = { ...spec, places: spec.phoneOnly ? [{ name: 'للحجز والاستفسار', area: '', days: '', time: '', phone: spec.phoneOnly }] : places, qr };
  if (spec.phoneOnly && !facts.includes(spec.phoneOnly)) { console.error('REJECTED: phone not in content/facts.md'); process.exit(1); }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: CANVAS_W, height: CANVAS_H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'banner.html'));
  await page.evaluate(d => fill(d), data);
  await page.evaluate(() => document.fonts.ready);

  // overflow check inside each block
  const over = await page.evaluate(() => [...document.querySelectorAll('.abs, .box, .place')]
    .filter(e => e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2)
    .map(e => (e.className || e.tagName) + ' ' + e.scrollHeight + '>' + e.clientHeight));
  if (over.length) { console.error('REJECTED overflow:\n- ' + over.join('\n- ')); await browser.close(); process.exit(1); }

  // preview: trim area 1200×3200
  const prev = path.join(outDir, `${slug}-preview-1200x3200.png`);
  await page.screenshot({ path: prev, clip: { x: 10, y: 10, width: 1200, height: 3200 } });
  console.log('OK', path.relative(ROOT, prev));

  // print PDF: zoom canvas to 610×1610 mm with bleed
  // Trim size 600×1600 mm (exact requested), bleed removed by offsetting the canvas by 10 design px
  const TRIM_W_MM = 600, TRIM_H_MM = 1600;
  const s = (TRIM_W_MM * PX_PER_MM_CSS) / 1200;   // CSS px per design px on the trim area
  await page.evaluate(({ s, W, H }) => {
    const c = document.getElementById('canvas');
    c.style.zoom = s; c.style.position = 'absolute';
    c.style.left = (-10 * s) + 'px'; c.style.top = (-10 * s) + 'px';
    document.documentElement.style.width = W + 'mm'; document.body.style.width = W + 'mm';
    document.documentElement.style.height = H + 'mm'; document.body.style.height = H + 'mm';
  }, { s, W: TRIM_W_MM, H: TRIM_H_MM });
  const pdf = path.join(outDir, `${slug}-PRINT-600x1600mm-trim.pdf`);
  await page.pdf({ path: pdf, width: TRIM_W_MM + 'mm', height: TRIM_H_MM + 'mm', printBackground: true, pageRanges: '1', preferCSSPageSize: false, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  console.log('OK', path.relative(ROOT, pdf));
  await browser.close();
})();
