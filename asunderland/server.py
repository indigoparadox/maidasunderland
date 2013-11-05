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

import socket
import json
import logging
from actor import Actor
from irc import server as irc_server
from irc import events as irc_events
from OpenSSL import SSL

DEFAULT_PORT = 6300

log = logging.getLogger(__name__)

class AsunderlandIRCClientHandler( irc_server.IRCClient ):

   actor = None

   #def __init__( self, request, client_address, server ):
   #   irc_server.IRCClient( request, client_address, server )
   #   self.actor = Actor()

   def handle_actor( self, params ):
      self.actor = Actor()

   def handle_movement( self, params ):
      # TODO: Determine the player's current location on their map and if there
      #       are any collisions. Respond to the client with their new position.

      # TODO: Don't allow/propagate walking "too fast".

      if None != self.actor:
         propagate = False

         if 'UP' == params:
            self.actor.maptilecoords = (
               self.actor.maptilecoords[0],
               self.actor.maptilecoords[1] - 1
            )
            propagate = True
         elif 'DOWN' == params:
            self.actor.maptilecoords = (
               self.actor.maptilecoords[0],
               self.actor.maptilecoords[1] + 1
            )
            propagate = True
         elif 'RIGHT' == params:
            self.actor.maptilecoords = (
               self.actor.maptilecoords[0] + 1,
               self.actor.maptilecoords[1]
            )
            propagate = True
         elif 'LEFT' == params:
            self.actor.maptilecoords = (
               self.actor.maptilecoords[0] - 1,
               self.actor.maptilecoords[1]
            )
            propagate = True

         if propagate:
            actor_string = self.actor.encode()
            for client_key in self.server.clients.keys():
               self.server.clients[client_key].send_actor( self )

   def handle_who( self, params ):
      # TODO: List users in the specified room.
      pass

   def handle_whois( self, params ):

      params = params.split( ' ' )

      # Look up the requested client.
      nick = params[0]
      whois_client = self.server.clients.get( nick, None )
      if None == whois_client:
         return

      # Send the information to the requester.
      # XXX: For some reason, this makes pidgin crash, so we've disabled it for
      #      now.
      #self.send_queue.append(
      #   ':{} {} {} {} {} * {}'.format(
      #      self.server.servername, irc_events.codes['whoisuser'],
      #      nick, whois_client.user, whois_client.host[0],
      #      whois_client.realname
      #   )
      #)
      if 2 == len( params ) and 'ACTOR' == params[1]:
         # Only send actor data if it's available.
         if None != whois_client.actor:
            self.send_actor( whois_client )
      self.send_queue.append(
         ':{} {} {} {} :End of /WHOIS list'.format(
            self.server.servername, irc_events.codes['endofwhois'], 
            self.nick, nick
         )
      )

   def handle_away( self, params ):
      # TODO: Implement some kind of sleep bubble.
      pass

   def send_actor( self, client_send ):

      ''' Encode and send a blob of the given client's actor data to this
      client. '''

      actor_string = client_send.actor.encode()
      self.send_queue.append(
         ':{} {} {} {} {}@{} {}'.format(
            # We're kind of rudely borrowing an uncommonly used code. It
            # might be a terrible idea to do this
            self.server.servername, irc_events.codes['whoisuser'],
            self.nick, client_send.nick, client_send.user,
            client_send.host[0], actor_string
         )
      )

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

