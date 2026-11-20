---
name: video-editing-pipeline
description: Exact ffmpeg/Picsart workflow to turn raw clinic footage into a TikTok-ready 9:16 video with Arabic captions, hook, logo and per-clinic end card. Use for any montage task.
---
# خط إنتاج المونتاج

## 1. الاستلام
- Drive `download_file_content` حدّه 10MB؛ الأكبر يُطلب تصغيره (Clipchamp 720p/480p أو واتساب).
- الملف يُحفظ في tool-results؛ انسخه إلى مجلد عمل جديد في scratchpad.
- `ffprobe` للمدة والأبعاد والصوت.

## 2. فحص الخصوصية (إلزامي قبل أي تعديل)
`ffmpeg -i in.mp4 -vf "fps=1,scale=320:-2,tile=5x4" sheet.jpg` ثم افحص كل لقطة: وجه، اسم، سوار، ورقة، شاشة. سجّل الثواني.
- تغبيش منطقة: `-vf "boxblur=20:enable='between(t,A,B)'"` مع crop/overlay للمنطقة، أو قص المقطع.

## 3. المونتاج
- القص: `-ss START -to END`، احذف الصمت في البداية (الكلام من أول ثانية).
- 9:16 1080x1920: `scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x123c46` (أو crop إن كان التصوير أفقياً).
- الصوت: `loudnorm=I=-14:TP=-1.5:LRA=11` + `highpass=f=80,afftdn`.
- الخطّاف (أول 3 ث): drawtext بخط عربي يدعم التشكيل (Noto Naskh/Kufi Arabic؛ تحقق من التثبيت بـ fc-list) على شريط شبه معتم أعلى الإطار، بعيداً عن منطقة واجهة تيك توك (أسفل 20% ويمين 15%).
- الترجمة: Picsart `picsart_media_transcribe` → راجع النص (اللهجة الليبية) → ملف .ass بخط عربي، حجم 54–64، حواف داكنة → `-vf ass=subs.ass`. **يرسَل النص للمستخدم للتصحيح قبل الحرق.**
- اللوحة الختامية (2–3 ث): الشعار الرسمي + «للحجز: رقم المصحة المعنية» + اسم المصحة. لا رقم عام.
- لصور الجروح: لوحة أولى «محتوى طبي – صور جروح» ثانيتان، وسطر ختامي «النتائج تختلف من حالة لأخرى، والعلاج يُحدَّد بعد الكشف».

## 4. التصدير
`-c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -movflags +faststart`، المدة ≤ 60 ث (يفضل 15–25).

## 5. التحقق والتسليم
- صورة معاينة من 3 نقاط (بداية/وسط/نهاية) وافحص النص العربي (اتجاه، اتصال الحروف).
- ارفع إلى Drive (create_file، base64Content بمرجع sha256:path، disableConversionToGoogleType:true، parentId المجلد).
- أعد: المعرّف، المدة، الحجم، ما تم، ما ينقص، وأي ملاحظات خصوصية.
