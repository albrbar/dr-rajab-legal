---
name: metricool-scheduling
description: Exact procedure to schedule clinic posts in Metricool (blogId 6495522) as drafts for approval. Use before any createScheduledPost call.
---
# الجدولة في Metricool
1. getBrandSettings للتأكد من الشبكات والتوقيت.
2. getBestTimeToPostByNetwork إن لم يحدد المستخدم وقتاً.
3. createScheduledPost مع: draft:true، autoPublish:true، publicationDate بتوقيت Africa/Tripoli، providers، وnetworkData لكل شبكة (facebookData {type:"POST"}، tiktokData {privacyOption:"PUBLIC_TO_EVERYONE", isAigc حسب الحالة}).
4. تيك توك يحتاج صورة/فيديو؛ إنستغرام غير متصل.
5. أعطِ المستخدم plannerUrl لكل منشور.
