from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene


from cocos.actions import Delay, CallFunc

import pyglet

class MessageScene(Scene):
    def __init__(self, background_scene, timeout, callback, *layers):
        super(MessageScene, self).__init__(*layers)
        self.bg = background_scene
        self.do(Delay(timeout) + CallFunc(self._close))
        self.callback = callback

    def _close(self):
        director.pop()
        if self.callback is not None:
            self.callback()

    def on_draw(self):
        self.bg.on_draw()
        super(MessageScene, self).on_draw()


class MessageLayer(Layer):
    def __init__(self, message):
        super(MessageLayer, self).__init__()

        x,y = director.get_window_size()

        ft = pyglet.font.load('Arial', 36)
        self.text = pyglet.font.Text(ft, message,
            halign=pyglet.font.Text.CENTER)
        self.text.x = x/2
        self.text.y = y/2

    def on_draw(self):
        self.text.draw()

