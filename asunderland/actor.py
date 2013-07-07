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

class Actor:

   def __init__( self ):
      self.sprite = 'mob_sprites_maid_black.png'
      self.maptilecoords = (0, 0)

def actor_encode( actor ):
   print 'XXXXXXXXXXXXXXXXXX'
   print actor.__dict__
   print 'XXXXXXXXXXXXXXXXXX'
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
   actor_mod.sprite_image = gamelayer.load_image(
      'mobiles/{}'.format( actor_mod.sprite )
   )

   return actor_mod


