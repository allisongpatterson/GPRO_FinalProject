############################################################
#
# Pizza Quest
#
# Jacob Kingery and Allison Patterson
#
# Future work:
# More levels!
# Using the implemented inventory system to advance the storyline (block up obstructions with explosives, etc.)
# Adding other items (such as health restoratives)
# Add sound effects
# 

import time
import random
import levels as lvl
from graphics import * 

# Print debugging logs?
DEBUG = True

# Tile size of the level
LEVEL_WIDTH = 50
LEVEL_HEIGHT = 50

# Tile size of the viewport (through which you view the level)
VIEWPORT_WIDTH = 15
VIEWPORT_HEIGHT = 15

# Pixel size of a tile (which gives you the size of the window)
TILE_SIZE = 48

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

    # is this object a LLama?
    def is_llama (self):
        return False

    # can this object be walked over during movement?
    def is_walkable (self):
        return False

    # can this object be taken by the player?
    def is_takable (self):
        return False

    # can this object be set on fire?
    def is_flammable (self):
        return False

    # is this object pizza?
    def is_pizza (self):
        return False

    def is_vortex (self):
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
        self._walkable = False
        self._takable = False
        self._flammable = False
        self._burnt = False
        self._sprite = Text(Point(TILE_SIZE/2,TILE_SIZE/2),"?")
        log("Thing.__init__ for "+str(self))

    def __str__ (self):
        return "<"+self.name()+">"

    def raise_sprite (self):
        self._sprite.canvas.tag_raise(self._sprite.id)

    def lower_sprite (self):
        self._sprite.canvas.tag_lower(self._sprite.id)

    def raise_or_lower_sprite (self,raise_player=True):
        p = self._screen._player
        x_dist = self._x - p._x
        if x_dist > (VIEWPORT_WIDTH-1)/2:
            self.lower_sprite()
        else:
            self.raise_sprite()
            if raise_player:
                p.raise_sprite()

    # shift sprite without changing Thing's position
    def shift (self,dx,dy,raise_player=True):
        self.raise_or_lower_sprite(raise_player)
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

    def facing_object (self):
        dx,dy = MOVE[self._facing]
        tx = self._x + dx
        ty = self._y + dy

        # Am I facing a Thing?
        for thing in self._screen._things:
            if (thing.position() == (tx,ty)):
                return thing

        return False

    def on_object (self):
        # Am I on a Thing?
        for thing in self._screen._things:
            if (thing.position() == (self._x,self._y)):
                return thing

        return False

    # creating a thing does not put it in play -- you have to 
    # call materialize, passing in the screen and the position
    # where you want it to appear
    def materialize (self,screen,x,y,cx=-1,cy=-1):
        if (cx != -1) and (cy != -1):
            screen.add(self,x,y,cx,cy)
        else:
            screen.add(self,x,y)
        self._screen = screen
        self._x = x
        self._y = y

        if self.is_player():
            # display health indicator
            self._h_obj.draw(self._screen._window) 

        return self

    def dematerialize (self):
        self._screen.delete(self)
        return self

    def register (self,q,freq):
        self._freq = freq
        q.enqueue(freq,self)
        return self

    def burn (self):
        # llama stuff...
        

        # Change sprite to ash pile
        pic = 'sprites/ash.gif'
        self._sprite.undraw()
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        p = self._screen._player
        self._sprite.move((self._x-(p._x-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                           (self._y-(p._y-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
        self._sprite.draw(self._screen._window)

        # Change attributes
        self._walkable = True
        self._flammable = False
        self._takable = False
        self._burnt = True
        self._name = "{}'s ashes".format(self._name)
        self._description = 'what used to be {}'.format(self._description)

        # Pull player sprite to top
        p.raise_sprite()
        
    def is_thing (self):
        return True

    def is_walkable (self):
        return self._walkable

    def is_takable (self):
        return self._takable

    def is_flammable (self):
        return self._flammable

    def is_burnt (self):
        return self._burnt

    def is_barricade_door (self):
        return False

class Projectile (Thing):
    def __init__ (self, facing, mrange, power):
        Thing.__init__(self,'Projectile','A projectile')
        self._facing = facing
        self._dx, self._dy = MOVE[facing]
        self._range = mrange
        self._power = power
        self._walkable = True



    def event (self,q):
        log("event for "+str(self))
        if self._range > 0:
            self._range -= 1
            done = self.move_or_stop()
            if not done:
                # Re-register event with same frequency
                self.register(q,self._freq)
        else:
            log(str(self)+' stopping at max range')
            self.stop()

    def stop (self):
        # Just stops projectile and undraws it
        # If it needs to do more, overwrite this in a subclass
        # print 'stopping'
        self._range = 0
        self.dematerialize()
        self._screen._window.update()

    def move_or_stop (self):
        def stop_now():
            self.stop()
            return True

        # Reached the border?
        if self._x == 0 and self._dx == -1:
            log(str(self)+' stopping at left border')
            return stop_now()        
        if self._x == LEVEL_WIDTH-1 and self._dx == 1:
            log(str(self)+' stopping at right border')
            return stop_now()
        if self._y == 0 and self._dy == -1:
            log(str(self)+' stopping at top border')
            return stop_now()
        if self._y == LEVEL_HEIGHT-1 and self._dy == 1:
            log(str(self)+' stopping at bottom border')
            return stop_now()

        # Reached an unwalkable and unflammable tile?
        f_tile = self._screen._level._pos(self._x+self._dx,self._y+self._dy)
        tile_val = self._screen._level._map[f_tile]
        if tile_val in lvl.UNWALKABLES and tile_val not in lvl.FLAMMABLES:
            log(str(self)+' stopping at unwalkable, unflammable tile')
            return stop_now()

        # On a flammable tile?
        o_tile = self._screen._level._pos(self._x, self._y)
        if self._screen._level._map[o_tile] in lvl.FLAMMABLES:
            log(str(self)+' stopping on flammable tile')
            return stop_now()

        # Reached an unwalkable, unflammable, nonLlama Thing?
        f_obj = self.facing_object()
        if f_obj and not f_obj.is_walkable() and not f_obj.is_flammable() and not f_obj.is_llama():
            log(str(self)+' stopping at unwalkable, unflammable Thing')
            return stop_now()

        # On an alive Llama?
        o_obj = self.on_object()
        if o_obj and o_obj.is_llama() and not o_obj.is_burnt():
            log(str(self)+' stopping on Llama')
            return stop_now()

        # On a flammable Thing?
        if o_obj and o_obj.is_flammable():
            log(str(self)+' stopping on flammable Thing')
            return stop_now()


        # Else, move
        log(str(self)+' moving')
        self._x = self._x + self._dx
        self._y = self._y + self._dy
        
        # Shift sprite
        self.shift(self._dx*TILE_SIZE,self._dy*TILE_SIZE)
        
        # Update window so changes are visible
        self._screen._window.update()

        # Not done moving yet
        return False


class Fireball (Projectile):
    def __init__ (self, facing, mrange, power):
        Projectile.__init__(self, facing, mrange, power)
        imgs = [{'Left': 'sprites/W_fireball.gif','Right': 'sprites/E_fireball.gif','Up' : 'sprites/N_fireball.gif','Down' : 'sprites/S_fireball.gif'},
            {'Left': 'sprites/W_big_fireball.gif','Right': 'sprites/E_big_fireball.gif','Up' : 'sprites/N_big_fireball.gif','Down' : 'sprites/S_big_fireball.gif'}
        ]
        self._DIR_IMGS = imgs[power]
        self._facing = facing
        pic = self._DIR_IMGS[self._facing]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)


    def stop (self):
        # Burn the thing if possible
        # print 'stopping'
        self._range = 0
        o_obj = self.on_object()
        o_tile = self._screen.tile(self._x,self._y)
        if not o_obj.is_burnt():
            if o_obj and o_obj.is_flammable():
                o_obj.burn()
            elif o_obj and o_obj.is_llama():
                o_obj.hit(self._power)
            elif o_tile in lvl.FLAMMABLES:
                elt = self._screen.tile_object(self._x,self._y)
                elt.undraw()
                pic = 'sprites/ash.gif'
                elt = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
                elt.move((self._x-(self._screen._player._x-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                         (self._y-(self._screen._player._y-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
                elt.draw(self._screen._window)

                tile_pos = self._screen._level._pos(self._x,self._y)
                self._screen._level._map[tile_pos] = 0000
                self._screen._map_elts[tile_pos] = elt

                self._screen._player.raise_sprite()

        # Dematerialize projectile
        self.dematerialize()
        self._screen._window.update()   

class Spitball (Projectile):
    def __init__ (self, facing, mrange, power):
        Projectile.__init__(self, facing, mrange, power)
        imgs = [{'Left': 'sprites/W_spit.gif','Right': 'sprites/E_spit.gif','Up' : 'sprites/N_spit.gif','Down' : 'sprites/S_spit.gif'},
            {'Left': 'sprites/W_spit.gif','Right': 'sprites/E_spit.gif','Up' : 'sprites/N_spit.gif','Down' : 'sprites/S_spit.gif'}
        ]
        self._DIR_IMGS = imgs[power]
        self._facing = facing
        pic = self._DIR_IMGS[self._facing]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)


    def move_or_stop (self):
        def stop_now():
            self.stop()
            return True

        # Reached the border?
        if self._x == 0 and self._dx == -1:
            log(str(self)+' stopping at left border')
            return stop_now()        
        if self._x == LEVEL_WIDTH-1 and self._dx == 1:
            log(str(self)+' stopping at right border')
            return stop_now()
        if self._y == 0 and self._dy == -1:
            log(str(self)+' stopping at top border')
            return stop_now()
        if self._y == LEVEL_HEIGHT-1 and self._dy == 1:
            log(str(self)+' stopping at bottom border')
            return stop_now()

        # Reached an unwalkable tile?
        f_tile = self._screen._level._pos(self._x+self._dx,self._y+self._dy)
        tile_val = self._screen._level._map[f_tile]
        if tile_val in lvl.UNWALKABLES:
            log(str(self)+' stopping at unwalkable tile')
            return stop_now()

        # Reached an unwalkable and nonPlayer Thing?
        f_obj = self.facing_object()
        if f_obj and not f_obj.is_walkable() and not f_obj.is_player():
            log(str(self)+' stopping at unwalkable, nonPlayer Thing')
            return stop_now()

        # On Player?
        o_obj = self.on_object()
        if o_obj and o_obj.is_player():
            log(str(self)+' stopping on Player')
            return stop_now()


        # Else, move
        log(str(self)+' moving')
        self._x = self._x + self._dx
        self._y = self._y + self._dy
        
        # Shift sprite
        self.shift(self._dx*TILE_SIZE,self._dy*TILE_SIZE,False)
        
        # Update window so changes are visible
        self._screen._window.update()

        # Not done moving yet
        return False

    def stop (self):
        # Hit the player if possible
        self._range = 0
        o_obj = self.on_object()
        o_tile = self._screen.tile(self._x,self._y)
        if o_obj and o_obj.is_player():
            o_obj.hit(self._power)
        
        # Dematerialize projectile
        self.dematerialize()
        self._screen._window.update() 

class Door (Thing):
    def __init__ (self,description):
        Thing.__init__(self,'Door',description)
        pic = 'sprites/V_door.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        self._flammable = True

class BarricadeDoor(Thing):
    def __init__ (self,description):
        Thing.__init__(self,"Barricade Door",description)
        pic = 'sprites/V_barricade.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)

    def is_barricade_door (self):
        return True

class Pizza (Thing):
    def __init__ (self,description):
        Thing.__init__(self,"Pizza Slice",description)
        pic = 'sprites/bigger_pizza.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)

    def is_pizza (self):
        return True

class Vortex (Thing):
    def __init__ (self):
        Thing.__init__(self,"Vortex",'Where does it lead?')
        self._IMGS = {
            0: 'sprites/1_vortex.gif',
            1: 'sprites/2_vortex.gif',
            2: 'sprites/3_vortex.gif',
            3: 'sprites/4_vortex.gif'
        }
        self._state = 0;
        pic = self._IMGS[0]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)

    def is_vortex (self):
        return True

    def event (self,q):
        log("event for "+str(self))

        # cycle amongst the 4 states
        self._state = (self._state+1) % 4

        # draw new state
        p = self._screen._player
        self._sprite.undraw()
        pic = self._IMGS[self._state]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        self._sprite.move((self._x-(p._x-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                           (self._y-(p._y-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
        self._sprite.draw(self._screen._window)
        self.raise_or_lower_sprite() # So that sprite doesn't show up over the sidepanel 

        # Update window so changes are visible
        self._screen._window.update()

        # re-register event
        self.register(q,self._freq)


#
# Example of a kind of thing with its specific sprite
# (here, a rather boring gray rectangle.)
#
class Felix (Thing):
    def __init__ (self,description):
        Thing.__init__(self,"Felix",description)
        pic = 'sprites/other_felix.gif'
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)


#
# Characters represent persons and animals and things that move
# about possibly proactively
#
class Character (Thing):
    def __init__ (self,name,desc):
        Thing.__init__(self,name,desc)
        log("Character.__init__ for "+str(self))
        self._walkable = False
        rect = Rectangle(Point(1,1),
                         Point(TILE_SIZE-1,TILE_SIZE-1))
        rect.setFill("red")
        rect.setOutline("red")
        self._sprite = rect

    def turn (self,dx,dy):
        return False


    # A character has a move() method that you should implement
    # to enable movement

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy

        # Turn if applicable
        turned = self.turn(dx,dy)
        if turned:
            return

        # Trying to go out of bounds?
        if not (tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT):
            return

        # Trying to walk through an unwalkable tile?
        new_pos = self._screen._level._map[self._screen._level._pos(tx,ty)]
        if new_pos in lvl.UNWALKABLES:
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

    def is_character (self):
        return True

class Llama (Character):
    def __init__ (self,facing,intelligence,health,ax,ay):
        words = {0: 'dumb', 1: 'average', 2: 'smart'}
        Character.__init__(self,'Llama','a {} llama'.format(words[intelligence]))
        log("Llama.__init__ for "+str(self))
        self._ax = ax; # Anchor locations
        self._ay = ay;
        self._health = health # Stats
        self._intelligence = intelligence
        self._fb_range = 2
        self._fb_speed = 15
        self._wander_range = 7
        self._DIR_IMGS = {
            'Left': 'sprites/W_llama.gif',
            'Right': 'sprites/E_llama.gif',
            'Up' : 'sprites/N_llama.gif',
            'Down' : 'sprites/S_llama.gif'
        }
        self._facing = facing
        pic = self._DIR_IMGS[self._facing]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)


    def is_llama (self):
        return True

    def hit (self, power):
        log(str(self)+' gets hit for '+str(power+1))   
        self._health -= (power + 1)

        if self._health <= 0:
            self._screen.ded_llamas.append(self)
            self.burn()
            if set(self._screen.initial_llamas) == set(self._screen.ded_llamas):
                for thing in self._screen._things:
                    if thing.is_barricade_door():
                        thing.dematerialize()

    def event (self,q):
        log("event for "+str(self))

        if not self.is_burnt():
            if self._intelligence == 0:
                # If dumb llama: stand in place, spit if player 
                # is in front of you and within range.
                if random.randrange(4) == 0:
                    self.face_player()
                elif random.randrange(3) == 0:
                    self.shoot_at_player()
            elif self._intelligence == 1:
                # If average llama: move randomly within range, 
                # spit if player is in front of you and within range.
                if random.randrange(3) == 0:
                    dx,dy = random.choice(MOVE.values())
                    if abs(self._x+dx-self._ax) < self._wander_range and abs(self._y+dy-self._ay) < self._wander_range:
                        # If still within wander range, move
                        self.move(dx,dy)
                elif random.randrange(3) == 0:
                    self.shoot_at_player()
            elif self._intelligence == 2:
                # If smart llama: move towards player if they get 
                # within <x> tiles of you, spit if player is in 
                #front of you and within range.
                if random.randrange(3) == 0:
                    self.move_towards_player()
                elif random.randrange(2) == 0:
                    self.shoot_at_player()

            # Re-register event with same frequency if not a pile of ashes
            self.register(q,self._freq)

    def turn (self,dx,dy):
        fdx,fdy = MOVE[self._facing]
        p = self._screen._player

        if not (fdx == dx and fdy == dy):
            key = DIRECTIONS[(dx,dy)]
            self._facing = key
            self._sprite.undraw()
            pic = self._DIR_IMGS[self._facing]
            self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
            self._sprite.move((self._x-(p._x-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                               (self._y-(p._y-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
            self._sprite.draw(self._screen._window)
            self.raise_or_lower_sprite() # So that sprite doesn't show up over the sidepanel 

            # Update window so changes are visible
            self._screen._window.update()
            return True

        return False


    def move_towards_player (self):
        p = self._screen._player
        px = p._x
        py = p._y
        lx = self._x
        ly = self._y

        if (abs(px-lx) < self._wander_range) and (abs(py-ly) < self._wander_range):
            distx = px - lx
            disty = py - ly
            choices = []
            if distx:
                choices.append((sign(distx),0))
            if disty:
                choices.append((0,sign(disty)))
            if choices:
                dx,dy = random.choice(choices)
                self.move(dx,dy)


    def face_player (self):
        # turn to face player
        lx = self._x
        ly = self._y
        px = self._screen._player._x
        py = self._screen._player._y

        new_facing = False
        if abs(px-lx) > abs(py-ly):
            if px-lx > 0:
                new_facing = 'Right'
            else:
                new_facing = 'Left'
        else:
            if py-ly > 0:
                new_facing = 'Down'
            else:
                new_facing = 'Up'

        # If you actually turned, replace with new image
        if self._facing != new_facing:
            self._facing = new_facing
            self._sprite.undraw()
            pic = self._DIR_IMGS[self._facing]
            self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
            self._sprite.move((self._x-(px-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                               (self._y-(py-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
            self._sprite.draw(self._screen._window)

            # Update window so changes are visible
            self._screen._window.update()


    def shoot_at_player(self):
        # Shoot player if in range
        lx = self._x
        ly = self._y
        px = self._screen._player._x
        py = self._screen._player._y

        if (abs(px-lx) < self._fb_range+3) and (abs(py-ly) < self._fb_range+3):
            # Am I facing the border?
            dx,dy = MOVE[self._facing]
            if not (self._x+dx >= 0 and self._x+dx <= LEVEL_WIDTH-1 and self._y+dy >= 0 and self._y+dy <= LEVEL_HEIGHT-1):
                return

            # Am I facing an unwalkable tile?
            f_tile_val = self._screen.tile(self._x+dx,self._y+dy)
            if f_tile_val in lvl.UNWALKABLES:
                return 

            # Am I facing an unwalkable, nonPlayer object?
            f_obj = self.facing_object()
            if f_obj and not f_obj.is_walkable() and not f_obj.is_player():
                return

            # Else, shoot spitball
            Spitball(
                self._facing, self._fb_range, 0).register(
                self._screen._q, self._fb_speed).materialize(
                self._screen, self._x+dx, self._y+dy, px, py
            )

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
        self._flammable = True
        self._takable = True

    # A helper method to register the Rat with the event queue
    # Call this method with a queue and a time delay before
    # the event is called
    # Note that the method returns the object itself, so we can
    # use method chaining, which is cool (though not as cool as
    # bowties...)



    # this gets called from event queue when the time is right

    def event (self,q):
        log("event for "+str(self))

        if not self.is_burnt():
            # Should I move this time?
            if random.randrange(self._restlessness) == 0:
                self.move_somewhere()   

            # Re-register event with same frequency if not a pile of ashes
            self.register(q,self._freq)

    def move_somewhere (self):
        dx,dy = random.choice(MOVE.values())
        self.move(dx,dy)




#
# The Player character
#
class Player (Character):
    def __init__ (self,name,facing,health,fb_range,fb_speed,fb_power):
        Character.__init__(self,name,"Yours truly")
        log("Player.__init__ for "+str(self))

        self._DIR_IMGS = {
            'Left': 'sprites/W_smaller_duck.gif',
            'Right': 'sprites/E_smaller_duck.gif',
            'Up' : 'sprites/N_smaller_duck.gif',
            'Down' : 'sprites/S_smaller_duck.gif'
        }
        self._facing = facing
        pic = self._DIR_IMGS[self._facing]
        self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
        
        self._inventory = []
        self._inventory_elts = {}

        self._fb_range = fb_range
        self._fb_speed = fb_speed
        self._fb_power = fb_power

        self._max_health = health
        self._health = health
        self._h_obj = Text(Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL/2+40,70),str(health))
        self._h_obj.setSize(16)
        self._h_obj.setFill("blue")

        # config = {}
        # for option in options:
        #     config[option] = DEFAULT_CONFIG[option]
        # self.config = config

    def is_player (self):
        return True

    def update_health (self):
        self._h_obj.setText(str(self._health))

    def die (self):
        log('Player died, game is lost')
        t = Text(Point(WINDOW_WIDTH/2,WINDOW_HEIGHT/2),'YOU LOST!')
        t.setSize(36)
        t.setTextColor('red')
        t.draw(self._screen._window)
        self._screen._window.getKey()
        time.sleep(.5)
        exit(0)

    def hit (self, power):
        log(str(self)+' gets hit for '+str(power+1))   
        self._health -= (power + 1)

        self.update_health()

        if self._health <= 0:
            self.die()

    def shoot (self):
        # Am I facing the border?
        dx,dy = MOVE[self._facing]
        if not (self._x+dx >= 0 and self._x+dx <= LEVEL_WIDTH-1 and self._y+dy >= 0 and self._y+dy <= LEVEL_HEIGHT-1):
            return

        # Am I facing an unwalkable and unflammable tile?
        f_tile_val = self._screen.tile(self._x+dx,self._y+dy)
        if f_tile_val in lvl.UNWALKABLES and f_tile_val not in lvl.FLAMMABLES:
            return 

        # Am I facing a nonflammable, nonLlama object?
        f_obj = self.facing_object()
        if f_obj and not f_obj.is_walkable() and not f_obj.is_flammable() and not f_obj.is_llama():
            return

        # Else, shoot fireball
        Fireball(
            self._facing, self._fb_range, self._fb_power).register(
            self._screen._q, self._fb_speed).materialize(
            self._screen, self._x+dx, self._y+dy, self._x, self._y
        )

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy

        fdx,fdy = MOVE[self._facing]

        # Turn if not facing direction told to go
        if not (fdx == dx and fdy == dy):
            key = DIRECTIONS[(dx,dy)]
            self._facing = key
            self._sprite.undraw()
            pic = self._DIR_IMGS[self._facing]
            self._sprite = Image(Point(TILE_SIZE/2,TILE_SIZE/2),pic)
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
        if new_pos in lvl.UNWALKABLES:
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
            fg.setFill('white')
            fg.draw(self._screen._window)
            self._inventory_elts[inv_num] = fg

    def interact (self):
        # Am I facing a Thing?
        thing = self.facing_object()
        if thing:
            self._screen.show_text(thing.description())

            if thing.is_pizza():
                thing.dematerialize()

                # increase stats
                self._max_health += 1
                self._health = self._max_health
                self.update_health()
                self._screen.show_text('Health goes up by 1!')

                self._fb_power += 1
                self._screen.show_text('Fireball power goes up by 1!')

                self._fb_range += 2
                self._screen.show_text('Fireball range goes up by 2!')

                self._fb_speed -= 3
                self._screen.show_text('Fireball speed goes up by 3!')                

                # make vortex appear
                self._screen.show_text('A swirling vortex appears nearby, and you can smell a hint of pepperoni...')
                Vortex().register(self._screen._q,20).materialize(self._screen,48,48)

            if thing.is_vortex():
                self._screen.show_text('You feel the next slice of pizza calling to you through the vortex.')
                self._screen.show_text('You take a deep breath and step through.')
                self._screen._DONE = True;




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
    def __init__ (self, num):
        # size = LEVEL_WIDTH * LEVEL_HEIGHT
        # the_map = [0] * size
        # for i in range(100):
        #     the_map[random.randrange(size)] = 1
        # for i in range(50):
        #     the_map[random.randrange(size)] = 2
        the_map = lvl.LEVELS[num]
        self._map = the_map

    def _pos (self,x,y):
        return x + (y*LEVEL_WIDTH);

    # return the tile value at a given tile position in the level
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
    def __init__ (self,level,window,q,p,cx,cy):
        self._q = q
        self._player = p
        self._level = level
        self._window = window
        self._cx = cx    # the initial center tile position 
        self._cy = cy    #  of the screen
        self._map_elts = {}
        self._things = []
        self.initial_llamas = []
        self.ded_llamas = []
        self._DONE = False


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

                pic = lvl.SPRITES[cell]
                elt = Image(Point(sx-dx+TILE_SIZE/2, sy-dy+TILE_SIZE/2), pic)

                elt.draw(window)

                self._map_elts[ind] = elt

    # return the tile value at a given tile position
    def tile (self,x,y):
        return self._level.tile(x,y)

    # return the graphics object at a given tile position in the level
    def tile_object (self,x,y):
        return self._map_elts[self._level._pos(x,y)]

    # add a thing to the screen at a given position
    def add (self,item,x,y,cx=-1,cy=-1):
        if (cx == -1) or (cy == -1):
            cx = self._cx
            cy = self._cy
        # first, move object into given position
        item.sprite().move((x-(cx-(VIEWPORT_WIDTH-1)/2))*TILE_SIZE,
                           (y-(cy-(VIEWPORT_HEIGHT-1)/2))*TILE_SIZE)
        item.sprite().draw(self._window)
        # then, add to list of all objects
        self._things.append(item)

        if item.is_llama():
            self.initial_llamas.append(item)

    def delete (self,item):
        item.sprite().undraw()
        self._things.remove(item)

    # helper method to get at underlying window
    def window (self):
        return self._window

    # shift viewport when player moves
    def shift_viewport (self, dx, dy):
        # Move tiles in the specified direction
        for key in self._map_elts:
            tile = self._map_elts[key]
            tile.move(dx*TILE_SIZE,dy*TILE_SIZE)
            
            # Push down if over right sidepanel
            if key > -1:
                self.raise_or_lower_tile(key)

        # Move Things as well so they appear to not move
        for thing in self._things:
            if not thing.is_player():
                thing.shift(dx*TILE_SIZE,dy*TILE_SIZE)

   
    def raise_or_lower_tile (self, ind):
        p = self._player
        tile_x,tile_y = self._level.ind_to_pos(ind)
        tile_x = tile_x/TILE_SIZE
        tile_y = tile_y/TILE_SIZE

        tile = self.tile_object(tile_x,tile_y)
        x_dist = tile_x - p._x
        if x_dist > (VIEWPORT_WIDTH-1)/2:
            self.lower_tile(tile)
        else:
            self.raise_tile(tile)
            p.raise_sprite()

    def raise_tile (self, tile):
        tile.canvas.tag_raise(tile.id)

    def lower_tile (self, tile):
        tile.canvas.tag_lower(tile.id)


    def show_text (self, text):
        # White box as a background
        bg = Rectangle(Point(0,WINDOW_HEIGHT-50), Point(WINDOW_WIDTH,WINDOW_HEIGHT))
        bg.setOutline('white')
        bg.setFill('white')
        bg.draw(self._window)
        # Description
        fg = Text(Point(WINDOW_WIDTH/2,WINDOW_HEIGHT-25),text)
        fg.setSize(16)
        fg.setFill('black')
        fg.draw(self._window)
        # Wait until a key is pressed, then undraw background and description
        key = self._window.getKey()
        fg.undraw()
        bg.undraw()



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
            (dx,dy) = MOVE[key]
            self._player.move(dx,dy)
        if key == 'f':
            self._player.take()
        if key == 'e':
            self._player.interact()
        if key == 'space':
            self._player.shoot()
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

    fg = Text(Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL/2,70),'Health:  ')
    fg.setSize(16)
    fg.setFill("blue")
    fg.draw(window)    

    fg = Text(Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL/2,100),'Inventory')
    fg.setSize(16)
    fg.setFill("white")
    fg.draw(window)

    fg = Text(Point(WINDOW_WIDTH+WINDOW_RIGHTPANEL/2,100),'________')
    fg.setSize(16)
    fg.setFill("white")
    fg.draw(window)


def sign (x):
    return (x > 0) - (x < 0)

#
# The main function
# 
# It initializes everything that needs to be initialized
# Order is important for graphics to display correctly
# Note that autoflush=False, so we need to explicitly
# call window.update() to refresh the window when we make
# changes
#


def play_level_0 (window):
    level = Level(0)
    log ("level created")

    q = EventQueue()

    p = Player("...what's your name, bub?...", 'Right', 3, 3, 10, 0)
    px = 4
    py = 10

    scr = Screen(level,window,q,p,px,py)
    log ("screen created")

    Door("a dry, wooden door with no doorknob").materialize(scr,11,10)
    BarricadeDoor("the front door of the llamas' spikey fortress").materialize(scr,40,44)

    Felix("Halp! Bad llamas haz take my nommy pizza! They go path!").materialize(scr,12,9)

    l1x,l1y = (39,43)
    l2x,l2y = (39,45)
    l = Llama('Left',0,1,l1x,l1y).register(q, 100).materialize(scr,l1x,l1y)
    ll = Llama('Left',2,3,l2x,l2y).register(q, 100).materialize(scr,l2x,l2y)

    Pizza('You take back the stolen slice of pizza. You feel your powers increasing.').materialize(scr,45,41)

    create_panel(window)

    p.materialize(scr,px,py)

    q.enqueue(1,CheckInput(window,p))

    # print scr._things

    while not scr._DONE:
        # Grab the next event from the queue if it's ready
        q.dequeue_if_ready()
        # Time unit = 10 milliseconds
        time.sleep(0.01)

    bg = Rectangle(Point(0,0),Point(TILE_SIZE*(LEVEL_WIDTH),TILE_SIZE*(LEVEL_HEIGHT)))
    bg.setFill('black')
    bg.setOutline('black')
    bg.draw(window)

    t = Text(Point(WINDOW_WIDTH/2,WINDOW_HEIGHT/2),'to be continued...')
    t.setSize(36)
    t.setTextColor('white')
    t.draw(window)
    window.getKey()
    time.sleep(.5)
    exit(0)


def main ():

    window = GraphWin("Olinland Redux", 
                      WINDOW_WIDTH+WINDOW_RIGHTPANEL, WINDOW_HEIGHT,
                      autoflush=False)


    play_level_0(window)



if __name__ == '__main__':
    main()
    