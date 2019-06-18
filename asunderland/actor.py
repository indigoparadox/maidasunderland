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
import json
import logging
from StringIO import StringIO

SPRITE_FRAME_LEN = 10

SPRITE_FRAME_RECTS = {
   'DWALK1': (0, 0, 32, 32),
   'DWALK2': (32, 0, 32, 32),
   'DWALK3': (0, 0, 32, 32),
   'DWALK4': (64, 0, 32, 32),
}

SPRITE_FRAME_NEXT = {
   'DWALK1': 'DWALK2',
   'DWALK2': 'DWALK3',
   'DWALK3': 'DWALK4',
   'DWALK4': 'DWALK1',
}

WALK_STEPS = 1 # These MUST be divisible by engine tile size.

log = logging.getLogger( __name__ )

class Actor:

   # Class attributes, for client animation use only.
   framerect = 'DWALK1'
   framecountdown = SPRITE_FRAME_LEN
   walkoffset = (0, 0)
   walkoldtilecoords = [] # A list to enable longer-than-1-tile walks.
   sprite = None

   @classmethod
   def from_json( cls, actor_string ):
      actor_out = Actor()

      # Create and populate an actor object.
      actor_dict = json.load( StringIO( actor_string ) )
      # TODO: Maybe add some error checking for invalid keys and such.
      for dict_key in actor_dict.keys():
         setattr( actor_out, dict_key, actor_dict[dict_key] )

      if actor_out.ready():
         # Fill in missing or computed fields.
         actor_out.spriteimage = gamelayer.load_image(
            'mobiles/{}'.format( actor_out.sprite )
         )

         return actor_out
      else:
         return None

   def __init__( self ):

      # TODO: Add a ready() function and have that return true when fields are
      #       full.
      #self.sprite = 'mob_sprites_maid_black.png'
      #self.maptilecoords = (0, 0)

      self.maptilecoords = (0, 0)

      animations = {}

   def ready( self ):
      if None == self.sprite:
         return False

      return True

   def get_framerect( self ):
      return SPRITE_FRAME_RECTS[self.framerect]

   def animate_tile( self, engine ):
      
      # Reduce the walking offset.
      if (0, 0) != self.walkoffset:
         # Calculate the new walk offset.
         # TODO: Clean this up!
         new_x = self.walkoffset[0]
         new_y = self.walkoffset[1]
         if 0 > self.walkoffset[0]:
            new_x = self.walkoffset[0] + WALK_STEPS
         elif 0 < self.walkoffset[0]:
            new_x = self.walkoffset[0] - WALK_STEPS
         if 0 > self.walkoffset[1]:
            new_y = self.walkoffset[1] + WALK_STEPS
         elif 0 < self.walkoffset[1]:
            new_y = self.walkoffset[1] - WALK_STEPS
         self.walkoffset = (new_x, new_y)

         # Make sure the old tiles get redrawn.
         for oldtile in self.walkoldtilecoords:
            #log.debug(
            #   'Adding {}, {} to dirty tiles.'.format( oldtile[0], oldtile[1] )
            #)
            engine.tilesdirty.append( oldtile )
      elif 0 < len( self.walkoldtilecoords ):
         log.debug(
            # TODO: Implement sprite name/serial.
            '{} clearing walked tile list.'.format( 0 )
         )
         # Clear the list in-place so that it's emptied despite being 
         # referenced all over the place.
         del self.walkoldtilecoords[0:len( self.walkoldtilecoords )]

      # Choose the correct next animation frame.
      if self.framecountdown < 0:
         self.framerect = SPRITE_FRAME_NEXT.get( self.framerect )
         self.framecountdown = SPRITE_FRAME_LEN
         engine.tilesdirty.append( tuple( self.maptilecoords ) )
      else:
         self.framecountdown -= 1

   def from_json_partial( self, actor_string ):
      # TODO: Handle partial dictionaries with specific attributes for an
      #       existing actor.
      pass

   def to_json( self ):
      return json.dumps( self.__dict__ )

