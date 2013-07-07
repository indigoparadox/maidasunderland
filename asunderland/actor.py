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

class Actor:

   # These don't seem to encode, for some reason, so they should be client-use-
   # only.
   framerect = 'DWALK1'
   framecountdown = SPRITE_FRAME_LEN

   walkoffset = (0, 0)
   walkoldtilecoords = [] # A list to enable longer-than-1-tile walks someday.

   def __init__( self ):
      self.sprite = 'mob_sprites_maid_black.png'
      self.maptilecoords = (0, 0)

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
         # XXX: This seems to append an increasing number of tiles with each
         #      call.
         #for oldtile in self.walkoldtilecoords:
         #   engine.tilesdirty.append( oldtile )
      elif 0 < len( self.walkoldtilecoords ):
         self.walkoldtilecoords = []

      # Choose the correct next animation frame.
      if self.framecountdown < 0:
         self.framerect = SPRITE_FRAME_NEXT.get( self.framerect )
         self.framecountdown = SPRITE_FRAME_LEN
         engine.tilesdirty.append( tuple( self.maptilecoords ) )
      else:
         self.framecountdown -= 1

def actor_encode( actor ):
   return json.dumps( actor.__dict__ )

def actor_decode( actor_string, actor_mod=None ):

   # TODO: Handle partial dictionaries with specific attributes for an existing
   #       actor.
   
   # Create and populate an actor object.
   actor_dict = json.load( StringIO( actor_string ) )
   if None == actor_mod:
      actor_mod = Actor()
   # TODO: Maybe add some error checking for invalid keys and such.
   for dict_key in actor_dict.keys():
      setattr( actor_mod, dict_key, actor_dict[dict_key] )

   # Fill in missing or computed fields.
   actor_mod.spriteimage = gamelayer.load_image(
      'mobiles/{}'.format( actor_mod.sprite )
   )

   return actor_mod


