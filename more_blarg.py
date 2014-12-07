from graphics import *
import time

tile_size = 24
win_size = tile_size*5
win = GraphWin("more_blarg",win_size,win_size,autoflush = False)
sprite = None # Image(Point(win_size/2,win_size/2),pic)
pic = None

MOVE = {
    'Left': 'W_arrow.png',
    'Right': 'E_arrow.png',
    'Up' : 'N_arrow.png',
    'Down' : 'S_arrow.png'
    # '' : 't_android_red.gif'
}

class Player (object):
	def __init__ (self,name,window):
		self._name = name
		self._window = window

	def draw_initial (self):
		pic = MOVE['Left']
		self._sprite = Image(Point(win_size/2,win_size/2),pic)
		self._sprite.draw(self._window)

	def out_with_the_old(self):
		self._sprite.undraw()

	def in_with_the_new(self,key):
		pic = MOVE[key]
		self._sprite = Image(Point(win_size/2,win_size/2),pic)
		self._sprite.draw(self._window)

class EventQueue (object):
    def __init__ (self):
        self._contents = []

    # list kept ordered by time left before firing
    def enqueue (self,when,obj):
        for (i,entry) in enumerate(self._contents):
            if when < entry[0]:
                self._contents.insert(i,[when,obj])
                break
        else:
            self._contents.append([when,obj])

    def ready (self):
        if self._contents:
            return (self._contents[0][0]==0)
        else:
            return False
        
    def dequeue_if_ready (self):
        acted = self.ready()
        while self.ready():
            entry = self._contents.pop(0)
            entry[1].event(self)
        for entry in self._contents:
            entry[0] -= 1

class CheckInput (object):
    def __init__ (self,window,player):
        self._window = window
        self._player = player

    def event (self,q):
        key = self._window.checkKey()
        if key == 'q':
            self._window.close()
            exit(0)
        if key in MOVE:
        	print 'so far so good'
        	self._player.out_with_the_old()
        	print "bam, he's gone"
        	self._player.in_with_the_new(key)
            # (dx,dy) = MOVE[key]
            # self._player.move(dx,dy)
        if key == 'e':
            self._player.take()
        q.enqueue(1,self)

def main():
	p = Player('p',win)
	p.draw_initial()
	
	q = EventQueue()
	q.enqueue(1,CheckInput(win,p))

	while True:
        # Grab the next event from the queue if it's ready
		q.dequeue_if_ready()
        # Time unit = 10 milliseconds
		time.sleep(0.01)

if __name__ == '__main__':
    main()

win.getMouse()
win.close()