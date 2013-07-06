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
import pytmx
import logging
import re
import os
from threading import Thread
from irc import client as irc_client
from yaml import load, dump
try:
   from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
   from yaml import Loader, Dumper

DEFAULT_ADVENTURE_MAP = 'Farm'

MAP_PROCESS_TIMEOUT = 10

class AsunderlandIRCClient( irc_client.IRC ):
   pass

class ClientEngine():
   configdata = None
   graphicslayer = None
   serveraddress = None
   running = False
   logger = None
   client = None
   connection = None
   channel = ''
   viewport = (0, 0, 0, 0)

   def __init__( self, configdata, graphicslayer ):
      self.logger = logging.getLogger( 'asunderland.clientengine' )
      self.configdata = configdata
      self.graphicslayer = graphicslayer

      # Viewport format is (X, Y, Width, Height).
      self.viewport = (
         0, 0,
         self.configdata['Options']['WindowWidth'],
         self.configdata['Options']['WindowHeight']
      )

   def connect(
      self,
      channel,
      serveraddress=("localhost", server.DEFAULT_PORT),
      client=None,
      connect=None
   ):

      ''' Connect to the specified server. This is a separate method so it can
      avoid being called on special cases like the title screen. 
      
      This method can be passed an existing client by another client engine
      instantiating it instead of a server address in order to avoid dropping
      connection.'''

      if None == client or None == connection:
         self.logger.info( serveraddress )
         self.serveraddress = serveraddress
         self.logger.info(
            'Connecting to %s on port %d...' % self.serveraddress
         )
         self.channel = channel
         self.client = AsunderlandIRCClient()
         # TODO: Add support for SSL using connect_factory.
         self.connection = self.client.server().connect(
            serveraddress[0],
            serveraddress[1],
            'tester' # FIXME
         )
         self.connection.join( self.channel )
      else:
         # Preserve a pre-existing client connection.
         pass

   def set_viewport( self, x, y ):
      self.viewport = (
         x, y,
         self.viewport[2],
         self.viewport[3]
      )
      

class ClientTitle( ClientEngine ):

   ''' This engine should be somewhat unique in that it has no real server
   component. All state is handled within the engine module.

   It should just display a pretty menu from which options relevant to starting
   the game proper may be selected. '''

   def process_key( self, key_char_in ):
      self.running = False

   def loop( self ):
      self.running = True
      self.logger.info( "Press any key to continue..." )
      while self.running:
         self.graphicslayer.screen_blank( (255, 255, 255) )

         self.graphicslayer.screen_flip()
         gamelayer.sleep( 100 )

      # Return the client to begin the game with.
      client_out = ClientAdventure( self.configdata, self.graphicslayer )
      return client_out

class ClientAdventure( ClientEngine ):

   ''' A tile-based hack-and-slash adventure mode. '''

   # TODO: At some point, maybe define a ClientTilemap class that inherits from
   #       ClientEngine and then have ClientAdventure inherit from that, thus
   #       allowing for tilemap-based engines that aren't adventure games, like
   #       strategy games or similar.

   gamemap = None
   tileviewport = None
   tilesize = (0, 0)
   tilesmoving = False # Flag to signal redraw of static tiles.
   mobiles = []

   def __init__( self, configdata, graphicslayer ):
      ClientEngine.__init__( self, configdata, graphicslayer )

      # TODO: Fetch list of mobiles with /who, iterating with /whois for each
      #       one to find sprite/location.

   def connect(
      self,
      channel,
      serveraddress=("localhost", server.DEFAULT_PORT),
      client=None,
      connect=None
   ):
      ClientEngine.connect( self, channel, serveraddress, client, connect )

      # Load the map from the channel topic if we can.
      self.connection.add_global_handler( 'topic', self.on_topic )
      process = 0
      while None == self.gamemap and process < MAP_PROCESS_TIMEOUT:
         self.client.process_once()
         process += 1

      if None == self.gamemap:
         # Set the map to a default map.
         self.logger.warn( 'No topic received.' )
         self.logger.info(
            'Falling back to default map "%s"', DEFAULT_ADVENTURE_MAP
         )
         self.load_map( DEFAULT_ADVENTURE_MAP )

   def on_topic( self, connection, event ):
      # Attempt to grab the map name from the channel topic.
      match_map = re.match( r'Map:(\S*)', event.arguments[0] )
      if None != match_map.groups():
         self.load_map( match_map.groups()[0] )
      else:
         # Set the map to a default map.
         self.logger.error( 'No map specified in topic.' )
         self.logger.info(
            'Falling back to default map "%s"', DEFAULT_ADVENTURE_MAP
         )
         self.load_map( DEFAULT_ADVENTURE_MAP )

   def process_key( self, key_char_in ):
      #self.connection.privmsg( self.channel, key_char_in )
      self.connection.send_raw( 'MOVEMENT %s' % key_char_in )

   def load_map( self, mapname ):
      try:
         # Load the map data file.
         mappath = os.path.join( 'maps', mapname + '.tmx' )
         self.logger.info( 'Attempting to load map "%s"...' % mappath )

         # TODO: Should this be abstracted, since it kind of relies on PyGame?
         self.gamemap = pytmx.tmxloader.load_pygame( mappath )

         # Make sure the tile layers are homogenous.
         self.tilesize = (self.gamemap.tilesets[0].tilewidth,
            self.gamemap.tilesets[0].tileheight)
         for tileset in self.gamemap.tilesets:
            if self.tilesize[0] != tileset.tilewidth: 
               raise Exception( 'Tile width mismatches!' )
            elif self.tilesize[1] != tileset.tileheight:
               raise Exception( 'Tile height mismatches!' )

         # Mark the tiles as undrawn on load so they'll be drawn at least once.
         self.tilesmoving = True
      except:
         # TODO: Set the map to a default or random map or something?
         self.logger.error(
            'Unable to load map "%s".' % mappath
         )
         self.logger.info(
            'Falling back to default map "%s"', DEFAULT_ADVENTURE_MAP
         )
         self.load_map( DEFAULT_ADVENTURE_MAP )

      self.set_viewport( 0, 0 )

   def set_viewport( self, x, y ):
      ClientEngine.set_viewport( self, x, y )

      # Setup the tile viewport based on map properties.
      self.tileviewport = (
         self.viewport[0],
         self.viewport[1],
         self.viewport[2] / self.gamemap.tilesets[0].tilewidth,
         self.viewport[3] / self.gamemap.tilesets[0].tileheight
      )

   def render_layer( self, layer_index ):
      for row in range( self.tileviewport[1], self.tileviewport[3] ):
         for column in \
         range( self.tileviewport[0], self.tileviewport[2] ):
            # Some layers may be missing tiles.
            try:
               self.graphicslayer.screen_blit(
                  self.gamemap.getTileImage( column, row, layer_index ),
                  destrect=(
                     (column * self.tilesize[0]) - self.viewport[0],
                     (row * self.tilesize[1]) - self.viewport[1],
                     self.tilesize[0],
                     self.tilesize[1]
                  )
               )
            except:
               pass

   def loop( self ):
      self.running = True
      while self.running:

         self.client.process_once()
         
         # TODO: Render layers. Likely: L1/L2 alternating first as animation,
         #       then sprites and objects, then M1/M2 midway through them
         #       (e.g. for standing in grass), then H1/H2 above them.

         # TODO: Only render tiles that have been changed recently (either by
         #       viewport movement or a mobile walking on/over them).

         if self.tilesmoving:
            # Lower layer (below player).
            self.render_layer( 0 )

         if self.tilesmoving:
            # TODO: Middle layer upper-half (below player).
            self.render_layer( 1 )

         # TODO: Ground mobiles.

         if self.tilesmoving:
            # TODO: Middle layer lower-half (above player).
            self.render_layer( 1 )

         if self.tilesmoving:
            # Upper layer (above player).
            self.render_layer( 2 )

         # TODO: Sky mobiles.

         if self.tilesmoving:
            self.tilesmoving = False

         # Loop maintenance.
         self.graphicslayer.screen_flip()
         #gamelayer.sleep( 100 )

