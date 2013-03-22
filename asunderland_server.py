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

import argparse
from miniircd import miniircd

class AsunderlandClient( miniircd.Client ):

   ''' This class overrides the modified miniircd client handler, allowing most
   of the game-related tweaks to remain in this file, separate from the
   miniircd code.  '''

   pass

class AsunderlandServer( miniircd.Server ):

   ''' This class overrides the modified miniircd server, allowing most of the
   game-related tweaks to remain in this file, separate from the miniircd code.
   '''

   def create_client( self, conn ):
      print "Asunderland client!"
      return AsunderlandClient( self, conn )

def main():
   parser = argparse.ArgumentParser()
   options = parser.parse_args()

   # Quick and dirty. Just start a crude IRC server for now. We'll bolt it on
   # tothe game engine later.
   options.ports = [6300]
   options.password = ''
   options.motd = ''
   options.verbose = True
   options.debug = False
   options.logdir = ''
   options.statedir = ''

   server = AsunderlandServer( options )
   server.start()

if __name__ == '__main__':
   main()

