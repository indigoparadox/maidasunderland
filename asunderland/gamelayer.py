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
from threading import Thread, Lock

class InputLayer( Thread ):

   ''' This class runs constantly in the background and tries to make the other
   classes do things based on user input received. '''

   engine = None

   def __init__( self, engine ):
      self.engine = engine
      Thread.__init__( self )

   def run( self ):
      # Wait for the engine to start up.
      while not self.engine.running:
         pygame.time.wait( 100 )
   
      pygame.fastevent.init()
      while self.engine.running:
         event = pygame.fastevent.wait()
         if event.type == pygame.QUIT:
            self.engine.running = False
         elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
               self.engine.running = False
            elif None != key_decode( event.key ):
               self.engine.process_key( key_decode( event.key ) )

class GraphicsLayer():
   config_data = None
   window = None

   def __init__( self, config_data_in ):
      self.config_data = config_data_in

   def start( self ):
      pygame.init()
      self.window = pygame.display.set_mode(
          (self.config_data['Options']['WindowWidth'],
         self.config_data['Options']['WindowHeight'])
      )
      pygame.display.set_caption( self.config_data['Title'] )

   def quit( self ):
      pygame.quit()

   def events_poll( self ):
      pass

   def screen_blank( self, color=(0, 0, 0) ):
      mask = pygame.Surface(
         (self.config_data['Options']['WindowWidth'],
            self.config_data['Options']['WindowHeight']),
         pygame.SRCALPHA
      )
      mask.fill( color )
      mask.set_alpha( 255 )
      self.window.blit( mask, (0, 0) )

   def screen_flip( self ):
      pygame.display.flip()

def sleep( sleep_us ):
   pygame.time.wait( sleep_us )

def key_decode( event_key_in ):
   
   ''' Given the result of a key event, this should return the character it
   produces, or a special abstract wrapper constant for non-letters/numbers.
   '''
   
   if 32 == event_key_in:
      # Pygame wants to call this "space".
      return ' '
   elif 33 <= event_key_in and 126 >= event_key_in:
      # Printable characters.
      return pygame.key.name( event_key_in )
   else:
      return None

