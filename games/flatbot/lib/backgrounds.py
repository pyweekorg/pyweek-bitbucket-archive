import random
from euclid import *
from pyglet.gl import *
import cocos
from cocos import tiles

from cocos.director import director

class GradientLayer(tiles.ScrollableLayer):
    def __init__(self, bottom, top):
        self.bottom = bottom
        self.top = top
        super(GradientLayer, self).__init__()

    def draw(self, x=0, y=0):
        w, h = director.window.width, director.window.height
        glBegin(GL_QUADS)
        glColor4ub(*self.bottom)
        glVertex2f(x, y)
        glVertex2f(x+w, y)
        glColor4ub(*self.top)
        glVertex2f(x+w, y+h)
        glVertex2f(x, y+h)
        glEnd()

class SkyLayer(GradientLayer):
    def __init__(self, bottom, top):
        super(SkyLayer, self).__init__(bottom, top)

        self._clouds = []

        # XXX add some random clouds
        self.add_cloud(400, 400, 300, 300)
        self.add_cloud(1200, 300, 400, 200)
        self.add_cloud(1900, 450, 300, 300)
        self.add_cloud(2400, 400, 300, 300)
        self.add_cloud(3200, 600, 400, 200)
        self.add_cloud(3900, 450, 300, 300)

    def draw(self):
        super(SkyLayer, self).draw(self.viewport_x, self.viewport_y)
        for cloud in self._clouds:
            glCallList(cloud)

    def add_cloud(self, x, y, w, h):
        l = glGenLists(1)
        glNewList(l, GL_COMPILE)
        draw_cloud((x, y), (x+w, y+h))
        glEndList()
        self._clouds.append(l)

def draw_cloud(bl, tr):
    '''
    - two base points, line between
    - another 4 points on semi-circle above
    - length of control vectors = 1/4 -> 1/2 R
    - angle of control vectors up to 45 degrees from angle to center
    '''
    x1, y1 = bl
    x2, y2 = tr

    l = bl
    t = (x2, y1)
    hx = (x2-x1)/2.
    hy = (y2-y1)/2.
    v = Vector2((x2-x1)/2., 0)
    m = Point2(x1 + hx, y1+ hy)

    angles = []
    points = []
    cps = []
    for i in range(6):
        angle = math.pi * i / 5.
        if i not in (0, 5):
            angle += (random.random()-.5) * (math.pi / 10.)
        angles.append(angle)
        r = Matrix3.new_rotate(angle)
        p = m + r * v
        points.append(p)
        r = Matrix3.new_rotate(angle + random.random() * math.pi / 5.)
        v1 = r * v * .5
        r = Matrix3.new_rotate(angle - random.random() * math.pi / 5.)
        v2 = r * v * .5
        cps.append((p + v1, p + v2))

    glColor4f(1, 1, 1, 1)
    glBegin(GL_POLYGON)
    for i in range(6):
        glVertex2f(*points[i])
    glEnd()

    glEnable(GL_MAP2_VERTEX_3)
    for i in range(5):
        p1 = tuple(points[i]) + (0,)
        p2 = tuple(points[i + 1]) + (0,)
        cp1 = tuple(cps[i][0]) + (0,)
        cp2 = tuple(cps[i+1][1]) + (0,)
        args = p1 + cp1 + cp2 + p2 + p1 + p1 + p2 + p2
        p = (GLfloat * 24)(*args)

        glMap2f(GL_MAP2_VERTEX_3, 0, 1, 3, 4, 0, 1, 12, 2, cast(byref(p),
            POINTER(c_float)))
        glMapGrid2f(12, 0.0, 1.0, 12, 0.0, 1.0)
        glEvalMesh2(GL_FILL, 0, 12, 0, 12)
    glDisable(GL_MAP2_VERTEX_3)

if __name__ == '__main__':
    director.init(resizable=True)

    director.run(cocos.scene.Scene(GradientLayer((200,200,255,255),
            (150, 150, 255, 255))))
