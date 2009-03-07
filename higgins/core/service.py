# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from os.path import join as pathjoin
from pkg_resources import resource_string
from twisted.application.service import MultiService
from twisted.internet import reactor
from higgins.conf import conf
from higgins.service import Service
from higgins.http import server, channel
from higgins.http import resource, wsgi
from higgins.http.http import Response
from higgins.core.configurator import Configurator, IntegerSetting
from higgins.core.manager import ManagerResource
from higgins.core.logger import CoreLogger
from higgins.upnp import upnp_service
from higgins.upnp.device import Device as UPnPDevice

class CoreHttpConfig(Configurator):
    pretty_name = "HTTP Server"
    description = "Configure the built-in HTTP Server"
    HTTP_PORT = IntegerSetting("Listening Port", 8000, min_value=0, max_value=65535)

class BrowserResource(wsgi.WSGIResource):
    def __init__(self):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi.WSGIResource.__init__(self, WSGIHandler())

class StaticResource(resource.Resource):
    def allowedMethods(self):
        return ("GET",)
    def locateChild(self, request, segments):
        path = pathjoin(*segments)
        try:
            self.data = resource_string('higgins.data', path)
            return self, []
        except:
            return None, []
    def render(self, request):
        return Response(200, headers=None, stream=self.data)

class RootResource(resource.Resource):
    def __init__(self):
        self.browser = BrowserResource()
    def locateChild(self, request, segments):
        if segments[0] == "static":
            return StaticResource(), segments
        if segments[0] == "manage":
            return ManagerResource(), segments[1:]
        return self.browser, segments

class CoreService(MultiService, CoreLogger):
    def __init__(self):
        self._plugins = {}
        # register the standard configs
        self._config_items = {
            'http': { 'name': 'http', 'config': CoreHttpConfig() }
            }
        # start the webserver
        self._site = server.Site(RootResource())
        MultiService.__init__(self)

    def startService(self):
        MultiService.startService(self)
        self._listener = reactor.listenTCP(CoreHttpConfig.HTTP_PORT, channel.HTTPFactory(self._site))
        self.log_debug("started core service")
        self.upnp_service = upnp_service
        # load enabled services
        try:
            for name in conf.get("CORE_ENABLED_PLUGINS", []):
                self.enablePlugin(name)
            self.log_debug ("finished starting enabled services")
        except Exception, e:
            raise e

    def stopService(self):
        MultiService.stopService(self)
        self._listener.stopListening()
        self.log_debug("stopped core service")

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
                if issubclass(configs, Configurator):
                    configs()
                elif issubclass(configs, dict):
                    for name,config in configs.items():
                        if issubclass(config, Configurator):
                            config()
                        elif issubclass(config, dict):
                            init_configs_recursive(config)
            init_configs_recursive(plugin.configs)                
            self._plugins[name] = plugin
            self.log_debug("registered plugin '%s'" % name)
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
            self.log_debug("unregistered plugin '%s'" % name)
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
            if isinstance(plugin, UPnPDevice):
                # if it isn't, then start it
                if self.upnp_service.running == 0:
                    # setServiceParent() implicitly calls startService()
                    self.upnp_service.setServiceParent(self)
                if plugin.parent == None:
                    plugin.setServiceParent(self.upnp_service)
                else:
                    plugin.startService()
            # otherwise plugin is a simple Service
            else:
                if plugin.parent == None:
                    plugin.setServiceParent(self)
                else:
                    plugin.startService()
            # update the list of enabled plugins
            conf.set(CORE_ENABLED_PLUGINS=[name for name,plugin in self._plugins.items() if plugin.running])
            self.log_debug("enabled plugin '%s'" % name)
        except Exception, e:
            self.log_error("failed to enable plugin '%s': %s" % (name, e))

    def disablePlugin(self, name):
        """Disables the named service."""
        try:
            if not name in self._plugins:
                raise Exception("plugin doesn't exist")
            if not self.pluginIsEnabled(name):
                raise Exception("plugin is not enabled")
            plugin = self._plugins[name]
            plugin.stopService()
            #if not self.upnp_service.running == 0:
            #    self.upnp_service.disownParent()
            conf.set(CORE_ENABLED_PLUGINS=[name for name,plugin in self._plugins.items() if plugin.running])
            self.log_debug("disabled plugin '%s'" % name)
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

core_service = CoreService()
