'''
Created on 15/06/2011

@author: adam

TODO: use resource locations
http://www.pyglet.org/doc/programming_guide/loading_resources.html
'''

import math
import time
import random

from pyglet.gl import *
import pyglet

import renderer.idle
import renderer.window
from renderer.viewport import Viewport
from renderer.projection_view_matrix import ProjectionViewMatrix
from scene.scene_node import SceneNode
from scene.camera_node import CameraNode
from scene.render_callback_node import RenderCallbackNode
import maths.quaternion

import md2


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
            [ 0.0, 0.0, 1.0, 1.0 ]
            )

        # over-ride the viewports setup method
        # so we can set some opengl states
        self.viewport.setup_viewport = self.setup_viewport
        self.viewport.tear_down_viewport = self.tear_down_viewport
        
        # setup our scene
        self.setup_scene()
        
        # setup our update loop the app
        # we'll render at 60 fps
        frequency = 60.0
        self.update_delta = 1.0 / frequency
        self.fps_display = pyglet.clock.ClockDisplay()
        # use a pyglet callback for our render loop
        pyglet.clock.schedule_interval(
            self.step,
            self.update_delta
            )
        
        print "Rendering at %iHz" % int(frequency)

    def setup_scene( self ):
        # create a scene
        self.scene_node = SceneNode( '/root' )

        self.mesh_node = SceneNode( '/mesh' )
        self.scene_node.add_child( self.mesh_node )

        # create our render node
        # this is seperate to the mesh node because
        # we need to rotate it about it's X axis
        # due to the model being on its side
        self.render_node = RenderCallbackNode(
            '/md2/rendernode',
            md2.initialise_mesh,
            md2.render_mesh
            )
        self.mesh_node.add_child( self.render_node )

        # the md2 is oriented at 90 degrees about X
        # re-orient the mesh
        self.render_node.rotate_object_x( -math.pi / 2.0 )

        # move the mesh so we can see it
        self.mesh_node.translate_inertial_z( -80.0 )
        
        # create a camera and a view matrix
        self.view_matrix = ProjectionViewMatrix(
            fov = 60.0,
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

        # use a variable for accumulating time
        # for animating the mesh
        self.animation_time = 0.0
        
    def setup_viewport( self ):
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # normalise any normals for us
        glEnable( GL_NORMALIZE )

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
    
    def tear_down_viewport( self ):
        glDisable( GL_LIGHT0 )
        glDisable( GL_LIGHTING )
        glDisable( GL_NORMALIZE )
        glDisable( GL_DEPTH_TEST )

    def run( self ):
        pyglet.app.run()
    
    def step( self, dt ):
        # add the current time to the animation
        self.animation_time += dt

        # check if we should move to the next frame
        # 20 fps
        if self.animation_time > (1.0 / 20.0):
            md2.mesh.frame += 1
            md2.mesh.frame %= md2.mesh.frames
            self.animation_time = 0.0

        # rotate the mesh about it's own vertical axis
        self.mesh_node.rotate_object_y( dt )
        
        # render the scene
        viewports = [ self.viewport ]
        renderer.window.render( self.window, viewports )
        
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

