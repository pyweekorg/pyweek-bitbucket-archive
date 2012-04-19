import random

import pyglet
pyglet.options['vsync'] = False

import cocos

from cocos.director import director
from cocos.menu import *
from cocos.actions import *

import game, backgrounds, robot, help

def main():
    #director.init(width=700, height=440)
    director.init(fullscreen=True)
    #director.init(width=1024, height=768)
    director.show_FPS = True
    director.window.set_exclusive_mouse(True)

    pyglet.gl.glClearColor(1, 1, 1, 1)
    pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)

    menu = cocos.scene.Scene(MainMenu())
    menu.add(backgrounds.GradientLayer((200, 200, 100, 255),
        (200, 200, 200, 255)), z=-1)
    menu.robot = DumbRobot()
    menu.add(menu.robot, (-200, -200))
    director.run(menu)

class DumbRobot(robot.RobotLayer):
    def on_enter(self):
        self.reset_parts()
        self.enable_step()
    def step(self, dt):
        pass

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("Flat Bot" )

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        self.font_item['color'] = (0, 0, 0, 255)
        self.font_item_selected['color'] = (150, 150, 0, 255)
        self.font_title['color'] = (0, 0, 0, 255)

        # then add the items
        self.add_item( MenuItem('Play', self.on_play ) )
        self.add_item( MenuItem('Help', self.on_help ) )
        self.add_item( MenuItem('Quit', self.on_quit ) )

        # after adding all the items just call build_items()
        self.build_items()

        im = pyglet.resource.image('ball.png')
        self.ball = ActionSprite(im)
        self.add(self.ball, (-200, -200))

    def on_enter(self):
        self.flush()
        self.do(Delay(1) + CallFunc(self.poke_bottom))

    def popup_flatbot(self):
        random.choice([self.jump_across, self.poke_bottom,
            self.bounce_ball])(self.popup_flatbot)

    def poke_bottom(self, cb=None):
        if cb is None:
            cb = self.bounce_ball
        r = self.parent.robot
        self.parent.robot.do(
            Place((director.window.width//2, -300)) +
             AccelDeccel(MoveBy((0, 200), 1)) +
             Delay(.5) +
             AccelDeccel(MoveBy((0, -200), 1)) +
             Delay(1) +
             CallFunc(cb)
        )

    def bounce_ball(self, cb=None):
        if cb is None:
            cb = self.jump_across
        self.ball.do(Place((-100, 0)) +
             Jump(100, director.window.width + 400, 5, 5) +
             Delay(1) +
             CallFunc(cb)
         )

    def jump_across(self, cb=None):
        if cb is None:
            cb = self.popup_flatbot
        self.parent.robot.do(
            Place((-200, 0)) +
             Jump(100, director.window.width + 400, 5, 5) +
             Delay(1) +
             CallFunc(cb)
         )

    def on_play(self):
        director.push(game.GameScene())

    def on_help(self):
        director.push(help.HelpScene())

    def on_quit(self):
        pyglet.app.exit()

