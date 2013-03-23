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
import logging
from irc import server as irc_server
from asunderland import server as as_server

def main():
   #parser = argparse.ArgumentParser()
   #options = parser.parse_args()

   logging.basicConfig()

   ## Quick and dirty. Just start a crude IRC server for now. We'll bolt it on
   ## tothe game engine later.
   my_server = irc_server.IRCServer(
      ("", 6300), as_server.ServerClientHandler
   )
   my_server.serve_forever()

if __name__ == '__main__':
   main()

