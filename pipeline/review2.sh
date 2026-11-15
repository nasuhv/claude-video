#!/bin/bash
# usage: review.sh out.jpg t1 t2 ...  (composites overlay stills onto source frames, tiles 2 columns)
S=$SCR; out=$1; shift
rm -f $S/review/ov_*.png $S/review/c_*.png
python3 -I $S/scripts/gfx2.py still $S/review "$@" 2>&1 | grep -v Warn
i=0
for t in "$@"; do
  f=$(printf "%s/review/ov_%07.2f.png" $S $t)
  ffmpeg -v error -ss $t -i $S/src/raw.mov -i $f -filter_complex "[0:v][1:v]overlay,drawtext=fontfile=$S/assets/fonts/jbm/fonts/ttf/JetBrainsMono-Bold.ttf:text='t=$t':x=20:y=h-50:fontsize=34:fontcolor=red,scale=960:-1" -frames:v 1 -y $(printf "%s/review/c_%03d.png" $S $i)
  i=$((i+1))
done
n=$#; rows=$(( (n+1)/2 ))
ffmpeg -v error -i $S/review/c_%03d.png -vf "tile=2x$rows" -frames:v 1 -y $out
