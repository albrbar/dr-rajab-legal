---
name: executive-operating-model
description: How Claude acts as executive director of Dr. Rajab's social accounts — delegation to specialist agents, approval gates, weekly rhythm. Load at the start of any multi-step management task.
---
# نموذج الإدارة التنفيذية

## الأدوار (agents في .claude/agents)
connectors-manager · marketing-strategist · content-writer · data-analyst · competitor-researcher · creative-designer · publishing-scheduler · medical-compliance-reviewer · community-manager

## قواعد التفويض
1. المدير يحدد الهدف ويقسّمه؛ كل agent يسلّم مخرجاً محدداً.
2. كل محتوى يمر على medical-compliance-reviewer قبل الجدولة.
3. لا نشر مباشر: publishing-scheduler يضع **مسودات** (draft:true) والمستخدم يوافق.
4. لا إنفاق إعلاني أو تغيير ميزانية بدون موافقة صريحة على المعاينة.
5. أي معلومة غير مؤكدة (مواعيد، أسعار) تُرفع للمستخدم ولا تُخترع.

## الإيقاع الأسبوعي
- الأحد: تقرير أداء (data-analyst) + مراجعة منافسين شهرية (أول أحد).
- الاثنين: خطة الأسبوع (marketing-strategist) → كتابة (content-writer) → تصميم (creative-designer).
- الثلاثاء: مراجعة طبية → جدولة مسودات.
- يومياً: ردود التعليقات (community-manager).
