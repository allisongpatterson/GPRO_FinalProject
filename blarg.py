from graphics import *

tile_size = 24
win_size = tile_size*3
win = GraphWin("blarg",win_size,win_size,autoflush = False)
pic = 'arrow.png'
sprite = Image(Point(win_size/2,win_size/2),pic)

def main():
	sprite.draw(win)
	win.getMouse()

main()