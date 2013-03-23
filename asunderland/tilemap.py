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

import logging
import gamelayer
from yaml import load, dump
try:
   from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
   from yaml import Loader, Dumper

class Tile():
   prototype = None # A reference to a ProtoTile.

class ProtoTile():

   ''' A prototypical tile stored in the tiles list in a tileset. '''

   tileset = None
   framecoords = [] # A list of coords for each animation frame.
   frameindex = 0 # The index of the last framecoord drawn.
   resistance = 0

   def __init__( self, tileset, coords, resistance=0 ):
      self.tileset = tileset
      self.framecoords = coords

   def get_current_frame( self ):
      try:
         return self.framecoords[frameindex]
      except:
         return None

   def animate_next( self ):
      if len( self.framecoords ) > self.frameindex + 1:
         self.frameindex += 1
      else:
         self.frameindex = 0

class TileSet():
   image = None
   prototiles = []

class TileMap():
   tiles = []
   tilesets = [] # One map can pull in more than one TileSet.
   logger = None

   def __init__( self ):
      self.logger = logging.getLogger( 'asunderland.tilemap' )

   def load_tileset( self, tilesetpath ):
      try:
         self.logger.debug(
            'Loading tileset "%s"...' % tilesetpath
         )
         with open( tilesetpath, 'r' ) as tilesetfile:
            tileset = TileSet()
            tilesetdata = load( tilesetfile )
            tileset.image = gamelayer.load_image( tilesetdata['Image'] )
            for tiledata in tilesetdata['Tiles']:
               coordlist = []
               for coord in tiledata['Frames']:
                  coordlist.append( (coord['X'], coord['Y']) )
               self.logger.debug(
                  'Loading tile "%s" with frames: %s' % 
                     (tiledata['Name'], coordlist)
               )
               tileset.prototiles.append( ProtoTile(
                  tileset, coordlist, tiledata['Resistance']
               ) )
               
      except:
         self.logger.error( 'Unable to load tileset %s!' % tilesetpath )

