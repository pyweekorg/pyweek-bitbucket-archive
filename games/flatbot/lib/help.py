
import pyglet
import cocos

from cocos.director import director

import backgrounds

class HelpScene(cocos.scene.Scene):
    def __init__(self):
        super(HelpScene, self).__init__()

        self.add(backgrounds.GradientLayer((200, 200, 100, 255),
            (200, 200, 200, 255)), z=-1)

        self.add(HelpLayer())

class HelpLayer(cocos.layer.Layer):
    def __init__(self):
        super(HelpLayer, self).__init__()

        im = pyglet.resource.image('help.png')
        im.anchor_x = im.width//2
        im.anchor_y = im.height//2
        self.help = pyglet.sprite.Sprite(im, x=director.window.width//2,
            y=director.window.height//2, batch=self.batch)

