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
import ssl
import functools
import json
import irc.connection
import irc.client
from actor import Actor
from threading import Thread
from yaml import load, dump
try:
   from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
   from yaml import Loader, Dumper

DEFAULT_ADVENTURE_MAP = 'Farm'

MAP_PROCESS_TIMEOUT = 10

log = logging.getLogger( __name__ )

class AsunderlandIRCClient( irc.client.IRC ):
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
   actors = {} # All of the actors online right now.

   def __init__( self, configdata, graphicslayer ):
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
         log.info( serveraddress )
         self.serveraddress = serveraddress
         log.info(
            'Connecting to %s on port %d...' % self.serveraddress
         )
         self.channel = channel
         self.client = AsunderlandIRCClient()
         my_server = self.client.server()
         # TODO: Implement trusted CA?
         ssl_wrapper = functools.partial( ssl.wrap_socket )
         self.connection = my_server.connect(
            serveraddress[0],
            serveraddress[1],
            'tester', # FIXME
            connect_factory = irc.connection.Factory( wrapper=ssl_wrapper )
         )
         # TODO: Handle failed connection.
         log.info(
            'SSL peer name: ' + str( self.connection.socket.getpeername() )
         )
         log.info(
            'SSL cipher: ' + str( self.connection.socket.cipher() )
         )
         log.info(
            'SSL certificate: ' +
               str( self.connection.socket.getpeercert() )
         )
         #print vars( self.connection.socket )
         self.connection.join( self.channel )

         self.connection.add_global_handler( 'join', self.on_join )
         self.connection.add_global_handler( 'part', self.on_part )
         self.connection.add_global_handler( 'whoisuser', self.on_whoisuser )
         # TODO: Handle nick changes and the actors list.

         # TODO: Send a real actor command with parameters.
         self.connection.send_raw( 'ACTOR' )

      else:
         # Preserve a pre-existing client connection.
         pass

   def on_join( self, connection, event ):
      log.info( 'Peer joined: ' + event.source )

      # Get more information about the new joining client.
      name_match = re.match( r'(.*)!(.*)@(.*)', event.source )
      self.whois( [name_match.groups()[0]], fetchactor=True )

   def on_part( self, connection, event ):
      pass

   def on_whoisuser( self, connection, event ):
      # This is probably pretty rude, but take actor data slipped in in
      # response to a WHOIS request and append it to the actors list.
      jdata_string = ' '.join( event.arguments[2:] )
      log.info( 'Received actor for {}: {} '.format(
         event.arguments[1], jdata_string
      ) )
      # TODO: Handle partial dictionaries with specific attributes for an
      #       existing actor.
      my_actor = Actor.from_json( jdata_string )
      if None != my_actor:
         self.actors[event.arguments[1]] = my_actor

   def set_viewport( self, x, y ):
      self.viewport = (
         x, y,
         self.viewport[2],
         self.viewport[3]
      )

   def whois( self, targets, fetchactor=False ):

      '''Send a WHOIS command. Optionally fetch actor information.'''

      if fetchactor:
         self.connection.send_raw(
            'WHOIS {} ACTOR'.format( ','.join( targets ) )
         )
      else:
         self.connection.send_raw( 'WHOIS {}'.format( ','.join( targets ) ) )


class ClientTitle( ClientEngine ):

   ''' This engine should be somewhat unique in that it has no real server
   component. All state is handled within the engine module.

   It should just display a pretty menu from which options relevant to starting
   the game proper may be selected. '''

   def process_key( self, key_char_in ):
      self.running = False

   def loop( self ):
      self.running = True
      log.info( "Press any key to continue..." )
      self.graphicslayer.screen_blank( (255, 255, 255) )
      while self.running:

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

   loaded = False
   gamemap = None
   tileviewport = None
   tilesize = (0, 0)
   tilesdirty = []

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
      # TODO: Remove these handlers on room change away from this one.
      self.connection.add_global_handler( 'topic', self.on_topic )
      process = 0
      while None == self.gamemap and process < MAP_PROCESS_TIMEOUT:
         self.client.process_once()
         process += 1

      if None == self.gamemap:
         # Set the map to a default map.
         log.warn( 'No topic received.' )
         log.info(
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
         log.error( 'No map specified in topic.' )
         log.info(
            'Falling back to default map "%s"', DEFAULT_ADVENTURE_MAP
         )
         self.load_map( DEFAULT_ADVENTURE_MAP )

   def on_whoisuser( self, connection, event ):
      
      # Try to find the specified actor in our list and mark their tile as
      # dirty in advance, since it's probably going to be different soon.
      old_coords = None
      dirty_actor = self.actors.get( event.arguments[1] )
      if None != dirty_actor:
         old_coords = tuple( dirty_actor.maptilecoords )
         self.tilesdirty.append( old_coords )

      ClientEngine.on_whoisuser( self, connection, event )

      new_coords = None
      dirty_actor = self.actors.get( event.arguments[1] )
      if None != dirty_actor:
         new_coords = tuple( dirty_actor.maptilecoords )
         self.tilesdirty.append( new_coords )

      # If we moved somewhere then set the walk offset for drawing to enable
      # the "gliding" effect instead of "blinking" from place to place.
      if None != old_coords and None != new_coords:
         dirty_actor.walkoffset = tuple( (
            (old_coords[0] - new_coords[0]) * self.tilesize[0],
            (old_coords[1] - new_coords[1]) * self.tilesize[1]
         ) )
         dirty_actor.walkoldtilecoords.append( old_coords )
         dirty_actor.walkoldtilecoords.append( new_coords )

   def process_key( self, key_char_in ):
      #self.connection.privmsg( self.channel, key_char_in )
      self.connection.send_raw( 'MOVEMENT {}'.format( key_char_in ) )

   def load_map( self, mapname ):
      try:
         # Load the map data file.
         mappath = os.path.join( 'maps', mapname + '.tmx' )
         log.info( 'Attempting to load map "%s"...' % mappath )

         # TODO: Should this be abstracted, since it kind of relies on PyGame?
         self.gamemap = pytmx.tmxloader.load_pygame( mappath, pixelalpha=True )

         # Make sure the tile layers are homogenous.
         self.tilesize = (self.gamemap.tilesets[0].tilewidth,
            self.gamemap.tilesets[0].tileheight)
         for tileset in self.gamemap.tilesets:
            if self.tilesize[0] != tileset.tilewidth: 
               raise Exception( 'Tile width mismatches!' )
            elif self.tilesize[1] != tileset.tileheight:
               raise Exception( 'Tile height mismatches!' )
      except:
         # TODO: Set the map to a default or random map or something?
         log.error(
            'Unable to load map "%s".' % mappath
         )
         log.info(
            'Falling back to default map "%s"', DEFAULT_ADVENTURE_MAP
         )
         self.load_map( DEFAULT_ADVENTURE_MAP )

      self.set_viewport( 0, 0 )
      # Mark the tiles as undrawn on load so they'll be drawn at least once.
      #self.tilesmoving = True
      for row in range( self.tileviewport[0], self.tileviewport[2] ):
         for column in range( self.tileviewport[1], self.tileviewport[3] ):
            self.tilesdirty.append( (row, column) )

      self.loaded = True

   def set_viewport( self, x, y ):
      ClientEngine.set_viewport( self, x, y )

      # Setup the tile viewport based on map properties.
      self.tileviewport = (
         self.viewport[0],
         self.viewport[1],
         self.viewport[2] / self.gamemap.tilesets[0].tilewidth,
         self.viewport[3] / self.gamemap.tilesets[0].tileheight
      )

   def _render_mobile( self, coords, mobile_actor, cliprect=None ):

      if None != cliprect:
         renderrect = tuple(
            x - y for x, y in zip( mobile_actor.get_framerect(), cliprect )
         )
      else:
         renderrect = mobile_actor.get_framerect()

      self.graphicslayer.screen_blit(
         mobile_actor.spriteimage,
         sourcerect=renderrect,
         destrect=(
            (mobile_actor.maptilecoords[0] * self.tilesize[0]) 
               - self.viewport[0] + mobile_actor.walkoffset[0],
            (mobile_actor.maptilecoords[1] * self.tilesize[1]) 
               - self.viewport[1] + mobile_actor.walkoffset[1],
            renderrect[2],
            renderrect[3]
         )
      )

   def _render_tile_layer(
      self, coords, layer, sourcerect=None, destoffset=None,
   ):

      if None == sourcerect:
         sourcerect = (0, 0, self.tilesize[0], self.tilesize[1])

      if None == destoffset:
         destoffset = (0, 0, 0, 0)

      # Some layers may be missing tiles.
      try:
         self.graphicslayer.screen_blit(
            self.gamemap.getTileImage( coords[0], coords[1], layer ),
            sourcerect=sourcerect,
            destrect=(
               (coords[0] * self.tilesize[0]) - self.viewport[0]
                  + destoffset[0],
               (coords[1] * self.tilesize[1]) - self.viewport[1]
                  + destoffset[1],
               self.tilesize[0] + destoffset[2],
               self.tilesize[1] + destoffset[3]
            )
         )
      except:
         pass

   def render_tile( self, coords, debug=False ):

      # Lower layer (below mobiles).
      self._render_tile_layer( coords, 0 )

      # Middle layer upper-half (below mobiles).
      self._render_tile_layer( coords, 1 )

      # DEBUG:
      #if debug and not self.walk_debug_first_pass:
      #   self.graphicslayer.screen_rect(
      #      (0, 0, 255),
      #      destrect=(
      #         (coords[0] * self.tilesize[0]) - self.viewport[0],
      #         (coords[1] * self.tilesize[1]) - self.viewport[1],
      #         32,
      #         32
      #      )
      #   )

      # Ground mobiles.
      for actor_key in self.actors.keys():
         if 0 != self.gamemap.getTileGID( coords[0], coords[1], 1 ):
            # We're wading through something in the middle layer, so cut the
            # render in half.
            self._render_mobile(
               coords,
               self.actors[actor_key],
               cliprect=(
                  0, 0, 0, self.tilesize[1] / 2
               )
            )
         else:
            self._render_mobile( coords, self.actors[actor_key] )

      # Upper layer (above mobiles).
      self._render_tile_layer( coords, 2 )

      # TODO: Sky mobiles.

      #coords_index = self.tilesdirty.index( coords )
      #del self.tilesdirty[coords_index]

   def loop( self ):
      self.running = True

      # DEBUG:
      self.walk_debug_first_pass = True

      while self.running:

         # Handle IRC events.
         self.client.process_once()

         if not self.loaded:
            continue

         for actor_key in self.actors.keys():
            # This will mark the mobile's tile as dirty, too.
            self.actors[actor_key].animate_tile( self )

         #log.debug( 'Beginning render cycle.' )

         # Render dirty tiles.
         for dirty_coords in self.tilesdirty:
            #log.debug( 'Rendering dirty tile {}'.format( dirty_coords ) )
            self.render_tile( dirty_coords, True )
         # Clear the list in-place so that it's emptied despite being 
         # referenced all over the place.
         del self.tilesdirty[0:len( self.tilesdirty )]

         # DEBUG:
         self.walk_debug_first_pass = False
            
         # Loop maintenance.
         self.graphicslayer.screen_flip()

