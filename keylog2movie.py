import gizeh as gz
import numpy as np

v = np.array

RES = (300, 300)
PAD = 12

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

def dict2layout(key_states):
    return [
      [col if col == '' else key_states[col] for col in row]
      for row in names_layout
    ]

def render_keys(key_states):
    isdown_layout = dict2layout(key_states)

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

    s.write_to_png('keys.png')

render_keys({
    'forward': True,
    'backward': False,
    'left': True,
    'right': False,
    'crouch': False,
    'jump': True,
})
