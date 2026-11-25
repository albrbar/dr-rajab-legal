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
 'reel1-signs':[('hook','رجلك تتنمّل؟ ولا تحرق بالليل؟'),('t','تنميل أو حرقان، ولا ما تحسش برجلك'),('t','جرح صغير ما يتحسنش في أيام'),('t','رجلك باردة، ولا لونها تغيّر'),('cta','أي علامة منهم، لا تستنى، كلّمنا')],
 'reel2-myth':[('hook','مريض السكر يمشي حافي في الحوش؟'),('tag','خرافة ❌|السكر يضعّف الإحساس، والخبش الصغير يكبر وانت ما تحسش'),('t','ديما شبشب ولا حذاء مريح، حتى في الحوش'),('cta','عندك سؤال؟ اكتبه في التعليقات ونجاوبك')],
 'reel3-heater':[('hook','الدفاية ممكن تحرق رجلك وانت ما تحسش بيها'),('t','مريض السكر ممكن ما يحسش بالسخونة أو بالحرارة'),('t','ما تحطش رجلك قدام الدفاية، ولا حتى على قربة مية ساخنة'),('t','جرّب المية بمرفق قبل ما تحط رجلك فيها'),('cta','شارك الفيديو مع حد عنده سكر من عيلتك')],
}
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
