import gizeh as gz
import numpy as np
import csv
from collections import OrderedDict
from scipy import interpolate
from moviepy.video.VideoClip import VideoClip

v = np.array

BORDER = 4
BORDER_RGB = (0.1,0.1,0.2)
RES = (300, 200)

# Keep synced with record-moves.py
names_layout = [
    ['crouch', 'forward', 'jump'],
    ['left', 'backward', 'right'],
]

chars_layout = [
    ['C', '↑', 'J'],
    ['←', '↓', '→'],
]

def set2layout(keys_down):
    return [
      [col if col == '' else (col in keys_down) for col in row]
      for row in names_layout
    ]

def render_keys(keys_down):
    isdown_layout = set2layout(keys_down)

    s = gz.Surface(RES[0]+2*BORDER, RES[1]+2*BORDER)
    #gz.rectangle(xy=(RES[0]/2, RES[1]/2), lx=RES[0], ly=RES[1], fill=(0,1,0)).draw(s) # greenscreen?
    gz.rectangle(xy=(RES[0]/2+BORDER, RES[1]/2+BORDER), lx=RES[0], ly=RES[1], fill=BORDER_RGB).draw(s)

    row_height = RES[1]/len(chars_layout)

    xy = v([BORDER, -row_height/2 + BORDER])

    for row, downs in zip(chars_layout, isdown_layout):
        xy += v([0, row_height]) # place pen at start pos for row

        tot_chars = sum([len(col) for col in row])

        for col, is_down in zip(row, downs):
            col_width = RES[0] * len(col) / tot_chars
            xy += v([col_width/2, 0]) # advance pen

            if col != ' ':
                fill = (0.5,0.5,1) if is_down else (0.2,0.2,0.4)
                gz.rectangle(xy=xy, lx=col_width, ly=row_height,
                             fill=fill, stroke=BORDER_RGB, stroke_width=BORDER).draw(s)
                gz.text(col, 'Arial', 60, fill=(1,1,1), xy=xy).draw(s)

            xy += v([col_width/2, 0]) # advance pen

        xy[0] = BORDER

    return s

keys_down_timeline = OrderedDict()
get_most_recent_time = None
last_t_ms = None

print('Building timeline...')
with open('keylog.txt', newline='') as infile:
    reader = csv.reader(infile, delimiter='\t')
    next(reader) # skip headings

    last_keys_down = None

    for entry in reader:
        time_ms = int(entry[0])
        keyname = entry[1]
        is_down = True if entry[2] == 'on' else False

        current_keys_down = set() if last_keys_down is None else set(last_keys_down)

        if is_down:
            current_keys_down.add(keyname)
        else:
            current_keys_down.remove(keyname)

        keys_down_timeline[time_ms] = current_keys_down

        last_keys_down = current_keys_down
        last_t_ms = time_ms

    ts = v(list(keys_down_timeline.keys()))
    get_most_recent_time = interpolate.interp1d(ts, ts, kind='previous')

def get_keys_down_at(time_ms):
    if time_ms > last_t_ms:
        return set()
    time = int(get_most_recent_time(time_ms))
    return keys_down_timeline[time]

def make_frame(t_sec):
    return render_keys(get_keys_down_at(t_sec*1000)).get_npimage()

print('Generating video...')

vc = VideoClip(make_frame, duration=(last_t_ms)/1000+5)
vc.write_videofile('keylog.mp4', fps=24)
