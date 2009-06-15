# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from os.path import join as pathjoin
from pkg_resources import resource_string
from twisted.application.service import MultiService
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from django.conf.urls.defaults import *
from django.db.models.signals import post_save, post_delete
from higgins.conf import conf
from higgins.service import Service
from higgins.http import server, channel
from higgins.http import resource, wsgi
from higgins.http.http import Response
from higgins.core.content_resource import ContentResource
from higgins.core.configurator import Configurator, IntegerSetting
from higgins.core.manager import ManagerResource
from higgins.core.logger import CoreLogger
from higgins.upnp.service import UPNPService
from higgins.upnp.device import UPNPDevice

class CoreHttpConfig(Configurator):
    pretty_name = "HTTP Server"
    description = "Configure the built-in HTTP Server"
    HTTP_PORT = IntegerSetting("Listening Port", 8000, min_value=0, max_value=65535)

class RootResource(resource.Resource):
    def __init__(self, service):
        self.service = service
    def locateChild(self, request, segments):
        if segments == []:
            return self, []
        if segments[0] == "content":
            return ContentResource(), segments[1:]
        if segments[0] == "static":
            return StaticResource(), segments
        if segments[0] == "manage":
            return ManagerResource(), segments[1:]
        if segments[0] == "library":
            return LibraryResource(), segments[1:]
        if segments[0] == "settings":
            return SettingsResource(self.service), segments[1:]
        #if segments[0] == "app":
        #    return ManagerResource(), segments[1:]
        None, []
    def http_GET(self, request):
        return render_to_response('templates/library-front.t', {})

class CoreService(MultiService, CoreLogger):
    def __init__(self):
        self._plugins = {}
        # start the webserver
        self._site = server.Site(RootResource())
        MultiService.__init__(self)

    def startService(self):
        MultiService.startService(self)
        self._listener = reactor.listenTCP(CoreHttpConfig.HTTP_PORT, channel.HTTPFactory(self._site))
        self.log_info("started core service")
        self.upnp_service = UPNPService()
        try:
            # load enabled services
            for name in conf.get("CORE_ENABLED_PLUGINS", []):
                self.enablePlugin(name)
            self.log_debug("started all enabled services")
        except Exception, e:
            raise e

    def _doStopService(self, result):
        self._listener.stopListening()
        self.log_info("stopped core service")

    def stopService(self):
        d = maybeDeferred(MultiService.stopService, self)
        d.addCallback(self._doStopService)
        return d

    def registerPlugin(self, name, plugin):
        """
        Load the plugin.  This method instantiates the plugin, i.e. the
        plugin's __init__ method is invoked here.
        """
        try:
            if name in self._plugins:
                raise Exception("plugin already exists")
            plugin = plugin()
            plugin.setName(name)
            # initialize any discovered configurators
            def init_configs_recursive(configs):
                if configs == None:
                    return
                if isinstance(configs, Configurator):
                    configs()
                elif isinstance(configs, dict):
                    for name,config in configs.items():
                        if isinstance(config, Configurator):
                            config()
                        elif isinstance(config, dict):
                            init_configs_recursive(config)
            init_configs_recursive(plugin.configs)                
            self._plugins[name] = plugin
            self.log_info("registered plugin '%s'" % name)
        except Exception, e:
            self.log_error("failed to register plugin '%s': %s" % (name, e))

    def unregisterPlugin(self, name):
        """
        Unloads the plugin.  After this method has been invoked, it is no
        longer possible to enable or disable the plugin.
        """
        try:
            if not name in self._plugins:
                raise Exception("plugin doesn't exist")
            if self.pluginIsEnabled(name):
                self.disablePlugin(name)
            del self._plugins[name]
            self.log_info("unregistered plugin '%s'" % name)
        except Exception, e:
            self.log_error("failed to unregister plugin '%s': %s" % (name, e))

    def enablePlugin(self, name):
        """Enables the named plugin."""
        try:
            if not name in self._plugins:
                raise Exception("plugin doesn't exist")
            if self.pluginIsEnabled(name):
                raise Exception("plugin is already enabled")
            plugin = self._plugins[name]
            # if plugin is a UPnP device, then check if the UPnP server is running
            if isinstance(plugin, UPNPDevice):
                # if it isn't, then start it
                if self.upnp_service.running == 0:
                    # setServiceParent() implicitly calls startService()
                    self.upnp_service.setServiceParent(self)
                if plugin.parent == None:
                    plugin.setServiceParent(self.upnp_service)
                else:
                    plugin.startService()
                # register UPNP device
                self.upnp_service.registerUPNPDevice(plugin)
            # otherwise plugin is a simple Service
            else:
                if plugin.parent == None:
                    plugin.setServiceParent(self)
                else:
                    plugin.startService()
            # update the list of enabled plugins
            conf.set(CORE_ENABLED_PLUGINS=[pname for pname,plugin in self._plugins.items() if plugin.running])
            self.log_info("enabled plugin '%s'" % name)
        except Exception, e:
            self.log_error("failed to enable plugin '%s': %s" % (name, e))

    def _doDisablePlugin(self, result, name, plugin):
        #if not self.upnp_service.running == 0:
        #    self.upnp_service.disownParent()
        if isinstance(plugin, UPNPDevice):
            self.upnp_service.unregisterUPNPDevice(plugin)
        conf.set(CORE_ENABLED_PLUGINS=[pname for pname,plugin in self._plugins.items() if plugin.running])
        self.log_info("disabled plugin '%s'" % name)

    def disablePlugin(self, name):
        """Disables the named service."""
        try:
            if not name in self._plugins:
                raise Exception("plugin doesn't exist")
            if not self.pluginIsEnabled(name):
                raise Exception("plugin is not enabled")
            plugin = self._plugins[name]
            d = maybeDeferred(plugin.stopService)
            d.addCallback(self._doDisablePlugin, name, plugin)
        except Exception, e:
            self.log_error("failure while disabling plugin '%s': %s" % (name, e))

    def pluginIsEnabled(self, name):
        """
        Returns True if the named plugin is enabled, otherwise False if it
        is disabled.  If the plugin does not exist it raises an Exception.
        """
        if not name in self._plugins:
            raise Exception("no such plugin '%s'" % name)
        plugin = self._plugins[name]
        if plugin.running:
            return True
        return False
