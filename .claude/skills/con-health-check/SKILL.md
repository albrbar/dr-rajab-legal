---
name: con-health-check
description: (مسؤول الموصلات والبنية) Daily connector health check.
---
- استدعاء قراءة خفيف لكل موصل حرج (getBrandSettings، get_connectors، search_files).
- فشل = تقرير بالموصل والخطأ والإجراء.
- ≤ 5 أسطر.
