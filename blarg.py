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

def get_input():
	if win.checkKey() != '':
		key = win.checkKey()
		if key in MOVE:
			pic = MOVE[key]
			# erase_old()
			return pic
			# Thingy._sprite = Image(Point(win_size/2,win_size/2),pic)
			# return pic
		# else:
		# 	time.sleep(1)
	else:
		return None

def draw_new(pic):
	# key = win.checkKey()
	# if key in MOVE:
	# 	# time.sleep(.1)
	# 	# sprite.undraw()
	# # if key in MOVE:
	# # 	pic = MOVE[key]
	# # 	return pic
	# 	pic = MOVE[key]
	# pic = img_at_press
	SPRITE = Image(Point(win_size/2,win_size/2),pic)
	SPRITE.draw(win)
	# return SPRITE
		
def erase_old():
	# key = win.checkKey()
	# if key in MOVE:
	# 	SPRITE.undraw()
	# 	draw_new()
# if draw_new():
	# SPRITE = draw_new()
	if SPRITE:
		SPRITE.undraw()


def main():
	pic = get_input()
	if pic != None:
		# img_at_press = get_input()
		# if img_at_press != '':
		erase_old()
		draw_new(pic)


while True:
	main()
	# time.sleep(1)
# time.sleep(.5)
	
# win.getMouse()



# class Thingy(object):
# 	def __init__(self,name,pic):
# 		self._name = name
# 		# self._sprite = Image(Point(win_size/2,win_size/2),pic)

# 	def sprite (self):
# 		return self._sprite

# 	def out_with_the_old(self):
# 		if self.sprite():
# 			self.sprite().undraw()

# 	def in_with_the_new(self):
# 		if self.sprite():
# 			self.sprite().draw(win)
		
# class Arrow(Thingy):
# 	def __init__(self,name,pic):
# 		Thingy.__init__(self,name,pic)
# 		self._sprite = Image(Point(win_size/2,win_size/2),pic)


# def get_input():
# 	key = win.checkKey()
# 	if key in MOVE:
# 		pic = MOVE[key]
# 		# Thingy._sprite = Image(Point(win_size/2,win_size/2),pic)
# 		return pic

# def main():
# 	while True:
# 		arrow = Arrow("the arrow",'')
# 		arrow.draw(win)
# 		if get_input():
# 			arrow.out_with_the_old()
# 			arrow.in_with_the_new()