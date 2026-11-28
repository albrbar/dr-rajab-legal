# ريل «قدم سكري فيها ميكروب» — بطاقات + تركيب. الصوت: scratchpad/abx/final/01..05.wav
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
W,H=1080,1920
BUR=(78,20,34); BUR2=(40,10,18); GOLD=(197,160,89); IVORY=(250,248,245); RED=(220,60,60); GRN=(56,170,110); MUTE=(215,200,200)
FB='/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf'; FR='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'; FN='/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
f=lambda p,s: ImageFont.truetype(p,s,layout_engine=ImageFont.Layout.RAQM)
S='/tmp/claude-0/-home-user-dr-rajab-legal/1cae6b2f-3d46-5bcc-a116-38cb49aff5b2/scratchpad/abx'
M='/home/user/dr-rajab-legal/media'
os.makedirs(f'{S}/cards',exist_ok=True); os.makedirs(f'{S}/seg',exist_ok=True)
logo=Image.open(f'{M}/logo.png').convert('RGBA')
doc=ImageOps.exif_transpose(Image.open(f'{M}/dr-rajab-white-coat.png')).convert('RGB').crop((340,330,1340,1330))
clinic=ImageOps.exif_transpose(Image.open(f'{M}/dr-rajab-clinic-ultrasound.jpg')).convert('RGB').crop((70,20,790,890))

def base(brand=True):
    im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(BUR[i]*(1-t)+BUR2[i]*t) for i in range(3)))
    lg=logo.copy(); lg.thumbnail((120,120)); im.paste(lg,(W-120-50,70),lg)
    if brand: d.text((60,130),'د. رجب البربار',font=f(FR,36),fill=GOLD,anchor='lm',direction='rtl')
    d.text((W/2,235),'معلومة توعوية لا تغني عن الكشف الطبي',font=f(FN,28),fill=MUTE,anchor='mm',direction='rtl')
    return im,d
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font,direction='rtl')<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def block(d,text,font,cy,color=IVORY,maxw=940,lh=1.35):
    ls=wrap(d,text,font,maxw); h=font.size*lh; y=cy-h*len(ls)/2
    for l in ls: d.text((W/2,y+h/2),l,font=font,fill=color,anchor='mm',direction='rtl',stroke_width=3,stroke_fill=(20,5,10)); y+=h
def blister(d,cx,cy,s=1.0,tilt=False):
    w,h=int(520*s),int(300*s); x0,y0=cx-w//2,cy-h//2
    d.rounded_rectangle([x0,y0,x0+w,y0+h],radius=int(36*s),fill=(205,210,218),outline=(150,155,165),width=6)
    for r in range(2):
        for c in range(4):
            px=x0+int(70*s)+c*int(127*s); py=y0+int(80*s)+r*int(140*s)
            d.rounded_rectangle([px-int(46*s),py-int(26*s),px+int(46*s),py+int(26*s)],radius=int(26*s),fill=(240,240,245),outline=(170,175,185),width=3)
            d.pieslice([px-int(46*s),py-int(26*s),px+int(6*s),py+int(26*s)],90,270,fill=(225,235,250))
def cross(d,cx,cy,r,col=RED,w=34):
    d.line([cx-r,cy-r,cx+r,cy+r],fill=col,width=w); d.line([cx-r,cy+r,cx+r,cy-r],fill=col,width=w)
def check(d,cx,cy,r,col=GRN,w=30):
    d.line([cx-r,cy,cx-r//3,cy+r*2//3,cx+r,cy-r*2//3],fill=col,width=w,joint='curve')
def bookmark(d,cx,cy,s=1.0,col=GOLD):
    w,h=int(150*s),int(200*s); x0,y0=cx-w//2,cy-h//2
    d.polygon([(x0,y0),(x0+w,y0),(x0+w,y0+h),(cx,y0+h-int(60*s)),(x0,y0+h)],fill=col)
def circ(im,d,img,s,cx,cy):
    p=img.resize((s,s)); m=Image.new('L',(s,s),0); ImageDraw.Draw(m).ellipse([0,0,s-1,s-1],fill=255)
    im.paste(p,(cx-s//2,cy-s//2),m); d.ellipse([cx-s//2-6,cy-s//2-6,cx+s//2+6,cy+s//2+6],outline=GOLD,width=8)
def chip(d,cx,cy,t,on=True):
    w=420; d.rounded_rectangle([cx-w//2,cy-62,cx+w//2,cy+62],radius=62,fill=GOLD if on else None,outline=GOLD,width=4)
    d.text((cx,cy),t,font=f(FB,50),fill=BUR2 if on else (120,90,90),anchor='mm',direction='rtl')
def save(im,n): im.save(f'{S}/cards/{n}.png')

# 1 الهوك — بلا صورة الدكتور ولا اسمه
im,d=base(brand=False); block(d,'ميكروب في رجلك؟',f(FB,118),560,IVORY,1000); blister(d,W//2,1000,1.2)
block(d,'قدم سكري فيها ميكروب',f(FB,62),1340,GOLD); save(im,'h1')
im,d=base(brand=False); block(d,'ميكروب في رجلك؟',f(FB,118),560,IVORY,1000); blister(d,W//2,1000,1.2)
block(d,'شنو علاجها؟',f(FB,96),1350,GOLD); save(im,'h2')
# 2 الدعوة
im,d=base(); block(d,'عندك السكر؟',f(FB,100),640); block(d,'ولا تعرف حد عنده السكر؟',f(FB,76),860,GOLD); save(im,'c1')
im,d=base(); bookmark(d,W//2,660,1.6); block(d,'احفظ الفيديو',f(FB,110),1000); block(d,'بيفيدك كتير',f(FB,72),1190,GOLD); save(im,'c2')
# 3 التحذير
im,d=base(); block(d,'رد بالك',f(FB,110),470,RED); blister(d,W//2,860,1.1); cross(d,W//2,860,200)
block(d,'تاخذ المضاد الحيوي من غير ما تسأل',f(FB,70),1260); save(im,'w1')
# 4 الطبيب أولاً
im,d=base(); ph=clinic.copy(); ph.thumbnail((620,750)); x=(W-ph.width)//2; im.paste(ph,(x,330)); d.rectangle([x-5,325,x+ph.width+5,330+ph.height+5],outline=GOLD,width=6)
block(d,'ميكروب القدم السكري',f(FB,70),1180,GOLD); block(d,'يبي طبيب يشوف الجرح قبل العلاج',f(FB,66),1340); save(im,'d1')
im,d=base(); check(d,W//2,620,170); block(d,'العلاج يحتاج',f(FB,84),960); block(d,'بروتوكولات خاصة',f(FB,104),1130,GOLD); save(im,'d2')
# 5 الخاتمة — الأعراض تظهر واحد واحد ثم بطاقة الواتساب
items=['جرح','ما يتحسنش','التهاب','انتفاخ']
for k in range(1,5):
    im,d=base(); block(d,'لو رجلك فيها',f(FB,80),430)
    for j,t in enumerate(items): chip(d,W//2,620+j*170,t,j<k)
    save(im,f'e{k}')
im,d=base(); circ(im,d,doc,440,W//2,600)
block(d,'د. رجب البربار',f(FR,72),930); block(d,'طبيب جراحة عامة والقدم السكري',f(FR,46),1030,GOLD)
block(d,'وصل معنا على الواتساب',f(FB,62),1180)
d.rounded_rectangle([150,1260,W-150,1400],radius=70,fill=(37,150,90)); d.text((W/2,1330),'0931210939',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',72),fill=IVORY,anchor='mm')
save(im,'e5')
print('cards ok')

# التركيب: لكل مقطع صوتي بطاقات بنسب زمنية (تقديرية حسب الوقفات)
plan=[('01',[('h1',0.52),('h2',0.48)]),('02',[('c1',0.32),('c2',0.68)]),('03',[('w1',1.0)]),('04',[('d1',0.55),('d2',0.45)]),('05',[('e1',0.14),('e2',0.14),('e3',0.14),('e4',0.14),('e5',0.44)])]
def run(c): subprocess.run(c,shell=True,check=True)
def dur(p): return float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {p}',shell=True))
lst=[]; n=0
for ci,(clip,cards) in enumerate(plan):
    pad=1.6 if ci==len(plan)-1 else 0.2
    run(f'ffmpeg -y -loglevel error -i {S}/final/{clip}.wav -af apad=pad_dur={pad} -ar 44100 -ac 1 {S}/seg/a{clip}.wav')
    D=dur(f'{S}/seg/a{clip}.wav'); t0=0.0
    for k,(card,frac) in enumerate(cards):
        dd=D*frac if k<len(cards)-1 else D-t0
        fr=int(dd*30)+2
        z="min(zoom+0.0007,1.05)" if n%2==0 else "if(eq(on,0),1.05,max(zoom-0.0007,1.0))"
        run(f'ffmpeg -y -loglevel error -loop 1 -i {S}/cards/{card}.png -ss {t0:.3f} -t {dd:.3f} -i {S}/seg/a{clip}.wav -filter_complex "[0:v]scale=1080:1920,zoompan=z=\'{z}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={fr}:s=1080x1920:fps=30,format=yuv420p[v]" -map "[v]" -map 1:a -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -t {dd:.3f} {S}/seg/s{n:02d}.mp4')
        lst.append(f"file 's{n:02d}.mp4'"); t0+=dd; n+=1
open(f'{S}/seg/list.txt','w').write('\n'.join(lst))
out='/home/user/dr-rajab-legal/media/2026-11-28-reel-antibiotic.mp4'
run(f'ffmpeg -y -loglevel error -f concat -safe 0 -i {S}/seg/list.txt -c copy -movflags +faststart {out}')
print(dur(out), os.path.getsize(out)//1024,'KB')
