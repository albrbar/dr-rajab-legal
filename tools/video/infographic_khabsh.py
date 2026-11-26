from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
W,H=1080,1350
NAVY=(16,30,64); NAVY2=(26,43,76); GOLD=(197,160,89); IVORY=(250,248,245); RED=(196,62,62); REDBG=(58,30,44); GRN=(46,150,96); GRNBG=(24,58,52)
FB='/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf'; FR='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'; FN='/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
f=lambda p,s: ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
for y in range(H):
    t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(NAVY[i]*(1-t)+NAVY2[i]*t) for i in range(3)))
def wrap(text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font,direction='rtl')<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
# title
lg=Image.open('/home/user/dr-rajab-legal/media/logo.png').convert('RGBA'); lg.thumbnail((110,110)); im.paste(lg,(40,30),lg)
d.text((W/2,175),'خبش صغير في رجلك، لوين ممكن يوصل؟',font=f(FB,46),fill=IVORY,anchor='mm',direction='rtl')
def section(y0,title,items,col,bg,numfont=34):
    tf=f(FB,38); itf=f(FR,33)
    # measure
    blocks=[wrap(t,itf,760) for t in items]
    h=80+sum(len(b)*46+26 for b in blocks)+10
    d.rounded_rectangle([50,y0,W-50,y0+h],radius=28,fill=bg,outline=col,width=4)
    d.text((W-90,y0+45),title,font=tf,fill=col,anchor='rm',direction='rtl')
    y=y0+90
    for i,b in enumerate(blocks):
        cy=y+ (len(b)*46)/2 -6
        d.ellipse([W-140,cy-26,W-88,cy+26],fill=col); d.text((W-114,cy),str(i+1),font=f(FB,numfont),fill=IVORY,anchor='mm')
        for j,l in enumerate(b): d.text((W-165,y+j*46),l,font=itf,fill=IVORY,anchor='ra',direction='rtl')
        y+=len(b)*46+26
    return y0+h
red=['خبش صغير ما تشبحاش وما تحسش بيه','بعد كم يوم يتغير لونه ويقعد أحمر أو ينتفخ','بعد أسبوع ولا أكتر ممكن يلتهب الجرح، ممكن يولي قرحة قدم سكري عميقة','آخر شيء والعياذ بالله إن الإنسان يوصل لمرحلة البتر']
grn=['افحص رجليك كل يوم','لو لقيت خبش في مرحلة مبكرة تمشي للطبيب في أسرع وقت','العلاج سهل والخطر أقل لما أنت تهتم بنفسك']
y=section(215,'لو ما انتبهتش',red,RED,REDBG)
y=section(y+22,'لما تنتبه لروحك',grn,GRN,GRNBG)
# footer with photo
ph=ImageOps.exif_transpose(Image.open('/home/user/dr-rajab-legal/media/dr-rajab-white-coat.png')).convert('RGB')
print(ph.size); ph=ph.crop((340,330,1340,1330)); pass
s=230; ph=ph.resize((s,s)); m=Image.new('L',(s,s),0); ImageDraw.Draw(m).ellipse([0,0,s-1,s-1],fill=255)
fy=y+25
im.paste(ph,(W-60-s,fy),m); d.ellipse([W-60-s-4,fy-4,W-56,fy+s+4],outline=GOLD,width=5)
d.text((W-60-s-25,fy+40),'د. رجب البربار',font=f(FR,40),fill=IVORY,anchor='rm',direction='rtl')
d.text((W-60-s-25,fy+92),'طبيب جراحة عامة والقدم السكري',font=f(FR,28),fill=GOLD,anchor='rm',direction='rtl')
d.rounded_rectangle([W-60-s-25-470,fy+135,W-60-s-25,fy+205],radius=40,fill=GOLD)
d.text((W-60-s-25-235,fy+170),'واتساب 0931210939',font=f(FB,28),fill=NAVY,anchor='mm',direction='rtl')
d.text((W/2,H-30),'معلومة توعوية لا تغني عن الكشف الطبي',font=f(FN,24),fill=(200,205,215),anchor='mm',direction='rtl')
print('bottom of content',fy+s, 'H',H)
im.save('/tmp/claude-0/-home-user-dr-rajab-legal/1cae6b2f-3d46-5bcc-a116-38cb49aff5b2/scratchpad/info/infographic-v2.png')
