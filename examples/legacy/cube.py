import pyglet.graphics
from pyglet.gl import GL_QUADS

vertex_list = None

vertices = [
     1.0, 1.0,-1.0,
    -1.0, 1.0,-1.0,
    -1.0, 1.0, 1.0,
     1.0, 1.0, 1.0,

     1.0,-1.0, 1.0,
    -1.0,-1.0, 1.0,
    -1.0,-1.0,-1.0,
     1.0,-1.0,-1.0,

     1.0, 1.0, 1.0,
    -1.0, 1.0, 1.0,
    -1.0,-1.0, 1.0,
     1.0,-1.0, 1.0,

     1.0,-1.0,-1.0,
    -1.0,-1.0,-1.0,
    -1.0, 1.0,-1.0,
     1.0, 1.0,-1.0,

    -1.0, 1.0, 1.0,
    -1.0, 1.0,-1.0,
    -1.0,-1.0,-1.0,
    -1.0,-1.0, 1.0,

     1.0, 1.0,-1.0,
     1.0, 1.0, 1.0,
     1.0,-1.0, 1.0,
     1.0,-1.0,-1.0,
     ]

colours = [
    # green
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    # orange
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    1.0, 0.5, 0.0,
    # blue
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 1.0,
    # violet
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    1.0, 0.0, 1.0,
    # yellow
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    # red
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 0.0, 0.0
    ]

def create():
    global vertex_list
    vertex_list = pyglet.graphics.vertex_list(
        24,
        ('v3f/static', (vertices) ),
        ('c3f/static', (colours) ),
        )

def draw():
    global vertex_list
    vertex_list.draw( GL_QUADS )
