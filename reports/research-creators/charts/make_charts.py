import csv, collections, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, warnings; warnings.filterwarnings('ignore')
from matplotlib import font_manager as fm
import arabic_reshaper
from bidi.algorithm import get_display
F='/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf'
import os
if not os.path.exists(F): F='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
for f in (F,'/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'): fm.fontManager.addfont(f)
plt.rcParams['font.family']=['Noto Sans Arabic','DejaVu Sans']
fp=fm.FontProperties(family=['Noto Sans Arabic','DejaVu Sans']); fpb=fm.FontProperties(family=['Noto Sans Arabic','DejaVu Sans'],weight='bold')
A=lambda s: str(s)
BLUE,ORANGE,INK,MUTED,BG,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#fcfcfb','#e6e5e0'
rows=list(csv.DictReader(open('/home/user/dr-rajab-legal/reports/research-creators/creators-data.csv',encoding='utf-8')))
num=lambda v: float(v) if v else None
def fmt(v): return f'{v/1e6:.1f}'.replace('.0','')+'M' if v>=1e6 else f'{round(v/1e3)}K'
OUT='/home/user/dr-rajab-legal/reports/research-creators/charts'; os.makedirs(OUT,exist_ok=True)
def base(h,title,sub):
    fig,ax=plt.subplots(figsize=(10,h),dpi=150); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    fig.text(.97,.965,A(title),ha='right',va='top',fontproperties=fpb,fontsize=17,color=INK)
    fig.text(.97,.915,A(sub),ha='right',va='top',fontproperties=fp,fontsize=11,color=MUTED)
    fig.text(.03,.02,A('د. رجب البربار، عيادة القدم السكري، بحث 22/11/2026'),ha='left',fontproperties=fp,fontsize=9,color=MUTED)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); ax.grid(axis='x',color=GRID,lw=.8); ax.set_axisbelow(True)
    return fig,ax
def hbar(name,title,sub,labels,vals,valfmt=str,color=BLUE,h=7):
    fig,ax=base(h,title,sub); y=range(len(labels))[::-1]
    ax.barh(list(y),vals,color=color,height=.62); ax.invert_xaxis(); ax.yaxis.tick_right()
    ax.set_yticks(list(y)); ax.set_yticklabels([A(l) for l in labels],fontproperties=fp,fontsize=12,color=INK)
    for yi,v in zip(y,vals): ax.text(v,yi,'  '+valfmt(v)+'  ',va='center',ha='right',fontsize=11,color=INK)
    ax.set_xticklabels([]); fig.subplots_adjust(left=.06,right=.70 if max(len(l) for l in labels)>18 else .80,top=.86,bottom=.08)
    fig.savefig(f'{OUT}/{name}.png',facecolor=BG); plt.close(fig)
pc=collections.Counter(r['pattern'] for r in rows).most_common()
hbar('1-patterns','كيف جذب صنّاع المحتوى جمهورهم','عدد صنّاع المحتوى في كل أسلوب نجاح (110 صانع، 11 دولة)',[p for p,_ in pc],[c for _,c in pc])
top=sorted([r for r in rows if r['group']=='قدم' and r['tiktok']],key=lambda r:-float(r['tiktok']))[:10]
hbar('2-top-foot-tiktok','أكبر متخصصي القدم على تيك توك','عدد المتابعين، أعلى 10 أرقام موثّقة',[f"{r['name'][:28]}، {r['country']}" for r in top],[float(r['tiktok']) for r in top],fmt)
# stacked countries
bc=collections.OrderedDict()
for r in rows:
    o=bc.setdefault(r['country'],[0,0,0,0]); o[0 if r['group']=='قدم' else 1]+=1; o[2]+=bool(r['tiktok']); o[3]+=bool(r['facebook'])
def stack(name,title,sub,i,j,n1,n2,order):
    items=sorted(bc.items(),key=order); fig,ax=base(7,title,sub); y=list(range(len(items)))[::-1]
    a=[v[i] for _,v in items]; b=[v[j] for _,v in items]
    ax.barh(y,a,color=BLUE,height=.62,edgecolor=BG,lw=2,label=A(n1)); ax.barh(y,b,left=a,color=ORANGE,height=.62,edgecolor=BG,lw=2,label=A(n2))
    for yi,x1,x2 in zip(y,a,b):
        if x1: ax.text(x1/2,yi,str(x1),ha='center',va='center',color='white',fontsize=11)
        if x2: ax.text(x1+x2/2,yi,str(x2),ha='center',va='center',color='white',fontsize=11)
    ax.invert_xaxis(); ax.yaxis.tick_right(); ax.set_yticks(y); ax.set_yticklabels([A(k) for k,_ in items],fontproperties=fp,fontsize=12,color=INK); ax.set_xticklabels([])
    ax.legend(prop=fp,frameon=False,loc='lower left',bbox_to_anchor=(0,1.0),ncol=2,fontsize=11); fig.subplots_adjust(left=.06,right=.85,top=.86,bottom=.08)
    fig.savefig(f'{OUT}/{name}.png',facecolor=BG); plt.close(fig)
stack('3-foot-by-country','متخصصو القدم في كل دولة','من أصل 10 في كل دولة: متخصص قدم مقابل بديل من تخصص آخر',0,1,'متخصص قدم','بديل',lambda kv:-kv[1][0])
stack('5-data-gap','فجوة البيانات: كم رقم موثّق في كل دولة','أرقام فيسبوك نادرة في المصادر العامة',2,3,'تيك توك موثّق','فيسبوك موثّق',lambda kv:-(kv[1][2]+kv[1][3]))
# scatter
both=[r for r in rows if r['tiktok'] and r['facebook']]
fig,ax=base(8,'تيك توك مقابل فيسبوك','كل نقطة صانع محتوى له الرقمان. فوق الخط القطري = فيسبوك أكبر')
ax.set_xscale('log'); ax.set_yscale('log'); ax.grid(axis='both',color=GRID,lw=.8)
lo,hi=2e4,1.2e7; ax.plot([lo,hi],[lo,hi],ls='--',color='#a9a8a1',lw=1); ax.set_xlim(lo,hi); ax.set_ylim(lo,hi)
for r in both:
    t,f=float(r['tiktok']),float(r['facebook']); c=BLUE if r['group']=='قدم' else ORANGE
    ax.scatter(t,f,s=90,color=c,edgecolor=BG,lw=2,zorder=3); ax.annotate(A(r['name'][:22]),(t,f),xytext=(6,6),textcoords='offset points',fontproperties=fp,fontsize=9,color=MUTED)
ticks=[1e5,1e6,1e7]; ax.set_xticks(ticks); ax.set_yticks(ticks); ax.set_xticklabels([fmt(t) for t in ticks]); ax.set_yticklabels([fmt(t) for t in ticks])
ax.set_xlabel(A('متابعو تيك توك'),fontproperties=fp,fontsize=12,color=MUTED); ax.set_ylabel(A('متابعو فيسبوك'),fontproperties=fp,fontsize=12,color=MUTED)
ax.scatter([],[],color=BLUE,label=A('متخصص قدم')); ax.scatter([],[],color=ORANGE,label=A('بديل')); ax.legend(prop=fp,frameon=False,loc='lower right')
fig.subplots_adjust(left=.1,right=.95,top=.86,bottom=.1); fig.savefig(f'{OUT}/4-tiktok-vs-facebook.png',facecolor=BG); plt.close(fig)
print(sorted(os.listdir(OUT)))
