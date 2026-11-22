import csv, collections, statistics as st, os, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ('/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf','/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'):
    if os.path.exists(f): fm.fontManager.addfont(f)
plt.rcParams['font.family']=['Noto Sans Arabic','DejaVu Sans']
BLUE,ORANGE,AQUA,YEL,INK,MUTED,BG,GRID='#2a78d6','#eb6834','#1baf7a','#eda100','#0b0b0b','#52514e','#fcfcfb','#e6e5e0'
D=os.path.dirname(os.path.abspath(__file__))+'/..'
base={r['id']:r for r in csv.DictReader(open(f'{D}/creators-data.csv',encoding='utf-8'))}
fx={r['id']:r for r in csv.DictReader(open(f'{D}/facebook-extra.csv',encoding='utf-8'))}
tt=list(csv.DictReader(open(f'{D}/tiktok-stats.csv',encoding='utf-8')))
owner={}
for r in tt:
    if r['handle'] and r['status'].startswith('ok'): owner[r['handle']]=max(owner.get(r['handle'],0),int(r['id']))
T={str(i):r for r in tt for h,i in owner.items() if r['handle']==h and r['id']==str(i)}
f=lambda v: float(v) if v not in ('',None) else None
# merged dataset
cols=['id','country','name','group','pattern','profession','gender','language','tiktok_handle','followers','total_likes','videos','median_views','engagement_rate','avg_duration_s','has_whatsapp','top_video_views','fb_followers','patient_footage','booking_cta']
with open(f'{D}/creators-merged.csv','w',newline='',encoding='utf-8') as fo:
    w=csv.writer(fo); w.writerow(cols)
    for i,b in base.items():
        t=T.get(i,{}); x=fx.get(i,{})
        fb=x.get('fb_followers') or b['facebook']
        w.writerow([i,b['country'],b['name'],b['group'],b['pattern'],x.get('profession',''),x.get('gender',''),x.get('language',''),t.get('handle',''),t.get('followers',''),t.get('total_likes',''),t.get('videos',''),t.get('median_views',''),t.get('engagement_rate',''),t.get('avg_duration_s',''),t.get('has_whatsapp',''),t.get('top_video_views',''),fb,x.get('patient_footage',''),x.get('booking_cta','')])
M=[r for r in csv.DictReader(open(f'{D}/creators-merged.csv',encoding='utf-8'))]
V=[r for r in M if f(r['followers']) and f(r['median_views']) is not None]
print('verified tiktok rows',len(V))
def fmt(v): return (f'{v/1e6:.1f}'.replace('.0','')+'M') if v>=1e6 else (f'{round(v/1e3)}K' if v>=1e3 else str(int(v)))
OUT=f'{D}/charts'
def base_fig(h,title,sub):
    fig,ax=plt.subplots(figsize=(10,h),dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    fig.text(.97,1-.25/h,title,ha='right',va='top',fontsize=17,fontweight='bold',color=INK)
    fig.text(.97,1-.62/h,sub,ha='right',va='top',fontsize=11,color=MUTED)
    fig.text(.03,.02,'د. رجب البربار، عيادة القدم السكري، بيانات تيك توك عبر ScrapeCreators 22/11/2026',ha='left',fontsize=9,color=MUTED)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); ax.set_axisbelow(True); return fig,ax
def hbar(name,title,sub,labels,vals,vfmt,colors=None,h=7):
    fig,ax=base_fig(h,title,sub); y=list(range(len(labels)))[::-1]; ax.grid(axis='x',color=GRID,lw=.8)
    ax.barh(y,vals,color=colors or BLUE,height=.62); ax.invert_xaxis(); ax.yaxis.tick_right()
    ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=11.5,color=INK)
    for yi,v in zip(y,vals): ax.text(v,yi,'  '+vfmt(v)+'  ',va='center',ha='right',fontsize=10.5,color=INK)
    ax.set_xticklabels([]); fig.subplots_adjust(left=.07,right=.66,top=1-1.0/h,bottom=.5/h+.02); fig.savefig(f'{OUT}/{name}.png',facecolor=BG); plt.close(fig)
# 6 views per follower
vp=sorted([r for r in V if f(r['followers'])>=5000],key=lambda r:-f(r['median_views'])/f(r['followers']))[:12]
hbar('6-views-per-follower','مين ياخذ مشاهدات أكبر من حجمه','نص المشاهدات لآخر فيديوهات ÷ عدد المتابعين (حسابات فوق 5 آلاف متابع)',[f"{r['name'][:26]}، {r['country']}" for r in vp],[f(r['median_views'])/f(r['followers']) for r in vp],lambda v:f'{v:.2f}',[BLUE if r['group']=='قدم' else ORANGE for r in vp])
# 7 engagement by country
bc=collections.defaultdict(list)
for r in V:
    if f(r['engagement_rate']) is not None: bc[r['country']].append(f(r['engagement_rate']))
items=sorted([(k,st.median(v),len(v)) for k,v in bc.items() if len(v)>=2],key=lambda x:-x[1])
hbar('7-engagement-by-country','نسبة التفاعل حسب الدولة','الوسيط: (إعجابات + تعليقات + مشاركات) ÷ مشاهدات، لآخر 10 فيديوهات',[f'{k} (ن={n})' for k,_,n in items],[m*100 for _,m,_ in items],lambda v:f'{v:.1f}%')
# 8 duration vs views
fig,ax=base_fig(7,'طول الفيديو مقابل المشاهدات','كل نقطة حساب: متوسط طول آخر فيديوهاته ونص مشاهداته'); ax.grid(color=GRID,lw=.8)
ax.set_yscale('log')
for r in V:
    d=f(r['avg_duration_s']); m=f(r['median_views'])
    if d and m and m>0 and d<240: ax.scatter(d,m,s=70,color=BLUE if r['group']=='قدم' else ORANGE,edgecolor=BG,lw=1.5)
ax.axvspan(15,35,color=AQUA,alpha=.08); ax.text(25,ax.get_ylim()[1]*0.7,'15 لـ 35 ثانية',ha='center',fontsize=10,color=MUTED)
ax.set_xlabel('متوسط طول الفيديو (ثانية)',fontsize=11,color=MUTED); ax.set_ylabel('نص المشاهدات',fontsize=11,color=MUTED)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: fmt(v)))
ax.scatter([],[],color=BLUE,label='متخصص قدم'); ax.scatter([],[],color=ORANGE,label='بديل'); ax.legend(frameon=False,loc='upper right')
fig.subplots_adjust(left=.1,right=.95,top=.86,bottom=.12); fig.savefig(f'{OUT}/8-duration-vs-views.png',facecolor=BG); plt.close(fig)
# 9 whatsapp in bio
g={'1':[], '0':[]}
for r in V:
    if r['has_whatsapp'] in g: g[r['has_whatsapp']].append(f(r['median_views']))
lab=[f"فيه رقم أو واتساب في البايو (ن={len(g['1'])})",f"بدون رقم (ن={len(g['0'])})"]
hbar('9-whatsapp-bio','رقم الواتساب في البايو والمشاهدات','نص المشاهدات لكل مجموعة',lab,[st.median(g['1']),st.median(g['0'])],fmt,[AQUA,MUTED],h=4.2)
# 10 profession
P={'surgeon':'جراح','podiatrist':'أخصائي قدم','nurse':'تمريض','GP':'طبيب عام','other':'أخرى'}
bp=collections.defaultdict(list)
for r in V: bp[P.get(r['profession'],'غير معروف')].append(f(r['median_views']))
items=sorted([(k,st.median(v),len(v)) for k,v in bp.items() if len(v)>=2],key=lambda x:-x[1])
hbar('10-profession','المهنة والمشاهدات','نص المشاهدات لآخر الفيديوهات حسب مهنة صانع المحتوى',[f'{k} (ن={n})' for k,_,n in items],[m for _,m,_ in items],fmt,h=5)
# 11 followers vs median views
fig,ax=base_fig(8,'المتابعين مقابل المشاهدات الفعلية','حساب كبير ما يعنيش مشاهدات كبيرة. فوق الخط = مشاهدات أكثر من 10% من المتابعين'); ax.grid(color=GRID,lw=.8)
ax.set_xscale('log'); ax.set_yscale('log')
for r in V:
    fo,m=f(r['followers']),f(r['median_views'])
    if fo>=1000 and m>0: ax.scatter(fo,m,s=70,color=BLUE if r['group']=='قدم' else ORANGE,edgecolor=BG,lw=1.5)
lo,hi=1e3,2e7; ax.plot([lo,hi],[lo*.1,hi*.1],ls='--',color='#a9a8a1',lw=1)
for r in sorted(V,key=lambda r:-f(r['median_views']))[:6]: ax.annotate(r['name'][:20],(f(r['followers']),f(r['median_views'])),xytext=(6,5),textcoords='offset points',fontsize=8.5,color=MUTED)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: fmt(v))); ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,_: fmt(v)))
ax.set_xlabel('المتابعين على تيك توك',fontsize=11,color=MUTED); ax.set_ylabel('نص المشاهدات',fontsize=11,color=MUTED)
ax.scatter([],[],color=BLUE,label='متخصص قدم'); ax.scatter([],[],color=ORANGE,label='بديل'); ax.legend(frameon=False,loc='lower right')
fig.subplots_adjust(left=.1,right=.95,top=.86,bottom=.13); fig.savefig(f'{OUT}/11-followers-vs-views.png',facecolor=BG); plt.close(fig)
# stats summary
def med(k,rows=V): xs=[f(r[k]) for r in rows if f(r[k]) is not None]; return st.median(xs) if xs else None
print('median followers',med('followers'),'median views',med('median_views'),'median ER',med('engagement_rate'),'median dur',med('avg_duration_s'))
print('foot median views',med('median_views',[r for r in V if r['group']=='قدم']),'alt',med('median_views',[r for r in V if r['group']!='قدم']))
print('wa',{k:(len(v),st.median(v)) for k,v in g.items()})
print('prof',items); print('vp',[(r['name'],round(f(r['median_views'])/f(r['followers']),2)) for r in vp[:5]])
