'''
Created on 03/03/2012

@author: adam
'''

import math

import numpy
from pyglet.gl import *
import pyglet

# over-ride the default pyglet idle loop
import pygly.renderer.idle
import pygly.renderer.window
from pygly.renderer.viewport import Viewport
from pygly.renderer.projection_view_matrix import ProjectionViewMatrix
from pygly.scene.scene_node import SceneNode
from pygly.scene.render_callback_node import RenderCallbackNode
from pygly.scene.camera_node import CameraNode
from pygly.maths import rectangle

from examples.render_callbacks import grid


class Application( object ):
    
    def __init__( self ):
        super( Application, self ).__init__()
        
        # setup our opengl requirements
        config = pyglet.gl.Config(
            depth_size = 16,
            double_buffer = True
            )

        # create our window
        self.window = pyglet.window.Window(
            fullscreen = False,
            width = 1024,
            height = 768,
            config = config
            )

        # create a viewport that spans
        # the entire screen
        self.viewport = Viewport(
            pygly.renderer.window.window_size_as_rect(
                self.window
                )
            )

        # make a second viewport
        # this viewport will be 1/10th the size
        self.viewport_rect = pygly.renderer.window.window_size_as_rect(
            self.window
            )
        self.viewport_rect[ 1 ] /= [10,10]

        self.floating_viewport = Viewport(
            self.viewport_rect
            )

        # setup our scene
        self.setup_scene()
        
        # setup our update loop the app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )

        # display the current FPS
        self.fps_display = pyglet.clock.ClockDisplay()

        print "Rendering at %iHz" % int(frequency)

    def setup_scene( self ):
        # create a scene
        self.scene_node = SceneNode( '/root' )

        # create a grid to render
        self.grid_node = RenderCallbackNode(
            '/grid',
            grid.initialise_grid,
            grid.render_grid
            )
        self.scene_node.add_child( self.grid_node )

        # rotate the mesh so it is tilting forward
        self.grid_node.rotate_object_x( math.pi / 4.0 )

        # move the grid backward so we can see it
        self.grid_node.translate_inertial_z( -80.0 )

        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera = CameraNode(
            '/camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )

        # we need to make a second camera because the
        # frustrum changes depending on the viewport
        # geometry
        # but for optimisation and convenience, the aspect
        # ratio is tighly coupled to the frustrum.
        # it is only designed to be updated at the start of
        # the frame
        self.view_matrix2 = ProjectionViewMatrix(
            self.floating_viewport.aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        self.camera2 = CameraNode(
            '/camera2',
            self.view_matrix2
            )
        self.scene_node.add_child( self.camera2 )

        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )
        self.floating_viewport.set_camera(
            self.scene_node,
            self.camera2
            )

        # we will use this as a vector to move the viewport
        # around the window
        self.velocity = numpy.array(
            [ 5, 5 ],
            dtype = numpy.int
            )
    
    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # move the viewport around the screen
        rect = self.floating_viewport.rect
        rect[ 0 ] += self.velocity
        self.floating_viewport.rect = rect

        # see if we've gone over the window's bounds
        if self.floating_viewport.left < 0:
            if self.velocity[ 0 ] < 0:
                self.velocity[ 0 ] = -self.velocity[ 0 ]
        if self.floating_viewport.right > self.window.width:
            if self.velocity[ 0 ] > 0:
                self.velocity[ 0 ] = -self.velocity[ 0 ]
        if self.floating_viewport.bottom < 0:
            if self.velocity[ 1 ] < 0:
                self.velocity[ 1 ] = -self.velocity[ 1 ]
        if self.floating_viewport.top > self.window.height:
            if self.velocity[ 1 ] > 0:
                self.velocity[ 1 ] = -self.velocity[ 1 ]

        # rotate the mesh about it's own vertical axis
        self.grid_node.rotate_object_y( dt )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        # render the scene
        # render the large viewport first then the smaller
        # viewport ontop of it
        viewports = [
            self.viewport,
            self.floating_viewport
            ]
        pygly.renderer.window.render( self.window, viewports )

        # render the fps
        self.fps_display.draw()

        # display the frame buffer
        self.window.flip()
    

def main():
    # create app
    app = Application()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

