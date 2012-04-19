import sys
import os
import collections
import random

import pyglet
from pyglet.gl import *
import cocos
from cocos import tiles, rect
from cocos.director import *
from cocos.actions import *

from constants import *

import collide
import sounds

def centered_image(filename):
    image = pyglet.resource.image(filename)
    image.anchor_x = image.width//2
    image.anchor_y = image.height//2
    return image


class RobotLayer(collide.Collider, tiles.ScrollableLayer):

    def __init__(self):
        super(RobotLayer, self).__init__()

        self.im_body = centered_image('robot-body.png')
        self.im_foot = centered_image('robot-foot.png')
        self.im_foot.anchor_y=0

        # XXX fix when Cocos gets depth-sorting
        #self.im_head = centered_image('robot-head.png')

        # stand-ins until above is fixed
        self.im_head = centered_image('robot-nonplussed.png')
        self.im_head_angry = centered_image('robot-angry.png')
        self.im_head_sheesh = centered_image('robot-sheesh.png')
        self.im_head_lr = centered_image('robot-look-right.png')
        self.im_head_ll = centered_image('robot-look-left.png')
        self.im_head_surp = centered_image('robot-surprised.png')
        self.im_head_zap = centered_image('robot-angry-laser.png')

        self.body = ActionSprite(self.im_body)
        self.add(self.body, z=0, name='body')
        self.body.rotation = 5

        # HEAD
        self.head = ActionSprite(self.im_head)
        self.add(self.head, z=1, name='head')
        # XXX fix when Cocos gets depth-sorting
        #self.lant = ActionSprite(self.im_lant)
        #self.head.add(self.lant, (-20, self.head.height//2), z=-1, name='lant')
        #self.rant = ActionSprite(self.im_rant)
        #self.head.add(self.rant, (20, self.head.height//2), z=-1, name='rant')

        # FEET
        self.left_foot = ActionSprite(self.im_foot)
        self.add(self.left_foot, (-self.body.width//2, 0), z=1, name='lfoot')
        self.mid_foot = ActionSprite(self.im_foot)
        self.add(self.mid_foot, (0, 0), z=1, name='mfoot')
        self.right_foot = ActionSprite(self.im_foot)
        self.add(self.right_foot, (self.body.width//2, 0), z=1, name='rfoot')

        # EYES
        # XXX fix when Cocos gets depth-sorting
        self.left_iris_position = (-20, -26) # relative to head
        #self.im_iris = centered_image('robot-iris.png')
        #self.im_brow = centered_image('robot-brow.png')
        #self.im_lant = centered_image('robot-left-antenna.png')
        #self.im_lant.anchor_y=0
        #self.im_rant = centered_image('robot-right-antenna.png')
        #self.im_rant.anchor_y=0
        #self.liris = ActionSprite(self.im_iris)
        #self.head.add(self.liris, (-22, 4), z=2, name='liris', color=(0,0,0))
        #self.riris = ActionSprite(self.im_iris)
        #self.head.add(self.riris, (22, 2), z=2, name='riris', color=(0,0,0))
        #self.lbrow = ActionSprite(self.im_brow)
        #self.head.add(self.lbrow, (-26, 33), z=2, name='lbrow')
        #self.rbrow = ActionSprite(self.im_brow)
        #self.head.add(self.rbrow, (22, 23), z=2, name='rbrow')

        self.dx = self.dy = 0

        self.keyboard = collections.defaultdict(list)

        self.width = self.body.width
        self.height = self.head.height + self.head.x


    def on_enter(self):
        self.reset_parts()
        self.parent.do(Delay(2) + CallFunc(self.show_find_friend_bubble))
        self.enable_step()

    def reset_parts(self):
        self.flush()
        self.left_foot.position = (-self.body.width//2, 0)
        self.mid_foot.position = (0, 0)
        self.right_foot.position = (self.body.width//2, 0)
        # XXX fix when Cocos gets layers
        #self.head.position = (0, 150)
        self.head.position = (0, 180)
        self.body.position = (0, 80)

    def on_key_press(self, symbol, modifiers):
        self.keyboard[symbol] = True
        if symbol == pyglet.window.key.Z:
            self.do_zap()
    def on_key_release(self, symbol, modifiers):
        self.keyboard[symbol] = False


    #
    # SPEECH BUBBLES
    #
    _find_friend_shown = False
    def show_find_friend_bubble(self):
        '''Show a "speech" bubble to indicate what to do
        '''
        if self._find_friend_shown: return
        self._find_friend_shown = True
        sounds.speak1.play()
        bubble = pyglet.resource.image('find-friend-bubble.png')
        self.show_bubble(bubble)

    _use_zap_shown = False
    def show_use_zap_bubble(self):
        if self._use_zap_shown: return
        self._use_zap_shown = True
        sounds.speak2.play()
        bubble = pyglet.resource.image('use-zap-bubble.png')
        self.show_bubble(bubble)

    _speech_bubble = None
    def show_bubble(self, image):
        if self._speech_bubble is not None:
            self.remove(self._speech_bubble)
        bubble = ActionSprite(image)
        self.add(bubble, (0, 240))
        self._speech_bubble = bubble
        self.parent.do(Delay(2) + CallFunc(self.clear_bubble))

    def clear_bubble(self):
        # already cleared?
        if self._speech_bubble is None:
            return
        self.remove(self._speech_bubble)
        self._speech_bubble = None


    _zapping = False
    zap_line = None
    def do_zap(self):
        if self._zapping:
            return
        self._zapping = True

        def get_target(cell):
            if cell.tile.properties.get('top'):
                return 'top', cell.midtop
            elif cell.tile.properties.get('left'):
                return 'left', cell.midleft
            elif cell.tile.properties.get('right'):
                return 'right', cell.midright
            return None, None

        # find a target
        cells = self.parent.level.get_visible()
        targets = [cell for cell in cells
            if cell.tile and cell.tile.properties.get('zap-target')]

        if targets:
            cell = random.choice(targets)
            side, aim = get_target(cell)
            self.zap_cell = cell
        else:
            self.zap_cell = None
            random.shuffle(cells)
            while 1:
                cell = cells.pop()
                if not cell.tile: continue
                side, aim = get_target(cell)
                if aim is not None: break
            else:
                # no zap :(
                return

        self.zap_target = aim

        sounds.laser.play()

        # change iris color
        # XXX layer stuff self.liris.color = (255, 0, 0)
        self.head.image = self.im_head_zap

        direction = dict(top='up', left='right', right='left')[side]
        self.parent.effects.add_smoke(aim[0], aim[1], direction=direction)

        # register this with the parent so it *is not flushed*
        self.parent.do(Delay(.5) + CallFunc(self.stop_zap))

    def stop_zap(self):
        # XXX layer stuff self.liris.color = (0, 0, 0)
        self._zapping = False
        self.head.image = self.im_head

        if self.zap_cell is None:
            return
        # zap all connected walls
        level = self.parent.level
        def zap_neighbors(cell):
            for direction in (level.UP, level.DOWN, level.LEFT, level.RIGHT):
                n = level.get_neighbor(cell, direction)
                if n.tile and n.tile.properties.get('zap-target'):
                    n.tile = None
                    zap_neighbors(n)
        self.zap_cell.tile = None
        zap_neighbors(self.zap_cell)
        self.parent.level.set_dirty()

    def draw(self):
        x, y = self.position

        glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT)
        glColor4f(0, 0, 0, 1)
        glEnable(GL_LINE_SMOOTH)

        glLineWidth(2)

        glBegin(GL_LINES)
        sx, sy = self.left_foot.position
        by = self.body.position[1]
        # XXX adjust for body angle
        glVertex2f(sx, sy+14)
        glVertex2f(sx+40, by-30)

        sx, sy = self.mid_foot.position
        glVertex2f(sx, sy+14)
        glVertex2f(sx+10, by-35)

        sx, sy = self.right_foot.position
        glVertex2f(sx, sy+14)
        glVertex2f(sx-20, by-40)
        glEnd()

        # draw the laser zap if required
        if self._zapping:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            hx, hy = self.head.position
            # XXX layers stuff lx, ly = self.liris.position
            lx, ly = self.left_iris_position
            zx, zy = self.zap_target

            # zap!
            glBegin(GL_LINES)
            glColor4f(1, 0, 0, .5)
            glVertex2f(hx + lx, hy + ly)
            glVertex2f(zx - x, zy - y)
            glEnd()

            glLineWidth(4)
            glBegin(GL_LINES)
            glColor4f(1, .5, .1, .2)
            glVertex2f(hx + lx, hy + ly)
            glVertex2f(zx - x, zy - y)
            glEnd()

            glLineWidth(8)
            glBegin(GL_LINES)
            glColor4f(1, .5, .1, .2)
            glVertex2f(hx + lx, hy + ly)
            glVertex2f(zx - x, zy - y)
            glEnd()

        glPopAttrib()

    def on_exit(self):
        self.disable_step()

    JUMP_SPEED = 1000

    _jumping = False
    def do_jump(self, direction):
        if self._jumping or self._landing: return
        self.reset_parts()
        self._jumping = True

        self.dy = self.JUMP_SPEED

        # animate the jump
        self.head.do(Jump(10, 0, 1, .5))
        self.left_foot.do(Jump(-20, 0, 1, .2))
        self.mid_foot.do(Jump(-20, 0, 1, .2))
        self.right_foot.do(Jump(-20, 0, 1, .2))

    _landing = False
    def do_land(self, dy):
        self._jumping = False
        if self._landing: return
        self.reset_parts()
        self._landing = True
        self.do(Delay(.2) +
            CallFuncS(lambda self: setattr(self, '_landing', False)))
        self.head.do(Jump(-10, 0, 1, .2))
        self.body.do(Jump(-20, 0, 1, .2))

    _anim_surprise = False
    def do_surprise(self):
        if self._anim_surprise: return
        self._anim_surprise = True
        self.lbrow.do(MoveBy((0, 20), .1) + Delay(.2) + MoveBy((0, -20), .3))
        self.rbrow.do(MoveBy((0, 20), .1) + Delay(.2) + MoveBy((0, -20), .3))
        self.do(Delay(.6) +
            CallFuncS(lambda self: setattr(self, '_anim_surprise', False)))

    def step(self, dt):
        self.dx = 0
        if self.keyboard[pyglet.window.key.MOTION_LEFT]:
            self.dx -= 400
        if self.keyboard[pyglet.window.key.MOTION_RIGHT]:
            self.dx += 400
        if not self._zapping:
            if self.dx > 0:
                if self.head.image is not self.im_head_lr:
                    self.head.image = self.im_head_lr
            elif self.dx < 0:
                if self.head.image is not self.im_head_ll:
                    self.head.image = self.im_head_ll
            else:
                if self.head.image is not self.im_head:
                    self.head.image = self.im_head

        level = self.parent.level

        o_x, o_y = x, y = self.position

        odx, ody = self.dx, self.dy

        # move this sprite
        self.dy -= 2000 * dt
        self.dy = min(self.JUMP_SPEED, max(-500, self.dy))
        y += self.dy * dt
        x += self.dx * dt

        # handle collision with world (inspired by PGU)
        width = self.body.width
        height = self.head.height + self.head.x
        left = x - width/2
        r = rect.Rect(left, y, width, height)
        o_l = o_x - width/2
        o_b = o_y
        o_r = o_l + width
        o_t = o_b + height
        for point in (r.midleft, r.bottomleft, r.midbottom, r.bottomright,
                r.midright):
            cell = level.get(*map(int, point))
            if cell is None or cell.tile is None: continue
            self.do_collision(cell, r, o_b, o_t, o_l, o_r, self.dy, ody, self.dx, odx)

        self.position = (int(r.x + width/2), int(r.y))

        ball = self.parent.ball.ball

        # handle kick - XXX handle when ball was inside player last update
        sx, sy = self.position
        y = sy
        footw = self.left_foot.width

        if y >= ball.y and y < ball.y + ball.height:
            lhs = sx + self.left_foot.position[0]
            rhs = sx + self.right_foot.position[0]
            if lhs < ball.x + ball.width and lhs > ball.x:
                if self.dx < 0: speed = 1000
                elif self.dx > 0: speed = 200
                else: speed = 600
                ball.dx = -600
                ball.dy = speed
                ball.resting = False
                sounds.kick.play()

            elif rhs < ball.x + ball.width and rhs > ball.x:
                if self.dx > 0: speed = 1000
                elif self.dx < 0: speed = 200
                else: speed = 600
                ball.dx = 600
                ball.dy = speed
                ball.resting = False
                sounds.kick.play()

        # detect whether to show the use-zap speech bubble
        if not self._use_zap_shown:
            for cell in self.parent.level.get_visible():
                if cell.tile and cell.tile.properties.get('zap-target'):
                    self.show_use_zap_bubble()
                    break


    def on_text_motion(self, motion):
        if motion == pyglet.window.key.MOTION_UP:
            self.do_jump(self.dx)
            return True


