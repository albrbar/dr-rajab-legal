#!/usr/bin/env bash
# Final polish for a 9:16 clinic video. Usage: finish.sh input.mp4 out_dir [cover_seconds]
set -euo pipefail
IN="$1"; OUT="${2:-finished}"; COVER="${3:-1.5}"
mkdir -p "$OUT/frames"
BASE="$(basename "${IN%.*}")"
DST="$OUT/$BASE-final.mp4"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | head -1)
VF="scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30,format=yuv420p"
# ~8 MB target: video bitrate from duration (leave 128k for audio)
VBR=$(python3 -c "d=float('$DUR'); print(max(800, min(6000, int(8*8*1024/d - 128))))")
if [ -n "$HAS_AUDIO" ]; then
  ffmpeg -y -loglevel error -i "$IN" -vf "$VF" -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
    -c:v libx264 -profile:v high -b:v "${VBR}k" -maxrate "${VBR}k" -bufsize "$((VBR*2))k" \
    -c:a aac -b:a 128k -ar 44100 -movflags +faststart "$DST"
else
  ffmpeg -y -loglevel error -i "$IN" -vf "$VF" -c:v libx264 -profile:v high -b:v "${VBR}k" \
    -maxrate "${VBR}k" -bufsize "$((VBR*2))k" -an -movflags +faststart "$DST"
fi
ffmpeg -y -loglevel error -ss "$COVER" -i "$DST" -frames:v 1 -q:v 2 "$OUT/$BASE-cover.jpg"
STEP=$(python3 -c "print(max(0.5, float('$DUR')/6))")
ffmpeg -y -loglevel error -i "$DST" -vf "fps=1/$STEP,scale=540:-1" "$OUT/frames/%02d.jpg"
echo "== QC $DST"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration,size -of default=nw=1 "$DST"
SIZE=$(stat -c %s "$DST"); echo "size_ok=$([ "$SIZE" -le 9000000 ] && echo yes || echo no) ($SIZE bytes)"
echo "audio=$([ -n "$HAS_AUDIO" ] && echo 'normalized -14 LUFS' || echo none)"
echo "cover=$OUT/$BASE-cover.jpg frames=$OUT/frames/ (read them: text, safe zones, end card)"
