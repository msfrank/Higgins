# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from pkg_resources import Environment, working_set
from twisted.application.service import Service as _Service
from higgins.settings import Configurable
from higgins.logger import Loggable

class Service(_Service, Configurable):
    def __init__(self, name):
        Configurable.__init__(self, name)
    def initService(self, core):
        pass
    def cleanupService(self):
        pass

class PluginStore(object, Loggable):
    log_domain = "loader"

    def load(self, pluginDirs=[]):
        """
        Load the plugin store, looking in sys.path plus any directories specified
        in pluginDirs.
        """
        _pluginDirs = []
        for d in pluginDirs:
            if os.path.isdir(d):
                working_set.add_entry(d)
                _pluginDirs.append(d)
                self.log_info("added %s to plugin search path" % d)
            else:
                self.log_warning("ignoring path %s: not a directory" % d)
        env = Environment(_pluginDirs)
        eggs,errors = working_set.find_plugins(env)
        # load plugin eggs
        for p in eggs:
            working_set.add(p)
            self.log_info("loaded plugin egg %s" % p)
        for e in errors:
            self.log_error("failed to load plugin egg %s" % e)

    def listEntryPoints(self, group, type):
        """
        List all discovered entry points in the named group of the specified type
        """
        eps = []
        for ep in working_set.iter_entry_points(group):
            try:
                cls = ep.load()
                if not issubclass(cls, type):
                    self.log_warning("ignoring plugin '%s': entry point has the wrong type" % ep.name)
                else:
                    eps.append((ep.name, cls))
            except Exception, e:
                self.log_error("failed to load plugin '%s': %s" % (ep.name, e))
        return eps

    def findEntryPoint(self, group, name, type):
        ep = None
        for _ep in working_set.iter_entry_points(group, name):
            if ep == None:
                ep = _ep
        try:
            cls = ep.load()
        except Exception, e:
            self.log_error("failed to load plugin '%s': %s" % (ep.name, e))
            return None
        if not issubclass(cls, type):
            self.log_warning("ignoring plugin '%s': entry point has the wrong type" % ep.name)
            return None
        return cls

    def loadEntryPoint(self, group, name, type):
        cls = self.findEntryPoint(group, name, type)
        return cls()

plugins = PluginStore()

__all__ = ['plugins','Service']
