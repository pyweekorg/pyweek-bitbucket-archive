
import cocos
from cocos.director import director
from cocos import tiles
from cocos.actions import *

import robot, ball, backgrounds, effects, message

class GameScene(cocos.scene.Scene):

    def __init__(self):
        super(GameScene, self).__init__()

        self.manager = tiles.ScrollingManager(director.window)

        self.bg = backgrounds.SkyLayer((200,200,255,255),
            (150, 150, 255, 255))
        self.add(self.bg, z=-1)
        self.manager.append(self.bg)

        self.level = tiles.load('data/level1-map.xml')['map0']
        self.manager.append(self.level)
        self.add(self.level, z=0)

        self.robot = robot.RobotLayer()
        self.add(self.robot, (300, 200), z=1)
        self.manager.append(self.robot)

        self.ball = ball.BallLayer()
        self.add(self.ball, z=2)
        self.manager.append(self.ball)

        overlay = tiles.load('data/level1-overlay.xml')['map0']
        self.manager.append(overlay)
        self.add(overlay, z=3)

        self.effects = effects.EffectsLayer()
        self.add(self.effects, z=4)
        self.manager.append(self.effects)

        self.start_focus()

    def level_end(self, *args):
        self.show_message('Congratulations!', 2, self.all_done)

    def all_done(self, *args):
        director.pop()

    def stop_focus(self):
        self.flush()

    def start_focus(self):
        self.do(FocusOnRobot())

    def show_message(self, m, timeout, callback=None):
        director.push(message.MessageScene(director.scene, timeout,
            callback, cocos.layer.ColorLayer(0.1,0.1,0.1,0.8),
            message.MessageLayer(m)))

class FocusOnRobot(cocos.actions.Action):

    def done(self): return False

    def step(self, dt):
        x, y = self.target.robot.position
        y += self.target.robot.head.position[1]
        self.target.manager.set_focus(int(x), int(y))

