# قالب البوسترات

```bash
cd tools/poster && npm install          # مرة واحدة (qrcode)
node tools/poster/render.js tools/poster/specs/example-kahili.json   # → media/posters/
```

- `template.html` — التصميم (كحلي/ذهبي، خط Cairo محلي، شعار، بطاقة مصحة، QR، تنبيه طبي). يصغّر النص تلقائيًا حتى يتسع.
- `clinics.json` — بيانات المصحات؛ يتحقق `render.js` أن كل رقم موجود حرفيًا في `content/facts.md`. عند تغيير جدول عدّل الملفين معًا.
- الصيغ: `square` `portrait` (PNG) · `story` (JPEG لتيك توك) · `a4` `a3` (PDF طباعة).
- الخط Cairo مرخّص SIL OFL 1.1 (`fonts/OFL.txt`).
