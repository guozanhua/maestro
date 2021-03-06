# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

import logging
import os.path
pj = os.path.join

import maestro.util.plugin
import maestro.util.mixins
import maestro.core
import event

class Environment(maestro.util.mixins.Singleton):
   """ The main environment/namespace for the Maestro.
       This class is a singleton.
       
       @var pluginManager: The plugin manager for the system.
   """
   def __init__(self):
      if not hasattr(self, '_init_called'):
         self._init_called = True
         self.mPluginManager = None
         self.settings = None
         self.mCmdOpts = None
         self.mLogger  = logging.getLogger('environment.Environment')

   def initialize(self, settings, opts=None, progressCB=None):
      """ Initialize the environment. """
      self.settings = settings
      self.mCmdOpts = opts

      # -- Event Manager -- #
      # Create an event dispatcher that will:
      #   - Connect to remote event manager objects.
      #   - Emit events to remote event manager objects.
      self.mEventManager = event.EventManager()

      # -- Plugin manager -- #
      self.mPluginManager = maestro.util.plugin.PluginManager()
      self.mPluginManager.scan(pj(maestro.core.const.PLUGIN_DIR), progressCB)
      #self.pluginManager.scan(self.settings.plugin_paths, progressCB)
      plugins = self.mPluginManager.getPlugins(returnNameDict=True)
      self.mLogger.info('Environment found plug-ins:')
      for (name,p) in plugins.iteritems():
         self.mLogger.info('  %s : %s' % (name, p))
