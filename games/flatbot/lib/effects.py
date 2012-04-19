import random; rr = random.randrange

import pyglet
from pyglet.gl import *
import cocos
from cocos import tiles
from cocos.director import director

class Particle(object):
    def __init__(self, x, y, dy, size):
        self.x, self.y, self.dy, self.size = x, y, dy, size
        self.frame = 0

class EffectsLayer(tiles.ScrollableLayer):
    def on_enter(self):
        self.pimg = pyglet.resource.image('particle.png')
        self.pimg.anchor_x = self.pimg.width//2
        self.pimg.anchor_y = self.pimg.height//2
        self._effects = []
        self.enable_step()

    def on_leave(self):
        self.disable_step()

    def add_smoke(self, x, y, amount=10, direction='up'):
        self._effects.append(SmokeEffect(self.batch, self.pimg, x, y,
            amount, direction))

    def step(self, dt):
        for effect in list(self._effects):
            if effect.step(dt):
                self._effects.remove(effect)

class SmokeEffect(object):
    def __init__(self, batch, image, x, y, amount, direction):
        self.batch = batch
        self.image = image
        self.x, self.y = x, y
        self.particles = []
        self.direction = direction
        self.to_add = amount
        self.group = pyglet.sprite.SpriteGroup(self.image.texture,
            blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)

    def step(self, dt):
        if self.to_add:
            for i in range(self.to_add):
                p = pyglet.sprite.Sprite(self.image, self.x, self.y,
                    group=self.group, batch=self.batch)
                p.dy = 100
                if self.direction == 'left':
                    p.dx = rr(0, 100)
                elif self.direction == 'right':
                    p.dx = rr(-100, 0)
                else:
                    p.dx = rr(-50, 50)
                p.scale = .1
                p.color = (255, 200, 100)
                p.lifespan = 2
                self.particles.append(p)
        self.to_add -= 1
        for p in list(self.particles):
            p.y += p.dy * dt
            p.x += p.dx * dt
            p.dx += rr(-10, 10)
            p.scale *= 1 + 2*dt
            p.opacity = max(0, p.opacity - rr(5, 10))
            r, g, b = p.color
            r = max(100, r - 10)
            g = max(100, g - 10)
            p.color = (r, g, b)
            p.lifespan = max(0, p.lifespan - dt)
            if not p.lifespan:
                self.particles.remove(p)

        return not self.particles

class FireLayer(cocos.layer.Layer):
    def on_enter(self):
        num = 500
        self.view_width = director.window.width
        self.goodies = []
        self.batch = pyglet.graphics.Batch()
        self.pimg = pyglet.resource.image('particle.png')
        self.group = pyglet.sprite.SpriteGroup(self.pimg.texture,
            blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add(4*num, GL_QUADS, self.group,
            'v2i', 'c4B', ('t3f', self.pimg.texture.tex_coords*num))
        for n in xrange(0, num):
            f = Particle(0,0,0,0,0)
            self.goodies.append(f)
            self.vertex_list.vertices[n*8:(n+1)*8] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.vertex_list.colors[n*16:(n+1)*16] = [0,0,0,0,] * 4

        self.enable_step()

    def on_leave(self):
        self.disable_step()

    def step(self,dt):
        w,h = self.pimg.width,self.pimg.height
        fires = self.goodies
        verts, clrs = self.vertex_list.vertices, self.vertex_list.colors
        for n,f in enumerate(fires):
            if not f.frame:
                f.x = rr(0,self.view_width)
                f.y = rr(-120,-80)
                f.dy = rr(40,70)/100.0
                f.frame = rr(50,250)
                f.size = 8+pow(rr(0.0,100)/100.0,2.0)*32;
                f.scale= f.size/32.0

            x = f.x = f.x+ rr(-50,50)/100.0
            y = f.y = f.y+f.dy*4
            c = 3*f.frame/255.0;
            r,g,b = (min(255,int(c*0xc2)),min(255,int(c*0x41)),min(255,int(c*0x21)))
            f.frame -= 1
            ww,hh = w*f.scale,h*f.scale
            x-=ww/2
            verts[n*8:(n+1)*8] = map(int,[x,y,x+ww,y,x+ww,y+hh,x,y+hh])
            clrs[n*16:(n+1)*16] = [r,g,b,255] * 4

