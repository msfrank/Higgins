# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.python import filepath
from twisted.application.service import MultiService
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from axiom.errors import ItemNotFound
from higgins.entrypoint import plugins, Service
from higgins.http import server, channel
from higgins.http.routes import RootDispatcher
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.http.stream import FileStream
from higgins.db import db, File
from higgins.artist import ArtistMethods
from higgins.album import AlbumMethods
from higgins.song import SongMethods
from higgins.playlist import PlaylistMethods
from higgins.gst.transcode import TranscodingStream, ProfileNotFound

class CoreConfiguration(object):
    HTTP_INTERFACE = '0.0.0.0'
    HTTP_PORT = 2727
    SERVICES = ['daap']

class CoreService(MultiService):
    log_domain = "core"

    def __init__(self):
        root = RootDispatcher()
        root.addRoute('/api/1.0/content/(\d+)\.?.*$', self.renderContent, allowedMethods=('GET'))
        root.addRoute('/api/1.0/artist/', ArtistMethods())
        root.addRoute('/api/1.0/album/', AlbumMethods())
        root.addRoute('/api/1.0/song/', SongMethods())
        root.addRoute('/api/1.0/playlist/', PlaylistMethods())
        self._site = server.Site(root)
        MultiService.__init__(self)

    def startService(self):
        MultiService.startService(self)
        # create the listening socket
        iface = CoreConfiguration.HTTP_ADDRESS
        if iface == '0.0.0.0':
            iface = ''
        port = CoreConfiguration.HTTP_PORT
        self._listener = reactor.listenTCP(port, channel.HTTPFactory(self._site))
        self.log_info("started core service")
        # load enabled services
        for name in CoreConfiguration.SERVICES:
            try:
                service = plugins.loadEntryPoint('higgins.plugin', name, Service)
                if service.parent == None:
                    service.setServiceParent(self)
                else:
                    service.startService()
                self.log_info("enabled service '%s'" % name)
            except Exception, e:
                self.log_warning("failed to enable service %s: %s" % (name, e))
        logger.log_debug("started all enabled services")

    def _doStopService(self, result):
        self._listener.stopListening()
        self.log_info("stopped core service")

    def stopService(self):
        d = maybeDeferred(MultiService.stopService, self)
        d.addCallback(self._doStopService)
        return d

    def renderContent(self, request, fileID):
        try:
            # look up the fileID
            fileID = int(fileID)
            file = db.get(File, File.storeID==fileID)
            logger.log_debug("file=%s" % str(file))
            # if mimetype is part of the request, then set up a transcoding stream
            if 'mimetype' in request.args:
                mimetype = request.args['mimetype'][0]
                logger.log_debug("streaming %s as %s" % (file.path, mimetype))
                stream = TranscodingStream(file, mimetype)
                return Response(200, {'content-type': stream.mimetype}, stream)
            # otherwise set up a normal file stream
            logger.log_debug("streaming %s" % file.path)
            mimetype = MimeType.fromString(str(file.MIMEType))
            f = open(str(file.path), 'rb')
            stream = FileStream(f)
            stream.length = file.size
            return Response(200, {'content-type': mimetype}, stream)
        except ItemNotFound, e:
            logger.log_debug("failed to stream fileID %s: no such item" % str(fileID))
            return Response(404)
        except ProfileNotFound, e:
            logger.log_debug("failed to stream fileID %s: %s" % (str(fileID), str(e)))
            return Response(400)
        except Exception, e:
            logger.log_error("failed to stream fileID %s: %s" % (str(fileID), str(e)))
            return Response(500)
