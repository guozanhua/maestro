# Maestro is Copyright (C) 2006 by Infiscape
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os
import popen2
import pwd
import re

import maestro.core
import procutil


class XsetSaverPlugin(maestro.core.ISaverPlugin):
   '''
   A screen saver management plug-in that wraps usage of the standard X11
   command xset(1). The xset(1) command controls screen blanking and DPMS.
   '''
   def __init__(self):
      maestro.core.ISaverPlugin.__init__(self)
      env = maestro.core.Environment()
      if env.settings.has_key('xset_cmd'):
         self.mCmd = env.settings['xset_cmd']
      else:
         self.mCmd = '/usr/X11R6/bin/xset'

   def getName():
      return 'xset'
   getName = staticmethod(getName)

   blank_re = re.compile('\s+timeout:\s+(\d)\s+.*')

   def isSaverEnabled(self, avatar):
      # Run 'xset q' and determine the setting of the screen saver timeout.
      (child_stdout, child_stdin) = popen2.popen2([self.mCmd, 'q'])
      lines = child_stdout.readlines()
      child_stdout.close()
      child_stdin.close()

      enabled = False

      for l in lines:
         match = self.blank_re.search(l)
         # If we have matched the line with the screen saver timeout value,
         # check to see if it is a non-zero value. A non-zero setting for the
         # timeout indicates that the screen will be blanked (eventually).
         if match is not None:
            if int(match.group(1)) != 0:
               enabled = True
            break

      return enabled

   def isSaverRunning(self, avatar):
      '''
      Indicates whether a screen saver is currently running on the local
      computer. This implementation always returns True because it is not
      possible to determine if the display is currently blanked. Hence, we
      assume that it is.
      '''
      return True

   def setSaverEnabled(self, avatar, enabled):
      pid = os.fork()
      if pid == 0:
         self.__changeToUserName(avatar.mCredentials['username'])
         if enabled:
            flag = 'on'
         else:
            flag = 'off'

         env = os.environ.copy()
         env['XAUTHORITY'] = os.environ['USER_XAUTHORITY']
         os.execle(self.mCmd, self.mCmd, 's', flag, env)

      (child_pid, status) = procutil.waitpidRetryOnEINTR(pid, 0)

   def stopSaver(self, avatar):
      pid = os.fork()
      if pid == 0:
         self.__changeToUserName(avatar.mCredentials['username'])
         env = os.environ.copy()
         env['XAUTHORITY'] = os.environ['USER_XAUTHORITY']
         os.execle(self.mCmd, self.mCmd, 's', 'reset', env)

      (child_pid, status) = procutil.waitpidRetryOnEINTR(pid, 0)

   def __changeToUserName(self, userName):
      pw_entry = pwd.getpwnam(userName)
      self.__changeToUser(pw_entry[2], pw_entry[3])

   def __changeToUser(self, uid, gid):
      # NOTE: os.setgid() must be called first or else we will get an
      # "operation not permitted" error.
      os.setgid(gid)
      os.setuid(uid)
