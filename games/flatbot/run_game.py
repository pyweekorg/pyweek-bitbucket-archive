#! /usr/bin/env python

import sys
import os

try:
    __file__
except NameError:
    pass
else:
    libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
    sys.path.insert(0, libdir)

import pyglet
pyglet.options['debug_gl'] = 0
pyglet.resource.path.append('data')
pyglet.resource.reindex()

import main
main.main()
