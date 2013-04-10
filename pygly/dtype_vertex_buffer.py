from OpenGL import GL

from pyrr.utils import parameters_as_numpy_arrays

from vertex_buffer import VertexBuffer
import numpy_utils


class DtypeVertexBuffer( VertexBuffer ):


    def __init__(
        self,
        dtype,
        target = GL.GL_ARRAY_BUFFER,
        usage = GL.GL_STATIC_DRAW,
        rows = None,
        data = None,
        handle = None
        ):
        # don't pass data to parent or it will call allocate
        # using nbytes instead of rows.
        super( DtypeVertexBuffer, self ).__init__(
            target = target,
            usage = usage,
            handle = handle,
            )

        self._dtype = dtype
        self._rows = 0

        # if data has been passed
        # check if it is an appropriate size
        # and calculate the number of rows
        if data != None:
            if (data.nbytes % dtype.itemsize) != 0:
                raise ValueError( "data.nbytes is not a multiple of dtype.itemsize" )
            rows = data.nbytes / dtype.itemsize

        # allocate the buffer if we have a set number of rows
        # and set the data if data has been passed
        if rows:
            self.bind()
            self.allocate( usage, rows )
            if data != None:
                self.set_data( data )
            self.unbind()

    @property
    def dtype( self ):
        """The dtype structure used by data in this buffer.
        """
        return self._dtype

    @property
    def rows( self ):
        """The number of instances of the dtype that this buffer contains.

        :rtype: int
        """
        return self._rows

    @property
    def stride( self ):
        """Returns the stride of the buffer.

        The stride is the size of a single block of the specified dtype.
        """
        return self.dtype.itemsize

    def allocate( self, usage, rows ):
        self._rows = rows
        nbytes = self.stride * rows
        super( DtypeVertexBuffer, self ).allocate( usage, nbytes )

    def offset( self, name ):
        """The byte offset for data of the named property.

        The name must match a name within the dtype.

        If a name is not given the result will be 0.

        :rtype: int
        :return: The offset of the data in bytes.
        :raise KeyError: Raised if the specified name does not exist.
        """
        return numpy_utils.dtype_offset( self.dtype, name )

    def element_count( self, name = None ):
        """The number of values for the specified named property in each row.

        If a name is not given, the buffer will attempt to perform the calculation
        with the assumption that the dtype contains a single data type.
        If this is not true, a ValueError exception will be raised.

        :rtype: int
        :return: The number of values in the specified named property.
        :raise ValueError: Raised if the specified name does not exist, or if
            no name was provided but there is more than one named property in the
            dtype.
        """
        return numpy_utils.dtype_element_count( self.dtype, name )

    def type( self, name = None ):
        """The OpenGL enumeration type for the specified named property.

        The name must match a name within the dtype.

        If a name is not given, the buffer will attempt to perform the conversion
        with the assumption that the dtype contains a single data type.

        :rtype: int
        :return: The OpenGL enumeration value representing the data type.
            Valid values are::

                GL_BYTE,
                GL_UNSIGNED_BYTE,
                GL_SHORT,
                GL_UNSIGNED_SHORT,
                GL_INT,
                GL_UNSIGNED_INT,
                GL_FLOAT,
                GL_DOUBLE,

        .. seealso: `py:func:pygly.numpy_utils.dtype_gl_enum`
        """
        return numpy_utils.dtype_gl_enum( self.dtype, name )

    def set_vertex_pointer_dtype( self, name = None, enable = True ):
        """Calculates and sets the glVertexPointer to the specified
        dtype attribute.

        .. warning:: This function is removed from the OpenGL Core profile and **only**
            exists in OpenGL Legacy profile (OpenGL version <=2.1).
        """
        values_per_vertex = self.element_count( name )
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )
        self.set_vertex_pointer( values_per_vertex, glType, stride, offset, enable )

    def set_color_pointer_dtype( self, name = None, enable = True ):
        """Calculates and sets the glColorPointer to the specified
        dtype attribute.

        .. warning:: This function is removed from the OpenGL Core profile and **only**
            exists in OpenGL Legacy profile (OpenGL version <=2.1).
        """
        values_per_vertex = self.element_count( name )
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )
        self.set_color_pointer( values_per_vertex, glType, stride, offset, enable )

    def set_texture_coord_pointer_dtype( self, name = None, enable = True ):
        """Calculates and sets the glTexCoordPointer to the specified
        dtype attribute.

        .. warning:: This function is removed from the OpenGL Core profile and **only**
            exists in OpenGL Legacy profile (OpenGL version <=2.1).
        """
        values_per_vertex = self.element_count( name )
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )
        self.set_texture_coord_pointer( values_per_vertex, glType, stride, offset, enable )

    def set_normal_pointer_dtype( self, name = None, enable = True ):
        """Calculates and sets the glNormalPointer to the specified
        dtype attribute.

        .. warning:: This function is removed from the OpenGL Core profile and **only**
            exists in OpenGL Legacy profile (OpenGL version <=2.1).
        """
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )
        self.set_normal_pointer( glType, stride, offset, enable )

    def set_index_pointer_dtype( self, name = None, enable = True ):
        """Calculates and sets the glIndexPointer to the specified
        dtype attribute.

        .. warning:: This function is removed from the OpenGL Core profile and **only**
            exists in OpenGL Legacy profile (OpenGL version <=2.1).
        """
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )
        self.set_index_pointer( glType, stride, offset, enable )

    def set_attribute_pointer_dtype(
        self,
        shader,
        attribute,
        name = None,
        normalise = False,
        enable = True
        ):
        """Binds the attribute to the currently bound buffer.

        This method wraps the glVertexAttribPointer call using
        information provided by the shader object and the dtype.

        :param Shader shader: The shader object.
        :param string attribute: The name of a shader attribute variable.
        :param string name: A named property defined within the dtype.
        """
        # get the attribute location
        location = shader.attributes[ attribute ].location

        values_per_vertex = self.element_count( name )
        glType = self.type( name )
        stride = self.stride
        offset = self.offset( name )

        self.set_attribute_pointer(
            location,
            values_per_vertex,
            glType,
            stride,
            offset,
            normalise,
            enable
            )

    def __str__( self ):
        string = \
            "DtypeVertexBuffer:\n" \
            "dtype:\t%s\n" \
            "rows:\t%d\n" \
            "nbytes:\t%d\n" \
            "stride:\t%d"  % (
                str(self._dtype),
                self.rows,
                self.nbytes,
                self.stride,
                )
        return string
