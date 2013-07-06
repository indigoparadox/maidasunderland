#!/usr/bin/env python

'''
This file is part of Asunderland.

Asunderland is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Asunderland is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Asunderland.  If not, see <http://www.gnu.org/licenses/>.
'''

from irc import server as irc_server
from OpenSSL import SSL
import socket

DEFAULT_PORT = 6300

class AsunderlandIRCClientHandler( irc_server.IRCClient ):

   def handle_movement( self, params ):
      # TODO: Determine the player's current location on their map and if there
      #       are any collisions. Respond to the client with their new position.
      print params

   def handle_who( self, params ):
      # TODO: List users in the specified room.
      pass

   def handle_whois( self, params ):
      # TODO: Implement extension to give engine-specific actor information
      #       (e.g. sprite/location for adventure engine) for the specified IRC
      #       user so the client can display it.
      pass

   def handle_away( self, params ):
      # TODO: Implement some kind of sleep bubble.
      pass

class AsunderlandIRCServer( irc_server.IRCServer ):
   def __init__( self, args, kwargs ):
      
      irc_server.IRCServer.__init__( self, args, kwargs )

      # Setup SSL.
      # TODO: Load certificate path from config and handle missing certificate.
      ssl_ctx = SSL.Context( SSL.SSLv23_METHOD )
      ssl_key_path = '../server.pem'
      ssl_ctx.use_privatekey_file( ssl_key_path )
      ssl_ctx.use_certificate_file( ssl_key_path )
      self.socket = SSL.Connection(
         ssl_ctx,
         socket.socket( self.address_family, self.socket_type )
      )
      self.server_bind()
      self.server_activate()         

      # Create a default channel and set a default map.
      channel = self.channels.setdefault(
         '#lobby',
         irc_server.IRCChannel( '#lobby' )
      )
      channel.topic = 'Map:Farm'

      # TODO: Load the map into the server to calculate collisions/etc.

class ServerEngine():
   pass

class ServerAdventure( ServerEngine ):
   pass

