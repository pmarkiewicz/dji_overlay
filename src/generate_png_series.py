from PIL import Image, ImageDraw, ImageFont

from parse_srt import parse_srt
from parse_log import parse_csv
from merge_log import merge_log

from charts import VChart, TChart, GPSChart, HChart

srt_fn = r'D:\FPV\Video\DJI\20201225\DJIG0000.srt'
log_fn = r'D:\FPV\Video\DJI\20201225\Banggod-2020-12-25.csv'
fnv = r'D:\FPV\Video\DJI\20201225\DJIU0000.mp4'
out = r'D:\FPV\Video\DJI\20201225\DJIU0000-out.mp4'

rows = parse_srt(srt_fn)
log = parse_csv(log_fn, 250)

merged_rows = merge_log(rows, log)

cells = 6

br = VChart('bitrate', no_of_bars=10, color_range_h=25, color_range_l=15, max_value=50.8, bar_h=2, bar_space=2)
sig = VChart('signal', 4, 3, 2, 4, bar_space=2, fmt='1d')
bat = HChart('bat', 10, 3.8*cells, 3.5*cells, min_value=3.0 * cells, max_value=25.1, bar_space=2)
delay = VChart('delay', 4, 38, 32, min_value=20, max_value=50, bar_space=2, fmt='2d', reversed=True)
thr = VChart('thr', no_of_bars=20, color_range_h=0, color_range_l=100, min_value=0, max_value=100, bar_space=1, bar_h=1, bar_w = 5, fmt='d')
alt = TChart('Alt:', 'm')
sat = TChart('SAT:')
curr = TChart('', 'A')
thr_txt = TChart('Th', '%')
br_txt = TChart('BR:')
delay_txt = TChart('D:', 'ms')
gps = GPSChart(font_size=18)
dist = TChart('H:', 'm', fmt='.0f')


for img_no, row in enumerate(merged_rows):
    img = Image.new('RGBA', (1920, 1080), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    br.draw(draw, 50, 10, row['bitrate'], img)
    sig.draw(draw, 100, 10, row['signal'], img)
    bat.draw(draw, 50, 850, row['uavBat'], img)
    delay.draw(draw, 150, 10, row['delay'], img)
    thr.draw(draw, 50, 100, row['Thr(%)'], img)
    alt.draw(draw, 250, 10, row['Alt(m)'])
    sat.draw(draw, 350, 10, row['Sats'])
    curr.draw(draw, 450, 10, row['Curr(A)'])
    thr_txt.draw(draw, 550, 10, row['Thr(%)'])
    br_txt.draw(draw, 650, 10, row['bitrate'])
    delay_txt.draw(draw, 750, 10, row['delay'])
    gps.draw(draw, 50, 500, row['GPS'])
    dist.draw(draw, 50, 600, row['distance(m)'])
    img.save(f'img/{img_no:04d}.png', 'PNG')

    if img_no == 0:
        complex_filter_script = [f"[0:v][1:v] overlay=enable='between(t, {row['start']}, {row['end']})' [tmp]\n"]
    else:
        complex_filter_script.append(f"; [tmp][{img_no}:v] overlay=enable='between(t, {row['start']}, {row['end']})' [tmp]\n")

    if img_no % 100 == 0:
        print('.', end='')

# remove last tmp
s = complex_filter_script[-1]
complex_filter_script[-1] = s[:-6]

with open('filter.txt', 'w') as f:
    f.writelines(complex_filter_script)

inputs = ['-i {:04d}.png'.format(i) for i in range(0, img_no + 1)]
input_files = ' '.join(inputs)

cmd = f'..\\ffmpeg -y -thread_queue_size 1024 -i {fnv} {input_files} -filter_complex_script ..\\filter.txt -c:v libx264 -preset slow -crf 12 -tune film {out}'
with open('ff.cmd', 'w') as f:
    f.write(cmd)
