# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from pkg_resources import Environment, working_set
from higgins.settings import settings
from higgins.service import Service
from higgins.logger import Loggable

class PluginStore(object, Loggable):
    log_domain = "loader"

    def __init__(self):
        self._plugins = {}
        self._isLoaded = False
        self.pluginDirs = []

    def load(self, dirs=[]):
        if self._isLoaded:
            raise Exception("plugins have already been loaded")
        for d in dirs:
            if os.path.isdir(d):
                self.pluginDirs.append(d)
                working_set.add_entry(d)
                self.log_info("added '%s' to plugin search path" % d)
            else:
                self.log_warning("ignoring path %s: not a directory" % d)
        env = Environment(self.pluginDirs)
        self._eggs,errors = working_set.find_plugins(env)
        # load plugin eggs
        for p in self._eggs:
            working_set.add(p)
            self.log_info("loaded plugin egg '%s'" % p)
        for e in errors:
            self.log_error("failed to load plugin egg '%s'" % e)
        # load all discovered plugins
        for ep in working_set.iter_entry_points('higgins.plugin'):
            try:
                factory = ep.load()
                if issubclass(factory, Service):
                    self.log_info("found service plugin '%s'" % ep.name)
                    self._plugins[ep.name] = factory
                else:
                    self.log_warning("ignoring plugin '%s': unknown plugin type" % ep.name)
            except Exception, e:
                self.log_error("failed to load plugin '%s': %s" % (ep.name, e))

    def __getitem__(self, key):
        return self._plugins[key]

    def __setitem__(self, key, value):
        raise Exception("PluginStore is read-only!")

    def __delitem__(self, key):
        raise Exception("PluginStore is read-only!")

    def __iter__(self):
        return iter(self._plugins.items())

    def __contains__(self, item):
        return item in self._plugins

plugins = PluginStore()


__all__ = ['plugins',]
