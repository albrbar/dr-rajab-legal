# DRAB COMMANDER BOT — مواصفات v0.1 (مقترح، بانتظار الاعتماد)
## المعمارية المجانية
| الطبقة | الاختيار | التكلفة |
|---|---|---|
| واجهة | Telegram Bot API | 0 |
| تشغيل | Cloudflare Workers (webhook فوري) أو GitHub Actions (كل 5–15 د) | 0 |
| طابور المهام | GitHub Issues بوسوم drab-task / needs-approval / done | 0 |
| منفّذ | مهمة Claude Code مجدولة تقرأ Issues وتعلّق بالنتيجة | ضمن الاشتراك |
## الأوامر
/task · /status · /report · /research · /decide · /approve · /reject (الأخيران للدكتور فقط)
## الأمان
قائمة معرّفات مسموحة · أي إجراء خارجي يحتاج /approve · فلتر بيانات المرضى · الأسرار في Cloudflare/GitHub Secrets لا في المستودع · كل أمر يُسجَّل Issue.
## مطلوب من صاحب المشروع
Token من @BotFather (لا يُرسل في المحادثة) · اختيار Cloudflare أو GitHub Actions · GitHub fine-grained token لمستودع واحد · معرّفات Telegram والمجموعة · اعتماد مستودع الكود.
## الحدود
Claude Code لا يعمل دائماً (مجدول، حد أسبوعي) · البوت لا يربط ChatGPT/Gemini تلقائياً.
