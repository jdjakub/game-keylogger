# WARNING!! Flagged as a keylogger by Windows (duh... though it's interesting
# that it reads Python code!) so RENAME to .txt extension before running!
# python record-moves.py.txt

# Writes to ./keylog.txt, exit by closing the window (Ctrl-C doesn't work lol)

from pynput.keyboard import Key, Listener as KeyL
from pynput.mouse import Listener as MouseL
from pynput.mouse import Button as B
import time

# Maps silly pynput str(key) to action name
ACTIONS = {
    "'w'": 'forward',
    "'a'": 'left',
    "'s'": 'backward',
    "'d'": 'right',
    "Key.space": 'crouch',
    'Button.right': 'jump',
}

# All keys up by default; used to filter out repeats
IS_DOWN = { action: False for action in ACTIONS.values() }

t0 = None
fout = None

def t_ms():
    global t0

    t = time.time()
    if t0 is None:
        t0 = t
    return int((t - t0) * 1000)

def state(is_down):
    return "on" if is_down else "off"

def log(button, is_down):
    action = ACTIONS.get(str(button))
    if action is not None and is_down != IS_DOWN[action]: # Not a repeat message
        IS_DOWN[action] = is_down # Update current state
        print(f"{t_ms()}\t{action}\t{state(is_down)}", file=fout)
        fout.flush()

fout = open("keylog.txt", "w")
print('time_ms\taction\tonoff', file=fout)

with KeyL(
    on_press=lambda key: log(key, True),
    on_release=lambda key: log(key, False)
) as kl:
    with MouseL(
        on_click=lambda x,y,button,is_down: log(button, is_down)
    ) as ml:
        kl.join()
        ml.join()
