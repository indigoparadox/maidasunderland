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

from irc import server as irc_server

DEFAULT_PORT = 6300

class ServerClientHandler( irc_server.IRCClient ):
   def handle_away( self, params ):
      # TODO: Implement some kind of sleep bubble.
      pass

class ServerEngine():
   pass

class ServerAdventure( ServerEngine ):
   pass

