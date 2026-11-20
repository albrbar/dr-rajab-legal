# خريطة البدائل (استمرارية العمل)
كل قدرة لها مزوّد أساسي وبدائل. إذا ضرب المزوّد حدًّا (429، رصيد صفر، حد شهري، انقطاع) **ينتقل الوكيل فورًا للبديل التالي** ولا يعيد المحاولة مع نفس المزوّد أكثر من مرة، ويسجّل التبديل في `ledger.json` (`skipped` أو `notes`). القواعد الطبية والخصوصية واحدة مع كل مزوّد.

| القدرة | الأساسي | البديل 1 | البديل 2 | البديل الأخير | الحالة |
|---|---|---|---|---|---|
| بحث الويب | Parallel (مجاني) | Exa | Firecrawl (رصيد) | WebSearch المدمج | ✅ 4 |
| قراءة صفحة | Parallel web_fetch | Exa web_fetch | Firecrawl scrape | WebFetch المدمج | ✅ 4 |
| بحث عميق/تقرير | Perplexity (حساب المالك) | Exa agent_run | Firecrawl agent (رصيد) | وكيل `competitor-researcher` بالبحث العادي | ✅ 4 |
| تحليلات TikTok/فيسبوك | Metricool | Windsor.ai Social (TikTok فقط، خطة مجانية) | Supermetrics | — | ✅ 3 |
| جدولة المنشورات | Metricool (مسودات) | Windsor.ai Social | Zapier | — | ✅ 3 |
| ملف Google/الخرائط | Windsor.ai Social (GBP) | — | — | يدوي من المالك | ⚠️ 1 |
| التصميم والصور | Canva | Picsart | Hugging Face | HTML محلي + Playwright | ✅ 4 |
| الفيديو | قالب `tools/video` المحلي | Picsart | Canva (بلا AI) | — | ✅ 3 |
| العروض/المستندات | Google Drive/Docs | Notion | GitHub (`docs/`) | Gamma (رصيد صفر) | ✅ 3 |
| البريد والتنبيه | Gmail | تنبيه الهاتف من المهمة | Zapier | — | ✅ 3 |
| واتساب/رسائل فورية | — | Slack (مربوط، بلا قنوات بعد) | — | البريد + التنبيه | ❌ فجوة |
| التقويم والتذكير | Google Calendar ✅ (مربوط 2026-11-21) | البريد | — | — | ✅ 2 |
| إعلانات TikTok/Meta | TikTok for Business (مربوط، 0 حسابات إعلانية: أنشئ حساب إعلانات TikTok) | AdWhispr (Meta مربوط؛ أبحاث إعلانات المنافسين) | Supermetrics (قراءة) | يدوي من المالك | ⚠️ |

## قاعدة التبديل
1. خطأ حد/رصيد/انقطاع → البديل التالي فورًا.
2. البديل أغلى (رصيد) → لا يُستخدم إلا إذا كانت المهمة ضرورية اليوم، ويُذكر في سطر الاستهلاك.
3. لا بديل متاح → سجّل «محجوب» في البريد واقترح الحل، ولا تخترع نتيجة.

## مهمة باحث الموصل المجاني
أولوية الاقتراح: سد الفجوات (❌) أولًا، ثم القدرات ذات المزوّد الواحد (⚠️ 1)، ثم البقية. يحدّث هذا الجدول في اقتراحاته (عبر المنسق/المبرمج) عند ربط موصل جديد.

## اختبار الموصلات 2026-11-21
يعمل: Gmail، Google Calendar، Drive، Docs، Metricool، Canva، Gamma (رصيد صفر)، Notion، Hugging Face، Picsart (5 رصيد)، Supermetrics، Windsor Social (TikTok)، Windsor.ai (مجاني)، TikTok for Business (0 حسابات إعلان)، Zapier (بلا واتساب)، Parallel، Exa، Firecrawl، AdWhispr، BrowserStack. لم يُختبر: BigQuery (لا مشروع)، Perplexity Computer (يحتاج خيط)، Fiverr (لا حاجة). Slack مربوط بلا قنوات.
