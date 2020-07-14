import gizeh as gz
import numpy as np
import csv
from itertools import islice
from collections import OrderedDict
from scipy import interpolate

v = np.array

RES = (300, 300)
PAD = 12

# Keep synced with record-moves.py
names_layout = [
    ['', 'forward', ''],
    ['left', 'backward', 'right'],
    ['crouch', 'jump'],
]

isdown_layout = [
    [False,True,False],
    [True,False,False],
    [True,True],
]

chars_layout = [
    [' ', '↑', ' '],
    ['←', '↓', '→'],
    ['crouch', 'jump'],
]

def set2layout(keys_down):
    return [
      [col if col == '' else (col in keys_down) for col in row]
      for row in names_layout
    ]

def render_keys(keys_down):
    isdown_layout = set2layout(keys_down)

    s = gz.Surface(*RES)

    row_height = RES[1]/len(chars_layout)

    xy = v([0,-row_height/2])

    for row, downs in zip(chars_layout, isdown_layout):
        xy += v([0, row_height]) # place pen at start pos for row

        tot_chars = sum([len(col) for col in row])

        for col, is_down in zip(row, downs):
            col_width = RES[0] * len(col) / tot_chars
            xy += v([col_width/2, 0]) # advance pen

            if col != ' ':
                fill = (0,0,0.8) if is_down else (0.2,0.2,0.4)
                gz.rectangle(xy=xy, lx=col_width-PAD/2, ly=row_height-PAD/2,
                             fill=fill, stroke=(1,1,1), stroke_width=1).draw(s)
                gz.text(col, 'Arial', 40, fill=(1,1,1), xy=xy).draw(s)

            xy += v([col_width/2, 0]) # advance pen

        xy[0] = 0

    return s

keys_down_timeline = OrderedDict()
get_most_recent_time = None

print('Building timeline...')
with open('keylog.txt', newline='') as infile:
    reader = csv.reader(infile, delimiter='\t')
    next(reader) # skip headings

    last_keys_down = None

    for entry in islice(reader, 20):
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

    ts = v(list(keys_down_timeline.keys()))
    get_most_recent_time = interpolate.interp1d(ts, ts, kind='previous')

def get_keys_down_at(time_ms):
    time = int(get_most_recent_time(time_ms))
    return keys_down_timeline[time]

print('Writing images...')

for i in range(0,10):
    time = 100*i
    filename = f'keys{time}.png'
    render_keys(get_keys_down_at(time)).write_to_png(filename)
