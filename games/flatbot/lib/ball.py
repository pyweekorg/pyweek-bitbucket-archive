
import pyglet

from cocos import tiles, rect
from cocos.actions import *

from constants import *

import collide
import sounds

class BallLayer(collide.Collider, tiles.ScrollableLayer):
    def __init__(self):
        super(BallLayer, self).__init__()

        self.im = pyglet.resource.image('ball.png')
        self.ball = ActionSprite(self.im)
        self.ball.resting = False
        self.ball.dx = self.ball.dy = 0

        self.add(self.ball, (600, 300))

        buddy = pyglet.resource.image('robot-buddy.png')
        self.buddy = ActionSprite(buddy)
        self.add(self.buddy, (128*32, 128*3))

    def on_enter(self):
        self.enable_step()

    def on_exit(self):
        self.disable_step()

    def do_land(self, dy):
        ball = self.ball
        # bounce
        ball.dy = dy / -2
        if abs(ball.dy) <= 50:
            ball.dy = 0
            ball.resting = True
        else:
            ball.resting = False
            ball.dy += GRAVITY

    def do_hitwall(self, dx):
        ball = self.ball
        # bounce
        ball.dx = dx / -2

    def step(self, dt):
        ball = self.ball
        level = self.parent.level

        o_x, o_y = x, y = ball.position
        odx, ody = ball.dx, ball.dy

        # move this sprite
        ball.dy -= 2000 * dt
        y += ball.dy * dt
        x += ball.dx * dt

        # handle collision with world (inspired by PGU)
        width = ball.width
        height = ball.height
        r = rect.Rect(x, y, width, height)
        o_r = o_x + width
        o_t = o_y + height
        for point in (r.bottomleft, r.bottomright, r.topleft, r.topright):
            cell = level.get(*map(int, point))
            if cell is None or cell.tile is None: continue
            self.do_collision(cell, r, o_y, o_t, o_x, o_r,
                ball.dy, ody, ball.dx, odx)

        self.ball.position = (int(r.x), int(r.y))

        br = self.buddy.get_rect()
        if r.intersects(br):
            self.buddy.do(Jump(64, 0, 3, 1) + CallFuncS(self.parent.level_end))
            sounds.happy.play()
            ball.dx = 0
            self.disable_step()

        if ball.resting:
            ball.dx -= ball.dx / 8.

