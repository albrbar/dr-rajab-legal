---
name: connectors-map
description: Which connector does what for Dr. Rajab's accounts, with account IDs and limits (Windsor, Metricool, Drive, Canva, Gamma, Hugging Face, GitHub). Load before calling any connector.
---
# خريطة الموصلات

| الموصل | الاستخدام | المعرفات / القيود |
|---|---|---|
| Metricool | **النشر والجدولة** + أفضل أوقات النشر + تحليلات | brand/blogId: `6495522`، توقيت Africa/Tripoli. متصل (منذ 19 نوفمبر 2026): فيسبوك صفحة «عيادة د.رجب البربار» (page 1462804010249423)، تيك توك @diabetic_foot_clinic، يوتيوب. إنستغرام وLinkedIn غير متصلين. الصفحة القديمة «د. رجب البربار Dr. Rajab Albarbar» (110705793672475، ~1,405 متابع، متوقفة منذ 10 أكتوبر) لم تعد مربوطة. |
| Windsor.ai (Social) | تحليلات تيك توك | خطة مجانية = حساب واحد: tiktok_organic `_000GY2ltwDaIt45d88meEflzaz5dZcspO9v` (@diabetic_foot_clinic). لا نشر على تيك توك من Windsor. |
| Google Drive | مخزن الأصول | مجلد «صفحة د رجب البربار» `1WXqkYdEV3QapL67BCZv78b3a0CjZLSJ0` |
| Canva | تصاميم قابلة للتعديل | مجلد «صفحة د.رجب البربار» `FAHbN8JOUHY`. لا Brand Kit. |
| Gamma | عروض، بوستات سوشيال، صفحات هبوط | يوجد ملف «TikTok Video Production: Diabetic Foot Clinic» |
| Hugging Face | توليد صور، إزالة خلفية، TTS، OCR | حساب albrbar مجاني |
| GitHub | albrbar/dr-rajab-legal — سياسة الخصوصية والشروط (GitHub Pages) | |
| HubSpot | CRM لتتبع حجوزات واتساب (رسالة ← مريض) | حساب `drab` 49340791، خطة مجانية. Deal pipeline `default` «حجوزات العيادة». لا نشر سوشيال (لا صلاحية). |

## قرار التركيز (19 نوفمبر 2026)
- **المنصة الأساسية: تيك توك — حساب العيادة @diabetic_foot_clinic** (عيادة القدم السكري والتقرحات).
- حساب الدكتور @dr_rajab_albarbar ثانوي؛ لا ننشر عليه إلا بطلب.
- المطلوب: ربط @diabetic_foot_clinic في Metricool بدل حساب الدكتور، وتحويله لحساب Business.

## ملاحظات
- Metricool يحتاج روابط صور عامة؛ صور Drive تعمل فقط إذا رُبط Drive داخل Metricool.
- البحث: Firecrawl و Exa و Parallel Search متصلة (لا Perplexity Search؛ Perplexity Computer لاستيراد اللوحات فقط).
- المرجع الرسمي للمواعيد: Notion https://app.notion.com/p/41ddc8c1ad23814d8f23ceeaacb04d1a
- لا يوجد موصل إعلانات ممولة حالياً (Meta/TikTok Ads).

## HubSpot — تسجيل الحجوزات
- المسجّل: Claude، من رسائل المالك بصيغة «رسالة جديدة: الاسم الأول، المصدر، العيادة».
- الخصوصية: الاسم الأول + المصدر + العيادة + المرحلة فقط. **لا تشخيص، لا صور، لا رقم هاتف، لا تفاصيل طبية.**
- كل حالة = Deal في pipeline `default`. اسم الصفقة: `<الاسم الأول> — <YYYY-MM-DD>`.
- المراحل (dealstage): رسالة جديدة `1496740189` · تم الرد `1496740190` · حجز مؤكد `1496740191` · حضر `1496740192` · لم يحضر/متابعة `1496740193`.
- `lead_source_channel`: tiktok · facebook · landing · referral · other.
- `clinic_location`: kuhaili · vittoria · alsayeh · alrabie · unknown.
- القياس الأسبوعي (`data-analyst`): عدد الصفقات المنشأة = الرسائل؛ الصفقات في «حضر» = المرضى؛ مجمّعة حسب المصدر.
