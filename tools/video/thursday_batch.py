import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; D=os.path.dirname(os.path.abspath(__file__))
NAVY=(16,30,64); NAVY2=(26,43,76); GOLD=(197,160,89); IVORY=(250,248,245); RED=(200,70,70)
FB='/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf'; FR='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
def font(p,s): return ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
doc=Image.open(f'{D}/doctor.png').convert('RGBA'); logo=Image.open('/home/user/dr-rajab-legal/media/logo.png').convert('RGBA')
def bg():
    im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
    for y in range(H): 
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(NAVY[i]*(1-t)+NAVY2[i]*t) for i in range(3)))
    return im
def wrap(d,text,f,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=f,direction='rtl')<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def text_block(d,text,f,cy,color=IVORY,maxw=900,lh=1.35):
    lines=wrap(d,text,f,maxw); h=f.size*lh; y=cy-h*len(lines)/2
    for l in lines:
        d.text((W/2,y+h/2),l,font=f,fill=color,anchor='mm',direction='rtl',stroke_width=2,stroke_fill=(8,14,30)); y+=h
def chrome(im,d,idx,total):
    lg=logo.copy(); lg.thumbnail((150,150)); im.paste(lg,(W-150-50,70),lg)
    d.text((80,125),'د. رجب البربار',font=font(FR,38),fill=GOLD,anchor='lm',direction='rtl')
    fs=font(FR,30)
    d.text((W/2,H-95),'معلومة توعوية لا تغني عن الكشف الطبي',font=fs,fill=(200,205,215),anchor='mm',direction='rtl')
    for i in range(total):
        x=W/2+(i-(total-1)/2)*36; d.ellipse([x-8,H-160,x+8,H-144],fill=GOLD if i<=idx else (70,85,120))
def card_hook(text,idx,total):
    im=bg(); d=ImageDraw.Draw(im)
    p=doc.copy().resize((760,760)); m=Image.new('L',(760,760),0); ImageDraw.Draw(m).ellipse([0,0,759,759],fill=255)
    im.paste(p,(160,300),m); d.ellipse([155,295,925,1065],outline=GOLD,width=8)
    text_block(d,text,font(FB,92),1380,IVORY,960)
    chrome(im,d,idx,total); return im
def card_text(text,idx,total,tag=None,tagcolor=GOLD):
    im=bg(); d=ImageDraw.Draw(im)
    d.rounded_rectangle([70,420,W-70,1500],radius=40,fill=(30,50,92),outline=GOLD,width=4)
    if tag: 
        d.text((W/2,620),tag,font=font(FB,150),fill=tagcolor,anchor='mm',direction='rtl')
        text_block(d,text,font(FB,74),1020,IVORY,860)
    else: text_block(d,text,font(FB,80),960,IVORY,860)
    if idx==total-2:
        d.rounded_rectangle([280,1560,W-280,1650],radius=45,outline=GOLD,width=3)
        d.text((W/2,1605),'واتساب 0931210939',font=font(FB,44),fill=GOLD,anchor='mm',direction='rtl')
    chrome(im,d,idx,total); return im
def card_cta(text,idx,total):
    im=bg(); d=ImageDraw.Draw(im)
    p=doc.copy().resize((420,420)); m=Image.new('L',(420,420),0); ImageDraw.Draw(m).ellipse([0,0,419,419],fill=255)
    im.paste(p,(330,330),m); d.ellipse([326,326,754,754],outline=GOLD,width=6)
    text_block(d,text,font(FB,78),1030,IVORY,900)
    d.rounded_rectangle([170,1330,W-170,1490],radius=80,fill=GOLD)
    d.text((W/2,1410),'واتساب 0931210939',font=font(FB,66),fill=NAVY,anchor='mm',direction='rtl')
    chrome(im,d,idx,total); return im
REELS={
 'reel4-daily-check':[('hook','افحص قدمك كل يوم في دقيقة واحدة'),('t','انظر بين الأصابع وتحت الكعب'),('t','استخدم مرآة، أو اطلب من أحد أفراد أسرتك'),('t','ابحث عن جرح أو احمرار أو تشقق أو تغيّر في اللون'),('cta','لاحظت شيئاً؟ لا تنتظر، تواصل معنا')],
 'reel5-shoes':[('hook','حذاؤك قد يجرح قدمك دون أن تشعر'),('t','اختر مقاساً مريحاً بمقدمة واسعة'),('t','افحص داخل الحذاء بيدك قبل لبسه'),('t','لا تمشِ حافياً، حتى داخل البيت'),('cta','شارك الفيديو مع من يهمك')],
 'reel6-nails':[('hook','قصّ الأظافر بطريقة خاطئة قد يسبب جرحاً'),('t','قصّ الظفر بشكل مستقيم، ولا تقصّ الزوايا'),('t','لا تستخدم أدوات حادة لإزالة الجلد القاسي'),('t','إذا كان النظر ضعيفاً، اطلب المساعدة'),('cta','عندك سؤال؟ اكتبه في التعليقات')],
 'reel7-urgent':[('hook','علامات في القدم السكرية لا تحتمل الانتظار'),('t','احمرار أو تورّم يزداد'),('t','رائحة أو إفرازات من الجرح'),('t','حرارة في الجسم مع جرح في القدم'),('cta','هذه حالة عاجلة، راجع الطبيب أو الطوارئ فوراً')],
}

POSTS={
 'post1-daily-check':('فحص القدم اليومي',['بين الأصابع','تحت الكعب','الأظافر','لون الجلد وحرارته']),
 'post2-shoes':('الحذاء المناسب لمريض السكري',['مقاس مريح','مقدمة واسعة','افحصه من الداخل','لا مشي حافياً']),
 'post3-heater':('احذر الحرارة في الشتاء',['لا تقترب من الدفاية','لا قربة ماء ساخن','اختبر الماء بمرفقك','جوارب قطنية دافئة']),
 'post4-urgent':('متى تراجع الطبيب فوراً؟',['جرح لا يلتئم','احمرار أو تورّم','رائحة أو إفرازات','حرارة في الجسم']),
}
def post_img(title,items):
    im=Image.new('RGB',(1080,1350),NAVY); d=ImageDraw.Draw(im)
    for y in range(1350):
        t=y/1350; d.line([(0,y),(1080,y)],fill=tuple(int(NAVY[i]*(1-t)+NAVY2[i]*t) for i in range(3)))
    lg=logo.copy(); lg.thumbnail((130,130)); im.paste(lg,(1080-130-50,50),lg)
    d.text((70,115),'د. رجب البربار',font=font(FR,34),fill=GOLD,anchor='lm',direction='rtl')
    d.text((540,290),title,font=font(FB,70),fill=IVORY,anchor='mm',direction='rtl',stroke_width=2,stroke_fill=(8,14,30))
    d.line([(390,370),(690,370)],fill=GOLD,width=5)
    for i,it in enumerate(items):
        y=470+i*170
        d.rounded_rectangle([90,y,990,y+130],radius=30,fill=(30,50,92),outline=GOLD,width=3)
        d.ellipse([880,y+25,960,y+105],fill=GOLD); d.text((920,y+65),str(i+1),font=font(FB,46),fill=NAVY,anchor='mm')
        d.text((840,y+65),it,font=font(FB,54),fill=IVORY,anchor='rm',direction='rtl')
    d.text((540,1180),'واتساب 0931210939',font=font(FB,46),fill=GOLD,anchor='mm',direction='rtl')
    d.text((540,1270),'معلومة توعوية لا تغني عن الكشف الطبي',font=font(FR,28),fill=(200,205,215),anchor='mm',direction='rtl')
    return im
def ad_img(w,h):
    im=Image.new('RGB',(w,h),NAVY); d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/h; d.line([(0,y),(w,y)],fill=tuple(int(NAVY[i]*(1-t)+NAVY2[i]*t) for i in range(3)))
    s=int(min(w,h)*(0.42 if h>w else 0.34)); p=doc.copy().resize((s,s)); m=Image.new('L',(s,s),0); ImageDraw.Draw(m).ellipse([0,0,s-1,s-1],fill=255)
    top=int(h*0.22) if h>w else int(h*0.06)
    im.paste(p,((w-s)//2,top),m); d.ellipse([(w-s)//2-5,top-5,(w+s)//2+5,top+s+5],outline=GOLD,width=7)
    y=top+s+int(h*0.07)
    d.text((w/2,y),'د. رجب البربار',font=font(FR,int(w*0.075)),fill=IVORY,anchor='mm',direction='rtl'); y+=int(w*0.1)
    d.text((w/2,y),'طبيب جراحة عامة والقدم السكري',font=font(FR,int(w*0.045)),fill=GOLD,anchor='mm',direction='rtl'); y+=int(w*0.11)
    d.text((w/2,y),'الكشف المبكر يقلّل خطر المضاعفات',font=font(FB,int(w*0.05)),fill=IVORY,anchor='mm',direction='rtl'); y+=int(w*0.12)
    bw=int(w*0.7); d.rounded_rectangle([(w-bw)//2,y-int(w*0.06),(w+bw)//2,y+int(w*0.06)],radius=int(w*0.06),fill=GOLD)
    d.text((w/2,y),'احجز عبر واتساب 0931210939',font=font(FB,int(w*0.045)),fill=NAVY,anchor='mm',direction='rtl')
    lg=logo.copy(); lg.thumbnail((int(w*0.12),int(w*0.12))); im.paste(lg,(w-lg.width-30,30),lg)
    d.text((w/2,h-40),'معلومة توعوية لا تغني عن الكشف الطبي',font=font(FR,int(w*0.026)),fill=(200,205,215),anchor='mm',direction='rtl')
    return im
os.makedirs(f'{D}/out',exist_ok=True)
for name,cards in REELS.items():
    if len(sys.argv)>1 and name!=sys.argv[1]: continue
    files=[]
    for i,(k,t) in enumerate(cards):
        if k=='hook': im=card_hook(t,i,len(cards))
        elif k=='cta': im=card_cta(t,i,len(cards))
        elif k=='tag':
            tag,body=t.split('|'); im=card_text(body,i,len(cards),tag.replace(' ❌',''),RED)
        else: im=card_text(t,i,len(cards))
        fn=f'{D}/out/{name}-{i}.png'; im.save(fn); files.append(fn)
    print(name,len(files))

for k,(t,items) in POSTS.items(): post_img(t,items).save(f'{D}/out/{k}.png'); print(k)
ad_img(1080,1080).save(f'{D}/out/ad-1x1.png'); ad_img(1080,1920).save(f'{D}/out/ad-9x16.png'); print('ads')
