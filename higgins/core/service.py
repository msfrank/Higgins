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

# our Django URLConf.  we set this dynamically in CoreService.__init__()
urlpatterns = None

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
        if segments[0] == "content":
            return ContentResource(), segments[1:]
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
        # 
        self._toplevel_pages = []
        # register URL patterns
        global urlpatterns
        urlpatterns = patterns('',
            (r'^/?$', 'higgins.core.front.index'),
            (r'^library/?$', 'higgins.core.browser.front'),
            (r'^library/music/?$', 'higgins.core.browser.music_front'),
            (r'^library/music/byartist/(?P<artist_id>\d+)/?$', 'higgins.core.browser.music_byartist'),
            (r'^library/music/bysong/(?P<song_id>\d+)/?$', 'higgins.core.browser.music_bysong'),
            (r'^library/music/byalbum/(?P<album_id>\d+)/?$', 'higgins.core.browser.music_byalbum'),
            (r'^library/music/bygenre/(?P<genre_id>\d+)/?$', 'higgins.core.browser.music_bygenre'),
            (r'^library/music/artists/?$', 'higgins.core.browser.music_artists'),
            (r'^library/music/genres/?$', 'higgins.core.browser.music_genres'),
            (r'^library/music/tags/?$', 'higgins.core.browser.music_tags'),
            (r'^library/playlists/?$', 'higgins.core.browser.list_playlists'),
            (r'^library/playlists/(?P<playlist_id>\d+)/?$', 'higgins.core.browser.playlist_show'),
            (r'^settings/plugins/?$', 'higgins.core.settings.list_plugins', {'core_service': self}),
            (r'^settings/plugins/(?P<name>\w+)/?$', 'higgins.core.settings.configure_plugin', {'core_service': self}),
            (r'^settings/?$', 'higgins.core.settings.front', {'core_service': self}),
            (r'^settings/(?P<name>\w+)/?$', 'higgins.core.settings.configure_toplevel', {'core_service': self}),
            (r'^view/(?P<name>\w+)/?$', 'higgins.core.frontend.show', {'core_service': self}),
            )
        # connect to the django db signals, so we can fire our own
        # signal when the database changes
        from higgins.core.models import db_changed
        self._db_changed = db_changed
        self._db_changed_marker = False
        post_save.connect(self._db_changed_callback)
        post_delete.connect(self._db_changed_callback)
        reactor.callLater(2, self._signal_db_changed)
        # start the webserver
        self._site = server.Site(RootResource())
        MultiService.__init__(self)

    def _db_changed_callback(self, sender, **kwdargs):
        self._db_changed_marker = True

    def _signal_db_changed(self):
        if self._db_changed_marker:
            self._db_changed_marker = False
            self._db_changed.signal(None)
        reactor.callLater(2, self._signal_db_changed)

    def startService(self):
        MultiService.startService(self)
        self._listener = reactor.listenTCP(CoreHttpConfig.HTTP_PORT, channel.HTTPFactory(self._site))
        self.log_debug("started core service")
        self.upnp_service = UPNPService()
        # load enabled services
        try:
            for name in conf.get("CORE_ENABLED_PLUGINS", []):
                self.enablePlugin(name)
            self.log_debug ("finished starting enabled services")
        except Exception, e:
            raise e

    def _doStopService(self, result):
        self._listener.stopListening()
        self.log_debug("stopped core service")

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
            self.log_debug("enabled plugin '%s'" % name)
        except Exception, e:
            self.log_error("failed to enable plugin '%s': %s" % (name, e))

    def _doDisablePlugin(self, result, name, plugin):
        #if not self.upnp_service.running == 0:
        #    self.upnp_service.disownParent()
        if isinstance(plugin, UPNPDevice):
            self.upnp_service.unregisterUPNPDevice(plugin)
        conf.set(CORE_ENABLED_PLUGINS=[pname for pname,plugin in self._plugins.items() if plugin.running])
        self.log_debug("disabled plugin '%s'" % name)

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

    def renderToResponse(self, template, context):
        return render_to_response(template, context)
