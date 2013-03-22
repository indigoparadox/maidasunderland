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

import pygame

class GameLayer():
   config_data = None

   def __init__( self, config_data_in ):
      self.config_data = config_data_in

   def start( self ):
      pygame.init()
      window = pygame.display.set_mode(
          (self.config_data['Options']['WindowWidth'],
         self.config_data['Options']['WindowHeight'])
      )
      pygame.display.set_caption( self.config_data['Title'] )

   def quit( self ):
      pygame.quit()

   def events_poll( self ):
      pass

   def screen_blank( self ):
      pass

   def sleep( self, sleep_us ):
      pygame.time.wait( sleep_us )

