# tools/qa — Smoke test لصفحة الهبوط

```bash
node tools/qa/smoke.js   # ~4 ثوانٍ، بلا إنترنت، exit 1 عند أي FAIL
```

يعتمد على Playwright المثبت مسبقًا (نفس `tools/video/render.js`)، ولا يحتاج `npm install`.

| الفحص | التفاصيل |
|---|---|
| واتساب واتصال لكل عيادة | الرقم في بطاقة كل عيادة وفي قسم الحجز يطابق جدول `content/facts.md` (مصدر الحقيقة)، ولا يوجد رقم واتساب خارجه |
| تتبع المصدر | `?src=tt/fb/yt/gmb` يظهر في نص رسالة واتساب، ويبقى بعد التنقل (sessionStorage)، وبدونه = «الموقع»، والرسالة تذكر اسم العيادة |
| OG / SEO | description، og:title/description/url/image، canonical، twitter:card، و`og-image.jpg` موجود بمقاس 1200×630 |
| الموبايل 390px | لا تمرير أفقي، `lang=ar dir=rtl` في الصفحات الأربع |
| الصفحات القانونية | `privacy.html` و`terms.html` و`404.html`: HTTP 200، title وh1، بلا أخطاء JS، وروابطها موجودة في index |

متى يُشغَّل: بعد أي تعديل على `index.html` أو الصفحات القانونية أو أرقام `content/facts.md`، وقبل الدمج (وكيل `coder`).
عند تغيير رقم عيادة: عدّل `content/facts.md` أولًا، ثم الصفحة، ثم شغّل الاختبار.
