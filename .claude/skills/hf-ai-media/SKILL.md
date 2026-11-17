---
name: hf-ai-media
description: Use Hugging Face Spaces for clinic media — background removal of doctor photos, image generation, Arabic text-to-speech voiceovers, OCR. Use for AI media tasks.
---
# Hugging Face
- dynamic_space operation:"discover" لإيجاد المهام، ثم view_parameters ثم invoke.
- إزالة الخلفية لصور الدكتور قبل التصميم.
- TTS عربي لتعليق فيديوهات تيك توك (راجع النطق).
- لا تولّد صوراً لمرضى «حقيقيين» أو صوراً للدكتور لم يلتقطها؛ علّم المحتوى المولد isAiGenerated/isAigc.
