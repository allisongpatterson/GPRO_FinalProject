from graphics import *
import time

tile_size = 24
win_size = tile_size*5
win = GraphWin("blarg",win_size,win_size,autoflush = False)
SPRITE = None # Image(Point(win_size/2,win_size/2),pic)
# pic = 't_android_red.gif'
# SPRITE = Image(Point(win_size/2,win_size/2),pic)
# SPRITE.draw(win)

MOVE = {
    'Left': 'W_arrow.png',
    'Right': 'E_arrow.png',
    'Up' : 'N_arrow.png',
    'Down' : 'S_arrow.png'
    # '' : 't_android_red.gif'
}
