from PIL import Image, ImageDraw, ImageFont, ImageOps
W,H=1080,1920
NAVY=(16,30,64); NAVY2=(26,43,76); GOLD=(197,160,89); IVORY=(250,248,245); RED=(196,62,62); REDBG=(58,30,44); GRN=(46,150,96); GRNBG=(24,58,52)
FB='/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf'; FR='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'; FN='/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
f=lambda p,s: ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
D='/tmp/claude-0/-home-user-dr-rajab-legal/1cae6b2f-3d46-5bcc-a116-38cb49aff5b2/scratchpad/voice/cards'
logo=Image.open('/home/user/dr-rajab-legal/media/logo.png').convert('RGBA')
doc=ImageOps.exif_transpose(Image.open('/home/user/dr-rajab-legal/media/dr-rajab-white-coat.png')).convert('RGB').crop((340,330,1340,1330))
def base(bg=None):
    im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(NAVY[i]*(1-t)+NAVY2[i]*t) for i in range(3)))
    lg=logo.copy(); lg.thumbnail((130,130)); im.paste(lg,(W-130-50,70),lg)
    d.text((60,135),'د. رجب البربار',font=f(FR,38),fill=GOLD,anchor='lm',direction='rtl')
    d.text((W/2,H-90),'معلومة توعوية لا تغني عن الكشف الطبي',font=f(FN,30),fill=(200,205,215),anchor='mm',direction='rtl')
    return im,d
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font,direction='rtl')<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def block(d,text,font,cy,color=IVORY,maxw=900,lh=1.4):
    ls=wrap(d,text,font,maxw); h=font.size*lh; y=cy-h*len(ls)/2
    for l in ls: d.text((W/2,y+h/2),l,font=font,fill=color,anchor='mm',direction='rtl',stroke_width=2,stroke_fill=(8,14,30)); y+=h
def photo(im,d,s,cy):
    p=doc.resize((s,s)); m=Image.new('L',(s,s),0); ImageDraw.Draw(m).ellipse([0,0,s-1,s-1],fill=255)
    x=(W-s)//2; y=cy-s//2; im.paste(p,(x,y),m); d.ellipse([x-6,y-6,x+s+6,y+s+6],outline=GOLD,width=8)
def save(im,n): im.save(f'{D}/{n}.png')
# intro
im,d=base(); photo(im,d,620,760); block(d,'د. رجب البربار',f(FR,84),1230); block(d,'طبيب جراحة عامة مختص في القدم السكري',f(FR,50),1360,GOLD); save(im,'intro')
im,d=base(); photo(im,d,420,620); block(d,'محتوى صحي يهم كل مرضى القدم السكري',f(FB,66),1150); save(im,'content')
im,d=base(); block(d,'خبش صغير في رجلك',f(FB,92),780,IVORY,1000); block(d,'لوين ممكن يوصل؟',f(FB,92),1060,GOLD,1000); save(im,'title')
def step(n,total,text,col,bg,head,name):
    im,d=base()
    d.text((W/2,420),head,font=f(FB,70),fill=col,anchor='mm',direction='rtl')
    d.rounded_rectangle([70,560,W-70,1480],radius=44,fill=bg,outline=col,width=6)
    d.ellipse([W/2-70,600,W/2+70,740],fill=col); d.text((W/2,670),str(n),font=f(FB,80),fill=IVORY,anchor='mm')
    block(d,text,f(FB,72),1090,IVORY,820)
    save(im,name)
red=['خبش صغير ما تشبحاش وما تحسش بيه','بعد كم يوم يتغير لونه ويقعد أحمر أو ينتفخ','بعد أسبوع ولا أكتر ممكن يلتهب الجرح، ممكن يولي قرحة قدم سكري عميقة','آخر شيء والعياذ بالله إن الإنسان يوصل لمرحلة البتر']
grn=['لما تنتبه لروحك، افحص رجليك كل يوم','لو لقيت خبش في مرحلة مبكرة تمشي للطبيب في أسرع وقت','العلاج سهل والخطر أقل لما أنت تهتم بنفسك']
for i,t in enumerate(red): step(i+1,4,t,RED,REDBG,'لو ما انتبهتش',f'red{i+1}')
for i,t in enumerate(grn): step(i+1,3,t,GRN,GRNBG,'لما تنتبه لروحك',f'grn{i+1}')
# landing card
im,d=base(); photo(im,d,360,520)
block(d,'كل حساباتي ورقم الواتساب',f(FB,70),900)
d.rounded_rectangle([90,1020,W-90,1160],radius=70,fill=GOLD)
d.text((W/2,1090),'albrbar.github.io/dr-rajab-legal',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',40),fill=NAVY,anchor='mm')
for i,(t) in enumerate(['فيسبوك','إنستغرام','تيك توك','واتساب']):
    x=W-170-i*245; d.rounded_rectangle([x-105,1240,x+105,1330],radius=45,outline=GOLD,width=3); d.text((x,1285),t,font=f(FR,36),fill=IVORY,anchor='mm',direction='rtl')
block(d,'الرابط في أول تعليق',f(FR,40),1430,(200,205,215)); save(im,'landing')
# share card with infographic
im,d=base()
info=Image.open('/home/user/dr-rajab-legal/reports/2026-11-26/infographic-khabsh-v2.png').convert('RGB'); info.thumbnail((880,1100)); im.paste(info,((W-info.width)//2,260))
block(d,'شارك المقطع مع شخص تحبه',f(FB,64),1480,GOLD)
d.text((W/2,1640),'واتساب 0931210939',font=f(FB,52),fill=IVORY,anchor='mm',direction='rtl'); save(im,'share')
print('ok')
