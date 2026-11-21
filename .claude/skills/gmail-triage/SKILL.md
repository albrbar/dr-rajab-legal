---
name: gmail-triage
description: Triage and clean the owner's Gmail at scale — labels, bulk classification, junk removal. Use for any request about inbox backlog, ads/automated mail, important vs private mail, or deleting junk. Prefer the Apps Script path for bulk; use the MCP path only for small batches.
---
# تصنيف Gmail وتنظيفه

## المبدأ
موصل Gmail MCP لا يملك: عمليات جماعية، ولا `nextPageToken`، ولا `labelIds` في النتائج. كل محادثة = استدعاء. لذلك:

| الحجم | الأداة | الكلفة |
|---|---|---|
| أكثر من ~100 محادثة / تنظيف شامل / تشغيل دوري | **Apps Script** `tools/gmail/triage.gs` (يعمل في حساب المالك) | صفر توكن؛ 100 محادثة لكل استدعاء |
| دفعة صغيرة أو حالة غامضة | MCP عبر وكيل `haiku` | استدعاء لكل محادثة |

## الهيكل (labels)
| Label | ID في MCP | المعنى | الحذف |
|---|---|---|---|
| `Auto/1-Junk-ForDelete` | Label_17 | إعلانات، نشرات، تنبيهات وظائف، تسويق بارد، إشعارات تلقائية | **يُنقل إلى Trash** (قابل للاسترجاع 30 يومًا) |
| `Auto/2-Work-Useful` | Label_18 | عمل: Business Profile، Calendar، GitHub/Vercel/Notion/Metricool… | لا |
| `Auto/3-Private` | Label_19 | أشخاص، عائلة، رسائل المالك لنفسه | لا |
| `Auto/4-Accounts-Security` | Label_20 | أمان، تحقق، فواتير، مدفوعات، بنوك | **لا يُحذف أبدًا** |
| `Auto/5-Review` | Label_21 | غامض: قرار المالك | لا |

## قواعد صارمة
1. التصنيف **بالمرسل والفئة فقط**؛ لا تُقرأ نصوص الرسائل (خصوصية). `get_thread` ممنوع في التصنيف.
2. الحذف = `Trash` فقط، وعلى `Auto/1` فقط، وليس لما عليه label آخر من الهيكل أو نجمة. لا حذف نهائيًا.
3. لا تخمّن بين العمل والخاص: غامض ← `Auto/5-Review`.
4. المجلدات اليدوية للمالك (Work, Personal, مخزن, GRE, Travel…): أي محادثة عليها label غير `Auto/*` تُتخطى في التصنيف والحذف، والفحص بقراءة مجلدات المحادثة (`isManual_`) لا بالاستعلام، لأن `label:personal` في بحث Gmail يطابق تبويب Primary.
5. لا إرسال ولا رد ولا مسودات من هذا المسار.

## طريقة MCP (للدفعات الصغيرة)
الموصل لا يرقّم الصفحات، فاستخدم **حلقة الاستثناء**: كل محادثة تأخذ label فتخرج من الاستعلام، فتعيد الدورة التالية دفعة جديدة.
```
in:inbox <scope> -label:auto-1-junk-fordelete -label:auto-2-work-useful -label:auto-3-private -label:auto-4-accounts-security -label:auto-5-review -label:work -label:مخزن
```
- `pageSize=50`، `view=THREAD_VIEW_METADATA_ONLY`، ثم `label_thread` متوازية لكل نتيجة، وكرّر حتى `{}`.
- اسم label المتداخل في البحث: صغيرة وتحويل المسافة و`/` إلى `-`.
- `category:primary` لا يعمل في الموصل؛ استخدم `-category:promotions -category:social -category:updates -category:forums`.
- كل وكيل حتى 6 دورات (~300 محادثة) لتفادي امتلاء السياق.

## طريقة Apps Script (للحجم الكبير)
الخطوات للمالك: script.google.com ← مشروع جديد ← لصق `tools/gmail/triage.gs` ← تشغيل `classifyAll` ← `previewTrash` ← مراجعة ← `trashJunk` ← (اختياري) `installDailyTrigger`.
القواعد في ثابت `RULES` أعلى الملف؛ عدّلها عند ظهور مرسل جديد بدل تصنيفه يدويًا.

## تقرير الإنجاز
جدول: عدد لكل label، عدد المراجعة مع أبرز المرسلين، ما نُقل إلى Trash.
