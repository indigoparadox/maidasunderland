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
from asunderland import *
from yaml import load, dump
try:
   from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
   from yaml import Loader, Dumper

def main():
   # If there's a data directory, descend into it.
   if os.path.isdir( 'data' ):
      os.chdir( 'data' )

   # Read configuration.
   config_data = None
   try:
      with open( 'config.yaml', 'r' ) as config_file:
         config_data = load( config_file )
   except:
      print "Unable to open configuration file. Aborting."

   # Start the abstraction layers and game engine.
   my_graphicslayer = gamelayer.GraphicsLayer( config_data )
   my_graphicslayer.start()
   my_engine = engine.EngineTitle( my_graphicslayer )
   my_inputlayer = gamelayer.InputLayer( my_engine )
   my_inputlayer.start()
   my_engine.loop()
   my_graphicslayer.quit()
   pass

if __name__ == '__main__':
   main()

