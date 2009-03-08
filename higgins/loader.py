# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from pkg_resources import Environment, working_set
from higgins.site_settings import site_settings
from higgins.service import Service
from higgins.logger import Loggable

class PluginLoader(object, Loggable):
    log_domain = "loader"

    def __init__(self):
        self._plugins = {}
        plugins_dir = os.path.join(site_settings["HIGGINS_DIR"], "plugins")
        self.log_debug("added '%s' to plugin search path" % plugins_dir)
        working_set.add_entry(plugins_dir)
        env = Environment([plugins_dir,])
        self._eggs,errors = working_set.find_plugins(env)
        # load plugin eggs
        for p in self._eggs:
            working_set.add(p)
            self.log_debug("loaded plugin egg '%s'" % p)
        for e in errors:
            self.log_error("failed to load plugin egg '%s'" % e)
        # load all discovered plugins
        for ep in working_set.iter_entry_points('higgins.plugin'):
            try:
                factory = ep.load()
                if issubclass(factory, Service):
                    self.log_debug("found service plugin '%s'" % ep.name)
                    self._plugins[ep.name] = factory
                else:
                    self.log_warning("ignoring plugin '%s': unknown plugin type" % ep.name)
            except Exception, e:
                self.log_error("failed to load plugin '%s': %s" % (ep.name, e))

    def __getitem__(self, key):
        return self._plugins[key]

    def __setitem__(self, key, value):
        raise Exception("Loader map is read-only!")

    def __delitem__(self, key):
        raise Exception("Loader map is read-only!")

    def __iter__(self):
        return iter(self._plugins.items())

    def __contains__(self, item):
        return item in self._plugins
