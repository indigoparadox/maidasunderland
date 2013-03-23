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

class ClientEngine():
   config_data = None
   graphicslayer = None
   netclient = None
   running = False

   def __init__( self, configdata, graphicslayer, netclient=None ):
      self.configdata = configdata
      self.graphicslayer = graphicslayer
      self.netclient = netclient

class ClientTitle( ClientEngine ):

   ''' This engine should be somewhat unique in that it has no real server
   component. All state is handled within the engine module.

   It should just display a pretty menu from which options relevant to starting
   the game proper may be selected. '''

   def process_key( self, key_char_in ):
      print 'Title' + key_char_in

   def loop( self ):
      self.running = True
      while self.running:
         self.graphicslayer.screen_blank( (255, 255, 255) )

         self.graphicslayer.screen_flip()
         gamelayer.sleep( 100 )

      # Return the client to begin the game with.
      client_out = ClientAdventure( self.config_data, self.graphicslayer )
      return client_out

class ClientAdventure( ClientEngine ):

   def process_key( self, key_char_in ):
      print 'Adventure' + key_char_in

   def loop( self ):
      self.running = True
      while self.running:
         self.graphicslayer.screen_flip()
         gamelayer.sleep( 100 )

