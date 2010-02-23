# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.application.service import MultiService
from higgins.entrypoint import plugins, Service
from higgins.http.channel import HTTPFactory
from higgins.http.server import Site
from higgins.http.routes import RootDispatcher
from higgins.artist import ArtistMethods
from higgins.album import AlbumMethods
from higgins.song import SongMethods
from higgins.playlist import PlaylistMethods
from higgins.content import ContentMethods
from higgins.settings import Configurable, IntegerSetting, StringSetting, NetworkInterfaceSetting
from higgins.logger import Loggable


class CoreService(MultiService, Configurable, Loggable):
    log_domain = "core"

    HTTP_INTERFACE = NetworkInterfaceSetting('http interface', '')
    HTTP_PORT = IntegerSetting('http port', 2727, min=1, max=65535)
    SERVICES = StringSetting('enabled services', '')

    def __init__(self):
        MultiService.__init__(self)
        Configurable.__init__(self, 'core')
        self.root = RootDispatcher()
        self.root.addRoute('/api/1.0/artist/', ArtistMethods())
        self.root.addRoute('/api/1.0/album/', AlbumMethods())
        self.root.addRoute('/api/1.0/song/', SongMethods())
        self.root.addRoute('/api/1.0/playlist/', PlaylistMethods())
        self.root.addRoute('/api/1.0/content/', ContentMethods())
        self._site = Site(self.root)

    def startService(self):
        MultiService.startService(self)
        # create the listening socket
        iface = self.HTTP_INTERFACE
        port = self.HTTP_PORT
        self._listener = reactor.listenTCP(port, HTTPFactory(self._site), interface=iface)
        self.log_info("started core service")
        # load enabled services
        for name in [s.strip() for s in self.SERVICES.split(',')]:
            try:
                service = plugins.loadEntryPoint('higgins.plugin', name, Service)
                service.initService(self)
                service.setServiceParent(self)
                self.log_info("enabled service '%s'" % name)
            except Exception, e:
                self.log_warning("failed to enable service %s: %s" % (name, e))
        self.log_debug("started all enabled services")

    def _doStopService(self, result):
        self._listener.stopListening()
        self.log_info("stopped core service")

    def stopService(self):
        d = maybeDeferred(MultiService.stopService, self)
        d.addCallback(self._doStopService)
        return d
