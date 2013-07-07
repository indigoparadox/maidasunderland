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
import logging
from threading import Thread, Lock

UP = 'UP'
DOWN = 'DOWN'
RIGHT = 'RIGHT'
LEFT = 'LEFT'

MAXLOGFRAMES = 100

log = logging.getLogger( __name__ )

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
   configdata = None
   window = None
   dirtyrects = []
   clock = None
   logframes = 0

   def __init__( self, configdata_in ):
      self.configdata = configdata_in
      self.clock = pygame.time.Clock()

   def start( self ):
      pygame.init()
      self.window = pygame.display.set_mode(
          (self.configdata['Options']['WindowWidth'],
         self.configdata['Options']['WindowHeight'])
      )
      pygame.display.set_caption( self.configdata['Title'] )

   def quit( self ):
      pygame.quit()

   def events_poll( self ):
      pass

   def screen_dirty( self, destrect ):
      #log.debug( 'Marking {} as dirty.'.format( destrect ) )
      self.dirtyrects.append( pygame.Rect(
         destrect[0],
         destrect[1],
         destrect[2],
         destrect[3]
      ) )

   def screen_blit(
      self, sourceimage, destimage=None, sourcerect=None, destrect=None
   ):
   
      ''' Blit the given image to the screen.

      sourcerect/destrect should be 4-tuples in the format 
         (left,top,width,height). '''

      if None == destrect:
         log.error( 'Invalid destrect specified. Aborting.' )
         return

      if None == destimage:
         destimage = self.window

      # Add anything blitted to the list of dirty rectangles.
      self.screen_dirty( destrect )

      # TODO: If source rect and dest rect don't match then scale them.
      if None == sourcerect:
         destimage.blit( sourceimage, destrect )      
      else:
         destimage.blit( sourceimage, destrect, area=sourcerect )

   def screen_blank( self, color=(0, 0, 0) ):
      mask = pygame.Surface(
         (self.configdata['Options']['WindowWidth'],
            self.configdata['Options']['WindowHeight']),
         pygame.SRCALPHA
      )
      mask.fill( color )
      mask.set_alpha( 255 )
      self.window.blit( mask, (0, 0) )

      # Mark the whole screen as dirty.
      self.screen_dirty( (
         0,
         0,
         self.configdata['Options']['WindowWidth'],
         self.configdata['Options']['WindowHeight']
      ) )

   def screen_flip( self ):
      pygame.display.update( self.dirtyrects )
      #pygame.display.flip()
      del self.dirtyrects[0:len( self.dirtyrects )]
      
      self.clock.tick_busy_loop( 60 )

      # Display the FPS counter to the debug log.
      self.logframes += 1
      if MAXLOGFRAMES <= self.logframes:
         log.debug( 'FPS: ' + str( self.clock.get_fps() ) )
         self.logframes = 0

def sleep( sleep_us ):
   pygame.time.wait( sleep_us )

def load_image( image_path_in ):
   return pygame.image.load( image_path_in ).convert()

def size_image( image_in ):
   return (image_in.get_width(), image_in.get_height())

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
   elif 273 == event_key_in:
      return UP
   elif 274 == event_key_in:
      return DOWN
   elif 275 == event_key_in:
      return RIGHT
   elif 276 == event_key_in:
      return LEFT
   else:
      return None

