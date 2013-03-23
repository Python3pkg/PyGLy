import textwrap

import numpy
from OpenGL import GL

from pygly.shader import Shader, ShaderProgram
from pygly.buffer import Buffer, BufferRegion
from pygly.vertex_array import VertexArray


vertices = numpy.array(
    [
        #  X    Y    Z          R    G,   B
        (( 1.0, 1.0,-1.0),     (0.0, 1.0, 0.0)),
        ((-1.0, 1.0,-1.0),     (0.0, 1.0, 0.0)),
        (( 1.0, 1.0, 1.0),     (0.0, 1.0, 0.0)),
        ((-1.0, 1.0,-1.0),     (0.0, 1.0, 0.0)),
        ((-1.0, 1.0, 1.0),     (0.0, 1.0, 0.0)),
        (( 1.0, 1.0, 1.0),     (0.0, 1.0, 0.0)),

        (( 1.0,-1.0, 1.0),     (1.0, 0.5, 0.0)),
        ((-1.0,-1.0, 1.0),     (1.0, 0.5, 0.0)),
        (( 1.0,-1.0,-1.0),     (1.0, 0.5, 0.0)),
        ((-1.0,-1.0, 1.0),     (1.0, 0.5, 0.0)),
        ((-1.0,-1.0,-1.0),     (1.0, 0.5, 0.0)),
        (( 1.0,-1.0,-1.0),     (1.0, 0.5, 0.0)),

        (( 1.0, 1.0, 1.0),     (0.0, 0.0, 1.0)),
        ((-1.0, 1.0, 1.0),     (0.0, 0.0, 1.0)),
        (( 1.0,-1.0, 1.0),     (0.0, 0.0, 1.0)),
        ((-1.0, 1.0, 1.0),     (0.0, 0.0, 1.0)),
        ((-1.0,-1.0, 1.0),     (0.0, 0.0, 1.0)),
        (( 1.0,-1.0, 1.0),     (0.0, 0.0, 1.0)),

        (( 1.0,-1.0,-1.0),     (1.0, 0.0, 1.0)),
        ((-1.0,-1.0,-1.0),     (1.0, 0.0, 1.0)),
        (( 1.0, 1.0,-1.0),     (1.0, 0.0, 1.0)),
        ((-1.0,-1.0,-1.0),     (1.0, 0.0, 1.0)),
        ((-1.0, 1.0,-1.0),     (1.0, 0.0, 1.0)),
        (( 1.0, 1.0,-1.0),     (1.0, 0.0, 1.0)),

        ((-1.0, 1.0, 1.0),     (1.0, 1.0, 0.0)),
        ((-1.0, 1.0,-1.0),     (1.0, 1.0, 0.0)),
        ((-1.0,-1.0, 1.0),     (1.0, 1.0, 0.0)),
        ((-1.0, 1.0,-1.0),     (1.0, 1.0, 0.0)),
        ((-1.0,-1.0,-1.0),     (1.0, 1.0, 0.0)),
        ((-1.0,-1.0, 1.0),     (1.0, 1.0, 0.0)),

        (( 1.0, 1.0,-1.0),     (1.0, 0.0, 0.0)),
        (( 1.0, 1.0, 1.0),     (1.0, 0.0, 0.0)),
        (( 1.0,-1.0,-1.0),     (1.0, 0.0, 0.0)),
        (( 1.0, 1.0, 1.0),     (1.0, 0.0, 0.0)),
        (( 1.0,-1.0, 1.0),     (1.0, 0.0, 0.0)),
        (( 1.0,-1.0,-1.0),     (1.0, 0.0, 0.0)),
        ],
    dtype = [
        ('position',    'float32',  (3,)),
        ('colour',      'float32',  (3,)),
        ]
    )


def create( core_profile = True ):
    if core_profile:
        return CoreCube()
    else:
        return LegacyCube()

class CoreCube( object ):

    vertex_shader = textwrap.dedent( """
        #version 150

        // input
        in vec3 in_position;
        in vec3 in_colour;
        uniform mat4 model_view;
        uniform mat4 projection;

        // shared
        out vec3 ex_colour;

        void main(void) 
        {
            // apply projection and model view matrix to vertex
            gl_Position = projection * model_view * vec4( in_position, 1.0 );

            ex_colour = in_colour;
        }
        """ )

    fragment_shader = textwrap.dedent( """
        #version 150

        // shared
        in vec3 ex_colour;

        // output
        out vec4 fragColor;

        void main(void) 
        {
            // set colour of each fragment
            fragColor = vec4( ex_colour, 1.0 );
        }
        """ )


    def __init__( self ):
        super( CoreCube, self ).__init__()

        global vertices
        
        # create our shader
        self.shader = ShaderProgram(
            Shader( GL.GL_VERTEX_SHADER, self.vertex_shader ),
            Shader( GL.GL_FRAGMENT_SHADER, self.fragment_shader )
            )

        # create a vertex buffer
        # we pass in a list of regions we want to define
        # we only have 1 region here
        # for each region, we pass in how many rows, and the dtype
        self.buffer = Buffer(
            GL.GL_ARRAY_BUFFER,
            GL.GL_STATIC_DRAW,
            (vertices.size, vertices.dtype)
            )

        self.vao = VertexArray()
        self.vao.bind()

        # pass the shader and region to our VAO
        # and bind each of the attributes to a VAO index
        # the shader name is the variable name used in the shader
        # the buffer name is the name of the property in our vertex dtype
        # create our vertex array
        self.buffer.bind()
        
        self.buffer[ 0 ].set_data( vertices )
        self.buffer[ 0 ].set_attribute_pointer( self.shader, 'in_position', 'position' )
        self.buffer[ 0 ].set_attribute_pointer( self.shader, 'in_colour', 'colour' )

        self.buffer.unbind()
        self.vao.unbind()

    def draw( self, projection, model_view ):
        self.shader.bind()
        self.shader.uniforms.projection = projection
        self.shader.uniforms.model_view = model_view

        self.vao.bind()
        GL.glDrawArrays( GL.GL_TRIANGLES, 0, self.buffer[ 0 ].rows )
        self.vao.unbind()

        self.shader.unbind()


class LegacyCube( object ):

    vertex_shader = textwrap.dedent( """
        #version 120

        void main(void) 
        {
            // apply projection and model view matrix to vertex
            gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;

            gl_FrontColor = gl_Color;
        }
        """ )

    fragment_shader = textwrap.dedent( """
        #version 120

        void main(void) 
        {
            // set colour of each fragment
            gl_FragColor = gl_Color;
        }
        """ )


    def __init__( self ):
        super( LegacyCube, self ).__init__()

        global vertices

        self.use_shaders = True

        # create our shader
        self.shader = ShaderProgram(
            Shader( GL.GL_VERTEX_SHADER, self.vertex_shader ),
            Shader( GL.GL_FRAGMENT_SHADER, self.fragment_shader )
            )

        # create our vertex buffer
        self.buffer = Buffer(
            GL.GL_ARRAY_BUFFER,
            GL.GL_STATIC_DRAW,
            (vertices.size, vertices.dtype)
            )

        self.buffer.bind()
        self.buffer[ 0 ].set_data( vertices )
        self.buffer.unbind()

    def draw( self ):
        if self.use_shaders:
            self.shader.bind()

        self.buffer.bind()
        self.buffer.push_attributes()

        # set the vertex pointer to the position data
        self.buffer[ 0 ].set_vertex_pointer( 'position' )
        self.buffer[ 0 ].set_color_pointer( 'colour' )

        GL.glDrawArrays( GL.GL_TRIANGLES, 0, self.buffer[ 0 ].rows )

        self.buffer.pop_attributes()
        self.buffer.unbind()

        if self.use_shaders:
            self.shader.unbind()
