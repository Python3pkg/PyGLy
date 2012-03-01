'''
Created on 29/02/2012

@author: adam
'''

from pyglet.gl import *


class Digital( object ):
    """
    This class provides access to a single digital
    device.

    Most physical hardware device will only require
    a single 'Digital' input object.

    Values provided are the event type
    (pressed / released) and the input (a button).
    """
    
    def __init__( self, device ):
        super( Digital, self ).__init__()
        
        self.device = device
        self.handlers = set()
    
    def register_handler( self, handler ):
        """
        Adds a handler to the list of
        handlers to receive events.

        @param handler: Must be a callable function.
        Function must take the parameters:
            name, event, value
        """
        assert handler not in self.handlers
        assert callable( handler )
        self.handlers.add( handler )
    
    def unregister_handler( self, handler ):
        """
        Removes a registered handler so it
        no longer receives updates.

        @param handler: Must be a callable function.
        Function must take the parameters:
            device, event, value

        @raise KeyError: if not present.
        """
        self.handlers.remove( handler )

    def dispatch_event( self, event, value ):
        """
        Sends an event to all registered handler
        functions.
        """
        for handler in self.handlers:
            handler( self.device, event, value )


if __name__ == "__main__":
    device = Digital( 'keyboard' )

    def handle_event( device, event, value ):
        print '[%s] %s: %s' % (device, event, value)
        pass

    assert handle_event not in device.handlers
    device.register_handler( handle_event )
    assert handle_event in device.handlers
    device.dispatch_event( 'down', ('d',None) )
    device.unregister_handler( handle_event )
    assert handle_event not in device.handlers


