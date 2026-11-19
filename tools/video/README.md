# قالب الفيديو التوعوي 9:16

1. انسخ `template.html` وعدّل نصوص الأقسام `<section data-a data-b>` (التوقيتات بالثواني، المدة الكلية `T=40`).
2. `mkdir -p f && node render.js "$PWD"` يرندر 1200 إطار في `f/`.
3. الصوت الخلفي ثم الترميز:
```
ffmpeg -f lavfi -i "sine=f=220:d=40" -f lavfi -i "sine=f=277.18:d=40" -f lavfi -i "sine=f=329.63:d=40" -f lavfi -i "sine=f=110:d=40" -filter_complex "[0][1][2][3]amix=inputs=4,tremolo=f=0.25:d=0.5,lowpass=f=900,aecho=0.8:0.7:120|240:0.3|0.2,volume=0.5,afade=t=in:d=2,afade=t=out:st=37:d=3" -ar 44100 pad.m4a
ffmpeg -framerate 30 -i f/%05d.jpg -i pad.m4a -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart -c:a aac -b:a 128k -shortest out.mp4
```
