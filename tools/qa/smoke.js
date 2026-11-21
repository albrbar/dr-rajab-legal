#!/usr/bin/env node
// Smoke test for the landing page. Usage: node tools/qa/smoke.js
// Source of truth for clinic numbers: content/facts.md. Exit code 1 on any failure.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '../..');
const PAGES = ['index.html', 'privacy.html', 'terms.html', '404.html'];
const SITE = 'https://albrbar.github.io/dr-rajab-legal/';
const MOBILE = { width: 390, height: 844 };
const SOURCES = { tt: 'تيك توك', fb: 'فيسبوك', yt: 'يوتيوب', gmb: 'خرائط Google' };

const results = [];
const check = (name, ok, detail = '') => results.push({ name, ok: !!ok, detail });

// --- clinics from content/facts.md: | name | area | days | time | 09xxxxxxxx |
function readClinics() {
  const md = fs.readFileSync(path.join(ROOT, 'content/facts.md'), 'utf8');
  const rows = [];
  for (const line of md.split('\n')) {
    const cells = line.split('|').map((c) => c.trim());
    const phone = cells[5];
    if (!/^09\d{8}$/.test(phone || '')) continue;
    const name = cells[1].replace(/\*\*/g, '').split(/\s[—(]/)[0].trim();
    rows.push({ name, phone, intl: '218' + phone.slice(1) });
  }
  return rows;
}

// --- static server so location/sessionStorage behave like production
function serve() {
  const types = { '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg', '.png': 'image/png', '.css': 'text/css', '.js': 'text/javascript', '.xml': 'application/xml', '.txt': 'text/plain' };
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p.endsWith('/')) p += 'index.html';
    const file = path.join(ROOT, path.normalize(p));
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404, { 'content-type': types['.html'] });
      return res.end(fs.readFileSync(path.join(ROOT, '404.html')));
    }
    res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(fs.readFileSync(file));
  });
  return new Promise((r) => server.listen(0, '127.0.0.1', () => r(server)));
}

async function newPage(ctx, errors) {
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(e.message));
  return page;
}

(async () => {
  const clinics = readClinics();
  check('facts.md: clinic numbers parsed', clinics.length >= 4, `${clinics.length} clinics`);

  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: MOBILE, isMobile: true, hasTouch: true });
  // Offline and deterministic: only the local server is reachable.
  await ctx.route('**/*', (route) => (route.request().url().startsWith(base) ? route.continue() : route.abort()));

  try {
    // 1) WhatsApp + tel links per clinic
    const errors = [];
    const page = await newPage(ctx, errors);
    await page.goto(base + 'index.html', { waitUntil: 'load' });
    const blocks = await page.$$eval('article, .booking-item', (els) =>
      els.map((el) => ({
        title: el.querySelector('h3')?.textContent.trim() || '',
        wa: [...el.querySelectorAll('a[href*="wa.me/"]')].map((a) => a.href),
        tel: [...el.querySelectorAll('a[href^="tel:"]')].map((a) => a.getAttribute('href')),
      }))
    );
    for (const c of clinics) {
      const mine = blocks.filter((b) => b.title.includes(c.name));
      const wa = mine.flatMap((b) => b.wa);
      const tel = mine.flatMap((b) => b.tel);
      check(`WhatsApp ${c.name}`, wa.length > 0 && wa.every((h) => h.includes(`wa.me/${c.intl}?`)), wa.length ? '' : 'no WhatsApp link found');
      check(`tel ${c.name}`, tel.length > 0 && tel.every((h) => h === `tel:+${c.intl}`), tel.join(' '));
    }
    const allowed = new Set(clinics.map((c) => c.intl));
    const allWa = await page.$$eval('a[href*="wa.me/"]', (as) => as.map((a) => a.href));
    const stray = allWa.filter((h) => !allowed.has((h.match(/wa\.me\/(\d+)/) || [])[1]));
    check('No WhatsApp number outside facts.md', stray.length === 0, stray.join(' '));
    check('No JS errors on index', errors.length === 0, errors.join(' | '));
    await page.close();

    // 2) Source tracking: ?src=... ends up in the prefilled WhatsApp text
    const waText = async (p) =>
      p.$$eval('a[href*="wa.me/"]', (as) => as.map((a) => new URL(a.href).searchParams.get('text') || ''));
    for (const [src, label] of Object.entries(SOURCES)) {
      const p = await newPage(ctx, []);
      await p.goto(`${base}index.html?src=${src}`, { waitUntil: 'load' });
      const texts = await waText(p);
      check(`src=${src} → "${label}"`, texts.length && texts.every((t) => t.includes(`(المصدر: ${label})`)), texts[0]);
      await p.close();
    }
    {
      const p = await newPage(ctx, []);
      await p.goto(`${base}index.html?src=tt`, { waitUntil: 'load' });
      await p.goto(`${base}index.html`, { waitUntil: 'load' });
      const texts = await waText(p);
      check('src kept across navigation (sessionStorage)', texts.every((t) => t.includes('(المصدر: تيك توك)')), texts[0]);
      const withClinic = (await p.$$eval('article a[href*="wa.me/"]', (as) => as.map((a) => ({
        clinic: a.closest('article').querySelector('h3').textContent.trim(),
        text: new URL(a.href).searchParams.get('text') || '',
      })))).every((x) => x.text.includes(x.clinic));
      check('WhatsApp text names the clinic', withClinic);
      await p.close();
    }
    {
      const fresh = await browser.newContext({ viewport: MOBILE });
      await fresh.route('**/*', (route) => (route.request().url().startsWith(base) ? route.continue() : route.abort()));
      const p = await fresh.newPage();
      await p.goto(base + 'index.html', { waitUntil: 'load' });
      const texts = await waText(p);
      check('No src → "الموقع"', texts.every((t) => t.includes('(المصدر: الموقع)')), texts[0]);
      await fresh.close();
    }

    // 3) OG / SEO tags
    {
      const p = await newPage(ctx, []);
      await p.goto(base + 'index.html', { waitUntil: 'load' });
      const meta = await p.evaluate(() => {
        const get = (sel) => document.querySelector(sel)?.getAttribute('content') || '';
        return {
          description: get('meta[name="description"]'),
          title: get('meta[property="og:title"]'),
          ogDesc: get('meta[property="og:description"]'),
          url: get('meta[property="og:url"]'),
          image: get('meta[property="og:image"]'),
          w: get('meta[property="og:image:width"]'),
          h: get('meta[property="og:image:height"]'),
          card: get('meta[name="twitter:card"]'),
          canonical: document.querySelector('link[rel="canonical"]')?.href || '',
        };
      });
      check('meta description', meta.description.length >= 50, `${meta.description.length} chars`);
      check('og:title', meta.title.length > 0, meta.title);
      check('og:description', meta.ogDesc.length > 0);
      check('og:url = canonical = site', meta.url === SITE && meta.canonical === SITE, `${meta.url} | ${meta.canonical}`);
      check('og:image absolute https on site', meta.image.startsWith(SITE), meta.image);
      check('og:image size declared 1200x630', meta.w === '1200' && meta.h === '630', `${meta.w}x${meta.h}`);
      check('twitter:card large image', meta.card === 'summary_large_image', meta.card);
      const local = meta.image.replace(SITE, '');
      const dims = await p.evaluate(async (src) => {
        const img = new Image();
        img.src = src;
        try { await img.decode(); } catch (e) { return null; }
        return [img.naturalWidth, img.naturalHeight];
      }, base + local);
      check(`${local} exists and is 1200x630`, dims && dims[0] === 1200 && dims[1] === 630, dims ? dims.join('x') : 'missing/unreadable');
      await p.close();
    }

    // 4) Mobile 390px without horizontal scroll + RTL, 5) legal pages
    for (const name of PAGES) {
      const errs = [];
      const p = await newPage(ctx, errs);
      const res = await p.goto(base + name, { waitUntil: 'load' });
      await p.waitForTimeout(300);
      const info = await p.evaluate(() => {
        const d = document.documentElement;
        const wide = [...document.body.querySelectorAll('*')]
          .filter((el) => { const r = el.getBoundingClientRect(); return r.width > 0 && (r.right > d.clientWidth + 1 || r.left < -1); })
          .filter((el) => getComputedStyle(el).position !== 'fixed')
          .slice(0, 3)
          .map((el) => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''));
        return { wide, sw: d.scrollWidth, cw: d.clientWidth, dir: d.dir, lang: d.lang, title: document.title, h1: !!document.querySelector('h1') };
      });
      check(`${name}: HTTP 200`, res && res.status() === 200, res && String(res.status()));
      check(`${name}: no horizontal scroll at 390px`, info.sw <= info.cw, `scrollWidth ${info.sw} > ${info.cw}; long unbreakable text or wide element: ${info.wide.join(', ') || 'check overflow-wrap'}`);
      check(`${name}: lang=ar dir=rtl`, info.lang === 'ar' && info.dir === 'rtl', `${info.lang}/${info.dir}`);
      check(`${name}: has <title> and <h1>`, info.title && info.h1, info.title);
      check(`${name}: no JS errors`, errs.length === 0, errs.join(' | '));
      await p.close();
    }
    {
      const p = await newPage(ctx, []);
      await p.goto(base + 'index.html', { waitUntil: 'load' });
      for (const legal of ['privacy.html', 'terms.html']) {
        const n = await p.locator(`a[href="${legal}"]`).count();
        check(`index links to ${legal}`, n > 0);
      }
      await p.close();
    }
  } finally {
    await browser.close();
    server.close();
  }

  const failed = results.filter((r) => !r.ok);
  for (const r of results) console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}${!r.ok && r.detail ? '  — ' + r.detail : ''}`);
  console.log(`\n${results.length - failed.length}/${results.length} passed`);
  process.exit(failed.length ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(2);
});
