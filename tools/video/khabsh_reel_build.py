import subprocess, os
V=os.path.dirname(os.path.abspath(__file__))
groups=[('intro',['01','02']),('content',['03']),('title',['04']),('red1',['05']),('red2',['06','07']),('red3',['08','09']),('red4',['10','11']),('grn1',['12']),('grn2',['13','14']),('grn3',['15']),('landing',['16']),('share',['17'])]
def run(c): subprocess.run(c,shell=True,check=True)
lst=[]
for i,(card,clips) in enumerate(groups):
    ins=' '.join(f'-i final/{c}.wav' for c in clips)
    parts=''.join(f'[{k}:a]apad=pad_dur=0.25[a{k}];' for k in range(len(clips)))
    cat=''.join(f'[a{k}]' for k in range(len(clips)))
    run(f'ffmpeg -y -loglevel error {ins} -filter_complex "{parts}{cat}concat=n={len(clips)}:v=0:a=1,apad=pad_dur=0.15[a]" -map "[a]" -ar 44100 -ac 1 seg/a{i:02d}.wav')
    dur=float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 seg/a{i:02d}.wav',shell=True))
    fr=int(dur*30)+1
    z = "min(zoom+0.0005,1.06)" if i%2==0 else "if(eq(on,0),1.06,max(zoom-0.0005,1.0))"
    run(f'ffmpeg -y -loglevel error -loop 1 -i cards/{card}.png -i seg/a{i:02d}.wav -filter_complex "[0:v]scale=1080:1920,zoompan=z=\'{z}\':d={fr}:s=1080x1920:fps=30,format=yuv420p[v]" -map "[v]" -map 1:a -c:v libx264 -preset medium -crf 22 -c:a aac -b:a 160k -t {dur:.3f} seg/s{i:02d}.mp4')
    lst.append(f"file 's{i:02d}.mp4'")
open('seg/list.txt','w').write('\n'.join(lst))
run('ffmpeg -y -loglevel error -f concat -safe 0 -i seg/list.txt -c copy -movflags +faststart reel-khabsh-full.mp4')
print(subprocess.check_output('ffprobe -v error -show_entries format=duration -of csv=p=0 reel-khabsh-full.mp4',shell=True).decode())
