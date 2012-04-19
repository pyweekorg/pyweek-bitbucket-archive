import sys
import os
import math

import pyglet
from pyglet.window.key import *
import cocos
from cocos import tiles
from cocos.director import director

class WitchSprite(cocos.actions.ActionSprite):
    dy = 0
    t = 0
    direction = 0

    STANDING = 'standing'
    WALK = 'walk'
    STRIDE = 'stride'
    FLY= 'fly'
    LEAP = 'leap'
    MOUSE = 'mouse'
    PUFF1 = 'puff1'
    PUFF2 = 'puff2'
    mode = STANDING

    target = None

    def fix_image(self):
        # make sure image is correct
        img = witch_images[self.mode +
            {-1: '-left', 0: '', 1: '-right'}[self.direction]]
        if img is not self.image:
            self.image = img
            #self.width = img.width
            #self.height = img.height

    def to_puff(self, target):
        self.target = target
        self.mode = self.PUFF1
        self.direction = 0
        midbottom = self.get_rect().midbottom
        self.fix_image()
        r = self.get_rect()
        r.midbottom = midbottom
        self.position = r.position
        self.t = .25

    def is_on_ground(self):
        x, y = self.get_rect().midbottom
        y -= 1
        cell = director.scene.level.get(*map(int, (x, y)))
        if cell is None or cell.tile is None: return False
        g = cell.tile.properties.get
        return g('top')

    def update(self, dt):
        # puff animation is special-case
        if self.mode in (self.PUFF1, self.PUFF2):
            self.t -= dt
            if self.t < 0:
                self.mode = {self.PUFF1: self.PUFF2,
                    self.PUFF2: self.target}[self.mode]
                midbottom = self.get_rect().midbottom
                self.fix_image()
                r = self.get_rect()
                r.midbottom = midbottom
                self.position = r.position
                if self.mode is self.PUFF2:
                    self.t = .25
                    #if self.target is self.MOUSE: self.bottom -= 50
                    #else: self.bottom += 50
                    self.direction = 1
                else:
                    self.target = None
            return

        # save off for later
        r = self.get_rect()
        o_l, o_r, o_t, o_b = r.left, r.right, r.top, r.bottom

        # move left/right
        if keyboard[MOTION_RIGHT] or keyboard[MOTION_LEFT]:
            self.direction = keyboard[MOTION_RIGHT] - keyboard[MOTION_LEFT]
        dx = (keyboard[MOTION_RIGHT] - keyboard[MOTION_LEFT]) * 250 * dt

        x, y = self.position

        # change mode
        if keyboard[MOTION_UP] and self.mode in (self.WALK, self.STRIDE,
                self.STANDING):
            self.mode = self.LEAP
            self.t = .1
        elif keyboard[MOTION_UP] and self.mode is self.MOUSE:
            self.to_puff(self.WALK)
            return
        elif keyboard[MOTION_DOWN] and self.mode in (self.FLY, self.LEAP) and \
                self.is_on_ground():
            self.mode = self.WALK
            self.t = .5
        elif keyboard[MOTION_DOWN] and self.mode in (self.WALK, self.STRIDE,
                self.STANDING):
            if self.t:
                self.t -= dt
                if self.t < 0: self.t = 0
            else:
                self.to_puff(self.MOUSE)
            return

        # walking / flying
        gravity = 25
        if self.mode == self.STANDING and dx:
            self.mode = self.WALK
        if self.mode in (self.WALK, self.STRIDE):
            if not dx:
                self.t = 0
                self.direction = 0
                self.mode = self.STANDING
            elif self.t <= 0:
                self.t = .25
                self.mode = {self.STRIDE: self.WALK,
                    self.WALK: self.STRIDE}[self.mode]
            else:
                self.t -= dt
        elif self.mode in (self.FLY, self.LEAP):
            if not self.direction: self.direction = 1
            gravity = 0
            if self.mode is self.FLY:
                self.dy = (keyboard[MOTION_UP] - keyboard[MOTION_DOWN]) * 250 * dt
            elif self.mode is self.LEAP:
                self.t -= dt
                if self.t < 0:
                    self.t = 0
                    y += 74        # thanks, Phil ;)
                    self.mode = self.FLY
        elif self.mode is self.MOUSE:
            if not self.direction: self.direction = 1

        # handle movement
        self.dy -= gravity * dt
        self.dy = min(300, max(-300, self.dy))
        self.position = (x + dx, y + self.dy)

        # handle collision with world (inspired by PGU)
        r = self.get_rect()
        for point in (r.bottomleft, r.bottomright, r.topleft,
                r.topright, r.midleft, r.midright, r.midbottom,
                r.midtop):
            cell = director.scene.level.get(*map(int, point))
            if cell is None or cell.tile is None: continue
            g = cell.tile.properties.get

            if (g('top') and o_b >= cell.top and r.bottom < cell.top):
                r.bottom = cell.top
                gravity = 0
                if self.dy < 0: self.dy = 0
            if (g('left') and o_r <= cell.left and r.right > cell.left):
                r.right = cell.left
                if self.mode in (self.WALK, self.STRIDE):
                    self.mode = self.STANDING
                self.t = 0
            if (g('right') and o_l >= cell.right and r.left < cell.right):
                r.left = cell.right
                if self.mode in (self.WALK, self.STRIDE):
                    self.mode = self.STANDING
                self.t = 0
            if (g('bottom') and o_t <= cell.bottom and r.top > cell.bottom):
                r.top = cell.bottom

        self.position = r.position

        # picking fruit
        cell = director.scene.level.get(*map(int, r.midbottom))
        if cell is not None and cell.tile is not None and \
                cell.tile.properties.get('fruit'):
            print 'GOT FRUIT'
            cell.tile = resource['tree']

        self.fix_image()

# open window
#director.init(width=700, height=440)
w = director.init(fullscreen=True)
w.set_exclusive_mouse()

keyboard = KeyStateHandler()
director.window.push_handlers(keyboard)

class SaveHandler(object):
    def on_text(self, text):
        if text != 's': return pyglet.window.event.EVENT_UNHANDLED
        image = pyglet.image.BufferImage().get_raw_image()
        fn = 'screenshot.png'
        n = 1
        while os.path.exists(fn):
            fn = 'screenshot' + str(n) + '.png'
            n += 1
        print "Saving to '%s'"%fn
        image.save(fn)
#w.push_handlers(SaveHandler())

# load the sprites & level
witch_images = {'fly-left': None, 'standing': None, 'walk-right': None,
    'fly-right': None, 'stride-left': None, 'leap-left': None,
    'mouse-right': None, 'mouse-left': None, 'standing-right': None,
    'standing-left': None, 'stride-right': None, 'leap-right': None,
    'walk-left': None, 'puff1': None, 'puff2': None}
for name in witch_images:
    witch_images[name] = pyglet.resource.image('witch-' + name + '.png')

class GameScene(cocos.scene.Scene):
    def __init__(self, level):
        super(GameScene, self).__init__()

        self.manager = tiles.ScrollingManager(director.window)
        self.level = level
        self.manager.append(level)

        sprite_layer = tiles.ScrollableLayer()
        self.witch = WitchSprite(witch_images['standing'])
        sprite_layer.add(self.witch)
        self.manager.append(sprite_layer)

        self.add(level, z=0)
        self.add(sprite_layer, z=1)

        # set witch start
        r = self.witch.get_rect()
        for col in self.level.cells:
            for cell in col:
                if 'player-start' in cell.properties:
                    r.midbottom = cell.midbottom
                    self.witch.position = r.position

        pyglet.clock.schedule(self.witch.update)

        self.do(FocusOnWitch())

class FocusOnWitch(cocos.actions.Action):

    def done(self): return False

    def step(self, dt):
        r = self.target.witch.get_rect()
        x, y = r.center
        self.target.manager.set_focus(int(x), int(y))

pyglet.gl.glClearColor(.3, .3, .3, 1)
resource = tiles.load('level1.xml')
director.run(GameScene(resource['level']))

