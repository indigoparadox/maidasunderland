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

import os
import logging
import argparse
from asunderland import *
from irc import server as irc_server
from threading import Thread
from yaml import load, dump
try:
   from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
   from yaml import Loader, Dumper

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument(
      '-d', '--debug', action='store_true', dest='debug',
      help='Display debug/info messages on stdout.'
   )
   args = parser.parse_args()

   if args.debug:
      logging.basicConfig( level=logging.DEBUG )
   else:
      logging.basicConfig()

   my_logger = logging.getLogger( 'asunderland' )

   # If there's a data directory, descend into it.
   if os.path.isdir( 'data' ):
      os.chdir( 'data' )

   # Read configuration.
   configdata = None
   try:
      with open( 'config.yaml', 'r' ) as configfile:
         configdata = load( configfile )
   except:
      my_logger.error( 'Unable to open configuration file. Aborting.' )

   # Start the abstraction layers and game engine.
   my_graphicslayer = gamelayer.GraphicsLayer( configdata )
   my_graphicslayer.start()
   my_engine = client.ClientTitle( configdata, my_graphicslayer )

   # Keep playing until we don't get passed another engine by the main loop.
   my_server = None
   while None != my_engine:
      # Setup a fresh game layer.
      my_inputlayer = gamelayer.InputLayer( my_engine )
      my_inputlayer.start()

      if not isinstance( my_engine, client.ClientTitle ):
         # If this is an SP game, start a local server to host it in the
         # background.
         my_logger.info( 'Starting server on localhost for single player...' )
         my_server = server.AsunderlandIRCServer(
            ('localhost', server.DEFAULT_PORT),
            server.AsunderlandIRCClientHandler
         )
         Thread( target=my_server.serve_forever ).start()
         my_engine.connect()

      # Delegate the main loop to the engine we've built.
      my_engine = my_engine.loop()
      if None != my_server:
         my_logger.info( 'Stopping server on localhost...' )
         my_server.shutdown()

   my_graphicslayer.quit()
   logging.shutdown()

if __name__ == '__main__':
   main()

