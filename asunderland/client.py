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

import gamelayer
import server
import logging
from irc import client as irc_client

class ClientEngine():
   configdata = None
   graphicslayer = None
   serveraddress = None
   running = False
   logger = None
   client = None
   connection = None

   def __init__( self, configdata, graphicslayer ):
      self.logger = logging.getLogger( 'clientengine' )
      self.configdata = configdata
      self.graphicslayer = graphicslayer

   def connect(
      self,
      serveraddress=("localhost", server.DEFAULT_PORT),
      client=None,
      connect = None
   ):

      ''' Connect to the specified server. This is a separate method so it can
      avoid being called on special cases like the title screen. 
      
      This method can be passed an existing client by another client engine
      instantiating it instead of a server address in order to avoid dropping
      connection.'''

      if None == client or None == connection:
         self.serveraddress = serveraddress
         self.logger.info(
            'Connecting to %s on port %d...' % self.serveraddress
         )
         self.client = irc_client.IRC()
         self.connection = self.client.server().connect(
            serveraddress[0],
            serveraddress[1],
            'tester' # FIXME
         )
      else:
         # Preserve a pre-existing client connection.
         pass



class ClientTitle( ClientEngine ):

   ''' This engine should be somewhat unique in that it has no real server
   component. All state is handled within the engine module.

   It should just display a pretty menu from which options relevant to starting
   the game proper may be selected. '''

   def process_key( self, key_char_in ):
      self.running = False

   def loop( self ):
      self.running = True
      print "Press any key to continue..."
      while self.running:
         self.graphicslayer.screen_blank( (255, 255, 255) )

         self.graphicslayer.screen_flip()
         gamelayer.sleep( 100 )

      # Return the client to begin the game with.
      client_out = ClientAdventure( self.configdata, self.graphicslayer )
      return client_out

class ClientAdventure( ClientEngine ):

   def process_key( self, key_char_in ):
      print 'Adventure' + key_char_in

   def loop( self ):
      self.running = True
      while self.running:
         self.graphicslayer.screen_flip()
         gamelayer.sleep( 100 )

