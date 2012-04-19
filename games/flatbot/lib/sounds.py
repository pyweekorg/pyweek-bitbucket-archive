
import pyglet

try:
    laser = pyglet.resource.media('laser.ogg', streaming=False)
    happy = pyglet.resource.media('happy.ogg', streaming=False)
    speak1 = pyglet.resource.media('robot-speak-one.ogg', streaming=False)
    speak2 = pyglet.resource.media('robot-speak-two.ogg', streaming=False)
    kick = pyglet.resource.media('kick.ogg', streaming=False)
except pyglet.media.MediaFormatException:
    print 'You should install AVBin so you can hear the sounds'
    print '   http://code.google.com/p/avbin/'
    print "(install a binary, don't try to compile)"
    class Dummy(object):
        @classmethod
        def play(*args): pass
    laser = happy = speak1 = speak2 = Dummy()
