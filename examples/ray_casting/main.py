'''
Created on 15/06/2011

@author: adam
'''

import math
import time
import random

from pyglet.gl import *
import pyglet
import numpy

import pygly.window
from pygly.viewport import Viewport
#from pygly.projection_view_matrix import ProjectionViewMatrix
from pygly.orthogonal_view_matrix import OrthogonalViewMatrix
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.render_callback_node import RenderCallbackNode
from pygly import debug_cube
from pygly.mesh.obj_mesh import OBJ_Mesh
from pygly.input.keyboard import Keyboard
from pygly.input.mouse import Mouse
import pygly.list

# over-ride the default pyglet idle loop
import pygly.monkey_patch
pygly.monkey_patch.patch_idle_loop()


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

        # create a viewport
        self.viewport = Viewport(
            pygly.window.create_rectangle(
                self.window
                )
            )

        # over-ride the viewports setup method
        # so we can set some opengl states
        self.viewport.setup_viewport = self.setup_viewport

        # create our input devices
        self.keyboard = Keyboard( self.window )
        self.mouse = Mouse( self.window )

        # initialise our mouse position to
        # an invalid value
        self.last_mouse_point = [-1, -1]
        
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

        # create our render node with callbacks to
        # render our mesh
        self.mesh_node = RenderCallbackNode(
            '/obj/rendernode',
            None,
            debug_cube.render
            )
        self.scene_node.add_child( self.mesh_node )

        # move the mesh so we can see it
        self.mesh_node.translate_inertial_z( -30.0 )

        # rotate the mesh so we can see it
        self.mesh_node.rotate_object_x( math.pi / 4.0 )
        
        # create a camera and a view matrix
        """
        self.view_matrix = ProjectionViewMatrix(
            self.viewport.aspect_ratio,
            aspect_ratio,
            fov = 60.0,
            near_clip = 1.0,
            far_clip = 200.0
            )
        """
        self.view_matrix = OrthogonalViewMatrix(
            self.viewport.aspect_ratio,
            scale = [ 20.0, 20.0 ],
            near_clip = 1.0,
            far_clip = 200.0
            )
        # create a camera
        self.camera = CameraNode(
            '/camera',
            self.view_matrix
            )
        self.scene_node.add_child( self.camera )
        
        # set the viewports camera
        self.viewport.set_camera( self.scene_node, self.camera )

        # create a light
        glEnable( GL_LIGHT0 )
        glLightfv(
            GL_LIGHT0,
            GL_POSITION,
            (GLfloat * 4)( *[-10.0, 0.0, 0.0, 1.0] )
            )
        glLightfv(
            GL_LIGHT0,
            GL_AMBIENT,
            (GLfloat * 4)( *[0.5, 0.5, 0.5, 1.0] )
            )
        glLightfv(
            GL_LIGHT0,
            GL_DIFFUSE,
            (GLfloat * 4)( *[1.0, 1.0, 1.0, 1.0] )
            )

    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # normalise any normals for us
        glEnable( GL_RESCALE_NORMAL )

        # enable us to clear viewports independently
        glEnable( GL_SCISSOR_TEST )

        # enable smooth shading
        # instead of flat shading
        glShadeModel( GL_SMOOTH )
            
        # setup lighting for our viewport
        glEnable( GL_LIGHTING )

        # set our ambient lighting
        glAmbient = glLightModelfv(
            GL_LIGHT_MODEL_AMBIENT,
            (GLfloat * 4)( *[ 0.8, 0.8, 0.8, 1.0 ] )
            )

    def initialise_mesh( self ):
        # load the mesh
        self.mesh.load()

    def render_mesh( self ):
        self.mesh.render()

    def run( self ):
        pyglet.app.run()

    def move_mesh( self ):
        # we don't need the delta
        # just clear it to stop overflows
        self.mouse.clear_delta()

        # see if the mouse moved
        mouse_pos = self.mouse.absolute_position
        mouse_moved = pygly.list.not_equivalent(
            mouse_pos,
            self.last_mouse_point
            )

        if False == mouse_moved:
            return

        # the mouse has moved
        # update our mouse pos
        self.last_mouse_point = mouse_pos

        # even though the mouse moved, we can't be
        # guaranteed that it is within the window.
        # we sometimes get events that include mouse
        # values that are outside the window.
        # so we need to check against this.
        viewports = [ self.viewport ]
        viewport = pygly.window.find_viewport_for_point(
            self.window,
            viewports,
            mouse_pos
            )

        if viewport == None:
            return

        # make the point relative to the viewport
        relative_point = self.viewport.create_viewport_point_from_window_point(
            mouse_pos
            )

        # cast a ray from the mouse's current position
        mouse_ray = self.viewport.create_ray_from_viewport_point(
            relative_point
            )

        # render the md2 at the current ray position
        # use the far_clip value
        distance = 50.0
        self.mesh_node.inertial_translation = mouse_ray[ 0 ] + mouse_ray[ 1 ] * distance
    
    def step( self, dt ):
        # move the mesh to the mouse position
        self.move_mesh()

        # rotate the mesh about it's own vertical axis
        self.mesh_node.rotate_object_y( dt )

        # clear our frame buffer and depth buffer
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        
        # render the scene
        viewports = [ self.viewport ]
        pygly.window.render( self.window, viewports )

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

