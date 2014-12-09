############################################################
#
# Olinland Redux
#
# Scaffolding to the final project for Game Programming
#
#

import time
import random
from graphics import * 

# Print debugging logs?
DEBUG = True

# Tile size of the level
LEVEL_WIDTH = 50
LEVEL_HEIGHT = 50

# Tile size of the viewport (through which you view the level)
VIEWPORT_WIDTH = 21
VIEWPORT_HEIGHT = 21

# Pixel size of a tile (which gives you the size of the window)
TILE_SIZE = 24

# Pixel size of the viewport
WINDOW_WIDTH = TILE_SIZE * VIEWPORT_WIDTH
WINDOW_HEIGHT = TILE_SIZE * VIEWPORT_HEIGHT

# Pixel size of the panel on the right where you can display stuff
WINDOW_RIGHTPANEL = 200


#############################################################
# 
# The class hierarchy for objects that you can interact with
# in the world
#
# Roughly modeled from the corresponding hierarchy in our
# adventure game
#


#
# The root object
#
class Root (object):
    # default predicates

    # is this object a Thing?
    def is_thing (self):
        return False

    # is this object a Character?
    def is_character (self):
        return False

    # is this object the Player?
    def is_player (self):
        return False

    # can this object be walked over during movement?
    def is_walkable (self):
        return False

    # can this object be taken by the player?
    def is_takable (self):
        return False


# A thing is something that can be interacted with and by default
# is not moveable or walkable over
#
#   Thing(name,description)
#
# A thing defines a default sprite in field _sprite
# To create a new kind of thing, subclass Thing and 
# assign it a specific sprite (see the OlinStatue below).
# 
class Thing (Root):
    def __init__ (self,name,desc):
        self._name = name
        self._description = desc
        self._sprite = Text(Point(TILE_SIZE/2,TILE_SIZE/2),"?")
        log("Thing.__init__ for "+str(self))

    def __str__ (self):
        return "<"+self.name()+">"

    # shift sprite without changing Thing's position
    def shift (self,dx,dy):
        self.sprite().move(dx,dy)

    # return the sprite for display purposes
    def sprite (self):
        return self._sprite

    # return the name
    def name (self):
        return self._name

    # return the position of the thing in the level array
    def position (self):
        return (self._x,self._y)
        
    # return the description
    def description (self):
        return self._description

    # creating a thing does not put it in play -- you have to 
    # call materialize, passing in the screen and the position
    # where you want it to appear
    def materialize (self,screen,x,y):
        screen.add(self,x,y)
        self._screen = screen
        self._x = x
        self._y = y
        return self

    def dematerialize (self):
        self._screen.delete(self)
        return self

    def is_thing (self):
        return True

    def is_walkable (self):
        return False


#
# Example of a kind of thing with its specific sprite
# (here, a rather boring gray rectangle.)
#
class OlinStatue (Thing):
    def __init__ (self):
        Thing.__init__(self,"Olin statue","A statue of F. W. Olin")
        rect = Rectangle(Point(0,0),Point(TILE_SIZE,TILE_SIZE))
        rect.setFill("gray")
        rect.setOutline("gray")
        self._sprite = rect

    def is_takable (self):
        return True

#
# Characters represent persons and animals and things that move
# about possibly proactively
#
class Character (Thing):
    def __init__ (self,name,desc):
        Thing.__init__(self,name,desc)
        log("Character.__init__ for "+str(self))
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect

    # A character has a move() method that you should implement
    # to enable movement

    # ###############################################################

    # def draw_initial (self):
    #     # This x,y thing worked below, so I think it should work here?
    #     x = self._x
    #     y = self._y
    #     pic = self._DIR_IMGS['Left'] # Not implemented yet, but should be defined per Character (like Rat._DIR_IMGS, Player._DIR_IMGS, etc.)
    #     self._sprite = Image(Point(self._x,self._y),pic) # Currently rectangles vs. pictures, need to fix.
    #     self._sprite.draw(self._window) # How to call window? Maybe self._screen._window from below?

    # ###############################################################

    # def out_with_the_old(self):
    #     self._sprite.undraw() # Don't know if this might need tweaking?

    # ###############################################################

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy


        # Trying to go out of bounds?
        if not (tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT):
            return

        # Trying to walk through an unwalkable tile?
        new_pos = self._screen._level._map[self._screen._level._pos(tx,ty)]
        if new_pos in self._screen._unwalkables:
            return

        # Trying to walk through a Thing that is unwalkable?
        for thing in self._screen._things:
            if (thing.position() == (tx,ty)) and (not thing.is_walkable()):
                return

        # Update character location
        self._x = tx
        self._y = ty
        
        # Shift sprite
        self.shift(dx*TILE_SIZE,dy*TILE_SIZE)
        
        # Update window so changes are visible
        self._screen._window.update()

    # ###############################################################

    # def in_with_the_new(self,key):
    #     # Maybe integrate this whole thing into the move function?
    #     pic = self._DIR_IMGS[key]
    #     self._sprite = Image(Point(self._x,self._y),pic)
    #     self._sprite.draw(self._window) # Again with the window call, see out_with_the_old.

    # ###############################################################

    def is_character (self):
        return True

    def is_walkable (self):
        return False


# 
# A Rat is an example of a character which defines an event that makes
# the rat move, so that it can be queued into the event queue to enable
# that behavior. (Which is right now unfortunately not implemented.)
#
class Rat (Character):
    def __init__ (self,name,desc):
        Character.__init__(self,name,desc)
        log("Rat.__init__ for "+str(self))
        rect = Rectangle(Point(0,0),
                         Point(TILE_SIZE,TILE_SIZE))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect
        self._direction = random.randrange(4)
        self._restlessness = 5

    # A helper method to register the Rat with the event queue
    # Call this method with a queue and a time delay before
    # the event is called
    # Note that the method returns the object itself, so we can
    # use method chaining, which is cool (though not as cool as
    # bowties...)

    def register (self,q,freq):
        self._freq = freq
        q.enqueue(freq,self)
        return self

    # this gets called from event queue when the time is right

    def event (self,q):
        log("event for "+str(self))

        # Should I move this time?
        if random.randrange(self._restlessness) == 0:
            self.move_somewhere()   

        # Re-register event with same frequency
        self.register(q,self._freq)

    def move_somewhere (self):
        dx,dy = random.choice(MOVE.values())
        self.move(dx,dy)

    def is_takable (self):
        return True

#
# The Player character
#
class Player (Character):
    def __init__ (self,name):
        Character.__init__(self,name,"Yours truly")
        log("Player.__init__ for "+str(self))

        self._DIR_IMGS = {
            'Left': 'W_arrow.gif',
            'Right': 'E_arrow.gif',
            'Up' : 'N_arrow.gif',
            'Down' : 'S_arrow.gif'
        }
        self._facing = 'Left'
        pic = self._DIR_IMGS[self._facing]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        
        self._inventory = []
        self._inventory_elts = {}
        # config = {}
        # for option in options:
        #     config[option] = DEFAULT_CONFIG[option]
        # self.config = config

    def is_player (self):
        return True

    # The move() method of the Player is called when you 
    # press movement keys. 
    # It is different enough from movement by the other
    # characters that you'll probably need to overwrite it.
    # In particular, when the Player move, the screen scrolls,
    # something that does not happen for other characters


    #     pic = self._DIR_IMGS[key]
    #     self._sprite = Image(Point(self._x,self._y),pic)
    #     self._sprite.draw(self._window) # Again with the window call, see out_with_the_old.

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy

        fdx,fdy = MOVE[self._facing]

        if not (fdx == dx and fdy == dy):
            key = DIRECTIONS[(dx,dy)]
            print key
            self._facing = key
            self._sprite.undraw()
            pic = self._DIR_IMGS[self._facing]
            self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
            print (self._x-(self._screen._cx-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE
            self._sprite.move((self._x-(self._x-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                               (self._y-(self._y-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
            self._sprite.draw(self._screen._window)

            # Update window so changes are visible
            self._screen._window.update()
            return

        # Trying to go out of bounds?
        if not (tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT):
            return

        # Trying to walk through an unwalkable tile?
        new_pos = self._screen._level._map[self._screen._level._pos(tx,ty)]
        if new_pos in self._screen._unwalkables:
            return

        # Trying to walk through a Thing that is unwalkable?
        for thing in self._screen._things:
            if (thing.position() == (tx,ty)) and (not thing.is_walkable()):
                return

        # Update player location
        self._x = tx
        self._y = ty
        
        # Shift viewport opposite of direction player moves
        self._screen.shift_viewport(-dx,-dy)
        
        # Update window so changes are visible
        self._screen._window.update()

    def facing_object (self):
        dx,dy = MOVE[self._facing]
        tx = self._x + dx
        ty = self._y + dy

        # Am I facing a Thing?
        for thing in self._screen._things:
            if (thing.position() == (tx,ty)):
                return thing

        return False


    def take (self):
        dx,dy = MOVE[self._facing]
        tx = self._x + dx
        ty = self._y + dy

        # Can I take the thing I'm facing?
        thing = self.facing_object()
        if thing and thing.is_takable():
            inv_num = len(self._inventory)
            self._inventory.append(thing)
            thing.dematerialize()

            fg = Text(Point(WINDOW_WIDTH+100,90+25*inv_num),thing.name())
            fg.setSize(16)
            fg.setFill("white")
            fg.draw(self._screen._window)
            self._inventory_elts[inv_num] = fg


    def examine (self):
        dx,dy = MOVE[self._facing]
        tx = self._x + dx
        ty = self._y + dy

        # Am I facing a Thing?
        thing = self.facing_object()
        if thing:
            # Black box as a background
            bg = Rectangle(Point(0,WINDOW_HEIGHT-50), Point(WINDOW_WIDTH,WINDOW_HEIGHT))
            bg.setFill('black')
            bg.draw(self._screen._window)
            # Description
            fg = Text(Point(WINDOW_WIDTH/2,WINDOW_HEIGHT-25),thing.description())
            fg.setSize(16)
            fg.setFill("white")
            fg.draw(self._screen._window)
            # Wait until a key is pressed, then undraw background and description
            key = self._screen._window.getKey()
            fg.undraw()
            bg.undraw()




#############################################################
# 
# The description of the world and the screen which displays
# the world
#
# A level contains the background stuff that you can't really
# interact with. The tiles are decorative, and do not come
# with a corresponding object in the world. (Though you can
# change that if you want.)
#
# Right now, a level is described using the following encoding
#
# 0 empty   (light green rectangle)
# 1 grass   (green rectangle)
# 2 tree    (sienna rectangle)
#
# you'll probably want to make nicer sprites at some point.


#
# This implements a random level right now. 
# You'll probably want to replace this with something that 
# implements a specific map -- perhaps of Olin?
#
class Level (object):
    def __init__ (self):
        size = LEVEL_WIDTH * LEVEL_HEIGHT
        the_map = [0] * size
        for i in range(100):
            the_map[random.randrange(size)] = 1
        for i in range(50):
            the_map[random.randrange(size)] = 2
        self._map = the_map

    def _pos (self,x,y):
        return x + (y*LEVEL_WIDTH);

    # return the tile at a given tile position in the level
    def tile (self,x,y):
        return self._map[self._pos(x,y)]

    def ind_to_pos (self, ind):
        x = ind % LEVEL_WIDTH
        y = (ind - x) / LEVEL_WIDTH
        return (x*TILE_SIZE,y*TILE_SIZE)

#
# A Screen is a representation of the level displayed in the 
# viewport, with a representation for all the tiles and a 
# representation for the objects in the world currently 
# visible. Managing all of that is key. 
#
# For simplicity, a Screen object contain a reference to the
# level it is displaying, and also to the window in which it
# draws its elements. So you can use the Screen object to 
# mediate access to both the level and the window if you need
# to access them.
# 
# You'll DEFINITELY want to add methods to this class. 
# Like, a lot of them.
#
class Screen (object):
    def __init__ (self,level,window,cx,cy):
        self._level = level
        self._unwalkables = [2]
        self._window = window
        self._cx = cx    # the initial center tile position 
        self._cy = cy    #  of the screen
        self._map_elts = {}
        self._things = []
        # Out-of-bounds is black
        out = Rectangle(Point(0,0),Point(WINDOW_WIDTH,WINDOW_HEIGHT))
        out.setFill("black")
        out.setOutline("black")
        out.draw(window)
        
        dx = (cx - (VIEWPORT_WIDTH-1)/2) * TILE_SIZE
        dy = (cy - (VIEWPORT_HEIGHT-1)/2) * TILE_SIZE

        # Background is lightgreen
        bg = Rectangle(Point(-dx,-dy),Point(TILE_SIZE*(LEVEL_WIDTH)-dx,TILE_SIZE*(LEVEL_HEIGHT)-dy))
        bg.setFill("lightgreen")
        bg.setOutline("lightgreen")
        bg.draw(window)
        self._map_elts[-1] = bg

        # Tiles
        for ind,cell in enumerate(self._level._map):
            if cell:
                sx,sy = self._level.ind_to_pos(ind)

                elt = Rectangle(Point(sx-dx,sy-dy),
                                Point(sx-dx+TILE_SIZE,sy-dy+TILE_SIZE))

                if cell == 1:
                    elt.setFill('green')
                    elt.setOutline('green')
                elif cell == 2:
                    elt.setFill('sienna')
                    elt.setOutline('sienna')
                elt.draw(window)

                self._map_elts[ind] = elt

    # return the tile at a given tile position
    def tile (self,x,y):
        return self._level.tile(x,y)

    # add a thing to the screen at a given position
    def add (self,item,x,y):
        # first, move object into given position
        item.sprite().move((x-(self._cx-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                           (y-(self._cy-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
        item.sprite().draw(self._window)
        # WRITE ME!   You'll have to figure out how to manage these
        # because chances are when you scroll these will not move!
        self._things.append(item)

    def delete (self,item):
        item.sprite().undraw()
        self._things.remove(item)

    # helper method to get at underlying window
    def window (self):
        return self._window

    # shift viewport when player moves
    def shift_viewport (self, dx, dy):
        for key in self._map_elts:
            # Move screen in the specified direction
            self._map_elts[key].move(dx*TILE_SIZE,dy*TILE_SIZE)
        for thing in self._things:
            # Move Things as well so they appear to not move
            if not thing.is_player():
                thing.shift(dx*TILE_SIZE,dy*TILE_SIZE)

   


# A helper function that lets you log information to the console
# with some timing information. I found this super useful to 
# debug tricky event-based problems.
#
def log (message):
    if DEBUG:
        print time.strftime("[%H:%M:%S]",time.localtime()),message

    

#############################################################
# 
# The event queue
#
# An event is any object that implements an event() method
# That event method gets the event queue as input, so that
# it can add to the event queue if it needs to.

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


# A simple event class that checks for user input.
# It re-enqueues itself after the check.

MOVE = {
    'Left': (-1,0),
    'Right': (1,0),
    'Up' : (0,-1),
    'Down' : (0,1),
    'a': (-1,0),
    'd': (1,0),
    'w' : (0,-1),
    's' : (0,1)
}

DIRECTIONS = {
    (-1,0): 'Left',
    (1,0): 'Right',
    (0,-1): 'Up',
    (0,1): 'Down'
}

class CheckInput (object):
    def __init__ (self,window,player):
        self._player = player
        self._window = window

    def event (self,q):
        key = self._window.checkKey()
        if key == 'q':
            self._window.close()
            exit(0)
        if key in MOVE:

    # ###############################################################

    #         # I'm sure these will have to be modified eventually.
    #         self._player.out_with_the_old()
    #         self._player.in_with_the_new(key)

    # ###############################################################

            (dx,dy) = MOVE[key]
            self._player.move(dx,dy)
        if key == 'f':
            self._player.take()
        if key == 'e':
            self._player.examine()
        q.enqueue(1,self)

#
# Create the right-side panel that can be used to display interesting
# information to the player
#
def create_panel (window):
    fg = Rectangle(Point(WINDOW_WIDTH+1,-20),
                   Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL+20,WINDOW_HEIGHT+20))
    fg.setFill("darkgray")
    fg.setOutline("darkgray")
    fg.draw(window)
    fg = Text(Point(WINDOW_WIDTH+100,30),"Pizza Quest")
    fg.setSize(20)
    fg.setStyle("italic")
    fg.setFill("red")
    fg.draw(window)

    fg = Text(Point(WINDOW_WIDTH+100,60),'Inventory')
    fg.setSize(16)
    fg.setFill("white")
    fg.draw(window)

    fg = Text(Point(WINDOW_WIDTH+100,60),'________')
    fg.setSize(16)
    fg.setFill("white")
    fg.draw(window)


#
# The main function
# 
# It initializes everything that needs to be initialized
# Order is important for graphics to display correctly
# Note that autoflush=False, so we need to explicitly
# call window.update() to refresh the window when we make
# changes
#
def main ():

    window = GraphWin("Olinland Redux", 
                      WINDOW_WIDTH+WINDOW_RIGHTPANEL, WINDOW_HEIGHT,
                      autoflush=False)

    level = Level()
    log ("level created")

    scr = Screen(level,window,25,25)
    log ("screen created")

    q = EventQueue()

    OlinStatue().materialize(scr,20,20)
    Rat("Pinky","A rat").register(q,40).materialize(scr,30,30)
    Rat("Brain","A rat with a big head").register(q,60).materialize(scr,10,30)

    create_panel(window)

    p = Player("...what's your name, bub?...").materialize(scr,25,25)

    q.enqueue(1,CheckInput(window,p))

    while True:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        time.sleep(0.01)



if __name__ == '__main__':
    main()
